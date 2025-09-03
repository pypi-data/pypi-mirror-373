from typing import Optional

import typer
from rich.prompt import Prompt

from mcp_agent.cli.auth import (
    save_api_key_credentials,
)
from mcp_agent.cli.config import settings
from mcp_agent.cli.exceptions import CLIError
from mcp_agent.cli.utils.ux import (
    print_info,
    print_success,
    print_warning,
)

from .constants import DEFAULT_API_AUTH_PATH


def login(
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        help="Optionally set an existing API key to use for authentication, bypassing manual login.",
        envvar="MCP_API_KEY",
    ),
    api_url: Optional[str] = typer.Option(
        None,
        "--api-url",
        help="API base URL. Overrides MCP_API_BASE_URL environment variable and persisted credentials.",
    ),
) -> str:
    """Authenticate to MCP Agent Cloud API.

    Direct to the api keys page for obtaining credentials, routing through login.

    Args:
        api_key: Optionally set an existing API key to use for authentication, bypassing manual login.
        api_url: Override the default base API url.


    Returns:
        None. Prints success message if login is successful.
    """

    if api_key:
        print_info("Using provided API key for authentication.")
        if not _is_valid_api_key(api_key):
            raise CLIError("Invalid API key provided.")
        save_api_key_credentials(api_key)
        print_success("API key set.")
        return api_key

    base_url = api_url or settings.API_BASE_URL
    auth_url = f"{base_url}/{DEFAULT_API_AUTH_PATH}"

    # TODO: This flow should be updated to Oauth2. Probably need to spin up local server to handle
    # the oauth2 callback url.
    print_info("Directing to MCP Agent Cloud API login...")
    typer.launch(auth_url)

    attempts = 3
    while attempts > 0:
        attempts -= 1
        input_api_key = Prompt.ask("Please enter your API key :key:", password=True)

        if not input_api_key:
            print_warning("No API key provided.")
            continue

        if _is_valid_api_key(input_api_key):
            save_api_key_credentials(input_api_key)
            print_success("API key set.")
            return input_api_key

        print_warning("Invalid API key provided.")

    raise CLIError("Failed to set valid API key")


def _is_valid_api_key(api_key: str) -> bool:
    """Validate the API key.

    Args:
        api_key: The API key to validate.

    Returns:
        bool: True if the API key is valid, False otherwise.
    """
    return api_key.startswith("lm_mcp_api_")
