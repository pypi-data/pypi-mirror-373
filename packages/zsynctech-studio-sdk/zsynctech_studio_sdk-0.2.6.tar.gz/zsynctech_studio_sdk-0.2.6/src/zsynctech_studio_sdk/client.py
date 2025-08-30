from httpx import Client, Response

_instance_id = None
_secret_key = None
_client = None
_server = None
_gateway = "automation-gateway"

def set_credentials(
    instance_id: str,
    server: str,
    secret_key: str
):
    global _instance_id, _client, _server, _secret_key, _gateway

    _secret_key = secret_key
    _instance_id = instance_id
    _server = str(server).rstrip("/")
    base_url = f"{_server}/{_gateway}/{_instance_id}"

    _client = Client(
        base_url=base_url,
        headers={
            "Authorization": f"Bearer {_secret_key}",
            "Content-Type": "application/json"
        },
        timeout=10
    )


def request(method: str, endpoint: str, **kwargs):
    if _client is None:
        raise RuntimeError("Credentials not set. Call set_credentials() first.")
    
    response = _client.request(method, endpoint, **kwargs)
    response.raise_for_status()

    return response


def get(endpoint: str, params: dict = None) -> Response:
    return request("GET", endpoint, params=params)


def post(endpoint: str, json: dict = None) -> Response:
    return request("POST", endpoint, json=json)


def put(endpoint: str, json: dict = None) -> Response:
    return request("PUT", endpoint, json=json)


def patch(endpoint: str, json: dict = None) -> Response:
    return request("PATCH", endpoint, json=json)
