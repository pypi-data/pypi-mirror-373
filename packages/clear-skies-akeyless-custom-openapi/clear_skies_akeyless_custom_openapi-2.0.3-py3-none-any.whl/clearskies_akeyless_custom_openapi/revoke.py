from typing import Any

import clearskies
import requests


def revoke(
    api_key: str,
    id_to_delete: str,
    requests: requests.Session,
) -> None:
    """Revoke credentials for the OpenApi service."""
    delete_response = requests.delete(
        f"https://api.openai.com/v1/organization/admin_api_keys/{id_to_delete}",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    if delete_response.status_code != 200:
        raise clearskies.exceptions.ClientError(
            f"Error from Open API: status code {delete_response.status_code}, message "
            + delete_response.content.decode("utf-8")
        )
