import time
from typing import Optional

from airflow.exceptions import AirflowException
from airflow.sensors.base import BaseSensorOperator

from .hook import AirbyteApiHook


class AirbyteJobMonitorSensor(BaseSensorOperator):
    template_fields = ("job_id",)

    def __init__(
        self,
        job_id: str,
        airbyte_conn_id: str = AirbyteApiHook.default_conn_name,
        api_base: Optional[str] = None,
        cancel_after_seconds: Optional[int] = None,
        request_timeout_seconds: int = 30,
        mode: str = "reschedule",
        poke_interval: int = 60,
        **kwargs,
    ) -> None:
        super().__init__(mode=mode, poke_interval=poke_interval, **kwargs)
        self.job_id = str(job_id)
        self.cancel_after_seconds = cancel_after_seconds
        self.hook = AirbyteApiHook(
            airbyte_conn_id=airbyte_conn_id,
            api_base=api_base,
            request_timeout_seconds=request_timeout_seconds,
        )
        self._started_at_monotonic: Optional[float] = None

    def poke(self, context) -> bool:  # type: ignore[override]
        if self._started_at_monotonic is None:
            self._started_at_monotonic = time.monotonic()

        # Handle None, empty, or special job_id values
        if not self.job_id or self.job_id == 'None' or self.job_id == 'NO_RUNNING_JOBS':
            self.log.info("No job ID provided or no running jobs, sensor will succeed immediately")
            return True

        # Cancel if we exceeded the time budget
        if self.cancel_after_seconds is not None:
            elapsed = time.monotonic() - self._started_at_monotonic
            if elapsed >= self.cancel_after_seconds:
                self.log.warning(
                    "Cancelling Airbyte job %s after %.0f seconds (threshold=%s)",
                    self.job_id,
                    elapsed,
                    self.cancel_after_seconds,
                )
                try:
                    self.hook.cancel_job(self.job_id)
                except Exception as e:
                    self.log.error("Failed to cancel job %s: %s", self.job_id, e)
                raise AirflowException(f"Airbyte job {self.job_id} cancelled after exceeding time limit of {self.cancel_after_seconds} seconds")

        try:
            status, payload = self.hook.get_job_status(self.job_id)
            self.log.info("Airbyte job %s status: %s", self.job_id, status)

            if status in {"succeeded", "success"}:
                return True
            if status in {"failed", "error", "cancelled", "canceled"}:
                raise AirflowException(f"Airbyte job {self.job_id} finished with status: {status}")

            return False
        except Exception as e:
            self.log.error("Error checking job %s status: %s", self.job_id, e)
            # Don't fail the sensor on API errors, just return False to retry
            return False 