from rapida.clients.protos.talk_api_pb2 import (
    CreateBulkPhoneCallRequest,
    CreateBulkPhoneCallResponse,
    CreatePhoneCallRequest,
    CreatePhoneCallResponse,
)
from rapida.connections import ConnectionConfig


def create_phone_call(
    client_cfg: ConnectionConfig, request: CreatePhoneCallRequest
) -> CreatePhoneCallResponse:
    return client_cfg.conversation_client.CreatePhoneCall(
        request,
        metadata=client_cfg.auth,
    )


def create_bulk_phone_call(
    client_cfg: ConnectionConfig, request: CreateBulkPhoneCallRequest
) -> CreateBulkPhoneCallResponse:

    return client_cfg.conversation_client.CreateBulkPhoneCall(
        request,
        metadata=client_cfg.auth,
    )
