"""
Tests for the Agent class
"""

import base64
import json
from unittest.mock import MagicMock, patch

import pytest

from agent_sdk import Agent, AgentConfig, AgentRequest, AgentResponse
from agent_sdk.utils import get_agent_config_from_pyproject, read_pyproject_config


class TestAgent:
    """Test cases for the Agent class"""

    @pytest.fixture
    def mock_execution_function(self):
        """Mock execution function for testing"""

        def mock_func(request: AgentRequest) -> AgentResponse:
            return AgentResponse(success=True, data={"message": "test"})

        return mock_func

    @pytest.fixture
    def mock_stop_function(self):
        """Mock stop function for testing"""

        def mock_func(request: AgentRequest) -> AgentResponse:
            return AgentResponse(success=True, data={"cleanup": "done"})

        return mock_func

    @pytest.fixture
    def mock_health_function(self):
        """Mock health function for testing"""

        def mock_func():
            return {"status": "healthy", "version": "1.0.0"}

        return mock_func

    @pytest.fixture
    def sample_request(self):
        """Sample AgentRequest for testing"""
        return AgentRequest(
            sessionId=123, sessionWalletAddress="0x1234567890abcdef", otherParameters={}
        )

    def test_agent_initialization(self, mock_execution_function, mock_stop_function):
        """Test basic agent initialization"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        assert agent.execution_function == mock_execution_function
        assert agent.stop_function == mock_stop_function
        assert agent.health_check_function is not None
        assert agent.config is not None
        assert agent.logger is not None

    def test_agent_initialization_with_all_functions(
        self, mock_execution_function, mock_stop_function, mock_health_function
    ):
        """Test agent initialization with all functions provided"""
        agent = Agent(
            execution_function=mock_execution_function,
            stop_function=mock_stop_function,
            health_check_function=mock_health_function,
        )

        assert agent.execution_function == mock_execution_function
        assert agent.stop_function == mock_stop_function
        assert agent._health_check_function == mock_health_function

    def test_agent_initialization_with_config(
        self, mock_execution_function, mock_stop_function
    ):
        """Test agent initialization with custom config"""
        config = AgentConfig(
            title="Test Agent",
            description="A test agent",
            version="2.0.0",
        )

        agent = Agent(
            execution_function=mock_execution_function,
            stop_function=mock_stop_function,
            config=config,
        )

        assert agent.config.title == "Test Agent"
        assert agent.config.description == "A test agent"
        assert agent.config.version == "2.0.0"

    def test_agent_initialization_missing_execution_function(self):
        """Test that agent raises error when execution function is missing"""
        with pytest.raises(TypeError):
            Agent()

    def test_process_request_success(
        self, mock_execution_function, mock_stop_function, sample_request
    ):
        """Test successful request processing"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        result = agent.process_request(
            session_id=sample_request.sessionId,
            session_wallet_address=sample_request.sessionWalletAddress,
            command="execute",
        )

        assert result["success"] is True
        assert "data" in result

    def test_process_request_with_error(self, mock_stop_function, sample_request):
        """Test request processing with error"""

        def error_function(request: AgentRequest) -> AgentResponse:
            raise Exception("Test error")

        agent = Agent(
            execution_function=error_function, stop_function=mock_stop_function
        )

        result = agent.process_request(
            session_id=sample_request.sessionId,
            session_wallet_address=sample_request.sessionWalletAddress,
            command="execute",
        )

        assert result["success"] is False
        assert "error" in result
        assert "Test error" in result["error"]

    def test_default_stop_function(self, mock_stop_function, sample_request):
        """Test the default stop function"""
        agent = Agent(
            execution_function=lambda req: AgentResponse(success=True),
            stop_function=mock_stop_function,
        )

        result = agent.stop_function(sample_request)

        assert isinstance(result, AgentResponse)
        assert result.success is True

    def test_default_health_function(self, mock_stop_function):
        """Test the default health function"""
        agent = Agent(
            execution_function=lambda req: AgentResponse(success=True),
            stop_function=mock_stop_function,
        )

        result = agent.health_check_function()

        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] == "healthy"

    def test_get_lambda_handler(self, mock_execution_function, mock_stop_function):
        """Test that lambda handler is returned"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        handler = agent.get_lambda_handler()

        assert callable(handler)
        assert handler.__name__ == "lambda_handler_func"

    def test_get_worker_export(self, mock_execution_function, mock_stop_function):
        """Test that worker export is returned"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        worker_export = agent.get_worker_export()

        # worker_export is a FastAPI app, not a function
        assert hasattr(worker_export, "get")
        assert hasattr(worker_export, "post")

    @patch("agent_sdk.agent.FASTAPI_AVAILABLE", False)
    def test_agent_without_fastapi(self, mock_execution_function, mock_stop_function):
        """Test agent initialization when FastAPI is not available"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        # Should not raise an error
        assert agent.app is None

    @patch("agent_sdk.agent.FASTAPI_AVAILABLE", True)
    def test_agent_with_fastapi(self, mock_execution_function, mock_stop_function):
        """Test agent initialization when FastAPI is available"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        # Should create FastAPI app
        assert agent.app is not None

    def test_agent_dict_style_initialization(
        self, mock_execution_function, mock_stop_function
    ):
        """Test agent initialization with dict-style parameters"""
        params = {
            "execution_function": mock_execution_function,
            "stop_function": mock_stop_function,
            "title": "Test Agent",
            "description": "A test agent",
        }

        agent = Agent(**params)

        assert agent.execution_function == mock_execution_function
        assert agent.stop_function == mock_stop_function
        assert agent.config.title == "Test Agent"
        assert agent.config.description == "A test agent"


class TestAgentIntegration:
    """Integration tests for the Agent class"""

    def test_full_agent_workflow(self):
        """Test a complete agent workflow"""

        def execution_func(request: AgentRequest) -> AgentResponse:
            return AgentResponse(
                success=True, data={"processed": True, "session": request.sessionId}
            )

        def stop_func(request: AgentRequest) -> AgentResponse:
            return AgentResponse(success=True, data={"cleaned_up": True})

        agent = Agent(execution_function=execution_func, stop_function=stop_func)

        # Test execution
        exec_result = agent.process_request(
            session_id=123,
            session_wallet_address="0x1234567890abcdef",
            command="execute",
        )

        assert exec_result["success"] is True
        assert exec_result["data"]["processed"] is True
        assert exec_result["data"]["session"] == 123

        # Test stop
        stop_result = agent.stop_function(
            AgentRequest(
                sessionId=123,
                sessionWalletAddress="0x1234567890abcdef",
                otherParameters={},
            )
        )

        assert stop_result.success is True
        assert stop_result.data["cleaned_up"] is True


class TestAgentLambdaHandler:
    """Test cases for Lambda handler functionality"""

    @pytest.fixture
    def mock_execution_function(self):
        """Mock execution function for testing"""

        def mock_func(request: AgentRequest) -> AgentResponse:
            return AgentResponse(success=True, data={"message": "test"})

        return mock_func

    @pytest.fixture
    def mock_stop_function(self):
        """Mock stop function for testing"""

        def mock_func(request: AgentRequest) -> AgentResponse:
            return AgentResponse(success=True, data={"cleanup": "done"})

        return mock_func

    @pytest.fixture
    def mock_health_function(self):
        """Mock health function for testing"""

        def mock_func():
            return {"status": "healthy", "version": "1.0.0"}

        return mock_func

    def test_lambda_handler_http_event(
        self, mock_execution_function, mock_stop_function
    ):
        """Test Lambda handler with HTTP event (should use Mangum)"""
        with patch("agent_sdk.agent.FASTAPI_AVAILABLE", True):
            agent = Agent(
                execution_function=mock_execution_function,
                stop_function=mock_stop_function,
            )

            # Mock the Mangum handler
            mock_mangum_response = {"statusCode": 200, "body": '{"success": true}'}
            agent.lambda_handler = MagicMock(return_value=mock_mangum_response)

            http_event = {
                "httpMethod": "POST",
                "path": "/execute",
                "body": '{"sessionId": 123, "sessionWalletAddress": "0x123"}',
                "headers": {"Content-Type": "application/json"},
            }

            result = agent.lambda_handler_func(http_event, {})

            assert result == mock_mangum_response
            agent.lambda_handler.assert_called_once_with(http_event, {})

    def test_lambda_handler_direct_invocation_execute(
        self, mock_execution_function, mock_stop_function
    ):
        """Test Lambda handler with direct invocation for execute command"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        event = {
            "body": json.dumps(
                {"sessionId": 123, "sessionWalletAddress": "0x1234567890abcdef"}
            ),
            "rawPath": "/execute",
        }

        result = agent.lambda_handler_func(event, {})

        assert result["statusCode"] == 200
        response_body = json.loads(result["body"])
        assert response_body["success"] is True

    def test_lambda_handler_direct_invocation_health(
        self, mock_execution_function, mock_stop_function, mock_health_function
    ):
        """Test Lambda handler with health command"""
        agent = Agent(
            execution_function=mock_execution_function,
            stop_function=mock_stop_function,
            health_check_function=mock_health_function,
        )

        event = {"body": "{}", "rawPath": "/health"}

        result = agent.lambda_handler_func(event, {})

        assert result["statusCode"] == 200
        response_body = json.loads(result["body"])
        assert response_body["status"] == "healthy"

    def test_lambda_handler_missing_parameters(
        self, mock_execution_function, mock_stop_function
    ):
        """Test Lambda handler with missing required parameters"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        event = {
            "body": json.dumps({}),  # Missing sessionId and sessionWalletAddress
            "rawPath": "/execute",
        }

        result = agent.lambda_handler_func(event, {})

        assert result["statusCode"] == 400
        assert "sessionId" in result["body"]

    def test_lambda_handler_base64_encoded_body(
        self, mock_execution_function, mock_stop_function
    ):
        """Test Lambda handler with base64 encoded body"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        body_data = {"sessionId": 123, "sessionWalletAddress": "0x123"}
        encoded_body = base64.b64encode(json.dumps(body_data).encode()).decode()

        event = {"body": encoded_body, "isBase64Encoded": True, "rawPath": "/execute"}

        result = agent.lambda_handler_func(event, {})

        assert result["statusCode"] == 200

    def test_lambda_handler_error_handling(self, mock_stop_function):
        """Test Lambda handler error handling"""

        def error_function(request: AgentRequest) -> AgentResponse:
            raise Exception("Test error")

        agent = Agent(
            execution_function=error_function, stop_function=mock_stop_function
        )

        event = {
            "body": json.dumps({"sessionId": 123, "sessionWalletAddress": "0x123"}),
            "rawPath": "/execute",
        }

        result = agent.lambda_handler_func(event, {})

        assert result["statusCode"] == 500
        assert "Internal server error" in result["body"]

    def test_lambda_handler_delete_stop_method(
        self, mock_execution_function, mock_stop_function
    ):
        """Test Lambda handler with DELETE method for stop command"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        event = {
            "httpMethod": "DELETE",
            "body": json.dumps({"sessionId": 123, "sessionWalletAddress": "0x123"}),
            "rawPath": "/stop",
        }

        result = agent.lambda_handler_func(event, {})

        assert result["statusCode"] == 200

    def test_is_http_event(self, mock_execution_function, mock_stop_function):
        """Test _is_http_event helper method"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        # Test with httpMethod and required fields
        assert (
            agent._is_http_event({"httpMethod": "POST", "headers": {}, "path": "/test"})
            is True
        )

        # Test with httpMethod but missing required fields
        assert agent._is_http_event({"httpMethod": "POST"}) is False

        # Test with requestContext (API Gateway v2.0 format)
        assert agent._is_http_event({"requestContext": {"http": {}}}) is True

        # Test with requestContext but missing http
        assert agent._is_http_event({"requestContext": {}}) is False

        # Test without either
        assert agent._is_http_event({"body": "{}"}) is False

    def test_parse_event_body_json_string(
        self, mock_execution_function, mock_stop_function
    ):
        """Test _parse_event_body with JSON string"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        event = {"body": '{"key": "value"}'}
        result = agent._parse_event_body(event)
        assert result == {"key": "value"}

    def test_parse_event_body_invalid_json(
        self, mock_execution_function, mock_stop_function
    ):
        """Test _parse_event_body with invalid JSON"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        event = {"body": "invalid json"}
        result = agent._parse_event_body(event)
        assert result == {}

    def test_parse_event_body_dict(self, mock_execution_function, mock_stop_function):
        """Test _parse_event_body with dict body"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        event = {"body": {"key": "value"}}
        result = agent._parse_event_body(event)
        assert result == {"key": "value"}

    def test_parse_event_body_base64_error(
        self, mock_execution_function, mock_stop_function
    ):
        """Test _parse_event_body with base64 decode error"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        event = {"body": "invalid_base64", "isBase64Encoded": True}
        result = agent._parse_event_body(event)
        assert result == {}

    def test_extract_command(self, mock_execution_function, mock_stop_function):
        """Test _extract_command helper method"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        # Test normal path
        assert agent._extract_command({"rawPath": "/execute"}) == "execute"

        # Test Lambda runtime URL
        runtime_path = "/2015-03-31/functions/function/invocations/health"
        assert agent._extract_command({"rawPath": runtime_path}) == "health"

        # Test default
        assert agent._extract_command({}) == ""


class TestAgentCommandProcessing:
    """Test cases for command processing functionality"""

    @pytest.fixture
    def mock_execution_function(self):
        def mock_func(request: AgentRequest) -> AgentResponse:
            return AgentResponse(success=True, data={"executed": True})

        return mock_func

    @pytest.fixture
    def mock_stop_function(self):
        def mock_func(request: AgentRequest) -> AgentResponse:
            return AgentResponse(success=True, data={"stopped": True})

        return mock_func

    @pytest.fixture
    def mock_health_function(self):
        def mock_func():
            return {"status": "healthy"}

        return mock_func

    def test_process_request_stop_command(
        self, mock_execution_function, mock_stop_function
    ):
        """Test process_request with stop command"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        result = agent.process_request(123, "0x123", "stop")

        assert result["success"] is True
        assert result["data"]["stopped"] is True

    def test_process_request_health_command(
        self, mock_execution_function, mock_stop_function, mock_health_function
    ):
        """Test process_request with health command"""
        agent = Agent(
            execution_function=mock_execution_function,
            stop_function=mock_stop_function,
            health_check_function=mock_health_function,
        )

        result = agent.process_request(123, "0x123", "health")

        assert result["status"] == "healthy"

    def test_process_request_unknown_command(
        self, mock_execution_function, mock_stop_function
    ):
        """Test process_request with unknown command"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        result = agent.process_request(123, "0x123", "unknown")

        assert result["success"] is False
        assert "Unknown command" in result["error"]

    def test_process_request_health_without_function(
        self, mock_execution_function, mock_stop_function
    ):
        """Test process_request health command without health function"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )
        agent._health_function = None

        result = agent.process_request(123, "0x123", "health")

        # Should still return healthy since health_function method handles None case
        assert isinstance(result, dict)
        assert result["status"] == "healthy"


class TestAgentRunMethod:
    """Test cases for the run method"""

    @pytest.fixture
    def mock_execution_function(self):
        def mock_func(request: AgentRequest) -> AgentResponse:
            return AgentResponse(success=True)

        return mock_func

    @pytest.fixture
    def mock_stop_function(self):
        def mock_func(request: AgentRequest) -> AgentResponse:
            return AgentResponse(success=True)

        return mock_func

    @patch("agent_sdk.agent.FASTAPI_AVAILABLE", False)
    def test_run_without_fastapi(self, mock_execution_function, mock_stop_function):
        """Test run method when FastAPI is not available"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        # Should not raise an error, just log and return
        agent.run()

    @patch("agent_sdk.agent.FASTAPI_AVAILABLE", True)
    def test_run_without_app(self, mock_execution_function, mock_stop_function):
        """Test run method when FastAPI app is not initialized"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )
        agent.app = None

        # Should not raise an error, just log and return
        agent.run()

    @patch("agent_sdk.agent.FASTAPI_AVAILABLE", True)
    @patch("uvicorn.run")
    def test_run_with_fastapi(
        self, mock_uvicorn_run, mock_execution_function, mock_stop_function
    ):
        """Test run method with FastAPI available"""
        agent = Agent(
            execution_function=mock_execution_function, stop_function=mock_stop_function
        )

        agent.run(host="127.0.0.1", port=8080)

        mock_uvicorn_run.assert_called_once_with(agent.app, host="127.0.0.1", port=8080)


class TestAgentErrorHandling:
    """Test cases for error handling scenarios"""

    @pytest.fixture
    def mock_stop_function(self):
        def mock_func(request: AgentRequest) -> AgentResponse:
            return AgentResponse(success=True)

        return mock_func

    def test_agent_initialization_none_execution_function(self, mock_stop_function):
        """Test agent initialization with None execution function"""
        with pytest.raises(ValueError, match="execution_function is required"):
            Agent(execution_function=None, stop_function=mock_stop_function)

    def test_default_stop_function_usage(self, mock_stop_function):
        """Test that default stop function works"""

        def mock_exec(request: AgentRequest) -> AgentResponse:
            return AgentResponse(success=True)

        agent = Agent(execution_function=mock_exec, stop_function=mock_stop_function)

        # Test the actual stop function
        request = AgentRequest(
            sessionId=123, sessionWalletAddress="0x123", otherParameters={}
        )
        result = agent.stop_function(request)

        assert result.success is True

    def test_get_worker_export_without_fastapi(self, mock_stop_function):
        """Test get_worker_export when FastAPI is not available"""

        def mock_exec(request: AgentRequest) -> AgentResponse:
            return AgentResponse(success=True)

        with patch("agent_sdk.agent.FASTAPI_AVAILABLE", False):
            agent = Agent(
                execution_function=mock_exec, stop_function=mock_stop_function
            )

            result = agent.get_worker_export()

            # Should return the lambda handler function
            assert callable(result)


class TestUtilsFunctionality:
    """Test cases for utils.py functions to improve coverage"""

    @patch("agent_sdk.utils.toml.load")
    @patch("builtins.open")
    @patch("pathlib.Path.exists")
    def test_read_pyproject_config_success(
        self, mock_exists, mock_open, mock_toml_load
    ):
        """Test successful reading of pyproject.toml"""
        mock_config = {
            "project": {
                "name": "test-agent",
                "description": "Test Agent",
                "version": "2.0.0",
            }
        }
        mock_exists.return_value = True
        mock_toml_load.return_value = mock_config

        result = read_pyproject_config()

        assert result == mock_config
        mock_open.assert_called_once()
        mock_toml_load.assert_called_once()

    @patch("builtins.open", side_effect=FileNotFoundError("File not found"))
    def test_read_pyproject_config_error_fallback(self, mock_open):
        """Test error handling and fallback config in read_pyproject_config"""
        result = read_pyproject_config()

        # Should return fallback config
        assert "project" in result
        assert result["project"]["name"] == "circuit-agent"
        assert result["project"]["version"] == "1.0.0"

    @patch("builtins.open")
    @patch("toml.load", side_effect=Exception("TOML parse error"))
    def test_read_pyproject_config_toml_error(self, mock_toml_load, mock_open):
        """Test TOML parsing error handling"""
        result = read_pyproject_config()

        # Should return fallback config
        assert result["project"]["name"] == "circuit-agent"

    def test_get_agent_config_from_pyproject_with_tool_section(self):
        """Test config extraction with tool.circuit section"""
        mock_config = {
            "project": {
                "name": "default-name",
                "description": "Default Description",
                "version": "1.0.0",
            },
            "tool": {
                "circuit": {
                    "name": "Custom Agent Name",
                    "description": "Custom Agent Description",
                }
            },
        }

        with patch("agent_sdk.utils.read_pyproject_config", return_value=mock_config):
            result = get_agent_config_from_pyproject()

            # Should prefer tool.circuit values over project values
            assert result["title"] == "Custom Agent Name"
            assert result["description"] == "Custom Agent Description"
            assert result["version"] == "1.0.0"

    def test_get_agent_config_from_pyproject_without_tool_section(self):
        """Test config extraction without tool.circuit section"""
        mock_config = {
            "project": {
                "name": "project-name",
                "description": "Project Description",
                "version": "2.0.0",
            }
        }

        with patch("agent_sdk.utils.read_pyproject_config", return_value=mock_config):
            result = get_agent_config_from_pyproject()

            # Should use project values
            assert result["title"] == "project-name"
            assert result["description"] == "Project Description"
            assert result["version"] == "2.0.0"

    def test_get_agent_config_from_pyproject_minimal_config(self):
        """Test config extraction with minimal/missing data"""
        mock_config = {}

        with patch("agent_sdk.utils.read_pyproject_config", return_value=mock_config):
            result = get_agent_config_from_pyproject()

            # Should use default values
            assert result["title"] == "Circuit Agent"
            assert result["description"] == "A Circuit Agent"
            assert result["version"] == "1.0.0"
