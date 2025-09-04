from analytics_ingest.internal.schemas.message_schema import MessageSchema
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.mutations import GraphQLMutations

_message_cache = {}


def get_cached_message_id(key: str) -> str | None:
    return _message_cache.get(key)


def create_message(executor: GraphQLExecutor, variables: list[dict]) -> list[str]:
    message_ids = []
    uncached_messages = []
    comparison_keys = []

    for var in variables:
        key = generate_message_cache_key(var)

        if key in _message_cache:
            message_ids.append(_message_cache[key])
        else:
            input_dict = {
                "arbId": var.get("arbId"),
                "name": var.get("messageName") or var.get("name"),
                "networkName": var.get("networkName"),
                "ecuName": var.get("ecuName"),
                "ecuId": var.get("ecuId"),
                "requestCode": var.get("requestCode"),
                "fileId": var.get("fileId"),
                "messageDate": var.get("messageDate"),
            }
            comparison_keys.append(key)
            uncached_messages.append(input_dict)

    if uncached_messages:
        response = executor.execute(
            GraphQLMutations.create_message(),
            {"input": {"messages": uncached_messages}},
        )
        if "errors" in response:
            error_message = f"Error in create_message response: {response['errors']}"
            raise RuntimeError("Error in create_message_response: %s", error_message)

        messages = response["data"].get("createMessage", [])
        if not messages:
            raise RuntimeError("No messages created")

        for idx, input_dict in enumerate(uncached_messages):
            key = comparison_keys[idx]
            key_fields = ["arbId", "networkName", "ecuName", "name"]

            def normalize(val):
                return (val or "").strip()

            matching = next(
                (
                    m
                    for m in messages
                    if all(
                        normalize(m.get(k)) == normalize(input_dict.get(k))
                        for k in key_fields
                    )
                ),
                None,
            )

            if matching:
                _message_cache[key] = str(matching["id"])
                message_ids.append(str(matching["id"]))

    return message_ids


def generate_message_cache_key(data: dict) -> str:
    """Consistent key used for message caching and lookup."""

    def safe(val):
        return str(val or '').strip()

    return f"{safe(data.get('arbId'))}|{safe(data.get('networkName'))}|{safe(data.get('ecuName'))}|{safe(data.get('messageName') or data.get('name'))}"
