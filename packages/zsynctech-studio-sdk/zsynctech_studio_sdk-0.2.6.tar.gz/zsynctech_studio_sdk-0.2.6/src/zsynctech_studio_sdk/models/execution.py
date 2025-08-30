from pydantic import Field, field_validator, model_validator, BaseModel
from zsynctech_studio_sdk.enums.execution import ExecutionStatus
from uuid_extensions.uuid7 import uuid7
from datetime import datetime
from typing import Optional
import re


class ExecutionModel(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid7()),
        min_length=1,
        description="ID único da execução"
    )

    observation: Optional[str] = Field(
        default=None,
        description="Observação sobre a execução"
    )

    status: Optional[ExecutionStatus] = Field(
        default=ExecutionStatus.WAITING,
        description="Status atual da execução"
    )

    endDate: Optional[str] = Field(
        default=None,
        description="Data de término no formato ISO 8601 com Z"
    )

    totalTaskCount: Optional[int] = Field(
        ge=0,
        default=0,
        description="Número total de tarefas"
    )

    currentTaskCount: Optional[int] = Field(
        ge=0,
        default=0,
        description="Número de tarefas executadas"
    )

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
            raise ValueError('endDate deve ser uma data válida')

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

    @model_validator(mode='after')
    def validate_business_rules(self):
        """Valida regras de negócio que dependem de múltiplos campos"""
        # Valida se current_task_count não excede total_task_count
        current = self.currentTaskCount or 0
        total = self.totalTaskCount or 0
        if current > total:
            raise ValueError('currentTaskCount não pode ser maior que totalTaskCount')

        return self

    class Config:
        extra = "forbid"
        validate_assignment = True
        json_schema_extra = {
            "example": {
                "id": "0685b254-3a1f-7bf6-8000-3a0ce7a0a52f",
                "observation": "Execução de teste bem-sucedida",
                "status": "FINISHED",
                "endDate": "2024-01-15T10:30:00.000Z",
                "totalTaskCount": 10,
                "currentTaskCount": 10
            }
        }
