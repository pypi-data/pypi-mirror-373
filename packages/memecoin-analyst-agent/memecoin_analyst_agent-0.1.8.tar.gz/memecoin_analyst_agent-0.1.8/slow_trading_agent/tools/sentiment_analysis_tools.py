"""
情绪分析工具模块
封装Twitter情绪分析、叙事分析、KOL提及等功能为LangChain工具
"""

from langchain.tools import BaseTool
from typing import Type, Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging
import json
from datetime import datetime
import re

logger = logging.getLogger(__name__)

# ============ 工具输入模型定义 ============

class TwitterSentimentInput(BaseModel):
    token_symbol: str = Field(description="代币符号，如$CATWIF，用于Twitter情绪分析")
    tweet_count: int = Field(default=100, description="分析的推文数量，默认100条")
    token_address: str = Field(default="", description="代币地址（可选，用于从地址推导符号）")

class NarrativeAnalysisInput(BaseModel):
    token_symbol: Optional[str] = Field(default=None, description="代币符号")
    token_address: Optional[str] = Field(default=None, description="代币合约地址")
    analysis_depth: str = Field(default="standard", description="分析深度: basic, standard, deep")

class InfluencerMentionsInput(BaseModel):
    token_symbol: str = Field(description="代币符号")
    time_range_hours: int = Field(default=24, description="时间范围（小时），默认24小时")

# ============ 情绪分析工具实现 ============

class TwitterSentimentTool(BaseTool):
    """Twitter情绪分析工具"""
    name: str = "twitter_sentiment_analysis"
    description: str = """
    分析指定代币在Twitter上的社区情绪。
    通过自然语言处理技术分析相关推文的情绪倾向。
    返回情绪指数、正负面分布、热度趋势等关键指标。
    这是判断市场情绪和社区活跃度的重要工具。
    """
    args_schema: Type[BaseModel] = TwitterSentimentInput

    def _run(self, token_symbol: str, tweet_count: int = 100, token_address: str = "") -> Dict[str, Any]:
        """执行Twitter情绪分析"""
        try:
            # 处理可能的JSON字符串参数或错误的参数传递
            import json
            if token_symbol.startswith('{') and token_symbol.endswith('}'):
                try:
                    parsed = json.loads(token_symbol)
                    if 'token_symbol' in parsed:
                        token_symbol = parsed['token_symbol']
                    elif 'token_address' in parsed:
                        # 如果传递了地址而不是符号，使用地址的一部分作为符号
                        # 这是临时解决方案，实际应该从地址查询符号
                        token_symbol = f"TOKEN_{parsed['token_address'][-8:]}"
                except json.JSONDecodeError:
                    pass  # 继续使用原始值
            
            logger.info(f"分析Twitter情绪: {token_symbol}, 推文数量: {tweet_count}")
            
            # 这里应该调用实际的Twitter API和情绪分析模型
            # sentiment_result = self.sentiment_analyzer.analyze_twitter_sentiment(token_symbol, tweet_count)
            
            # 模拟情绪分析结果
            mock_sentiment_data = {
                "token_symbol": token_symbol,
                "analysis_time": datetime.now().isoformat(),
                "tweet_count": tweet_count,
                "sentiment_distribution": {
                    "positive": 65,
                    "neutral": 25,
                    "negative": 10
                },
                "sentiment_index": 0.72,  # -1到1之间，0.72表示较为积极
                "key_emotions": {
                    "excitement": 0.68,
                    "fear": 0.15,
                    "greed": 0.45,
                    "confidence": 0.58
                },
                "trending_keywords": [
                    "moon", "bullish", "gem", "hold", "community"
                ],
                "influencer_engagement": {
                    "mentions_by_influencers": 3,
                    "total_influencer_followers": 250000,
                    "engagement_score": 7.2
                },
                "sentiment_trend_24h": {
                    "direction": "improving",
                    "change_rate": 0.15
                },
                "risk_indicators": {
                    "fud_detected": False,
                    "spam_ratio": 0.08,
                    "bot_activity_score": 0.12
                }
            }
            
            logger.info(f"情绪分析完成，情绪指数: {mock_sentiment_data['sentiment_index']}")
            return mock_sentiment_data
            
        except Exception as e:
            logger.error(f"Twitter情绪分析失败: {e}")
            return {"error": str(e), "token_symbol": token_symbol}

class NarrativeAnalysisTool(BaseTool):
    """叙事分析工具"""
    name: str = "narrative_analysis"
    description: str = """
    深度分析代币的市场叙事和故事背景。
    识别代币的核心概念、社区故事、市场定位等。
    通过大语言模型理解和总结代币的价值主张。
    用于判断代币是否具有强有力的市场故事。
    """
    args_schema: Type[BaseModel] = NarrativeAnalysisInput

    def _run(
        self, 
        token_symbol: Optional[str] = None, 
        token_address: Optional[str] = None, 
        analysis_depth: str = "standard"
    ) -> Dict[str, Any]:
        """执行叙事分析"""
        import json
        
        # 增强的参数解析逻辑
        final_args = {}
        all_inputs = [token_symbol, token_address]
        
        for item in all_inputs:
            if isinstance(item, str) and item.startswith('{'):
                try:
                    data = json.loads(item)
                    final_args.update(data)
                except json.JSONDecodeError:
                    pass
        
        # 从原始参数填充
        if token_symbol and 'token_symbol' not in final_args:
            final_args['token_symbol'] = token_symbol
        if token_address and 'token_address' not in final_args:
            final_args['token_address'] = token_address
        if analysis_depth and 'analysis_depth' not in final_args:
            final_args['analysis_depth'] = analysis_depth
            
        # 在工具内部进行严格验证
        if 'token_symbol' not in final_args or 'token_address' not in final_args:
            error_msg = f"NarrativeAnalysisTool缺少必需参数。收到: symbol='{token_symbol}', address='{token_address}'"
            logger.error(error_msg)
            return {"error": error_msg}

        # 使用验证后的参数
        valid_symbol = final_args['token_symbol']
        valid_address = final_args['token_address']
        valid_depth = final_args.get('analysis_depth', 'standard')

        try:
            logger.info(f"分析代币叙事: {valid_symbol}, 地址: {valid_address}, 深度: {valid_depth}")
            
            # 模拟叙事分析结果
            mock_narrative_data = {
                "token_symbol": valid_symbol,
                "token_address": valid_address,
                "analysis_depth": valid_depth,
                "analysis_time": datetime.now().isoformat(),
                "primary_narrative": "社区驱动的猫主题Meme币，旨在成为BSC链上的'DOGE'。",
                "core_concepts": ["Meme Coin", "Community Driven", "Animal Theme", "Fair Launch"],
                "market_positioning": "旨在通过强大的社区和病毒式营销，在拥挤的Meme币市场中脱颖而出。",
                "community_story": "由一群匿名的加密爱好者发起，灵感来源于一个流行的网络迷因'戴帽子的猫'。",
                "value_proposition": "提供纯粹的娱乐价值和社区归属感，没有复杂的DeFi功能。",
                "narrative_strength_score": 7.8,
                "narrative_risks": ["Meme币热度不可持续", "缺乏实际应用场景", "竞争激烈"],
                "narrative_opportunities": ["强大的社区可能推动病毒式增长", "名人效应可能带来关注", "新的交易所上币预期"],
                "summary": "一个典型的Meme币项目，成功与否高度依赖社区活跃度和市场情绪。叙事简单易懂，易于传播，但缺乏长期价值支撑。"
            }
            
            logger.info(f"叙事分析完成: {valid_symbol}")
            return mock_narrative_data
            
        except Exception as e:
            logger.error(f"叙事分析失败: {valid_symbol}, 错误: {e}")
            return {"error": str(e)}

class InfluencerMentionsTool(BaseTool):
    """KOL提及分析工具"""
    name: str = "influencer_mentions_analysis"
    description: str = """
    分析加密货币KOL和意见领袖对代币的提及情况。
    追踪重要人物的言论和推荐，评估其对价格的潜在影响。
    识别正面推荐、警告信号、中性提及等不同类型的关注。
    """
    args_schema: Type[BaseModel] = InfluencerMentionsInput

    def _run(self, token_symbol: str, time_range_hours: int = 24) -> Dict[str, Any]:
        """执行KOL提及分析"""
        try:
            logger.info(f"分析KOL提及: {token_symbol}, 时间范围: {time_range_hours}小时")
            
            # 模拟KOL提及分析结果
            mock_influencer_data = {
                "token_symbol": token_symbol,
                "time_range_hours": time_range_hours,
                "analysis_time": datetime.now().isoformat(),
                "total_mentions": 5,
                "mention_details": [
                    {
                        "influencer": "CryptoWhale123",
                        "followers": 150000,
                        "mention_type": "positive",
                        "content_snippet": "Interesting new cat token, community looks solid",
                        "engagement": {"likes": 245, "retweets": 67, "replies": 23},
                        "influence_score": 8.2,
                        "timestamp": "2024-01-15T14:30:00Z"
                    },
                    {
                        "influencer": "DeFiAnalyst",
                        "followers": 89000,
                        "mention_type": "neutral",
                        "content_snippet": "New token alert: CATWIF launched on BSC",
                        "engagement": {"likes": 89, "retweets": 12, "replies": 5},
                        "influence_score": 6.5,
                        "timestamp": "2024-01-15T16:45:00Z"
                    }
                ],
                "influence_metrics": {
                    "total_reach": 239000,
                    "weighted_sentiment": 0.65,
                    "viral_potential": 6.8,
                    "credibility_score": 7.3
                },
                "mention_categories": {
                    "positive_recommendations": 2,
                    "neutral_alerts": 2,
                    "negative_warnings": 0,
                    "technical_analysis": 1
                },
                "trending_status": {
                    "is_trending": False,
                    "trend_velocity": 0.23,
                    "peak_mention_time": "2024-01-15T15:00:00Z"
                },
                "risk_assessment": {
                    "pump_risk": "medium",
                    "manipulation_signals": False,
                    "coordinated_promotion": False
                }
            }
            
            logger.info(f"KOL分析完成，总影响力: {mock_influencer_data['influence_metrics']['total_reach']}")
            return mock_influencer_data
            
        except Exception as e:
            logger.error(f"KOL提及分析失败: {e}")
            return {"error": str(e), "token_symbol": token_symbol}

# ============ 工具列表导出 ============

def get_sentiment_analysis_tools():
    """获取所有情绪分析工具的实例"""
    return [
        TwitterSentimentTool(),
        NarrativeAnalysisTool(),
        InfluencerMentionsTool()
    ]
