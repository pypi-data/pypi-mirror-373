import random
from datetime import datetime, timedelta, timezone

from faker import Faker

fake = Faker()


def random_hex_status():
    return f"{random.randint(0, 255):02X}"


def single_dtc_item(base_time, index_offset):
    entry_time = (base_time + timedelta(seconds=index_offset)).isoformat()

    entry = {
        "dtcId": f"P{random.randint(1000, 9999)}-{random.randint(10, 99)}",
        "value": random.choice(["ACTIVE", "PASSIVE"]),
        "status": random_hex_status(),
        "description": fake.sentence(nb_words=6),
        "time": entry_time,
        "extension": [],
        "snapshot": [],
    }

    if random.choice([True, False]):
        entry["extension"].append({"bytes": fake.hexify(text="^" * 8)})

    if random.choice([True, False]):
        entry["snapshot"].append({"bytes": fake.hexify(text="^" * 8)})

    return entry


def dtc_factory(num_dtc_entries=1000, items_per_dtc=50):
    base_time = datetime.now(timezone.utc)
    dtc_data = []

    for dtc_index in range(num_dtc_entries):
        dtc_items = [
            single_dtc_item(base_time, dtc_index * items_per_dtc + i)
            for i in range(items_per_dtc)
        ]

        dtc_data.append({"data": dtc_items})

    return dtc_data
