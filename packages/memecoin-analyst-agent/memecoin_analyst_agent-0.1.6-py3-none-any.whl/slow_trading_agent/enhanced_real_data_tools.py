#!/usr/bin/env python3
"""
增强版真实数据查询工具
使用已验证可用的API提供完整的代币分析数据
"""

from langchain.tools import BaseTool
from typing import List
from pydantic import BaseModel, Field
import json
import requests
import re
from datetime import datetime

# 导入API配置，如果失败则使用空值
try:
    from api_config import MORALIS_API_KEY, BSCSCAN_API_KEY
except ImportError:
    MORALIS_API_KEY = ""
    BSCSCAN_API_KEY = ""

class TokenAnalysisInput(BaseModel):
    token_address: str = Field(description="The BSC token contract address")

class RealDataFetcher:
    """A synchronous client to fetch real token data using requests."""
    
    def _make_request(self, url, method="GET", params=None, headers=None):
        try:
            response = requests.request(method, url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed for {url}: {e}")
            return None

    def get_token_basic_info_moralis(self, token_address: str):
        if not MORALIS_API_KEY:
            return None
        url = f"https://deep-index.moralis.io/api/v2/erc20/metadata"
        params = {"chain": "bsc", "addresses": token_address}
        headers = {"X-API-Key": MORALIS_API_KEY, "accept": "application/json"}
        data = self._make_request(url, params=params, headers=headers)
        if isinstance(data, list) and data:
            item = data[0]
            return {
                "name": item.get("name") or "Unknown",
                "symbol": item.get("symbol") or "UNKNOWN"
            }
        return None

    def get_token_basic_info(self, token_address: str):
        # Prefer Moralis, fallback to DexScreener
        moralis_info = self.get_token_basic_info_moralis(token_address)
        if moralis_info:
            return moralis_info
        # Using DexScreener fallback
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        data = self._make_request(url)
        if data and data.get('pairs'):
            best_pair = max(data['pairs'], key=lambda p: (float(p.get('liquidity', {}).get('usd', 0)), p.get('pairCreatedAt', 0)))
            base_token_info = best_pair.get('baseToken', {})
            return {
                "name": base_token_info.get('name', 'Unknown'),
                "symbol": base_token_info.get('symbol', 'UNKNOWN'),
            }
        return {"name": "N/A", "symbol": "N/A", "error": "Failed to fetch basic info"}

    def get_token_price_data(self, token_address: str):
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        data = self._make_request(url)
        if data and data.get('pairs'):
            best_pair = max(data['pairs'], key=lambda p: float(p.get('liquidity', {}).get('usd', 0)))
            return {
                "price_usd": float(best_pair.get('priceUsd', 0)),
                "liquidity_usd": float(best_pair.get('liquidity', {}).get('usd', 0)),
                "market_cap": float(best_pair.get('fdv', 0)),
            }
        return {"price_usd": 0, "liquidity_usd": 0, "market_cap": 0, "error": "Failed to fetch market data"}

    def get_security_analysis(self, token_address: str):
        url = f"https://api.gopluslabs.io/api/v1/token_security/56?contract_addresses={token_address}"
        data = self._make_request(url)
        if data and data.get('result', {}).get(token_address.lower()):
            result = data['result'][token_address.lower()]
            return {
                "is_honeypot": result.get('is_honeypot') == '1',
                "buy_tax": float(result.get('buy_tax', '0')) * 100,
                "sell_tax": float(result.get('sell_tax', '0')) * 100,
                "holder_count": int(result.get('holder_count', '0')),
            }
        return {"is_honeypot": "N/A", "buy_tax": "N/A", "sell_tax": "N/A", "holder_count": "N/A", "error": "Failed to fetch security"}

class QuickTokenAnalysisTool(BaseTool):
    name: str = "quick_token_analysis"
    description: str = "Quickly fetches token basic info (Moralis/Dex fallback), market data (DexScreener), and security (GoPlus) for a BSC token, returning a token_summary JSON for report header."
    args_schema: type = TokenAnalysisInput

    def _run(self, token_address: str) -> str:
        # Allow JSON input
        if isinstance(token_address, str) and token_address.strip().startswith('{'):
            try:
                data = json.loads(token_address.strip())
                token_address = data.get('token_address', token_address)
            except:
                pass
        if not re.match(r'^0x[a-fA-F0-9]{40}$', token_address):
            return json.dumps({"status": "failed", "error": f"Invalid BSC address format: {token_address}"})
        fetcher = RealDataFetcher()
        basic = fetcher.get_token_basic_info(token_address)
        market = fetcher.get_token_price_data(token_address)
        security = fetcher.get_security_analysis(token_address)
        status = "success" if basic and market else "failed"
        summary = {
            "status": status,
            "token_address": token_address,
            "fetched_at": datetime.now().isoformat(),
            "token_summary": {
                "basic_info": basic,
                "market_data": market,
                "security_assessment": security
            }
        }
        return json.dumps(summary, ensure_ascii=False, indent=2)

class GetComprehensiveTokenDataTool(BaseTool):
    """
    A comprehensive tool to get all essential data for a token in one call:
    - Basic Info (name, symbol) from DexScreener
    - Market Data (price, market cap, liquidity) from DexScreener
    - Security Assessment (honeypot check, taxes) from GoPlus Security.
    Use this as your FIRST step for any token analysis to gather foundational data.
    """
    name: str = "get_comprehensive_token_data"
    description: str = "Fetches comprehensive foundational data (info, price, security) for a given BSC token address. This should be the first tool you use."
    args_schema: type = TokenAnalysisInput

    def _run(self, token_address: str) -> str:
        
        if isinstance(token_address, str) and token_address.strip().startswith('{'):
            try:
                data = json.loads(token_address.strip())
                token_address = data.get('token_address', token_address)
            except:
                pass

        if not re.match(r'^0x[a-fA-F0-9]{40}$', token_address):
            return json.dumps({"error": f"Invalid BSC address format: {token_address}"})
        
        fetcher = RealDataFetcher()
        
        # DexScreener often has both price and basic info in one call
        dex_data = fetcher._make_request(f"https://api.dexscreener.com/latest/dex/tokens/{token_address}")
        
        basic_info = {"name": "N/A", "symbol": "N/A"}
        price_data = {"price_usd": 0, "liquidity_usd": 0, "market_cap": 0}

        if dex_data and dex_data.get('pairs'):
            best_pair = max(dex_data['pairs'], key=lambda p: (float(p.get('liquidity', {}).get('usd', 0)), p.get('pairCreatedAt', 0)))
            base_token_info = best_pair.get('baseToken', {})
            basic_info = {
                "name": base_token_info.get('name', 'Unknown'),
                "symbol": base_token_info.get('symbol', 'UNKNOWN'),
            }
            price_data = {
                "price_usd": float(best_pair.get('priceUsd', 0)),
                "liquidity_usd": float(best_pair.get('liquidity', {}).get('usd', 0)),
                "market_cap": float(best_pair.get('fdv', 0)),
            }

        security_data = fetcher.get_security_analysis(token_address)
        
        combined_data = {
            "status": "success",
            "token_address": token_address,
            "fetched_at": datetime.now().isoformat(),
            "basic_info": basic_info,
            "market_data": price_data,
            "security_assessment": security_data
        }
        
        return json.dumps(combined_data, indent=2)

def create_real_data_tools() -> List[BaseTool]:
    """Creates the list of real-data tools, exposing only quick analysis to enforce usage."""
    return [QuickTokenAnalysisTool()]
