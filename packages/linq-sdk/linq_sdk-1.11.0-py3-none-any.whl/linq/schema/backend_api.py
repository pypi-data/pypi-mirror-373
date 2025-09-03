from datetime import datetime
from enum import Enum
from typing import Generic, Literal, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkcellMode(str, Enum):
    ACTIVE = "active"
    VALIDATING = "validating"
    MAINTENANCE = "maintenance"


class WorkcellStatus(str, Enum):
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"
    READY = "ready"
    RUNNING = "running"


class DeviceStateStatus(str, Enum):
    NO_WORKFLOW = "no_workflow"
    INIT = "init"
    LOADING = "loading"
    UNCALIBRATED = "uncalibrated"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    RESETTING = "resetting"
    ERROR = "error"
    ACTION_REQUIRED = "action_required"
    EMERGENCY_STOP = "emergency_stop"
    ABORTED = "aborted"
    OFFLINE = "offline"


class DeviceState(BaseModel):
    status: DeviceStateStatus
    details: str | None


class DeviceErrorInstrument(BaseModel):
    id: str
    name: str
    type: str


class DeviceErrorSeverity(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


class DeviceErrorAvailableActions(str, Enum):
    Reset = "reset"
    Skip = "skip-task"
    Retry = "retry-task"
    Abort = "abort"
    AbortLabware = "abort-labware"


class DeviceErrorAffectedLabwareLocation(BaseModel):
    instrument_id: str
    slot: int


class DeviceErrorAffectedLabware(BaseModel):
    labware_id: str
    reason: str
    current_location: DeviceErrorAffectedLabwareLocation


class DeviceError(BaseModel):
    id: UUID
    run_history_id: UUID
    error_code: str
    error_severity: DeviceErrorSeverity
    error_message: str
    instrument: DeviceErrorInstrument
    available_actions: list[DeviceErrorAvailableActions]
    timestamp: datetime
    labware_affected_by_abort: list[DeviceErrorAffectedLabware]


class Device(BaseModel):
    id: UUID
    name: str
    serial: str
    online: bool
    state: DeviceState
    error: DeviceError | None = None


class DeviceDataOnly(BaseModel):
    errors: list[DeviceError] | None = None


class DeviceData(Device, DeviceDataOnly):
    pass


class Workcell(BaseModel):
    hub_id: UUID
    hub_last_access: datetime
    id: UUID
    mode: WorkcellMode
    name: str
    status: WorkcellStatus


class Organization(BaseModel):
    externalID: str  # "org_XXXXXXXXXXXXXXXX"
    id: UUID
    logo: str  # URL
    name: str
    slug: str
    workspace: UUID


class Owner(BaseModel):
    id: UUID
    type: Literal["organization"]


class WorkflowReference(BaseModel):
    id: UUID
    name: str
    checksum: str
    status: Literal["valid", "outdated", "invalid"]


class Tag(BaseModel):
    id: UUID
    name: str
    color: str
    is_archived: bool


class RunHistory(BaseModel):
    id: UUID
    device_id: UUID
    last_updated: datetime
    owner: Owner
    outcome: str
    outcome_details: Optional[str] = None
    start_time: datetime
    stop_time: Optional[datetime] = None
    workflow: Optional[WorkflowReference] = None
    tags: list[Tag] = Field(default_factory=list)


T = TypeVar("T")


class CursorPaginatedResults(BaseModel, Generic[T]):
    list: list[T]
    next_cursor: Optional[str] = None


class CommandStatusResult(BaseModel):
    status: Optional[str]
    instance_name: Optional[str]
    status_details: Optional[str]
