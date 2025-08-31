import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
import rapida.clients.protos.common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeploymentAudioProvider(_message.Message):
    __slots__ = ("id", "audioProvider", "audioOptions", "audioProviderId", "status", "audioType")
    ID_FIELD_NUMBER: _ClassVar[int]
    AUDIOPROVIDER_FIELD_NUMBER: _ClassVar[int]
    AUDIOOPTIONS_FIELD_NUMBER: _ClassVar[int]
    AUDIOPROVIDERID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    AUDIOTYPE_FIELD_NUMBER: _ClassVar[int]
    id: int
    audioProvider: str
    audioOptions: _containers.RepeatedCompositeFieldContainer[_common_pb2.Metadata]
    audioProviderId: int
    status: str
    audioType: str
    def __init__(self, id: _Optional[int] = ..., audioProvider: _Optional[str] = ..., audioOptions: _Optional[_Iterable[_Union[_common_pb2.Metadata, _Mapping]]] = ..., audioProviderId: _Optional[int] = ..., status: _Optional[str] = ..., audioType: _Optional[str] = ...) -> None: ...

class AssistantDeploymentCapturer(_message.Message):
    __slots__ = ("id", "assistantDeploymentId", "capturerType", "capturerProviderId", "capturerProvider", "capturerOptions", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTDEPLOYMENTID_FIELD_NUMBER: _ClassVar[int]
    CAPTURERTYPE_FIELD_NUMBER: _ClassVar[int]
    CAPTURERPROVIDERID_FIELD_NUMBER: _ClassVar[int]
    CAPTURERPROVIDER_FIELD_NUMBER: _ClassVar[int]
    CAPTUREROPTIONS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: int
    assistantDeploymentId: int
    capturerType: str
    capturerProviderId: int
    capturerProvider: str
    capturerOptions: _containers.RepeatedCompositeFieldContainer[_common_pb2.Metadata]
    status: str
    def __init__(self, id: _Optional[int] = ..., assistantDeploymentId: _Optional[int] = ..., capturerType: _Optional[str] = ..., capturerProviderId: _Optional[int] = ..., capturerProvider: _Optional[str] = ..., capturerOptions: _Optional[_Iterable[_Union[_common_pb2.Metadata, _Mapping]]] = ..., status: _Optional[str] = ...) -> None: ...

class AssistantWebpluginDeployment(_message.Message):
    __slots__ = ("id", "assistantId", "name", "role", "tone", "experties", "greeting", "mistake", "ending", "inputAudio", "outputAudio", "capturers", "url", "raw", "suggestion", "helpCenterEnabled", "productCatalogEnabled", "articleCatalogEnabled", "uploadFileEnabled", "createdDate", "updatedDate", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TONE_FIELD_NUMBER: _ClassVar[int]
    EXPERTIES_FIELD_NUMBER: _ClassVar[int]
    GREETING_FIELD_NUMBER: _ClassVar[int]
    MISTAKE_FIELD_NUMBER: _ClassVar[int]
    ENDING_FIELD_NUMBER: _ClassVar[int]
    INPUTAUDIO_FIELD_NUMBER: _ClassVar[int]
    OUTPUTAUDIO_FIELD_NUMBER: _ClassVar[int]
    CAPTURERS_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    RAW_FIELD_NUMBER: _ClassVar[int]
    SUGGESTION_FIELD_NUMBER: _ClassVar[int]
    HELPCENTERENABLED_FIELD_NUMBER: _ClassVar[int]
    PRODUCTCATALOGENABLED_FIELD_NUMBER: _ClassVar[int]
    ARTICLECATALOGENABLED_FIELD_NUMBER: _ClassVar[int]
    UPLOADFILEENABLED_FIELD_NUMBER: _ClassVar[int]
    CREATEDDATE_FIELD_NUMBER: _ClassVar[int]
    UPDATEDDATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: int
    assistantId: int
    name: str
    role: str
    tone: str
    experties: str
    greeting: str
    mistake: str
    ending: str
    inputAudio: DeploymentAudioProvider
    outputAudio: DeploymentAudioProvider
    capturers: _containers.RepeatedCompositeFieldContainer[AssistantDeploymentCapturer]
    url: str
    raw: _common_pb2.Content
    suggestion: _containers.RepeatedScalarFieldContainer[str]
    helpCenterEnabled: bool
    productCatalogEnabled: bool
    articleCatalogEnabled: bool
    uploadFileEnabled: bool
    createdDate: _timestamp_pb2.Timestamp
    updatedDate: _timestamp_pb2.Timestamp
    status: str
    def __init__(self, id: _Optional[int] = ..., assistantId: _Optional[int] = ..., name: _Optional[str] = ..., role: _Optional[str] = ..., tone: _Optional[str] = ..., experties: _Optional[str] = ..., greeting: _Optional[str] = ..., mistake: _Optional[str] = ..., ending: _Optional[str] = ..., inputAudio: _Optional[_Union[DeploymentAudioProvider, _Mapping]] = ..., outputAudio: _Optional[_Union[DeploymentAudioProvider, _Mapping]] = ..., capturers: _Optional[_Iterable[_Union[AssistantDeploymentCapturer, _Mapping]]] = ..., url: _Optional[str] = ..., raw: _Optional[_Union[_common_pb2.Content, _Mapping]] = ..., suggestion: _Optional[_Iterable[str]] = ..., helpCenterEnabled: bool = ..., productCatalogEnabled: bool = ..., articleCatalogEnabled: bool = ..., uploadFileEnabled: bool = ..., createdDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updatedDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[str] = ...) -> None: ...

class AssistantPhoneDeployment(_message.Message):
    __slots__ = ("id", "assistantId", "name", "role", "tone", "experties", "greeting", "mistake", "ending", "inputAudio", "outputAudio", "phoneProviderName", "phoneProviderId", "phoneOptions", "capturers", "createdDate", "updatedDate", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TONE_FIELD_NUMBER: _ClassVar[int]
    EXPERTIES_FIELD_NUMBER: _ClassVar[int]
    GREETING_FIELD_NUMBER: _ClassVar[int]
    MISTAKE_FIELD_NUMBER: _ClassVar[int]
    ENDING_FIELD_NUMBER: _ClassVar[int]
    INPUTAUDIO_FIELD_NUMBER: _ClassVar[int]
    OUTPUTAUDIO_FIELD_NUMBER: _ClassVar[int]
    PHONEPROVIDERNAME_FIELD_NUMBER: _ClassVar[int]
    PHONEPROVIDERID_FIELD_NUMBER: _ClassVar[int]
    PHONEOPTIONS_FIELD_NUMBER: _ClassVar[int]
    CAPTURERS_FIELD_NUMBER: _ClassVar[int]
    CREATEDDATE_FIELD_NUMBER: _ClassVar[int]
    UPDATEDDATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: int
    assistantId: int
    name: str
    role: str
    tone: str
    experties: str
    greeting: str
    mistake: str
    ending: str
    inputAudio: DeploymentAudioProvider
    outputAudio: DeploymentAudioProvider
    phoneProviderName: str
    phoneProviderId: int
    phoneOptions: _containers.RepeatedCompositeFieldContainer[_common_pb2.Metadata]
    capturers: _containers.RepeatedCompositeFieldContainer[AssistantDeploymentCapturer]
    createdDate: _timestamp_pb2.Timestamp
    updatedDate: _timestamp_pb2.Timestamp
    status: str
    def __init__(self, id: _Optional[int] = ..., assistantId: _Optional[int] = ..., name: _Optional[str] = ..., role: _Optional[str] = ..., tone: _Optional[str] = ..., experties: _Optional[str] = ..., greeting: _Optional[str] = ..., mistake: _Optional[str] = ..., ending: _Optional[str] = ..., inputAudio: _Optional[_Union[DeploymentAudioProvider, _Mapping]] = ..., outputAudio: _Optional[_Union[DeploymentAudioProvider, _Mapping]] = ..., phoneProviderName: _Optional[str] = ..., phoneProviderId: _Optional[int] = ..., phoneOptions: _Optional[_Iterable[_Union[_common_pb2.Metadata, _Mapping]]] = ..., capturers: _Optional[_Iterable[_Union[AssistantDeploymentCapturer, _Mapping]]] = ..., createdDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updatedDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[str] = ...) -> None: ...

class AssistantWhatsappDeployment(_message.Message):
    __slots__ = ("id", "assistantId", "name", "role", "tone", "experties", "greeting", "mistake", "ending", "whatsappProviderName", "whatsappProviderId", "whatsappOptions", "createdDate", "updatedDate", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TONE_FIELD_NUMBER: _ClassVar[int]
    EXPERTIES_FIELD_NUMBER: _ClassVar[int]
    GREETING_FIELD_NUMBER: _ClassVar[int]
    MISTAKE_FIELD_NUMBER: _ClassVar[int]
    ENDING_FIELD_NUMBER: _ClassVar[int]
    WHATSAPPPROVIDERNAME_FIELD_NUMBER: _ClassVar[int]
    WHATSAPPPROVIDERID_FIELD_NUMBER: _ClassVar[int]
    WHATSAPPOPTIONS_FIELD_NUMBER: _ClassVar[int]
    CREATEDDATE_FIELD_NUMBER: _ClassVar[int]
    UPDATEDDATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: int
    assistantId: int
    name: str
    role: str
    tone: str
    experties: str
    greeting: str
    mistake: str
    ending: str
    whatsappProviderName: str
    whatsappProviderId: int
    whatsappOptions: _containers.RepeatedCompositeFieldContainer[_common_pb2.Metadata]
    createdDate: _timestamp_pb2.Timestamp
    updatedDate: _timestamp_pb2.Timestamp
    status: str
    def __init__(self, id: _Optional[int] = ..., assistantId: _Optional[int] = ..., name: _Optional[str] = ..., role: _Optional[str] = ..., tone: _Optional[str] = ..., experties: _Optional[str] = ..., greeting: _Optional[str] = ..., mistake: _Optional[str] = ..., ending: _Optional[str] = ..., whatsappProviderName: _Optional[str] = ..., whatsappProviderId: _Optional[int] = ..., whatsappOptions: _Optional[_Iterable[_Union[_common_pb2.Metadata, _Mapping]]] = ..., createdDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updatedDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[str] = ...) -> None: ...

class AssistantDebuggerDeployment(_message.Message):
    __slots__ = ("id", "assistantId", "name", "role", "tone", "experties", "greeting", "mistake", "ending", "inputAudio", "outputAudio", "capturers", "url", "raw", "suggestion", "createdDate", "updatedDate", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TONE_FIELD_NUMBER: _ClassVar[int]
    EXPERTIES_FIELD_NUMBER: _ClassVar[int]
    GREETING_FIELD_NUMBER: _ClassVar[int]
    MISTAKE_FIELD_NUMBER: _ClassVar[int]
    ENDING_FIELD_NUMBER: _ClassVar[int]
    INPUTAUDIO_FIELD_NUMBER: _ClassVar[int]
    OUTPUTAUDIO_FIELD_NUMBER: _ClassVar[int]
    CAPTURERS_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    RAW_FIELD_NUMBER: _ClassVar[int]
    SUGGESTION_FIELD_NUMBER: _ClassVar[int]
    CREATEDDATE_FIELD_NUMBER: _ClassVar[int]
    UPDATEDDATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: int
    assistantId: int
    name: str
    role: str
    tone: str
    experties: str
    greeting: str
    mistake: str
    ending: str
    inputAudio: DeploymentAudioProvider
    outputAudio: DeploymentAudioProvider
    capturers: _containers.RepeatedCompositeFieldContainer[AssistantDeploymentCapturer]
    url: str
    raw: _common_pb2.Content
    suggestion: _containers.RepeatedScalarFieldContainer[str]
    createdDate: _timestamp_pb2.Timestamp
    updatedDate: _timestamp_pb2.Timestamp
    status: str
    def __init__(self, id: _Optional[int] = ..., assistantId: _Optional[int] = ..., name: _Optional[str] = ..., role: _Optional[str] = ..., tone: _Optional[str] = ..., experties: _Optional[str] = ..., greeting: _Optional[str] = ..., mistake: _Optional[str] = ..., ending: _Optional[str] = ..., inputAudio: _Optional[_Union[DeploymentAudioProvider, _Mapping]] = ..., outputAudio: _Optional[_Union[DeploymentAudioProvider, _Mapping]] = ..., capturers: _Optional[_Iterable[_Union[AssistantDeploymentCapturer, _Mapping]]] = ..., url: _Optional[str] = ..., raw: _Optional[_Union[_common_pb2.Content, _Mapping]] = ..., suggestion: _Optional[_Iterable[str]] = ..., createdDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updatedDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[str] = ...) -> None: ...

class AssistantApiDeployment(_message.Message):
    __slots__ = ("id", "assistantId", "name", "role", "tone", "experties", "greeting", "mistake", "ending", "inputAudio", "outputAudio", "capturers", "createdDate", "updatedDate", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TONE_FIELD_NUMBER: _ClassVar[int]
    EXPERTIES_FIELD_NUMBER: _ClassVar[int]
    GREETING_FIELD_NUMBER: _ClassVar[int]
    MISTAKE_FIELD_NUMBER: _ClassVar[int]
    ENDING_FIELD_NUMBER: _ClassVar[int]
    INPUTAUDIO_FIELD_NUMBER: _ClassVar[int]
    OUTPUTAUDIO_FIELD_NUMBER: _ClassVar[int]
    CAPTURERS_FIELD_NUMBER: _ClassVar[int]
    CREATEDDATE_FIELD_NUMBER: _ClassVar[int]
    UPDATEDDATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: int
    assistantId: int
    name: str
    role: str
    tone: str
    experties: str
    greeting: str
    mistake: str
    ending: str
    inputAudio: DeploymentAudioProvider
    outputAudio: DeploymentAudioProvider
    capturers: _containers.RepeatedCompositeFieldContainer[AssistantDeploymentCapturer]
    createdDate: _timestamp_pb2.Timestamp
    updatedDate: _timestamp_pb2.Timestamp
    status: str
    def __init__(self, id: _Optional[int] = ..., assistantId: _Optional[int] = ..., name: _Optional[str] = ..., role: _Optional[str] = ..., tone: _Optional[str] = ..., experties: _Optional[str] = ..., greeting: _Optional[str] = ..., mistake: _Optional[str] = ..., ending: _Optional[str] = ..., inputAudio: _Optional[_Union[DeploymentAudioProvider, _Mapping]] = ..., outputAudio: _Optional[_Union[DeploymentAudioProvider, _Mapping]] = ..., capturers: _Optional[_Iterable[_Union[AssistantDeploymentCapturer, _Mapping]]] = ..., createdDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updatedDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[str] = ...) -> None: ...

class CreateAssistantApiDeploymentRequest(_message.Message):
    __slots__ = ("deployment",)
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    deployment: AssistantApiDeployment
    def __init__(self, deployment: _Optional[_Union[AssistantApiDeployment, _Mapping]] = ...) -> None: ...

class AssistantApiDeploymentResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: AssistantApiDeployment
    error: _common_pb2.Error
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Union[AssistantApiDeployment, _Mapping]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ...) -> None: ...

class CreateAssistantPhoneDeploymentRequest(_message.Message):
    __slots__ = ("deployment",)
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    deployment: AssistantPhoneDeployment
    def __init__(self, deployment: _Optional[_Union[AssistantPhoneDeployment, _Mapping]] = ...) -> None: ...

class AssistantPhoneDeploymentResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: AssistantPhoneDeployment
    error: _common_pb2.Error
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Union[AssistantPhoneDeployment, _Mapping]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ...) -> None: ...

class CreateAssistantWhatsappDeploymentRequest(_message.Message):
    __slots__ = ("deployment",)
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    deployment: AssistantWhatsappDeployment
    def __init__(self, deployment: _Optional[_Union[AssistantWhatsappDeployment, _Mapping]] = ...) -> None: ...

class AssistantWhatsappDeploymentResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: AssistantWhatsappDeployment
    error: _common_pb2.Error
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Union[AssistantWhatsappDeployment, _Mapping]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ...) -> None: ...

class CreateAssistantDebuggerDeploymentRequest(_message.Message):
    __slots__ = ("deployment",)
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    deployment: AssistantDebuggerDeployment
    def __init__(self, deployment: _Optional[_Union[AssistantDebuggerDeployment, _Mapping]] = ...) -> None: ...

class AssistantDebuggerDeploymentResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: AssistantDebuggerDeployment
    error: _common_pb2.Error
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Union[AssistantDebuggerDeployment, _Mapping]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ...) -> None: ...

class CreateAssistantWebpluginDeploymentRequest(_message.Message):
    __slots__ = ("deployment",)
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    deployment: AssistantWebpluginDeployment
    def __init__(self, deployment: _Optional[_Union[AssistantWebpluginDeployment, _Mapping]] = ...) -> None: ...

class AssistantWebpluginDeploymentResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: AssistantWebpluginDeployment
    error: _common_pb2.Error
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Union[AssistantWebpluginDeployment, _Mapping]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ...) -> None: ...

class GetAssistantDeploymentRequest(_message.Message):
    __slots__ = ("assistantId",)
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    assistantId: int
    def __init__(self, assistantId: _Optional[int] = ...) -> None: ...
