import datetime
import uuid
from dataclasses import dataclass
from datetime import timezone
from typing import Dict, Literal, Optional
from uuid import UUID

import requests
from packaging.version import Version
from pydantic import BaseModel
from requests.exceptions import ConnectionError

from . import __version__
from .auth.server import AuthErrorMessage
from .config import Config
from .credentials import Credentials
from .exceptions import APIError, AuthError, DuplicateWorkflowName, HubRestartCommandResponseNotFound
from .parameters import ParameterValue
from .schema import auth_api, backend_api, workflow_api
from .workflow import WORKFLOW_TYPE, Workflow

REASON_NOT_REQUIRED = "[CODE_REASON_NOT_REQUIRED]"


class WorkflowAPIErrorResponse(BaseModel):
    detail: str = "An unexpected error occurred"

    def __str__(self) -> str:
        return self.detail


class LinqBackendErrorResponse(BaseModel):
    message: str = "An unexpected error occurred"

    def __str__(self) -> str:
        return self.message


@dataclass(kw_only=True, slots=True)
class Linq:
    """The Automata LINQ API client.

    Use this object to validate, plan and otherwise interact with workflows.
    """

    @property
    def config(self) -> Config:
        config = Config.load()
        if not config.is_configured():
            raise AuthError(
                message=AuthErrorMessage(
                    error="configuration_error",
                    description=(
                        "Validation error: Configuration is not set. Please run 'linq auth configure' command."
                    ),
                )
            )
        return config

    @property
    def credentials(self) -> Credentials:
        credentials = Credentials.load()
        if not credentials.is_configured():
            raise AuthError(
                message=AuthErrorMessage(
                    error="credentials_error",
                    description=(
                        "Validation error: Credentials are not set. Please login by running 'linq auth login' command."
                    ),
                )
            )

        if credentials.is_expired():
            raise AuthError(
                message=AuthErrorMessage(
                    error="credentials_expired",
                    description=(
                        "Validation error: Token has expired. Please login again by running 'linq auth login' command."
                    ),
                )
            )

        return credentials

    @property
    def _api_url(self) -> str:
        """Return the full api_url built from the configured domain.

        If the domain starts with http (mostly for local testing),
        it's returned directly, otherwise https:// is added.
        """
        if self.config.domain.startswith(("http://", "https://")):
            return self.config.domain
        if self.config.domain.split(":", 1)[0] in ["localhost", "127.0.0.1", "host.docker.internal"]:
            return f"http://{self.config.domain}"
        return f"https://{self.config.domain}"

    def _temp_replace_domain(self, route: str) -> str:
        """This is a temporary hack fix to enable keeping a single domain variable while the domains have been split for the linq api and the linq backend."""
        api_url = self._api_url
        if route.startswith("v3"):
            return f"{api_url.replace('api.', 'sdk.', 1)}/{route}"
        if route.startswith("v1"):
            return f"{api_url.replace('sdk.', 'api.', 1)}/{route}"

        return f"{api_url}/{route}"

    def _make_request(
        self,
        method: Literal["get", "post", "put", "delete"],
        endpoint: str,
        data: dict[str, object] | None = None,
        parameters: dict[str, str | int | bool] | None = None,
    ) -> requests.Response:
        """Low-level helper for making consistent requests to the API."""
        data = data or {}
        parameters = parameters or {}

        url = self._temp_replace_domain(endpoint)

        headers = {
            "Authorization": f"Bearer {self.credentials.access_token}",
            "Content-Type": "application/json",
            "Automata-Sdk-Version": f"{__version__}",
        }

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=parameters,
            )
        except ConnectionError:
            raise APIError("Cannot reach API - please ensure the SDK is configured with the correct domain.")

        if response.status_code in [200, 201, 204, 422, 400, 404, 409]:
            return response

        raise APIError(
            f"Unexpected response from API with status {response.status_code}. Response was '{response.text}'",
        )

    def get_api_version(self) -> str:
        """
        Get Workflow Builder API version or unknown if it's not possible to retrieve version.

        :return: API version.
        """
        try:
            response = self._make_request("get", "version")
            version = response.json().get("version", "unknown")
        except Exception:
            return "unknown"

        return version

    def get_organizations(self) -> list[backend_api.Organization]:
        """Get the list of organizations the user is a member of.

        :return: the list of organizations
        :raises APIError: if the request fails
        """
        response = self._make_request("get", "v2/user/organizations")

        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to get list of organizations: {error_response.detail}")

        return [backend_api.Organization.model_validate(org) for org in response.json().get("organizations")]

    def create_workflow(self, workflow: Workflow) -> workflow_api.WorkflowInfo:
        """Create a new workflow.

        :param workflow: the workflow definition
        :return: the workflow information
        :raises APIError: if creating the workflow fails
        """
        response = self._make_request(
            "post",
            "v3/workflow",
            data=workflow.to_api_input().model_dump(exclude_none=True, mode="json"),
        )
        if response.status_code != 201:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to create workflow '{workflow.name}': {error_response.detail}")

        return workflow_api.WorkflowInfo.model_validate(response.json())

    def get_workflows(
        self,
        page: int = 1,
        page_size: int = 100,
    ) -> list[workflow_api.WorkflowInfo]:
        """
        Get a list of workflows.

        :param page: The page number to retrieve.
        :param page_size: The number of items per page.
        :return: a list of all workflow information
        :raises APIError: if the request fails
        """
        response = self._make_request(
            method="get",
            endpoint="v3/workflow",
            parameters={
                "workflow_type": WORKFLOW_TYPE,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to get list of workflows: {error_response.detail}")

        return [workflow_api.WorkflowInfo.model_validate(workflow) for workflow in response.json()]

    def update_workflow(self, workflow_id: uuid.UUID, workflow: Workflow) -> workflow_api.WorkflowInfo:
        """Update an existing workflow.

        :param workflow_id: the workflow ID to update
        :param workflow: the workflow definition to update to
        :return: the updated workflow information
        :raises APIError: if updating the workflow fails
        """
        response = self._make_request(
            "put",
            f"v3/workflow/{workflow_id}",
            data=workflow.to_api_input().model_dump(exclude_none=True, mode="json"),
        )
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to get update workflow '{workflow_id}': {error_response.detail}")

        return workflow_api.WorkflowInfo.model_validate(response.json())

    def delete_workflow(self, workflow_id: uuid.UUID) -> None:
        """Delete a workflow.

        :param workflow_id: the workflow ID
        :return: None
        :raises APIError: if deleting the workflow fails
        """
        response = self._make_request(
            "delete",
            f"v3/workflow/{workflow_id}",
        )
        if response.status_code != 204:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to delete workflow '{workflow_id}': {error_response.detail}")

    def validate_workflow(
        self,
        workflow: Workflow,
        validate_for_execution: bool = False,
        validate_for_infeasibility: bool = False,
        parameter_values: list[ParameterValue] = [],
    ) -> workflow_api.WorkflowValidationResult:
        """Validate a workflow by submitting it to the API.

        :param workflow: the workflow to be validated
        :param validate_for_execution:
            set to True for deeper validation of actions/configuration
            set to False (default) to ignore hardware/driver-specific issues early during workflow development
        :return: the validation result for the workflow
        :raises APIError: if the validation request fails
        """
        response = self._make_request(
            "post",
            "v3/workflow/validate",
            data=workflow.to_api_input_with_parameter_values(parameter_values).model_dump(
                exclude_none=True, mode="json"
            ),
            parameters={
                "validate_for_execution": validate_for_execution,
                "validate_for_infeasibility": validate_for_infeasibility,
            },
        )
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to validate workflow '{workflow.name}': {error_response.detail}")

        return workflow_api.WorkflowValidationResult.model_validate(response.json())

    def plan_workflow(
        self,
        workflow_id: UUID | str,
        parameter_values: list[ParameterValue] = [],
    ) -> workflow_api.WorkflowPlanStatus:
        """Plan a workflow by submitting it to the API.

        :param workflow_id: the ID of the workflow to be planned
        :param parameter_values: the parameter values to use for planning - essential if batching with a parameter
        :return: the plan status for the workflow
        :raises APIError: if the planning request fails
        """
        response = self._make_request(
            method="post",
            endpoint=f"v3/workflow/plan?workflow_id={workflow_id}",
            data={"parameter_values": [pv.model_dump(exclude_none=True, mode="json") for pv in parameter_values]},
        )
        if response.status_code not in [200, 201]:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to plan workflow '{workflow_id}': {error_response.detail}")

        return workflow_api.WorkflowPlanStatus.model_validate(response.json())

    def get_plan_status(self, workflow_id: UUID | str, plan_id: UUID | str) -> workflow_api.WorkflowPlanStatus:
        """Get the status of a planned workflow execution.

        :param workflow_id: the ID of the workflow
        :param plan_id: the ID of the plan
        :return: the status of the plan for a workflow
        :raises APIError: if the plan status request fails
        """
        response = self._make_request(
            "get",
            f"v3/workflow/{workflow_id}/plan/{plan_id}/status",
        )
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to fetch plan status '{workflow_id}': {error_response.detail}")

        return workflow_api.WorkflowPlanStatus.model_validate(response.json())

    def get_plan_result(self, workflow_id: UUID | str, plan_id: UUID | str) -> workflow_api.WorkflowPlanResult:
        """Get the result of a planned workflow execution.

        :param workflow_id: the ID of the workflow
        :param plan_id: the ID of the plan
        :return: the result of the plan for a workflow
        :raises APIError: if the plan result request fails
        """
        response = self._make_request(
            "get",
            f"v3/workflow/{workflow_id}/plan/{plan_id}/result",
        )
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to get plan result: {error_response.detail}")

        return workflow_api.WorkflowPlanResult.model_validate(response.json())

    def list_plans_for_workflow(self, workflow_id: uuid.UUID) -> list[workflow_api.WorkflowPlanStatus]:
        """List existing plans for a workflow.

        :param workflow_id: the ID of the workflow to list plans for
        :return: a list of plan statuses for the workflow
        :raises APIError: if the request fails
        """
        response = self._make_request(
            "get",
            f"v3/workflow/{workflow_id}/plan",
        )
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to list plans for workflow '{workflow_id}': {error_response.detail}")

        return [workflow_api.WorkflowPlanStatus.model_validate(plan) for plan in response.json()]

    def get_supported_scheduler_versions(self) -> dict[str, list[str]]:
        """Returns all supported scheduler versions as a dict of versions per scheduler.
        The versions are sorted with the latest version first.

        {<scheduler>: [latest_version, previous_version,..., oldest_version]}
        :return: a dict of supported schedulers and their versions
        :raises APIError: if the request fails
        """
        supported_versions: dict[str, list[str]] = self._make_request(
            method="get",
            endpoint="v3/workflow/scheduler_versions",
        ).json()

        for scheduler, versions in supported_versions.items():
            if len(versions) > 1:
                # Sort versions by semver
                supported_versions[scheduler] = sorted(versions, key=Version, reverse=True)
        return supported_versions

    def get_workflow(self, id: uuid.UUID) -> workflow_api.WorkflowConfig:
        """Get a workflow by ID.

        :param id: the ID of the workflow
        :return: the workflow
        :raises APIError: if the get workflow request fails
        """
        response = self._make_request(method="get", endpoint=f"v3/workflow/{id}")
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to get workflow: {error_response.detail}")
        return workflow_api.WorkflowConfig.model_validate(response.json())

    def get_sdk_workflow(self, id: uuid.UUID) -> Workflow:
        """Get a workflow by ID, as an SDK Workflow object.

        :param id: the ID of the workflow
        :return: the workflow
        :raises APIError: if the get workflow request fails
        """
        raw_workflow = self.get_workflow(id)
        # TODO: Move this out of the client, since client should only deal in workflow_api types
        return Workflow.from_api_output(raw_workflow)

    def get_all_drivers(self, scheduler: str, version: str) -> list[workflow_api.Driver]:
        """Get all drivers for a given scheduler and version.

        :param scheduler: the scheduler name
        :param version: the scheduler version
        :return: a list of all the drivers for the given scheduler and version
        :raises APIError: if the request fails
        """
        response = self._make_request("get", f"v3/driver/{scheduler}/{version}")
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to get drivers: {error_response.detail}")

        return [workflow_api.Driver.model_validate(raw_driver) for raw_driver in response.json()]

    def get_workcells(
        self,
        workspace_id: UUID,
    ) -> list[backend_api.Workcell]:
        """Get a list of workcells.

        :return: a list of all workcells
        :raises APIError: if the request fails
        """
        response = self._make_request(
            "get",
            f"v1/workspace/{workspace_id}/workcells",
        )
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to get list of workcells: {error_response.detail}")

        return [backend_api.Workcell.model_validate(device) for device in response.json().get("workcells")]

    def deploy_workflow(
        self,
        *,
        workflow_id: UUID,
        device_id: UUID,
        reason: str = REASON_NOT_REQUIRED,
    ) -> None:
        """Deploy workflow with a given ID to a hub.

        :param workflow_id: the ID of the workflow to deploy
        :param device_id: the ID of the hub related to the workcell to deploy the workflow to
        :param reason: the reason for deploying the workflow (optional)
        :return: None
        :raises APIError: if the deployment fails
        """

        response = self._make_request(
            method="post",
            endpoint=f"v3/workflow/{workflow_id}/deploy",
            data={
                "device_id": str(device_id),
                "reason": reason,
            },
        )

        if response.status_code != 204:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to deploy workflow: {error_response.detail}")

    def get_status(
        self,
        *,
        device_id: UUID | str,
    ) -> backend_api.DeviceState:
        """Get the status of the given hub.

        :param device_id: the ID of the hub related to the workcell to get the status of
        :return: the status of the workcell
        :raises APIError: if the status request fails
        """
        response = self._make_request(
            method="get",
            endpoint=f"v1/devices/{device_id}",
        )
        if response.status_code != 200:
            error_response = LinqBackendErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to get device status: {error_response}")
        device_state = backend_api.Device.model_validate(response.json())
        return device_state.state

    def get_latest_error(
        self,
        *,
        device_id_or_serial: UUID | str,
    ) -> backend_api.DeviceError | None:
        """Get the latest error of a given hub.

        :param device_id_or_serial: the ID or serial of the hub related to the workcell to get the error of
        :return: the error status of the workcell
        :raises APIError: if the error request fails
        """
        response = self._make_request(
            method="get",
            endpoint=f"v1/devices/{device_id_or_serial}",
        )
        if response.status_code != 200:
            error_response = LinqBackendErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to get device error: {error_response}")

        device_data = backend_api.DeviceData.model_validate(response.json())

        device = backend_api.Device(**device_data.model_dump())
        device.error = self._latest_error_from_device_data(device_data)

        if device.error is not None:
            # NOTE: Abort is always available, but not returned from the API
            device.error.available_actions.append(backend_api.DeviceErrorAvailableActions.Abort)
        return device.error

    @staticmethod
    def _latest_error_from_device_data(device_data: backend_api.DeviceData) -> backend_api.DeviceError | None:
        """Return the DeviceError with the most recent timestamp from a list of DeviceErrors"""
        if device_data.errors:
            return max(device_data.errors, key=lambda e: e.timestamp)

        return None

    def respond_to_error(
        self,
        *,
        device_id: UUID,
        error_id: UUID,
        action: backend_api.DeviceErrorAvailableActions,
    ) -> None:
        """Respond to an error on the given hub.

        :param device_id: the ID of the hub related to the workcell to respond to the error on
        :param error_id: the ID of the error to respond to
        :param action: the action to take in response to the error
        :return: None
        :raises APIError: if the error response fails
        """
        if action is backend_api.DeviceErrorAvailableActions.Abort:
            workcell_status = self.get_status(device_id=str(device_id))
            if workcell_status.status == backend_api.DeviceStateStatus.RUNNING:
                # If there is an error during driver creation the system will be in RUNNING state so we need to stop not
                # reset. This logic is replicated on the frontend.
                self.stop_workflow(device_id=device_id, reason=f"Aborting workflow in response to error {error_id}")
                return
            self.reset_workflow(device_id=device_id, reason=f"Aborting workflow in response to error {error_id}")
            return
        response = self._make_request(
            method="post",
            endpoint=f"v1/devices/{device_id}/errors/{error_id}/action",
            data={"action": action},
        )
        if response.status_code != 204:
            error_message = LinqBackendErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to action error with {action}: {error_message}")

    def start_workflow(
        self,
        *,
        device_id: UUID,
        # FIXME: Remove this optional parameter, frontend no longer has this popup
        times_to_run: int = 1,
        reason: str = REASON_NOT_REQUIRED,
    ) -> None:
        """Start the workflow currently deployed to the given hub.

        :param device_id: the ID of the hub related to the workcell to start the workflow on
        :param times_to_run: the number of times the workflow should run (default 1)
        :param reason: the reason for starting the workflow (optional)
        :return: None
        :raises APIError: if the start request fails
        """
        response = self._make_request(
            method="post",
            endpoint=f"v1/devices/{device_id}/state/start",
            data={
                "payload": {"times_to_run": times_to_run},
                "reason": {"details": reason},
            },
        )
        if response.status_code != 204:
            error_message = LinqBackendErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to start workflow: {error_message}")

    def pause_workflow(
        self,
        *,
        device_id: UUID,
        reason: str = REASON_NOT_REQUIRED,
    ) -> None:
        """Pause the workflow currently running on the given hub.

        :param device_id: the ID of the hub related to the workcell to pause the workflow on
        :param reason: the reason for pausing the workflow (optional)
        :return: None
        :raises APIError: if the pause request fails
        """
        response = self._make_request(
            method="post",
            endpoint=f"v1/devices/{device_id}/state/pause",
            data={
                "reason": {"details": reason},
            },
        )
        if response.status_code != 204:
            error_message = LinqBackendErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to pause workflow: {error_message}")

    def resume_workflow(
        self,
        *,
        device_id: UUID,
        reason: str = REASON_NOT_REQUIRED,
    ) -> None:
        """Resume the workflow currently paused on the given hub.

        :param device_id: the ID of the hub related to the workcell to resume the workflow on
        :param reason: the reason for resuming the workflow (optional)
        :return: None
        :raises APIError: if the resume request fails
        """
        response = self._make_request(
            method="post",
            endpoint=f"v1/devices/{device_id}/state/resume",
            data={
                "reason": {"details": reason},
            },
        )
        if response.status_code != 204:
            error_message = LinqBackendErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to resume workflow: {error_message}")

    def stop_workflow(
        self,
        *,
        device_id: UUID,
        reason: str = REASON_NOT_REQUIRED,
    ) -> None:
        """Stop the workflow currently deployed to the given hub.

        :param device_id: the ID of the hub related to the workcell to stop the workflow on
        :param reason: the reason for stopping the workflow (optional)
        :return: None
        :raises APIError: if the stop request fails
        """
        response = self._make_request(
            method="post",
            endpoint=f"v1/devices/{device_id}/state/stop",
            data={
                "reason": {"details": reason},
            },
        )
        if response.status_code != 204:
            error_message = LinqBackendErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to stop workflow: {error_message}")

    def reset_workflow(
        self,
        *,
        device_id: UUID,
        reason: str = REASON_NOT_REQUIRED,
    ) -> None:
        """Reset the workflow currently deployed to the given hub.

        :param device_id: the ID of the hub related to the workcell to reset the workflow on
        :param reason: the reason for resetting the workflow (optional)
        :return: None
        :raises APIError: if the reset request fails
        """
        response = self._make_request(
            method="post",
            endpoint=f"v1/devices/{device_id}/state/reset",
            data={
                "reason": {"details": reason},
            },
        )
        if response.status_code != 204:
            error_message = LinqBackendErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to reset workflow: {error_message}")

    def publish_workflow(
        self,
        *,
        workflow_id: UUID,
        plan_id_to_include: UUID | None = None,
        simulate_drivers: bool = False,
        simulate_time: bool = False,
        reason: str = REASON_NOT_REQUIRED,
        parameter_values: list[ParameterValue] = [],
        overwrite_on_conflict: bool = False,
    ) -> workflow_api.PublishedWorkflow:
        """Publish the workflow currently deployed to the given device (workcell)."""
        parameters = {
            "simulate_drivers": simulate_drivers,
            "simulate_time": simulate_time,
            "reason": reason,
            "overwrite_on_conflict": overwrite_on_conflict,
        }

        if plan_id_to_include is not None:
            parameters["plan_id_to_include"] = str(plan_id_to_include)

        response = self._make_request(
            method="post",
            endpoint=f"v3/workflow/{workflow_id}/publish",
            parameters=parameters,
            data={"parameter_values": [pv.model_dump(exclude_none=True, mode="json") for pv in parameter_values]},
        )
        if response.status_code == 409:
            error_message = WorkflowAPIErrorResponse.model_validate(response.json())
            raise DuplicateWorkflowName(f"Failed to publish workflow: {error_message}")
        if response.status_code != 200:
            error_message = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to publish workflow: {error_message}")
        return workflow_api.PublishedWorkflow.model_validate(response.json())

    def get_scripts_info(
        self,
        version: str | None = None,
    ) -> workflow_api.OrgScriptsInfo:
        """Retrieve the information about the available scripts for the users organization."""
        response = self._make_request(
            method="get",
            endpoint="v3/scripts/info",
            parameters={"version": version} if version else None,
        )
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to get scripts info: {error_response}")
        return workflow_api.OrgScriptsInfo.model_validate(response.json())

    def list_scripts_versions(self) -> list[str]:
        """List all available scripts versions."""
        response = self._make_request(
            method="get",
            endpoint="v3/scripts",
        )
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to list scripts versions: {error_response}")
        return response.json()

    def list_machine_credentials(self) -> list[auth_api.MachineCredentials]:
        """List all machine credentials.

        :return: a list of all machine credentials
        :raises APIError: if the request fails
        """
        response = self._make_request(
            method="get",
            endpoint="v3/auth-management/machine-credentials",
        )
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to list machine credentials: {error_response}")

        return [auth_api.MachineCredentials.model_validate(credentials) for credentials in response.json()]

    def create_machine_credentials(self, *, name: str) -> auth_api.MachineCredentialsWithSecret:
        """Create a new machine credentials with a given name.

        :param name: the name of the machine credentials to create
        :return: the machine credentials with client secret
        :raises APIError: if creating the machine credentials fails
        """
        response = self._make_request(
            method="post",
            endpoint="v3/auth-management/machine-credentials",
            data={"name": name},
        )
        if response.status_code != 201:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to create machine credentials: {error_response}")

        return auth_api.MachineCredentialsWithSecret.model_validate(response.json())

    def delete_machine_credentials(self, *, id: str) -> None:
        """Delete a machine credentials with a given ID.

        :param id: the ID of the machine credentials to delete
        :return: None
        :raises APIError: if deleting the machine credentials fails
        """
        response = self._make_request(
            method="delete",
            endpoint=f"v3/auth-management/machine-credentials/{id}",
        )
        if response.status_code != 204:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to delete machine credentials: {error_response}")

    def rotate_machine_credentials_secret(self, *, id: str) -> auth_api.MachineCredentialsWithSecret:
        """Rotate the secret of a machine credentias with a given ID.

        :param id: the ID of the machine credentials to rotate the secret for
        :return: the machine credentials with the new secret
        :raises APIError: if rotating the secret fails
        """
        response = self._make_request(
            method="put",
            endpoint=f"v3/auth-management/machine-credentials/{id}/secret",
        )
        if response.status_code != 201:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to rotate machine credentials secret: {error_response}")

        return auth_api.MachineCredentialsWithSecret.model_validate(response.json())

    def get_workflow_info(self, workflow_id: UUID) -> workflow_api.WorkflowInfo:
        response = self._make_request(
            method="get",
            endpoint=f"v3/workflow/info/{workflow_id}",
        )
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to get workflow info: {error_response.detail}")
        return workflow_api.WorkflowInfo.model_validate(response.json())

    def get_workflow_puml(
        self,
        workflow: Workflow,
        parameter_values: list[ParameterValue] = [],
    ) -> tuple[str, str]:
        """Get the PlantUML representation of a workflow before & after interpretation.

        :param workflow: the workflow to be validated
        :return: (before, after) PlantUML representations of the workflow
        :raises APIError: if the request fails
        """
        response = self._make_request(
            method="post",
            endpoint="v3/workflow/puml",
            data=workflow.to_api_input_with_parameter_values(parameter_values).model_dump(
                exclude_none=True, mode="json"
            ),
        )
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to get puml representations of workflow '{workflow.name}': {error_response.detail}")
        return tuple(response.json())

    def get_run_histories(
        self,
        device_id: UUID,
        *,
        # run.start_time filters, i.e. start <= start_time < end
        start: Optional[datetime.datetime] = None,
        end: Optional[datetime.datetime] = None,
        # default count = 100, max = 1000, min = 10
        count: Optional[int] = None,
        # default to descending order
        order: Optional[Literal["ascending", "descending"]] = None,
        # pagination cursor, next page cursor returned from previous request if there are more pages
        cursor: Optional[str] = None,
    ) -> backend_api.CursorPaginatedResults[backend_api.RunHistory]:
        """Fetch run histories ordered by start_time for a hub.

        :param device_id: the ID of the hub related to the workcell to fetch run histories for
        :param start: start time filter for run.start_time (inclusive)
        :param end: end time filter for run.start_time (exclusive)
        :param count: number of results to return (default 100, max 1000, min 10)
        :param order: sort order (default descending)
        :param cursor: pagination cursor for next page
        :return: paginated run histories
        :raises APIError: if the request fails
        """
        parameters = {
            "range_start": _format_datetime_param(start),
            "range_end": _format_datetime_param(end),
            "count": count,
            "order": order,
            "cursor": cursor,
        }
        parameters = {k: v for k, v in parameters.items() if v is not None}

        response = self._make_request(
            method="get", endpoint=f"v1/devices/{device_id}/history/run-histories", parameters=parameters
        )

        if response.status_code != 200:
            error_response = LinqBackendErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to get run histories for device '{device_id}': {error_response.message}")

        response_json = response.json()
        return backend_api.CursorPaginatedResults[backend_api.RunHistory](
            next_cursor=response_json["next_cursor"],
            list=[backend_api.RunHistory.model_validate(run_history) for run_history in response_json["list"]],
        )

    def export_run_logs(self, run_id: UUID) -> str:
        response = self._make_request(
            method="get",
            endpoint=f"v1/run-histories/{run_id}/logs/export",
        )
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to export run logs for run '{run_id}': {error_response.detail}")

        return response.json()["download_url"]

    def restart_hub_runtime(self, hub_serial: str) -> str:
        response = self._make_request(
            method="post",
            endpoint=f"v3/workcell/hub/{hub_serial}/restart",
        )
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response.json())
            raise APIError(f"Failed to restart hub runtime for hub '{hub_serial}': {error_response.detail}")

        return response.json()["command_id"]

    def get_restart_command_status(self, command_id: str) -> backend_api.CommandStatusResult:
        response = self._make_request(
            method="get",
            endpoint=f"v3/workcell/hub/{command_id}/status",
        )
        response_json = response.json()
        if response.status_code == 404:
            raise HubRestartCommandResponseNotFound
        if response.status_code != 200:
            error_response = WorkflowAPIErrorResponse.model_validate(response_json)
            raise APIError(f"Failed to get restart command status for command '{command_id}': {error_response.detail}")

        return backend_api.CommandStatusResult(
            status=response_json["result"]["status"],
            instance_name=response_json["result"]["instance_name"],
            status_details=response_json["result"]["status_details"],
        )


def _format_datetime_param(date_param: datetime.datetime | None) -> str | None:
    if date_param is None:
        return None
    if date_param.tzinfo is None:
        # Explicitly set the naive datetime to UTC
        date_param = date_param.replace(tzinfo=timezone.utc)
    return date_param.isoformat()
