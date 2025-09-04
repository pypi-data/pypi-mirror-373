import random
from datetime import datetime, timedelta, timezone

from faker import Faker

fake = Faker()


def gps_factory(num_entries=120):
    base_time = datetime.now(timezone.utc)
    gps_data = []

    for i in range(num_entries):
        timestamp = (base_time + timedelta(seconds=i)).isoformat()
        entry = {
            "time": timestamp,
            "latitude": float(round(fake.latitude(), 6)),
            "longitude": float(round(fake.longitude(), 6)),
            "accuracy": float(round(random.uniform(5.0, 50.0), 2)),
            "altitude": float(round(random.uniform(100.0, 1000.0), 2)),
            "speed": float(round(random.uniform(0.0, 120.0), 2)),
            "bearing": float(round(random.uniform(0.0, 120.0), 2)),
            "available": {
                "accuracy": bool(random.getrandbits(1)),
                "altitude": bool(random.getrandbits(1)),
                "bearing": bool(random.getrandbits(1)),
                "speed": bool(random.getrandbits(1)),
                "time": bool(random.getrandbits(1)),
            },
        }
        gps_data.append(entry)

    return gps_data
