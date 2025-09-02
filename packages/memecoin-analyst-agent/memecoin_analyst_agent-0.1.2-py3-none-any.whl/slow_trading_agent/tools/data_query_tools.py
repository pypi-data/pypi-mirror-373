"""
数据查询工具模块
封装价格监控、链上分析等数据获取功能为LangChain工具
"""

from langchain.tools import BaseTool
from typing import Type, Dict, Any, Optional
from pydantic import BaseModel, Field
import aiohttp
import asyncio
import json
import logging
from datetime import datetime, timedelta
import requests # 导入requests库

# 导入现有的PancakeSwap客户端
# from onchain_pancake_client import PancakeSwapClient

logger = logging.getLogger(__name__)

# ============ 工具输入模型定义 ============

class TokenPriceInput(BaseModel):
    token_address: str = Field(description="BSC代币合约地址，用于查询实时价格")

class TokenInfoInput(BaseModel):
    token_address: str = Field(description="BSC代币合约地址，用于获取基础信息")

class LiquidityAnalysisInput(BaseModel):
    token_address: str = Field(description="BSC代币合约地址，用于分析流动性状况")

class HistoricalDataInput(BaseModel):
    token_address: str = Field(description="BSC代币合约地址")
    days: int = Field(default=7, description="历史数据天数，默认7天")

# ============ 数据查询工具实现 ============

class TokenPriceTool(BaseTool):
    """实时价格查询工具"""
    name: str = "token_price_query"
    description: str = """
    获取指定BSC代币的实时价格信息。
    返回USD价格、BNB价格、24小时变化率、流动性等关键数据。
    这是分析任何代币的第一步，用于了解当前市场状况。
    """
    args_schema: Type[BaseModel] = TokenPriceInput

    def __init__(self):
        super().__init__()
        # 这里应该初始化PancakeSwap客户端
        # self.pancake_client = PancakeSwapClient()
        
    def _run(self, token_address: str) -> Dict[str, Any]:
        """执行价格查询"""
        try:
            logger.info(f"查询代币价格: {token_address}")
            
            # 模拟调用PancakeSwap客户端
            # price_data = self.pancake_client.get_token_price(token_address)
            
            # 模拟返回数据
            mock_price_data = {
                "token_address": token_address,
                "price_usd": 0.00125,
                "price_bnb": 0.000002156,
                "liquidity_usd": 55000.0,
                "volume_24h": 125000.0,
                "price_change_24h": 15.6,
                "market_cap": 1250000.0,
                "last_updated": datetime.now().isoformat()
            }
            
            logger.info(f"价格查询完成: ${mock_price_data['price_usd']}")
            return mock_price_data
            
        except Exception as e:
            logger.error(f"价格查询失败: {e}")
            return {"error": str(e), "token_address": token_address}

class TokenInfoTool(BaseTool):
    """代币基础信息查询工具"""
    name: str = "token_info_query"
    description: str = """
    获取代币的基础信息，包括名称、符号、总供应量、小数位数等。
    用于了解代币的基本属性和技术规格。
    """
    args_schema: Type[BaseModel] = TokenInfoInput

    def _run(self, token_address: str) -> Dict[str, Any]:
        """执行代币信息查询"""
        try:
            from api_config import BSCSCAN_API_KEY
            if not BSCSCAN_API_KEY or BSCSCAN_API_KEY == "YOUR_BSCSCAN_API_KEY_HERE":
                raise ValueError("BSCScan API Key not configured in api_config.py")

            logger.info(f"查询代币信息 (BSCScan): {token_address}")
            
            params = {
                'module': 'token',
                'action': 'tokeninfo',
                'contractaddress': token_address,
                'apikey': BSCSCAN_API_KEY
            }
            response = requests.get("https://api.bscscan.com/api", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == '1' and data.get('result'):
                result = data['result'][0]
                token_info = {
                    "address": token_address,
                    "name": result.get('tokenName', 'Unknown'),
                    "symbol": result.get('symbol', 'UNKNOWN'),
                    "decimals": int(result.get('divisor', 18)),
                    "total_supply": float(result.get('totalSupply', 0)),
                    "verified_contract": True,
                    "creation_time": "N/A",
                    "creator_address": "N/A"
                }
                logger.info(f"代币信息查询完成: {token_info['symbol']}")
                return token_info
            else:
                logger.warning(f"BSCScan API did not return valid data for {token_address}: {data.get('message')}")
                return self._get_mock_info(token_address)

        except Exception as e:
            logger.error(f"代币信息查询失败: {e}")
            return self._get_mock_info(token_address, error=str(e))

    def _get_mock_info(self, token_address: str, error: Optional[str] = None) -> Dict[str, Any]:
        """备用模拟数据"""
        mock_info = {
            "address": token_address,
            "name": "Cat With Hat (Mock)",
            "symbol": "CATWIF_MOCK",
            "decimals": 18,
            "total_supply": 1000000000,
            "verified_contract": False,
            "creation_time": "2024-01-15T10:30:00Z",
            "creator_address": "0x742d35Cc6634C0532925a3b8D39A6C33f4b4E4B1"
        }
        if error:
            mock_info["error"] = error
        return mock_info

class LiquidityAnalysisTool(BaseTool):
    """流动性分析工具"""
    name: str = "liquidity_analysis"
    description: str = """
    深度分析代币的流动性状况，包括：
    - 各DEX的流动性分布
    - LP锁定情况
    - 流动性变化趋势
    - 大额交易的价格影响
    用于评估代币的交易深度和市场稳定性。
    """
    args_schema: Type[BaseModel] = LiquidityAnalysisInput

    def _run(self, token_address: str) -> Dict[str, Any]:
        """执行流动性分析"""
        try:
            logger.info(f"分析流动性: {token_address}")
            
            # 模拟多DEX流动性分析
            mock_liquidity_analysis = {
                "token_address": token_address,
                "total_liquidity_usd": 155000.0,
                "dex_distribution": {
                    "pancakeswap_v2": 120000.0,
                    "pancakeswap_v3": 25000.0,
                    "biswap": 10000.0
                },
                "lp_locked_percentage": 85.5,
                "liquidity_trend_7d": {
                    "change_percentage": 12.3,
                    "trend": "increasing"
                },
                "price_impact_analysis": {
                    "impact_1_bnb": 0.5,
                    "impact_5_bnb": 2.8,
                    "impact_10_bnb": 6.2
                },
                "liquidity_health_score": 7.5
            }
            
            logger.info(f"流动性分析完成，健康评分: {mock_liquidity_analysis['liquidity_health_score']}")
            return mock_liquidity_analysis
            
        except Exception as e:
            logger.error(f"流动性分析失败: {e}")
            return {"error": str(e), "token_address": token_address}

class HistoricalDataTool(BaseTool):
    """历史数据查询工具"""
    name: str = "historical_data_query"
    description: str = """
    获取代币的历史价格和交易数据，用于技术分析。
    包括K线数据、交易量变化、价格趋势等。
    支持自定义时间范围的数据查询。
    """
    args_schema: Type[BaseModel] = HistoricalDataInput

    def _run(self, token_address: str, days: int = 7) -> Dict[str, Any]:
        """执行历史数据查询"""
        try:
            logger.info(f"查询历史数据: {token_address}, {days}天")
            
            # 模拟历史数据
            mock_historical_data = {
                "token_address": token_address,
                "period_days": days,
                "price_history": [
                    {"timestamp": "2024-01-10T00:00:00Z", "price_usd": 0.001, "volume": 50000},
                    {"timestamp": "2024-01-11T00:00:00Z", "price_usd": 0.0011, "volume": 65000},
                    {"timestamp": "2024-01-12T00:00:00Z", "price_usd": 0.00095, "volume": 45000},
                    {"timestamp": "2024-01-13T00:00:00Z", "price_usd": 0.0012, "volume": 85000},
                    {"timestamp": "2024-01-14T00:00:00Z", "price_usd": 0.00125, "volume": 125000}
                ],
                "technical_indicators": {
                    "trend": "bullish",
                    "volatility": "medium",
                    "support_level": 0.00095,
                    "resistance_level": 0.0015,
                    "rsi": 68.5
                },
                "volume_analysis": {
                    "avg_daily_volume": 74000,
                    "volume_trend": "increasing",
                    "volume_spike_detected": True
                }
            }
            
            logger.info(f"历史数据查询完成，趋势: {mock_historical_data['technical_indicators']['trend']}")
            return mock_historical_data
            
        except Exception as e:
            logger.error(f"历史数据查询失败: {e}")
            return {"error": str(e), "token_address": token_address}

# ============ 工具列表导出 ============

def get_data_query_tools():
    """获取所有数据查询工具的实例"""
    return [
        TokenPriceTool(),
        TokenInfoTool(),
        LiquidityAnalysisTool(),
        HistoricalDataTool()
    ]
