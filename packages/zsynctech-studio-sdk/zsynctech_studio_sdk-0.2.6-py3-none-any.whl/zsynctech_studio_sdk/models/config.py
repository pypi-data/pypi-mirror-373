from uuid_extensions import uuid7
from typing import Optional, List
from pydantic import BaseModel
from enum import StrEnum


class InputOutputTypes(StrEnum):
    FTP = 'FTP'
    API = 'API'
    FILA = 'FILA'


class Credential(BaseModel):
    key: str
    value: str
    encrypted: bool


class Config(BaseModel):
    instanceId: str
    automationName: Optional[str] = "System"
    clientId: Optional[str] = None
    userId: Optional[str] = "System"
    executionId: Optional[str] = str(uuid7())
    outputPath: Optional[str] = None
    inputPath: Optional[str] = None
    inputMetaData: Optional[dict] = None
    inputType: Optional[InputOutputTypes] = InputOutputTypes.FTP
    outputType: Optional[InputOutputTypes] = InputOutputTypes.FTP
    outputMetaData: Optional[dict] = None
    keepAlive: Optional[bool] = False
    keepAliveInterval: Optional[int] = 30
    credentials: Optional[List[Credential]] = None


if __name__ == "__main__":
    print(Config(
        instanceId='0198cdc7-6e20-74b9-89f8-2a6e975da3db',
        automationName='Robô Benner Eventos',
        clientId='0198c254-dec1-7bc2-9ed2-33f046155d13',
        userId='0198c254-df28-7074-9b48-2567993dcf12',
        executionId='0198d8d5-548f-7c00-baba-12f514b6419a',
        inputPath='/benner/eventos/input',
        inputMetaData=None,
        inputType='FTP',
        outputPath='/benner/eventos/output',
        outputMetaData=None,
        outputType='FTP',
        keepAlive=False,
        keepAliveInterval=None,
        credentials=None
    ).model_dump())