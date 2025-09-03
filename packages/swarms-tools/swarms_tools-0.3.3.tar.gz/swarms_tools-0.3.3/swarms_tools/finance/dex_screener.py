"""
DexScreener API Client

This module provides a Python interface for the DexScreener API, allowing users to fetch
token profiles, pairs, and perform token-related searches.
"""

import httpx
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from loguru import logger

from swarms_tools.utils.formatted_string import (
    format_object_to_string,
)

# Constants
BASE_URL = "https://api.dexscreener.com"
PAIRS_RATE_LIMIT = 300  # requests per minute
PROFILES_RATE_LIMIT = 60  # requests per minute


@dataclass
class TokenInfo:
    """Token information data structure."""

    address: str
    name: str
    symbol: str


@dataclass
class Liquidity:
    """Liquidity information data structure."""

    usd: float
    base: float
    quote: float


@dataclass
class Website:
    """Website information data structure."""

    url: str


@dataclass
class Social:
    """Social media information data structure."""

    platform: str
    handle: str


@dataclass
class TokenPairInfo:
    """Detailed token pair information data structure."""

    chain_id: str
    dex_id: str
    url: str
    pair_address: str
    labels: Optional[List[str]]
    base_token: TokenInfo
    quote_token: TokenInfo
    price_native: str
    price_usd: Optional[str]
    liquidity: Optional[Liquidity]
    fdv: Optional[float]
    market_cap: Optional[float]
    pair_created_at: Optional[int]


class DexScreenerAPIError(Exception):
    """Base exception for DexScreener API errors."""

    pass


class RateLimitExceeded(DexScreenerAPIError):
    """Raised when rate limit is exceeded."""

    pass


class DexScreenerAPI:
    """
    DexScreener API client for accessing token and pair information.

    This class provides methods to interact with the DexScreener API endpoints
    while handling rate limiting and error cases.
    """

    def __init__(self, timeout: int = 10):
        """
        Initialize the DexScreener API client.

        Args:
            timeout (int): Request timeout in seconds
        """
        self.client = httpx.Client(timeout=timeout)
        logger.info("DexScreener API client initialized")

    def get_latest_token_profiles(self) -> Dict[str, Any]:
        """
        Get the latest token profiles.

        Returns:
            Dict[str, Any]: Latest token profiles data

        Raises:
            DexScreenerAPIError: If the API request fails
            RateLimitExceeded: If rate limit is exceeded
        """
        try:
            response = self.client.get(
                f"{BASE_URL}/token-profiles/latest/v1"
            )
            response.raise_for_status()
            logger.debug("Successfully fetched latest token profiles")
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitExceeded(
                    "Token profiles rate limit exceeded"
                )
            logger.error(f"Failed to fetch token profiles: {str(e)}")
            raise DexScreenerAPIError(f"API request failed: {str(e)}")

    def get_latest_token_boosts(self) -> Dict[str, Any]:
        """
        Get the latest token boosts.

        Returns:
            Dict[str, Any]: Latest token boosts data

        Raises:
            DexScreenerAPIError: If the API request fails
            RateLimitExceeded: If rate limit is exceeded
        """
        try:
            response = self.client.get(
                f"{BASE_URL}/token-boosts/latest/v1"
            )
            response.raise_for_status()
            logger.debug("Successfully fetched latest token boosts")
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitExceeded(
                    "Token boosts rate limit exceeded"
                )
            logger.error(f"Failed to fetch token boosts: {str(e)}")
            raise DexScreenerAPIError(f"API request failed: {str(e)}")

    def get_pair(self, chain_id: str, pair_id: str) -> TokenPairInfo:
        """
        Get information about a specific trading pair.

        Args:
            chain_id (str): The blockchain network ID
            pair_id (str): The trading pair ID

        Returns:
            TokenPairInfo: Detailed information about the trading pair

        Raises:
            DexScreenerAPIError: If the API request fails
            RateLimitExceeded: If rate limit is exceeded
        """
        try:
            response = self.client.get(
                f"{BASE_URL}/latest/dex/pairs/{chain_id}/{pair_id}"
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("pairs"):
                logger.warning(
                    f"No pair data found for {chain_id}/{pair_id}"
                )
                return None

            pair = data["pairs"][0]
            logger.debug(
                f"Successfully fetched pair data for {chain_id}/{pair_id}"
            )

            return TokenPairInfo(
                chain_id=pair["chainId"],
                dex_id=pair["dexId"],
                url=pair["url"],
                pair_address=pair["pairAddress"],
                labels=pair.get("labels"),
                base_token=TokenInfo(**pair["baseToken"]),
                quote_token=TokenInfo(**pair["quoteToken"]),
                price_native=pair["priceNative"],
                price_usd=pair.get("priceUsd"),
                liquidity=(
                    Liquidity(**pair["liquidity"])
                    if pair.get("liquidity")
                    else None
                ),
                fdv=pair.get("fdv"),
                market_cap=pair.get("marketCap"),
                pair_created_at=pair.get("pairCreatedAt"),
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitExceeded("Pairs rate limit exceeded")
            logger.error(f"Failed to fetch pair data: {str(e)}")
            raise DexScreenerAPIError(f"API request failed: {str(e)}")

    def search_pairs(self, query: str) -> List[TokenPairInfo]:
        """
        Search for trading pairs matching the query.

        Args:
            query (str): Search query string

        Returns:
            List[TokenPairInfo]: List of matching trading pairs

        Raises:
            DexScreenerAPIError: If the API request fails
            RateLimitExceeded: If rate limit is exceeded
        """
        try:
            response = self.client.get(
                f"{BASE_URL}/latest/dex/search", params={"q": query}
            )
            response.raise_for_status()
            data = response.json()

            pairs = []
            for pair in data.get("pairs", []):
                pairs.append(
                    TokenPairInfo(
                        chain_id=pair["chainId"],
                        dex_id=pair["dexId"],
                        url=pair["url"],
                        pair_address=pair["pairAddress"],
                        labels=pair.get("labels"),
                        base_token=TokenInfo(**pair["baseToken"]),
                        quote_token=TokenInfo(**pair["quoteToken"]),
                        price_native=pair["priceNative"],
                        price_usd=pair.get("priceUsd"),
                        liquidity=(
                            Liquidity(**pair["liquidity"])
                            if pair.get("liquidity")
                            else None
                        ),
                        fdv=pair.get("fdv"),
                        market_cap=pair.get("marketCap"),
                        pair_created_at=pair.get("pairCreatedAt"),
                    )
                )

            logger.debug(
                f"Successfully searched pairs with query: {query}"
            )
            return pairs
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitExceeded("Search rate limit exceeded")
            logger.error(f"Failed to search pairs: {str(e)}")
            raise DexScreenerAPIError(f"API request failed: {str(e)}")

    def get_token_pairs(
        self, chain_id: str, token_addresses: Union[str, List[str]]
    ) -> List[TokenPairInfo]:
        """
        Get pairs information for one or multiple token addresses.

        Args:
            chain_id (str): The blockchain network ID
            token_addresses (Union[str, List[str]]): Single token address or list of addresses

        Returns:
            List[TokenPairInfo]: List of token pair information

        Raises:
            DexScreenerAPIError: If the API request fails
            RateLimitExceeded: If rate limit is exceeded
        """
        if isinstance(token_addresses, list):
            if len(token_addresses) > 30:
                raise ValueError(
                    "Maximum 30 token addresses allowed per request"
                )
            addresses = ",".join(token_addresses)
        else:
            addresses = token_addresses

        try:
            response = self.client.get(
                f"{BASE_URL}/tokens/v1/{chain_id}/{addresses}"
            )
            response.raise_for_status()
            pairs = []

            for pair in response.json():
                pairs.append(
                    TokenPairInfo(
                        chain_id=pair["chainId"],
                        dex_id=pair["dexId"],
                        url=pair["url"],
                        pair_address=pair["pairAddress"],
                        labels=pair.get("labels"),
                        base_token=TokenInfo(**pair["baseToken"]),
                        quote_token=TokenInfo(**pair["quoteToken"]),
                        price_native=pair["priceNative"],
                        price_usd=pair.get("priceUsd"),
                        liquidity=(
                            Liquidity(**pair["liquidity"])
                            if pair.get("liquidity")
                            else None
                        ),
                        fdv=pair.get("fdv"),
                        market_cap=pair.get("marketCap"),
                        pair_created_at=pair.get("pairCreatedAt"),
                    )
                )

            logger.debug(
                f"Successfully fetched token pairs for {chain_id}/{addresses}"
            )
            return pairs
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitExceeded(
                    "Token pairs rate limit exceeded"
                )
            logger.error(f"Failed to fetch token pairs: {str(e)}")
            raise DexScreenerAPIError(f"API request failed: {str(e)}")

    def __del__(self):
        """Cleanup method to close the HTTP client."""
        if hasattr(self, "client"):
            self.client.close()


# Example usage
def fetch_dex_screener_profiles():
    """
    Fetches and prints the latest token profiles from DexScreener.

    This function initializes a DexScreenerAPI instance, fetches the latest token profiles,
    and prints them in a formatted string.
    """
    dex_screener = DexScreenerAPI()
    pairs = dex_screener.get_latest_token_profiles()
    print(format_object_to_string(pairs))


def fetch_latest_token_boosts():
    """
    Fetches and prints the latest token boosts from DexScreener.

    This function initializes a DexScreenerAPI instance, fetches the latest token boosts,
    and prints them in a formatted string.
    """
    dex_screener = DexScreenerAPI()
    pairs = dex_screener.get_latest_token_boosts()
    print(format_object_to_string(pairs))


def fetch_solana_token_pairs(token_addresses: List[str]):
    """
    Fetches and prints the token pairs for Solana blockchain from DexScreener.

    Args:
        token_addresses (List[str]): A list of token addresses to fetch pairs for.

    This function initializes a DexScreenerAPI instance, fetches the token pairs for the specified
    token addresses on the Solana blockchain, and prints them in a formatted string.
    """
    chain_id = "solana"  # Replace with the actual chain ID for Solana
    dex_screener = DexScreenerAPI()
    pairs = dex_screener.get_token_pairs(chain_id, token_addresses)
    print(format_object_to_string(pairs))


# # fetch_dex_screener_profiles()
# fetch_latest_token_boosts()
# # fetch_solana_token_pairs(
# #     ["9pqmkBHY3FV2ayMAjtyrVp51jWCbDjFL7NEcPsNDpump"]
# # )
