import atexit
import pathlib
from typing import Any, BinaryIO, Dict, Optional, Tuple

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from obvyr_agent import utils
from obvyr_agent.error_handling import handle_api_error, handle_network_error
from obvyr_agent.logging_config import get_logger

logger = get_logger("api_client")

project_config = utils.get_project_config()


class ObvyrAPIClient:
    """Client for sending execution data to the Obvyr API."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: float = 5.0,
        verify_ssl: bool = True,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        """Initialize API client with optional settings injection."""
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self.client: httpx.Client = http_client or httpx.Client(
            base_url=base_url, timeout=timeout, verify=self.verify_ssl
        )
        self._closed = False
        atexit.register(self.close)

    def _get_headers(self) -> Dict[str, str]:
        """Generate headers for authentication."""
        return {
            "Authorization": (f"Bearer {self.api_key}"),
            "User-Agent": f"obvyr-agent/{project_config['version']}",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(
            (httpx.RequestError, httpx.HTTPStatusError)
        ),
        reraise=True,
    )
    def send_data(
        self,
        endpoint: str,
        data: Dict[str, Any],
        file: Optional[Tuple[str, BinaryIO]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Send execution data to the API with retries on transient failures."""
        headers = self._get_headers()

        try:
            optional_parameters: Dict[str, Any] = {}

            if file:
                optional_parameters = {
                    **optional_parameters,
                    "files": {"attachment": (file[0], file[1])},
                }

            response = self.client.post(
                endpoint, headers=headers, data=data, **optional_parameters
            )

            response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            return handle_api_error(e)
        except (httpx.RequestError, httpx.TimeoutException) as e:
            handle_network_error(e)
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(
            (httpx.RequestError, httpx.HTTPStatusError)
        ),
        reraise=True,
    )
    def send_archive(
        self, endpoint: str, archive_path: pathlib.Path
    ) -> Optional[Dict[str, Any]]:
        """Send archive file to the API with retries on transient failures."""
        if not archive_path.exists():
            raise FileNotFoundError(f"Archive file not found: {archive_path}")

        headers = self._get_headers()

        try:
            with open(archive_path, "rb") as archive_file:
                files = {"archive": ("artifacts.tar.zst", archive_file)}
                response = self.client.post(
                    endpoint, headers=headers, files=files
                )

            response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            return handle_api_error(e)
        except (httpx.RequestError, httpx.TimeoutException) as e:
            handle_network_error(e)
            return None

    def close(self) -> None:
        """Close the HTTP connection pool."""
        if not self._closed:
            self.client.close()
            self._closed = True
            logger.debug("Closed API client connection.")

    def __enter__(self) -> "ObvyrAPIClient":
        """Enable use of `with ObvyrAPIClient() as client`."""
        return self

    def __exit__(self, *args: object, **kwargs: object) -> None:
        """Ensure the HTTP client is closed when exiting context."""
        self.close()
