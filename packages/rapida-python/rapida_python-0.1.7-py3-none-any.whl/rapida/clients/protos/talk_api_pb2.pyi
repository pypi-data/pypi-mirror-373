import datetime

from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
import rapida.clients.protos.common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AssistantDefinition(_message.Message):
    __slots__ = ("assistantId", "version")
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    assistantId: int
    version: str
    def __init__(self, assistantId: _Optional[int] = ..., version: _Optional[str] = ...) -> None: ...

class AssistantMessagingRequest(_message.Message):
    __slots__ = ("assistant", "message", "assistantConversationId", "metadata", "source", "args", "options")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _any_pb2.Any
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    class ArgsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _any_pb2.Any
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    class OptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _any_pb2.Any
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    ASSISTANT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTCONVERSATIONID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    assistant: AssistantDefinition
    message: _common_pb2.Message
    assistantConversationId: int
    metadata: _containers.MessageMap[str, _any_pb2.Any]
    source: _common_pb2.Source
    args: _containers.MessageMap[str, _any_pb2.Any]
    options: _containers.MessageMap[str, _any_pb2.Any]
    def __init__(self, assistant: _Optional[_Union[AssistantDefinition, _Mapping]] = ..., message: _Optional[_Union[_common_pb2.Message, _Mapping]] = ..., assistantConversationId: _Optional[int] = ..., metadata: _Optional[_Mapping[str, _any_pb2.Any]] = ..., source: _Optional[_Union[_common_pb2.Source, str]] = ..., args: _Optional[_Mapping[str, _any_pb2.Any]] = ..., options: _Optional[_Mapping[str, _any_pb2.Any]] = ...) -> None: ...

class AssistantConversationConfiguration(_message.Message):
    __slots__ = ("assistantConversationId", "assistant", "time")
    ASSISTANTCONVERSATIONID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANT_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    assistantConversationId: int
    assistant: AssistantDefinition
    time: _timestamp_pb2.Timestamp
    def __init__(self, assistantConversationId: _Optional[int] = ..., assistant: _Optional[_Union[AssistantDefinition, _Mapping]] = ..., time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AssistantConversationInterruption(_message.Message):
    __slots__ = ("id", "type", "time")
    class InterruptionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        INTERRUPTION_TYPE_UNSPECIFIED: _ClassVar[AssistantConversationInterruption.InterruptionType]
        INTERRUPTION_TYPE_VAD: _ClassVar[AssistantConversationInterruption.InterruptionType]
        INTERRUPTION_TYPE_WORD: _ClassVar[AssistantConversationInterruption.InterruptionType]
    INTERRUPTION_TYPE_UNSPECIFIED: AssistantConversationInterruption.InterruptionType
    INTERRUPTION_TYPE_VAD: AssistantConversationInterruption.InterruptionType
    INTERRUPTION_TYPE_WORD: AssistantConversationInterruption.InterruptionType
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: AssistantConversationInterruption.InterruptionType
    time: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., type: _Optional[_Union[AssistantConversationInterruption.InterruptionType, str]] = ..., time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AssistantConversationUserMessage(_message.Message):
    __slots__ = ("message", "id", "completed", "time")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    message: _common_pb2.Message
    id: str
    completed: bool
    time: _timestamp_pb2.Timestamp
    def __init__(self, message: _Optional[_Union[_common_pb2.Message, _Mapping]] = ..., id: _Optional[str] = ..., completed: bool = ..., time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AssistantConversationAssistantMessage(_message.Message):
    __slots__ = ("message", "id", "completed", "time")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    message: _common_pb2.Message
    id: str
    completed: bool
    time: _timestamp_pb2.Timestamp
    def __init__(self, message: _Optional[_Union[_common_pb2.Message, _Mapping]] = ..., id: _Optional[str] = ..., completed: bool = ..., time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AssistantMessagingResponse(_message.Message):
    __slots__ = ("code", "success", "error", "configuration", "interruption", "user", "assistant", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    INTERRUPTION_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    ASSISTANT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    error: _common_pb2.Error
    configuration: AssistantConversationConfiguration
    interruption: AssistantConversationInterruption
    user: AssistantConversationUserMessage
    assistant: AssistantConversationAssistantMessage
    message: _common_pb2.AssistantConversationMessage
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., configuration: _Optional[_Union[AssistantConversationConfiguration, _Mapping]] = ..., interruption: _Optional[_Union[AssistantConversationInterruption, _Mapping]] = ..., user: _Optional[_Union[AssistantConversationUserMessage, _Mapping]] = ..., assistant: _Optional[_Union[AssistantConversationAssistantMessage, _Mapping]] = ..., message: _Optional[_Union[_common_pb2.AssistantConversationMessage, _Mapping]] = ...) -> None: ...

class CreateMessageMetricRequest(_message.Message):
    __slots__ = ("assistantId", "assistantConversationId", "messageId", "metrics")
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTCONVERSATIONID_FIELD_NUMBER: _ClassVar[int]
    MESSAGEID_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    assistantId: int
    assistantConversationId: int
    messageId: str
    metrics: _containers.RepeatedCompositeFieldContainer[_common_pb2.Metric]
    def __init__(self, assistantId: _Optional[int] = ..., assistantConversationId: _Optional[int] = ..., messageId: _Optional[str] = ..., metrics: _Optional[_Iterable[_Union[_common_pb2.Metric, _Mapping]]] = ...) -> None: ...

class CreateMessageMetricResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: _containers.RepeatedCompositeFieldContainer[_common_pb2.Metric]
    error: _common_pb2.Error
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Iterable[_Union[_common_pb2.Metric, _Mapping]]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ...) -> None: ...

class CreateConversationMetricRequest(_message.Message):
    __slots__ = ("assistantId", "assistantConversationId", "metrics")
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTCONVERSATIONID_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    assistantId: int
    assistantConversationId: int
    metrics: _containers.RepeatedCompositeFieldContainer[_common_pb2.Metric]
    def __init__(self, assistantId: _Optional[int] = ..., assistantConversationId: _Optional[int] = ..., metrics: _Optional[_Iterable[_Union[_common_pb2.Metric, _Mapping]]] = ...) -> None: ...

class CreateConversationMetricResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: _containers.RepeatedCompositeFieldContainer[_common_pb2.Metric]
    error: _common_pb2.Error
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Iterable[_Union[_common_pb2.Metric, _Mapping]]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ...) -> None: ...

class CreatePhoneCallRequest(_message.Message):
    __slots__ = ("assistant", "metadata", "args", "options", "fromNumber", "toNumber")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _any_pb2.Any
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    class ArgsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _any_pb2.Any
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    class OptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _any_pb2.Any
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    ASSISTANT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    FROMNUMBER_FIELD_NUMBER: _ClassVar[int]
    TONUMBER_FIELD_NUMBER: _ClassVar[int]
    assistant: AssistantDefinition
    metadata: _containers.MessageMap[str, _any_pb2.Any]
    args: _containers.MessageMap[str, _any_pb2.Any]
    options: _containers.MessageMap[str, _any_pb2.Any]
    fromNumber: str
    toNumber: str
    def __init__(self, assistant: _Optional[_Union[AssistantDefinition, _Mapping]] = ..., metadata: _Optional[_Mapping[str, _any_pb2.Any]] = ..., args: _Optional[_Mapping[str, _any_pb2.Any]] = ..., options: _Optional[_Mapping[str, _any_pb2.Any]] = ..., fromNumber: _Optional[str] = ..., toNumber: _Optional[str] = ...) -> None: ...

class CreatePhoneCallResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: _common_pb2.AssistantConversation
    error: _common_pb2.Error
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Union[_common_pb2.AssistantConversation, _Mapping]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ...) -> None: ...

class CreateBulkPhoneCallRequest(_message.Message):
    __slots__ = ("phoneCalls",)
    PHONECALLS_FIELD_NUMBER: _ClassVar[int]
    phoneCalls: _containers.RepeatedCompositeFieldContainer[CreatePhoneCallRequest]
    def __init__(self, phoneCalls: _Optional[_Iterable[_Union[CreatePhoneCallRequest, _Mapping]]] = ...) -> None: ...

class CreateBulkPhoneCallResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: _containers.RepeatedCompositeFieldContainer[_common_pb2.AssistantConversation]
    error: _common_pb2.Error
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Iterable[_Union[_common_pb2.AssistantConversation, _Mapping]]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ...) -> None: ...
