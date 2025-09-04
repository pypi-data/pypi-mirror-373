from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class BytesInput(BaseModel):
    bytes: str


class DTCSchema(BaseModel):
    dtcId: str
    status: str
    description: str
    time: datetime
    extended: Optional[List[BytesInput]] = None
    snapshot: Optional[List[BytesInput]] = None

    @classmethod
    def from_variables(cls, variables: dict) -> list["DTCSchema"]:
        return [cls(**item) for item in variables.get("data", [])]
