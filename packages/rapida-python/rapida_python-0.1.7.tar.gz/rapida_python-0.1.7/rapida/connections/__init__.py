"""
# Copyright (c) 2024. Rapida
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Author: Prashant <prashant@rapida.ai>
"""

from typing import Optional, TypedDict
from rapida.configs import (
    ASSISTANT_API,
    ENDPOINT_API,
    LOCAL_ASSISTANT_API,
    LOCAL_ENDPOINT_API,
    LOCAL_WEB_API,
    WEB_API,
)
from rapida.utils.rapida_source import RapidaSource
from rapida.utils.rapida_header import (
    HEADER_API_KEY,
    HEADER_AUTH_ID,
    HEADER_PROJECT_ID,
    HEADER_SOURCE_KEY,
)
from rapida.clients.protos.talk_api_pb2_grpc import TalkServiceStub
from rapida.clients.protos.assistant_api_pb2_grpc import AssistantServiceStub
from rapida.clients.protos.invoker_api_pb2_grpc import DeploymentStub
from rapida.clients.protos.web_api_pb2_grpc import (
    AuthenticationServiceStub,
    OrganizationServiceStub,
    ProjectServiceStub,
)
from rapida.clients.protos.knowledge_api_pb2_grpc import KnowledgeServiceStub
from rapida.clients.protos.document_api_pb2_grpc import DocumentServiceStub
from rapida.clients.protos.vault_api_pb2_grpc import VaultServiceStub
from rapida.clients.protos.endpoint_api_pb2_grpc import EndpointServiceStub
from rapida.clients.protos.audit_logging_api_pb2_grpc import AuditLoggingServiceStub
from rapida.clients.protos.marketplace_api_pb2_grpc import MarketplaceServiceStub
from rapida.clients.protos.assistant_deployment_pb2_grpc import (
    AssistantDeploymentServiceStub,
)
from rapida.clients.protos.connect_api_pb2_grpc import ConnectServiceStub
from rapida.clients.protos.provider_api_pb2_grpc import ProviderServiceStub
import grpc


class UserAuthInfo(TypedDict):
    authorization: str
    auth_id: str
    project_id: str
    Client: dict[str, str]


class ClientAuthInfo(TypedDict):
    api_key: str
    auth_id: Optional[str]
    Client: dict[str, str]


class ConnectionConfig:
    @staticmethod
    def with_debugger(
        authorization: str, user_id: str, project_id: str
    ) -> UserAuthInfo:
        return {
            "authorization": authorization,
            HEADER_AUTH_ID: user_id,
            HEADER_PROJECT_ID: project_id,
            HEADER_SOURCE_KEY: RapidaSource.DEBUGGER.get(),
        }

    @staticmethod
    def with_personal_token(
        authorization: str, auth_id: str, project_id: str
    ) -> UserAuthInfo:
        return {
            "authorization": authorization,
            HEADER_AUTH_ID: auth_id,
            HEADER_PROJECT_ID: project_id,
            HEADER_SOURCE_KEY: RapidaSource.SDK.get(),
        }

    @staticmethod
    def with_webplugin_client(api_key: str, user_id: str = None) -> ClientAuthInfo:
        return {
            HEADER_API_KEY: api_key,
            HEADER_AUTH_ID: user_id,
            HEADER_SOURCE_KEY: RapidaSource.WEB_PLUGIN.get(),
        }

    @staticmethod
    def with_sdk(api_key: str, user_id: str = None) -> ClientAuthInfo:
        return {
            HEADER_API_KEY: api_key,
            HEADER_AUTH_ID: user_id,
            HEADER_SOURCE_KEY: RapidaSource.SDK.get(),
        }

    def __init__(self, endpoint=None, debug=False):
        self._endpoint = endpoint or {
            "assistant": ASSISTANT_API,
            "web": WEB_API,
            "endpoint": ENDPOINT_API,
        }
        self._debug = debug
        self._auth = None

    def get_client_options(self):
        return {"debug": self._debug}

    @property
    def conversation_client(self):
        return TalkServiceStub(self._create_channel(self._endpoint["assistant"]))

    @property
    def assistant_client(self):
        return AssistantServiceStub(self._create_channel(self._endpoint["web"]))

    @property
    def project_client(self):
        return ProjectServiceStub(self._create_channel(self._endpoint["web"]))

    @property
    def knowledge_client(self):
        return KnowledgeServiceStub(self._create_channel(self._endpoint["web"]))

    @property
    def deployment_client(self):
        return DeploymentStub(self._create_channel(self._endpoint["web"]))

    @property
    def marketplace_client(self):
        return MarketplaceServiceStub(self._create_channel(self._endpoint["web"]))

    @property
    def document_client(self):
        return DocumentServiceStub(self._create_channel(self._endpoint["web"]))

    @property
    def vault_client(self):
        return VaultServiceStub(self._create_channel(self._endpoint["web"]))

    @property
    def endpoint_client(self):
        return EndpointServiceStub(self._create_channel(self._endpoint["web"]))

    @property
    def audit_logging_client(self):
        return AuditLoggingServiceStub(self._create_channel(self._endpoint["web"]))

    @property
    def assistant_deployment_client(self):
        return AssistantDeploymentServiceStub(
            self._create_channel(self._endpoint["web"])
        )

    @property
    def organization_client(self):
        return OrganizationServiceStub(self._create_channel(self._endpoint["web"]))

    @property
    def connect_client(self):
        return ConnectServiceStub(self._create_channel(self._endpoint["web"]))

    @property
    def provider_client(self):
        return ProviderServiceStub(self._create_channel(self._endpoint["web"]))

    @property
    def authentication_client(self):
        return AuthenticationServiceStub(self._create_channel(self._endpoint["web"]))

    def with_local(self):
        return self.with_custom_endpoint(
            {
                "assistant": LOCAL_ASSISTANT_API,
                "web": LOCAL_WEB_API,
                "endpoint": LOCAL_ENDPOINT_API,
            },
            True,
        )

    @property
    def auth(self) -> list[tuple[str, str]]:
        if self._auth is not None:
            return (
                list(self._auth.items()) if isinstance(self._auth, dict) else self._auth
            )
        return []

    def with_custom_endpoint(self, endpoint=None, debug=None):
        self._endpoint = endpoint or {
            "assistant": ASSISTANT_API,
            "web": WEB_API,
            "endpoint": ENDPOINT_API,
        }
        if debug is not None:
            self._debug = debug
        return self

    def with_auth(self, auth):
        self._auth = auth
        return self

    @staticmethod
    def default_connection_config(auth):
        cc = ConnectionConfig()
        cc.with_auth(auth)
        return cc

    def _create_channel(self, endpoint):
        if self._debug:
            return grpc.insecure_channel(endpoint)
        else:
            return grpc.secure_channel(endpoint, grpc.ssl_channel_credentials())


__all__ = ["ConnectionConfig"]
