import logging
import os
import subprocess
import time
from typing import List

from obvyr_agent.schemas import RunCommandResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_obvyr_agent_user() -> str:
    """
    Retrieves the user running the agent based on the OBVYR_AGENT_USER environment variable.
    This allows for maximum configurability and control by the customer.
    """
    user = os.getenv("OBVYR_AGENT_USER")
    if user:
        logger.info(f"Using user specified by OBVYR_AGENT_USER: {user}")
        return user

    # Default if the user hasn't specified anything
    logger.warning("OBVYR_AGENT_USER not set. Using default: 'unknown_user'")
    return "unknown_user"


def run_command(
    command: List[str],
) -> RunCommandResponse:
    """
    Executes a system command and returns the output.
    :param command: List of command arguments.
    :return: RunCommandResponse object.
    """
    user = get_obvyr_agent_user()

    start_time = time.time()

    try:
        process = subprocess.Popen(  # noqa: S603
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        logger.info(f"Executed command: {' '.join(command)}")

        stdout, stderr = process.communicate()
        returncode = process.returncode
    except Exception as e:
        exception_type = e.__class__.__name__
        exception_string = f"{exception_type}: {e}"
        logger.error(
            f"Failed to execute command: {command}. {exception_string}"
        )
        stdout = None
        stderr = exception_string
        returncode = -1

    end_time = time.time()
    execution_time = end_time - start_time

    return RunCommandResponse(
        command=command,
        stdout=stdout,
        stderr=stderr,
        returncode=returncode,
        user=user,
        execution_time=execution_time,
    )
