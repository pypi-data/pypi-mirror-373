import os
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class IngestConfigSchema(BaseModel):
    device_id: int
    vehicle_id: int
    fleet_id: int
    org_id: int

    batch_interval_seconds: Optional[float] = Field(
        default=1, ge=0.1, description="Must be >= 0.1"
    )
    batch_size: Optional[int] = Field(default=1, ge=1, description="Must be >= 1")
    graphql_endpoint: str = Field(default_factory=lambda: os.getenv("GRAPH_ENDPOINT"))
    max_signal_count: Optional[int] = Field(default=1, ge=1)
    debug: Optional[bool] = True
    jwt_token: Optional[str] = Field(
        default_factory=lambda: os.getenv("SEC_AUTH_TOKEN")
    )

    @model_validator(mode="after")
    def validate_env_or_param(self):
        if not self.graphql_endpoint:
            raise ValueError(
                "Missing GraphQL endpoint. Set via param or GRAPH_ENDPOINT env."
            )
        return self
