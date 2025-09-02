"""
Request type definitions with conditional shapes based on network.

This module provides request models that adapt their required fields based
on the target network, providing type safety while maintaining flexibility.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AddLogRequest(BaseModel):
    """
    Message request for send_log function.

    Used to send timeline logs that show up in session traces and UIs for
    observability, human-in-the-loop reviews, and debugging.

    Attributes:
        type: Message type for categorization. Available options:
            • "observe"  - General observations and status updates
            • "validate" - Validation checks and confirmations
            • "reflect"  - Analysis and reasoning about actions
            • "error"    - Error logs and failures
            • "warning"  - Warnings and potential issues
        short_message: Brief message content (max 250 characters)

    Examples:
        ```python
        # Status observation
        sdk.send_log({
            "type": "observe",
            "short_message": "Starting swap operation"
        })

        # Validation result
        sdk.send_log({
            "type": "validate",
            "short_message": "Confirmed sufficient balance"
        })

        # Error reporting
        sdk.send_log({
            "type": "error",
            "short_message": "Transaction failed: insufficient gas"
        })
        ```
    """

    type: Literal["observe", "validate", "reflect", "error", "warning"] = Field(
        ..., description="Type of log for categorization"
    )
    short_message: str = Field(..., description="Brief message content", max_length=250)

    model_config = ConfigDict(extra="forbid")


class EthereumSignRequest(BaseModel):
    """
    Ethereum-specific transaction request.

    This request type supports all standard EVM transaction parameters including
    gas optimization, fee strategies, and transaction control options.

    Attributes:
        to_address: Recipient address in hex format (0x...)
        data: Transaction data in hex format (0x...)
        value: Transaction value in wei as string
        gas: Optional gas limit for the transaction
        max_fee_per_gas: Optional max fee per gas in wei as string
        max_priority_fee_per_gas: Optional max priority fee per gas in wei as string
        nonce: Optional nonce for the transaction
        enforce_transaction_success: Optional flag to enforce transaction success
    """

    to_address: str = Field(
        ...,
        description="Recipient address in hex format",
        pattern=r"^0x[a-fA-F0-9]{40}$",
    )
    data: str = Field(
        ..., description="Transaction data in hex format", pattern=r"^0x[a-fA-F0-9]*$"
    )
    value: str = Field(..., description="Transaction value in wei as string")
    gas: int | None = Field(None, description="Optional gas limit for the transaction")
    max_fee_per_gas: str | None = Field(
        None, description="Optional max fee per gas in wei as string"
    )
    max_priority_fee_per_gas: str | None = Field(
        None, description="Optional max priority fee per gas in wei as string"
    )
    nonce: int | None = Field(None, description="Optional nonce for the transaction")
    enforce_transaction_success: bool | None = Field(
        None,
        description="Optional flag to enforce transaction success, if set to true, failed tx simulations will be ignored",
    )

    model_config = ConfigDict(extra="forbid")


class SolanaSignRequest(BaseModel):
    """Solana-specific transaction request."""

    hex_transaction: str = Field(
        ...,
        alias="hexTransaction",
        description="Serialized VersionedTransaction as hex string",
    )

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class SignAndSendRequest(BaseModel):
    """
    Main sign_and_send request type with network-specific conditional shapes.

    The request shape changes based on the network field:
    - For ethereum:chainId networks: requires EthereumSignRequest fields
    - For solana network: requires SolanaSignRequest fields

    Attributes:
        network: Target network ("ethereum:chainId" or "solana")
        message: Optional short message attached to the transaction
        request: Network-specific transaction details

    Example:
        ```python
        # Ethereum transaction with basic parameters
        sdk.sign_and_send({
            "network": "ethereum:1",
            "message": "Token transfer",
            "request": {
                "to_address": "0x742d35cc6634C0532925a3b8D65e95f32B6b5582",
                "data": "0xa9059cbb...",  # encoded transfer()
                "value": "0"
            }
        })

        # Ethereum transaction with advanced parameters
        sdk.sign_and_send({
            "network": "ethereum:42161",  # Arbitrum
            "message": "Optimized swap",
            "request": {
                "to_address": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
                "data": "0x38ed1739...",  # swapExactTokensForTokens
                "value": "0",
                "gas": 300000,
                "max_fee_per_gas": "20000000000",  # 20 gwei
                "max_priority_fee_per_gas": "2000000000",  # 2 gwei
                "nonce": 42,
                "enforce_transaction_success": True
            }
        })

        # Solana transaction
        sdk.sign_and_send({
            "network": "solana",
            "message": "SOL transfer",
            "request": {
                "hex_transaction": "010001030a0b..."
            }
        })
        ```
    """

    network: str = Field(..., description="Target network (ethereum:chainId or solana)")
    message: str | None = Field(
        None,
        description="Optional short message attached to the transaction",
        max_length=250,
    )
    request: EthereumSignRequest | SolanaSignRequest = Field(
        ..., description="Network-specific transaction details"
    )

    @field_validator("network")
    @classmethod
    def validate_network(cls, v: str) -> str:
        """Validate network format."""
        if v == "solana":
            return v
        if v.startswith("ethereum:"):
            try:
                chain_id = int(v.split(":")[1])
                if chain_id <= 0:
                    raise ValueError("Chain ID must be positive")
                return v
            except (IndexError, ValueError):
                raise ValueError(
                    "Invalid ethereum network format. Use ethereum:chainId"
                ) from None
        raise ValueError("Network must be 'solana' or 'ethereum:chainId'")

    @model_validator(mode="after")
    def validate_request_matches_network(self) -> "SignAndSendRequest":
        """Ensure request type matches network."""
        if self.network == "solana":
            if not isinstance(self.request, SolanaSignRequest):
                raise ValueError("Solana network requires SolanaSignRequest")
        elif self.network.startswith("ethereum:"):
            if not isinstance(self.request, EthereumSignRequest):
                raise ValueError("Ethereum network requires EthereumSignRequest")

        return self

    model_config = ConfigDict(extra="forbid")


class EvmMessageSignRequest(BaseModel):
    """EVM message signing request."""

    messageType: Literal["eip712", "eip191"]
    data: dict  # Will contain either EIP712 or EIP191 structure
    chainId: int
