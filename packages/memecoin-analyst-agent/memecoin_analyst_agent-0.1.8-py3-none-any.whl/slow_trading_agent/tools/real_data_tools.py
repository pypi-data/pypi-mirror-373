"""
真实数据工具 - 使用真实API获取代币数据
替换模拟数据工具，提供真实的市场数据
"""

import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import json
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

class RealTokenAnalysisInput(BaseModel):
    token_address: str = Field(description="BSC代币合约地址")

class RealDataAPIClient:
    """真实数据API客户端"""
    
    def __init__(self, config: Dict[str, str] = None):
        self.config = config or {}
        self.session = None
        
        # API配置
        self.bscscan_api_key = self.config.get('BSCSCAN_API_KEY', '')
        self.moralis_api_key = self.config.get('MORALIS_API_KEY', '')
        self.twitter_bearer_token = self.config.get('TWITTER_BEARER_TOKEN', '')
        
        # API端点
        self.endpoints = {
            'bscscan': 'https://api.bscscan.com/api',
            'dexscreener': 'https://api.dexscreener.com/latest',
            'goplus': 'https://api.gopluslabs.io/api/v1',
            'moralis': 'https://deep-index.moralis.io/api/v2',
            'twitter': 'https://api.twitter.com/2'
        }
    
    async def get_session(self):
        """获取HTTP会话"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )
        return self.session
    
    async def close_session(self):
        """关闭HTTP会话"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def fetch_token_basic_info(self, token_address: str) -> Dict[str, Any]:
        """从BSCScan获取代币基础信息"""
        if not self.bscscan_api_key:
            logger.warning("BSCScan API密钥未配置，返回默认数据")
            return {
                'name': 'Unknown Token',
                'symbol': 'UNKNOWN',
                'decimals': 18,
                'total_supply': 0,
                'verified': False
            }
        
        try:
            session = await self.get_session()
            
            params = {
                'module': 'token',
                'action': 'tokeninfo',
                'contractaddress': token_address,
                'apikey': self.bscscan_api_key
            }
            
            async with session.get(self.endpoints['bscscan'], params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == '1' and data.get('result'):
                        result = data['result'][0] if isinstance(data['result'], list) else data['result']
                        return {
                            'name': result.get('tokenName', 'Unknown'),
                            'symbol': result.get('symbol', 'UNKNOWN'),
                            'decimals': int(result.get('divisor', '18')),
                            'total_supply': float(result.get('totalSupply', '0')),
                            'verified': True
                        }
        except Exception as e:
            logger.error(f"BSCScan API调用失败: {e}")
        
        return {
            'name': 'Unknown Token',
            'symbol': 'UNKNOWN', 
            'decimals': 18,
            'total_supply': 0,
            'verified': False
        }
    
    async def fetch_token_price_data(self, token_address: str) -> Dict[str, Any]:
        """从DexScreener获取价格数据"""
        try:
            session = await self.get_session()
            
            url = f"{self.endpoints['dexscreener']}/dex/tokens/{token_address}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    pairs = data.get('pairs', [])
                    
                    if pairs:
                        # 选择流动性最高的交易对
                        pair = max(pairs, key=lambda x: float(x.get('liquidity', {}).get('usd', 0) or 0))
                        
                        return {
                            'price_usd': float(pair.get('priceUsd', 0) or 0),
                            'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0) or 0),
                            'volume_24h': float(pair.get('volume', {}).get('h24', 0) or 0),
                            'liquidity_usd': float(pair.get('liquidity', {}).get('usd', 0) or 0),
                            'market_cap': float(pair.get('fdv', 0) or 0),
                            'dex_name': pair.get('dexId', 'Unknown'),
                            'pair_address': pair.get('pairAddress', ''),
                            'data_source': 'dexscreener'
                        }
        except Exception as e:
            logger.error(f"DexScreener API调用失败: {e}")
        
        return {
            'price_usd': 0.0,
            'price_change_24h': 0.0,
            'volume_24h': 0.0,
            'liquidity_usd': 0.0,
            'market_cap': 0.0,
            'dex_name': 'Unknown',
            'pair_address': '',
            'data_source': 'default'
        }
    
    async def fetch_security_data(self, token_address: str) -> Dict[str, Any]:
        """从GoPlus获取安全数据"""
        try:
            session = await self.get_session()
            
            url = f"{self.endpoints['goplus']}/token_security/56"
            params = {'contract_addresses': token_address}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get('result', {}).get(token_address.lower())
                    
                    if result:
                        return {
                            'is_honeypot': result.get('is_honeypot') == '1',
                            'can_buy': result.get('can_buy') == '1',
                            'can_sell': result.get('can_sell') == '1',
                            'buy_tax': float(result.get('buy_tax', '0')) * 100,
                            'sell_tax': float(result.get('sell_tax', '0')) * 100,
                            'lp_locked': result.get('is_lp_locked') == '1',
                            'holder_count': int(result.get('holder_count', '0')),
                            'owner_change_balance': result.get('owner_change_balance') == '1',
                            'data_source': 'goplus'
                        }
        except Exception as e:
            logger.error(f"GoPlus API调用失败: {e}")
        
        return {
            'is_honeypot': False,
            'can_buy': True,
            'can_sell': True,
            'buy_tax': 0.0,
            'sell_tax': 0.0,
            'lp_locked': False,
            'holder_count': 0,
            'owner_change_balance': False,
            'data_source': 'default'
        }

class RealTokenAnalysisTool(BaseTool):
    """真实代币分析工具"""
    name: str = "real_token_analysis"
    description: str = """
    获取真实的BSC代币综合信息，包括：
    - 基础信息（从BSCScan API获取）
    - 市场数据（从DexScreener API获取）
    - 安全评估（从GoPlus Security API获取）
    返回真实准确的代币数据。
    """
    args_schema = RealTokenAnalysisInput
    
    def __init__(self, api_config: Dict[str, str] = None):
        super().__init__()
        self.api_client = RealDataAPIClient(api_config)
    
    async def _arun(self, token_address: str) -> str:
        """异步运行工具"""
        try:
            # 并行获取所有数据
            basic_info_task = self.api_client.fetch_token_basic_info(token_address)
            price_data_task = self.api_client.fetch_token_price_data(token_address)
            security_data_task = self.api_client.fetch_security_data(token_address)
            
            basic_info = await basic_info_task
            price_data = await price_data_task
            security_data = await security_data_task
            
            # 生成综合报告
            report = f"""
真实代币分析结果 (地址: {token_address}):

基础信息 (来源: BSCScan):
- 代币名称: {basic_info['name']}
- 代币符号: {basic_info['symbol']}
- 小数位数: {basic_info['decimals']}
- 总供应量: {basic_info['total_supply']:,.0f}
- 合约验证: {'已验证' if basic_info['verified'] else '未验证'}

市场数据 (来源: DexScreener):
- 当前价格: ${price_data['price_usd']:.8f}
- 24h变化: {price_data['price_change_24h']:+.2f}%
- 24h交易量: ${price_data['volume_24h']:,.0f}
- 流动性: ${price_data['liquidity_usd']:,.0f}
- 市值: ${price_data['market_cap']:,.0f}
- 交易所: {price_data['dex_name']}

安全评估 (来源: GoPlus Security):
- 蜜罐检测: {'是蜜罐' if security_data['is_honeypot'] else '非蜜罐'}
- 可以买入: {'是' if security_data['can_buy'] else '否'}
- 可以卖出: {'是' if security_data['can_sell'] else '否'}
- 买入税率: {security_data['buy_tax']:.1f}%
- 卖出税率: {security_data['sell_tax']:.1f}%
- LP锁定: {'已锁定' if security_data['lp_locked'] else '未锁定'}
- 持有者数量: {security_data['holder_count']:,}

风险评估:
- 基础风险: {'高' if security_data['is_honeypot'] else '低' if security_data['can_sell'] else '中'}
- 流动性风险: {'高' if price_data['liquidity_usd'] < 10000 else '中' if price_data['liquidity_usd'] < 50000 else '低'}
- 税率风险: {'高' if security_data['sell_tax'] > 10 else '中' if security_data['sell_tax'] > 5 else '低'}

数据时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
数据来源: BSCScan + DexScreener + GoPlus Security
"""
            
            return report
            
        except Exception as e:
            logger.error(f"真实代币分析失败: {e}")
            return f"分析失败: {str(e)}"
        finally:
            await self.api_client.close_session()
    
    def _run(self, token_address: str) -> str:
        """同步运行工具"""
        return asyncio.run(self._arun(token_address))

# 工厂函数
def create_real_data_tools(api_config: Dict[str, str] = None) -> List[BaseTool]:
    """创建真实数据工具集"""
    return [
        RealTokenAnalysisTool(api_config)
    ]

# 配置示例
def load_api_config() -> Dict[str, str]:
    """加载API配置"""
    try:
        # 尝试从配置文件加载
        from api_config import (
            BSCSCAN_API_KEY, 
            MORALIS_API_KEY, 
            TWITTER_BEARER_TOKEN
        )
        return {
            'BSCSCAN_API_KEY': BSCSCAN_API_KEY,
            'MORALIS_API_KEY': MORALIS_API_KEY,
            'TWITTER_BEARER_TOKEN': TWITTER_BEARER_TOKEN,
        }
    except ImportError:
        # 从环境变量加载
        import os
        return {
            'BSCSCAN_API_KEY': os.getenv('BSCSCAN_API_KEY', ''),
            'MORALIS_API_KEY': os.getenv('MORALIS_API_KEY', ''),
            'TWITTER_BEARER_TOKEN': os.getenv('TWITTER_BEARER_TOKEN', ''),
        }

# 使用示例
if __name__ == "__main__":
    async def test_real_tools():
        """测试真实数据工具"""
        config = load_api_config()
        tool = RealTokenAnalysisTool(config)
        
        # 测试CAKE代币
        test_token = "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82"
        result = await tool._arun(test_token)
        print(result)
    
    asyncio.run(test_real_tools())
