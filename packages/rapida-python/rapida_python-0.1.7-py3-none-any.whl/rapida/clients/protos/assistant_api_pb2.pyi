import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
import rapida.clients.protos.common_pb2 as _common_pb2
import rapida.clients.protos.assistant_deployment_pb2 as _assistant_deployment_pb2
import rapida.clients.protos.assistant_tool_pb2 as _assistant_tool_pb2
import rapida.clients.protos.assistant_analysis_pb2 as _assistant_analysis_pb2
import rapida.clients.protos.assistant_webhook_pb2 as _assistant_webhook_pb2
import rapida.clients.protos.assistant_knowledge_pb2 as _assistant_knowledge_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Assistant(_message.Message):
    __slots__ = ("id", "status", "visibility", "source", "sourceIdentifier", "assistantTools", "projectId", "organizationId", "assistantProviderModelId", "assistantProviderModel", "name", "description", "assistantTag", "language", "organization", "createdBy", "createdUser", "updatedBy", "updatedUser", "createdDate", "updatedDate", "debuggerDeployment", "phoneDeployment", "whatsappDeployment", "webPluginDeployment", "apiDeployment", "assistantConversations", "assistantWebhooks")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SOURCEIDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTTOOLS_FIELD_NUMBER: _ClassVar[int]
    PROJECTID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATIONID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTPROVIDERMODELID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTPROVIDERMODEL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTTAG_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    CREATEDBY_FIELD_NUMBER: _ClassVar[int]
    CREATEDUSER_FIELD_NUMBER: _ClassVar[int]
    UPDATEDBY_FIELD_NUMBER: _ClassVar[int]
    UPDATEDUSER_FIELD_NUMBER: _ClassVar[int]
    CREATEDDATE_FIELD_NUMBER: _ClassVar[int]
    UPDATEDDATE_FIELD_NUMBER: _ClassVar[int]
    DEBUGGERDEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    PHONEDEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    WHATSAPPDEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    WEBPLUGINDEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    APIDEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTCONVERSATIONS_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTWEBHOOKS_FIELD_NUMBER: _ClassVar[int]
    id: int
    status: str
    visibility: str
    source: str
    sourceIdentifier: int
    assistantTools: _containers.RepeatedCompositeFieldContainer[_assistant_tool_pb2.AssistantTool]
    projectId: int
    organizationId: int
    assistantProviderModelId: int
    assistantProviderModel: AssistantProviderModel
    name: str
    description: str
    assistantTag: _common_pb2.Tag
    language: str
    organization: _common_pb2.Organization
    createdBy: int
    createdUser: _common_pb2.User
    updatedBy: int
    updatedUser: _common_pb2.User
    createdDate: _timestamp_pb2.Timestamp
    updatedDate: _timestamp_pb2.Timestamp
    debuggerDeployment: _assistant_deployment_pb2.AssistantDebuggerDeployment
    phoneDeployment: _assistant_deployment_pb2.AssistantPhoneDeployment
    whatsappDeployment: _assistant_deployment_pb2.AssistantWhatsappDeployment
    webPluginDeployment: _assistant_deployment_pb2.AssistantWebpluginDeployment
    apiDeployment: _assistant_deployment_pb2.AssistantApiDeployment
    assistantConversations: _containers.RepeatedCompositeFieldContainer[_common_pb2.AssistantConversation]
    assistantWebhooks: _containers.RepeatedCompositeFieldContainer[_assistant_webhook_pb2.AssistantWebhook]
    def __init__(self, id: _Optional[int] = ..., status: _Optional[str] = ..., visibility: _Optional[str] = ..., source: _Optional[str] = ..., sourceIdentifier: _Optional[int] = ..., assistantTools: _Optional[_Iterable[_Union[_assistant_tool_pb2.AssistantTool, _Mapping]]] = ..., projectId: _Optional[int] = ..., organizationId: _Optional[int] = ..., assistantProviderModelId: _Optional[int] = ..., assistantProviderModel: _Optional[_Union[AssistantProviderModel, _Mapping]] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., assistantTag: _Optional[_Union[_common_pb2.Tag, _Mapping]] = ..., language: _Optional[str] = ..., organization: _Optional[_Union[_common_pb2.Organization, _Mapping]] = ..., createdBy: _Optional[int] = ..., createdUser: _Optional[_Union[_common_pb2.User, _Mapping]] = ..., updatedBy: _Optional[int] = ..., updatedUser: _Optional[_Union[_common_pb2.User, _Mapping]] = ..., createdDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updatedDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., debuggerDeployment: _Optional[_Union[_assistant_deployment_pb2.AssistantDebuggerDeployment, _Mapping]] = ..., phoneDeployment: _Optional[_Union[_assistant_deployment_pb2.AssistantPhoneDeployment, _Mapping]] = ..., whatsappDeployment: _Optional[_Union[_assistant_deployment_pb2.AssistantWhatsappDeployment, _Mapping]] = ..., webPluginDeployment: _Optional[_Union[_assistant_deployment_pb2.AssistantWebpluginDeployment, _Mapping]] = ..., apiDeployment: _Optional[_Union[_assistant_deployment_pb2.AssistantApiDeployment, _Mapping]] = ..., assistantConversations: _Optional[_Iterable[_Union[_common_pb2.AssistantConversation, _Mapping]]] = ..., assistantWebhooks: _Optional[_Iterable[_Union[_assistant_webhook_pb2.AssistantWebhook, _Mapping]]] = ...) -> None: ...

class AssistantProviderModel(_message.Message):
    __slots__ = ("id", "template", "description", "modelProviderId", "modelProviderName", "assistantModelOptions", "status", "createdBy", "createdUser", "updatedBy", "updatedUser", "createdDate", "updatedDate")
    ID_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MODELPROVIDERID_FIELD_NUMBER: _ClassVar[int]
    MODELPROVIDERNAME_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTMODELOPTIONS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATEDBY_FIELD_NUMBER: _ClassVar[int]
    CREATEDUSER_FIELD_NUMBER: _ClassVar[int]
    UPDATEDBY_FIELD_NUMBER: _ClassVar[int]
    UPDATEDUSER_FIELD_NUMBER: _ClassVar[int]
    CREATEDDATE_FIELD_NUMBER: _ClassVar[int]
    UPDATEDDATE_FIELD_NUMBER: _ClassVar[int]
    id: int
    template: _common_pb2.TextChatCompletePrompt
    description: str
    modelProviderId: int
    modelProviderName: str
    assistantModelOptions: _containers.RepeatedCompositeFieldContainer[_common_pb2.Metadata]
    status: str
    createdBy: int
    createdUser: _common_pb2.User
    updatedBy: int
    updatedUser: _common_pb2.User
    createdDate: _timestamp_pb2.Timestamp
    updatedDate: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., template: _Optional[_Union[_common_pb2.TextChatCompletePrompt, _Mapping]] = ..., description: _Optional[str] = ..., modelProviderId: _Optional[int] = ..., modelProviderName: _Optional[str] = ..., assistantModelOptions: _Optional[_Iterable[_Union[_common_pb2.Metadata, _Mapping]]] = ..., status: _Optional[str] = ..., createdBy: _Optional[int] = ..., createdUser: _Optional[_Union[_common_pb2.User, _Mapping]] = ..., updatedBy: _Optional[int] = ..., updatedUser: _Optional[_Union[_common_pb2.User, _Mapping]] = ..., createdDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updatedDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateAssistantRequest(_message.Message):
    __slots__ = ("assistantProviderModel", "assistantKnowledges", "assistantTools", "description", "visibility", "language", "source", "sourceIdentifier", "tags", "name")
    ASSISTANTPROVIDERMODEL_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTKNOWLEDGES_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTTOOLS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SOURCEIDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    assistantProviderModel: CreateAssistantProviderModelRequest
    assistantKnowledges: _containers.RepeatedCompositeFieldContainer[_assistant_knowledge_pb2.CreateAssistantKnowledgeRequest]
    assistantTools: _containers.RepeatedCompositeFieldContainer[_assistant_tool_pb2.CreateAssistantToolRequest]
    description: str
    visibility: str
    language: str
    source: str
    sourceIdentifier: int
    tags: _containers.RepeatedScalarFieldContainer[str]
    name: str
    def __init__(self, assistantProviderModel: _Optional[_Union[CreateAssistantProviderModelRequest, _Mapping]] = ..., assistantKnowledges: _Optional[_Iterable[_Union[_assistant_knowledge_pb2.CreateAssistantKnowledgeRequest, _Mapping]]] = ..., assistantTools: _Optional[_Iterable[_Union[_assistant_tool_pb2.CreateAssistantToolRequest, _Mapping]]] = ..., description: _Optional[str] = ..., visibility: _Optional[str] = ..., language: _Optional[str] = ..., source: _Optional[str] = ..., sourceIdentifier: _Optional[int] = ..., tags: _Optional[_Iterable[str]] = ..., name: _Optional[str] = ...) -> None: ...

class CreateAssistantProviderModelRequest(_message.Message):
    __slots__ = ("assistantId", "description", "template", "modelProviderId", "modelProviderName", "assistantModelOptions")
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    MODELPROVIDERID_FIELD_NUMBER: _ClassVar[int]
    MODELPROVIDERNAME_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTMODELOPTIONS_FIELD_NUMBER: _ClassVar[int]
    assistantId: int
    description: str
    template: _common_pb2.TextChatCompletePrompt
    modelProviderId: int
    modelProviderName: str
    assistantModelOptions: _containers.RepeatedCompositeFieldContainer[_common_pb2.Metadata]
    def __init__(self, assistantId: _Optional[int] = ..., description: _Optional[str] = ..., template: _Optional[_Union[_common_pb2.TextChatCompletePrompt, _Mapping]] = ..., modelProviderId: _Optional[int] = ..., modelProviderName: _Optional[str] = ..., assistantModelOptions: _Optional[_Iterable[_Union[_common_pb2.Metadata, _Mapping]]] = ...) -> None: ...

class GetAssistantProviderModelResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: AssistantProviderModel
    error: _common_pb2.Error
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Union[AssistantProviderModel, _Mapping]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ...) -> None: ...

class CreateAssistantTagRequest(_message.Message):
    __slots__ = ("assistantId", "tags")
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    assistantId: int
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, assistantId: _Optional[int] = ..., tags: _Optional[_Iterable[str]] = ...) -> None: ...

class GetAssistantRequest(_message.Message):
    __slots__ = ("id", "assistantProviderModelId")
    ID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTPROVIDERMODELID_FIELD_NUMBER: _ClassVar[int]
    id: int
    assistantProviderModelId: int
    def __init__(self, id: _Optional[int] = ..., assistantProviderModelId: _Optional[int] = ...) -> None: ...

class DeleteAssistantRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetAssistantResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: Assistant
    error: _common_pb2.Error
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Union[Assistant, _Mapping]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ...) -> None: ...

class GetAllAssistantRequest(_message.Message):
    __slots__ = ("paginate", "criterias")
    PAGINATE_FIELD_NUMBER: _ClassVar[int]
    CRITERIAS_FIELD_NUMBER: _ClassVar[int]
    paginate: _common_pb2.Paginate
    criterias: _containers.RepeatedCompositeFieldContainer[_common_pb2.Criteria]
    def __init__(self, paginate: _Optional[_Union[_common_pb2.Paginate, _Mapping]] = ..., criterias: _Optional[_Iterable[_Union[_common_pb2.Criteria, _Mapping]]] = ...) -> None: ...

class GetAllAssistantResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error", "paginated")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PAGINATED_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: _containers.RepeatedCompositeFieldContainer[Assistant]
    error: _common_pb2.Error
    paginated: _common_pb2.Paginated
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Iterable[_Union[Assistant, _Mapping]]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., paginated: _Optional[_Union[_common_pb2.Paginated, _Mapping]] = ...) -> None: ...

class GetAllAssistantProviderModelRequest(_message.Message):
    __slots__ = ("paginate", "criterias", "assistantId")
    PAGINATE_FIELD_NUMBER: _ClassVar[int]
    CRITERIAS_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    paginate: _common_pb2.Paginate
    criterias: _containers.RepeatedCompositeFieldContainer[_common_pb2.Criteria]
    assistantId: int
    def __init__(self, paginate: _Optional[_Union[_common_pb2.Paginate, _Mapping]] = ..., criterias: _Optional[_Iterable[_Union[_common_pb2.Criteria, _Mapping]]] = ..., assistantId: _Optional[int] = ...) -> None: ...

class GetAllAssistantProviderModelResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error", "paginated")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PAGINATED_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: _containers.RepeatedCompositeFieldContainer[AssistantProviderModel]
    error: _common_pb2.Error
    paginated: _common_pb2.Paginated
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Iterable[_Union[AssistantProviderModel, _Mapping]]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., paginated: _Optional[_Union[_common_pb2.Paginated, _Mapping]] = ...) -> None: ...

class GetAllAssistantMessageRequest(_message.Message):
    __slots__ = ("paginate", "criterias", "assistantId", "order", "selectors")
    PAGINATE_FIELD_NUMBER: _ClassVar[int]
    CRITERIAS_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    SELECTORS_FIELD_NUMBER: _ClassVar[int]
    paginate: _common_pb2.Paginate
    criterias: _containers.RepeatedCompositeFieldContainer[_common_pb2.Criteria]
    assistantId: int
    order: _common_pb2.Ordering
    selectors: _containers.RepeatedCompositeFieldContainer[_common_pb2.FieldSelector]
    def __init__(self, paginate: _Optional[_Union[_common_pb2.Paginate, _Mapping]] = ..., criterias: _Optional[_Iterable[_Union[_common_pb2.Criteria, _Mapping]]] = ..., assistantId: _Optional[int] = ..., order: _Optional[_Union[_common_pb2.Ordering, _Mapping]] = ..., selectors: _Optional[_Iterable[_Union[_common_pb2.FieldSelector, _Mapping]]] = ...) -> None: ...

class GetAllAssistantMessageResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error", "paginated")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PAGINATED_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: _containers.RepeatedCompositeFieldContainer[_common_pb2.AssistantConversationMessage]
    error: _common_pb2.Error
    paginated: _common_pb2.Paginated
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Iterable[_Union[_common_pb2.AssistantConversationMessage, _Mapping]]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., paginated: _Optional[_Union[_common_pb2.Paginated, _Mapping]] = ...) -> None: ...

class GetAllMessageRequest(_message.Message):
    __slots__ = ("paginate", "criterias", "order", "selectors")
    PAGINATE_FIELD_NUMBER: _ClassVar[int]
    CRITERIAS_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    SELECTORS_FIELD_NUMBER: _ClassVar[int]
    paginate: _common_pb2.Paginate
    criterias: _containers.RepeatedCompositeFieldContainer[_common_pb2.Criteria]
    order: _common_pb2.Ordering
    selectors: _containers.RepeatedCompositeFieldContainer[_common_pb2.FieldSelector]
    def __init__(self, paginate: _Optional[_Union[_common_pb2.Paginate, _Mapping]] = ..., criterias: _Optional[_Iterable[_Union[_common_pb2.Criteria, _Mapping]]] = ..., order: _Optional[_Union[_common_pb2.Ordering, _Mapping]] = ..., selectors: _Optional[_Iterable[_Union[_common_pb2.FieldSelector, _Mapping]]] = ...) -> None: ...

class GetAllMessageResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error", "paginated")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PAGINATED_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: _containers.RepeatedCompositeFieldContainer[_common_pb2.AssistantConversationMessage]
    error: _common_pb2.Error
    paginated: _common_pb2.Paginated
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Iterable[_Union[_common_pb2.AssistantConversationMessage, _Mapping]]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., paginated: _Optional[_Union[_common_pb2.Paginated, _Mapping]] = ...) -> None: ...

class UpdateAssistantVersionRequest(_message.Message):
    __slots__ = ("assistantId", "assistantProviderModelId")
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTPROVIDERMODELID_FIELD_NUMBER: _ClassVar[int]
    assistantId: int
    assistantProviderModelId: int
    def __init__(self, assistantId: _Optional[int] = ..., assistantProviderModelId: _Optional[int] = ...) -> None: ...

class UpdateAssistantDetailRequest(_message.Message):
    __slots__ = ("assistantId", "name", "description")
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    assistantId: int
    name: str
    description: str
    def __init__(self, assistantId: _Optional[int] = ..., name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class GetAllAssistantUserConversationRequest(_message.Message):
    __slots__ = ("assistantId", "paginate", "criterias", "source")
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    PAGINATE_FIELD_NUMBER: _ClassVar[int]
    CRITERIAS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    assistantId: int
    paginate: _common_pb2.Paginate
    criterias: _containers.RepeatedCompositeFieldContainer[_common_pb2.Criteria]
    source: _common_pb2.Source
    def __init__(self, assistantId: _Optional[int] = ..., paginate: _Optional[_Union[_common_pb2.Paginate, _Mapping]] = ..., criterias: _Optional[_Iterable[_Union[_common_pb2.Criteria, _Mapping]]] = ..., source: _Optional[_Union[_common_pb2.Source, str]] = ...) -> None: ...

class GetAllAssistantUserConversationResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error", "paginated")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PAGINATED_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: _containers.RepeatedCompositeFieldContainer[_common_pb2.AssistantConversation]
    error: _common_pb2.Error
    paginated: _common_pb2.Paginated
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Iterable[_Union[_common_pb2.AssistantConversation, _Mapping]]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., paginated: _Optional[_Union[_common_pb2.Paginated, _Mapping]] = ...) -> None: ...

class GetAssistantConversationRequest(_message.Message):
    __slots__ = ("assistantId", "conversationId", "paginate", "criterias", "selectors")
    ASSISTANTID_FIELD_NUMBER: _ClassVar[int]
    CONVERSATIONID_FIELD_NUMBER: _ClassVar[int]
    PAGINATE_FIELD_NUMBER: _ClassVar[int]
    CRITERIAS_FIELD_NUMBER: _ClassVar[int]
    SELECTORS_FIELD_NUMBER: _ClassVar[int]
    assistantId: int
    conversationId: int
    paginate: _common_pb2.Paginate
    criterias: _containers.RepeatedCompositeFieldContainer[_common_pb2.Criteria]
    selectors: _containers.RepeatedCompositeFieldContainer[_common_pb2.FieldSelector]
    def __init__(self, assistantId: _Optional[int] = ..., conversationId: _Optional[int] = ..., paginate: _Optional[_Union[_common_pb2.Paginate, _Mapping]] = ..., criterias: _Optional[_Iterable[_Union[_common_pb2.Criteria, _Mapping]]] = ..., selectors: _Optional[_Iterable[_Union[_common_pb2.FieldSelector, _Mapping]]] = ...) -> None: ...

class GetAssistantConversationResponse(_message.Message):
    __slots__ = ("code", "success", "data", "error", "paginated")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PAGINATED_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    data: _common_pb2.AssistantConversation
    error: _common_pb2.Error
    paginated: _common_pb2.Paginated
    def __init__(self, code: _Optional[int] = ..., success: bool = ..., data: _Optional[_Union[_common_pb2.AssistantConversation, _Mapping]] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., paginated: _Optional[_Union[_common_pb2.Paginated, _Mapping]] = ...) -> None: ...
