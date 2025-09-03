from typing import Any

from ..client import Linq
from ..schema import workflow_api


class InternalLinq(Linq):
    def translate_workflow(
        self,
        workflow: workflow_api.WorkflowConfigInputWithParameters,
    ) -> dict[str, Any]:
        """INTERNAL USE ONLY. Translate a workflow."""
        response = self._make_request(
            method="post",
            endpoint="v3/workflow/translate",
            data=workflow.model_dump(exclude_none=True, mode="json"),
        )
        return response.json()

    def get_workcell_transport_config(self, workcell_id: str) -> dict[str, Any]:
        """INTERNAL USE ONLY"""
        response = self._make_request(
            method="get",
            endpoint=f"v3/workcell/transport?workcell_id={workcell_id}",
        )
        return response.json()

    def post_workcell_transport_config(self, transport_config: dict[str, Any]) -> dict[str, Any]:
        """INTERNAL USE ONLY"""
        response = self._make_request(
            method="post",
            endpoint=f"v3/workcell/transport",
            data=transport_config,
        )
        return response.json()
