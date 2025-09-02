"""
Main AgentSdk class with simplified API surface.

This module provides the primary AgentSdk class that serves as the main entry point
for all agent operations. It offers a clean, type-safe interface with just two
core methods that cover the majority of agent interactions.
"""

from typing import Any

from .client import APIClient
from .types import (
    AddLogRequest,
    EthereumSignRequest,
    EvmMessageSignRequest,
    EvmMessageSignResponse,
    SDKConfig,
    SignAndSendRequest,
    SignAndSendResponse,
    SolanaSignRequest,
    get_chain_id_from_network,
    is_ethereum_network,
    is_solana_network,
)


class AgentSdk:
    """
    Main SDK entrypoint used by agents to interact with the Circuit backend.

    Provides a minimal sdk with three core methods that cover the
    majority of agent interactions:

    - send_log() — emit timeline logs for observability and UX
    - sign_message() — sign EIP712 and EIP191 messages on EVM networks
    - sign_and_send() — sign and broadcast transactions across networks
    """

    def __init__(self, config: SDKConfig) -> None:
        """
        Create a new AgentSdk instance.

        Args:
            config: SDK configuration
                - session_id: Numeric session identifier that scopes auth and actions
                - verbose: When True, prints detailed request/response logs
                - testing: When True, short-circuits network calls with mock values
                - base_url: Override API base URL (detected automatically otherwise)

        Example:
            ```python
            sdk = AgentSdk(SDKConfig(session_id=42, verbose=True))
            ```
        """
        self.config = config
        self.client = APIClient(config)
        # Pass the sign_and_send method to utils to avoid circular dependency
        # self.utils = AgentUtils(self.client, self.config, self.sign_and_send)

    def _mask_sensitive_data(self, data: Any) -> Any:
        """
        Mask sensitive information in data structures.

        Args:
            data: Data to mask

        Returns:
            Data with sensitive information masked
        """
        if isinstance(data, dict):
            masked_data = {}
            for key, value in data.items():
                if key.lower() in ["authorization", "x-api-key", "bearer", "token"]:
                    if isinstance(value, str) and len(value) > 8:
                        # Show first 8 characters and mask the rest
                        masked_data[key] = f"{value[:8]}...***MASKED***"
                    else:
                        masked_data[key] = "***MASKED***"
                else:
                    masked_data[key] = self._mask_sensitive_data(value)
            return masked_data
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        else:
            return data

    def _log(self, log: str, data: Any = None) -> None:
        """Log debug information when verbose mode is enabled."""
        if self.config.verbose:
            log_message = f"[AGENT SDK DEBUG] {log}"
            if data is not None:
                import json

                masked_data = self._mask_sensitive_data(data)
                log_message += f" {json.dumps(masked_data, indent=2, default=str)}"
            print(log_message)

    def send_log(self, log: AddLogRequest | dict) -> None:
        """
        Add a log to the agent timeline.

        Logs show up in session traces and UIs and are useful for observability,
        human-in-the-loop reviews, and debugging.

        Args:
            log: Timeline message with the following fields:
                - type: Message type for categorization. Options:
                    • "observe"  - General observations and status updates
                    • "validate" - Validation checks and confirmations
                    • "reflect"  - Analysis and reasoning about actions
                    • "error"    - Error logs and failures
                    • "warning"  - Warnings and potential issues
                - short_message: Brief, human-readable message (automatically truncated to 250 characters if longer)

        Raises:
            requests.RequestException: If the backend request fails

        Examples:
            ```python
            # Status observation
            sdk.send_log({
                "type": "observe",
                "short_message": "Starting swap operation"
            })
            # Validation check
            sdk.send_log({
                "type": "validate",
                "short_message": "Confirmed sufficient balance: 1.5 ETH"
            })
            # Error reporting
            sdk.send_log({
                "type": "error",
                "short_message": "Transaction failed: insufficient gas"
            })
            # Long logs are automatically truncated to 250 characters (when using dict input)
            sdk.send_log({
                "type": "observe",
                "short_message": "This is a very long message that will be automatically truncated if it exceeds 250 characters to prevent validation failures and ensure the message gets through successfully"
            })
            # Note: Pydantic models must be valid when created (max 250 chars)
            # Dict inputs are automatically truncated by the SDK
            ```
        """
        # Handle both dict and Pydantic model inputs (like TypeScript SDK)
        if isinstance(log, dict):
            # Automatically truncate logs that exceed 250 characters before validation
            if "short_message" in log and len(log["short_message"]) > 250:
                original_message = log["short_message"]
                truncated_message = original_message[:247] + "..."
                self._log(
                    f"Message truncated from {len(original_message)} to 250 characters"
                )
                log["short_message"] = truncated_message

            # Convert dict to Pydantic model for validation and type safety
            message_obj = AddLogRequest(**log)
        else:
            # For Pydantic models, we need to handle truncation differently
            # since validation already happened. We'll create a new dict and truncate it.
            message_dict = log.model_dump()

            if len(message_dict["short_message"]) > 250:
                original_message = message_dict["short_message"]
                truncated_message = original_message[:247] + "..."
                self._log(
                    f"Message truncated from {len(original_message)} to 250 characters"
                )
                message_dict["short_message"] = truncated_message
                # Create a new Pydantic model with the truncated log
                message_obj = AddLogRequest(**message_dict)
            else:
                message_obj = log

        self._log("ADD_LOG", message_obj.model_dump())

        # Convert to the internal logs format
        logs_request = [
            {"type": message_obj.type, "shortMessage": message_obj.short_message}
        ]

        self._send_logs(logs_request)

    def sign_and_send(self, request: SignAndSendRequest | dict) -> SignAndSendResponse:
        """
        Sign and broadcast a transaction on the specified network.

        The backend performs validation and policy checks; you only need to provide
        the minimal request shape for the selected network.

        Args:
            request: Network-specific transaction input
                - network: "solana" or "ethereum:chainId"
                - message: Optional human-readable context message (short), stored with the transaction
                - request: Transaction payload
                  - For Ethereum: {"to_address": "0x...", "data": "0x...", "value": "wei_amount"}
                    - to_address: recipient contract or EOA as hex string
                    - data: calldata as hex string (use "0x" for simple transfers)
                    - value: stringified wei amount
                    - gas: optional gas limit for the transaction
                    - max_fee_per_gas: optional max fee per gas in wei as string
                    - max_priority_fee_per_gas: optional max priority fee per gas in wei as string
                    - nonce: optional nonce for the transaction
                    - enforce_transaction_success: optional flag to enforce transaction success
                  - For Solana: {"hex_transaction": "hex_string"}
                    - hex_transaction: serialized VersionedTransaction as hex string

        Returns:
            SignAndSendResponse with internal_transaction_id, tx_hash, and optional transaction_url

        Raises:
            ValueError: If the network is unsupported or request validation fails
            requests.RequestException: If the backend rejects the request

        Example:
            ```python
            # Ethereum (Arbitrum) native transfer with gas optimization
            sdk.sign_and_send({
                "network": "ethereum:42161",
                "request": {
                    "to_address": "0xabc...",
                    "data": "0x",
                    "value": "1000000000000000",  # 0.001 ETH
                    "gas": 21000,
                    "max_fee_per_gas": "20000000000",  # 20 gwei
                    "max_priority_fee_per_gas": "2000000000"  # 2 gwei
                },
                "message": "Self-transfer demo"
            })

            # Solana
            sdk.sign_and_send({
                "network": "solana",
                "request": {"hex_transaction": "01ab..."},
                "message": "Swap with Jupiter"
            })
            ```
        """
        # Handle both dict and Pydantic model inputs (like TypeScript SDK)
        if isinstance(request, dict):
            # Convert dict to Pydantic model for validation and type safety
            request_obj = SignAndSendRequest(**request)
        else:
            request_obj = request
        self._log(
            "SIGN_AND_SEND",
            {"request": request_obj.model_dump(), "testing_mode": self.config.testing},
        )

        if self.config.testing:
            return SignAndSendResponse(
                internal_transaction_id=123,
                tx_hash=(
                    "0xTEST"
                    if is_ethereum_network(request_obj.network)
                    else "TEST_SOL_TX"
                ),
                transaction_url=None,
            )

        if is_ethereum_network(request_obj.network):
            chain_id = get_chain_id_from_network(request_obj.network)

            # Ensure we have an Ethereum request
            if not isinstance(request_obj.request, EthereumSignRequest):
                raise ValueError("Ethereum network requires EthereumSignRequest")

            # Build request payload, only including non-None values
            payload = {
                "chainId": chain_id,
                "toAddress": request_obj.request.to_address,
                "data": request_obj.request.data,
                "valueWei": request_obj.request.value,  # Map 'value' to 'valueWei'
            }

            if request_obj.message is not None:
                payload["message"] = request_obj.message
            # Only add optional fields if they have values
            if request_obj.request.gas is not None:
                payload["gas"] = request_obj.request.gas
            if request_obj.request.max_fee_per_gas is not None:
                payload["maxFeePerGas"] = request_obj.request.max_fee_per_gas
            if request_obj.request.max_priority_fee_per_gas is not None:
                payload["maxPriorityFeePerGas"] = (
                    request_obj.request.max_priority_fee_per_gas
                )
            if request_obj.request.nonce is not None:
                payload["nonce"] = request_obj.request.nonce
            if request_obj.request.enforce_transaction_success is not None:
                payload["enforceTransactionSuccess"] = (
                    request_obj.request.enforce_transaction_success
                )

            return self._handle_evm_transaction(payload)

        if is_solana_network(request_obj.network):
            # Ensure we have a Solana request
            if not isinstance(request_obj.request, SolanaSignRequest):
                raise ValueError("Solana network requires SolanaSignRequest")

            return self._handle_solana_transaction(
                {
                    "hexTransaction": request_obj.request.hex_transaction,
                    "message": request_obj.message,
                }
            )

        raise ValueError(f"Unsupported network: {request_obj.network}")

    def sign_message(
        self, request: EvmMessageSignRequest | dict
    ) -> EvmMessageSignResponse:
        """
        Sign a message on an EVM network.

        Args:
            request: EVM message signing input
                - messageType: "eip712" or "eip191"
                - chainId: Ethereum chain ID
                - data: Message data structure

        Returns:
            EvmMessageSignResponse with signature components
        """
        if isinstance(request, dict):
            request_obj = EvmMessageSignRequest(**request)
        else:
            request_obj = request

        self._log(
            "SIGN_MESSAGE",
            {"request": request_obj.model_dump(), "testing_mode": self.config.testing},
        )

        if self.config.testing:
            return EvmMessageSignResponse(
                status=200,
                v=27,
                r="0xTEST_R",
                s="0xTEST_S",
                formattedSignature="0xTEST_SIGNATURE",
                type="evm",
            )

        # Call the message signing endpoint
        response = self.client.post("/v1/messages/evm", request_obj.model_dump())
        return EvmMessageSignResponse(**response)

    # =====================
    # Private Implementation Methods (migrated from AgentToolset)
    # =====================

    def _handle_evm_transaction(self, request: dict[str, Any]) -> SignAndSendResponse:
        """Handle EVM transaction signing and broadcasting."""
        # 1) Sign the transaction
        sign_response = self.client.post("/v1/transactions/evm", request)

        # 2) Broadcast the transaction
        transaction_id = sign_response["internalTransactionId"]
        broadcast_response = self.client.post(
            f"/v1/transactions/evm/{transaction_id}/broadcast"
        )

        return SignAndSendResponse(
            internal_transaction_id=transaction_id,
            tx_hash=broadcast_response["txHash"],
            transaction_url=broadcast_response.get("transactionUrl"),
        )

    def _handle_solana_transaction(
        self, request: dict[str, Any]
    ) -> SignAndSendResponse:
        """Handle Solana transaction signing and broadcasting."""
        # 1) Sign the transaction
        sign_response = self.client.post("/v1/transactions/solana", request)

        # 2) Broadcast the transaction
        transaction_id = sign_response["internalTransactionId"]
        broadcast_response = self.client.post(
            f"/v1/transactions/solana/{transaction_id}/broadcast"
        )

        return SignAndSendResponse(
            internal_transaction_id=transaction_id,
            tx_hash=broadcast_response["txHash"],
            transaction_url=broadcast_response.get("transactionUrl"),
        )

    def _send_logs(self, logs: list) -> dict[str, Any]:
        """Send logs to the agent timeline (migrated from AgentToolset)."""
        if self.config.testing:
            print(f"Logs added successfully (TESTING): {logs}")
            return {
                "status": 200,
                "message": "Logs added successfully (TESTING)",
            }

        return self.client.post("/v1/logs", logs)

    # No legacy methods - clean major version!
