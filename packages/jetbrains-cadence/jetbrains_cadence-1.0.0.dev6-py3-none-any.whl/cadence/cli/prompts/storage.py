import click

from cadence.api.model.storage import Storage

ACCELERATE_ENDPOINT_URL = "https://s3-accelerate.amazonaws.com"


def read_storage_data_from_user(name: str) -> Storage:
    access_key_id = click.prompt("Access key ID", type=str)
    secret_access_key = click.prompt("Secret access key", type=str, hide_input=True)

    session_token = click.prompt("Session token (optional)", type=str, default="", hide_input=True, show_default=False)
    if session_token == "":
        session_token = None

    bucket = click.prompt("Bucket", type=str)

    endpoint_url = click.prompt("Custom endpoint URL (optional)", type=str, default="", show_default=False)
    if endpoint_url == "":
        use_acceleration_endpoint = click.confirm(f"Use acceleration endpoint?")
        if use_acceleration_endpoint:
            endpoint_url = ACCELERATE_ENDPOINT_URL
        else:
            endpoint_url = None

    return Storage(name=name,
                          accessKeyId=access_key_id,
                          secretAccessKey=secret_access_key,
                          sessionToken=session_token,
                          endpointUrl=endpoint_url,
                          bucket=bucket)
