from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, ValidationError, field_serializer
from DLMS_SPODES.settings import toml_data


class Worker(BaseModel):
    run: bool = Field(default=False, title="auto running")
    time_checking: float = Field(default=1.0, title="time checking")


class Storage(BaseModel):
    persistent_depth: int = Field(default=1000, title="persistent depth")
    volatile_depth: int = Field(default=100, title="volatile depth")


class Session(BaseModel):
    result_storage: Storage = Field(default_factory=Storage, title="result storage")
    work_storage: Storage = Field(
        default=Storage(
            persistent_depth=100,
            volatile_depth=10),
        title="work storage")
    worker: Worker = Field(default_factory=Worker, title="Рабочий")


class HeaderNamesCSV(BaseModel):
    secret: list[str] = Field(default=["secret"])
    ip: list[str] = Field(default=["ip"])
    name: list[str] = Field(default=["name"])
    port: list[str] = Field(default=["port"])
    m_id: list[str] = Field(default=["m_id"])
    sap: list[str] = Field(default=["sap"])
    da: list[str] = Field(default=["da"])
    timeout: list[str] = Field(default=["timeout"])


class CSV(BaseModel):
    header_names: HeaderNamesCSV = Field(default_factory=HeaderNamesCSV)


class Settings(BaseModel):
    session: Session = Field(default_factory=Session, title="Session")
    from_csv: CSV = Field(default_factory=CSV, title="from CSV")


data = toml_data.get("DLMSClient", {})
settings = Settings(**data)
print(settings)
