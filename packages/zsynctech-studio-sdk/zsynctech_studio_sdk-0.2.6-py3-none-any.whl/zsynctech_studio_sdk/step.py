from zsynctech_studio_sdk.common.exceptions import TaksNotStardedError, ExecutionNotStardedError
from zsynctech_studio_sdk.models.step import StepModel, StepStatus
from zsynctech_studio_sdk.enums.operations import Operations
from zsynctech_studio_sdk.utils import get_utc_now
from zsynctech_studio_sdk.context import Context
from zsynctech_studio_sdk import client
from typing import Optional


STEP_STATUS_COMPLETED = [
    StepStatus.FAIL,
    StepStatus.SUCCESS,
]


class Step(StepModel):
    def __init__(self, code: str, observation: Optional[str] = None):
        if Context.execution is None:
            raise ExecutionNotStardedError("Execution not started")

        if Context.task is None:
            raise TaksNotStardedError("Task not started")

        super().__init__(
            stepCode=code,
            taskId=Context.task.id,
            automationOnClientId=client._instance_id,
            startDate=get_utc_now(),
            observation=observation
        )

    def _update(
            self,
            status: Optional[StepStatus] = None,
            observation: Optional[str] = None,
        ) -> dict:
        if status in STEP_STATUS_COMPLETED:
            self.endDate = get_utc_now()

        self.observation = observation if observation is not None else self.observation
        self.status = status if status is not None else self.status

        try:
            if self.operation == Operations.CREATE:
                response = client.post(
                    endpoint=f"{Context.execution.id}/taskSteps",
                    json=self.model_dump()
                )
            else:
                response = client.patch(
                    endpoint=f"{Context.execution.id}/taskSteps",
                    json=self.model_dump()
                )
            response.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Erro ao atualizar steep: {str(e)}") from e

        self.operation = Operations.UPDATE

        return self.model_dump()
    
    def _start(self, observation: Optional[str] = None) -> dict:
        return self._update(status=StepStatus.RUNNING, observation=observation)

    def fail(self, observation: Optional[str] = None) -> dict:
        return self._update(status=StepStatus.FAIL, observation=observation)

    def success(self, observation: Optional[str] = None) -> dict:
        return self._update(status=StepStatus.SUCCESS, observation=observation)

    def __enter__(self):
        self._start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.status not in STEP_STATUS_COMPLETED:
            if exc_type is not None:
                self.fail(observation=str(exc_value))
            else:
                self.success()

        return False