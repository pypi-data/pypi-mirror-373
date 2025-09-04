from datetime import datetime

from analytics_ingest.internal.schemas.dtc_schema import DTCSchema
from analytics_ingest.internal.schemas.message_schema import MessageSchema
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.message import (
    generate_message_cache_key,
    get_cached_message_id,
)
from analytics_ingest.internal.utils.mutations import GraphQLMutations
from analytics_ingest.internal.utils.serialization import serialize_payload


def create_dtc(
    executor: GraphQLExecutor,
    config_id: str,
    dtc: dict,
):
    file_id = dtc.get("fileId", "")
    message_date = dtc.get("messageDate", "")
    message_key = generate_message_cache_key(dtc)
    message_id = get_cached_message_id(message_key)
    if not message_id:
        raise RuntimeError(f"No message ID found for key: {message_key}")

    dtc_items = DTCSchema.from_variables(dtc)

    payload_data = {
        "fileId": file_id,
        "configurationId": config_id,
        "messageId": int(message_id),
        "messageDate": message_date,
        "data": [item.model_dump() for item in dtc_items],
    }

    payload = serialize_payload({"input": payload_data})
    executor.execute(GraphQLMutations.upsert_dtc_mutation(), payload)
