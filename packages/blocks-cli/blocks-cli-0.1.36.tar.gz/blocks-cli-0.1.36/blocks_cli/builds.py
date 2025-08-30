import time

from blocks_cli.api import api_client
from blocks_cli.config.config import config

def poll_build_status(image_id: str, build_id: str):
    build_completed = False
    while not build_completed:
        try:
            time.sleep(0.5)
            res = api_client.get(f"{config.clients.orchestrator_url}/v1/images/{image_id}/builds/{build_id}")
            build_status_response = res.json()
                
            is_completed = build_status_response.get("is_completed")
            is_succeeded = build_status_response.get("is_succeeded")

            build_completed = is_completed

            if is_completed and not is_succeeded:
                error_message = build_status_response.get("error_message") or "Unknown build error"
                logs = build_status_response.get("logs")
                if logs:
                    error_message += f"\nBuild logs: {logs}"
                raise Exception(f"Build failed: {error_message}")
        except Exception as e:
            if "Build failed" in str(e):
                raise
            raise Exception(f"Failed to retrieve build status: {str(e)}")
        