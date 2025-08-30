from zsynctech_studio_sdk.enums.operations import Operations
from pydantic import Field, field_validator, BaseModel
from zsynctech_studio_sdk.enums.task import TaskStatus
from zsynctech_studio_sdk.utils import get_utc_now
from uuid_extensions.uuid7 import uuid7
from datetime import datetime
from typing import Optional
import re


class TaskModel(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid7()),
        min_length=1,
        description="ID único da task"
    )

    operation: Operations = Field(
        default=Operations.CREATE,
        description="Operação a ser realizada na task"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=60,
        description="Descrição da task"
    )

    jsonData: Optional[dict] = Field(
        default=None,
        description="Dados JSON da task"
    )

    observation: Optional[str] = Field(
        default=None,
        description="Observação sobre a task"
    )

    code: Optional[str] = Field(
        default=None,
        description="Código da task"
    )

    executionId: Optional[str] = Field(
        min_length=1,
        default=None,
        description="ID da execução"
    )

    status: TaskStatus = Field(
        default=TaskStatus.UNPROCESSED,
        description="Status da task"
    )

    startDate: Optional[str] = Field(
        default=get_utc_now(),
        description="Data de início da task"
    )

    endDate: Optional[str] = Field(
        default=None,
        description="Data de término da task"
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
        if v not in TaskStatus:
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

    @field_validator('executionId')
    @classmethod
    def validate_executionid_format(cls, v):
        """Valida se o executionId é um UUID7 válido"""
        # Verifica se é um UUID válido
        if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', v):
            raise ValueError('executionId deve ser um UUID válido')

        # Verifica se é um UUID7 (primeiro dígito da versão deve ser 7)
        version = int(v[14], 16)
        if version != 7:
            raise ValueError('executionId deve ser um UUID7 válido')

        return v

    @field_validator('description')
    @classmethod
    def validate_description_length(cls, v):
        """Valida se a descrição tem no máximo 60 caracteres"""

        if v is None:
            return v

        if len(v) > 60:
            raise ValueError('description deve ter no máximo 60 caracteres')
        return v

    class Config:
        extra = "forbid"
        validate_assignment = True
        json_schema_extra = {
            "example": {
                "id": "0685b254-3a1f-7bf6-8000-3a0ce7a0a52f",
                "operation": "CREATE",
                "description": "Processar dados do cliente",
                "jsonData": {"clientId": "12345", "action": "process"},
                "observation": "Task executada com sucesso",
                "executionId": "0685b254-3a1f-7bf6-8000-3a0ce7a0a52f",
                "status": "SUCCESS",
                "endDate": "2024-01-15T10:30:00.000Z"
            }
        }
