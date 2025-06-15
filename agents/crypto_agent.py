import os
import requests
from typing import Dict, Any
from datetime import datetime

class CryptoAgent:
    """Agent for fetching information about cryptocurrencies.
    
    This agent uses the CoinGecko API to get information about cryptocurrencies
    based on the user's query.
    """
    
    def __init__(self):
        """Initialize the Crypto agent with API endpoint."""
        # CoinGecko API doesn't require an API key for basic usage
        self.api_url = "https://api.coingecko.com/api/v3"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data to get cryptocurrency information.
        
        Args:
            input_data (dict): Input data containing the user's goal
            
        Returns:
            dict: Enriched data with cryptocurrency information
        """
        print("Crypto Agent: Fetching cryptocurrency information...")
        
        # Create a copy of the input data to avoid modifying the original
        result = input_data.copy()
        
        try:
            # Extract crypto terms from the user's goal
            crypto_terms = self._extract_crypto_terms(input_data)
            
            # Get crypto information for each term
            crypto_results = {}
            for term in crypto_terms:
                crypto_info = self._get_crypto_info(term)
                crypto_results[term] = crypto_info
            
            # Add crypto data to result
            result["crypto_data"] = {
                "results": crypto_results,
                "search_terms": crypto_terms
            }
            
            print(f"Crypto Agent: Found information for {len(crypto_results)} terms")
        
        except Exception as e:
            result["crypto_data"] = {"error": f"Failed to get cryptocurrency data: {str(e)}"}
            print(f"Crypto Agent: Error - {str(e)}")
        
        return result
    
    def _extract_crypto_terms(self, input_data: Dict[str, Any]) -> list:
        """Extract cryptocurrency terms from the input data.
        
        Args:
            input_data (dict): Input data containing the user's goal
            
        Returns:
            list: List of cryptocurrency terms
        """
        crypto_terms = []
        
        # Common cryptocurrency names and symbols
        common_cryptos = {
            "bitcoin": "btc",
            "ethereum": "eth",
            "tether": "usdt",
            "binance coin": "bnb",
            "binance": "bnb",
            "cardano": "ada",
            "solana": "sol",
            "xrp": "xrp",
            "polkadot": "dot",
            "dogecoin": "doge",
            "avalanche": "avax",
            "chainlink": "link",
            "litecoin": "ltc",
            "stellar": "xlm",
            "uniswap": "uni"
        }
        
        # Extract from the user's goal
        if "goal" in input_data:
            goal = input_data["goal"].lower()
            
            # Check if the goal is related to cryptocurrencies
            crypto_keywords = [
                "crypto", "cryptocurrency", "bitcoin", "ethereum", "coin",
                "blockchain", "token", "mining", "wallet", "exchange",
                "defi", "nft", "altcoin", "stablecoin", "binance", "coinbase",
                "price", "value", "market cap", "trading", "invest"
            ]
            
            # Check if any crypto keyword is in the goal
            if any(keyword in goal for keyword in crypto_keywords):
                # Check for specific cryptocurrencies mentioned
                for crypto, symbol in common_cryptos.items():
                    if crypto in goal or symbol in goal:
                        crypto_terms.append(crypto)
                
                # If no specific cryptocurrency was found but the query is crypto-related
                if not crypto_terms and any(keyword in goal for keyword in crypto_keywords):
                    # Add bitcoin as a default if the query is about price or value
                    if any(term in goal for term in ["price", "value", "worth", "cost"]):
                        crypto_terms.append("bitcoin")
                    else:
                        # Otherwise, get top cryptocurrencies
                        crypto_terms.append("top_cryptocurrencies")
        
        # Ensure we have at least one term
        if not crypto_terms:
            crypto_terms.append("bitcoin")
        
        return crypto_terms
    
    def _get_crypto_info(self, term: str) -> Dict[str, Any]:
        """Get cryptocurrency information from the CoinGecko API.
        
        Args:
            term (str): Cryptocurrency term to search for
            
        Returns:
            dict: Cryptocurrency information
        """
        try:
            if term == "top_cryptocurrencies":
                # Get top cryptocurrencies by market cap
                response = requests.get(
                    f"{self.api_url}/coins/markets",
                    params={
                        "vs_currency": "usd",
                        "order": "market_cap_desc",
                        "per_page": 5,
                        "page": 1,
                        "sparkline": False
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "type": "top_list",
                    "data": [
                        {
                            "name": coin["name"],
                            "symbol": coin["symbol"].upper(),
                            "current_price": coin["current_price"],
                            "market_cap": coin["market_cap"],
                            "price_change_24h": coin["price_change_percentage_24h"],
                            "last_updated": coin["last_updated"]
                        }
                        for coin in data
                    ]
                }
            else:
                # Search for the specific cryptocurrency
                search_response = requests.get(
                    f"{self.api_url}/search",
                    params={"query": term}
                )
                search_response.raise_for_status()
                search_data = search_response.json()
                
                if search_data["coins"] and len(search_data["coins"]) > 0:
                    coin_id = search_data["coins"][0]["id"]
                    
                    # Get detailed information for this coin
                    detail_response = requests.get(
                        f"{self.api_url}/coins/{coin_id}",
                        params={
                            "localization": False,
                            "tickers": False,
                            "market_data": True,
                            "community_data": False,
                            "developer_data": False,
                            "sparkline": False
                        }
                    )
                    detail_response.raise_for_status()
                    coin_data = detail_response.json()
                    
                    return {
                        "type": "single_coin",
                        "name": coin_data["name"],
                        "symbol": coin_data["symbol"].upper(),
                        "description": coin_data["description"]["en"].split("\n")[0] if coin_data["description"]["en"] else "No description available",
                        "current_price": coin_data["market_data"]["current_price"]["usd"],
                        "market_cap": coin_data["market_data"]["market_cap"]["usd"],
                        "price_change_24h": coin_data["market_data"]["price_change_percentage_24h"],
                        "price_change_7d": coin_data["market_data"]["price_change_percentage_7d"],
                        "price_change_30d": coin_data["market_data"]["price_change_percentage_30d"],
                        "all_time_high": {
                            "price": coin_data["market_data"]["ath"]["usd"],
                            "date": coin_data["market_data"]["ath_date"]["usd"]
                        },
                        "last_updated": coin_data["last_updated"]
                    }
                else:
                    return {"error": f"No cryptocurrency found for '{term}'"}
        
        except requests.exceptions.RequestException as e:
            # If the API is rate limited or unavailable, return mock data
            print(f"Crypto Agent: API error - {str(e)}. Using mock data.")
            return self._get_mock_crypto_data(term)
    
    def _get_mock_crypto_data(self, term: str) -> Dict[str, Any]:
        """Generate mock cryptocurrency data for testing.
        
        Args:
            term (str): Cryptocurrency term
            
        Returns:
            dict: Mock cryptocurrency data
        """
        current_time = datetime.utcnow().isoformat()
        
        if term == "top_cryptocurrencies":
            return {
                "type": "top_list",
                "data": [
                    {
                        "name": "Bitcoin",
                        "symbol": "BTC",
                        "current_price": 50000.0,
                        "market_cap": 950000000000,
                        "price_change_24h": 2.5,
                        "last_updated": current_time
                    },
                    {
                        "name": "Ethereum",
                        "symbol": "ETH",
                        "current_price": 3000.0,
                        "market_cap": 350000000000,
                        "price_change_24h": 1.8,
                        "last_updated": current_time
                    },
                    {
                        "name": "Tether",
                        "symbol": "USDT",
                        "current_price": 1.0,
                        "market_cap": 80000000000,
                        "price_change_24h": 0.01,
                        "last_updated": current_time
                    },
                    {
                        "name": "Binance Coin",
                        "symbol": "BNB",
                        "current_price": 400.0,
                        "market_cap": 65000000000,
                        "price_change_24h": 3.2,
                        "last_updated": current_time
                    },
                    {
                        "name": "Cardano",
                        "symbol": "ADA",
                        "current_price": 2.0,
                        "market_cap": 60000000000,
                        "price_change_24h": -1.5,
                        "last_updated": current_time
                    }
                ],
                "note": "This is mock data for testing purposes"
            }
        elif term.lower() == "bitcoin":
            return {
                "type": "single_coin",
                "name": "Bitcoin",
                "symbol": "BTC",
                "description": "Bitcoin is a decentralized digital currency, without a central bank or single administrator, that can be sent from user to user on the peer-to-peer bitcoin network without the need for intermediaries.",
                "current_price": 50000.0,
                "market_cap": 950000000000,
                "price_change_24h": 2.5,
                "price_change_7d": 5.2,
                "price_change_30d": 10.8,
                "all_time_high": {
                    "price": 69000.0,
                    "date": "2021-11-10T00:00:00Z"
                },
                "last_updated": current_time,
                "note": "This is mock data for testing purposes"
            }
        elif term.lower() == "ethereum":
            return {
                "type": "single_coin",
                "name": "Ethereum",
                "symbol": "ETH",
                "description": "Ethereum is a decentralized, open-source blockchain with smart contract functionality. Ether is the native cryptocurrency of the platform.",
                "current_price": 3000.0,
                "market_cap": 350000000000,
                "price_change_24h": 1.8,
                "price_change_7d": 4.5,
                "price_change_30d": 9.2,
                "all_time_high": {
                    "price": 4800.0,
                    "date": "2021-11-08T00:00:00Z"
                },
                "last_updated": current_time,
                "note": "This is mock data for testing purposes"
            }
        else:
            return {
                "type": "single_coin",
                "name": f"Mock {term.capitalize()}",
                "symbol": term[:3].upper(),
                "description": f"This is a mock description for {term}.",
                "current_price": 100.0,
                "market_cap": 10000000000,
                "price_change_24h": 1.0,
                "price_change_7d": 2.0,
                "price_change_30d": 5.0,
                "all_time_high": {
                    "price": 200.0,
                    "date": "2022-01-01T00:00:00Z"
                },
                "last_updated": current_time,
                "note": "This is mock data for testing purposes"
            }