import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import struct_pb2 as _struct_pb2
import rapida.clients.protos.common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VaultCredential(_message.Message):
    __slots__ = ("id", "name", "value", "status", "vaultLevel", "vaultLevelId", "vaultType", "vaultTypeId", "createdDate", "updatedDate", "lastUsedDate")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VAULTLEVEL_FIELD_NUMBER: _ClassVar[int]
    VAULTLEVELID_FIELD_NUMBER: _ClassVar[int]
    VAULTTYPE_FIELD_NUMBER: _ClassVar[int]
    VAULTTYPEID_FIELD_NUMBER: _ClassVar[int]
    CREATEDDATE_FIELD_NUMBER: _ClassVar[int]
    UPDATEDDATE_FIELD_NUMBER: _ClassVar[int]
    LASTUSEDDATE_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    value: _struct_pb2.Struct
    status: str
    vaultLevel: str
    vaultLevelId: int
    vaultType: str
    vaultTypeId: int
    createdDate: _timestamp_pb2.Timestamp
    updatedDate: _timestamp_pb2.Timestamp
    lastUsedDate: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., status: _Optional[str] = ..., vaultLevel: _Optional[str] = ..., vaultLevelId: _Optional[int] = ..., vaultType: _Optional[str] = ..., vaultTypeId: _Optional[int] = ..., createdDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updatedDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., lastUsedDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateProviderCredentialRequest(_message.Message):
    __slots__ = ("providerId", "credential", "name", "providerName")
    PROVIDERID_FIELD_NUMBER: _ClassVar[int]
    CREDENTIAL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROVIDERNAME_FIELD_NUMBER: _ClassVar[int]
    providerId: int
    credential: _struct_pb2.Struct
    name: str
    providerName: str
    def __init__(self, providerId: _Optional[int] = ..., credential: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., name: _Optional[str] = ..., providerName: _Optional[str] = ...) -> None: ...

class CreateToolCredentialRequest(_message.Message):
    __slots__ = ("toolId", "credential", "name", "toolName")
    TOOLID_FIELD_NUMBER: _ClassVar[int]
    CREDENTIAL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TOOLNAME_FIELD_NUMBER: _ClassVar[int]
    toolId: int
    credential: _struct_pb2.Struct
    name: str
    toolName: str
    def __init__(self, toolId: _Optional[int] = ..., credential: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., name: _Optional[str] = ..., toolName: _Optional[str] = ...) -> None: ...

class DeleteCredentialRequest(_message.Message):
    __slots__ = ("vaultId",)
    VAULTID_FIELD_NUMBER: _ClassVar[int]
    vaultId: int
    def __init__(self, vaultId: _Optional[int] = ...) -> None: ...

class GetAllOrganizationCredentialRequest(_message.Message):
    __slots__ = ("paginate", "criterias")
    PAGINATE_FIELD_NUMBER: _ClassVar[int]
    CRITERIAS_FIELD_NUMBER: _ClassVar[int]
    paginate: _common_pb2.Paginate
    criterias: _containers.RepeatedCompositeFieldContainer[_common_pb2.Criteria]
    def __init__(self, paginate: _Optional[_Union[_common_pb2.Paginate, _Mapping]] = ..., criterias: _Optional[_Iterable[_Union[_common_pb2.Criteria, _Mapping]]] = ...) -> None: ...

class GetAllOrganizationCredentialResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error", "paginated")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PAGINATED_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: _containers.RepeatedCompositeFieldContainer[VaultCredential]
    error: _common_pb2.Error
    paginated: _common_pb2.Paginated
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Iterable[_Union[VaultCredential, _Mapping]]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., paginated: _Optional[_Union[_common_pb2.Paginated, _Mapping]] = ...) -> None: ...

class GetProviderCredentialRequest(_message.Message):
    __slots__ = ("providerId", "organizationId")
    PROVIDERID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATIONID_FIELD_NUMBER: _ClassVar[int]
    providerId: int
    organizationId: int
    def __init__(self, providerId: _Optional[int] = ..., organizationId: _Optional[int] = ...) -> None: ...

class GetCredentialResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: VaultCredential
    error: _common_pb2.Error
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Union[VaultCredential, _Mapping]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ...) -> None: ...

class GetCredentialRequest(_message.Message):
    __slots__ = ("vaultId",)
    VAULTID_FIELD_NUMBER: _ClassVar[int]
    vaultId: int
    def __init__(self, vaultId: _Optional[int] = ...) -> None: ...
