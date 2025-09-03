import socket
from datetime import datetime


class WorkflowInitializer:
    def __init__(self):
        pass

    @staticmethod
    def initialize() -> None:
        # Import here to avoid circular dependency
        from ..client import A79Client

        api_client = A79Client()

        # Generate timestamp string in format: YYYYMMDD_HHMMSS
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hostname = socket.gethostname()

        base_name = f"sdk-run-{hostname}-{timestamp}"

        folder_response = api_client.raw_request(
            method="POST", url="/api/v1/folder", json={"name": base_name}
        )
        print(folder_response)
