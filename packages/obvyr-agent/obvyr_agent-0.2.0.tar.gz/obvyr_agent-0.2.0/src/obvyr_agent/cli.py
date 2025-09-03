import time
from typing import List

import click

from obvyr_agent.api_client import ObvyrAPIClient
from obvyr_agent.archive_builder import build_artifacts_tar_zst
from obvyr_agent.command_wrapper import run_command
from obvyr_agent.config import AgentSettings, Settings, get_settings
from obvyr_agent.error_handling import handle_archive_error
from obvyr_agent.logging_config import configure_logging, get_logger
from obvyr_agent.schemas import RunCommandResponse

logger = get_logger("cli")

# ===================================
# CLI Support Functions
# ===================================


def list_available_agents(settings: Settings) -> None:
    """
    Lists all available agents.
    """
    agents = settings.list_agents()

    if len(agents) == 0:
        click.echo("\nNo agents available.\n")
        return

    click.echo("\nAvailable agents:\n")
    for agent in agents:
        click.echo(f"  - {agent}")
    click.echo("")


def show_agent_config(
    settings: Settings, agent_name: str | None = None
) -> None:
    """
    Shows the configuration for the specified or active agent.
    """
    config = settings.show_config(agent_name)

    agent_display = agent_name or settings.ACTIVE_AGENT
    click.echo(f"\nAgent '{agent_display}' configuration:\n")
    for key, value in config.items():
        click.echo(f"  {key}: {value}")
    click.echo("")


def has_handled_initial_options(
    command: List[str],
    list_agents: bool,
    show_config: bool,
    settings: Settings,
    agent: str | None = None,
) -> bool:
    """Handle initial options for listing agents or showing configuration."""
    if command:
        return False

    if list_agents:
        list_available_agents(settings)
        return True

    if show_config:
        show_agent_config(settings, agent)
        return True

    raise click.UsageError(
        "\n".join(
            (
                "No command provided.",
                "Usage: obvyr-agent <command> [arguments]",
                "Try 'obvyr-agent --help' for more information.",
            )
        )
    )


def fetch_active_agent(
    settings: Settings, agent_name: str | None = None
) -> AgentSettings:
    """Retrieve the active agent from settings."""
    active_agent = settings.get_agent(agent_name)
    agent_display_name = agent_name or settings.ACTIVE_AGENT
    logger.debug(f"Using agent: {agent_display_name}")
    return active_agent


def display_output(response: RunCommandResponse) -> None:
    """Display the command's output and errors."""
    if response.stdout:
        click.echo(f"\n{response.stdout}")

    if response.stderr:
        click.echo(f"\n{response.stderr}", err=True)

    output = (
        f"\nExecuted by {click.style(response.user, fg='green')} "
        f"in {click.style(f'{response.execution_time:.2f}s', fg='blue')}\n"
    )
    click.echo(output)


def send_to_api(active_agent: AgentSettings, data: RunCommandResponse) -> None:
    """
    Sends execution data to the Obvyr API.

    :param active_agent: Agent configuration to use for API submission.
    :param data: Command execution result to be sent to the API.
    """

    if not active_agent.API_KEY:
        logger.debug("API submission disabled: No API key configured.")
        return

    archive_path = None
    try:
        # Create archive from command execution data
        archive_path = build_artifacts_tar_zst(data)

        with ObvyrAPIClient(
            api_key=active_agent.API_KEY,
            base_url=active_agent.API_URL,
            timeout=active_agent.TIMEOUT,
            verify_ssl=active_agent.VERIFY_SSL,
        ) as client:
            start_time = time.time()
            response = client.send_archive("/collect", archive_path)
            end_time = time.time()

            logger.debug(f"API request time: {end_time - start_time:.2f}s")

            if response:
                logger.debug(f"Successfully sent data to API: {response}")
            else:
                logger.warning(
                    "Failed to send data to API. Check your configuration."
                )

    except OSError as e:
        handle_archive_error(e)
    except Exception as e:
        # Other errors are already handled by the API client's centralised error handling
        logger.error(f"Unexpected error during API submission: {e}")
    finally:
        # Always clean up the temporary archive file
        if archive_path and archive_path.exists():
            archive_path.unlink()


# ===================================
# Click CLI
# ===================================


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("command", nargs=-1, required=False, type=click.UNPROCESSED)
@click.option(
    "--list-agents",
    "list_agents",
    is_flag=True,
    help="List all available agents.",
)
@click.option(
    "--show-config",
    "show_config",
    is_flag=True,
    help="Show config for active agent.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging (debug mode).",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Enable quiet mode (errors only).",
)
@click.option(
    "--agent",
    "-a",
    help="Specify which agent configuration to use.",
)
def cli_run_process(
    command: List[str],
    list_agents: bool,
    show_config: bool,
    verbose: bool,
    quiet: bool,
    agent: str | None,
) -> None:
    """
    Executes a system command while using the Obvyr agent configuration.
    """
    # Configure logging based on CLI flags
    configure_logging(verbose=verbose, quiet=quiet)

    try:
        settings = get_settings()

        if has_handled_initial_options(
            command, list_agents, show_config, settings, agent
        ):
            return

        active_agent = fetch_active_agent(settings, agent)

        response: RunCommandResponse = run_command(list(command))

        if active_agent.API_URL and active_agent.API_KEY:
            send_to_api(active_agent, response)

        display_output(response)

        if response.returncode != 0:
            raise click.exceptions.Exit(response.returncode)

    except Exception as e:
        raise click.ClickException(str(e)) from e
