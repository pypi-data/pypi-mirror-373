"""
Low-level HTTP client used internally by the SDK.

This module provides the APIClient class that handles all HTTP communication
with the Circuit backend, including authentication, request/response logging,
and error handling.
"""

import json
import os
from pathlib import Path
from typing import Any, TypeVar

import requests
from pydantic import BaseModel

from .types.config import API_BASE_URL_LAMBDA, API_BASE_URL_LOCAL, SDKConfig

T = TypeVar("T", bound=BaseModel)


class APIClient:
    """
    Low-level HTTP client used internally by the SDK.

    - Automatically detects Lambda environment and uses VPC proxy
    - Falls back to HTTP requests for local development with session token auth
    - Adds session ID and agent slug headers automatically
    - Emits verbose request/response logs when SDKConfig.verbose is enabled

    Authentication:
    - Lambda environments: No additional auth needed (VPC proxy handles it)
    - Local development: Session token from CLI auth config if available
    - Always includes session ID and agent slug headers for validation

    Although this class can be used directly, most users should interact with
    higher-level abstractions like AgentSdk and AgentUtils.

    Example:
        ```python
        from agent_sdk import SDKConfig
        from agent_sdk.client import APIClient

        config = SDKConfig(session_id=123, verbose=True)
        client = APIClient(config)

        # Make authenticated requests
        response = await client.post("/v1/logs", [{"type": "observe", "shortMessage": "test"}])
        ```
    """

    def __init__(self, config: SDKConfig) -> None:
        """
        Create an API client.

        Args:
            config: SDK configuration containing session ID, base URL, and other settings
        """
        self.config = config
        self.base_url = config.base_url or self._get_default_base_url()

    def _is_lambda_environment(self) -> bool:
        """Check if running in AWS Lambda environment."""
        # Check for Lambda-specific environment variables
        return (
            os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None
            or os.environ.get("LAMBDA_TASK_ROOT") is not None
            or os.environ.get("AWS_EXECUTION_ENV") is not None
        )

    def _get_default_base_url(self) -> str:
        """Get default base URL based on environment."""
        if self._is_lambda_environment():
            # Use internal VPC URL for Lambda agents
            return API_BASE_URL_LAMBDA
        else:
            # Default to local development URL
            return API_BASE_URL_LOCAL

    def _get_auth_headers(self) -> dict[str, str]:
        """
        Generate authentication headers for requests.

        For Lambda environments, no additional auth is needed as the proxy
        handles Cloudflare Access authentication. For local development,
        session token auth is used if available.

        Returns:
            Dictionary of headers to include in requests
        """
        headers: dict[str, str] = {}

        # Always include session ID header
        if self.config.session_id:
            headers["X-Session-Id"] = str(self.config.session_id)

        # Include agent slug if available (for deployed agents)
        agent_slug = self._get_agent_slug()
        if agent_slug:
            headers["X-Agent-Slug"] = agent_slug

        # For Lambda environments, we don't need additional auth
        # as the proxy handles Cloudflare Access authentication
        if self._is_lambda_environment():
            return headers

        # For local development, try to include session token
        try:
            auth_config = self._load_auth_config()
            if auth_config and auth_config.get("sessionToken"):
                headers["Authorization"] = f"Bearer {auth_config['sessionToken']}"
        except Exception:
            # Auth config not available, continue without auth
            pass

        return headers

    def _get_agent_slug(self) -> str | None:
        """Get agent slug from environment variables."""
        # Check for agent slug in environment variables
        return os.environ.get("CIRCUIT_AGENT_SLUG")

    def _load_auth_config(self) -> dict[str, Any] | None:
        """
        Try to load auth config from the same location the CLI uses.

        Returns:
            Auth configuration dictionary or None if not available
        """
        try:
            # Try to load from file system (same path as TypeScript CLI)
            home = Path.home()
            auth_path = home / ".config" / "circuit" / "auth.json"

            if auth_path.exists():
                with open(auth_path, encoding="utf-8") as f:
                    data: dict[str, Any] = json.load(f)
                    return data
        except Exception:
            # Auth config not available
            pass
        return None

    def _log(self, log: str, data: Any = None) -> None:
        """
        Log debug information when verbose mode is enabled.

        Args:
            log: Log message
            data: Optional data to include in log
        """
        if self.config.verbose:
            log_message = f"[SDK DEBUG] {log}"
            if data is not None:
                log_message += f" {json.dumps(data, indent=2, default=str)}"
            print(log_message)

    def _make_request(
        self, method: str, endpoint: str, data: Any = None
    ) -> dict[str, Any]:
        """
        Perform a JSON HTTP request.

        Automatically attaches auth headers and logs details when verbose is on.
        Raises helpful errors when the HTTP response is not ok.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API path beginning with /v1/...
            data: Optional JSON payload to serialize

        Returns:
            Parsed JSON response

        Raises:
            requests.RequestException: When response.ok is False or other HTTP errors
        """
        url = f"{self.base_url}{endpoint}"

        auth_headers = self._get_auth_headers()
        default_headers = {
            "Content-Type": "application/json",
            **auth_headers,
        }

        # Prepare request data
        json_data = None
        if data is not None:
            if isinstance(data, BaseModel):
                json_data = data.model_dump()
            else:
                json_data = data

        # Log request details
        self._log("=== REQUEST DETAILS ===")
        self._log("URL:", url)
        self._log("Method:", method)
        self._log("Headers:", default_headers)
        self._log("Body:", json_data)
        self._log("Session ID:", self.config.session_id)
        self._log("Agent Slug:", self._get_agent_slug())
        self._log("Environment:", self._get_environment_info())
        self._log("Base URL:", self.base_url)
        self._log("=====================")

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=default_headers,
                json=json_data,
                timeout=30,
            )

            # Log response details
            self._log("=== RESPONSE DETAILS ===")
            self._log("Status:", response.status_code)
            self._log("Status Text:", response.reason)
            self._log("Response Headers:", dict(response.headers))
            self._log("======================")

            if not response.ok:
                try:
                    error_data = response.json()
                except Exception:
                    error_data = {}

                self._log("=== ERROR RESPONSE ===")
                self._log("Error Data:", error_data)
                self._log("====================")

                # Extract error message for logging (was unused before)
                error_message = error_data.get(
                    "message", f"HTTP {response.status_code}: {response.reason}"
                )
                self._log("Error message:", error_message)
                response.raise_for_status()  # This will raise the appropriate requests exception

            response_data: dict[str, Any] = response.json()
            self._log("=== SUCCESS RESPONSE ===")
            self._log("Response Data:", response_data)
            self._log("======================")

            return response_data

        except requests.RequestException as e:
            self._log("=== REQUEST ERROR ===")
            self._log("Error:", str(e))
            self._log("====================")
            raise

    def _get_environment_info(self) -> str:
        """Get human-readable environment information."""
        if self._is_lambda_environment():
            return "AWS Lambda (using VPC proxy)"
        else:
            return "Local Development"

    def get(self, endpoint: str) -> dict[str, Any]:
        """
        HTTP GET convenience method.

        Args:
            endpoint: API path beginning with /v1/...

        Returns:
            Parsed JSON response
        """
        return self._make_request("GET", endpoint)

    def post(self, endpoint: str, data: Any = None) -> dict[str, Any]:
        """
        HTTP POST convenience method sending a JSON body.

        Args:
            endpoint: API path beginning with /v1/...
            data: Optional JSON payload to serialize

        Returns:
            Parsed JSON response
        """
        return self._make_request("POST", endpoint, data)
