from chaukas.spec.common.v1 import events_pb2 as _events_pb2
from chaukas.spec.common.v1 import query_pb2 as _query_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HealthzRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthzResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCapabilitiesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCapabilitiesResponse(_message.Message):
    __slots__ = ("capabilities",)
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    capabilities: _query_pb2.Capabilities
    def __init__(self, capabilities: _Optional[_Union[_query_pb2.Capabilities, _Mapping]] = ...) -> None: ...

class IngestEventRequest(_message.Message):
    __slots__ = ("event",)
    EVENT_FIELD_NUMBER: _ClassVar[int]
    event: _events_pb2.Event
    def __init__(self, event: _Optional[_Union[_events_pb2.Event, _Mapping]] = ...) -> None: ...

class IngestEventResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class IngestEventBatchRequest(_message.Message):
    __slots__ = ("event_batch",)
    EVENT_BATCH_FIELD_NUMBER: _ClassVar[int]
    event_batch: _events_pb2.EventBatch
    def __init__(self, event_batch: _Optional[_Union[_events_pb2.EventBatch, _Mapping]] = ...) -> None: ...

class IngestEventBatchResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class QueryEventsRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: _query_pb2.QueryRequest
    def __init__(self, query: _Optional[_Union[_query_pb2.QueryRequest, _Mapping]] = ...) -> None: ...

class QueryEventsResponse(_message.Message):
    __slots__ = ("response",)
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: _query_pb2.QueryResponse
    def __init__(self, response: _Optional[_Union[_query_pb2.QueryResponse, _Mapping]] = ...) -> None: ...
