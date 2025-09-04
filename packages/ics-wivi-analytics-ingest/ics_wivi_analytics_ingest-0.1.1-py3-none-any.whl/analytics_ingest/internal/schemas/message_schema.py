from typing import Optional

from pydantic import BaseModel


class MessageSchema(BaseModel):
    arbId: Optional[str] = ""
    name: str
    networkName: str = ""
    ecuName: Optional[str] = ""
    ecuId: Optional[str] = ""
    fileId: Optional[str] = ""
    messageDate: Optional[str] = ""
    requestCode: Optional[str] = ""

    @classmethod
    def from_variables(cls, variables):
        name = variables.get("messageName") or variables["name"]
        return cls(
            arbId=variables.get("arbId", ""),
            name=name,
            networkName=variables.get("networkName", ""),
            ecuName=variables.get("ecuName", ""),
            ecuId=variables.get("ecuId", ""),
            fileId=variables.get("fileId", ""),
            messageDate=variables.get("messageDate", ""),
            requestCode=variables.get("requestCode", ""),
        )

    def cache_key(self) -> str:
        return f"{self.name}|{self.networkName}|{self.ecuName}|{self.arbId}"
