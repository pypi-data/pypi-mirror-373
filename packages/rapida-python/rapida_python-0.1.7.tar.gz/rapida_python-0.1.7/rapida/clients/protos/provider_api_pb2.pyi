import rapida.clients.protos.common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetAllModelProviderRequest(_message.Message):
    __slots__ = ("paginate", "criterias")
    PAGINATE_FIELD_NUMBER: _ClassVar[int]
    CRITERIAS_FIELD_NUMBER: _ClassVar[int]
    paginate: _common_pb2.Paginate
    criterias: _containers.RepeatedCompositeFieldContainer[_common_pb2.Criteria]
    def __init__(self, paginate: _Optional[_Union[_common_pb2.Paginate, _Mapping]] = ..., criterias: _Optional[_Iterable[_Union[_common_pb2.Criteria, _Mapping]]] = ...) -> None: ...

class GetAllModelProviderResponse(_message.Message):
    __slots__ = ("code", "success", "data")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: _containers.RepeatedCompositeFieldContainer[_common_pb2.Provider]
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Iterable[_Union[_common_pb2.Provider, _Mapping]]] = ...) -> None: ...

class ToolProvider(_message.Message):
    __slots__ = ("id", "name", "description", "image", "feature", "connectConfiguration")
    class ConnectConfigurationEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_FIELD_NUMBER: _ClassVar[int]
    CONNECTCONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    description: str
    image: str
    feature: _containers.RepeatedScalarFieldContainer[str]
    connectConfiguration: _containers.ScalarMap[str, str]
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., image: _Optional[str] = ..., feature: _Optional[_Iterable[str]] = ..., connectConfiguration: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetAllToolProviderRequest(_message.Message):
    __slots__ = ("paginate", "criterias")
    PAGINATE_FIELD_NUMBER: _ClassVar[int]
    CRITERIAS_FIELD_NUMBER: _ClassVar[int]
    paginate: _common_pb2.Paginate
    criterias: _containers.RepeatedCompositeFieldContainer[_common_pb2.Criteria]
    def __init__(self, paginate: _Optional[_Union[_common_pb2.Paginate, _Mapping]] = ..., criterias: _Optional[_Iterable[_Union[_common_pb2.Criteria, _Mapping]]] = ...) -> None: ...

class GetAllToolProviderResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error", "paginated")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PAGINATED_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: _containers.RepeatedCompositeFieldContainer[ToolProvider]
    error: _common_pb2.Error
    paginated: _common_pb2.Paginated
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Iterable[_Union[ToolProvider, _Mapping]]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., paginated: _Optional[_Union[_common_pb2.Paginated, _Mapping]] = ...) -> None: ...
