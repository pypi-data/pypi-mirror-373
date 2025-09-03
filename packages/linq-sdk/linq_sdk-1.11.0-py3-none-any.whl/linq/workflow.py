import uuid
from dataclasses import dataclass, field
from enum import Enum
from logging import getLogger
from typing import (
    Any,
    Literal,
    Optional,
    Self,
    Sequence,
    cast,
)

from .hooks import (
    LabwareMovementHook,
    NewPlanHook,
    RunStateChangeHook,
    SafetyStateChangeHook,
    TaskStateChangeHook,
)
from .labware import Labware, LabwareType
from .parameters import IntegerParameterDefinition, ParameterDefinition, ParameterReference, ParameterValue
from .schema import workflow_api
from .sdk_entity import SDKEntity
from .task import (
    ActionTask,
    Comparison,
    If,
    Task,
    TaskLike,
)
from .task_factory import TaskFactory
from .workcell import Workcell

# These types are very simple wrappers around enums, there's not point in abstracting them away.
FailureResponse = workflow_api.FailureResponse

logger = getLogger(__name__)

SdkHookType = TaskStateChangeHook | RunStateChangeHook | LabwareMovementHook | NewPlanHook | SafetyStateChangeHook
WorkflowApiHookType = (
    workflow_api.TaskStateChangeHook
    | workflow_api.RunStateChangeHook
    | workflow_api.LabwareMovementHook
    | workflow_api.NewPlanHook
    | workflow_api.SafetyStateChangeHook
)


MATCH_WORKFLOW_API_TO_SDK_HOOK = {
    workflow_api.TaskStateChangeHook: TaskStateChangeHook,
    workflow_api.RunStateChangeHook: RunStateChangeHook,
    workflow_api.LabwareMovementHook: LabwareMovementHook,
    workflow_api.NewPlanHook: NewPlanHook,
    workflow_api.SafetyStateChangeHook: SafetyStateChangeHook,
}

WORKFLOW_TYPE = "sdk"


def get_sdk_hook_match(api_hook: WorkflowApiHookType | Any) -> SdkHookType | None:
    if isinstance(api_hook, WorkflowApiHookType):  # pragma: no cover
        return MATCH_WORKFLOW_API_TO_SDK_HOOK.get(type(api_hook))


class TimeConstraintType(str, Enum):
    START_TO_END = "start_to_end"
    START_TO_START = "start_to_start"
    END_TO_END = "end_to_end"
    END_TO_START = "end_to_start"
    CONSISTENCY = "consistency"


@dataclass(kw_only=True, slots=True)
class TimeConstraint(SDKEntity[workflow_api.TimeConstraintInput, workflow_api.TimeConstraint]):
    """A time constraint for a sequence of tasks."""

    id: str
    """Unique ID for this time constraint."""

    constraint_type: TimeConstraintType
    """Time constraint type."""

    start_task: ActionTask
    """First task in the sequence that the constraint applies to."""

    end_task: ActionTask
    """Last task in the sequence that the constraint applies to."""

    min_duration: int | None
    """Minimum duration allowed for the sequence."""

    max_duration: int | None
    """Maximum duration allowed for the sequence."""

    def to_api_input(self) -> workflow_api.TimeConstraintInput:
        return workflow_api.TimeConstraintInput(
            id=self.id,
            type=self.constraint_type.value,
            start_task_id=self.start_task.id,
            end_task_id=self.end_task.id,
            min_duration=self.min_duration,
            max_duration=self.max_duration,
        )

    @classmethod
    def from_api_output(
        cls,
        api_output: workflow_api.TimeConstraint,
        start_task: ActionTask,
        end_task: ActionTask,
    ) -> Self:
        return cls(
            id=api_output.id,
            constraint_type=TimeConstraintType(api_output.type),
            start_task=start_task,
            end_task=end_task,
            min_duration=api_output.min_duration,
            max_duration=api_output.max_duration,
        )


@dataclass(kw_only=True, slots=True)
class InstrumentBlock(SDKEntity[workflow_api.InstrumentBlockInput, workflow_api.InstrumentBlock]):
    """An instrument block instruction, keeping the instrument from being used between two tasks."""

    start_task: ActionTask

    end_task: ActionTask

    def to_api_input(self) -> workflow_api.InstrumentBlockInput:
        return workflow_api.InstrumentBlockInput(
            start_task_id=self.start_task.id,
            end_task_id=self.end_task.id,
        )

    @classmethod
    def from_api_output(
        cls,
        api_output: workflow_api.InstrumentBlock,
        start_task: ActionTask,
        end_task: ActionTask,
    ) -> Self:
        return cls(
            start_task=start_task,
            end_task=end_task,
        )


@dataclass(kw_only=True, slots=True)
class PlannerOptions(SDKEntity[workflow_api.PlannerOptionsInput, workflow_api.PlannerOptions]):
    """Planning-specific options, used to tweak how the planner behaves and what it optimises for."""

    target_objective: float | None = None
    """Target objective value."""

    max_computation_time: int | None = None
    """Max computation time allowed for the planner, in seconds.
    Starting point governed by option guaranteed_solution."""

    max_dead_time: int | None = None
    """Max dead time allowed between tasks with a transport between them"""

    round_robin_load_balancing: bool = False
    """Where there are equidistant instruments (instruments that take the same time to transport to),
    maestro uses round robin to assign instruments to those tasks."""

    preset: Literal["DRAFT", "TEST", "PROD_STANDARD", "PROD_LARGE"] | None = None
    """The plan CLI has a number of presets that can be used to quickly adjust the behaviour of the planner to suit different user needs. The available presets are:
    - DRAFT: To be used when it is not important if the plan is accurate or feasible. A plan generated with this preset does not guarantee that the workflow is actually possible to run in the real world
    - TEST: The planner will try to find a plan quickly, but it may not be optimal.
    - PROD_STANDARD: A preset with fairly standard settings. This is useful for making sure that the planner is using the recommended settings.
    - PROD_LARGE: A preset with settings that are more suitable for large workflows. This preset is useful when the workflow is large and the planner is taking a long time to find a plan.
    """

    optimisation_target: Literal[
        "minimize_total_plan_duration",
        "minimize_labware_idle_time",
        "balance_total_plan_duration_and_labware_idle_time",
    ] = "minimize_total_plan_duration"

    def to_api_input(self) -> workflow_api.PlannerOptionsInput:
        return workflow_api.PlannerOptionsInput(
            target_objective=self.target_objective,
            max_computation_time=self.max_computation_time,
            max_dead_time=self.max_dead_time,
            round_robin_load_balancing=self.round_robin_load_balancing,
            preset=self.preset,
            optimisation_target=self.optimisation_target,
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.PlannerOptions) -> Self:
        return cls(
            target_objective=api_output.target_objective,
            max_computation_time=api_output.max_computation_time,
            max_dead_time=api_output.max_dead_time,
            round_robin_load_balancing=api_output.round_robin_load_balancing,
            preset=api_output.preset,
        )


@dataclass(kw_only=True, slots=True)
class ExecutorOptions(SDKEntity[workflow_api.ExecutorOptionsInput, workflow_api.ExecutorOptions]):
    """Options for the execution of a workflow."""

    behaviour_on_failure: FailureResponse
    """Behaviour of the system when a task fails. Defaults to cancelling the workflow."""

    def to_api_input(self) -> workflow_api.ExecutorOptionsInput:
        return workflow_api.ExecutorOptionsInput(
            behaviour_on_failure=self.behaviour_on_failure,
            # TODO: Wack
            behaviour_on_planner_failure=None,
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.ExecutorOptions) -> Self:
        return cls(
            behaviour_on_failure=api_output.behaviour_on_failure,
        )


@dataclass(kw_only=True, slots=True)
class Options(SDKEntity[workflow_api.OptionsInput, workflow_api.Options]):
    """Planning and execution options for a workflow."""

    planner: PlannerOptions | None = None
    """Planning-specific options, used to tweak what the planner optimises for."""

    executor: ExecutorOptions | None = None
    """Execution-specific options."""

    is_explicit: bool = False
    """Set this to true to prevent the API from adding any implicit logic, like opening doors,
loading/unloading instruments, etc."""

    def to_api_input(self) -> workflow_api.OptionsInput:
        return workflow_api.OptionsInput(
            planner=self.planner.to_api_input() if self.planner is not None else None,
            executor=(self.executor.to_api_input() if self.executor is not None else None),
            is_explicit=self.is_explicit,
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.Options) -> Self:
        return cls(
            planner=PlannerOptions.from_api_output(api_output.planner),
            executor=ExecutorOptions.from_api_output(api_output.executor),
        )


@dataclass(kw_only=True, slots=True)
class RunInstruction(SDKEntity[workflow_api.RunInstructionInput, workflow_api.RunInstruction]):
    """Instructions for running a workflow."""

    description: str
    phase: Literal["pre", "mid", "post"]

    def to_api_input(self) -> workflow_api.RunInstructionInput:
        return workflow_api.RunInstructionInput(
            description=self.description,
            phase=self.phase,
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.RunInstruction) -> Self:
        return cls(description=api_output.description, phase=api_output.phase)


class DuplicateTaskIdError(Exception):
    pass


@dataclass(kw_only=True, slots=True)
class Workflow(SDKEntity[workflow_api.WorkflowConfigInput, workflow_api.WorkflowConfig]):
    """Describes a workflow. This is the main entrypoint into the SDK, most CLI actions require a workflow to work."""

    workcell: Workcell
    """The workcell this workflow will be run in."""

    name: str
    """Workflow name."""

    author: str
    """Workflow author."""

    description: str
    """Workflow description."""

    workflow_type: workflow_api.WorkflowType = WORKFLOW_TYPE
    """Workflow type."""

    version: str
    """Workflow version. This is arbitrary for now."""

    scheduler_version: str
    """Version of the scheduler to use. Use `get_latest_scheduler_version` to get the latest supported version."""

    labware_types: list[LabwareType]
    """List of all types of labware used in the workflow."""

    labware: list[Labware]
    """List of all labware used in the workflow."""

    tasks: Sequence[Task] = field(default_factory=list)
    """The workflow tasks."""

    time_constraints: list[TimeConstraint] = field(default_factory=list)
    """List of time constraints the workflow has to fulfill."""

    instrument_blocks: list[InstrumentBlock] = field(default_factory=list)
    """List of instrument blocks the workflow has to fulfill."""

    options: Options = field(default_factory=Options)
    """Planning and execution options."""

    run_instructions: list[RunInstruction] = field(default_factory=list)
    """Instructions for running the workflow."""

    published: bool = False
    """Whether the workflow is published on the LINQ platform or not"""

    hooks: Sequence[
        TaskStateChangeHook | RunStateChangeHook | LabwareMovementHook | SafetyStateChangeHook | NewPlanHook
    ] = field(default_factory=list)
    """Hooks to be triggered when a run state or task state changes."""

    python_scripts_version: str | None = field(default=None)
    """Version of the Python scripts repository managed by the organization. Leaving as `None` will pull the latest version if available."""

    parameter_definitions: list[ParameterDefinition] = field(default_factory=list)

    batches: int | ParameterReference = field(default=1)
    """Number of batches of the workflow to run. Default value 1 means no batching."""

    drivers_version: str | None = field(default=None)
    """Version of the drivers repository managed by the organization. Leaving as `None` will pull the latest version if available."""

    evals_version: str | None = field(default=None)
    """Version of the evals repository managed by the organization. Leaving as `None` will pull the latest version if available."""

    # Private attributes
    __task_ids: list[str] = field(default_factory=list, init=False, repr=False, compare=False)

    def __post_init__(self):
        self._ensure_batches_parameter()

    @property
    def task_ids(self) -> list[str]:
        if len(self.__task_ids) != len(self.tasks):
            self.__task_ids = [task.id for task in self.tasks]
        return self.__task_ids

    def add_task(self, task: TaskLike) -> TaskLike:
        """
        Add a task to the workflow.
        """
        if task.id in self.task_ids:
            raise DuplicateTaskIdError(f"Task with id '{task.id}' already exists in the workflow")

        # Note - task may already exist in nested conditional. Not checked in SDK.

        if not isinstance(self.tasks, list):  # pragma: no cover
            # NOTE: Workaround to allow covariance in the tasks attribute
            self.tasks = list(self.tasks)
        self.tasks.append(task)
        return task

    def _ensure_batches_parameter(self):
        if isinstance(self.batches, ParameterReference):
            batches_parameter_definition = next(
                iter(pd for pd in self.parameter_definitions if pd.id == self.batches.parameter_id), None
            )
            if batches_parameter_definition is None:
                self.parameter_definitions.append(
                    IntegerParameterDefinition(
                        id=self.batches.parameter_id,
                        name="Number of Batches",
                        default=None,
                        minimum=1,
                        always_required=True,
                    )
                )
            else:
                if not isinstance(batches_parameter_definition, IntegerParameterDefinition):
                    raise TypeError(
                        f"Parameter Definition used for batches '{self.batches.parameter_id}' must be an IntegerParameterDefinition, got {batches_parameter_definition.__class__.__name__}"
                    )

    def to_api_input(self) -> workflow_api.WorkflowConfigInput:
        return workflow_api.WorkflowConfigInput(
            name=self.name,
            metadata=workflow_api.WorkflowMetadataInput(
                author=self.author,
                description=self.description,
                version=self.version,
                workflow_type=self.workflow_type,
            ),
            workflow=workflow_api.WorkflowInput(
                labware_types=[labware_type.to_api_input() for labware_type in self.labware_types],
                labware=[labware.to_api_input() for labware in self.labware],
                tasks={task.id: task.to_api_input() for task in self.tasks},
                time_constraints=[time_constraint.to_api_input() for time_constraint in self.time_constraints],
                instrument_blocks=[instrument_block.to_api_input() for instrument_block in self.instrument_blocks],
                hooks=[hook.to_api_input() for hook in self.hooks],
                batches=self.batches if isinstance(self.batches, int) else self.batches.to_api_input(),
            ),
            workcell=self.workcell.to_api_input(),
            options=self.options.to_api_input(),
            run_instructions=[run_instruction.to_api_input() for run_instruction in self.run_instructions],
            scheduler_config=workflow_api.SchedulerConfigInput(
                scheduler="maestro",
                version=self.scheduler_version,
                python_scripts_version=self.python_scripts_version,
            ),
            parameter_definitions=[param.to_api_input() for param in self.parameter_definitions],
            drivers_version=self.drivers_version,
            evals_version=self.evals_version,
        )

    def to_api_input_with_parameter_values(
        self, parameter_values: list[ParameterValue]
    ) -> workflow_api.WorkflowConfigInputWithParameters:
        workflow_config_input = self.to_api_input()
        workflow_config_input_with_parameters = workflow_api.WorkflowConfigInputWithParameters(
            **workflow_config_input.model_dump(),
            parameter_values=parameter_values,
        )
        return workflow_config_input_with_parameters

    @classmethod
    def from_api_output(cls, api_output: workflow_api.WorkflowConfig) -> Self:
        workcell = Workcell.from_api_output(api_output.workcell)
        labware_types = {lt.id: LabwareType.from_api_output(lt) for lt in api_output.workflow.labware_types}
        all_labware = [
            Labware.from_api_output(
                labware,
                labware_type=labware_types[labware.type],
                instruments={instrument.id: instrument for instrument in api_output.workcell.instruments},
            )
            for labware in api_output.workflow.labware
        ]
        task_factory = TaskFactory(raw_tasks=api_output.workflow.tasks, all_labware=all_labware)
        hooks: list[SdkHookType] = []

        if api_output.workflow.hooks:
            for api_hook in api_output.workflow.hooks:
                sdk_hook = get_sdk_hook_match(api_hook)

                if sdk_hook:  # pragma: no cover
                    hooks.append(getattr(sdk_hook, "from_api_output")(api_hook))

        time_constraints = []
        for tc in api_output.workflow.time_constraints:
            start_task = cast(ActionTask, task_factory.get_task(api_output.workflow.tasks[tc.start_task_id]))
            end_task = cast(ActionTask, task_factory.get_task(api_output.workflow.tasks[tc.end_task_id]))
            time_constraints.append(TimeConstraint.from_api_output(tc, start_task, end_task))

        instrument_blocks = [
            InstrumentBlock.from_api_output(
                instrument_block,
                start_task=cast(
                    ActionTask,
                    task_factory.get_task(api_output.workflow.tasks[instrument_block.start_task_id]),
                ),
                end_task=cast(
                    ActionTask,
                    task_factory.get_task(api_output.workflow.tasks[instrument_block.end_task_id]),
                ),
            )
            for instrument_block in api_output.workflow.instrument_blocks
        ]

        return cls(
            workcell=workcell,
            name=api_output.name,
            author=api_output.metadata.author,
            description=api_output.metadata.description,
            version=str(api_output.metadata.version),
            scheduler_version=api_output.scheduler_config.version,
            labware_types=list(labware_types.values()),
            labware=list(all_labware),
            tasks=[task_factory.get_task(raw_task) for raw_task in api_output.workflow.tasks.values()],
            time_constraints=time_constraints,
            run_instructions=[
                RunInstruction.from_api_output(run_instruction) for run_instruction in api_output.run_instructions
            ],
            instrument_blocks=instrument_blocks,
            published=api_output.published,
            hooks=hooks,
            drivers_version=api_output.drivers_version,
            evals_version=api_output.evals_version,
        )

    def If(self, comparison: Comparison, id: Optional[str] = None) -> "If":
        conditional = If(id=id or str(uuid.uuid4()), comparison=comparison, is_expected=True)
        # Nested IF statements will be added as subtasks in their parent container.
        # self.add_task needs to ensure no duplication by checking first.
        self.add_task(conditional)
        return conditional
