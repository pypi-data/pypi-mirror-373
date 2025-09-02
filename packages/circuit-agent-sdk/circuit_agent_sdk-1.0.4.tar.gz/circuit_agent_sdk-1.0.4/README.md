# 🚀 Agent SDK (Python)

> **A simple Python SDK for building cross-chain agents**

[![PyPI version](https://badge.fury.io/py/circuit-agent-sdk.svg)](https://badge.fury.io/py/circuit-agent-sdk)
[![Python Version](https://img.shields.io/pypi/pyversions/circuit-agent-sdk.svg)](https://pypi.org/project/circuit-agent-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python SDK for building automated agents to deploy on Circuit. Features an incredibly simple API surface with just **2 main methods**.

> **💡 Best used with [Circuit Agents CLI](https://github.com/circuitorg/agents-cli)** - Deploy, manage, and test your agents with ease

## 📖 SDK Philosophy

This SDK is built on a **low-level first** approach:

1. **Core Functionality**: At its heart, the SDK provides `sign_and_send()` - a single, powerful method that accepts any pre-built transaction for any supported network. This gives you complete control over transaction construction.


2. **Bring Your Own Tools**: For production agents, we recommend using:
   - **Solana**: Use `solana-py`, `solders`, or `anchorpy` for transaction construction
   - **EVM**: Use `web3.py` or `eth-account` for transaction building
   - **RPC**: Make your own RPC calls for complex queries and custom needs


## ✨ Features

- **🎯 Simple API**: Only 2 main methods - `send_log()` and `sign_and_send()`
- **🔒 Type Hinting**: Network parameter determines valid request shapes automatically
- **🚀 Cross-Chain**: Unified interface for EVM and Solana networks
- **⚡ Low-Level Control**: `sign_and_send()` accepts any pre-built transaction
- **🛠️ Smart Deployment**: The agent wrapper detects its environment and exposes the necessary endpoints and handlers so you can focus on execution logic and easily test locally via our CLI tool

## 🚀 Quick Start

### Install the SDK

```bash
pip install circuit-agent-sdk
# or with uv
uv pip install circuit-agent-sdk
```

### Sample usage
>**Tip:** Use the cli tool to spin up a sample agent, simple run 'circuit agent init' and select the python option. This will give you a fully functioning agent that will send a sample message. Simply plug in your execution logic, we will handle the rest.
```python
"""
Circuit Agent - Python SDK Example

This demonstrates how to use the Circuit Agent Python SDK to create
an agent that can run locally via FastAPI and deploy to AWS Lambda.
"""

from agent_sdk import (
    Agent,
    AgentRequest,
    AgentResponse,
    AgentSdk,
    SDKConfig,
    setup_logging,
)

# Set up logging
logger = setup_logging()
logger.info("Python Agent SDK module loaded - executing main.py")


def execution_function(request: AgentRequest) -> AgentResponse:
    """
    Main execution function for the agent.

    This function demonstrates proper usage of the Circuit Agent SDK with
    the new clean API using send_log() and sign_and_send().

    Args:
        request: Validated request containing sessionId,
                sessionWalletAddress, and otherParameters

    Returns:
        AgentResponse: Validated response indicating success/failure
    """
    # Create SDK instance with the session ID from the request
    sdk = AgentSdk(
        SDKConfig(session_id=request.sessionId, verbose=True)  # Enable debug logging
    )

    try:
        # Send observation message
        sdk.send_log(
            {
                "type": "observe",
                "short_message": f"Python SDK Agent - Checking balance for {request.sessionWalletAddress[:8]}...",
            }
        )

        # Example transaction (commented out for safety)
        # result = sdk.sign_and_send({
        #     "network": "ethereum:1",
        #     "request": {
        #         "to_address": request.sessionWalletAddress,
        #         "data": "0x",
        #         "value": "100000000000000000"  # 0.1 ETH
        #     },
        #     "message": "Self-transfer demo"
        # })

        # Return success response
        return AgentResponse(success=True, message="Execution completed")

    except Exception as error:
        logger.error(f"Error in agent execution: {error}")

        try:
            # Send error message to user
            sdk.send_log(
                {
                    "type": "error",
                    "short_message": f"Agent execution error: {str(error)}",
                }
            )
        except Exception as msg_error:
            logger.error(f"Failed to send error message: {msg_error}")

        return AgentResponse(success=False, error=str(error))


def stop_function(request: AgentRequest) -> AgentResponse:
    """
    Agent stop/cleanup function.

    This function is called when an agent session is being stopped.
    Use this to perform any necessary cleanup operations.

    Args:
        request: Validated request containing sessionId, sessionWalletAddress, and otherParameters

    Returns:
        AgentResponse: Validated response indicating cleanup success/failure
    """
    # Create SDK for cleanup operations
    sdk = AgentSdk(SDKConfig(session_id=request.sessionId))

    try:
        # Notify about cleanup
        sdk.send_log(
            {
                "type": "observe",
                "short_message": f"Agent session {request.sessionId} stopping...",
            }
        )

        return AgentResponse(success=True, message="Cleanup completed")

    except Exception as error:
        logger.error(f"Error in stop function: {error}")
        return AgentResponse(success=False, error=str(error))


# NOTE: Everything below this should remain unchanged, unless you want to
# customize the agent configuration. This setup ensures you can run the agent
# locally and in the Circuit platform without any changes.

# Create the agent (configuration read from pyproject.toml)
agent = Agent(execution_function=execution_function, stop_function=stop_function)

# Export the Lambda handler for AWS deployment
handler = agent.get_lambda_handler()

# Local development server
if __name__ == "__main__":
    logger.info("Starting Circuit Agent development server...")
    logger.info(
        "The agent will automatically log available endpoints and example usage"
    )

    # Start the server for local development
    agent.run()
```

## 🎯 Core API (Only 2 Methods!)

The SDK is designed around just two main methods that cover all agent interactions:

### 1. Add Messages to Timeline

> **Use this for all agent communication and observability**

```python
sdk.send_log({
    "type": "observe",
    "short_message": "Starting swap operation"
})

# Long messages are automatically truncated to 250 characters (when using dict input)
sdk.send_log({
    "type": "observe",
    "short_message": "This is a very long message that will be automatically truncated if it exceeds 250 characters to prevent validation failures and ensure the message gets through successfully"
})

# Note: Pydantic models must be valid when created (max 250 chars)
# Dict inputs are automatically truncated by the SDK

## ✂️ Smart Message Truncation

The SDK automatically handles long messages to prevent validation failures:

```python
# Long messages are automatically truncated to 250 characters
sdk.send_log({
    "type": "error",
    "short_message": "This is a very long error message that contains a lot of details and would normally cause validation to fail because it exceeds 250 characters, but the SDK automatically truncates it and adds '...' to indicate truncation, ensuring your message gets through successfully"
})

# Result: Message is truncated to 250 chars with "..." suffix
# This prevents the common error: "String should have at most 250 characters"
```

**How it works:**
- **Dict inputs**: Automatically truncated before validation
- **Pydantic models**: Must be valid when created (max 250 chars)
- **Truncation**: Adds "..." suffix to indicate truncation
- **Logging**: Debug logs show when truncation occurs

### 2. Sign & Send Transactions

> **This is the core method for executing transactions across all supported networks**

The `sign_and_send()` method accepts **any pre-built transaction** for the target network. You have complete control over how you build these transactions.

#### Ethereum (any EVM chain)

```python
# Native ETH transfer
sdk.sign_and_send({
    "network": "ethereum:1",  # Chain ID in network string
    "request": {
        "to_address": "0x742d35cc6634C0532925a3b8D65e95f32B6b5582",
        "data": "0x",
        "value": "1000000000000000000"  # 1 ETH in wei
    },
    "message": "Sending 1 ETH"
})

# Contract interaction (e.g., ERC-20 transfer)
sdk.sign_and_send({
    "network": "ethereum:42161",  # Arbitrum
    "request": {
        "to_address": "0xTokenContract...",
        "data": "0xa9059cbb...",  # encoded transfer(address,uint256)
        "value": "0"
    },
    "message": "ERC-20 transfer"
})

# You can build the transaction data using web3.py:
from web3 import Web3
w3 = Web3()
contract = w3.eth.contract(abi=ERC20_ABI)
data = contract.encodeABI(fn_name="transfer", args=[recipient, amount])
```

#### Solana

```python
# Any Solana transaction (transfers, swaps, etc.)
sdk.sign_and_send({
    "network": "solana",
    "request": {
        "hex_transaction": "010001030a0b..."  # serialized VersionedTransaction
    },
    "message": "Solana transaction"
})

# Build transactions using solana-py or solders:
from solders.transaction import VersionedTransaction
from solders.message import Message
# ... build your transaction
tx = VersionedTransaction(message, [NullSigner(payer)])
hex_transaction = bytes(tx).hex()

# Or use our optional utilities for simple cases:
from agent_sdk.utils.solana import create_native_sol_transfer_transaction
hex_tx = create_native_sol_transfer_transaction(...)
```
