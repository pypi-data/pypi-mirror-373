import logging

from faker import Faker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker()


def message_factory(vehicle_id):
    return [
        {
            "name": f"TestMessage_{vehicle_id}",
            "networkName": "CAN",
            "arbId": f"0x{fake.random_int(min=100, max=999):03X}",
            "ecuId": f"ECU{fake.random_int(min=1, max=9)}",
            "messageDate": fake.date_time_between(
                start_date="-1y", end_date="now"
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "requestCode": f"Code_{fake.word()}",
            "ecuName": f"ECU_{fake.word()}",
            "fileId": f"File_{fake.random_int(min=1, max=9)}",
        }
    ]
