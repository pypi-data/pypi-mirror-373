from zsynctech_studio_sdk.enums.operations import Operations
from pydantic import Field, field_validator, BaseModel
from zsynctech_studio_sdk.enums.step import StepStatus
from zsynctech_studio_sdk.utils import get_utc_now
from uuid_extensions.uuid7 import uuid7
from datetime import datetime
from typing import Optional
import re


class StepModel(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid7()),
        min_length=1,
        description="ID único do step"
    )

    observation: Optional[str] = Field(
        default=None,
        description="Observação sobre o step"
    )

    operation: Operations = Field(
        default=Operations.CREATE,
        description="Operação a ser realizada no step"
    )

    taskId: Optional[str] = Field(
        min_length=1,
        default=None,
        description="ID da tarefa a ser realizada no step"
    )

    automationOnClientId: Optional[str] = Field(
        default=None,
        min_length=1,
        description="ID do cliente da automação"
    )

    status: StepStatus = Field(
        default=StepStatus.UNPROCESSED,
        description="Status do step"
    )

    stepCode: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Código do step"
    )

    startDate: Optional[str] = Field(
        default=get_utc_now(),
        description="Data de término do step"
    )

    endDate: Optional[str] = Field(
        default=None,
        description="Data de término do step"
    )

    @field_validator('startDate')
    @classmethod
    def validate_start_date_format(cls, v):
        """Valida o formato da data de término"""
        if v is None:
            return v

        # Regex para formato ISO 8601 com Z no final
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$'
        if not re.match(pattern, v):
            raise ValueError('endDate deve estar no formato ISO 8601 com Z (ex: 2024-01-15T10:30:00.000Z)')

        # Valida se é uma data válida
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('end_date deve ser uma data válida')

        return v

    @field_validator('endDate')
    @classmethod
    def validate_end_date_format(cls, v):
        """Valida o formato da data de término"""
        if v is None:
            return v

        # Regex para formato ISO 8601 com Z no final
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$'
        if not re.match(pattern, v):
            raise ValueError('endDate deve estar no formato ISO 8601 com Z (ex: 2024-01-15T10:30:00.000Z)')

        # Valida se é uma data válida
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('end_date deve ser uma data válida')

        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Valida se o status é um status válido"""
        if v not in StepStatus:
            raise ValueError('status deve ser um status válido')
        return v

    @field_validator('id')
    @classmethod
    def validate_id_format(cls, v):
        """Valida se o ID é um UUID7 válido"""
        # Verifica se é um UUID válido
        if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', v):
            raise ValueError('ID deve ser um UUID válido')

        # Verifica se é um UUID7 (primeiro dígito da versão deve ser 7)
        version = int(v[14], 16)
        if version != 7:
            raise ValueError('ID deve ser um UUID7 válido')

        return v

    @field_validator('taskId')
    @classmethod
    def validate_task_id_format(cls, v):
        """Valida se o task_id é um UUID7 válido"""
        # Verifica se é um UUID válido
        if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', v):
            raise ValueError('taskId deve ser um UUID válido')

        # Verifica se é um UUID7 (primeiro dígito da versão deve ser 7)
        version = int(v[14], 16)
        if version != 7:
            raise ValueError('taskId deve ser um UUID7 válido')

        return v

    @field_validator('automationOnClientId')
    @classmethod
    def validate_automation_on_cliente_id_format(cls, v):
        """Valida se o automationOnClientId é um UUID7 válido"""
        if v is None:
            return v

        # Verifica se é um UUID válido
        if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', v):
            raise ValueError('automationOnClientId deve ser um UUID válido')

        # Verifica se é um UUID7 (primeiro dígito da versão deve ser 7)
        version = int(v[14], 16)
        if version != 7:
            raise ValueError('automationOnClientId deve ser um UUID7 válido')

        return v

    class Config:
        extra = "forbid"
        validate_assignment = True
        json_schema_extra = {
            "example": {
                "id": "0685b254-3a1f-7bf6-8000-3a0ce7a0a52f",
                "observation": "Execução bem-sucedida",
                "operation": "CREATE",
                "taskId": "0685b254-3a1f-7bf6-8000-3a0ce7a0a52f",
                "automationOnClienteId": "0685b254-3a1f-7bf6-8000-3a0ce7a0a52f",
                "status": "SUCCESS",
                "stepCode": "0001",
                "endDate": "2024-01-15T10:30:00.000Z"
            }
        }

    