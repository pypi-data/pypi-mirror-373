from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import (
    ClassVar,
    Literal,
    Self,
)

from pydantic import BaseModel, Field
from typing_extensions import deprecated

from linq.schema import workflow_api
from linq.sdk_entity import (
    InputType,
    OutputType,
    SDKEntity,
)

DEPRECATED_FILTER_FIELD = Field(description="Event type triggering the hook. No longer required.", deprecated=True)


class Filters(str, Enum):
    """Types of events that can trigger a hook."""

    ON_TASK_STATE_CHANGE = "on_task_state_change"
    ON_RUN_STATE_CHANGE = "on_run_state_change"
    ON_LABWARE_MOVEMENT = "on_labware_movement"
    ON_SAFETY_STATE_CHANGE = "on_safety_state_change"
    ON_NEW_PLAN = "on_new_plan"


class HookParameters(BaseModel):
    url: str
    headers: dict[str, str] = Field(
        default_factory=dict,
        description="HTTP headers to include in the request",
    )

    def to_api_input(self) -> workflow_api.HookParametersInput:
        return workflow_api.HookParametersInput(
            url=self.url,
            headers=self.headers,
        )

    @classmethod
    def from_api_output(cls, api_output_parameters: workflow_api.HookParameters) -> Self:
        return cls(
            url=api_output_parameters.url,
            headers=api_output_parameters.headers if api_output_parameters.headers is not None else {},
        )


@dataclass(kw_only=True)
class BaseHook(SDKEntity[InputType, OutputType]):
    """Base hook class to be triggered by state change."""

    parameters: HookParameters

    @classmethod
    @abstractmethod
    def from_api_output(cls, api_output: OutputType) -> Self:
        pass


@dataclass(kw_only=True, slots=True)
class TaskStateChangeHook(BaseHook[workflow_api.TaskStateChangeHookInput, workflow_api.TaskStateChangeHook]):
    """Hook to be triggered when a task state changes."""

    filter: Literal[Filters.ON_TASK_STATE_CHANGE] = DEPRECATED_FILTER_FIELD
    event_filter: ClassVar[Literal[Filters.ON_TASK_STATE_CHANGE]] = Filters.ON_TASK_STATE_CHANGE

    task_ids: list[str] = Field(
        description="List of task IDs that the hook should be triggered for. If empty, the hook will be triggered for all tasks.",
    )

    def to_api_input(self) -> workflow_api.TaskStateChangeHookInput:
        return workflow_api.TaskStateChangeHookInput(
            filter=self.event_filter.value,
            parameters=self.parameters.to_api_input(),
            task_ids=self.task_ids,
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.TaskStateChangeHook) -> Self:
        return cls(
            parameters=HookParameters.from_api_output(api_output.parameters),
            task_ids=api_output.task_ids,
        )


@dataclass(kw_only=True, slots=True)
class RunStateChangeHook(BaseHook[workflow_api.RunStateChangeHookInput, workflow_api.RunStateChangeHook]):
    """Hook to be triggered when a run state changes."""

    filter: Literal[Filters.ON_RUN_STATE_CHANGE] = DEPRECATED_FILTER_FIELD
    event_filter: ClassVar[Literal[Filters.ON_RUN_STATE_CHANGE]] = Filters.ON_RUN_STATE_CHANGE

    def to_api_input(self) -> workflow_api.RunStateChangeHookInput:
        return workflow_api.RunStateChangeHookInput(
            filter=self.event_filter.value,
            parameters=self.parameters.to_api_input(),
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.RunStateChangeHook) -> Self:
        return cls(
            parameters=HookParameters.from_api_output(api_output.parameters),
        )


@dataclass(kw_only=True, slots=True)
class LabwareMovementHook(BaseHook[workflow_api.LabwareMovementHookInput, workflow_api.LabwareMovementHook]):
    """Hook to be triggered when labware is transported."""

    filter: Literal[Filters.ON_LABWARE_MOVEMENT] = DEPRECATED_FILTER_FIELD
    event_filter: ClassVar[Literal[Filters.ON_LABWARE_MOVEMENT]] = Filters.ON_LABWARE_MOVEMENT
    labware_ids: list[str] = Field(
        description="List of labware IDs that the hook should be triggered for. If empty, the hook will be triggered for all labware.",
    )
    trigger_on: Literal["start", "end", "both"] = Field(
        "both",
        description="When to trigger the hook. 'start' triggers the hook when the labware is picked up, 'end' triggers the hook when the labware is placed down, 'both' does both.",
        title="Trigger On",
    )

    def to_api_input(self) -> workflow_api.LabwareMovementHookInput:
        return workflow_api.LabwareMovementHookInput(
            filter=self.event_filter.value,
            parameters=self.parameters.to_api_input(),
            labware_ids=self.labware_ids,
            trigger_on=self.trigger_on,
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.LabwareMovementHook) -> Self:
        return cls(
            parameters=HookParameters.from_api_output(api_output.parameters),
            labware_ids=api_output.labware_ids,
            trigger_on=api_output.trigger_on,
        )


@dataclass(kw_only=True, slots=True)
class SafetyStateChangeHook(BaseHook[workflow_api.SafetyStateChangeHookInput, workflow_api.SafetyStateChangeHook]):
    """Hook to be triggered on changes to the state of the safety adapter."""

    filter: Literal[Filters.ON_SAFETY_STATE_CHANGE] = DEPRECATED_FILTER_FIELD
    event_filter: ClassVar[Literal[Filters.ON_SAFETY_STATE_CHANGE]] = Filters.ON_SAFETY_STATE_CHANGE

    def to_api_input(self) -> workflow_api.SafetyStateChangeHookInput:
        return workflow_api.SafetyStateChangeHookInput(
            filter=self.event_filter.value,
            parameters=self.parameters.to_api_input(),
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.SafetyStateChangeHook) -> Self:
        return cls(
            parameters=HookParameters.from_api_output(api_output.parameters),
        )


@dataclass(kw_only=True, slots=True)
class NewPlanHook(BaseHook[workflow_api.NewPlanHookInput, workflow_api.NewPlanHook]):
    """Hook to be triggered when a new plan is generated."""

    filter: Literal[Filters.ON_NEW_PLAN] = DEPRECATED_FILTER_FIELD
    event_filter: ClassVar[Literal[Filters.ON_NEW_PLAN]] = Filters.ON_NEW_PLAN

    def to_api_input(self) -> workflow_api.NewPlanHookInput:
        return workflow_api.NewPlanHookInput(
            filter=self.event_filter.value,
            parameters=self.parameters.to_api_input(),
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.NewPlanHook) -> Self:
        return cls(
            parameters=HookParameters.from_api_output(api_output.parameters),
        )
