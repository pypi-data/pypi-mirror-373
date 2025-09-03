import subprocess
import subprocess
import logging
import os
import json
import anatools

def configure_logging():
    """Configures logging to output to both file and console."""
    log_directory = os.path.join(os.path.dirname(__file__), '.logs')
    os.makedirs(log_directory, exist_ok=True)
    log_filepath = os.path.join(log_directory, 'mcp-server.log')

    # Create a custom logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_filepath)
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(log_format)
    f_handler.setFormatter(log_format)

    # Add handlers to the logger
    # Check if handlers are already added to avoid duplication
    if not logger.handlers:
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

    return logger

# Configure and get the logger instance
logger = configure_logging()

_anatools_client = None

def get_anatools_client():
    """Initializes and returns a singleton anatools client."""
    global _anatools_client
    if _anatools_client is None:
        _anatools_client = anatools.client()
    return _anatools_client



def get_workspace_id():
    """Gets the Workspace ID from the environment."""
    return os.getenv("RENDEREDAI_WORKSPACE_ID")


async def run_service(service_id: str, params: dict) -> str:
    """Runs a local service container using Docker.

    Args:
        service_id: The ID of the service to run, used to find the Docker image.
        params: A dictionary of parameters to pass to the service as a JSON string payload. The /ana/data directory is mounted to /data in the container.

    Returns:
        A markdown-formatted string with the execution result or an error.
    """
    renderedai_api_key = os.getenv("RENDEREDAI_API_KEY")
    if not renderedai_api_key:
        return """❌ **Configuration Error**: RENDEREDAI_API_KEY is not set.

**Suggestions**:
- Please set the `RENDEREDAI_API_KEY` environment variable in your `.env` file.
"""

    logger.info(f"Attempting to run service: {service_id}")

    try:
        # Find the docker image for the given service_id
        image_name = None
        # Command to list all images in JSON format
        image_list_cmd = "docker images -a --format '{{json .}}'"
        result = subprocess.run(image_list_cmd, shell=True, capture_output=True, text=True, check=True)

        # Find the image that contains the service_id in its JSON representation
        for image_json_str in result.stdout.strip().split('\n'):
            if service_id in image_json_str:
                image_data = json.loads(image_json_str)
                image_name = image_data.get('ID') # Using Image ID is more reliable
                if image_name:
                    break

        if not image_name:
            logger.error(f"No Docker image found for service_id: {service_id}")
            return f"""❌ **Execution Error**: Docker image not found.

**Suggestions**:
- Verify that an image containing the service ID `{service_id}` exists on your local machine.
- Check the output of `docker images`.
"""

        logger.info(f"Found image '{image_name}' for service '{service_id}'.")

        # get user id and group id
        user_id = os.getuid()
        group_id = os.getgid()

        def _map_paths_to_container(obj):
            if isinstance(obj, dict):
                return {k: _map_paths_to_container(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_map_paths_to_container(elem) for elem in obj]
            elif isinstance(obj, str) and '/ana/data' in obj:
                return obj.replace('/ana/data', '/data')
            return obj

        mapped_params = _map_paths_to_container(params)

        logger.info(f"Mapped parameters: {mapped_params}")

        # Safely create the JSON payload string
        payload = json.dumps(mapped_params)

        logger.info(f"Payload: {payload}")

        # Construct and execute the docker command
        docker_command = [
            "docker", "run", "--rm",
            "-u", f"{user_id}:{group_id}",
            "-e", f"payload={payload}",
            "-v", f"{os.path.expanduser('~')}/.renderedai:/data",
            image_name
        ]

        logger.debug(f"Executing command: {' '.join(docker_command)}")

        run_result = subprocess.run(docker_command, capture_output=True, text=True)

        if run_result.returncode != 0:
            logger.error(f"Docker execution failed for {service_id}. Stderr: {run_result.stderr.strip()}")
            return f"""❌ **Docker Execution Error** (Exit Code: {run_result.returncode}):

        **Stderr**:
        ```
        {run_result.stderr.strip()}
        ```

        **Stdout**:
        ```
        {run_result.stdout.strip()}
        ```
        """

        logger.info(f"Service {service_id} executed successfully.")
        return f"""✅ **Service Execution Successful**

        **Service ID**: `{service_id}`

        **Output**:
        ```
        {run_result.stdout.strip()}
        ```
        """

    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess failed: {e.stderr}")
        return f"""❌ **Subprocess Error**: Failed to execute a system command.

        **Error**:
        ```
        {e.stderr}
        ```
        """
    except Exception as e:
        logger.exception(f"An unexpected error occurred while running service {service_id}")
        return f"""❌ **Unexpected Error**: {e}

        **Suggestions**:
        - Check the server logs for more details.
        """