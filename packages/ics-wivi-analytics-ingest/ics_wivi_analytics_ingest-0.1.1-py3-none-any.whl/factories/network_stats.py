import random
from datetime import datetime, timedelta

from faker import Faker

fake = Faker()


def network_stats_factory(vehicle_id: int) -> dict:
    base_time = datetime.utcnow()

    return {
        "errorMessages": random.randint(1, 200),
        "longMessageParts": random.randint(1, 200),
        "matchedMessages": random.randint(100, 200),
        "maxTime": (base_time + timedelta(minutes=random.randint(1, 60))).isoformat()
        + "Z",
        "minTime": (base_time - timedelta(minutes=random.randint(1, 60))).isoformat()
        + "Z",
        "name": fake.domain_word(),
        "rate": round(random.uniform(1.0, 100.0), 2),
        "totalMessages": random.randint(200, 500),
        "unmatchedMessages": random.randint(0, 100),
        "uploadId": 4255,
        "vehicleId": vehicle_id,
    }
