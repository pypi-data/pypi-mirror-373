from chaukas.spec.common.v1 import events_pb2 as _events_pb2
from chaukas.spec.common.v1 import query_pb2 as _query_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class IngestEventResponse(_message.Message):
    __slots__ = ("event_id", "status", "processed_at")
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_AT_FIELD_NUMBER: _ClassVar[int]
    event_id: str
    status: str
    processed_at: int
    def __init__(self, event_id: _Optional[str] = ..., status: _Optional[str] = ..., processed_at: _Optional[int] = ...) -> None: ...

class IngestEventBatchResponse(_message.Message):
    __slots__ = ("batch_id", "accepted_count", "rejected_count", "rejected_event_ids")
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_COUNT_FIELD_NUMBER: _ClassVar[int]
    REJECTED_COUNT_FIELD_NUMBER: _ClassVar[int]
    REJECTED_EVENT_IDS_FIELD_NUMBER: _ClassVar[int]
    batch_id: str
    accepted_count: int
    rejected_count: int
    rejected_event_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, batch_id: _Optional[str] = ..., accepted_count: _Optional[int] = ..., rejected_count: _Optional[int] = ..., rejected_event_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class GetEventStatsRequest(_message.Message):
    __slots__ = ("tenant_id", "project_id", "time_range")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TIME_RANGE_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    project_id: str
    time_range: _query_pb2.TimeRange
    def __init__(self, tenant_id: _Optional[str] = ..., project_id: _Optional[str] = ..., time_range: _Optional[_Union[_query_pb2.TimeRange, _Mapping]] = ...) -> None: ...

class GetEventStatsResponse(_message.Message):
    __slots__ = ("total_events", "total_sessions", "events_by_type", "avg_session_duration_ms")
    class EventsByTypeEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    TOTAL_EVENTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SESSIONS_FIELD_NUMBER: _ClassVar[int]
    EVENTS_BY_TYPE_FIELD_NUMBER: _ClassVar[int]
    AVG_SESSION_DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    total_events: int
    total_sessions: int
    events_by_type: _containers.ScalarMap[str, int]
    avg_session_duration_ms: float
    def __init__(self, total_events: _Optional[int] = ..., total_sessions: _Optional[int] = ..., events_by_type: _Optional[_Mapping[str, int]] = ..., avg_session_duration_ms: _Optional[float] = ...) -> None: ...

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

class IngestEventBatchRequest(_message.Message):
    __slots__ = ("event_batch",)
    EVENT_BATCH_FIELD_NUMBER: _ClassVar[int]
    event_batch: _events_pb2.EventBatch
    def __init__(self, event_batch: _Optional[_Union[_events_pb2.EventBatch, _Mapping]] = ...) -> None: ...

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
