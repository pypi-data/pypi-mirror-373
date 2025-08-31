import datetime

from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_TYPE_UNSPECIFIED: _ClassVar[EventType]
    EVENT_TYPE_SESSION_START: _ClassVar[EventType]
    EVENT_TYPE_SESSION_END: _ClassVar[EventType]
    EVENT_TYPE_AGENT_START: _ClassVar[EventType]
    EVENT_TYPE_AGENT_END: _ClassVar[EventType]
    EVENT_TYPE_AGENT_HANDOFF: _ClassVar[EventType]
    EVENT_TYPE_MODEL_INVOCATION_START: _ClassVar[EventType]
    EVENT_TYPE_MODEL_INVOCATION_END: _ClassVar[EventType]
    EVENT_TYPE_TOOL_CALL_START: _ClassVar[EventType]
    EVENT_TYPE_TOOL_CALL_END: _ClassVar[EventType]
    EVENT_TYPE_MCP_CALL_START: _ClassVar[EventType]
    EVENT_TYPE_MCP_CALL_END: _ClassVar[EventType]
    EVENT_TYPE_INPUT_RECEIVED: _ClassVar[EventType]
    EVENT_TYPE_OUTPUT_EMITTED: _ClassVar[EventType]
    EVENT_TYPE_ERROR: _ClassVar[EventType]
    EVENT_TYPE_RETRY: _ClassVar[EventType]
    EVENT_TYPE_POLICY_DECISION: _ClassVar[EventType]
    EVENT_TYPE_DATA_ACCESS: _ClassVar[EventType]
    EVENT_TYPE_STATE_UPDATE: _ClassVar[EventType]
    EVENT_TYPE_SYSTEM: _ClassVar[EventType]

class EventStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_STATUS_UNSPECIFIED: _ClassVar[EventStatus]
    EVENT_STATUS_STARTED: _ClassVar[EventStatus]
    EVENT_STATUS_IN_PROGRESS: _ClassVar[EventStatus]
    EVENT_STATUS_COMPLETED: _ClassVar[EventStatus]
    EVENT_STATUS_FAILED: _ClassVar[EventStatus]
    EVENT_STATUS_CANCELLED: _ClassVar[EventStatus]

class Severity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SEVERITY_UNSPECIFIED: _ClassVar[Severity]
    SEVERITY_DEBUG: _ClassVar[Severity]
    SEVERITY_INFO: _ClassVar[Severity]
    SEVERITY_WARN: _ClassVar[Severity]
    SEVERITY_ERROR: _ClassVar[Severity]

class Author(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUTHOR_UNSPECIFIED: _ClassVar[Author]
    AUTHOR_USER: _ClassVar[Author]
    AUTHOR_AGENT: _ClassVar[Author]
    AUTHOR_TOOL: _ClassVar[Author]
    AUTHOR_SYSTEM: _ClassVar[Author]
    AUTHOR_LLM: _ClassVar[Author]
EVENT_TYPE_UNSPECIFIED: EventType
EVENT_TYPE_SESSION_START: EventType
EVENT_TYPE_SESSION_END: EventType
EVENT_TYPE_AGENT_START: EventType
EVENT_TYPE_AGENT_END: EventType
EVENT_TYPE_AGENT_HANDOFF: EventType
EVENT_TYPE_MODEL_INVOCATION_START: EventType
EVENT_TYPE_MODEL_INVOCATION_END: EventType
EVENT_TYPE_TOOL_CALL_START: EventType
EVENT_TYPE_TOOL_CALL_END: EventType
EVENT_TYPE_MCP_CALL_START: EventType
EVENT_TYPE_MCP_CALL_END: EventType
EVENT_TYPE_INPUT_RECEIVED: EventType
EVENT_TYPE_OUTPUT_EMITTED: EventType
EVENT_TYPE_ERROR: EventType
EVENT_TYPE_RETRY: EventType
EVENT_TYPE_POLICY_DECISION: EventType
EVENT_TYPE_DATA_ACCESS: EventType
EVENT_TYPE_STATE_UPDATE: EventType
EVENT_TYPE_SYSTEM: EventType
EVENT_STATUS_UNSPECIFIED: EventStatus
EVENT_STATUS_STARTED: EventStatus
EVENT_STATUS_IN_PROGRESS: EventStatus
EVENT_STATUS_COMPLETED: EventStatus
EVENT_STATUS_FAILED: EventStatus
EVENT_STATUS_CANCELLED: EventStatus
SEVERITY_UNSPECIFIED: Severity
SEVERITY_DEBUG: Severity
SEVERITY_INFO: Severity
SEVERITY_WARN: Severity
SEVERITY_ERROR: Severity
AUTHOR_UNSPECIFIED: Author
AUTHOR_USER: Author
AUTHOR_AGENT: Author
AUTHOR_TOOL: Author
AUTHOR_SYSTEM: Author
AUTHOR_LLM: Author

class MessageContent(_message.Message):
    __slots__ = ("role", "text", "metadata")
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    role: str
    text: str
    metadata: _struct_pb2.Struct
    def __init__(self, role: _Optional[str] = ..., text: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class ToolCall(_message.Message):
    __slots__ = ("id", "name", "arguments", "auth_required", "function_name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ARGUMENTS_FIELD_NUMBER: _ClassVar[int]
    AUTH_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    arguments: _struct_pb2.Struct
    auth_required: bool
    function_name: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., arguments: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., auth_required: _Optional[bool] = ..., function_name: _Optional[str] = ...) -> None: ...

class ToolResponse(_message.Message):
    __slots__ = ("tool_call_id", "output", "error_message", "execution_time_ms", "http_status")
    TOOL_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    HTTP_STATUS_FIELD_NUMBER: _ClassVar[int]
    tool_call_id: str
    output: _struct_pb2.Struct
    error_message: str
    execution_time_ms: float
    http_status: int
    def __init__(self, tool_call_id: _Optional[str] = ..., output: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., error_message: _Optional[str] = ..., execution_time_ms: _Optional[float] = ..., http_status: _Optional[int] = ...) -> None: ...

class LLMInvocation(_message.Message):
    __slots__ = ("provider", "model", "request", "response", "prompt_tokens", "completion_tokens", "total_tokens", "temperature", "max_tokens", "top_p", "frequency_penalty", "presence_penalty", "start_time", "end_time", "duration_ms", "finish_reason")
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    PROMPT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    COMPLETION_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TOP_P_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_PENALTY_FIELD_NUMBER: _ClassVar[int]
    PRESENCE_PENALTY_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    FINISH_REASON_FIELD_NUMBER: _ClassVar[int]
    provider: str
    model: str
    request: _struct_pb2.Struct
    response: _struct_pb2.Struct
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    temperature: float
    max_tokens: int
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    duration_ms: float
    finish_reason: str
    def __init__(self, provider: _Optional[str] = ..., model: _Optional[str] = ..., request: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., response: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., prompt_tokens: _Optional[int] = ..., completion_tokens: _Optional[int] = ..., total_tokens: _Optional[int] = ..., temperature: _Optional[float] = ..., max_tokens: _Optional[int] = ..., top_p: _Optional[float] = ..., frequency_penalty: _Optional[float] = ..., presence_penalty: _Optional[float] = ..., start_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., duration_ms: _Optional[float] = ..., finish_reason: _Optional[str] = ...) -> None: ...

class PolicyDecision(_message.Message):
    __slots__ = ("policy_id", "outcome", "rule_ids", "rationale")
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    RULE_IDS_FIELD_NUMBER: _ClassVar[int]
    RATIONALE_FIELD_NUMBER: _ClassVar[int]
    policy_id: str
    outcome: str
    rule_ids: _containers.RepeatedScalarFieldContainer[str]
    rationale: str
    def __init__(self, policy_id: _Optional[str] = ..., outcome: _Optional[str] = ..., rule_ids: _Optional[_Iterable[str]] = ..., rationale: _Optional[str] = ...) -> None: ...

class DataAccess(_message.Message):
    __slots__ = ("datasource", "document_ids", "chunk_ids", "pii_categories")
    DATASOURCE_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_IDS_FIELD_NUMBER: _ClassVar[int]
    CHUNK_IDS_FIELD_NUMBER: _ClassVar[int]
    PII_CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    datasource: str
    document_ids: _containers.RepeatedScalarFieldContainer[str]
    chunk_ids: _containers.RepeatedScalarFieldContainer[str]
    pii_categories: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, datasource: _Optional[str] = ..., document_ids: _Optional[_Iterable[str]] = ..., chunk_ids: _Optional[_Iterable[str]] = ..., pii_categories: _Optional[_Iterable[str]] = ...) -> None: ...

class RedactionInfo(_message.Message):
    __slots__ = ("fields", "method", "salt_id")
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    SALT_ID_FIELD_NUMBER: _ClassVar[int]
    fields: _containers.RepeatedScalarFieldContainer[str]
    method: str
    salt_id: str
    def __init__(self, fields: _Optional[_Iterable[str]] = ..., method: _Optional[str] = ..., salt_id: _Optional[str] = ...) -> None: ...

class RetryInfo(_message.Message):
    __slots__ = ("attempt", "strategy", "backoff_ms")
    ATTEMPT_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    BACKOFF_MS_FIELD_NUMBER: _ClassVar[int]
    attempt: int
    strategy: str
    backoff_ms: int
    def __init__(self, attempt: _Optional[int] = ..., strategy: _Optional[str] = ..., backoff_ms: _Optional[int] = ...) -> None: ...

class PerformanceMetrics(_message.Message):
    __slots__ = ("cpu_percent", "memory_mb", "duration_ms", "throughput", "latency_ms")
    CPU_PERCENT_FIELD_NUMBER: _ClassVar[int]
    MEMORY_MB_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    THROUGHPUT_FIELD_NUMBER: _ClassVar[int]
    LATENCY_MS_FIELD_NUMBER: _ClassVar[int]
    cpu_percent: float
    memory_mb: float
    duration_ms: float
    throughput: float
    latency_ms: float
    def __init__(self, cpu_percent: _Optional[float] = ..., memory_mb: _Optional[float] = ..., duration_ms: _Optional[float] = ..., throughput: _Optional[float] = ..., latency_ms: _Optional[float] = ...) -> None: ...

class InfrastructureMetrics(_message.Message):
    __slots__ = ("resource_type", "metrics", "host", "process_id", "thread_id")
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    PROCESS_ID_FIELD_NUMBER: _ClassVar[int]
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    resource_type: str
    metrics: _struct_pb2.Struct
    host: str
    process_id: int
    thread_id: str
    def __init__(self, resource_type: _Optional[str] = ..., metrics: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., host: _Optional[str] = ..., process_id: _Optional[int] = ..., thread_id: _Optional[str] = ...) -> None: ...

class CostDetails(_message.Message):
    __slots__ = ("provider", "service", "input_tokens", "output_tokens", "total_tokens", "input_cost", "output_cost", "total_cost", "currency", "input_rate_per_token", "output_rate_per_token")
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    INPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TOKENS_FIELD_NUMBER: _ClassVar[int]
    INPUT_COST_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_COST_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COST_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    INPUT_RATE_PER_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_RATE_PER_TOKEN_FIELD_NUMBER: _ClassVar[int]
    provider: str
    service: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    currency: str
    input_rate_per_token: float
    output_rate_per_token: float
    def __init__(self, provider: _Optional[str] = ..., service: _Optional[str] = ..., input_tokens: _Optional[int] = ..., output_tokens: _Optional[int] = ..., total_tokens: _Optional[int] = ..., input_cost: _Optional[float] = ..., output_cost: _Optional[float] = ..., total_cost: _Optional[float] = ..., currency: _Optional[str] = ..., input_rate_per_token: _Optional[float] = ..., output_rate_per_token: _Optional[float] = ...) -> None: ...

class AgentHandoff(_message.Message):
    __slots__ = ("from_agent_id", "from_agent_name", "to_agent_id", "to_agent_name", "handoff_data", "reason", "handoff_type")
    FROM_AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    TO_AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    TO_AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    HANDOFF_DATA_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    HANDOFF_TYPE_FIELD_NUMBER: _ClassVar[int]
    from_agent_id: str
    from_agent_name: str
    to_agent_id: str
    to_agent_name: str
    handoff_data: _struct_pb2.Struct
    reason: str
    handoff_type: str
    def __init__(self, from_agent_id: _Optional[str] = ..., from_agent_name: _Optional[str] = ..., to_agent_id: _Optional[str] = ..., to_agent_name: _Optional[str] = ..., handoff_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., reason: _Optional[str] = ..., handoff_type: _Optional[str] = ...) -> None: ...

class MCPCall(_message.Message):
    __slots__ = ("server_name", "server_url", "operation", "method", "request", "response", "protocol_version", "execution_time_ms")
    SERVER_NAME_FIELD_NUMBER: _ClassVar[int]
    SERVER_URL_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_VERSION_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    server_name: str
    server_url: str
    operation: str
    method: str
    request: _struct_pb2.Struct
    response: _struct_pb2.Struct
    protocol_version: str
    execution_time_ms: float
    def __init__(self, server_name: _Optional[str] = ..., server_url: _Optional[str] = ..., operation: _Optional[str] = ..., method: _Optional[str] = ..., request: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., response: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., protocol_version: _Optional[str] = ..., execution_time_ms: _Optional[float] = ...) -> None: ...

class ErrorInfo(_message.Message):
    __slots__ = ("error_message", "error_code", "stack_trace", "recoverable", "recovery_action")
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    STACK_TRACE_FIELD_NUMBER: _ClassVar[int]
    RECOVERABLE_FIELD_NUMBER: _ClassVar[int]
    RECOVERY_ACTION_FIELD_NUMBER: _ClassVar[int]
    error_message: str
    error_code: str
    stack_trace: str
    recoverable: bool
    recovery_action: str
    def __init__(self, error_message: _Optional[str] = ..., error_code: _Optional[str] = ..., stack_trace: _Optional[str] = ..., recoverable: _Optional[bool] = ..., recovery_action: _Optional[str] = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ("event_id", "tenant_id", "project_id", "session_id", "span_id", "parent_span_id", "type", "severity", "status", "author", "timestamp", "agent_id", "agent_name", "invocation_id", "response_id", "is_partial", "is_final", "hash_prev", "content_hash", "worm_proof_id", "branch", "tags", "trace_id", "message", "tool_call", "tool_response", "llm_invocation", "policy", "data_access", "state_update", "error", "agent_handoff", "mcp_call", "retry", "redaction", "pii_categories", "performance", "infrastructure", "cost", "metadata", "extensions")
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SPAN_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_SPAN_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    INVOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    IS_PARTIAL_FIELD_NUMBER: _ClassVar[int]
    IS_FINAL_FIELD_NUMBER: _ClassVar[int]
    HASH_PREV_FIELD_NUMBER: _ClassVar[int]
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    WORM_PROOF_ID_FIELD_NUMBER: _ClassVar[int]
    BRANCH_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALL_FIELD_NUMBER: _ClassVar[int]
    TOOL_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    LLM_INVOCATION_FIELD_NUMBER: _ClassVar[int]
    POLICY_FIELD_NUMBER: _ClassVar[int]
    DATA_ACCESS_FIELD_NUMBER: _ClassVar[int]
    STATE_UPDATE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    AGENT_HANDOFF_FIELD_NUMBER: _ClassVar[int]
    MCP_CALL_FIELD_NUMBER: _ClassVar[int]
    RETRY_FIELD_NUMBER: _ClassVar[int]
    REDACTION_FIELD_NUMBER: _ClassVar[int]
    PII_CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    PERFORMANCE_FIELD_NUMBER: _ClassVar[int]
    INFRASTRUCTURE_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    EXTENSIONS_FIELD_NUMBER: _ClassVar[int]
    event_id: str
    tenant_id: str
    project_id: str
    session_id: str
    span_id: str
    parent_span_id: str
    type: EventType
    severity: Severity
    status: EventStatus
    author: Author
    timestamp: _timestamp_pb2.Timestamp
    agent_id: str
    agent_name: str
    invocation_id: str
    response_id: str
    is_partial: bool
    is_final: bool
    hash_prev: str
    content_hash: str
    worm_proof_id: str
    branch: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    trace_id: str
    message: MessageContent
    tool_call: ToolCall
    tool_response: ToolResponse
    llm_invocation: LLMInvocation
    policy: PolicyDecision
    data_access: DataAccess
    state_update: _struct_pb2.Struct
    error: ErrorInfo
    agent_handoff: AgentHandoff
    mcp_call: MCPCall
    retry: RetryInfo
    redaction: RedactionInfo
    pii_categories: _containers.RepeatedScalarFieldContainer[str]
    performance: PerformanceMetrics
    infrastructure: InfrastructureMetrics
    cost: CostDetails
    metadata: _struct_pb2.Struct
    extensions: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
    def __init__(self, event_id: _Optional[str] = ..., tenant_id: _Optional[str] = ..., project_id: _Optional[str] = ..., session_id: _Optional[str] = ..., span_id: _Optional[str] = ..., parent_span_id: _Optional[str] = ..., type: _Optional[_Union[EventType, str]] = ..., severity: _Optional[_Union[Severity, str]] = ..., status: _Optional[_Union[EventStatus, str]] = ..., author: _Optional[_Union[Author, str]] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., agent_id: _Optional[str] = ..., agent_name: _Optional[str] = ..., invocation_id: _Optional[str] = ..., response_id: _Optional[str] = ..., is_partial: _Optional[bool] = ..., is_final: _Optional[bool] = ..., hash_prev: _Optional[str] = ..., content_hash: _Optional[str] = ..., worm_proof_id: _Optional[str] = ..., branch: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ..., trace_id: _Optional[str] = ..., message: _Optional[_Union[MessageContent, _Mapping]] = ..., tool_call: _Optional[_Union[ToolCall, _Mapping]] = ..., tool_response: _Optional[_Union[ToolResponse, _Mapping]] = ..., llm_invocation: _Optional[_Union[LLMInvocation, _Mapping]] = ..., policy: _Optional[_Union[PolicyDecision, _Mapping]] = ..., data_access: _Optional[_Union[DataAccess, _Mapping]] = ..., state_update: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., error: _Optional[_Union[ErrorInfo, _Mapping]] = ..., agent_handoff: _Optional[_Union[AgentHandoff, _Mapping]] = ..., mcp_call: _Optional[_Union[MCPCall, _Mapping]] = ..., retry: _Optional[_Union[RetryInfo, _Mapping]] = ..., redaction: _Optional[_Union[RedactionInfo, _Mapping]] = ..., pii_categories: _Optional[_Iterable[str]] = ..., performance: _Optional[_Union[PerformanceMetrics, _Mapping]] = ..., infrastructure: _Optional[_Union[InfrastructureMetrics, _Mapping]] = ..., cost: _Optional[_Union[CostDetails, _Mapping]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., extensions: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ...) -> None: ...

class EventBatch(_message.Message):
    __slots__ = ("batch_id", "timestamp", "events", "metadata", "total_cost", "total_tokens", "total_duration_ms")
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COST_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    batch_id: str
    timestamp: _timestamp_pb2.Timestamp
    events: _containers.RepeatedCompositeFieldContainer[Event]
    metadata: _struct_pb2.Struct
    total_cost: float
    total_tokens: int
    total_duration_ms: float
    def __init__(self, batch_id: _Optional[str] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., events: _Optional[_Iterable[_Union[Event, _Mapping]]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., total_cost: _Optional[float] = ..., total_tokens: _Optional[int] = ..., total_duration_ms: _Optional[float] = ...) -> None: ...
