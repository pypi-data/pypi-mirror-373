import inspect
import os

from ..models.tools.workflow_models import RunnableConfig

GLOBAL_ENV_VAR_PREFIX = "__A79_GLOBAL_ENV"

RUN_CTX_ENV_NAME = "__A79_RUN_CTX"
CURRENT_NODE_ID_ENV_NAME = "__A79_CURRENT_NODE_ID"
ORG_ID_ENV_NAME = "__A79_ORG_ID"
USER_ID_ENV_NAME = "__A79_USER_ID"


def get_global_env_var_name(var_name: str) -> str:
    return f"{GLOBAL_ENV_VAR_PREFIX}{var_name}"


def get_execution_globals_from_stack():
    """Walk up the call stack to find execution globals with workflow context.

    Returns:
        dict | None: The execution globals containing workflow context, or None if not
        found.
    """
    frame = inspect.currentframe()
    try:
        # Walk up the stack to find a frame with workflow context
        while frame:
            frame_globals = frame.f_globals
            if get_global_env_var_name(RUN_CTX_ENV_NAME) in frame_globals:
                return frame_globals
            frame = frame.f_back
        return None
    finally:
        del frame  # Prevent reference cycles


class WorkflowConfig:
    @staticmethod
    def __get_var_from_globals_or_env(var_name: str) -> str:
        execution_globals = get_execution_globals_from_stack()
        if execution_globals is None:
            var = os.environ.get(var_name)
            if not var:
                raise ValueError(
                    f"{var_name} not found in call stack or environment. "
                    "Make sure this is called from within a workflow node."
                )
            return var
        var = execution_globals.get(get_global_env_var_name(var_name))
        if not var:
            raise ValueError(f"{var_name} not found in execution globals.")
        return var

    @staticmethod
    def get_run_config_json() -> str:
        """Get run config JSON automatically by inspecting the call stack.

        Returns:
            str: The workflow run configuration as JSON.

        Raises:
            ValueError: If no workflow context is found in the call stack.
        """
        return WorkflowConfig.__get_var_from_globals_or_env(RUN_CTX_ENV_NAME)

    @staticmethod
    def get_run_config() -> RunnableConfig:
        """Get run config automatically by inspecting the call stack.

        Returns:
            RunnableConfig: The workflow run configuration.
        """
        run_ctx_json = WorkflowConfig.get_run_config_json()
        return RunnableConfig.model_validate_json(run_ctx_json)

    @staticmethod
    def get_current_node_id() -> str:
        """Get current node ID automatically by inspecting the call stack.

        Returns:
            str: The current node ID.

        Raises:
            ValueError: If no workflow context is found in the call stack.
        """
        return WorkflowConfig.__get_var_from_globals_or_env(CURRENT_NODE_ID_ENV_NAME)

    @staticmethod
    def get_org_id() -> str:
        """Get org id automatically by inspecting the call stack.

        Returns:
            str: The org id.
        """
        return WorkflowConfig.__get_var_from_globals_or_env(ORG_ID_ENV_NAME)

    @staticmethod
    def get_user_id() -> str:
        """Get user id automatically by inspecting the call stack.

        Returns:
            str: The user id.
        """
        return WorkflowConfig.__get_var_from_globals_or_env(USER_ID_ENV_NAME)
