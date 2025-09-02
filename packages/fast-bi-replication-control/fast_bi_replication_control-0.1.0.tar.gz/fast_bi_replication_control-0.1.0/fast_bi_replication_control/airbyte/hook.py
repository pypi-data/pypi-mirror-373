import os
import logging
from typing import Any, Dict, Optional, Tuple

import requests
from airflow.hooks.base import BaseHook


class AirbyteApiHook(BaseHook):
    """Hook for interacting with Airbyte public API for job monitoring/cancellation.

    Connection expected:
    - Conn Id: defaults to 'Data-Replication' (override via airbyte_conn_id)
    - Conn Type: 'airbyte' (not strictly enforced)
    - Host: base URL, e.g. 'http://data-replication-airbyte-webapp-svc.data-replication.svc.cluster.local'
    - Port: optional
    - No authentication required (internal network)

    Environment fallbacks (used if connection not configured):
    - AIRBYTE_API_LINK (default host)
    - AIRBYTE_API_BASE (default to 'api/public')
    """

    conn_name_attr = 'airbyte_conn_id'
    default_conn_name = 'Data-Replication'
    hook_name = 'Airbyte API'

    def __init__(
        self,
        airbyte_conn_id: str = default_conn_name,
        api_base: Optional[str] = None,
        request_timeout_seconds: int = 30,
    ) -> None:
        super().__init__()
        self.airbyte_conn_id = airbyte_conn_id
        self._api_base_override = api_base
        self.request_timeout_seconds = request_timeout_seconds
        self._session: Optional[requests.Session] = None
        self._started = False

    # ---- Public API ----

    def list_workspaces(self) -> Dict[str, Any]:
        """List all accessible workspaces."""
        url = self._build_url("workspaces")
        headers = {"accept": "application/json"}
        response = self.session.get(url, headers=headers, timeout=self.request_timeout_seconds)
        response.raise_for_status()
        return response.json()

    def list_connections(self, workspace_ids: Optional[str] = None) -> Dict[str, Any]:
        """List connections, optionally filtered by workspace IDs.
        
        Args:
            workspace_ids: Comma-separated workspace IDs to filter by
        """
        url = self._build_url("connections")
        headers = {"accept": "application/json"}
        params = {}
        if workspace_ids:
            params["workspaceIds"] = workspace_ids
        response = self.session.get(url, headers=headers, params=params, timeout=self.request_timeout_seconds)
        response.raise_for_status()
        return response.json()

    def list_jobs(self, connection_id: Optional[str] = None, workspace_ids: Optional[str] = None, job_type: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
        """List jobs, optionally filtered by connection ID, workspace IDs, job type, or status.
        
        Args:
            connection_id: Filter by specific connection ID
            workspace_ids: Comma-separated workspace IDs to filter by
            job_type: Filter by job type (e.g., 'sync', 'reset')
            status: Filter by job status (e.g., 'running', 'succeeded', 'failed')
        """
        url = self._build_url("jobs")
        headers = {"accept": "application/json"}
        params = {}
        if connection_id:
            params["connectionId"] = connection_id
        if workspace_ids:
            params["workspaceIds"] = workspace_ids
        if job_type:
            params["jobType"] = job_type
        if status:
            params["status"] = status
        response = self.session.get(url, headers=headers, params=params, timeout=self.request_timeout_seconds)
        response.raise_for_status()
        return response.json()

    def get_job(self, job_id: str) -> Dict[str, Any]:
        url = self._build_url(f"jobs/{job_id}")
        headers = {"accept": "application/json"}
        response = self.session.get(url, headers=headers, timeout=self.request_timeout_seconds)
        response.raise_for_status()
        return response.json()

    def get_job_status(self, job_id: str) -> Tuple[str, Dict[str, Any]]:
        payload = self.get_job(job_id)
        status = (
            payload.get('status')
            or payload.get('job', {}).get('status')
            or payload.get('data', {}).get('status')
        )
        if not status:
            logging.warning("Airbyte get_job response missing status; payload keys: %s", list(payload.keys()))
            status = 'unknown'
        return status.lower(), payload

    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        url = self._build_url(f"jobs/{job_id}")
        headers = {"accept": "application/json"}
        response = self.session.delete(url, headers=headers, timeout=self.request_timeout_seconds)
        response.raise_for_status()
        return response.json() if response.content else {"result": "cancelled"}

    # ---- Internals ----

    @property
    def session(self) -> requests.Session:
        if self._session is None:
            self._session = requests.Session()
        return self._session

    def _get_base_url(self) -> str:
        # Prefer Airflow connection, fallback to env
        try:
            connection = self.get_connection(self.airbyte_conn_id)
        except Exception:
            connection = None

        host_from_env = os.environ.get(
            'AIRBYTE_API_LINK',
            'http://data-replication-airbyte-webapp-svc.data-replication.svc.cluster.local',
        )

        if connection and (connection.host or connection.port):
            host = (connection.host or '').strip()
            if host and not host.startswith(('http://', 'https://')):
                host = f"http://{host}"
            if connection.port:
                # Only append port if not already present in host
                if f":{connection.port}" not in host:
                    host = f"{host.rstrip('/')}:{connection.port}"
            base_url = host
        else:
            base_url = host_from_env

        return base_url.rstrip('/')

    def _get_api_base(self) -> str:
        api_base = self._api_base_override or os.environ.get('AIRBYTE_API_BASE', 'api/public')
        return api_base.strip('/').rstrip('/')

    def _build_url(self, relative_path: str) -> str:
        base_url = self._get_base_url()
        api_base = self._get_api_base()
        # Airbyte public API version in path
        version = 'v1'
        relative = relative_path.lstrip('/')
        return f"{base_url}/{api_base}/{version}/{relative}" 