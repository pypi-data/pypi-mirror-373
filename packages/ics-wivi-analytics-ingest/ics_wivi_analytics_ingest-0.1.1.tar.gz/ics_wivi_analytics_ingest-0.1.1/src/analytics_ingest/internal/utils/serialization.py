import json
from datetime import datetime


def serialize_payload(payload):
    return json.loads(
        json.dumps(
            payload, default=lambda o: o.isoformat() if isinstance(o, datetime) else o
        )
    )
