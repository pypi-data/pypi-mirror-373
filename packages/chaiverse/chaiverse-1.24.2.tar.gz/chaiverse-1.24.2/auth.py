from chaiverse.http_client import AuthClient


def get_login_url(redirect_uri, provider="huggingface"):
    auth_client = AuthClient()
    payload = {"redirect_uri": redirect_uri}
    response = auth_client.post(f"/oauth2/{provider}/authorize", json=payload)
    return response["login_url"]
