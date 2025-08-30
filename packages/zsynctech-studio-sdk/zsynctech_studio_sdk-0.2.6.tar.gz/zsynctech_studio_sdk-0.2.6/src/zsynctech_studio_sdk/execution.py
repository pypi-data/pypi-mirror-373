from zsynctech_studio_sdk.models.execution import ExecutionModel, ExecutionStatus
from zsynctech_studio_sdk.common.exceptions import ExecutionUpdateError
from zsynctech_studio_sdk.utils import get_utc_now
from zsynctech_studio_sdk.context import Context
from zsynctech_studio_sdk import client
from typing import Optional, Any


EXECUTION_STATUS_COMPLETED = [
    ExecutionStatus.OUT_OF_OPERATING_HOURS,
    ExecutionStatus.INTERRUPTED,
    ExecutionStatus.FINISHED,
    ExecutionStatus.ERROR,
]


class Execution(ExecutionModel):
    def __init__(self, execution_id: Optional[str] = None):
        if execution_id:
            super().__init__(
                id=execution_id
            )
        else:
            super().__init__()

        Context.execution = self

    def _update(
            self,
            status: Optional[ExecutionStatus] = None,
            observation: Optional[str] = None,
            total_task_count: Optional[int] = None,
            current_task_count: Optional[int] = None,
        ) -> dict:

        if self.status in EXECUTION_STATUS_COMPLETED:
            return self.model_dump()

        if status in EXECUTION_STATUS_COMPLETED:
            self.endDate = get_utc_now()

        self.status = status if status is not None else self.status
        self.observation = observation if observation is not None else self.observation
        self.totalTaskCount = total_task_count if total_task_count is not None else self.totalTaskCount
        self.currentTaskCount = current_task_count if current_task_count is not None else self.currentTaskCount

        try:
            response = client.patch(
                endpoint=f"{self.id}/executions",
                json=self.model_dump()
            )
            response.raise_for_status()
        except Exception as e:
            raise ExecutionUpdateError(f"Erro ao atualizar execução: {str(e)}") from e

        return self.model_dump()

    def set_total_task_count(self, total_task_count: int) -> dict[str, Any]:
        return self._update(total_task_count=total_task_count)

    def update_current_task_count(self, current_task_count: int) -> dict[str, Any]:
        return self._update(current_task_count=current_task_count)

    def update_observation(self, observation: str) -> dict[str, Any]:
        return self._update(observation=observation)

    def start(self, observation: Optional[str] = None) -> dict:
        return self._update(ExecutionStatus.RUNNING, observation)

    def error(self, observation: Optional[str] = None) -> dict:
        return self._update(ExecutionStatus.ERROR, observation=observation)

    def out_of_operating_hours(self, observation: Optional[str] = None) -> dict:
        return self._update(ExecutionStatus.OUT_OF_OPERATING_HOURS, observation=observation)

    def finished(self, observation: Optional[str] = None) -> dict:
        return self._update(ExecutionStatus.FINISHED, observation=observation)

    def interrupted(self, observation: Optional[str] = None) -> dict:
        return self._update(ExecutionStatus.INTERRUPTED, observation=observation)
