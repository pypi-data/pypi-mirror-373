# Fast.Bi Replication Control

Airflow utilities to monitor and cancel long-running Airbyte jobs with advanced job tracking.

## Overview

This package provides Airflow operators and hooks to:
- Discover all Airbyte workspaces and connections
- Monitor running jobs across connections using proper API filters
- Track job durations across DAG runs using XCom persistence
- Cancel jobs that exceed configurable time limits
- Provide full context (connection names, workspace info)
- Calculate actual duration from start time (not Airbyte's unreliable duration field)

## Key Features

### 🎯 **Advanced Job Tracking**
- **Robust Persistence**: Uses Airflow Variables for cross-worker persistence (works with HPA scaling)
- **Worker Consistency**: Pinned to specific worker (`data-orchestration-worker-0`) for consistency
- **Accurate Duration Calculation**: Calculates actual runtime from stored start times
- **Full Context**: Provides connection names, workspace info, and job details

### 🔧 **Persistence Strategy**
The system uses a multi-layered persistence approach to handle dynamic worker scaling:

1. **Primary**: Airflow Variables - Works across all workers and DAG runs
2. **Fallback**: XCom - For same DAG run persistence
3. **Worker Pinning**: Queue assignment to `default` for consistency

This ensures job tracking data persists even with HPA scaling and worker restarts.

### 🔍 **Smart Job Discovery**
- **API-First Approach**: Uses proper Airbyte API filters (`status=running`) instead of hardcoded job IDs
- **Dynamic Detection**: Automatically finds all running jobs without manual configuration
- **Fallback Support**: Graceful degradation if API filters fail

### 🛡️ **Safety Features**
- **Dry Run Mode**: Default `dry_run=True` for safety - preview what would be canceled
- **Configurable Limits**: Set different time limits for different connections
- **Error Handling**: Robust error handling with detailed logging

## Installation

```bash
pip install fast_bi_replication_control
```

## Airflow Connection Setup

Create an Airflow connection with the following details:

- **Connection Id**: `Data-Replication` (or customize via parameter)
- **Connection Type**: `airbyte`
- **Host**: `http://data-replication-airbyte-webapp-svc.data-replication.svc.cluster.local`
- **Port**: (leave empty or specify if needed)
- **No authentication required** (internal network)

## Environment Variables (Fallback)

If no Airflow connection is configured, the package will use these environment variables:

```bash
AIRBYTE_API_LINK=http://data-replication-airbyte-webapp-svc.data-replication.svc.cluster.local
AIRBYTE_API_BASE=api/public
```

## Usage Examples

### 1. Monitor All Connections (Recommended)

```python
from fast_bi_replication_control import AirbyteJobMonitorOperator

# Monitor all connections with job tracking
# Note: Uses queue='default' for worker consistency
monitor_task = AirbyteJobMonitorOperator(
    task_id='monitor_all_connections',
    airbyte_conn_id='Data-Replication',
    connection_ids=None,  # Monitor all connections
    max_runtime_hours=3.0,  # Cancel jobs running longer than 3 hours
    job_type='sync',  # Monitor sync jobs only
    dry_run=True,  # Default to True for safety - set to False to actually cancel
    queue='default',  # Pin to specific worker for consistency
    dag=dag,
)
```

### 2. Monitor Specific Connections

```python
# Monitor only specific connection IDs with job tracking
# Note: Uses queue='default' for worker consistency
monitor_task = AirbyteJobMonitorOperator(
    task_id='monitor_specific_connections',
    airbyte_conn_id='Data-Replication',
    connection_ids=['fccd3766-624e-478f-bb0d-3dc31d8a4efb'],  # Specific connection IDs
    max_runtime_hours=2.0,  # More aggressive threshold for specific connections
    job_type='sync',  # Monitor sync jobs only
    dry_run=True,  # Default to True for safety - set to False to actually cancel
    queue='default',  # Pin to specific worker for consistency
    dag=dag,
)
```

### 3. Use Job Tracking System Directly

```python
from fast_bi_replication_control import track_and_monitor_jobs

def custom_monitoring(**context):
    """Custom monitoring logic using the job tracking system."""
    from fast_bi_replication_control import AirbyteApiHook
    
    hook = AirbyteApiHook(airbyte_conn_id='Data-Replication')
    
    # Use the new tracking system
    result = track_and_monitor_jobs(
        hook=hook,
        context=context,
        max_runtime_hours=1.0,  # 1 hour threshold
        dry_run=True  # Don't actually cancel
    )
    
    print(f"Tracked jobs: {result['tracked_jobs_count']}")
    print(f"Running jobs found: {result['running_jobs_found']}")
    print(f"Long running jobs: {result['long_running_jobs']}")
    
    return result

# Use in PythonOperator
custom_task = PythonOperator(
    task_id='custom_monitoring',
    python_callable=custom_monitoring,
    dag=dag,
)
```

### 4. Generate Tracking Reports

```python
from fast_bi_replication_control import create_job_tracker

def generate_report(**context):
    """Generate a report of currently tracked jobs."""
    tracker = create_job_tracker(context)
    summary = tracker.get_tracking_summary()
    
    print(f"Total tracked jobs: {summary['total_tracked']}")
    
    for job in summary['jobs']:
        print(f"Job {job['job_id']}: {job['formatted']}")
        print(f"  Connection: {job['connection_name']}")
        print(f"  Workspace: {job['workspace_name']}")
    
    return summary

report_task = PythonOperator(
    task_id='generate_report',
    python_callable=generate_report,
    dag=dag,
)
```

### 5. Complete Example DAG

```python
from fast_bi_replication_control import AirbyteApiHook

hook = AirbyteApiHook(airbyte_conn_id='Data-Replication')

# List workspaces
workspaces = hook.list_workspaces()
print(f"Found {len(workspaces.get('data', []))} workspaces")

# List connections
connections = hook.list_connections()
print(f"Found {len(connections.get('data', []))} connections")

# List jobs for a specific connection
jobs = hook.list_jobs(connection_id='your-connection-id')
print(f"Found {len(jobs.get('data', []))} jobs")

# Get job status
status, details = hook.get_job_status('your-job-id')
print(f"Job status: {status}")

# Cancel a job
result = hook.cancel_job('your-job-id')
print(f"Cancel result: {result}")
```

## API Endpoints Used

The package interacts with the following Airbyte API endpoints:

- `GET /v1/workspaces` - List all workspaces
- `GET /v1/connections` - List connections (with optional workspace filtering)
- `GET /v1/jobs` - List jobs (with optional connection/workspace filtering)
- `GET /v1/jobs/{jobId}` - Get job status and details
- `DELETE /v1/jobs/{jobId}` - Cancel a running job

## Configuration Options

### AirbyteJobMonitorOperator

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `airbyte_conn_id` | str | `'Data-Replication'` | Airflow connection ID |
| `connection_ids` | List[str] | `None` | List of connection IDs to monitor (None = all) |
| `max_runtime_hours` | float | `3.0` | Maximum runtime before canceling |
| `job_type` | str | `None` | Filter by job type ('sync', 'reset', or None for all) |
| `dry_run` | bool | `False` | If True, log what would be canceled but don't actually cancel |

### AirbyteJobMonitorSensor

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `job_id` | str | Required | Job ID to monitor |
| `airbyte_conn_id` | str | `'Data-Replication'` | Airflow connection ID |
| `cancel_after_seconds` | int | `None` | Cancel job after this many seconds |
| `poke_interval` | int | `60` | How often to check job status (seconds) |
| `timeout` | int | `None` | Maximum time to wait for job completion |

## Job Duration Tracking

**Important**: Since the Airbyte API doesn't provide runtime duration, the package uses job creation time (`createdAt`) to estimate runtime. This means:

1. On the first run, if a job is already running, the package can't determine how long it has been running
2. For accurate duration tracking across DAG runs, consider implementing persistent storage (XCom, database) to track job start times

## Example DAG

See `example_dag.py` for a comprehensive example showing all usage patterns.

## Error Handling

The package includes robust error handling:
- API failures are logged but don't stop the entire operation
- Individual connection/job failures are isolated
- Detailed logging for debugging

## Development

To build the package locally:

```bash
cd fast_bi_replication_control
python -m build
```

## License

MIT License 