from typing import ClassVar as _ClassVar
from typing import Iterable as _Iterable
from typing import Mapping as _Mapping
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class EmbedRequest(_message.Message):
    __slots__ = ("texts", "task")
    TEXTS_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    texts: _containers.RepeatedScalarFieldContainer[str]
    task: str
    def __init__(
        self, texts: _Optional[_Iterable[str]] = ..., task: _Optional[str] = ...
    ) -> None: ...

class Embedding(_message.Message):
    __slots__ = ("vector",)
    VECTOR_FIELD_NUMBER: _ClassVar[int]
    vector: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, vector: _Optional[_Iterable[float]] = ...) -> None: ...

class EmbedResponse(_message.Message):
    __slots__ = ("embeddings", "processed_tokens")
    EMBEDDINGS_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_TOKENS_FIELD_NUMBER: _ClassVar[int]
    embeddings: _containers.RepeatedCompositeFieldContainer[Embedding]
    processed_tokens: int
    def __init__(
        self,
        embeddings: _Optional[_Iterable[_Union[Embedding, _Mapping]]] = ...,
        processed_tokens: _Optional[int] = ...,
    ) -> None: ...

class RerankRequest(_message.Message):
    __slots__ = ("query", "texts")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    TEXTS_FIELD_NUMBER: _ClassVar[int]
    query: str
    texts: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self, query: _Optional[str] = ..., texts: _Optional[_Iterable[str]] = ...
    ) -> None: ...

class RerankItem(_message.Message):
    __slots__ = ("score", "index")
    SCORE_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    score: float
    index: int
    def __init__(
        self, score: _Optional[float] = ..., index: _Optional[int] = ...
    ) -> None: ...

class RerankResponse(_message.Message):
    __slots__ = ("scores", "processed_tokens")
    SCORES_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_TOKENS_FIELD_NUMBER: _ClassVar[int]
    scores: _containers.RepeatedCompositeFieldContainer[RerankItem]
    processed_tokens: int
    def __init__(
        self,
        scores: _Optional[_Iterable[_Union[RerankItem, _Mapping]]] = ...,
        processed_tokens: _Optional[int] = ...,
    ) -> None: ...

class OcrRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class OcrResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
