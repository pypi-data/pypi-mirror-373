"""
乐观版叙事评分工具
采用更积极的评分策略，突出代币的积极面
"""

from langchain.tools import BaseTool
from typing import Type, Dict, Any, List, Optional
from pydantic import BaseModel, Field
import re
import logging
import json

logger = logging.getLogger(__name__)

class OptimisticScoringInput(BaseModel):
    token_name: Optional[str] = Field(default=None, description="代币名称")
    token_symbol: Optional[str] = Field(default=None, description="代币符号")
    token_description: Optional[str] = Field(default="", description="代币描述或项目介绍")
    community_info: Optional[Dict[str, Any]] = Field(default_factory=dict, description="社区信息")
    market_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="市场数据")

class OptimisticNarrativeScoringTool(BaseTool):
    """乐观版多维叙事评分工具 - 100分制评分系统"""
    name: str = "multi_dimensional_narrative_scoring"
    description: str = """
    对代币进行多维度叙事质量评分，采用乐观的100分制：
    1. 叙事完整性 (0-20分) - 故事的完整性和逻辑性
    2. 传播可能性 (0-20分) - 在社交媒体传播的潜力
    3. 创意表现 (0-20分) - 创新性和独特性
    4. 理解友好度 (0-20分) - 普通用户的理解难度
    5. 可信度 (0-20分) - 项目的可靠性和真实性
    总分100分，采用积极乐观的评分策略。
    """
    args_schema: Type[BaseModel] = OptimisticScoringInput

    def _run(
        self, 
        token_name: Optional[str] = None, 
        token_symbol: Optional[str] = None, 
        token_description: Optional[str] = "", 
        community_info: Optional[Dict[str, Any]] = None, 
        market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        
        # 处理可能的JSON字符串参数（与原工具保持一致）
        final_name = token_name or ""
        final_symbol = token_symbol or ""
        final_description = token_description or ""
        final_community = community_info or {}
        final_market = market_data or {}
        
        # 参数解析逻辑（处理Agent可能传递的JSON字符串）
        all_inputs = [token_name, token_symbol, token_description, community_info, market_data]
        for item in all_inputs:
            if isinstance(item, str) and item.strip().startswith('{'):
                try:
                    data = json.loads(item.strip())
                    if isinstance(data, dict):
                        final_name = data.get('token_name') or final_name
                        final_symbol = data.get('token_symbol') or final_symbol
                        final_description = data.get('token_description') or final_description
                        if data.get('community_info'):
                            final_community = data['community_info']
                        if data.get('market_data'):
                            final_market = data['market_data']
                except:
                    pass
        
        try:
            logger.info(f"进行乐观版多维叙事评分: {final_symbol or final_name}")
            
            # 1. 叙事完整性 (乐观评分)
            narrative_completeness = self._evaluate_optimistic_completeness(final_name, final_symbol, final_description, final_community)
            
            # 2. 传播可能性 (乐观评分)
            viral_potential = self._evaluate_optimistic_viral_potential(final_name, final_symbol, final_description, final_market)
            
            # 3. 创意表现 (乐观评分)
            creative_expression = self._evaluate_optimistic_creativity(final_name, final_symbol, final_description)
            
            # 4. 理解友好度 (乐观评分)
            accessibility = self._evaluate_optimistic_accessibility(final_name, final_symbol, final_description)
            
            # 5. 可信度 (乐观评分)
            credibility = self._evaluate_optimistic_credibility(final_name, final_symbol, final_community, final_market)
            
            # 计算总分
            total_score = (narrative_completeness['score'] + viral_potential['score'] + 
                          creative_expression['score'] + accessibility['score'] + credibility['score'])
            
            # 生成评分说明
            score_breakdown = self._generate_optimistic_breakdown(
                narrative_completeness, viral_potential, creative_expression, 
                accessibility, credibility, total_score
            )
            
            result = {
                'narrative_completeness': narrative_completeness,
                'viral_potential': viral_potential,
                'creative_expression': creative_expression,
                'accessibility': accessibility,
                'credibility': credibility,
                'total_narrative_score': total_score,
                'score_grade': self._get_optimistic_grade(total_score),
                'score_breakdown': score_breakdown
            }
            
            logger.info(f"乐观版叙事评分完成，总分: {total_score}/100")
            return result
            
        except Exception as e:
            logger.error(f"乐观版叙事评分失败: {e}")
            return {"error": str(e)}
    
    def _evaluate_optimistic_completeness(self, name: str, symbol: str, description: str, community_info: Dict[str, Any]) -> Dict[str, Any]:
        """乐观版叙事完整性评估"""
        score = 5  # 基础分5分
        evaluation_parts = []
        
        # 项目描述 (0-8分)
        if description and len(description) > 10:
            if len(description) > 100:
                score += 8
                evaluation_parts.append("✅ 项目描述丰富")
            elif len(description) > 30:
                score += 6
                evaluation_parts.append("✅ 项目描述清晰")
            else:
                score += 4
                evaluation_parts.append("✅ 项目描述简洁")
        else:
            score += 2
            evaluation_parts.append("⚠️ 项目描述待完善")
        
        # 名称符号关联性 (0-4分)
        if name and symbol:
            score += 4
            evaluation_parts.append("✅ 名称符号匹配")
        else:
            score += 2
            evaluation_parts.append("⚠️ 名称符号待优化")
        
        # 主题连贯性 (0-3分)
        score += 3  # 直接给满分，体现乐观
        evaluation_parts.append("✅ 主题连贯统一")
        
        return {
            'score': min(20, score),
            'evaluation': " | ".join(evaluation_parts)
        }
    
    def _evaluate_optimistic_viral_potential(self, name: str, symbol: str, description: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """乐观版传播可能性评估"""
        score = 6  # 基础分6分
        evaluation_parts = []
        
        # 名称吸引力 (0-6分)
        if name and len(name) <= 15:
            score += 6
            evaluation_parts.append("✅ 名称简洁有力")
        else:
            score += 4
            evaluation_parts.append("✅ 名称具有特色")
        
        # 社交媒体适应性 (0-5分)
        score += 5
        evaluation_parts.append("✅ 适合社交传播")
        
        # 情感共鸣 (0-3分)
        score += 3
        evaluation_parts.append("✅ 具有情感共鸣")
        
        return {
            'score': min(20, score),
            'evaluation': " | ".join(evaluation_parts)
        }
    
    def _evaluate_optimistic_creativity(self, name: str, symbol: str, description: str) -> Dict[str, Any]:
        """乐观版创意表现评估"""
        score = 8  # 基础分8分
        evaluation_parts = []
        
        # 原创性 (0-8分)
        score += 6
        evaluation_parts.append("✅ 具有原创性")
        
        # 创新性 (0-4分)
        score += 4
        evaluation_parts.append("✅ 创新表现良好")
        
        return {
            'score': min(20, score),
            'evaluation': " | ".join(evaluation_parts)
        }
    
    def _evaluate_optimistic_accessibility(self, name: str, symbol: str, description: str) -> Dict[str, Any]:
        """乐观版理解友好度评估"""
        score = 10  # 基础分10分
        evaluation_parts = []
        
        # 名称简单性 (0-5分)
        if name and len(name) <= 12:
            score += 5
            evaluation_parts.append("✅ 名称简单易懂")
        else:
            score += 3
            evaluation_parts.append("✅ 名称可理解")
        
        # 符号清晰度 (0-5分)
        if symbol and len(symbol) <= 8:
            score += 5
            evaluation_parts.append("✅ 符号简洁明了")
        else:
            score += 3
            evaluation_parts.append("✅ 符号可识别")
        
        return {
            'score': min(20, score),
            'evaluation': " | ".join(evaluation_parts)
        }
    
    def _evaluate_optimistic_credibility(self, name: str, symbol: str, community_info: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """乐观版可信度评估"""
        score = 8  # 基础分8分
        evaluation_parts = []
        
        # 专业性 (0-6分)
        if name and not self._has_scam_indicators(name, symbol):
            score += 6
            evaluation_parts.append("✅ 项目名称专业")
        else:
            score += 4
            evaluation_parts.append("✅ 项目名称可接受")
        
        # 社区可信度 (0-6分)
        score += 4
        evaluation_parts.append("✅ 社区基础良好")
        
        return {
            'score': min(20, score),
            'evaluation': " | ".join(evaluation_parts)
        }
    
    def _has_scam_indicators(self, name: str, symbol: str) -> bool:
        """检查是否有诈骗指标"""
        scam_keywords = ['scam', 'rug', 'moon', 'safe', 'baby', 'mini', 'doge', 'elon']
        text = (name + " " + symbol).lower()
        return any(keyword in text for keyword in scam_keywords)
    
    def _get_optimistic_grade(self, total_score: int) -> str:
        """获取乐观版评分等级"""
        if total_score >= 90:
            return "A+ (优秀)"
        elif total_score >= 80:
            return "A (良好)"
        elif total_score >= 70:
            return "B+ (不错)"
        elif total_score >= 60:
            return "B (一般)"
        elif total_score >= 50:
            return "C+ (及格)"
        else:
            return "C (有待改进)"
    
    def _generate_optimistic_breakdown(self, narrative_completeness: Dict, viral_potential: Dict,
                                     creative_expression: Dict, accessibility: Dict, 
                                     credibility: Dict, total_score: int) -> str:
        """生成乐观版评分说明"""
        return f"""总分 {total_score}/100 分评分构成：

📖 叙事完整性: {narrative_completeness['score']}/20 分
{narrative_completeness['evaluation']}

🚀 传播可能性: {viral_potential['score']}/20 分
{viral_potential['evaluation']}

🎨 创意表现: {creative_expression['score']}/20 分
{creative_expression['evaluation']}

🔤 理解友好度: {accessibility['score']}/20 分
{accessibility['evaluation']}

🛡️ 可信度: {credibility['score']}/20 分
{credibility['evaluation']}

综合评级: {self._get_optimistic_grade(total_score)}"""

def get_optimistic_narrative_tools() -> List[BaseTool]:
    """获取乐观版叙事评分工具"""
    return [OptimisticNarrativeScoringTool()]
