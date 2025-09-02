"""
Response type definitions for the Agent SDK.

This module provides all response models returned by SDK operations.
All models use strict Pydantic validation for type safety.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SignAndSendResponse(BaseModel):
    """
    Standard response from sign_and_send operations.

    This response is returned after successfully signing and broadcasting
    a transaction through the Circuit backend.

    Attributes:
        internal_transaction_id: Internal transaction ID for tracking
        tx_hash: Transaction hash once broadcast to the network
        transaction_url: Optional transaction URL (explorer link)

    Example:
        ```python
        response = sdk.sign_and_send({
            "network": "ethereum:1",
            "request": {"toAddress": "0x...", "data": "0x", "value": "0"}
        })
        print(f"Transaction hash: {response.tx_hash}")
        if response.transaction_url:
            print(f"View on explorer: {response.transaction_url}")
        ```
    """

    internal_transaction_id: int = Field(
        ..., description="Internal transaction ID for tracking"
    )
    tx_hash: str = Field(..., description="Transaction hash once broadcast")
    transaction_url: str | None = Field(
        None, description="Optional transaction URL (explorer link)"
    )

    model_config = ConfigDict(extra="forbid")


class EvmMessageSignResponse(BaseModel):
    """Response from EVM message signing."""

    status: int
    v: int
    r: str
    s: str
    formattedSignature: str
    type: Literal["evm"]
