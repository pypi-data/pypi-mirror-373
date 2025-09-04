from pydantic import BaseModel


class ConfigurationSchema(BaseModel):
    deviceId: int
    fleetId: int
    organizationId: int
    vehicleId: int

    @classmethod
    def from_variables(cls, variables: dict) -> "ConfigurationSchema":
        return cls(
            deviceId=variables["device_id"],
            fleetId=variables["fleet_id"],
            organizationId=variables["org_id"],
            vehicleId=variables["vehicle_id"],
        )
