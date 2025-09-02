import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from airflow.models import BaseOperator
from airflow.utils.context import Context

from .hook import AirbyteApiHook
from .job_tracker import track_and_monitor_jobs


class AirbyteJobMonitorOperator(BaseOperator):
    """Operator to monitor and manage long-running Airbyte jobs.
    
    This operator can:
    1. Discover all workspaces and connections
    2. Find running jobs for specified connections (or all)
    3. Track job duration and cancel jobs exceeding time limits
    4. Store state between runs to track job start times
    
    Args:
        airbyte_conn_id: Airflow connection ID for Airbyte API
        connection_ids: List of connection IDs to monitor (None = all)
        max_runtime_hours: Maximum runtime in hours before canceling
        job_type: Filter by job type ('sync', 'reset', or None for all)
        dry_run: If True, log what would be canceled but don't actually cancel
    """
    
    template_fields = ("connection_ids",)
    
    def __init__(
        self,
        airbyte_conn_id: str = AirbyteApiHook.default_conn_name,
        connection_ids: Optional[List[str]] = None,
        max_runtime_hours: float = 3.0,
        job_type: Optional[str] = None,
        dry_run: bool = False,
        queue: Optional[str] = None,  # Add queue parameter
        **kwargs,
    ) -> None:
        super().__init__(queue=queue, **kwargs)  # Pass queue to parent
        self.airbyte_conn_id = airbyte_conn_id
        self.connection_ids = connection_ids
        self.max_runtime_hours = max_runtime_hours
        self.job_type = job_type
        self.dry_run = dry_run
        self.hook = AirbyteApiHook(airbyte_conn_id=airbyte_conn_id)
        
    def execute(self, context: Context) -> Dict[str, Any]:
        """Execute the job monitoring logic with detailed logging."""
        self.log.info("🚀 Starting Airbyte Job Monitoring")
        self.log.info("="*60)
        
        # Log configuration
        self.log.info("📋 Configuration:")
        self.log.info("  - Connection IDs: %s", 
                     "ALL connections" if self.connection_ids is None else self.connection_ids)
        self.log.info("  - Max runtime: %.1f hours", self.max_runtime_hours)
        self.log.info("  - Job type: %s", self.job_type or "ALL")
        self.log.info("  - Dry run: %s", "YES (safe mode)" if self.dry_run else "NO (will cancel)")
        
        # Use the new job tracking system
        result = track_and_monitor_jobs(
            hook=self.hook,
            context=context,
            max_runtime_hours=self.max_runtime_hours,
            dry_run=self.dry_run
        )
        
        # Log detailed results like simulate_production_tracking.sh
        self.log.info("📊 Monitoring Results:")
        self.log.info("  - Tracked jobs: %d", result['tracked_jobs_count'])
        self.log.info("  - Running jobs found: %d", result['running_jobs_found'])
        self.log.info("  - Long running jobs: %d", result['long_running_jobs'])
        self.log.info("  - Jobs canceled: %d", result['jobs_canceled'])
        
        # Show detailed tracking info
        if result['tracking_summary']['jobs']:
            self.log.info("📋 Currently tracked jobs:")
            for job in result['tracking_summary']['jobs']:
                self.log.info("    - Job %s: %s", job['job_id'], job['formatted'])
                self.log.info("      Connection: %s", job['connection_name'])
                self.log.info("      Workspace: %s", job['workspace_name'])
                self.log.info("      Started: %s", job['start_time'])
        else:
            self.log.info("📋 No jobs currently being tracked")
        
        # Show canceled jobs
        if result['canceled_jobs']:
            self.log.info("🚫 Canceled jobs:")
            for job in result['canceled_jobs']:
                self.log.info("    - Job %s: %s", job['job_id'], job['duration'])
                self.log.info("      Connection: %s", job['connection_name'])
        
        self.log.info("="*60)
        self.log.info("✅ Airbyte job monitoring completed")
        
        return result
    
    def _get_workspaces(self) -> Dict[str, Any]:
        """Get all accessible workspaces."""
        try:
            return self.hook.list_workspaces()
        except Exception as e:
            self.log.error("Failed to list workspaces: %s", e)
            return {"data": []}
    
    def _get_connections(self, workspace_ids: List[str]) -> Dict[str, Any]:
        """Get connections from all workspaces."""
        try:
            workspace_ids_str = ",".join(workspace_ids) if workspace_ids else None
            return self.hook.list_connections(workspace_ids=workspace_ids_str)
        except Exception as e:
            self.log.error("Failed to list connections: %s", e)
            return {"data": []}
    
    def _get_target_connection_ids(self, connections: Dict[str, Any]) -> List[str]:
        """Get list of connection IDs to monitor."""
        all_connection_ids = [conn.get('connectionId') for conn in connections.get('data', [])]
        
        if self.connection_ids is None:
            # Monitor all connections
            return all_connection_ids
        else:
            # Monitor only specified connections
            return [cid for cid in self.connection_ids if cid in all_connection_ids]
    
    def _find_running_jobs(self, connection_ids: List[str]) -> List[Dict[str, Any]]:
        """Find running jobs for the specified connections."""
        running_jobs = []
        
        for connection_id in connection_ids:
            try:
                jobs_response = self.hook.list_jobs(
                    connection_id=connection_id,
                    job_type=self.job_type
                )
                
                for job in jobs_response.get('data', []):
                    status = job.get('status', '').lower()
                    if status in ['running', 'pending']:
                        job['connection_id'] = connection_id
                        running_jobs.append(job)
                        
            except Exception as e:
                self.log.error("Failed to get jobs for connection %s: %s", connection_id, e)
        
        return running_jobs
    
    def _check_and_cancel_long_running_jobs(self, running_jobs: List[Dict[str, Any]], context: Context) -> List[Dict[str, Any]]:
        """Check job duration and cancel those exceeding the limit."""
        canceled_jobs = []
        max_runtime_seconds = self.max_runtime_hours * 3600
        
        for job in running_jobs:
            job_id = job.get('id')
            job_start_time = self._get_job_start_time(job, context)
            
            if job_start_time is None:
                self.log.warning("Could not determine start time for job %s", job_id)
                continue
            
            runtime_seconds = time.time() - job_start_time.timestamp()
            
            if runtime_seconds > max_runtime_seconds:
                self.log.warning(
                    "Job %s (connection %s) has been running for %.1f hours (limit: %.1f)",
                    job_id, job.get('connection_id'), runtime_seconds / 3600, self.max_runtime_hours
                )
                
                if not self.dry_run:
                    try:
                        self.hook.cancel_job(job_id)
                        self.log.info("Successfully canceled job %s", job_id)
                        canceled_jobs.append(job)
                    except Exception as e:
                        self.log.error("Failed to cancel job %s: %s", job_id, e)
                else:
                    self.log.info("DRY RUN: Would cancel job %s", job_id)
                    canceled_jobs.append(job)
            else:
                self.log.info(
                    "Job %s (connection %s) running for %.1f hours (within limit)",
                    job_id, job.get('connection_id'), runtime_seconds / 3600
                )
        
        return canceled_jobs
    
    def _get_job_start_time(self, job: Dict[str, Any], context: Context) -> Optional[datetime]:
        """Get the start time of a job.
        
        Since Airbyte API doesn't provide runtime duration, we need to track start times.
        This is a simplified implementation - in production you might want to use XCom or
        a database to persist job start times across DAG runs.
        """
        # Try to get from job data first
        created_at = job.get('createdAt')
        if created_at:
            try:
                return datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
        
        # Fallback: use current time (this means we can't track duration on first run)
        # In a real implementation, you'd want to store job start times in XCom or database
        self.log.warning("Using current time as job start time for job %s", job.get('id'))
        return datetime.now() 