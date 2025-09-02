import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union
from uuid import UUID

import httpx
from httpx import Response

from .api import ApiError
from .models import QECExperiment

LOOM_CONFIG_PATH = Path.home() / ".loom" / "config.json"

logger = logging.getLogger(__package__)


class LoomClient:
    def __init__(self, api_url: Optional[str] = None, api_token: Optional[str] = None):
        self.loom_api_url = api_url or self.__get_config_value(
            "api_url", "LOOM_API_URL"
        )
        self.loom_api_token = api_token or self.__get_config_value(
            "api_token", "LOOM_API_TOKEN"
        )

        # Strip trailing slashes
        self.loom_api_url = self.loom_api_url.rstrip("/") if self.loom_api_url else None

        if not self.loom_api_url or not self.loom_api_token:
            if not LOOM_CONFIG_PATH.exists():
                config_dir = LOOM_CONFIG_PATH.parent
                print(f"""
Error: Loom APIs configuration file not found!

Please create a config file at: {LOOM_CONFIG_PATH}
You may need to create the directory first: mkdir -p {config_dir}

The config file should contain JSON with the following structure:
{{
    "api_url": "https://your-loom-api-endpoint.com",
    "api_token": "your-api-token"
}}

Alternatively, you can set two environment variables:
- LOOM_API_URL
- LOOM_API_TOKEN
                """)
            raise ValueError("API URL and token must be set via env or config")

    ################################################################################################
    ## INTERNALS
    ################################################################################################

    def __get_config_value(self, key: str, env_var: str) -> Optional[str]:
        val = os.getenv(env_var)
        if val:
            return val
        if LOOM_CONFIG_PATH.is_file():
            with open(LOOM_CONFIG_PATH) as f:
                return json.load(f).get(key)

        return None

    def __endpoint_url(self, endpoint: str) -> str:
        """
        Constructs the absolute URL for a given API endpoint.
        """
        # Sanity check: we already check this in __init__
        assert self.loom_api_url, "Loom API URL must be set"

        endpoint = endpoint.lstrip("/")

        return f"{self.loom_api_url}/{endpoint}"

    def __get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.loom_api_token}",
            "Content-Type": "application/json",
        }

    def __get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Response:
        return httpx.get(
            url=self.__endpoint_url(endpoint),
            headers=self.__get_headers(),
            params=params,
        )

    async def __get_async(
        self,
        client: httpx.AsyncClient,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Response:
        return await client.get(
            url=self.__endpoint_url(endpoint),
            headers=self.__get_headers(),
            params=params,
        )

    def __post(
        self, endpoint: str, data: Optional[Union[Dict[str, Any], str]] = None
    ) -> Response:
        """
        Post data to the Loom API.

        Accepted data types:
            - Dict[str, Any]: Will be converted to a JSON payload
            - str: JSON string (will be sent as raw data with correct content type)

        Raises:
            ValueError: If the Loom API URL is not set.
        """
        url = self.__endpoint_url(endpoint)

        if isinstance(data, str):
            # If data is a JSON string, pass it directly as raw text, headers will set content type
            return httpx.post(url=url, headers=self.__get_headers(), content=data)
        else:
            # If data is a dict or None, use json parameter from `requests`
            return httpx.post(url=url, headers=self.__get_headers(), json=data)

    def __post_model(self, endpoint: str, model: Any) -> Response:
        """
        Post a Pydantic model directly to the Loom API. The model will be dumped and transported as JSON.

        Args:
            endpoint: API endpoint to call
            model: Pydantic model instance (must have .model_dump() or .dict() method)

        Returns:
            requests.Response object
        """

        # Check if model has model_dump method (Pydantic v2+)
        if hasattr(model, "model_dump"):
            data = model.model_dump()
        # Fall back to .dict() for older Pydantic versions
        elif hasattr(model, "dict"):
            data = model.dict()
        else:
            raise TypeError(
                "Object must be a Pydantic model with .model_dump() or .dict() method"
            )

        return self.__post(endpoint, data)

    def __is_completed_state(self, state: str) -> bool:
        """
        Check if the given state indicates a completed run
        """
        return state in ["Completed", "Cached", "RolledBack"]

    def __raise_for_failure_state(
        self,
        state: str,
        run_id: UUID,
        start_time: Optional[float] = None,
    ):
        """
        Raise an exception if the run is in a failure state.

        Args:
            state: Current state of the run
            run_id: UUID of the experiment run
            start_time: Time when the run started (extra context for timeout error reporting)
        Raises:
            RuntimeError: If the run is in a failure state
            TimeoutError: If the run has timed out
        """
        if state in ["Cancelled", "Cancelling"]:
            raise RuntimeError(f"Experiment run '{run_id}' was cancelled")
        elif state in ["Failed", "Crashed", "TimedOut"]:
            raise RuntimeError(
                f"Experiment run '{run_id}' failed due an internal error"
            )
        elif state in ["TimedOut"]:
            msg = f"Experiment run '{run_id}' timed out"
            if start_time is not None:
                msg += f" after {time.time() - start_time:.2f} seconds"

            raise TimeoutError(msg)

    def __raise_for_timeout(self, start_time: float, timeout: int):
        """
        Raise a TimeoutError if the run has exceeded the specified timeout.
        Args:
            start_time: Time when the run started
            timeout: Timeout in seconds
        Raises:
            TimeoutError: If the run has exceeded the timeout
        """
        if (time.time() - start_time) > timeout:
            raise TimeoutError(f"The request timed out after {timeout} seconds")

    def __raise_for_error_response(self, response: Response):
        """
        Raise an ApiError or HTTPStatusError if the response indicates an error.

        Use this instead of response.raise_for_status() to handle API-specific errors.

        Args:
            response: HTTP response object
        Raises:
            ApiError: If the response indicates an API error (client or server error)
            HTTPStatusError: If the response is indicates other HTTP errors
        """

        # Catch and convert HTTPStatusError (only client or server errors)
        if response.is_client_error or response.is_server_error:
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as http_status_error:
                raise ApiError(http_status_error)

        # Fallback
        response.raise_for_status()

    ################################################################################################
    ## PUBLIC METHODS
    ################################################################################################

    def experiment_run(self, experiment: QECExperiment) -> UUID:
        """
        Submit a memory experiment run to the Loom API.
        """

        response = self.__post_model("/experiment_run/", experiment)
        # Handle errors
        self.__raise_for_error_response(response)

        result = response.json()
        return UUID(result.get("run_id"))

    def experiment_run_json(self, experiment: Dict[str, Any]) -> UUID:
        """
        Submit a memory experiment run to the Loom API.
        """

        response = self.__post("/experiment_run/", experiment)
        # Handle errors
        self.__raise_for_error_response(response)

        result = response.json()
        return UUID(result.get("run_id"))

    def get_experiment_run_status(self, run_id: UUID) -> Dict[str, Any]:
        """
        Get the status of a specific experiment run by its ID.

        Args:
            run_id: UUID of the experiment run

        Returns:
            JSON object containing the run status
        """

        response = self.__get(f"/experiment_run/{run_id}")
        self.__raise_for_error_response(response)

        return response.json()

    def get_experiment_run_result(self, run_id: UUID) -> dict[str, Any]:
        """
        Get the result of a specific experiment run by its ID. Will return a 404 (not found) status
        error if no result is present for the given run ID.

        Use the `get_experiment_run_status` method first, to check the progress of the run.

        Args:
            run_id: UUID of the experiment run

        Returns:
            JSON object containing the run result or raises a 404 error if the result doesn't exist.
        """

        response = self.__get(f"/experiment_run/{run_id}/result")
        self.__raise_for_error_response(response)

        return response.json()

    def get_result_sync(
        self, run_id: UUID, timeout: Optional[int] = None
    ) -> dict[str, Any]:
        """
        Synchronously wait for and retrieve the result of an experiment run.
        This method blocks until the run is completed or fails.

        Args:
            run_id: UUID of the experiment run
            timeout: Optional timeout in seconds. If None, will wait indefinitely.

        Returns:
            JSON object containing the run result
        Raises:
            RuntimeError: If the experiment run fails or crashes
            TimeoutError: If the timeout is reached before the run completes
        """

        start_time = time.time()

        while True:
            # Get the current status
            status = self.get_experiment_run_status(run_id)

            logger.debug(f"Experiment run '{run_id}' current status: {status['state']}")

            # Raise for failure state
            self.__raise_for_failure_state(
                status["state"],
                run_id=run_id,
                start_time=start_time,
            )

            # Raise for user provided timeout
            if timeout is not None:
                self.__raise_for_timeout(start_time, timeout)

            # Check if the run is completed
            if self.__is_completed_state(status["state"]):
                # Get and return the result
                return self.get_experiment_run_result(run_id)

            # Wait
            time.sleep(1)

    async def get_result_async(
        self, run_id: UUID, timeout: Optional[int] = None
    ) -> dict[str, Any]:
        """
        Asynchronously wait for and retrieve the result of an experiment run.

        This is the non-blocking version of get_result_sync.

        Args:
            run_id: UUID of the experiment run
            timeout: Optional timeout in seconds

        Returns:
            JSON object containing the run result

        Raises:
            RuntimeError: If the experiment run fails or crashes
            TimeoutError: If the timeout is reached before the run completes
        """

        import asyncio
        import time

        import httpx

        # Add this check to prevent None.rstrip() error
        if not self.loom_api_url:
            raise ValueError(
                "Loom API base URL is not set. Configure it in the config file or environment variable LOOM_API_URL."
            )

        start_time = time.time()

        # Create HTTP client for async requests
        async with httpx.AsyncClient() as client:
            while True:
                # Get the current status
                response = await self.__get_async(client, f"/experiment_run/{run_id}")
                self.__raise_for_error_response(response)

                status = response.json()

                logger.debug(
                    f"Experiment run '{run_id}' current status: {status['state']}"
                )

                # Raise for experiment failure state
                self.__raise_for_failure_state(
                    status["state"],
                    run_id=run_id,
                    start_time=start_time,
                )

                # Raise for user provided timeout
                if timeout is not None:
                    self.__raise_for_timeout(start_time, timeout)

                # Check if the run is completed
                if self.__is_completed_state(status["state"]):
                    # Get and return the result
                    response = await self.__get_async(
                        client, f"/experiment_run/{run_id}/result"
                    )
                    self.__raise_for_error_response(response)

                    return response.json()

                # Non-blocking sleep
                await asyncio.sleep(1)
