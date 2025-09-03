import importlib
import os
import time
from typing import Any

import requests

from .helpers.config import WorkflowConfig
from .models.enums import RunStatus
from .models.tools.workflow_models import StreamId

api_url = os.environ.get("A79_API_URL")
api_key = os.environ.get("A79_API_KEY")

__all__ = ["A79Client"]


class A79ClientExternal:
    """Simple HTTP client for interacting with A79 API."""

    def __init__(self):
        """
        Initialize the A79 API client.

        Args:
            api_url: Base URL for A79 API
            api_key: API key for authentication
        """
        api_url = os.environ.get("A79_API_URL")
        api_key = os.environ.get("A79_API_KEY")

        if not api_url:
            raise ValueError("A79_API_URL environment variable must be set")

        if not api_key:
            raise ValueError("A79_API_KEY environment variable must be set")

        self.base_url = api_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def raw_request(self, *, method: str, url: str, json: dict) -> dict:
        response = requests.request(
            method, f"{self.base_url}{url}", headers=self.headers, json=json
        )
        response.raise_for_status()
        return response.json()

    def execute_tool(
        self, *, package: str, name: str, input: dict[str, Any]
    ) -> dict[str, Any]:
        url = f"{self.base_url}/api/v1/tool/execute"
        workflow_run_config_json = WorkflowConfig.get_run_config_json()

        response = requests.post(
            url,
            json={
                "package": package,
                "name": name,
                "input": input,
                "workflow_run_config_json": workflow_run_config_json,
            },
            headers=self.headers,
        )
        response.raise_for_status()
        task_id = response.json()

        # Since sub-workflows are also treated as a single tool call, we need to wait for
        # a longer time. Setting it to 15 minutes for now to handle sub-workflows.
        wait_time_secs = 0.25
        total_wait_time_secs = 15 * 60  # 15 minutes
        number_of_attempts = total_wait_time_secs / wait_time_secs
        number_of_failed_attempts = 0
        while number_of_attempts > 0:
            number_of_attempts = number_of_attempts - 1
            response = requests.get(
                f"{self.base_url}/api/v1/tool/status/{task_id}", headers=self.headers
            )
            response.raise_for_status()
            wait_time_secs = min(wait_time_secs * 2, 5)
            if response.status_code != 200 or response.json()["status"] == "running":
                if response.status_code != 200:
                    number_of_failed_attempts = number_of_failed_attempts + 1
                    if number_of_failed_attempts > 5:
                        break
                time.sleep(wait_time_secs)
            else:
                break
        result = response.json()
        if not result:
            raise Exception("Tool execution failed. No result returned.")
        if result and result["status"] == RunStatus.FAILED.value:
            raise Exception(result["error_msg"])
        return result["output"]

    def execute_tool_streaming(
        self, *, package: str, name: str, input: dict[str, Any]
    ) -> StreamId:
        """Execute a streaming tool and return a stream ID.

        This method is used for tools that return streaming responses (like
        perplexity.chat_stream).
        It returns a stream ID that can be used with the /stream/{stream_id} endpoint
        to get the actual SSE stream.

        Args:
            package: Tool package name
            name: Tool name
            input: Tool input parameters

        Returns:
            str: Stream ID that can be used to subscribe to the stream

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}/api/v1/tool/execute_stream"
        workflow_run_config_json = WorkflowConfig.get_run_config_json()

        # Get the stream_id from the execute_stream endpoint
        response = requests.post(
            url,
            json={
                "package": package,
                "name": name,
                "input": input,
                "workflow_run_config_json": workflow_run_config_json,
            },
            headers=self.headers,
        )
        response.raise_for_status()
        stream_id = response.json()
        return stream_id


if not api_url and not api_key:
    a79_sdk_client = importlib.import_module("common_py.internal.a79_sdk_client")
    A79Client = a79_sdk_client.A79ClientInternal
else:
    A79Client = A79ClientExternal
