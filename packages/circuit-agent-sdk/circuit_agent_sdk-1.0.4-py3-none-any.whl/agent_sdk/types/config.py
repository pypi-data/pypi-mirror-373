"""
Configuration type definitions for the Agent SDK.

This module provides configuration models and constants used throughout the SDK.
"""

from pydantic import BaseModel, ConfigDict, Field

# Base URLs for the API
API_BASE_URL_LOCAL = "https://agents.circuit.org"
# Internal VPC URL for Lambda agents (resolves to proxy instance)
API_BASE_URL_LAMBDA = "http://transaction-service.agent.internal"


class SDKConfig(BaseModel):
    """
    Configuration for the SDK client.

    This is the main configuration object passed to AgentSdk constructor.
    Only sessionId is required; all other fields have sensible defaults.

    Attributes:
        session_id: Numeric session identifier that scopes auth and actions
        verbose: Enable verbose logging for debugging requests/responses
        testing: Enable testing mode to return mock responses instead of real calls
        base_url: Override API base URL (auto-detected if not provided)
        connections: Optional RPC URLs used by utils for direct chain access

    Example:
        ```python
        # Minimal configuration
        config = SDKConfig(session_id=123)

        # Full configuration
        config = SDKConfig(
            session_id=123,
            verbose=True,
            testing=False,
            base_url="https://custom-api.example.com"
        )
        ```
    """

    session_id: int = Field(
        ...,
        description="Session ID for the current agent instance",
        gt=0,  # Must be positive
    )
    verbose: bool = Field(False, description="Enable verbose logging for debugging")
    testing: bool = Field(
        False, description="Enable testing mode to return mock responses"
    )
    base_url: str | None = Field(None, description="Optional base URL for API requests")

    model_config = ConfigDict(extra="forbid")
