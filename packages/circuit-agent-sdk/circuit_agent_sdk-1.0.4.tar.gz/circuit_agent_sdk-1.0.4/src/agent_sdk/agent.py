"""
HTTP server wrapper for agent functions.

This module provides the Agent class that exposes agent functions as HTTP endpoints,
supporting both local development via FastAPI and deployment to AWS Lambda.

Exposes the following endpoints:
- POST /execute — required, calls your execution function
- POST /chat — optional, when a chat_function is provided
- POST /stop and DELETE / — optional, when a stop_function is provided
- GET /health — always available, uses provided or default health check
"""

import base64
import json
import os
from collections.abc import Callable
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .utils import get_agent_config_from_pyproject, setup_logging

# FastAPI imports for local development
try:
    from fastapi import FastAPI, HTTPException
    from mangum import Mangum

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


# Core models for Agent wrapper
class AgentConfig(BaseModel):
    """Configuration for the Agent"""

    title: str = Field(default="Circuit Agent", description="Agent title")
    description: str = Field(default="A Circuit Agent", description="Agent description")
    version: str = Field(default="1.0.0", description="Agent version")


class AgentRequest(BaseModel):
    """Request structure for agent operations"""

    sessionId: int = Field(..., description="Unique session identifier")
    sessionWalletAddress: str = Field(..., description="Wallet address for the session")
    otherParameters: dict[str, Any] | None = Field(
        None, description="Additional parameters"
    )


class AgentResponse(BaseModel):
    """Response structure for agent operations (execute and stop commands)"""

    success: bool = Field(..., description="Whether the operation was successful")
    error: str | None = Field(None, description="Error message if operation failed")
    message: str | None = Field(
        None, description="Success message if operation succeeded"
    )
    data: dict[str, Any] | None = Field(
        None, description="Optional data returned by the operation"
    )


class HealthResponse(BaseModel):
    """Response structure for health check operations"""

    status: str = Field(..., description="Health status (healthy/unhealthy)")


class LambdaResponse(BaseModel):
    """AWS Lambda response structure"""

    statusCode: int = Field(..., description="HTTP status code")
    body: str = Field(..., description="Response body as JSON string")
    headers: dict[str, str] | None = Field(None, description="Response headers")


# Pydantic models for agent contracts
class AgentRequestSchema(BaseModel):
    """Request object for agent functions containing session and wallet information."""

    session_id: int = Field(..., description="Unique session identifier")
    session_wallet_address: str = Field(
        ..., description="Wallet address for the session"
    )
    other_parameters: dict[str, Any] | None = Field(
        None, description="Additional parameters"
    )


class AgentResponseSchema(BaseModel):
    """Standard response format for agent functions (execute and stop commands)."""

    success: bool = Field(..., description="Whether the operation was successful")
    error: str | None = Field(None, description="Error message if operation failed")
    message: str | None = Field(
        None, description="Optional message describing the operation result"
    )
    data: dict[str, Any] | None = Field(
        None, description="Optional data returned by the operation"
    )


class HealthResponseSchema(BaseModel):
    """Health check response format."""

    status: str = Field(..., description="Health status")


# Type aliases for function contracts
ExecutionFunctionContract = Callable[[AgentRequest], AgentResponse]
StopFunctionContract = Callable[[AgentRequest], AgentResponse]
ChatFunctionContract = Callable[[AgentRequest], AgentResponse]
HealthCheckFunctionContract = Callable[[], dict[str, Any]]


class AgentConfigClass(BaseModel):
    """Configuration object for creating a new agent."""

    execution_function: ExecutionFunctionContract = Field(
        ...,
        description="Main execution function that implements the agent's core logic",
    )
    chat_function: ChatFunctionContract | None = Field(
        None, description="Optional chat function for handling interactive messaging"
    )
    stop_function: StopFunctionContract | None = Field(
        None,
        description="Optional winddown function for cleanup operations, this is called when the agent is stopped",
    )
    health_check_function: HealthCheckFunctionContract | None = Field(
        None,
        description="Optional health check function for monitoring agent health status",
    )


class Agent:
    """
    HTTP server wrapper for agent functions.

    Exposes the following endpoints:
    - POST /execute — required, calls your execution function
    - POST /chat — optional, when a chat_function is provided
    - POST /stop and DELETE / — optional, when a stop_function is provided
    - GET /health — always available, uses provided or default health check

    Example:
        ```python
        from agent_sdk import Agent, AgentRequest, AgentResponse

        def execution_function(request: AgentRequest) -> AgentResponse:
            return AgentResponse(success=True, message="Execution completed")

        def stop_function(request: AgentRequest) -> AgentResponse:
            return AgentResponse(success=True, message="Agent stopped")

        agent = Agent(
            execution_function=execution_function,
            stop_function=stop_function
        )
        agent.run()  # Start local development server
        ```
    """

    def __init__(
        self,
        execution_function: ExecutionFunctionContract,
        stop_function: StopFunctionContract | None = None,
        chat_function: ChatFunctionContract | None = None,
        health_check_function: HealthCheckFunctionContract | None = None,
        config: AgentConfig | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Create a new Agent with the provided handlers.

        Args:
            execution_function: Main execution function (required)
            stop_function: Optional stop/cleanup function
            chat_function: Optional chat function for interactive messaging
            health_check_function: Optional health check function
            config: Optional AgentConfig object
            **kwargs: Additional config parameters
        """
        # Load environment variables from .env file first
        load_dotenv()

        # Set up logging first
        self.logger = setup_logging()

        # Store function references
        self.execution_function = execution_function
        self.stop_function = stop_function
        self.chat_function = chat_function
        self._health_check_function = (
            health_check_function or self._default_health_check_function
        )

        # Handle configuration
        config_dict = kwargs
        pyproject_config = get_agent_config_from_pyproject()
        merged_config = {**pyproject_config, **config_dict}

        if config:
            self.config = config
        else:
            self.config = AgentConfig(**merged_config)

        # Validate required functions
        if self.execution_function is None:
            raise ValueError("execution_function is required")

        self.logger.info(
            f"Initialized Circuit Agent: {self.config.title} v{self.config.version}"
        )

        # Initialize FastAPI app if available
        self.app: FastAPI | None = None
        self.lambda_handler: Mangum | None = None
        if FASTAPI_AVAILABLE:
            self._setup_fastapi()

    def _default_stop_function(self, request: AgentRequest) -> AgentResponse:
        """Default stop function"""
        return AgentResponse(
            success=True,
            error=None,
            message=f"Agent stopped for session {request.sessionId}",
            data=None,
        )

    def _default_health_check_function(self) -> dict[str, Any]:
        """Default health check function - returns dict matching TypeScript format"""
        return {"status": "healthy"}

    def health_check_function(self) -> dict[str, Any]:
        """
        Health check function that returns a dict matching TypeScript format
        """
        # _health_check_function is never None due to initialization with default
        result = self._health_check_function()
        # The result is always a dict since _default_health_check_function returns dict
        # and user-provided functions are expected to return dict as well
        return result

    def _setup_fastapi(self) -> None:
        """Set up FastAPI application"""
        if not FASTAPI_AVAILABLE:
            return

        self.app = FastAPI(
            title=self.config.title,
            description=self.config.description,
            version=self.config.version,
        )

        # Create Mangum handler for AWS Lambda compatibility
        self.lambda_handler = Mangum(self.app)

        @self.app.get("/")
        def root() -> dict[str, Any]:
            return {
                "message": f"{self.config.title} is running",
                "mode": "local",
                "version": self.config.version,
            }

        @self.app.get("/health")
        def health() -> dict[str, Any]:
            return self.health_check_function()

        @self.app.post("/execute")
        def execute_agent(request: AgentRequest) -> AgentResponse:
            try:
                result = self.execution_function(request)
                return result
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Execution error: {str(e)}"
                ) from e

        # Only add /chat endpoint if chat_function is provided
        if self.chat_function:

            @self.app.post("/chat")
            def chat_agent(request: AgentRequest) -> AgentResponse:
                try:
                    assert self.chat_function is not None  # Type narrowing for mypy
                    result = self.chat_function(request)
                    return result
                except Exception as e:
                    raise HTTPException(
                        status_code=500, detail=f"Chat error: {str(e)}"
                    ) from e

        @self.app.post("/stop")
        def stop_agent(request: AgentRequest) -> AgentResponse:
            try:
                if self.stop_function:
                    result = self.stop_function(request)
                else:
                    result = self._default_stop_function(request)
                return result
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Stop error: {str(e)}"
                ) from e

        # Only add stop endpoints if stop_function is provided
        if self.stop_function:

            @self.app.delete("/")
            def stop_agent_delete(request: AgentRequest) -> AgentResponse:
                try:
                    assert self.stop_function is not None  # Type narrowing for mypy
                    result = self.stop_function(request)
                    return result
                except Exception as e:
                    raise HTTPException(
                        status_code=500, detail=f"Stop error: {str(e)}"
                    ) from e

        @self.app.post("/{command}")
        def handle_command(
            command: str, request: AgentRequest
        ) -> AgentResponse | dict[str, Any]:
            try:
                if command == "execute":
                    result = self.execution_function(request)
                elif command == "stop":
                    if self.stop_function:
                        result = self.stop_function(request)
                    else:
                        result = self._default_stop_function(request)
                elif command == "health":
                    health_result = self.health_check_function()
                    return health_result
                else:
                    raise HTTPException(
                        status_code=400, detail=f"Unknown command: {command}"
                    )
                return result
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Command error: {str(e)}"
                ) from e

        @self.app.get("/{command}")
        def handle_command_get(command: str) -> dict[str, Any]:
            try:
                if command == "health":
                    return self.health_check_function()
                else:
                    raise HTTPException(
                        status_code=400, detail=f"Unknown command: {command}"
                    )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Command error: {str(e)}"
                ) from e

    def process_request(
        self,
        session_id: int,
        session_wallet_address: str,
        command: str = "execute",
        other_parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process an agent request

        Args:
            session_id: Session ID
            session_wallet_address: Wallet address
            command: Command to execute
            other_parameters: Additional parameters for the request

        Returns:
            Response dictionary
        """
        if other_parameters is None:
            other_parameters = {}

        try:
            if command == "execute":
                request = AgentRequest(
                    sessionId=session_id,
                    sessionWalletAddress=session_wallet_address,
                    otherParameters=other_parameters,
                )
                result = self.execution_function(request)
            elif command == "stop":
                request = AgentRequest(
                    sessionId=session_id,
                    sessionWalletAddress=session_wallet_address,
                    otherParameters=other_parameters,
                )
                if self.stop_function:
                    result = self.stop_function(request)
                else:
                    result = self._default_stop_function(request)
            elif command == "health":
                # Simply call health_check_function which handles all the conversion
                return self.health_check_function()
            else:
                raise ValueError(f"Unknown command: {command}")

            # Convert AgentResponse to dict
            return result.model_dump()

        except Exception as e:
            self.logger.error(f"Request processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Request processing failed",
            }

    def lambda_handler_func(
        self, event: dict[str, Any], context: Any
    ) -> dict[str, Any]:
        """
        AWS Lambda handler function

        Args:
            event: Lambda event
            context: Lambda context

        Returns:
            Lambda response
        """
        self.logger.debug("Lambda handler function called")
        self.logger.debug(f"Event received: {json.dumps(event, default=str)}")

        # If FastAPI is available and this is an HTTP event, use Mangum
        if FASTAPI_AVAILABLE and self.app and self._is_http_event(event):
            if self.lambda_handler is None:
                raise RuntimeError("Lambda handler not available")
            return self.lambda_handler(event, context)

        # Handle direct Lambda invocation
        try:
            # Parse event body
            body = self._parse_event_body(event)

            # Extract command from URL path
            command = self._extract_command(event)

            # Handle DELETE method for stop command
            http_method: str | None = event.get("httpMethod")
            if http_method == "DELETE" and command == "stop":
                command = "stop"  # Ensure command is 'stop' for DELETE /stop

            # Extract required parameters
            session_id = body.get("sessionId")
            session_wallet_address = body.get("sessionWalletAddress")
            other_parameters = body.get("otherParameters", {})

            # Single info log with all relevant information
            if command == "health":
                self.logger.info(f"Lambda request: command={command}")
            else:
                self.logger.info(
                    f"Lambda request: command={command}, session={session_id}, wallet={session_wallet_address}"
                )

            if not all([session_id, session_wallet_address]) and command != "health":
                self.logger.error(
                    "Missing required parameters: sessionId and sessionWalletAddress"
                )
                return LambdaResponse(
                    statusCode=400,
                    body="You must provide 'sessionId' and 'sessionWalletAddress' parameters",
                    headers={},
                ).model_dump()

            # Process the request
            if command == "health":
                # Health check - no sessionId/walletAddress needed
                result: dict[str, Any] = self.health_check_function()
            else:
                if session_id is None or session_wallet_address is None:
                    raise ValueError("Missing required parameters")
                result = self.process_request(
                    session_id, session_wallet_address, command, other_parameters
                )

            self.logger.info(
                f"Lambda response: command={command}, success={result.get('success', True)}"
            )

            # If the result indicates failure, return 500 status code
            if isinstance(result, dict) and result.get("success") is False:
                return LambdaResponse(
                    statusCode=500,
                    body=f"Internal server error: {result.get('error', 'Unknown error')}",
                    headers={},
                ).model_dump()

            return LambdaResponse(
                statusCode=200, body=json.dumps(result), headers={}
            ).model_dump()

        except ValueError as e:
            return LambdaResponse(statusCode=400, body=str(e), headers={}).model_dump()
        except Exception as e:
            return LambdaResponse(
                statusCode=500, body=f"Internal server error: {str(e)}", headers={}
            ).model_dump()

    def _is_http_event(self, event: dict[str, Any]) -> bool:
        """Check if event is an HTTP event"""
        # Check for API Gateway v1.0 format
        if "httpMethod" in event:
            # Require additional fields that would be present in a real API Gateway event
            return all(key in event for key in ["httpMethod", "headers", "path"])
        # Check for API Gateway v2.0 format
        if "requestContext" in event:
            return "http" in event.get("requestContext", {})
        return False

    def _parse_event_body(self, event: dict[str, Any]) -> dict[str, Any]:
        """Parse event body from Lambda event"""
        is_base64_encoded: bool = event.get("isBase64Encoded", False)
        if is_base64_encoded:
            try:
                body_str = base64.b64decode(event["body"]).decode("utf-8")
                parsed_result: dict[str, Any] = json.loads(body_str)
                return parsed_result
            except Exception:
                return {}
        else:
            body: Any = event.get("body", {})
            if isinstance(body, str):
                try:
                    parsed_body: dict[str, Any] = json.loads(body)
                    return parsed_body
                except (json.JSONDecodeError, TypeError):
                    return {}
            return body if isinstance(body, dict) else {}

    def _extract_command(self, event: dict[str, Any]) -> str:
        """Extract command from Lambda event path"""
        raw_path: str = event.get("rawPath", "/")

        # Handle Lambda runtime URL structure
        if raw_path.startswith("/2015-03-31/functions/function/invocations/"):
            return raw_path.split("/")[-1]
        else:
            return raw_path.lstrip("/")

    def run(self, host: str | None = None, port: int | None = None) -> None:
        """
        Run the agent locally using FastAPI

        Args:
            host: Host to bind to
            port: Port to bind to
        """
        if not FASTAPI_AVAILABLE:
            self.logger.error(
                "FastAPI not available. Install with: uv add fastapi uvicorn mangum"
            )
            return

        if not self.app:
            self.logger.error("FastAPI app not initialized")
            return

        import uvicorn

        host = host or "0.0.0.0"
        # Prefer explicit argument, then environment variables set by the CLI, then default
        env_port_str = os.environ.get("PORT") or os.environ.get("AGENT_PORT")
        env_port: int | None = None
        if env_port_str:
            try:
                env_port = int(env_port_str)
            except ValueError:
                env_port = None
        port = port or env_port or 8000

        self.logger.info(
            f"Starting {self.config.title} v{self.config.version} development server on {host}:{port}"
        )
        self.logger.info(
            "Available endpoints: GET /, GET /health, POST /execute, POST /stop, POST /{command}"
        )
        self.logger.info(
            f'Example: curl -X POST "http://{host}:{port}/execute" -H "Content-Type: application/json" -d \'{{"sessionId": 123, "sessionWalletAddress": "0x123..."}}\''
        )

        uvicorn.run(self.app, host=host, port=port)

    def get_lambda_handler(self) -> Any:
        """
        Get the Lambda handler function

        Returns:
            Lambda handler function
        """
        return self.lambda_handler_func

    def get_worker_export(self) -> Any:
        """
        Get export for worker environments (like Cloudflare Workers)
        Currently returns the FastAPI app

        Returns:
            FastAPI app or handler
        """
        if FASTAPI_AVAILABLE and self.app:
            return self.app
        return self.lambda_handler_func


# Simple factory function - just creates an agent
def create_agent_handler(
    execution_function: ExecutionFunctionContract,
    chat_function: ChatFunctionContract | None = None,
    stop_function: StopFunctionContract | None = None,
    health_check_function: HealthCheckFunctionContract | None = None,
) -> Agent:
    """
    Convenience factory to create an Agent from function handlers.

    Args:
        execution_function: Main execution function that implements the agent's core logic
        chat_function: Optional chat function for handling interactive messaging
        stop_function: Optional winddown function for cleanup operations
        health_check_function: Optional health check function for monitoring agent health status

    Returns:
        Agent instance configured with the provided functions

    Example:
        ```python
        from agent_sdk import create_agent_handler, AgentRequest, AgentResponse

        def execution_function(request: AgentRequest) -> AgentResponse:
            return AgentResponse(success=True, message="Execution completed")

        agent = create_agent_handler(execution_function)
        agent.run()
        ```
    """
    return Agent(
        execution_function=execution_function,
        chat_function=chat_function,
        stop_function=stop_function,
        health_check_function=health_check_function,
    )
