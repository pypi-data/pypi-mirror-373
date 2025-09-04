import logging

from faker import Faker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker()


def configuration_factory():
    vehicle_id = fake.random_int(min=1000, max=10000000)
    device_id = fake.random_int(min=1000, max=10000000)
    organization_id = fake.random_int(min=1000, max=10000000)
    fleet_id = fake.random_int(min=1000, max=10000000)
    return {
        "vehicle_id": vehicle_id,
        "fleet_id": fleet_id,
        "organization_id": organization_id,
        "device_id": device_id,
    }
