from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Contact(_message.Message):
    __slots__ = ("email", "name")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    email: str
    name: str
    def __init__(self, email: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class WelcomeEmailRequest(_message.Message):
    __slots__ = ("userId", "to")
    USERID_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    userId: int
    to: Contact
    def __init__(self, userId: _Optional[int] = ..., to: _Optional[_Union[Contact, _Mapping]] = ...) -> None: ...

class WelcomeEmailResponse(_message.Message):
    __slots__ = ("code", "success")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    def __init__(self, code: _Optional[int] = ..., success: bool = ...) -> None: ...

class ResetPasswordEmailRequest(_message.Message):
    __slots__ = ("userId", "to", "resetPasswordLink")
    USERID_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    RESETPASSWORDLINK_FIELD_NUMBER: _ClassVar[int]
    userId: int
    to: Contact
    resetPasswordLink: str
    def __init__(self, userId: _Optional[int] = ..., to: _Optional[_Union[Contact, _Mapping]] = ..., resetPasswordLink: _Optional[str] = ...) -> None: ...

class ResetPasswordEmailResponse(_message.Message):
    __slots__ = ("code", "success")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    def __init__(self, code: _Optional[int] = ..., success: bool = ...) -> None: ...

class InviteMemeberEmailRequest(_message.Message):
    __slots__ = ("userId", "to", "organizationName", "projectName", "inviterName")
    USERID_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATIONNAME_FIELD_NUMBER: _ClassVar[int]
    PROJECTNAME_FIELD_NUMBER: _ClassVar[int]
    INVITERNAME_FIELD_NUMBER: _ClassVar[int]
    userId: int
    to: Contact
    organizationName: str
    projectName: str
    inviterName: str
    def __init__(self, userId: _Optional[int] = ..., to: _Optional[_Union[Contact, _Mapping]] = ..., organizationName: _Optional[str] = ..., projectName: _Optional[str] = ..., inviterName: _Optional[str] = ...) -> None: ...

class InviteMemeberEmailResponse(_message.Message):
    __slots__ = ("code", "success")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    code: int
    success: bool
    def __init__(self, code: _Optional[int] = ..., success: bool = ...) -> None: ...
