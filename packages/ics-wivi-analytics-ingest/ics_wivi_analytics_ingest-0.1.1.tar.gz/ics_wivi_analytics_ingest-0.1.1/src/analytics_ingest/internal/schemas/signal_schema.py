from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, root_validator, validator


class SignalType(str, Enum):
    SIGNAL = "SIGNAL"
    DID = "DID"
    PID = "PID"
    DMR = "DMR"


class ParamType(str, Enum):
    ENCODED = "ENCODED"
    RAW = "RAW"
    TEXT = "TEXT"
    NUMBER = "NUMBER"
    STRING = "STRING"


class SignalDataInput(BaseModel):
    value: Optional[float] = None
    svalue: Optional[str] = None
    time: str

    @root_validator(pre=True)
    def check_time(cls, values):
        if "time" not in values or values["time"] is None:
            raise ValueError("Missing required 'time' field in SignalDataInput")
        return values


class SignalSchema(BaseModel):
    configurationId: int
    messageId: int
    name: str
    unit: str
    paramType: Optional[ParamType] = None
    paramId: Optional[str] = ""
    signalType: Optional[SignalType] = None
    data: List[SignalDataInput]

    @validator("signalType", pre=True, always=True)
    def validate_signal_type(cls, v):
        if not v:
            return None
        try:
            return SignalType(v.upper())
        except ValueError:
            raise ValueError(f"Invalid signalType: {v}")

    @validator("paramType", pre=True, always=True)
    def validate_param_type(cls, v):
        if not v:
            return None
        normalized = cls.get_vehicle_param_type(v)
        try:
            return ParamType(normalized)
        except ValueError:
            raise ValueError(
                f"Invalid paramType after normalization: {v} -> {normalized}"
            )

    @staticmethod
    def get_vehicle_param_type(value):
        type_mapping = {
            "RawValue": "RAW",
            "State Encoded": "ENCODED",
            "NUMBER": "RAW",
            "string": "STRING",
        }
        return type_mapping.get(value, "TEXT")

    @classmethod
    def from_variables(cls, config_id, message_id, batch, variables):
        parsed_data = []
        for entry in batch:
            if "value" in entry or "svalue" in entry:
                if "timestamp" in entry:
                    entry["time"] = cls().parseTime(entry)
                parsed_data.append(
                    {k: v for k, v in entry.items() if k in {"value", "svalue", "time"}}
                )
        return cls(
            configurationId=config_id,
            messageId=message_id,
            name=variables["name"],
            paramId=variables.get("paramId", ""),
            paramType=variables.get("paramType", ""),
            signalType=variables.get("signalType", ""),
            unit=variables["unit"],
            data=parsed_data,
        )

    def parseTime(self, entry):
        ts = entry["timestamp"]
        if isinstance(ts, (int, float)):
            return datetime.utcfromtimestamp(ts / 1000).strftime("%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(ts, str):
            ts_str = ts[:-3] if "." in ts else ts
            dt = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            raise ValueError(f"Unknown timestamp format: {ts}")
