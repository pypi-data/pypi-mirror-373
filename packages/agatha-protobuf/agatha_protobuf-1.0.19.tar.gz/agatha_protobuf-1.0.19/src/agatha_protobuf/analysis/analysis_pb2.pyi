from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AnalyzeRequest(_message.Message):
    __slots__ = ("user_id", "text", "context")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    text: str
    context: str
    def __init__(self, user_id: _Optional[str] = ..., text: _Optional[str] = ..., context: _Optional[str] = ...) -> None: ...

class AnalyzeResponse(_message.Message):
    __slots__ = ("category", "reason")
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    category: str
    reason: str
    def __init__(self, category: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class AnalyzeLLMSResponse(_message.Message):
    __slots__ = ("llms",)
    LLMS_FIELD_NUMBER: _ClassVar[int]
    llms: _containers.RepeatedCompositeFieldContainer[LLM]
    def __init__(self, llms: _Optional[_Iterable[_Union[LLM, _Mapping]]] = ...) -> None: ...

class LLM(_message.Message):
    __slots__ = ("name", "response")
    NAME_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    name: str
    response: AnalyzeResponse
    def __init__(self, name: _Optional[str] = ..., response: _Optional[_Union[AnalyzeResponse, _Mapping]] = ...) -> None: ...

class CreateFeedbackRequest(_message.Message):
    __slots__ = ("_id", "scale", "analyze", "context", "input", "build", "model")
    _ID_FIELD_NUMBER: _ClassVar[int]
    SCALE_FIELD_NUMBER: _ClassVar[int]
    ANALYZE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    BUILD_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    _id: str
    scale: str
    analyze: str
    context: str
    input: str
    build: str
    model: str
    def __init__(self, _id: _Optional[str] = ..., scale: _Optional[str] = ..., analyze: _Optional[str] = ..., context: _Optional[str] = ..., input: _Optional[str] = ..., build: _Optional[str] = ..., model: _Optional[str] = ...) -> None: ...

class CreateMigrationResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...
