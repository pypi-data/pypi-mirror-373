from typing import Any

import pandas as pd

from ..models.tools import HumanReadableNodeOutput, ToolSummary
from .human_feedback_models import (
    HumanFeedbackToolInput,
    HumanFeedbackToolOutput,
    InputAction,
    InputMethod,
)

__all__ = [
    "get_input",
    "HumanFeedbackToolInput",
    "HumanFeedbackToolOutput",
    "InputAction",
    "InputMethod",
]


class HumanFeedbackToolInternal:
    """
    A tool for gathering user information through human feedback.
    """

    def __init__(self, node_input_data: HumanFeedbackToolInput):
        self.node_input_data = node_input_data

    def input_method_console(
        self,
        *,
        prompt: str,
        tabular_data: list[dict[str, Any]],
        chart_config_data: dict[str, Any] | None,
    ) -> str:
        """
        Get input from the user using the console input method.

        Args:
            prompt (str): The prompt to display to the user.
            tabular_data (list[dict[str, Any]]): The tabular data of the tool.
            chart_config_data (list[dict[str, Any]]): The chart config data of the tool.

        Returns:
            str: The user's input.
        """
        context = ""
        if prompt:
            context = f"{prompt}\n\n"
        if tabular_data:
            context += f"{tabular_data}\n\n"
        if chart_config_data:
            context += f"{chart_config_data}\n\n"
        return input(
            f"""Please provide feedback on the following intermediate output:

{context}

Your feedback: """
        )

    def execute(self) -> HumanFeedbackToolOutput:
        """Execute the tool with the provided input data."""
        input_data = self.node_input_data

        # Validate input
        if (
            not input_data.input
            and not input_data.tabular_data
            and not input_data.chart_config_data
        ):
            raise ValueError(
                "Input data must contain an 'input' key with the prompt for the user "
                "or a 'tabular_data' or a 'chart_config_data' key with the data to "
                "select from."
            )

        if input_data.input_method == InputMethod.console:
            content = self.input_method_console(
                prompt=input_data.input,
                tabular_data=input_data.tabular_data,
                chart_config_data=input_data.chart_config_data,
            )
            return self.get_user_result(content)
        elif input_data.input_method == InputMethod.api:
            # For API input method, return paused state
            if input_data.input_action == InputAction.worksheet_document_upload:
                if not input_data.worksheet_id:
                    raise ValueError("worksheet_id is required for document uploads")
            return self.get_paused_user_result()
        else:
            raise ValueError(f"Unsupported input method: {input_data.input_method}")

    @staticmethod
    def get_user_result(content: str) -> HumanFeedbackToolOutput:
        return HumanFeedbackToolOutput(
            content={"text": content},
            tool_summary=ToolSummary(
                short_summary="Human feedback received",
                long_summary=HumanReadableNodeOutput(text=content),
            ),
        )

    def get_paused_user_result(self) -> HumanFeedbackToolOutput:
        output = HumanFeedbackToolOutput(
            input_action=self.node_input_data.input_action,
            input_question=self.node_input_data.input_question,
            input=self.node_input_data.input,
            chart_config_data=self.node_input_data.chart_config_data,
            tool_summary=ToolSummary(short_summary="Waiting for user input"),
        )
        tabular_data = self.node_input_data.tabular_data
        try:
            if tabular_data and HumanReadableNodeOutput.represents_table_data(
                tabular_data
            ):
                # Add worksheet_id to the output for document uploads
                if (
                    self.node_input_data.input_action
                    == InputAction.worksheet_document_upload
                ):
                    output.worksheet_id = self.node_input_data.worksheet_id
                output.tabular_data = HumanReadableNodeOutput.convert_to_table_data(
                    pd.DataFrame.from_records(tabular_data)
                )
        except (ValueError, TypeError):
            pass
        return output


def get_input(
    *,
    input_method: InputMethod = InputMethod.console,
    input_action: InputAction = InputAction.text,
    input_question: str = "",
    input: str = "",
    tabular_data: list[dict[str, Any]] = [],
    chart_config_data: dict[str, Any] | None = None,
    worksheet_id: int | None = None,
) -> HumanFeedbackToolOutput:
    """
    Gather user feedback through console or API input.
    """
    input_model = HumanFeedbackToolInput(
        input_method=input_method,
        input_action=input_action,
        input_question=input_question,
        input=input,
        tabular_data=tabular_data,
        chart_config_data=chart_config_data,
        worksheet_id=worksheet_id,
    )
    internal = HumanFeedbackToolInternal(node_input_data=input_model)
    return internal.execute()
