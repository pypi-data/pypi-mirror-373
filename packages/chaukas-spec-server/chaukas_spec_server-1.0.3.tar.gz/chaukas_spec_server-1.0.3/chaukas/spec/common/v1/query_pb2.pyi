import datetime

from chaukas.spec.common.v1 import events_pb2 as _events_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SortOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SORT_ORDER_UNSPECIFIED: _ClassVar[SortOrder]
    SORT_ORDER_ASC: _ClassVar[SortOrder]
    SORT_ORDER_DESC: _ClassVar[SortOrder]
SORT_ORDER_UNSPECIFIED: SortOrder
SORT_ORDER_ASC: SortOrder
SORT_ORDER_DESC: SortOrder

class TimeRange(_message.Message):
    __slots__ = ("start", "end")
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    start: _timestamp_pb2.Timestamp
    end: _timestamp_pb2.Timestamp
    def __init__(self, start: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class QueryFilter(_message.Message):
    __slots__ = ("tenant_id", "project_id", "session_id", "agent_id", "span_id", "trace_id", "types", "statuses", "severities", "tags", "text_query", "time")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    SPAN_ID_FIELD_NUMBER: _ClassVar[int]
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    TYPES_FIELD_NUMBER: _ClassVar[int]
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    SEVERITIES_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    TEXT_QUERY_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    project_id: str
    session_id: str
    agent_id: str
    span_id: str
    trace_id: str
    types: _containers.RepeatedScalarFieldContainer[_events_pb2.EventType]
    statuses: _containers.RepeatedScalarFieldContainer[_events_pb2.EventStatus]
    severities: _containers.RepeatedScalarFieldContainer[_events_pb2.Severity]
    tags: _containers.RepeatedScalarFieldContainer[str]
    text_query: str
    time: TimeRange
    def __init__(self, tenant_id: _Optional[str] = ..., project_id: _Optional[str] = ..., session_id: _Optional[str] = ..., agent_id: _Optional[str] = ..., span_id: _Optional[str] = ..., trace_id: _Optional[str] = ..., types: _Optional[_Iterable[_Union[_events_pb2.EventType, str]]] = ..., statuses: _Optional[_Iterable[_Union[_events_pb2.EventStatus, str]]] = ..., severities: _Optional[_Iterable[_Union[_events_pb2.Severity, str]]] = ..., tags: _Optional[_Iterable[str]] = ..., text_query: _Optional[str] = ..., time: _Optional[_Union[TimeRange, _Mapping]] = ...) -> None: ...

class QueryRequest(_message.Message):
    __slots__ = ("filter", "page_size", "page_token", "order_by_time")
    FILTER_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_TIME_FIELD_NUMBER: _ClassVar[int]
    filter: QueryFilter
    page_size: int
    page_token: str
    order_by_time: SortOrder
    def __init__(self, filter: _Optional[_Union[QueryFilter, _Mapping]] = ..., page_size: _Optional[int] = ..., page_token: _Optional[str] = ..., order_by_time: _Optional[_Union[SortOrder, str]] = ...) -> None: ...

class QueryResponse(_message.Message):
    __slots__ = ("events", "next_page_token")
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[_events_pb2.Event]
    next_page_token: str
    def __init__(self, events: _Optional[_Iterable[_Union[_events_pb2.Event, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...

class Capabilities(_message.Message):
    __slots__ = ("worm_retention", "audit_proofs", "distributed_query", "rbac", "sso", "policy_decisions", "data_access_events")
    WORM_RETENTION_FIELD_NUMBER: _ClassVar[int]
    AUDIT_PROOFS_FIELD_NUMBER: _ClassVar[int]
    DISTRIBUTED_QUERY_FIELD_NUMBER: _ClassVar[int]
    RBAC_FIELD_NUMBER: _ClassVar[int]
    SSO_FIELD_NUMBER: _ClassVar[int]
    POLICY_DECISIONS_FIELD_NUMBER: _ClassVar[int]
    DATA_ACCESS_EVENTS_FIELD_NUMBER: _ClassVar[int]
    worm_retention: bool
    audit_proofs: bool
    distributed_query: bool
    rbac: bool
    sso: bool
    policy_decisions: bool
    data_access_events: bool
    def __init__(self, worm_retention: _Optional[bool] = ..., audit_proofs: _Optional[bool] = ..., distributed_query: _Optional[bool] = ..., rbac: _Optional[bool] = ..., sso: _Optional[bool] = ..., policy_decisions: _Optional[bool] = ..., data_access_events: _Optional[bool] = ...) -> None: ...
