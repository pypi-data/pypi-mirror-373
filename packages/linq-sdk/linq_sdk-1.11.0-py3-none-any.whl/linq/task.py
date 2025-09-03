import inspect
import re
import uuid
from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Self,
    Sequence,
    TypeAlias,
    TypeVar,
    Union,
    cast,
    overload,
)

from linq.parameters import ParameterReference
from linq.schema.workflow_api import IntegerParameterDefinitionInput, ParameterReferenceInput
from linq.schema.workflow_api_types import (
    APIData,
    APIDataInput,
)
from linq.types import ComparisonOperator, ElseComparison

from .labware import Labware, SlotRange
from .parameters import IntegerParameterDefinition
from .schema import workflow_api
from .sdk_entity import SDKEntity

Task = Union["ActionTask", "CodeTask", "Conditional", "SftpDataConnector", "OperatorTransport"]
TaskLike = TypeVar("TaskLike", "ActionTask", "CodeTask", "Conditional", "SftpDataConnector", "OperatorTransport")


@dataclass(kw_only=True, slots=True)
class AvailableFailureActions(SDKEntity[workflow_api.AvailableActionsInput, workflow_api.AvailableActions]):
    """Available actions that can be taken by an operator if a task fails."""

    complete_manually: bool = True
    """Allow manually completing the task."""

    retry: bool = True
    """Allow retrying."""

    def to_api_input(self) -> workflow_api.AvailableActionsInput:
        return workflow_api.AvailableActionsInput(
            complete_manually=self.complete_manually,
            retry=self.retry,
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.AvailableActions) -> Self:
        return cls(
            complete_manually=api_output.complete_manually,
            retry=api_output.retry,
        )


@dataclass(slots=True)
class ConditionalSourceTask(SDKEntity[workflow_api.ConditionalSourceTaskInput, workflow_api.ConditionalSourceTask]):
    """Specifies the potential source tasks that labware can be retrieved from."""

    tasks: list[Task]

    def to_api_input(self) -> workflow_api.ConditionalSourceTaskInput:
        return workflow_api.ConditionalSourceTaskInput(task_ids=[task.id for task in self.tasks])

    @classmethod
    def from_api_output(cls, api_output: workflow_api.ConditionalSourceTask, tasks: list[Task]) -> Self:
        # add the tasks in the same order as in api_output
        temp_tasks = {task.id: task for task in tasks if task.id in api_output.task_ids}
        return cls(tasks=[temp_tasks[task_id] for task_id in api_output.task_ids])


@dataclass(slots=True)
class SlotFillingRule(SDKEntity[workflow_api.SlotFillingRuleInput, workflow_api.SlotFillingRule]):
    range: SlotRange | list[SlotRange]
    """The range of slots that the labware can be placed in."""

    min_count: int | None = None
    """The minimum number of labware items that must be placed in the slots."""

    max_count: int | None = None
    """The maximum number of labware items that can be placed in the slots."""

    distribution: workflow_api.SlotFillingDistribution = "unique"
    """How the labware will be distributed across the slots. `unique` ensure each labware is placed in a unique slot. `non_unique` allows multiple labware to be placed in the same slot over many instances of the task"""

    def to_api_input(self) -> workflow_api.SlotFillingRuleInput:
        return workflow_api.SlotFillingRuleInput(
            range=self.range.to_api_input()
            if isinstance(self.range, SlotRange)
            else [r.to_api_input() for r in self.range],
            min_count=self.min_count,
            max_count=self.max_count,
            distribution=self.distribution,
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.SlotFillingRule) -> Self:
        if isinstance(api_output.range, workflow_api.SlotRange):
            ranges = SlotRange.from_api_output(api_output.range)
        else:
            ranges = [SlotRange.from_api_output(r) for r in api_output.range]
        return cls(
            range=ranges,
            min_count=api_output.min_count,
            max_count=api_output.max_count,
            distribution=api_output.distribution,
        )


@dataclass(slots=True)
class LabwareSource(SDKEntity[workflow_api.LabwareSourceInput, workflow_api.LabwareSource]):
    """Specifies the labware required for a task."""

    labware: Labware
    """Labware being passed into a task."""

    destination_slot: int | SlotFillingRule = 1
    """The instrument slot where the labware will be placed, or the rule for filling slots with labware (batching)"""

    source_task: "ActionTask | ConditionalSourceTask | OperatorTransport | None" = None
    """ID of the task the labware is being transported from. None for tasks retrieving labware from their initial instrument."""

    dependencies: list["Task"] = field(default_factory=list)
    """Additional tasks that have to be completed before the labware for the task is retrieved."""

    units_consumed: int | None = None
    "The number of units of the labware that are consumed in the task. Tied to the total_units of the labware. Leave blank for no units to be consumed."

    def _get_source_task_for_input(self) -> str | workflow_api.ConditionalSourceTaskInput | None:
        if isinstance(self.source_task, (ActionTask, OperatorTransport)):
            return self.source_task.id
        if isinstance(self.source_task, ConditionalSourceTask):
            return workflow_api.ConditionalSourceTaskInput(task_ids=[task.id for task in self.source_task.tasks])
        return None

    def to_api_input(self) -> workflow_api.LabwareSourceInput:
        dependencies = [dependency.id for dependency in self.dependencies]
        return workflow_api.LabwareSourceInput(
            type="labware_source",
            labware_id=self.labware.id,
            destination_slot=self.destination_slot
            if isinstance(self.destination_slot, int)
            else self.destination_slot.to_api_input(),
            source_task=self._get_source_task_for_input(),
            dependencies=dependencies,
            units_consumed=self.units_consumed,
        )


@dataclass(slots=True)
class StoredLabware(SDKEntity[workflow_api.StoredLabwareInput, workflow_api.StoredLabware]):
    labware: Labware
    slot: int

    def to_api_input(self) -> workflow_api.StoredLabwareInput:
        return workflow_api.StoredLabwareInput(
            type="stored_labware",
            labware_id=self.labware.id,
            slot=self.slot,
        )


@dataclass(slots=True)
class OutputSlotFillingRule(SDKEntity[workflow_api.OutputSlotFillingRuleInput, workflow_api.OutputSlotFillingRule]):
    behavior: workflow_api.OutputSlotFillingBehavior = "match_input"
    """The output slot filling behaviour."""

    def to_api_input(self) -> workflow_api.OutputSlotFillingRuleInput:
        return workflow_api.OutputSlotFillingRuleInput(behavior=self.behavior)

    @classmethod
    def from_api_output(cls, api_output: workflow_api.OutputSlotFillingRule) -> Self:
        return cls(behavior=api_output.behavior)


@dataclass(slots=True)
class LabwareOutput(SDKEntity[workflow_api.LabwareOutputItemInput, workflow_api.LabwareOutput]):
    """Specifies the output of labware from a task."""

    labware: Labware
    """Labware output by the task."""

    slot: int | OutputSlotFillingRule = 1
    """The slot the task outputs the labware at. Defaults to 1. If using a SlotFillingRule for the input, use OutputSlotFillingRule for the output to match the slots."""

    def to_api_input(self) -> workflow_api.LabwareOutputItemInput:
        return workflow_api.LabwareOutputItemInput(
            type="labware_output",
            labware_id=self.labware.id,
            slot=self.slot if isinstance(self.slot, int) else self.slot.to_api_input(),
        )


ComparisonLeftHandSide: TypeAlias = "TaskOutputReference | ReferenceData "
ComparisonRightHandSide: TypeAlias = (
    "TaskOutputReference | ReferenceData | ParameterReference | workflow_api.JsonSerializable"
)


@dataclass(slots=True, kw_only=True)
class Comparison(SDKEntity[workflow_api.ComparisonInput, workflow_api.Comparison]):
    lhs: ComparisonLeftHandSide
    rhs: ComparisonRightHandSide
    operator: ComparisonOperator

    def _rhs_to_api_input(self) -> APIDataInput:
        if isinstance(self.rhs, (TaskOutputReference, ReferenceData, ParameterReference)):
            return self.rhs.to_api_input()
        return workflow_api.StaticDataInput(value=self.rhs)

    @staticmethod
    def _lhs_from_api_output(
        api_output: workflow_api.TaskOutputReference | workflow_api.ReferenceData,
        tasks: dict[str, Task],
    ) -> ComparisonLeftHandSide:
        if isinstance(api_output, workflow_api.TaskOutputReference):
            return TaskOutputReference.from_api_output(api_output, tasks)
        return ReferenceData.from_api_output(api_output)

    @staticmethod
    def _rhs_from_api_output(
        api_output: APIData,
        tasks: dict[str, Task],
    ) -> ComparisonRightHandSide:
        if isinstance(api_output, workflow_api.TaskOutputReference):
            return TaskOutputReference.from_api_output(api_output, tasks)
        if isinstance(api_output, workflow_api.ReferenceData):
            return ReferenceData.from_api_output(api_output)
        if isinstance(api_output, workflow_api.ParameterReference):
            return ParameterReference.from_api_output(api_output)
        return api_output.value

    def to_api_input(self) -> workflow_api.ComparisonInput:
        return workflow_api.ComparisonInput(
            lhs=self.lhs.to_api_input(),
            rhs=self._rhs_to_api_input(),
            operator=self.operator,
        )

    @classmethod
    def from_api_output(
        cls,
        api_output: workflow_api.Comparison,
        tasks: dict[str, Task],
    ) -> Self:
        return cls(
            lhs=cls._lhs_from_api_output(api_output.lhs, tasks),
            rhs=cls._rhs_from_api_output(api_output.rhs, tasks),
            operator=api_output.operator,
        )


@dataclass(kw_only=True, slots=True)
class TaskOutputReference(SDKEntity[workflow_api.TaskOutputReferenceInput, workflow_api.TaskOutputReference]):
    task: Task
    """The task that produces the data"""

    output_name: str | None = field(default=None)
    """The name of the output from the task. Can leave as None if the task has only one output."""

    def to_api_input(self) -> workflow_api.TaskOutputReferenceInput:
        return workflow_api.TaskOutputReferenceInput(task_id=self.task.id, output_name=self.output_name)

    @classmethod
    def from_api_output(
        cls,
        api_output: workflow_api.TaskOutputReference,
        tasks: dict[str, Task],
    ) -> Self:
        task = tasks.get(api_output.task_id)
        if not task:
            raise ValueError(f"Task not found from api_output: {api_output.task_id}")
        return cls(
            task=task,
            output_name=api_output.output_name,
        )

    @staticmethod
    def _verify_rhs(other: object) -> ComparisonRightHandSide:
        # TODO verify rhs is correct type
        return cast(ComparisonRightHandSide, other)

    def __eq__(self, other: object) -> "Comparison":  # type: ignore[reportIncompatibleMethodOverride]
        return Comparison(lhs=self, rhs=self._verify_rhs(other), operator="==")

    def __ne__(self, other: object) -> "Comparison":  # type: ignore[reportIncompatibleMethodOverride]
        return Comparison(lhs=self, rhs=self._verify_rhs(other), operator="!=")

    def __lt__(self, other: object) -> "Comparison":
        return Comparison(lhs=self, rhs=self._verify_rhs(other), operator="<")

    def __le__(self, other: object) -> "Comparison":
        return Comparison(lhs=self, rhs=self._verify_rhs(other), operator="<=")

    def __gt__(self, other: object) -> "Comparison":
        return Comparison(lhs=self, rhs=self._verify_rhs(other), operator=">")

    def __ge__(self, other: object) -> "Comparison":
        return Comparison(lhs=self, rhs=self._verify_rhs(other), operator=">=")

    def equals_any(self, other: Sequence[int | bool | str | float | None] | "TaskOutputReference" | "ReferenceData"):
        return Comparison(lhs=self, rhs=other, operator="in")  # type: ignore

    def equals_none(self, other: Sequence[int | bool | str | float | None] | "TaskOutputReference" | "ReferenceData"):
        return Comparison(lhs=self, rhs=other, operator="not in")  # type: ignore


@dataclass(kw_only=True, slots=True)
class ReferenceData(SDKEntity[workflow_api.ReferenceDataInput, workflow_api.ReferenceData]):
    key: str

    def to_api_input(self) -> workflow_api.ReferenceDataInput:
        return workflow_api.ReferenceDataInput(key=self.key)

    @classmethod
    def from_api_output(cls, api_output: workflow_api.ReferenceData) -> Self:
        return cls(key=api_output.key)


_Input = TaskOutputReference | ReferenceData | ParameterReference | workflow_api.JsonSerializable | SDKEntity


class Inputs(dict[str, _Input], SDKEntity[dict[str, APIDataInput], APIData]):
    def __init__(self, **kwargs: _Input):
        self.update(kwargs)

    def to_api_input(self) -> dict[str, APIDataInput]:
        out = dict()
        for key, value in self.items():
            if isinstance(value, (TaskOutputReference, ReferenceData, ParameterReference)):
                out[key] = value.to_api_input()
            elif isinstance(value, SDKEntity):
                out[key] = workflow_api.StaticDataInput(value=value.to_api_input())
            else:
                out[key] = workflow_api.StaticDataInput(value=value)
        return out

    @classmethod
    def from_api_output(
        cls,
        api_output: dict[str, APIData],
        data_reference_tasks: dict[str, Task],  # Map of task id to task
    ) -> Self:
        args = cls()
        for input_name, input_value in api_output.items():
            if isinstance(input_value, workflow_api.TaskOutputReference):
                args[input_name] = TaskOutputReference(
                    task=data_reference_tasks[input_value.task_id],
                    output_name=input_value.output_name,
                )
            elif isinstance(input_value, workflow_api.StaticData):
                args[input_name] = input_value.value
            elif isinstance(input_value, workflow_api.ReferenceData):
                args[input_name] = ReferenceData(key=input_value.key)
            else:
                raise NotImplementedError(f"Unknown input type {input_value}")
        return args


@dataclass(kw_only=True, slots=True)
class MockBehaviour(SDKEntity[workflow_api.MockBehaviourInput, workflow_api.MockBehaviour]):
    execution_time: float | None = None
    """Execution time in seconds. Overrides the default execution time of the task. If set to 0, task will not start"""

    success: bool = True
    """Whether the task should succeed or fail"""

    data_outputs: dict[str, workflow_api.JsonSerializable] | None = None
    """key,value pairs of data to be stored in the data store after the task is completed"""

    def to_api_input(self) -> workflow_api.MockBehaviourInput:
        return workflow_api.MockBehaviourInput(
            execution_time=self.execution_time,
            success=self.success,
            data_outputs=self.data_outputs,
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.MockBehaviour) -> Self:
        return cls(
            execution_time=api_output.execution_time,
            success=api_output.success,
            data_outputs=api_output.data_outputs,
        )


@dataclass(kw_only=True, slots=True)
class BaseTask:
    id: str = ""
    """Unique ID of this task."""

    description: str = ""
    """Description."""

    dependencies: list[Task] = field(default_factory=list)
    """Tasks that have to be executed before this task can run."""

    @abstractmethod
    def _generate_id(self) -> str:
        """Generate a unique id for the task."""

    @abstractmethod
    def _generate_description(self) -> str:
        """Generate a description for the task, used if none is supplied directly."""

    def __post_init__(self) -> None:
        if self.id == "":
            self.id = self._generate_id()

        if self.description == "":
            self.description = self._generate_description()

    @abstractmethod
    def out(self, output_name: str | None = None) -> TaskOutputReference:
        """Reference to the output of this task. If the task has only one output, output_name can be left as None."""
        ...


@dataclass(kw_only=True, slots=True)
class ActionTask(SDKEntity[workflow_api.ActionTaskInput, workflow_api.ActionTask], BaseTask):
    """A Task executing an action."""

    action: str = ""
    """ID of the action taken (see driver CLI for possible actions for each instrument.)"""

    time_estimate: int | ParameterReference = field(default=1)
    """Estimated time to execute the task."""

    instrument_type: str
    """Type of the instrument this task runs on."""

    labware_sources: list[LabwareSource | StoredLabware] = field(default_factory=list)
    """Defines the source of each labware used in this task."""

    labware_outputs: list[LabwareOutput | StoredLabware] = field(default_factory=list)
    """Outputs of this task. If left empty, defaults to a labware output for each labware source.
    If no labware sources are defined, this will be empty."""

    instrument_mappings: list[str] | None = None
    """Restrict task to run on an instrument from one of these mappings."""

    available_failure_actions: AvailableFailureActions = field(default_factory=AvailableFailureActions)
    """Available actions to be taken in case of failure."""

    skip: bool = False
    """Set to true to skip this task."""

    mock_behaviour: MockBehaviour | None = None
    """Overrides for the behaviour of the task on mock drivers"""

    inputs: Inputs = field(default_factory=Inputs)
    """Inputs to be passed to the task. The key is the name of the input.
    Can be a TaskOutputReference to the output of another task, a ReferenceData to some stored data, or a literal value."""

    static_arguments: dict[str, Any] | None = field(default=None)
    """Deprecated, use typed 'inputs' field instead"""

    shared_arguments: dict[str, str] | None = field(default=None)
    """Deprecated, use typed 'inputs' field instead"""

    def _get_time_estimate_input(self) -> int | ParameterReferenceInput:
        """Validates and converts time_estimate for API serialization."""
        if isinstance(self.time_estimate, int):
            return self.time_estimate
        if isinstance(self.time_estimate, ParameterReference):
            return ParameterReference.to_api_input(self.time_estimate)
        raise TypeError(f"time_estimate must be int or ParameterReference, got {type(self.time_estimate)}")

    def _generate_id(self) -> str:
        """Generate a unique id for the task in the form of {action}_{labware}_{instrument}_{short_uuid}"""
        if len(self.labware_sources) == 1:
            labware_slug = self.labware_sources[0].labware.id
        elif len(self.labware_sources) == 0:
            labware_slug = None
        else:
            labware_slug = f"{self.labware_sources[0].labware.id}_etc"

        return "-".join(
            [
                item
                for item in [self.action, labware_slug, self.instrument_type, str(uuid.uuid4())[:8]]
                if item is not None
            ]
        )

    def _generate_description(self) -> str:
        """Generate a description for the task, used if none is supplied directly."""
        labwares = ", ".join(source.labware.id for source in self.labware_sources)

        return " ".join([item for item in [self.action, labwares, "on", self.instrument_type] if item != ""])

    def __post_init__(self):
        BaseTask.__post_init__(self)
        if len(self.labware_outputs) == 0:
            # By default, mirror each labware source as a labware output
            for labware_source in self.labware_sources:
                if isinstance(labware_source, StoredLabware):
                    self.labware_outputs.append(
                        LabwareOutput(
                            labware=labware_source.labware,
                            slot=labware_source.slot,
                        )
                    )
                else:
                    if isinstance(labware_source.destination_slot, SlotFillingRule):
                        output_slot = OutputSlotFillingRule(behavior="match_input")
                    else:
                        output_slot = labware_source.destination_slot
                    self.labware_outputs.append(LabwareOutput(labware=labware_source.labware, slot=output_slot))
        if self.inputs and (self.static_arguments or self.shared_arguments):
            raise ValueError(
                "Cannot use 'inputs' and 'static_arguments'/'shared_arguments' together. Please use 'inputs' only, as 'static_arguments' and 'shared_arguments' are deprecated."
            )

    def to_api_input(self) -> workflow_api.ActionTaskInput:
        if self.inputs:
            # Get inputs from the 'inputs' field
            inputs = self.inputs.to_api_input()
        else:
            # Get inputs from the deprecated 'static_arguments' and 'shared_arguments' fields
            inputs = {}
            if self.static_arguments is not None:
                for key, value in self.static_arguments.items():
                    inputs[key] = workflow_api.StaticDataInput(value=value)
            if self.shared_arguments is not None:
                for key, value in self.shared_arguments.items():
                    inputs[key] = workflow_api.ReferenceDataInput(key=value)

        return workflow_api.ActionTaskInput(
            id=self.id,
            description=self.description,
            dependencies=_validate_and_extract_task_ids(self.dependencies, self.id),
            skip=self.skip,
            mock_behaviour=self.mock_behaviour.to_api_input() if self.mock_behaviour is not None else None,
            available_failure_actions=self.available_failure_actions.to_api_input(),
            instrument=workflow_api.TaskInstrumentInput(
                type=self.instrument_type,
                mappings=self.instrument_mappings,
            ),
            action=self.action,
            labware_sources={
                labware_source.labware.id: labware_source.to_api_input() for labware_source in self.labware_sources
            },
            labware_outputs={lo.labware.id: lo.to_api_input() for lo in self.labware_outputs},
            time_estimate=self._get_time_estimate_input(),
            arguments=None,  # deprecated field
            inputs=inputs,
        )

    @classmethod
    def from_api_output(
        cls,
        api_output: workflow_api.ActionTask,
        labware_sources: list[LabwareSource | StoredLabware],
        labware_outputs: list[LabwareOutput | StoredLabware],
        dependencies: list[Task],
        data_reference_outputs: dict[str, Task],  # Map of task id to task
    ) -> Self:
        return cls(
            id=api_output.id,
            description=api_output.description,
            action=api_output.action,
            labware_sources=labware_sources,
            labware_outputs=labware_outputs,
            time_estimate=(
                api_output.time_estimate
                if isinstance(api_output.time_estimate, int)
                else ParameterReference.from_api_output(api_output.time_estimate)
            ),
            instrument_type=api_output.instrument.type,
            instrument_mappings=None if len(api_output.instrument.mappings) == 0 else api_output.instrument.mappings,
            available_failure_actions=AvailableFailureActions.from_api_output(api_output.available_failure_actions),
            dependencies=dependencies,
            skip=api_output.skip,
            inputs=Inputs.from_api_output(api_output.inputs, data_reference_outputs),
            static_arguments=api_output.arguments.static if api_output.arguments is not None else None,
            shared_arguments=api_output.arguments.shared if api_output.arguments is not None else None,
            mock_behaviour=None
            if (
                api_output.mock_behaviour.execution_time is None
                and api_output.mock_behaviour.success == True
                and len(api_output.mock_behaviour.data_outputs) == 0
            )
            else MockBehaviour.from_api_output(api_output.mock_behaviour),
        )

    # TODO: Remove the output feature, it's not used?
    @overload
    def forward(
        self,
        *,
        output: int,
        destination_slot: int | SlotFillingRule = 1,
        units_consumed: int | None = None,
        dependencies: list[Task] | None = None,
    ) -> LabwareSource:
        ...  # pragma: no cover

    @overload
    def forward(
        self,
        *,
        labware: Labware | None = None,
        destination_slot: int | SlotFillingRule = 1,
        units_consumed: int | None = None,
        dependencies: list[Task] | None = None,
    ) -> LabwareSource:
        ...  # pragma: no cover

    def forward(
        self,
        *,
        output: int | None = None,
        labware: Labware | None = None,
        destination_slot: int | SlotFillingRule = 1,
        units_consumed: int | None = None,
        dependencies: list[Task] | None = None,
    ) -> LabwareSource:
        """Create a labware source from an output of a previous task.

        This can be used to forward previously used labware to another task without having to reference
        the source task multiple times."""

        labware_to_forward = None

        if output is not None and labware is None:
            if len(self.labware_outputs) < output - 1:
                raise IndexError(f"Tried to forward non-existent output {output} of task {self.id}")
            labware_output = self.labware_outputs[output]
            labware_to_forward = labware_output.labware
        elif output is None and labware is not None:
            for labware_output_candidate in self.labware_outputs:
                if labware_output_candidate.labware == labware:
                    labware_output = labware_output_candidate
                    break
            else:
                raise KeyError(f"No labware output of task {self.id} contains labware {labware.id}")

            labware_to_forward = labware
        else:
            raise ValueError("forward() expects exactly one of `output` or `forward` to be specified.")

        if isinstance(labware_output, StoredLabware):
            raise ValueError(
                f"Cannot forward output {output} of task {self.id} - "
                "stored labware cannot be used as an input for other tasks."
            )

        return LabwareSource(
            labware=labware_to_forward,
            destination_slot=destination_slot,
            source_task=self,
            units_consumed=units_consumed,
            dependencies=dependencies or [],
        )

    def out(self, output_name: str | None = None) -> TaskOutputReference:
        """Reference to the output of this task. If the task has only one output, output_name can be left as None."""
        return TaskOutputReference(task=self, output_name=output_name)


class LuaFunction(str):
    @property
    def function_name(self) -> str:
        function_pattern = r"^\n?\s*function\s*(\w*)\s*\("
        match = re.search(function_pattern, self)
        if match is None:
            return "lua_func"
        return match.group(1).strip()


class PythonReferenceFunction(str):
    @property
    def function_name(self) -> str:
        if self.endswith(".py"):
            return self[:-3]
        return self


CodeTaskFunction = LuaFunction | PythonReferenceFunction


@dataclass(kw_only=True, slots=True)
class Conditional(SDKEntity[workflow_api.ConditionalInput, workflow_api.Conditional]):
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_expected: bool
    comparison: Comparison | ElseComparison
    description: str = "Conditional"

    # Conditionals exist in a chain - e.g. If.ElseIf.ElseIf.Else
    # The chain is stored as a linked list going from If -> Else
    next: "Conditional | None" = None
    # Only used by SDK
    _prev: "Conditional | None" = None

    # As tasks get added to the conditional, we keep track of them here
    # This contains any nested tasks in the conditional (e.g. If(If().Else(If()))...), no matter how deep
    # It does _not_ include tasks in previous parts of the conditionals chain
    _tasks: dict[str, Task] = field(init=False, default_factory=dict)

    def Then(self, *dependents: "Task") -> Self:
        """Register tasks to run when this condition is met."""

        # Adds the condition on the task and remembers the task on the conditional.
        # Note that this does not add a task to the workflow automatically.
        for dependent in dependents:
            if isinstance(dependent, Conditional):
                # Must register the root of the conditional chain
                while dependent._prev is not None:
                    dependent = dependent._prev
            self._tasks[dependent.id] = dependent
        return self

    def to_api_input(self) -> workflow_api.ConditionalInput:
        return workflow_api.ConditionalInput(
            id=self.id,
            comparison=self.comparison.to_api_input() if isinstance(self.comparison, Comparison) else "Else",
            is_expected=self.is_expected,
            next=self.next.to_api_input() if self.next else None,
            tasks={task_id: task.to_api_input() for task_id, task in self._tasks.items()},
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.Conditional, tasks: dict[str, Task]) -> Self:
        return cls(
            id=api_output.id,
            is_expected=api_output.is_expected,
            comparison="Else"
            if api_output.comparison == "Else"
            else Comparison.from_api_output(api_output.comparison, tasks),
            next=cls.from_api_output(api_output.next, tasks) if api_output.next else None,
        )


@dataclass(kw_only=True, slots=True)
class If(Conditional):
    is_expected: bool = True

    def ElseIf(self, comparison: Comparison) -> "If":  # extremely dangerous
        # make id from "If" id
        root_id = self.id
        if "-elseif-" in root_id:
            root_id = root_id.split("-elseif-")[0]
        self.next = If(
            id=f"{root_id}-elseif-{str(uuid.uuid4())[:6]}",
            comparison=comparison,
            is_expected=False,
            _prev=self,
        )
        return self.next

    def Else(self, *dependents: "Task") -> Conditional:
        root_id = self.id
        if "-elseif-" in root_id:
            root_id = root_id.split("-elseif-")[0]
        self.next = Conditional(
            id=f"{root_id}-else",
            comparison="Else",
            is_expected=False,
            _prev=self,
        ).Then(*dependents)
        return self.next


@dataclass(kw_only=True, slots=True)
class CodeTask(SDKEntity[workflow_api.CodeTaskInput, workflow_api.CodeTask], BaseTask):
    function: CodeTaskFunction
    """The function to be executed."""

    inputs: Inputs = field(default_factory=Inputs)
    """The inputs to the function. The key is the name of the input.
    Can be a TaskOutputReference to the output of another task, a ReferenceData to some stored data, or a literal value."""

    mock_behaviour: MockBehaviour | None = None
    """Overrides for the behaviour of the task on mock drivers"""

    def _generate_id(self) -> str:
        """Generate a unique id for the task in the form of code_task_{short_uuid}"""
        return f"code_task_{str(uuid.uuid4())[:8]}"

    def _generate_description(self) -> str:
        """Generate a description for the task, used if none is supplied directly."""
        # Run <function_name> with inputs <inputs>

        def input_description(input_name: str, input_value: Any) -> str:
            if isinstance(input_value, TaskOutputReference):
                return f"{input_name}={input_value.output_name} from {input_value.task.id}"
            elif isinstance(input_value, ReferenceData):
                return f"{input_name}=reference data {input_value.key}"
            else:
                try:
                    input_value_str = str(input_value)
                    if len(input_value_str) > 20:
                        input_value_str = input_value_str[:20] + "..."
                except Exception:  # pragma: no cover
                    input_value_str = "..."
                return f"{input_name}={input_value_str}"

        inputs = (
            "["
            + ", ".join(input_description(input_name, input_value) for input_name, input_value in self.inputs.items())
            + "]"
        )

        return " ".join([item for item in ["Run", self.function.function_name, "with inputs", inputs] if item != ""])

    def to_api_input(self) -> workflow_api.CodeTaskInput:
        return workflow_api.CodeTaskInput(
            id=self.id,
            description=self.description,
            dependencies=_validate_and_extract_task_ids(self.dependencies, self.id),
            function=workflow_api.LuaFunctionInput(type="lua", value=self.function)
            if isinstance(self.function, LuaFunction)
            else workflow_api.PythonReferenceFunctionInput(type="python_reference", value=self.function),
            inputs=self.inputs.to_api_input(),
            mock_behaviour=self.mock_behaviour.to_api_input() if self.mock_behaviour else None,
        )

    @classmethod
    def from_api_output(
        cls,
        api_output: workflow_api.CodeTask,
        dependencies: list[Task],
        data_reference_tasks: dict[str, Task],  # Map of task id to task
    ) -> Self:
        return cls(
            id=api_output.id,
            description=api_output.description,
            dependencies=dependencies,
            function=LuaFunction(api_output.function.value)
            if api_output.function.type == "lua"
            else PythonReferenceFunction(api_output.function.value),
            inputs=Inputs.from_api_output(api_output.inputs, data_reference_tasks),
            mock_behaviour=None
            if (
                api_output.mock_behaviour.execution_time is None
                and api_output.mock_behaviour.success
                and not api_output.mock_behaviour.data_outputs
            )
            else MockBehaviour.from_api_output(api_output.mock_behaviour),
        )

    def out(self, output_name: str | None = None) -> TaskOutputReference:
        """Reference to the output of this task. If the task has only one output, output_name can be left as None."""
        return TaskOutputReference(task=self, output_name=output_name)


class DataConnectorType(str, Enum):
    SFTP = "sftp"


class SftpDataConnectorAction(str, Enum):
    IMPORT = "import"
    EXPORT = "export"

    @classmethod
    def from_api_output(cls, action_type: workflow_api.DataConnectorAction) -> "SftpDataConnectorAction":
        return cls(action_type)


@dataclass(kw_only=True, slots=True)
class SftpDataConnector(SDKEntity[workflow_api.DataConnectorInput, workflow_api.DataConnector], BaseTask):
    action: SftpDataConnectorAction
    file_path: str | TaskOutputReference
    input_task: TaskOutputReference
    mock_behaviour: MockBehaviour | None = None

    @property
    def _data_connector_type(self) -> DataConnectorType:
        return DataConnectorType.SFTP

    def _generate_id(self) -> str:
        return f"{self._data_connector_type.value}_data_connector{str(uuid.uuid4())[:8]}"

    def _generate_description(self) -> str:
        """Generate a description for the task, used if none is supplied directly."""

        def input_description(name: str, value: str | TaskOutputReference) -> str:
            if isinstance(value, TaskOutputReference):
                return f"{name}={value.output_name} from {value.task.id}"
            return f"{name}={value}"

        inputs = ", ".join(
            input_description(name, value)
            for name, value in {"file_path": self.file_path, "input_task": self.input_task}.items()
        )

        return f"Perform {self.action.value} using {self.id} with inputs [{inputs}]"

    def to_api_input(self) -> workflow_api.DataConnectorInput:
        return workflow_api.DataConnectorInput(
            id=self.id,
            description=self.description,
            dependencies=_validate_and_extract_task_ids(self.dependencies, self.id),
            data_connector_type=self._data_connector_type.value,
            action=self.action.value,
            inputs=Inputs(file_path=self.file_path, input_task=self.input_task).to_api_input(),
            mock_behaviour=self.mock_behaviour.to_api_input() if self.mock_behaviour else None,
        )

    @classmethod
    def from_api_output(
        cls,
        api_output: workflow_api.DataConnector,
        dependencies: list[Task],
        data_reference_tasks: dict[str, Task],
    ) -> Self:
        inputs = Inputs.from_api_output(api_output.inputs, data_reference_tasks)
        file_path = inputs.get("file_path")
        input_task = inputs.get("input_task")

        if not isinstance(file_path, (str, TaskOutputReference)):
            raise TypeError(f"file_path must be of type str or TaskOutputReference, got {type(file_path)}")

        if not isinstance(input_task, TaskOutputReference):
            raise TypeError(f"input_task must be of type TaskOutputReference, got {type(input_task)}")

        return cls(
            id=api_output.id,
            description=api_output.description,
            dependencies=dependencies,
            action=SftpDataConnectorAction.from_api_output(api_output.action),
            file_path=file_path,
            input_task=input_task,
            mock_behaviour=MockBehaviour.from_api_output(api_output.mock_behaviour)
            if api_output.mock_behaviour
            else None,
        )

    def out(self, output_name: str | None = None) -> TaskOutputReference:
        return TaskOutputReference(task=self, output_name=output_name)


@dataclass(kw_only=True, slots=True)
class OperatorTransport(ActionTask):
    """
    Task for transporting labware between ActionTasks using an operator.

    This class represents a transport action where an operator moves labware
    from one location to another. Only supports ActionTask as source and
    destination tasks to avoid complexity with placeholders.

    """

    action: str = field(default="operator", init=False)
    instrument_type: str = field(default="transport", init=False)
    labware: Labware
    source_task: "ActionTask"
    destination_task: "ActionTask | None" = None
    source_slot: int = 1
    destination_slot: int = 1

    def __post_init__(self):
        object.__setattr__(self, "instrument_type", "transport")
        object.__setattr__(self, "action", "operator")

        self.labware_sources = []
        self.labware_outputs = []

        BaseTask.__post_init__(self)

    @classmethod
    def from_api_output(
        cls,
        api_output: workflow_api.ActionTask,
        labware_sources: list[LabwareSource | StoredLabware],
        labware_outputs: list[LabwareOutput | StoredLabware],
        dependencies: list[Task],
        data_reference_outputs: dict[str, Task],
    ) -> Self:
        if not labware_sources:
            raise ValueError("OperatorTransport requires at least one labware source for reconstruction")

        labware_source = labware_sources[0]
        labware_output = labware_outputs[0]

        if isinstance(labware_source, LabwareSource):
            labware = labware_source.labware
            source_slot = labware_source.destination_slot if isinstance(labware_source.destination_slot, int) else 1

            if not isinstance(labware_source.source_task, ActionTask):
                raise ValueError(
                    f"OperatorTransport requires ActionTask as source_task, got {type(labware_source.source_task)}."
                )
            source_task = labware_source.source_task
        else:
            raise ValueError("OperatorTransport doesn't support StoredLabware as source")

        destination_slot = labware_output.slot if isinstance(labware_output.slot, int) else 1

        destination_task = None
        for task in data_reference_outputs.values():
            if isinstance(task, ActionTask) and task != source_task:
                destination_task = task
                break

        return cls(
            id=api_output.id,
            description=api_output.description,
            labware=labware,
            source_task=source_task,
            destination_task=destination_task,
            source_slot=source_slot,
            destination_slot=destination_slot,
            time_estimate=(
                api_output.time_estimate
                if isinstance(api_output.time_estimate, int)
                else ParameterReference.from_api_output(api_output.time_estimate)
            ),
            dependencies=dependencies,
        )


def _dependency_type_error(task_id: str, line_info: str, dep_type: str, index: int | None = None) -> TypeError:
    location = f"at index {index} " if index is not None else ""
    return TypeError(
        f"Task '{task_id}' has invalid dependency {location}{line_info}. "
        f"Expected Task object, but got {dep_type}. "
        f"Dependencies must be Task objects with 'id' attribute."
    )


def _validate_and_extract_task_ids(dependencies: Task | list[Task], task_id: str) -> list[str]:
    line_number = get_caller_line_number()
    line_info = f"(line {line_number})"

    def is_task_object(obj):
        return hasattr(obj, "id") and isinstance(obj, BaseTask)

    if not isinstance(dependencies, list):
        if is_task_object(dependencies):
            return [dependencies.id]
        else:
            raise _dependency_type_error(task_id, line_info, type(dependencies).__name__)

    task_ids = []
    for i, dep in enumerate(dependencies):
        if is_task_object(dep):
            task_ids.append(dep.id)
        else:
            raise _dependency_type_error(task_id, line_info, type(dep).__name__, i)
    return task_ids


def get_caller_line_number() -> int | None:
    frame = inspect.currentframe()
    line_number = None
    try:
        if frame and frame.f_back and frame.f_back.f_back:
            line_number = frame.f_back.f_back.f_lineno
    finally:
        del frame  # Avoid reference cycles
    return line_number
