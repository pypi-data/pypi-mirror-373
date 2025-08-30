from zsynctech_studio_sdk.common.exceptions import TaskUpdateError, ExecutionNotStardedError
from zsynctech_studio_sdk.models.task import TaskModel, TaskStatus
from zsynctech_studio_sdk.enums.operations import Operations
from zsynctech_studio_sdk.utils import get_utc_now
from zsynctech_studio_sdk.context import Context
from zsynctech_studio_sdk import client
from uuid_extensions import uuid7
from typing import Optional


TASK_STATUS_COMPLETED = [
    TaskStatus.FAIL,
    TaskStatus.SUCCESS,
    TaskStatus.VALIDATION_ERROR
]


class Task(TaskModel):
    def __init__(self, description: Optional[str] = None, code: Optional[str] = None):
        if Context.execution is None:
            raise ExecutionNotStardedError("Execution not started")

        super().__init__(
            executionId=Context.execution.id
        )

        self.description = description if description is not None else "Descrição não informada"
        self.code = code if code is not None else str(uuid7())

    def _update(
            self,
            status: Optional[TaskStatus] = None,
            observation: Optional[str] = None,
            description: Optional[str] = None,
            code: Optional[str] = None,
        ) -> dict:
        if status in TASK_STATUS_COMPLETED:
            self.endDate = get_utc_now()

        self.observation = observation if observation is not None else self.observation
        self.description = description if description is not None else self.description
        self.status = status if status is not None else self.status
        self.code = code if code is not None else self.code

        try:
            if self.operation == Operations.CREATE:
                response = client.post(
                    endpoint=f"{self.executionId}/tasks",
                    json=self.model_dump()
                )
            else:
                response = client.patch(
                    endpoint=f"{self.executionId}/tasks",
                    json=self.model_dump()
                )
            response.raise_for_status()
        except Exception as e:
            raise TaskUpdateError(f"Erro ao atualizar task: {str(e)}") from e

        self.operation = Operations.UPDATE

        return self.model_dump()
    
    def _start(self, observation: Optional[str] = None) -> dict:
        return self._update(status=TaskStatus.RUNNING, observation=observation)

    def fail(self, observation: Optional[str] = None) -> dict:
        return self._update(status=TaskStatus.FAIL, observation=observation)

    def validation_error(self, observation: Optional[str] = None) -> dict:
        return self._update(status=TaskStatus.VALIDATION_ERROR, observation=observation)

    def success(self, observation: Optional[str] = None) -> dict:
        return self._update(status=TaskStatus.SUCCESS, observation=observation)

    def __enter__(self):
        self._start()
        Context.task = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.status not in TASK_STATUS_COMPLETED:
            if exc_type is not None:
                self.fail(observation=str(exc_value))
            else:
                self.success()
            
        Context.task = None

        return False