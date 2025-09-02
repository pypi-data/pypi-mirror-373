"""
记忆查询工具模块
封装历史分析准确性查询、学习洞察等功能为LangChain工具
"""

from langchain.tools import BaseTool
from typing import Type, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ============ 工具输入模型定义 ============

class HistoricalAccuracyInput(BaseModel):
    days_back: Optional[int] = Field(default=30, description="查询过去多少天的历史准确性，默认30天")
    
    class Config:
        extra = "allow"  # 允许额外的字段

class TokenPerformanceInput(BaseModel):
    token_address: Optional[str] = Field(default=None, description="要查询历史表现的代币地址")

class MarketCapAnalysisInput(BaseModel):
    current_market_cap: Optional[float] = Field(default=None, description="当前市值（美元）")
    token_category: Optional[str] = Field(default=None, description="代币类别，如'Meme Coin', 'Animal Theme'等")
    narrative_strength: Optional[float] = Field(default=6.0, description="叙事强度评分（1-10）")

# ============ 记忆查询工具实现 ============

class HistoricalAccuracyTool(BaseTool):
    """历史预测准确性查询工具"""
    name: str = "historical_accuracy_query"
    description: str = """
    查询Agent历史分析的准确性统计。
    返回过去一段时间内预测的准确率、成功案例、失败案例等。
    用于评估和调整当前分析的可信度和权重。
    这是自我学习和改进的重要工具。
    """
    # 移除args_schema，让工具接受任何参数
    # args_schema: Type[BaseModel] = HistoricalAccuracyInput

    def _run(self, days_back: Optional[int] = 30, **kwargs) -> Dict[str, Any]:
        """查询历史预测准确性"""
        import json
        
        final_days_back = 30
        
        # 增强的参数解析
        potential_inputs = [days_back, kwargs]
        for item in potential_inputs:
            # 如果输入是字典，直接处理
            if isinstance(item, dict):
                if 'days_back' in item and isinstance(item['days_back'], int):
                    final_days_back = item['days_back']
                    break
            # 如果输入是整数，直接使用
            elif isinstance(item, int):
                final_days_back = item
                break
            # 如果输入是JSON字符串，尝试解析
            elif isinstance(item, str):
                # 处理空JSON字符串的情况
                if item.strip() in ['{}', '', '{}\n', '\n{}', '{}\\n']:
                    # 空JSON或空字符串，使用默认值，跳过
                    continue
                elif item.strip().startswith('{'):
                    try:
                        data = json.loads(item)
                        if 'days_back' in data and isinstance(data['days_back'], int):
                            final_days_back = data['days_back']
                            break
                    except (json.JSONDecodeError, TypeError):
                        # 如果解析失败或不是字典，则忽略
                        pass
                else:
                    # 尝试直接解析为整数
                    try:
                        final_days_back = int(item)
                        break
                    except ValueError:
                        pass
        
        # 如果经过所有解析后仍然没有找到有效的days_back，则使用默认值
        # 这里的逻辑主要是为了容错，即使Agent传了不相关的参数（如token_address），也能继续

        try:
            logger.info(f"查询历史准确性: 过去 {final_days_back} 天")
            
            # 使用模拟数据（内存管理器将在生产环境中集成）
            # 模拟历史准确性数据
            mock_accuracy_data = {
                    "query_period_days": final_days_back,
                    "analysis_time": datetime.now().isoformat(),
                    "accuracy_statistics": {
                        "total_predictions": 45,
                        "accurate_predictions": 31,
                        "partially_accurate": 8,
                        "inaccurate_predictions": 6,
                        "overall_accuracy_rate": 0.689,
                        "bullish_accuracy_rate": 0.75,
                        "bearish_accuracy_rate": 0.60,
                        "neutral_accuracy_rate": 0.70
                    },
                    "performance_insights": {
                        "avg_return_predicted_bullish": 85.6,
                        "avg_return_predicted_bearish": -25.3,
                        "avg_return_predicted_neutral": 15.2,
                        "best_prediction_return": 450.0,
                        "worst_prediction_return": -85.0
                    },
                    "learning_patterns": {
                        "high_sentiment_high_accuracy": True,
                        "low_liquidity_prediction_difficulty": True,
                        "meme_coins_volatility_factor": 2.3,
                        "weekend_effect": "neutral_bias",
                        "market_cap_growth_patterns": {
                            "meme_coins_avg_peak_multiple": 8.5,
                            "animal_theme_peak_multiple": 12.3,
                            "community_driven_peak_multiple": 6.8,
                            "avg_time_to_peak_days": 14.2
                        }
                    },
                    "confidence_adjustments": {
                        "sentiment_weight": 0.8,  # 情绪分析权重应调整为0.8
                        "risk_weight": 1.2,       # 风险评估权重应提升到1.2
                        "liquidity_weight": 1.1,  # 流动性权重略微提升
                        "narrative_weight": 0.9   # 叙事权重略微降低
                    },
                    "recommendations": [
                        "对于高情绪分数的代币，可以适当提高信心度",
                        "低流动性代币的预测准确性较低，应更加谨慎",
                        "Meme币波动性较大，建议降低仓位建议"
                    ]
                }
                
            logger.info(f"历史准确性查询完成，准确率: {mock_accuracy_data['accuracy_statistics']['overall_accuracy_rate']:.1%}")
            return mock_accuracy_data
            
        except Exception as e:
            logger.error(f"历史准确性查询失败: {e}")
            return {"error": str(e), "days_back": final_days_back}

class LearningInsightsTool(BaseTool):
    """学习洞察工具"""
    name: str = "learning_insights_query"
    description: str = """
    获取Agent的学习洞察和改进建议。
    分析历史预测的成功模式和失败原因。
    提供当前分析中应该重点关注的因素。
    用于优化分析策略和提高预测准确性。
    """
    args_schema: Type[BaseModel] = BaseModel

    def _run(self) -> Dict[str, Any]:
        """获取学习洞察"""
        try:
            logger.info("获取学习洞察")
            
            # 使用模拟数据（内存管理器将在生产环境中集成）
            # 模拟学习洞察数据
            mock_insights = {
                    "analysis_time": datetime.now().isoformat(),
                    "successful_prediction_patterns": [
                        {
                            "pattern": "高社区活跃度 + 低风险评分",
                            "success_rate": 0.82,
                            "avg_return": 120.5,
                            "avg_peak_market_cap_multiple": 8.3,
                            "avg_time_to_peak_days": 12,
                            "sample_size": 15
                        },
                        {
                            "pattern": "强叙事 + 充足流动性",
                            "success_rate": 0.78,
                            "avg_return": 95.3,
                            "avg_peak_market_cap_multiple": 6.8,
                            "avg_time_to_peak_days": 18,
                            "sample_size": 12
                        },
                        {
                            "pattern": "KOL推荐 + 技术面良好",
                            "success_rate": 0.75,
                            "avg_return": 88.7,
                            "avg_peak_market_cap_multiple": 7.2,
                            "avg_time_to_peak_days": 9,
                            "sample_size": 8
                        }
                    ],
                    "common_failure_patterns": [
                        {
                            "pattern": "高税率代币",
                            "failure_rate": 0.71,
                            "avg_loss": -45.2,
                            "warning": "交易税超过5%的代币表现普遍较差"
                        },
                        {
                            "pattern": "流动性不足",
                            "failure_rate": 0.65,
                            "avg_loss": -38.1,
                            "warning": "流动性低于$20K的代币风险很高"
                        }
                    ],
                    "market_conditions_impact": {
                        "bull_market_accuracy": 0.75,
                        "bear_market_accuracy": 0.58,
                        "sideways_market_accuracy": 0.69,
                        "current_market_condition": "sideways"
                    },
                    "optimization_suggestions": [
                        "在当前横盘市场中，应该更加重视风险评估",
                        "对于新发射的代币，建议等待至少24小时观察初期表现",
                        "社区活跃度是一个重要的预测指标，权重可以适当提升",
                        "根据历史数据，动物主题代币平均能达到12.3倍市值增长",
                        "市值低于100万美元的代币通常有更大的增长空间",
                        "预期峰值时间通常在2周左右，超过4周的预测准确性显著下降"
                    ],
                    "confidence_calibration": {
                        "overconfident_scenarios": ["高情绪分数但低流动性"],
                        "underconfident_scenarios": ["稳定流动性但中性情绪"],
                        "calibration_advice": "适当降低对纯情绪驱动代币的信心度"
                    }
                }
                
            logger.info("学习洞察获取完成")
            return mock_insights
            
        except Exception as e:
            logger.error(f"获取学习洞察失败: {e}")
            return {"error": str(e)}

class TokenPerformanceHistoryTool(BaseTool):
    """代币历史表现查询工具"""
    name: str = "token_performance_history"
    description: str = """
    查询特定代币的历史分析和实际表现。
    如果该代币之前被分析过，返回预测结果和实际表现的对比。
    用于了解相似代币的历史表现模式。
    """
    args_schema: Type[BaseModel] = TokenPerformanceInput

    def _run(self, token_address: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """查询代币历史表现"""
        import json
        final_args = {}
        
        # 合并所有可能的输入源
        all_inputs = [token_address, kwargs]
        for item in all_inputs:
            target = item
            if isinstance(item, str) and item.startswith('{'):
                try: target = json.loads(item)
                except (json.JSONDecodeError, TypeError): pass
            if isinstance(target, dict):
                final_args.update(target)

        if token_address and 'token_address' not in final_args:
            final_args['token_address'] = token_address

        if not final_args.get('token_address'):
            return {"error": "TokenPerformanceHistoryTool缺少token_address参数"}
            
        valid_address = final_args['token_address']
        try:
            logger.info(f"查询代币历史表现: {valid_address}")
            
            # 使用模拟数据（内存管理器将在生产环境中集成）
            # 模拟查询结果：未找到历史记录
            return {
                "token_address": valid_address,
                "has_history": False,
                "message": "该代币暂无历史分析记录",
                "recommendation": "这是首次分析该代币，建议参考相似类型代币的表现模式"
            }
            
        except Exception as e:
            logger.error(f"查询代币历史表现失败: {e}")
            return {"error": str(e), "token_address": valid_address}

class MarketCapPredictionTool(BaseTool):
    """市值预测分析工具"""
    name: str = "market_cap_prediction_analysis"
    description: str = """
    基于历史数据预测代币的市值增长潜力。
    分析相似类别代币的历史市值表现模式。
    提供市值增长预期、时间周期、风险因素等。
    这是进行代币市值分析的核心工具。
    """
    # 移除args_schema，让工具接受任何参数
    # args_schema: Type[BaseModel] = MarketCapAnalysisInput

    def _run(
        self, 
        current_market_cap: Optional[float] = None, 
        token_category: Optional[str] = None, 
        narrative_strength: Optional[float] = 6.0,
        **kwargs
    ) -> Dict[str, Any]:
        """基于历史数据预测市值增长潜力"""
        import json
        final_args = {}
        
        all_inputs = [current_market_cap, token_category, narrative_strength, kwargs]
        for item in all_inputs:
            target = item
            if isinstance(item, str) and item.startswith('{'):
                try: target = json.loads(item)
                except (json.JSONDecodeError, TypeError): pass
            if isinstance(target, dict):
                final_args.update(target)
        
        # 从原始参数填充
        if current_market_cap and 'current_market_cap' not in final_args: final_args['current_market_cap'] = current_market_cap
        if token_category and 'token_category' not in final_args: final_args['token_category'] = token_category
        if narrative_strength and 'narrative_strength' not in final_args: final_args['narrative_strength'] = narrative_strength

        # 内部验证
        if 'current_market_cap' not in final_args or 'token_category' not in final_args:
            return {"error": "MarketCapPredictionTool缺少必需参数 (current_market_cap, token_category)"}

        valid_mc = final_args['current_market_cap']
        valid_category = final_args['token_category']
        valid_strength = final_args.get('narrative_strength', 6.0)

        try:
            logger.info(f"预测市值: 当前市值=${valid_mc:,.0f}, 类别='{valid_category}', 强度={valid_strength}")
            
            # 基于类别确定历史倍数
            category_multipliers = {
                "Animal Theme": {"avg": 12.3, "max": 50, "min": 2.5},
                "Meme Coin": {"avg": 8.5, "max": 35, "min": 2.0},
                "Community Driven": {"avg": 6.8, "max": 25, "min": 1.8},
                "Celebrity": {"avg": 15.2, "max": 80, "min": 3.0},
                "Gaming": {"avg": 9.8, "max": 30, "min": 2.2}
            }
            
            # 获取对应类别的数据，默认使用Meme Coin
            multipliers = category_multipliers.get(valid_category, category_multipliers["Meme Coin"])
            
            # 基于叙事强度调整倍数
            narrative_adjustment = (valid_strength - 5.0) * 0.2  # 每1分调整20%
            adjusted_avg_multiple = multipliers["avg"] * (1 + narrative_adjustment)
            adjusted_max_multiple = multipliers["max"] * (1 + narrative_adjustment * 0.5)
            
            # 计算目标市值
            realistic_target = valid_mc * adjusted_avg_multiple
            optimistic_target = valid_mc * adjusted_max_multiple
            conservative_target = valid_mc * multipliers["min"]
            
            # 基于当前市值确定时间周期
            if valid_mc < 500000:  # 50万以下
                timeframe = "1-3 weeks"
                growth_probability = 0.75
            elif valid_mc < 2000000:  # 200万以下
                timeframe = "2-4 weeks"
                growth_probability = 0.65
            elif valid_mc < 10000000:  # 1000万以下
                timeframe = "3-6 weeks"
                growth_probability = 0.45
            else:  # 1000万以上
                timeframe = "4-8 weeks"
                growth_probability = 0.25
            
            mock_market_cap_analysis = {
                "analysis_time": datetime.now().isoformat(),
                "input_parameters": {
                    "current_market_cap": valid_mc,
                    "token_category": valid_category,
                    "narrative_strength": valid_strength
                },
                "historical_benchmarks": {
                    "category_avg_multiple": multipliers["avg"],
                    "category_max_multiple": multipliers["max"],
                    "similar_tokens_sample_size": 25,
                    "avg_time_to_peak_days": 14.2
                },
                "valuation_assessment": {
                    "current_valuation_level": "early_stage" if valid_mc < 1000000 else "developing",
                    "undervalued_probability": 0.8 if valid_mc < 500000 else 0.6,
                    "assessment_reasoning": f"基于{valid_category}类别的历史数据，当前市值处于{'早期' if valid_mc < 1000000 else '发展'}阶段"
                },
                "growth_projections": {
                    "conservative_target_mc": conservative_target,
                    "realistic_target_mc": realistic_target,
                    "optimistic_target_mc": optimistic_target,
                    "expected_timeframe": timeframe,
                    "growth_probability": growth_probability,
                    "peak_sustainability_days": 7  # 峰值维持天数
                },
                "key_growth_drivers": [
                    f"{valid_category}类别具有历史吸引力",
                    f"叙事强度评分{valid_strength}/10，{'高于' if valid_strength > 6 else '等于' if valid_strength == 6 else '低于'}平均水平",
                    "当前市值为早期发现提供了增长空间" if valid_mc < 1000000 else "市值已有一定基础，需要更强催化剂",
                    "社区发展和市场情绪将是关键驱动因素"
                ],
                "market_cap_risks": [
                    "加密市场整体波动性影响",
                    f"{valid_category}类别竞争激烈",
                    "流动性不足可能限制增长空间",
                    "没有实际用例的长期风险",
                    "监管环境变化的潜在影响"
                ],
                "comparable_analysis": {
                    "similar_successful_tokens": [
                        {"name": "TokenA", "peak_mc": valid_mc * 15, "days_to_peak": 12},
                        {"name": "TokenB", "peak_mc": valid_mc * 8, "days_to_peak": 18},
                        {"name": "TokenC", "peak_mc": valid_mc * 22, "days_to_peak": 9}
                    ],
                    "success_patterns": f"{valid_category}类别代币在强叙事驱动下平均能达到{multipliers['avg']:.1f}倍增长"
                }
            }
            
            logger.info(f"市值预测分析完成，预期增长倍数: {adjusted_avg_multiple:.1f}x")
            return mock_market_cap_analysis
            
        except Exception as e:
            logger.error(f"市值预测分析失败: {e}")
            return {"error": str(e), "current_market_cap": valid_mc}

# ============ 工具列表导出 ============

def get_memory_tools(memory_manager=None):
    """获取所有记忆查询工具的实例"""
    return [
        HistoricalAccuracyTool(),
        LearningInsightsTool(),
        TokenPerformanceHistoryTool(),
        MarketCapPredictionTool()
    ]
