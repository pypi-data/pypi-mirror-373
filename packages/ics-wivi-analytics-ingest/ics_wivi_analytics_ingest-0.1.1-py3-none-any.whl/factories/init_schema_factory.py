from analytics_ingest.internal.schemas.ingest_config_schema import IngestConfigSchema
from tests.test_settings import GRAPHQL_ENDPOINT


def init_schema_factory(**overrides):
    base = {
        "device_id": 1,
        "vehicle_id": 2,
        "fleet_id": 3,
        "org_id": 4,
        "graphql_endpoint": GRAPHQL_ENDPOINT,
        "batch_size": 50,
        "batch_interval_seconds": 5,
        "debug": True,
    }
    base.update(overrides)
    return base
