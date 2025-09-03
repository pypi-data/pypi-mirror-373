import clearskies
import clearskies_akeyless_custom_producer
from clearskies import columns, validators

from clearskies_akeyless_custom_openapi.create import create
from clearskies_akeyless_custom_openapi.revoke import revoke


class PayloadSchema(clearskies.Schema):
    api_key = columns.String(
        validators=[validators.Required()],
    )
    id = columns.String(
        validators=[validators.Required()],
    )


def build_openapi_producer(url: str = "") -> clearskies_akeyless_custom_producer.endpoints.NoInput:
    """
    Build the OpenApi producer with create/rotate/revoke endpoints.

    Args:
        url (str): Optional URL prefix for the endpoints

    Returns:
        clearskies_akeyless_custom_producer.endpoints.NoInput: The configured producer
    """
    return clearskies_akeyless_custom_producer.endpoints.NoInput(
        create_callable=create,
        revoke_callable=revoke,
        payload_schema=PayloadSchema,
        url=url,
        id_column_name="id",
    )
