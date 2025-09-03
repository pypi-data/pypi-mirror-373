import base64
import json
import socket
from datetime import datetime

import requests
from qwak.inner.di_configuration.account import UserAccountConfiguration
from qwak.inner.tool.auth import Auth0ClientBase, FrogMLAuthClient
from qwak.inner.const import QwakConstants


def _get_authorization():
    user_account_configuration = UserAccountConfiguration()
    if issubclass(user_account_configuration._auth_client, Auth0ClientBase):
        auth_client = Auth0ClientBase()
        tenant_id = None
    else:
        auth_client = FrogMLAuthClient()
        tenant_id = auth_client.get_tenant_id()

    token = auth_client.get_token()
    token_split = token.split(".")
    decoded_token = json.loads(_base64url_decode(token_split[1]).decode("utf-8"))
    token_expiration = datetime.fromtimestamp(decoded_token["exp"])
    return f"Bearer {token}", token_expiration, tenant_id


def _base64url_decode(input):
    rem = len(input) % 4
    if rem > 0:
        input += "=" * (4 - rem)

    return base64.urlsafe_b64decode(input)


class SocketAdapter(requests.adapters.HTTPAdapter):
    def __init__(self, *args, socket_params=None, **kwargs):
        self.socket_params = socket_params
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        if self.socket_params:
            kwargs["socket_options"] = self.socket_params
        super().init_poolmanager(*args, **kwargs)


# Configure only TCP attributes that are available in the OS
def validate_socket_config(socket_options):
    config = []
    for line in socket_options:
        if hasattr(socket, line[0]) and hasattr(socket, line[1]):
            config.append((getattr(socket, line[0]), getattr(socket, line[1]), line[2]))
    return config


class RestSession(requests.Session):
    def __init__(self):
        super().__init__()
        self.headers.update({"Content-Type": "application/json"})
        socket_options = [
            ("SOL_SOCKET", "SO_KEEPALIVE", 1),
            ("SOL_TCP", "TCP_KEEPIDLE", 120),
            ("SOL_TCP", "TCP_KEEPINTVL", 75),
            ("SOL_TCP", "TCP_KEEPCNT", 9),
        ]
        socket_options = validate_socket_config(socket_options)
        adapter = SocketAdapter(socket_params=socket_options)
        self.mount("https://", adapter)

    def prepare_request(self, request):
        if "Authorization" not in self.headers:
            self.prepare_request_token()
        else:
            if self.jwt_expiration <= datetime.utcnow():
                self.prepare_request_token()

        return super().prepare_request(request)

    def prepare_request_token(self):
        auth_token, self.jwt_expiration, tenant_id = _get_authorization()
        self.headers["Authorization"] = auth_token

        if tenant_id:
            self.headers[QwakConstants.JFROG_TENANT_HEADER_KEY] = tenant_id
