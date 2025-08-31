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

class GetAllDeploymentRequest(_message.Message):
    __slots__ = ("paginate", "criterias")
    PAGINATE_FIELD_NUMBER: _ClassVar[int]
    CRITERIAS_FIELD_NUMBER: _ClassVar[int]
    paginate: _common_pb2.Paginate
    criterias: _containers.RepeatedCompositeFieldContainer[_common_pb2.Criteria]
    def __init__(self, paginate: _Optional[_Union[_common_pb2.Paginate, _Mapping]] = ..., criterias: _Optional[_Iterable[_Union[_common_pb2.Criteria, _Mapping]]] = ...) -> None: ...

class SearchableDeployment(_message.Message):
    __slots__ = ("id", "status", "visibility", "type", "projectId", "organizationId", "tag", "language", "organization", "name", "description", "createdDate", "updatedDate", "appAppearance", "webAppearance", "modelProviderId", "modelProviderName", "modelOptions")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PROJECTID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATIONID_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATEDDATE_FIELD_NUMBER: _ClassVar[int]
    UPDATEDDATE_FIELD_NUMBER: _ClassVar[int]
    APPAPPEARANCE_FIELD_NUMBER: _ClassVar[int]
    WEBAPPEARANCE_FIELD_NUMBER: _ClassVar[int]
    MODELPROVIDERID_FIELD_NUMBER: _ClassVar[int]
    MODELPROVIDERNAME_FIELD_NUMBER: _ClassVar[int]
    MODELOPTIONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    status: str
    visibility: str
    type: str
    projectId: str
    organizationId: str
    tag: _containers.RepeatedScalarFieldContainer[str]
    language: str
    organization: _common_pb2.Organization
    name: str
    description: str
    createdDate: _timestamp_pb2.Timestamp
    updatedDate: _timestamp_pb2.Timestamp
    appAppearance: _struct_pb2.Struct
    webAppearance: _struct_pb2.Struct
    modelProviderId: int
    modelProviderName: str
    modelOptions: _containers.RepeatedCompositeFieldContainer[_common_pb2.Metadata]
    def __init__(self, id: _Optional[str] = ..., status: _Optional[str] = ..., visibility: _Optional[str] = ..., type: _Optional[str] = ..., projectId: _Optional[str] = ..., organizationId: _Optional[str] = ..., tag: _Optional[_Iterable[str]] = ..., language: _Optional[str] = ..., organization: _Optional[_Union[_common_pb2.Organization, _Mapping]] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., createdDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updatedDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., appAppearance: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., webAppearance: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., modelProviderId: _Optional[int] = ..., modelProviderName: _Optional[str] = ..., modelOptions: _Optional[_Iterable[_Union[_common_pb2.Metadata, _Mapping]]] = ...) -> None: ...

class GetAllDeploymentResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error", "paginated")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PAGINATED_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: _containers.RepeatedCompositeFieldContainer[SearchableDeployment]
    error: _common_pb2.Error
    paginated: _common_pb2.Paginated
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Iterable[_Union[SearchableDeployment, _Mapping]]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., paginated: _Optional[_Union[_common_pb2.Paginated, _Mapping]] = ...) -> None: ...
