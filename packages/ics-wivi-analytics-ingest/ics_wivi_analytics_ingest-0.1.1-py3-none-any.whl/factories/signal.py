import logging
from datetime import datetime, timedelta

from faker import Faker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from factories import message_factory

fake = Faker()


def signal_factory(vehicle_id):
    units = ["RPM", "km/h", "m/s", "kPa", "degC"]
    param_types = ["NUMBER", "STRING", "TEXT"]
    signal_types = ["SIGNAL", "DID", "PID", "DMR"]
    message = message_factory(vehicle_id=vehicle_id)[0]

    return {
        "name": f"Signal_{fake.word()}_{fake.random_int(min=1000, max=9999)}",
        "unit": fake.random_element(units),
        "paramType": fake.random_element(param_types),
        "signalType": fake.random_element(signal_types),
        "paramId": f"param_{fake.random_int(min=1000, max=9999)}",
        "messageName": message["name"],
        "ecuId": message["ecuId"],
        "arbId": message["arbId"],
        "messageDate": message["messageDate"],
        "fileId": message["fileId"],
        "requestCode": message["requestCode"],
        "networkName": message["networkName"],
        "ecuName": message["ecuName"],
        "data": [
            {
                "value": fake.pyfloat(
                    min_value=1000, max_value=10000000, right_digits=1
                ),
                "time": (
                    fake.date_time_between(start_date="-1d", end_date="now")
                    + timedelta(seconds=i)
                ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            for i in range(10)
        ],
    }
