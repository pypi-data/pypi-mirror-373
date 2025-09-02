"""
Job tracking utilities for Airbyte jobs.

This module provides functionality to track job start times and calculate
actual duration across Airflow DAG runs, since Airbyte API duration field
is unreliable for running jobs.
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple

from airflow.models import TaskInstance, Variable
from airflow.utils.context import Context


class JobTracker:
    """Track Airbyte job durations across DAG runs using XCom."""
    
    def __init__(self, task_instance: TaskInstance):
        self.task_instance = task_instance
        # Use Airflow Variables for cross-worker persistence
        self.variable_key = "airbyte_job_tracker_data"
        # Fallback XCom key
        self.xcom_key = "airbyte_job_tracker_global"
    
    def get_tracked_jobs(self) -> Dict[str, Any]:
        """Get currently tracked jobs with robust persistence across workers."""
        # Strategy 1: Try Airflow Variables (works across all workers and DAG runs)
        try:
            tracked_data = Variable.get(self.variable_key, default_var=None)
            if tracked_data:
                data = json.loads(tracked_data)
                print(f"Retrieved tracking data from Airflow Variable: {self.variable_key}")
                return data
        except Exception as e:
            print(f"Warning: Failed to get tracking data from Airflow Variable: {e}")
        
        # Strategy 2: Try XCom from current task instance
        try:
            tracked_data = self.task_instance.xcom_pull(
                task_ids=self.task_instance.task_id,
                key=self.xcom_key
            )
            if tracked_data:
                return json.loads(tracked_data)
        except Exception:
            pass
        
        # Strategy 3: Try XCom from previous runs
        try:
            tracked_data = self.task_instance.xcom_pull(
                task_ids=self.task_instance.task_id,
                key=self.xcom_key,
                dag_id=self.task_instance.dag_id,
                include_prior_dates=True
            )
            if tracked_data:
                print(f"Retrieved tracking data from previous DAG run")
                return json.loads(tracked_data)
        except Exception:
            pass
                
        return {}
    
    def save_tracked_jobs(self, tracked_jobs: Dict[str, Any]) -> None:
        """Save tracked jobs with robust persistence across workers."""
        # Strategy 1: Save to Airflow Variables (works across all workers and DAG runs)
        try:
            Variable.set(self.variable_key, json.dumps(tracked_jobs))
            print(f"Saved tracking data to Airflow Variable: {self.variable_key}")
        except Exception as e:
            print(f"Warning: Failed to save tracked jobs to Airflow Variable: {e}")
        
        # Strategy 2: Save to XCom as fallback
        try:
            self.task_instance.xcom_push(
                key=self.xcom_key,
                value=json.dumps(tracked_jobs)
            )
        except Exception as e:
            print(f"Warning: Failed to save tracked jobs to XCom: {e}")
    
    def start_tracking_job(self, job_id: str, connection_id: str, 
                          connection_name: str, workspace_name: str, 
                          job_start_time: str = None) -> None:
        """Start tracking a job by recording its start time."""
        tracked_jobs = self.get_tracked_jobs()
        job_id = str(job_id)
        
        current_time = datetime.now(timezone.utc)
        
        # Use the actual job start time from Airbyte API if available
        if job_start_time:
            try:
                # Parse the job start time from Airbyte API
                start_time = datetime.fromisoformat(job_start_time.replace('Z', '+00:00'))
                start_time_str = start_time.isoformat()
            except Exception:
                start_time_str = current_time.isoformat()
        else:
            start_time_str = current_time.isoformat()
        
        tracked_jobs[job_id] = {
            'start_time': start_time_str,
            'connection_id': connection_id,
            'connection_name': connection_name,
            'workspace_name': workspace_name,
            'first_seen': current_time.isoformat(),
            'last_seen': current_time.isoformat(),
            'status': 'running'
        }
        
        self.save_tracked_jobs(tracked_jobs)
        print(f"Started tracking job {job_id} at {start_time_str}")
    
    def update_job_status(self, job_id: str, status: str) -> None:
        """Update job status and last seen time."""
        tracked_jobs = self.get_tracked_jobs()
        job_id = str(job_id)
        
        if job_id in tracked_jobs:
            current_time = datetime.now(timezone.utc)
            tracked_jobs[job_id]['last_seen'] = current_time.isoformat()
            tracked_jobs[job_id]['status'] = status
            
            # If job is no longer running, remove from tracking immediately
            if status.lower() not in ['running', 'pending']:
                del tracked_jobs[job_id]
                print(f"Job {job_id} finished with status '{status}', removed from tracking")
            else:
                print(f"Updated job {job_id} status to '{status}'")
            
            self.save_tracked_jobs(tracked_jobs)
    
    def get_job_duration(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the actual duration of a tracked job."""
        tracked_jobs = self.get_tracked_jobs()
        job_id = str(job_id)
        
        if job_id not in tracked_jobs:
            return None
        
        job_data = tracked_jobs[job_id]
        start_time = datetime.fromisoformat(job_data['start_time'])
        current_time = datetime.now(timezone.utc)
        
        duration = current_time - start_time
        total_seconds = int(duration.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return {
            'job_id': job_id,
            'connection_id': job_data['connection_id'],
            'connection_name': job_data['connection_name'],
            'workspace_name': job_data['workspace_name'],
            'start_time': job_data['start_time'],
            'total_seconds': total_seconds,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'formatted': f"{hours}h {minutes}m {seconds}s",
            'status': job_data['status']
        }
    
    def get_long_running_jobs(self, max_hours: float = 3.0) -> List[Dict[str, Any]]:
        """Get list of jobs that have been running longer than max_hours."""
        tracked_jobs = self.get_tracked_jobs()
        long_running = []
        max_seconds = max_hours * 3600
        
        for job_id in tracked_jobs:
            duration_info = self.get_job_duration(str(job_id))
            if duration_info and duration_info['total_seconds'] > max_seconds:
                long_running.append(duration_info)
        
        # Sort by duration (longest first)
        long_running.sort(key=lambda x: x['total_seconds'], reverse=True)
        return long_running
    
    def cleanup_finished_jobs(self, hook=None) -> None:
        """Remove jobs that are no longer running from tracking."""
        tracked_jobs = self.get_tracked_jobs()
        jobs_to_remove = []
        
        for job_id, job_data in tracked_jobs.items():
            # If we have a hook, check the actual job status from Airbyte API
            if hook:
                try:
                    status, payload = hook.get_job_status(job_id)
                    current_status = status.lower()
                    
                    # Remove jobs that are no longer running
                    if current_status not in ['running', 'pending']:
                        jobs_to_remove.append(job_id)
                        print(f"Job {job_id} finished with status '{current_status}', will remove from tracking")
                        continue
                    else:
                        # Update the status in our tracking data
                        job_data['status'] = current_status
                except Exception as e:
                    print(f"Could not check status for job {job_id}: {e}")
                    # If we can't check status, keep the job for now
            
            # Fallback: Check our stored status
            if job_data['status'].lower() not in ['running', 'pending']:
                jobs_to_remove.append(job_id)
                print(f"Job {job_id} has finished status '{job_data['status']}', will remove from tracking")
        
        for job_id in jobs_to_remove:
            del tracked_jobs[job_id]
            print(f"Removed finished job {job_id} from tracking")
        
        if jobs_to_remove:
            self.save_tracked_jobs(tracked_jobs)
    
    def get_tracking_summary(self) -> Dict[str, Any]:
        """Get a summary of currently tracked jobs."""
        tracked_jobs = self.get_tracked_jobs()
        
        summary = {
            'total_tracked': len(tracked_jobs),
            'jobs': []
        }
        
        for job_id in tracked_jobs:
            duration_info = self.get_job_duration(job_id)
            if duration_info:
                summary['jobs'].append(duration_info)
        
        return summary


def create_job_tracker(context: Context) -> JobTracker:
    """Create a JobTracker instance from Airflow context."""
    task_instance = context['task_instance']
    return JobTracker(task_instance)


def track_and_monitor_jobs(hook, context: Context, max_runtime_hours: float = 3.0,
                          dry_run: bool = False) -> Dict[str, Any]:
    """
    Track running jobs and monitor for long-running ones.
    
    This function should be called in each DAG run to:
    1. Find currently running jobs
    2. Start tracking new jobs
    3. Update status of existing tracked jobs
    4. Identify jobs that have exceeded max_runtime_hours
    5. Optionally cancel long-running jobs
    
    Returns:
        Dict with tracking and cancellation results
    """
    tracker = create_job_tracker(context)
    
    # Clean up finished jobs by checking actual status from Airbyte API
    tracker.cleanup_finished_jobs(hook)
    
    # Find currently running jobs
    running_jobs = []
    
    # Method 1: Use proper API filter to get running jobs
    try:
        print(f"  🔍 Using API filter: status=running")
        jobs = hook.list_jobs(job_type='sync', status='running')
        print(f"  📊 API returned {len(jobs.get('data', []))} running jobs")
        
        for job in jobs.get('data', []):
            running_jobs.append({
                'jobId': job.get('jobId'),
                'connectionId': job.get('connectionId'),
                'startTime': job.get('startTime')
            })
            print(f"  ✅ Found running job {job.get('jobId')} via API filter")
    except Exception as e:
        print(f"  ❌ Error getting running jobs via API filter: {e}")
        
        # Fallback: Check all jobs and filter by status
        try:
            print(f"  🔄 Fallback: Getting all jobs and filtering by status")
            jobs = hook.list_jobs(job_type='sync')
            for job in jobs.get('data', []):
                if job.get('status', '').lower() == 'running':
                    running_jobs.append({
                        'jobId': job.get('jobId'),
                        'connectionId': job.get('connectionId'),
                        'startTime': job.get('startTime')
                    })
                    print(f"  ✅ Found running job {job.get('jobId')} via fallback")
        except Exception as e2:
            print(f"  ❌ Error in fallback method: {e2}")
    
    # Update tracking for all running jobs
    for job in running_jobs:
        job_id = job['jobId']
        connection_id = job['connectionId']
        
        # Get connection details
        try:
            connections = hook.list_connections()
            connection_info = None
            for conn in connections.get('data', []):
                if conn.get('connectionId') == connection_id:
                    connection_info = conn
                    break
            
            connection_name = connection_info.get('name', 'Unknown') if connection_info else 'Unknown'
            workspace_id = connection_info.get('workspaceId', 'Unknown') if connection_info else 'Unknown'
            
            # Get workspace name
            workspace_name = 'Unknown'
            try:
                workspaces = hook.list_workspaces()
                for workspace in workspaces.get('data', []):
                    if workspace.get('workspaceId') == workspace_id:
                        workspace_name = workspace.get('name', 'Unknown')
                        break
            except Exception:
                pass
            
            # Check if we're already tracking this job
            duration_info = tracker.get_job_duration(job_id)
            
            if duration_info is None:
                # Start tracking new job with actual start time from Airbyte API
                job_start_time = job.get('startTime')  # Get actual start time from Airbyte
                tracker.start_tracking_job(job_id, connection_id, connection_name, workspace_name, job_start_time)
            else:
                # Update existing job status to running
                tracker.update_job_status(job_id, 'running')
                
        except Exception as e:
            print(f"Error processing job {job_id}: {e}")
    
    # Also check status of all tracked jobs that weren't in the running list
    # This ensures we catch jobs that finished between DAG runs
    tracked_jobs = tracker.get_tracked_jobs()
    running_job_ids = {job['jobId'] for job in running_jobs}
    
    for job_id in tracked_jobs:
        if job_id not in running_job_ids:
            # This job wasn't in the running list, check its actual status
            try:
                status, payload = hook.get_job_status(job_id)
                current_status = status.lower()
                
                if current_status not in ['running', 'pending']:
                    # Job has finished, update status (will be cleaned up in next run)
                    tracker.update_job_status(job_id, current_status)
                    print(f"Job {job_id} not in running list, status: {current_status}")
                else:
                    # Job is still running but wasn't in the API response (API inconsistency)
                    tracker.update_job_status(job_id, current_status)
                    print(f"Job {job_id} still running but not in API response")
            except Exception as e:
                print(f"Could not check status for tracked job {job_id}: {e}")
    
    # Get long-running jobs
    long_running_jobs = tracker.get_long_running_jobs(max_runtime_hours)
    
    # Cancel long-running jobs if not in dry run mode
    canceled_jobs = []
    if not dry_run and long_running_jobs:
        for job_info in long_running_jobs:
            job_id = job_info['job_id']
            try:
                print(f"Canceling job {job_id} (running for {job_info['formatted']})")
                result = hook.cancel_job(job_id)
                canceled_jobs.append({
                    'job_id': job_id,
                    'duration': job_info['formatted'],
                    'connection_name': job_info['connection_name'],
                    'result': result
                })
                tracker.update_job_status(job_id, 'cancelled')
            except Exception as e:
                print(f"Error canceling job {job_id}: {e}")
    
    # Get tracking summary
    summary = tracker.get_tracking_summary()
    
    return {
        'tracked_jobs_count': summary['total_tracked'],
        'running_jobs_found': len(running_jobs),
        'long_running_jobs': len(long_running_jobs),
        'jobs_canceled': len(canceled_jobs),
        'canceled_jobs': canceled_jobs,
        'tracking_summary': summary
    }
