from typing import cast

from .labware import Labware
from .schema import workflow_api
from .schema.workflow_api_types import APIData, APITask
from .task import (
    CodeTask,
    Conditional,
    ConditionalSourceTask,
    DataConnectorType,
    LabwareOutput,
    LabwareSource,
    OutputSlotFillingRule,
    SftpDataConnector,
    SlotFillingRule,
    StoredLabware,
    Task,
)
from .workflow import ActionTask


class TaskFactory:
    """A factory for creating tasks."""

    __slots__ = ("_raw_tasks", "_tasks", "_labware")

    _raw_tasks: dict[str, APITask]
    _tasks: dict[str, Task]
    _labware: dict[str, "Labware"]

    def __init__(
        self,
        raw_tasks: dict[str, APITask],
        all_labware: list[Labware],
    ):
        self._raw_tasks = self._get_all_nested_tasks(raw_tasks)
        self._labware = {labware.id: labware for labware in all_labware}

        # These attributes are used to cache the created tasks - we cannot use the cache decorator directly
        # because the API classes aren't necessarily hashable.
        self._tasks = {}

    @staticmethod
    def _get_all_nested_tasks(raw_tasks: dict[str, APITask]) -> dict[str, APITask]:
        """Get all raw tasks including nested tasks"""
        all_tasks = {}

        def get_nested_tasks(task: APITask) -> None:
            all_tasks[task.id] = task
            if isinstance(task, workflow_api.Conditional):
                for nested_task in task.tasks.values():
                    get_nested_tasks(nested_task)
                if task.next is not None:
                    get_nested_tasks(task.next)

        for task in raw_tasks.values():
            get_nested_tasks(task)

        return all_tasks

    def _get_labware(self, labware_id: str) -> Labware:
        try:
            return self._labware[labware_id]
        except KeyError:
            raise KeyError(f"TaskFactory has no labware with id {labware_id} - the workflow is invalid")

    def _get_raw_task(self, task_id: str) -> APITask:
        try:
            return self._raw_tasks[task_id]
        except KeyError:
            raise KeyError(f"TaskFactory has no task with id {task_id} - the workflow is invalid")

    def get_task(self, raw_task: APITask) -> Task:
        # We manually cache the created tasks - using a cache decorator isn't possible because
        # we have no control over the cacheability of the api types.
        if raw_task.id in self._tasks:
            return self._tasks[raw_task.id]

        if isinstance(raw_task, workflow_api.ActionTask):
            return self._get_action_task(raw_task)
        elif isinstance(raw_task, workflow_api.CodeTask):
            return self._get_code_task(raw_task)
        elif isinstance(raw_task, workflow_api.Conditional):
            return self._get_conditional(raw_task)
        elif isinstance(raw_task, workflow_api.DataConnector):
            return self._get_data_connector(raw_task)
        else:  # pragma: no cover
            raise NotImplementedError(f"Task type {type(raw_task)} is not supported")

    def _get_action_task(self, raw_task: workflow_api.ActionTask) -> ActionTask:
        action_task = ActionTask.from_api_output(
            raw_task,
            labware_sources=self._get_processed_labware_inputs(raw_task.labware_sources),
            labware_outputs=self._get_processed_labware_outputs(raw_task.labware_outputs),
            dependencies=[
                self.get_task(
                    self._get_raw_task(dependency_id),
                )
                for dependency_id in raw_task.dependencies
            ],
            data_reference_outputs=self.__get_data_reference_tasks(raw_task.inputs),
        )

        self._tasks[action_task.id] = action_task
        return action_task

    def _get_code_task(self, raw_task: workflow_api.CodeTask) -> CodeTask:
        code_task = CodeTask.from_api_output(
            raw_task,
            dependencies=[self.get_task(self._get_raw_task(dependency_id)) for dependency_id in raw_task.dependencies],
            data_reference_tasks=self.__get_data_reference_tasks(raw_task.inputs),
        )

        self._tasks[code_task.id] = code_task
        return code_task

    def _get_conditional(self, raw_task: workflow_api.Conditional) -> Conditional:
        for task_id in raw_task.tasks:
            self.get_task(self._get_raw_task(task_id))

        conditional = Conditional.from_api_output(
            raw_task,
            self._tasks,
        )
        self._tasks[conditional.id] = conditional
        # Add the nested tasks to the conditional
        raw_c = raw_task
        c = conditional
        while c.next is not None and raw_c.next is not None:
            raw_c = raw_c.next
            c = c.next
            c._tasks = {task: self.get_task(self._get_raw_task(task)) for task in raw_c.tasks}

        conditional._tasks = {task: self.get_task(self._get_raw_task(task)) for task in raw_task.tasks}

        return conditional

    def _get_data_connector(self, raw_task: workflow_api.DataConnector) -> Task:
        if raw_task.data_connector_type == DataConnectorType.SFTP:
            data_connector_task = SftpDataConnector.from_api_output(
                raw_task,
                dependencies=[
                    self.get_task(self._get_raw_task(dependency_id)) for dependency_id in raw_task.dependencies
                ],
                data_reference_tasks=self.__get_data_reference_tasks(raw_task.inputs),
            )
        else:
            raise NotImplementedError(f"Data connector type {raw_task.data_connector_type} is not supported")

        self._tasks[data_connector_task.id] = data_connector_task
        return data_connector_task

    def __get_data_reference_tasks(self, inputs: dict[str, APIData]) -> dict[str, Task]:
        raw_data_references = [arg for arg in inputs.values() if isinstance(arg, workflow_api.TaskOutputReference)]
        return {
            data_ref.task_id: self.get_task(self._get_raw_task(data_ref.task_id)) for data_ref in raw_data_references
        }

    def _get_processed_labware_inputs(
        self, labware_sources_dict: dict[str, workflow_api.LabwareSource | workflow_api.StoredLabware]
    ) -> list[LabwareSource | StoredLabware]:
        labware_sources = []
        for labware_source in labware_sources_dict.values():
            if isinstance(labware_source, workflow_api.LabwareSource):
                if labware_source.source_task is None:
                    source_task = None
                elif isinstance(labware_source.source_task, workflow_api.ConditionalSourceTask):
                    referenced_tasks = [
                        self.get_task(self._get_raw_task(tid)) for tid in labware_source.source_task.task_ids
                    ]
                    source_task = ConditionalSourceTask.from_api_output(
                        api_output=labware_source.source_task,
                        tasks=referenced_tasks,
                    )
                else:
                    task_id = cast(str, labware_source.source_task)
                    source_task = self.get_task(self._get_raw_task(task_id))
                    if not isinstance(source_task, ActionTask):
                        raise ValueError(
                            f"Labware {labware_source.labware_id} has a source task {labware_source.source_task} which is not an action task"
                        )
                destination_slot = (
                    SlotFillingRule.from_api_output(labware_source.destination_slot)
                    if isinstance(labware_source.destination_slot, workflow_api.SlotFillingRule)
                    else labware_source.destination_slot
                )
                labware_sources.append(
                    LabwareSource(
                        labware=self._get_labware(labware_source.labware_id),
                        destination_slot=destination_slot,
                        source_task=source_task,
                        dependencies=[self.get_task(self._get_raw_task(d)) for d in labware_source.dependencies],
                        units_consumed=labware_source.units_consumed,
                    )
                )
            elif isinstance(labware_source, workflow_api.StoredLabware):
                labware_sources.append(
                    StoredLabware(
                        labware=self._get_labware(labware_source.labware_id),
                        slot=labware_source.slot,
                    )
                )
        return labware_sources

    def _get_processed_labware_outputs(
        self, labware_outputs_dict: dict[str, workflow_api.LabwareOutput | workflow_api.StoredLabware]
    ) -> list[LabwareOutput | StoredLabware]:
        labware_outputs = []
        for labware_output in labware_outputs_dict.values():
            if labware_output.type == "labware_output":
                labware_outputs.append(
                    LabwareOutput(
                        labware=self._get_labware(labware_output.labware_id),
                        slot=(
                            OutputSlotFillingRule.from_api_output(labware_output.slot)
                            if isinstance(labware_output.slot, workflow_api.OutputSlotFillingRule)
                            else labware_output.slot
                        ),
                    )
                )
            elif labware_output.type == "stored_labware":
                labware_outputs.append(
                    StoredLabware(
                        labware=self._get_labware(labware_output.labware_id),
                        slot=labware_output.slot,
                    )
                )
        return labware_outputs
