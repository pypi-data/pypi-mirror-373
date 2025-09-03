from typing import Any

import clearskies
import requests


def create(
    api_key: str,
    requests: requests.Session,
    uuid: Any,
    for_rotate: bool = False,
) -> dict[str, Any]:
    """Create/fetch credentials from the OpenApi service."""
    label = "root" if for_rotate else "temporary"
    create_response = requests.post(
        "https://api.openai.com/v1/organization/admin_api_keys",
        json={
            "name": f"Akeyless {label} user {uuid.uuid4()}",
        },
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    if create_response.status_code != 200:
        raise clearskies.exceptions.ClientError(
            f"Error from Open API: status code {create_response.status_code}, message "
            + create_response.content.decode("utf-8")
        )
    response_data = create_response.json()
    if not response_data.get("value"):
        raise clearskies.exceptions.ClientError(
            f"Error from Open API: received 200 response but I can't find the new secret value.  Sorry :("
        )
    return {
        "api_key": response_data["value"],
        "id": response_data["id"],
    }
