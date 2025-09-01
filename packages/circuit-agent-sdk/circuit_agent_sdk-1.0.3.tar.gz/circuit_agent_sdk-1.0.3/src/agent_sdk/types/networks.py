"""
Network type definitions and guard functions for the Agent SDK.

This module provides type-safe network definitions and utilities for working
with different blockchain networks in a unified way.
"""

from typing import Literal

# Network type definition matching TypeScript exactly
Network = str | Literal["solana"]  # This will be constrained by validation


def is_ethereum_network(network: str) -> bool:
    """
    Type guard to check if network is Ethereum-based.

    Args:
        network: Network string to check

    Returns:
        True if network follows ethereum:chainId format

    Example:
        >>> is_ethereum_network("ethereum:1")
        True
        >>> is_ethereum_network("ethereum:42161")
        True
        >>> is_ethereum_network("solana")
        False
    """
    return network.startswith("ethereum:")


def is_solana_network(network: str) -> bool:
    """
    Type guard to check if network is Solana.

    Args:
        network: Network string to check

    Returns:
        True if network is "solana"

    Example:
        >>> is_solana_network("solana")
        True
        >>> is_solana_network("ethereum:1")
        False
    """
    return network == "solana"


def get_chain_id_from_network(network: str) -> int:
    """
    Extract chain ID from Ethereum network string.

    Args:
        network: Ethereum network string in format "ethereum:chainId"

    Returns:
        Chain ID as integer

    Raises:
        ValueError: If network is not a valid Ethereum network string

    Example:
        >>> get_chain_id_from_network("ethereum:1")
        1
        >>> get_chain_id_from_network("ethereum:42161")
        42161
    """
    if not is_ethereum_network(network):
        raise ValueError(f"Invalid Ethereum network format: {network}")

    try:
        chain_id = int(network.split(":")[1])
        return chain_id
    except (IndexError, ValueError) as e:
        raise ValueError(f"Invalid Ethereum network format: {network}") from e
