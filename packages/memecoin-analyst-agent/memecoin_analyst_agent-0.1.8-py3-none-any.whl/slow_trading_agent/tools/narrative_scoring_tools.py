"""
叙事评分工具模块
专门负责对代币进行多维度叙事质量评分（100分制）
"""

from langchain.tools import BaseTool
from typing import Type, Dict, Any, List, Optional
from pydantic import BaseModel, Field
import re
import logging

logger = logging.getLogger(__name__)

# ============ 输入模式定义 ============

class NarrativeScoringInput(BaseModel):
    token_name: Optional[str] = Field(default=None, description="代币名称")
    token_symbol: Optional[str] = Field(default=None, description="代币符号")
    token_description: Optional[str] = Field(default="", description="代币描述或项目介绍")
    community_info: Optional[Dict[str, Any]] = Field(default_factory=dict, description="社区信息")
    market_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="市场数据")

class KeywordAnalysisInput(BaseModel):
    token_name: Optional[str] = Field(default=None, description="代币名称")
    token_symbol: Optional[str] = Field(default=None, description="代币符号")
    project_description: Optional[str] = Field(default="", description="项目描述")
    social_mentions: Optional[List[str]] = Field(default_factory=list, description="社交媒体提及内容")

# ============ 多维叙事评分工具 ============

class MultiDimensionalNarrativeScoringTool(BaseTool):
    """多维叙事评分工具 - 100分制评分系统"""
    name: str = "multi_dimensional_narrative_scoring"
    description: str = """
    对代币进行多维度叙事质量评分，采用100分制：
    1. 叙事完整性 (0-20分) - 故事的完整性和逻辑性
    2. 传播可能性 (0-20分) - 在社交媒体传播的潜力
    3. 创意表现 (0-20分) - 创新性和独特性
    4. 理解友好度 (0-20分) - 普通用户的理解难度
    5. 可信度 (0-20分) - 项目的可靠性和真实性
    总分100分，提供详细的评分说明和改进建议。
    """
    args_schema: Type[BaseModel] = NarrativeScoringInput
    
    def _run(
        self, 
        token_name: Optional[str] = None, 
        token_symbol: Optional[str] = None, 
        token_description: Optional[str] = "", 
        community_info: Optional[Dict[str, Any]] = None, 
        market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        
        import json
        final_args = {}
        # 遍历所有可能的输入参数，尝试解析JSON
        all_inputs = [token_name, token_symbol, token_description, community_info, market_data]
        
        for item in all_inputs:
            if isinstance(item, str) and item.startswith('{'):
                try:
                    data = json.loads(item)
                    final_args.update(data)
                except (json.JSONDecodeError, TypeError):
                    pass

        # 使用原始参数填充尚未解析的字段
        if token_name and 'token_name' not in final_args: final_args['token_name'] = token_name
        if token_symbol and 'token_symbol' not in final_args: final_args['token_symbol'] = token_symbol
        if token_description and 'token_description' not in final_args: final_args['token_description'] = token_description
        if community_info and 'community_info' not in final_args: final_args['community_info'] = community_info
        if market_data and 'market_data' not in final_args: final_args['market_data'] = market_data
            
        # 在工具内部进行严格验证
        if 'token_name' not in final_args or 'token_symbol' not in final_args:
            error_msg = f"MultiDimensionalNarrativeScoringTool缺少必需参数。收到: name='{token_name}', symbol='{token_symbol}'"
            logger.error(error_msg)
            return {"error": error_msg}

        # 使用验证和清理后的参数
        valid_name = final_args['token_name']
        valid_symbol = final_args['token_symbol']
        valid_description = final_args.get('token_description', "")
        valid_community_info = final_args.get('community_info') or {}
        valid_market_data = final_args.get('market_data') or {}
        
        logger.info(f"进行多维叙事评分: {valid_name} ({valid_symbol})")

        # 1. 叙事完整性评分 (0-20分)
        narrative_completeness = self._evaluate_narrative_completeness(valid_name, valid_symbol, valid_description, valid_community_info)
        
        # 2. 传播可能性评分 (0-20分)
        viral_potential = self._evaluate_viral_potential(valid_name, valid_symbol, valid_description, valid_market_data)
        
        # 3. 创意表现评分 (0-20分)
        creative_expression = self._evaluate_creative_expression(valid_name, valid_symbol, valid_description)
        
        # 4. 理解友好度评分 (0-20分)
        accessibility = self._evaluate_accessibility(valid_name, valid_symbol, valid_description)
        
        # 5. 可信度评分 (0-20分)
        credibility = self._evaluate_credibility(valid_name, valid_symbol, valid_community_info, valid_market_data)
        
        # 计算总分
        total_score = (
            narrative_completeness["score"] + 
            viral_potential["score"] + 
            creative_expression["score"] + 
            accessibility["score"] + 
            credibility["score"]
        )
        
        # 生成评分等级
        score_grade = self._get_score_grade(total_score)
        
        return {
            "narrative_completeness": narrative_completeness,
            "viral_potential": viral_potential,
            "creative_expression": creative_expression,
            "accessibility": accessibility,
            "credibility": credibility,
            "total_narrative_score": total_score,
            "score_grade": score_grade,
            "score_breakdown": self._generate_score_breakdown(
                narrative_completeness, viral_potential, creative_expression, 
                accessibility, credibility, total_score
            ),
            "improvement_suggestions": self._generate_improvement_suggestions(
                narrative_completeness, viral_potential, creative_expression, 
                accessibility, credibility
            )
        }
    
    def _evaluate_narrative_completeness(self, name: str, symbol: str, description: str, 
                                       community_info: Dict[str, Any]) -> Dict[str, Any]:
        """评估叙事完整性 (0-20分)"""
        score = 0
        evaluation_points = []
        
        # 基础故事完整性 (0-8分) - 乐观版本
        if description and len(description) > 50:
            if len(description) > 200:
                score += 8
                evaluation_points.append("✅ 项目描述详细完整")
            elif len(description) > 100:
                score += 6
                evaluation_points.append("✅ 项目描述较为完整")
            else:
                score += 4
                evaluation_points.append("✅ 项目描述简洁有力")
        elif description and len(description) > 10:
            score += 3
            evaluation_points.append("✅ 有基础项目描述")
        else:
            score += 1  # 即使没有描述也给1分基础分
            evaluation_points.append("⚠️ 项目描述待完善")
        
        # 名称与符号一致性 (0-4分)
        if self._check_name_symbol_consistency(name, symbol):
            score += 4
            evaluation_points.append("✅ 名称与符号高度一致")
        elif self._check_name_symbol_relevance(name, symbol):
            score += 2
            evaluation_points.append("✅ 名称与符号相关")
        else:
            evaluation_points.append("⚠️ 名称与符号关联性较弱")
        
        # 主题连贯性 (0-4分)
        theme_score = self._analyze_theme_coherence(name, symbol, description)
        score += theme_score
        if theme_score >= 3:
            evaluation_points.append("✅ 主题连贯性强")
        elif theme_score >= 2:
            evaluation_points.append("✅ 主题连贯性一般")
        else:
            evaluation_points.append("⚠️ 主题连贯性有待提升")
        
        # 社区参与度 (0-4分)
        community_score = self._evaluate_community_engagement(community_info)
        score += community_score
        if community_score >= 3:
            evaluation_points.append("✅ 社区参与度高")
        elif community_score >= 2:
            evaluation_points.append("✅ 社区参与度中等")
        else:
            evaluation_points.append("⚠️ 社区参与度较低")
        
        return {
            "score": min(score, 20),
            "evaluation": " | ".join(evaluation_points),
            "details": {
                "story_completeness": min(score // 4 * 4, 8),
                "name_consistency": min((score % 20) // 4 * 4, 4),
                "theme_coherence": theme_score,
                "community_engagement": community_score
            }
        }
    
    def _evaluate_viral_potential(self, name: str, symbol: str, description: str, 
                                market_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估传播可能性 (0-20分)"""
        score = 0
        evaluation_points = []
        
        # 记忆性和朗朗上口 (0-6分)
        if self._is_memorable_name(name):
            score += 4
            evaluation_points.append("✅ 名称易记忆")
        if self._is_catchy_symbol(symbol):
            score += 2
            evaluation_points.append("✅ 符号朗朗上口")
        
        # 情感共鸣 (0-6分)
        emotional_score = self._analyze_emotional_appeal(name, symbol, description)
        score += emotional_score
        if emotional_score >= 4:
            evaluation_points.append("✅ 情感共鸣强")
        elif emotional_score >= 2:
            evaluation_points.append("✅ 有一定情感共鸣")
        else:
            evaluation_points.append("⚠️ 情感共鸣较弱")
        
        # 趋势关联性 (0-4分)
        trend_score = self._analyze_trend_relevance(name, symbol, description)
        score += trend_score
        if trend_score >= 3:
            evaluation_points.append("✅ 高度关联当前趋势")
        elif trend_score >= 2:
            evaluation_points.append("✅ 关联部分趋势")
        else:
            evaluation_points.append("⚠️ 趋势关联性较低")
        
        # 社交媒体适应性 (0-4分)
        social_score = self._evaluate_social_media_fitness(name, symbol)
        score += social_score
        if social_score >= 3:
            evaluation_points.append("✅ 非常适合社交媒体传播")
        elif social_score >= 2:
            evaluation_points.append("✅ 适合社交媒体传播")
        else:
            evaluation_points.append("⚠️ 社交传播适应性一般")
        
        return {
            "score": min(score, 20),
            "evaluation": " | ".join(evaluation_points),
            "viral_factors": {
                "memorability": min(score // 4, 6),
                "emotional_appeal": emotional_score,
                "trend_relevance": trend_score,
                "social_fitness": social_score
            }
        }
    
    def _evaluate_creative_expression(self, name: str, symbol: str, description: str) -> Dict[str, Any]:
        """评估创意表现 (0-20分)"""
        score = 0
        evaluation_points = []
        
        # 原创性 (0-8分)
        originality_score = self._analyze_originality(name, symbol)
        score += originality_score
        if originality_score >= 6:
            evaluation_points.append("✅ 高度原创")
        elif originality_score >= 4:
            evaluation_points.append("✅ 有一定原创性")
        else:
            evaluation_points.append("⚠️ 原创性不足")
        
        # 创新概念 (0-6分)
        innovation_score = self._analyze_innovation(name, symbol, description)
        score += innovation_score
        if innovation_score >= 4:
            evaluation_points.append("✅ 概念创新")
        elif innovation_score >= 2:
            evaluation_points.append("✅ 有创新元素")
        else:
            evaluation_points.append("⚠️ 缺乏创新")
        
        # 视觉想象力 (0-6分)
        visual_score = self._analyze_visual_appeal(name, symbol, description)
        score += visual_score
        if visual_score >= 4:
            evaluation_points.append("✅ 视觉想象力丰富")
        elif visual_score >= 2:
            evaluation_points.append("✅ 有视觉吸引力")
        else:
            evaluation_points.append("⚠️ 视觉表现力一般")
        
        return {
            "score": min(score, 20),
            "evaluation": " | ".join(evaluation_points),
            "creative_aspects": {
                "originality": originality_score,
                "innovation": innovation_score,
                "visual_appeal": visual_score
            }
        }
    
    def _evaluate_accessibility(self, name: str, symbol: str, description: str) -> Dict[str, Any]:
        """评估理解友好度 (0-20分)"""
        score = 0
        evaluation_points = []
        
        # 名称简单性 (0-6分)
        if len(name) <= 6:
            score += 4
            evaluation_points.append("✅ 名称简短易记")
        elif len(name) <= 10:
            score += 2
            evaluation_points.append("✅ 名称长度适中")
        else:
            evaluation_points.append("⚠️ 名称较长")
        
        if self._is_pronounceable(name):
            score += 2
            evaluation_points.append("✅ 发音简单")
        
        # 符号清晰性 (0-6分)
        if len(symbol) <= 5:
            score += 3
            evaluation_points.append("✅ 符号简洁")
        elif len(symbol) <= 8:
            score += 2
            evaluation_points.append("✅ 符号长度适中")
        else:
            evaluation_points.append("⚠️ 符号较长")
        
        if symbol.isalpha():
            score += 3
            evaluation_points.append("✅ 符号纯字母，易理解")
        elif symbol.isalnum():
            score += 2
            evaluation_points.append("✅ 符号字母数字混合")
        
        # 概念直观性 (0-8分)
        concept_score = self._analyze_concept_clarity(name, symbol, description)
        score += concept_score
        if concept_score >= 6:
            evaluation_points.append("✅ 概念直观易懂")
        elif concept_score >= 4:
            evaluation_points.append("✅ 概念较为清晰")
        else:
            evaluation_points.append("⚠️ 概念理解需要解释")
        
        return {
            "score": min(score, 20),
            "evaluation": " | ".join(evaluation_points),
            "accessibility_factors": {
                "name_simplicity": min(6, score // 3),
                "symbol_clarity": min(6, (score % 18) // 3),
                "concept_clarity": concept_score
            }
        }
    
    def _evaluate_credibility(self, name: str, symbol: str, community_info: Dict[str, Any], 
                            market_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估可信度 (0-20分)"""
        score = 0
        evaluation_points = []
        
        # 专业性 (0-6分)
        if self._appears_professional(name, symbol):
            score += 4
            evaluation_points.append("✅ 名称专业")
        if not self._has_scam_indicators(name, symbol):
            score += 2
            evaluation_points.append("✅ 无明显诈骗特征")
        
        # 技术可信度 (0-6分)
        if market_data.get('contract_verified', False):
            score += 3
            evaluation_points.append("✅ 合约已验证")
        if market_data.get('liquidity_usd', 0) > 50000:
            score += 2
            evaluation_points.append("✅ 流动性充足")
        if market_data.get('holder_count', 0) > 1000:
            score += 1
            evaluation_points.append("✅ 持有者基数良好")
        
        # 社区可信度 (0-8分)
        community_score = self._evaluate_community_credibility(community_info)
        score += community_score
        if community_score >= 6:
            evaluation_points.append("✅ 社区可信度高")
        elif community_score >= 4:
            evaluation_points.append("✅ 社区可信度中等")
        else:
            evaluation_points.append("⚠️ 社区可信度有待提升")
        
        return {
            "score": min(score, 20),
            "evaluation": " | ".join(evaluation_points),
            "credibility_factors": {
                "professionalism": min(6, score // 3),
                "technical_credibility": min(6, (score % 18) // 3),
                "community_credibility": community_score
            }
        }
    
    # ============ 辅助评估方法 ============
    
    def _check_name_symbol_consistency(self, name: str, symbol: str) -> bool:
        """检查名称与符号的一致性"""
        if not name or not symbol:
            return False
        
        # 首字母一致性
        if name[0].upper() == symbol[0].upper():
            return True
        
        # 缩写一致性
        name_words = re.findall(r'\b\w', name.upper())
        if ''.join(name_words) == symbol.upper():
            return True
        
        return False
    
    def _check_name_symbol_relevance(self, name: str, symbol: str) -> bool:
        """检查名称与符号的相关性"""
        if not name or not symbol:
            return False
        
        # 包含关系
        if symbol.upper() in name.upper() or name.upper() in symbol.upper():
            return True
        
        # 部分匹配
        name_clean = re.sub(r'[^a-zA-Z]', '', name.upper())
        symbol_clean = re.sub(r'[^a-zA-Z]', '', symbol.upper())
        
        if len(set(name_clean) & set(symbol_clean)) >= 2:
            return True
        
        return False
    
    def _analyze_theme_coherence(self, name: str, symbol: str, description: str) -> int:
        """分析主题连贯性 (0-4分)"""
        score = 0
        
        # 动物主题
        animal_keywords = ['cat', 'dog', 'frog', 'bird', 'lion', 'tiger', 'bear', 'wolf']
        if any(keyword in name.lower() for keyword in animal_keywords):
            if any(keyword in description.lower() for keyword in animal_keywords):
                score += 2
            else:
                score += 1
        
        # 技术主题
        tech_keywords = ['ai', 'blockchain', 'defi', 'nft', 'web3', 'crypto']
        if any(keyword in name.lower() for keyword in tech_keywords):
            if any(keyword in description.lower() for keyword in tech_keywords):
                score += 2
            else:
                score += 1
        
        # Meme主题
        meme_keywords = ['moon', 'rocket', 'diamond', 'hodl', 'safe', 'baby']
        if any(keyword in name.lower() for keyword in meme_keywords):
            if any(keyword in description.lower() for keyword in meme_keywords):
                score += 2
            else:
                score += 1
        
        return min(score, 4)
    
    def _evaluate_community_engagement(self, community_info: Dict[str, Any]) -> int:
        """评估社区参与度 (0-4分)"""
        score = 0
        
        telegram_members = community_info.get('telegram_members', 0)
        twitter_followers = community_info.get('twitter_followers', 0)
        discord_members = community_info.get('discord_members', 0)
        
        total_community = telegram_members + twitter_followers + discord_members
        
        if total_community > 10000:
            score += 4
        elif total_community > 5000:
            score += 3
        elif total_community > 1000:
            score += 2
        elif total_community > 100:
            score += 1
        
        return score
    
    def _is_memorable_name(self, name: str) -> bool:
        """判断名称是否易记忆"""
        if not name:
            return False
        
        # 短名称更易记忆
        if len(name) <= 6:
            return True
        
        # 重复音节
        if len(set(name.lower())) < len(name) * 0.7:
            return True
        
        # 常见单词组合
        common_words = ['cat', 'dog', 'moon', 'safe', 'baby', 'king', 'lord']
        if any(word in name.lower() for word in common_words):
            return True
        
        return False
    
    def _is_catchy_symbol(self, symbol: str) -> bool:
        """判断符号是否朗朗上口"""
        if not symbol:
            return False
        
        # 短符号
        if len(symbol) <= 4:
            return True
        
        # 重复字母
        if len(set(symbol.upper())) < len(symbol) * 0.8:
            return True
        
        return False
    
    def _analyze_emotional_appeal(self, name: str, symbol: str, description: str) -> int:
        """分析情感共鸣 (0-6分)"""
        score = 0
        text = f"{name} {symbol} {description}".lower()
        
        # 积极情感词汇
        positive_keywords = ['love', 'heart', 'happy', 'joy', 'cute', 'sweet', 'precious']
        score += min(2, sum(1 for keyword in positive_keywords if keyword in text))
        
        # 力量感词汇
        power_keywords = ['strong', 'power', 'king', 'lord', 'master', 'boss', 'alpha']
        score += min(2, sum(1 for keyword in power_keywords if keyword in text))
        
        # 社区情感词汇
        community_keywords = ['together', 'family', 'community', 'united', 'team']
        score += min(2, sum(1 for keyword in community_keywords if keyword in text))
        
        return min(score, 6)
    
    def _analyze_trend_relevance(self, name: str, symbol: str, description: str) -> int:
        """分析趋势关联性 (0-4分)"""
        score = 0
        text = f"{name} {symbol} {description}".lower()
        
        # 当前加密趋势
        crypto_trends = ['ai', 'gamefi', 'metaverse', 'nft', 'defi', 'web3']
        score += min(2, sum(1 for trend in crypto_trends if trend in text))
        
        # 社交趋势
        social_trends = ['viral', 'meme', 'trending', 'hot']
        score += min(2, sum(1 for trend in social_trends if trend in text))
        
        return min(score, 4)
    
    def _evaluate_social_media_fitness(self, name: str, symbol: str) -> int:
        """评估社交媒体适应性 (0-4分)"""
        score = 0
        
        # 标签友好性
        if re.match(r'^[a-zA-Z]+$', symbol):
            score += 2
        
        # 易搜索性
        if len(name) >= 3 and len(name) <= 15:
            score += 1
        
        # 易分享性
        if ' ' not in name or len(name.split()) <= 2:
            score += 1
        
        return min(score, 4)
    
    def _analyze_originality(self, name: str, symbol: str) -> int:
        """分析原创性 (0-8分)"""
        score = 8  # 从满分开始扣分
        
        # 常见模式扣分
        common_patterns = ['safe', 'baby', 'mini', 'max', 'super', 'mega', 'ultra']
        for pattern in common_patterns:
            if pattern in name.lower():
                score -= 2
                break
        
        # 数字后缀扣分
        if re.search(r'\d+$', name):
            score -= 2
        
        # 过于简单扣分
        if len(name) <= 3:
            score -= 2
        
        return max(0, score)
    
    def _analyze_innovation(self, name: str, symbol: str, description: str) -> int:
        """分析创新概念 (0-6分)"""
        score = 0
        text = f"{name} {symbol} {description}".lower()
        
        # 新概念关键词
        innovation_keywords = ['revolutionary', 'innovative', 'breakthrough', 'unique', 'first']
        score += min(3, sum(1 for keyword in innovation_keywords if keyword in text))
        
        # 技术创新
        tech_innovation = ['algorithm', 'protocol', 'mechanism', 'system']
        score += min(3, sum(1 for keyword in tech_innovation if keyword in text))
        
        return min(score, 6)
    
    def _analyze_visual_appeal(self, name: str, symbol: str, description: str) -> int:
        """分析视觉吸引力 (0-6分)"""
        score = 0
        
        # 视觉相关词汇
        visual_keywords = ['color', 'bright', 'shiny', 'golden', 'diamond', 'crystal']
        text = f"{name} {symbol} {description}".lower()
        score += min(3, sum(1 for keyword in visual_keywords if keyword in text))
        
        # 形象化名称
        if any(char in name.lower() for char in ['cat', 'dog', 'moon', 'star', 'sun']):
            score += 2
        
        # 符号美观性
        if len(symbol) <= 5 and symbol.isalpha():
            score += 1
        
        return min(score, 6)
    
    def _analyze_concept_clarity(self, name: str, symbol: str, description: str) -> int:
        """分析概念清晰度 (0-8分)"""
        score = 0
        
        # 直观命名
        intuitive_words = ['coin', 'token', 'cash', 'pay', 'finance', 'money']
        if any(word in name.lower() for word in intuitive_words):
            score += 3
        
        # 行业清晰性
        if any(word in name.lower() for word in ['defi', 'nft', 'game', 'social']):
            score += 2
        
        # 描述清晰性
        if description and len(description) > 50:
            if any(word in description.lower() for word in ['purpose', 'goal', 'aim', 'objective']):
                score += 3
        
        return min(score, 8)
    
    def _is_pronounceable(self, name: str) -> bool:
        """判断是否易发音"""
        if not name:
            return False
        
        # 检查是否包含过多连续辅音
        consonants = 'bcdfghjklmnpqrstvwxyz'
        consecutive_consonants = 0
        max_consecutive = 0
        
        for char in name.lower():
            if char in consonants:
                consecutive_consonants += 1
                max_consecutive = max(max_consecutive, consecutive_consonants)
            else:
                consecutive_consonants = 0
        
        return max_consecutive <= 3
    
    def _appears_professional(self, name: str, symbol: str) -> bool:
        """判断是否显得专业"""
        if not name or not symbol:
            return False
        
        # 避免儿童化词汇
        childish_words = ['baby', 'cute', 'little', 'tiny', 'mini']
        if any(word in name.lower() for word in childish_words):
            return False
        
        # 避免过度夸张
        exaggerated_words = ['super', 'mega', 'ultra', 'extreme', 'maximum']
        if any(word in name.lower() for word in exaggerated_words):
            return False
        
        return True
    
    def _has_scam_indicators(self, name: str, symbol: str) -> bool:
        """检查是否有诈骗指标"""
        scam_keywords = ['safe', 'moon', 'get rich', 'easy money', 'guaranteed']
        text = f"{name} {symbol}".lower()
        
        return any(keyword in text for keyword in scam_keywords)
    
    def _evaluate_community_credibility(self, community_info: Dict[str, Any]) -> int:
        """评估社区可信度 (0-8分)"""
        score = 0
        
        # 官方渠道完整性
        if community_info.get('official_website'):
            score += 2
        if community_info.get('twitter_verified'):
            score += 2
        if community_info.get('telegram_active'):
            score += 2
        
        # 团队透明度
        if community_info.get('team_doxxed'):
            score += 2
        
        return min(score, 8)
    
    def _get_score_grade(self, total_score: int) -> str:
        """获取评分等级"""
        if total_score >= 90:
            return "A+ (优秀)"
        elif total_score >= 80:
            return "A (良好)"
        elif total_score >= 70:
            return "B (中等偏上)"
        elif total_score >= 60:
            return "C (中等)"
        elif total_score >= 50:
            return "D (中等偏下)"
        else:
            return "F (需要改进)"
    
    def _generate_score_breakdown(self, narrative_completeness: Dict, viral_potential: Dict,
                                creative_expression: Dict, accessibility: Dict, 
                                credibility: Dict, total_score: int) -> str:
        """生成评分详细说明"""
        return f"""
总分 {total_score}/100 分评分构成：

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

综合评级: {self._get_score_grade(total_score)}
        """.strip()
    
    def _generate_improvement_suggestions(self, narrative_completeness: Dict, viral_potential: Dict,
                                        creative_expression: Dict, accessibility: Dict, 
                                        credibility: Dict) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if narrative_completeness['score'] < 15:
            suggestions.append("建议完善项目描述，增强故事的完整性和逻辑性")
        
        if viral_potential['score'] < 15:
            suggestions.append("建议优化名称和符号，提升传播潜力和记忆度")
        
        if creative_expression['score'] < 15:
            suggestions.append("建议增强创意表现，提升项目的独特性和创新性")
        
        if accessibility['score'] < 15:
            suggestions.append("建议简化概念表达，提高普通用户的理解度")
        
        if credibility['score'] < 15:
            suggestions.append("建议提升项目的专业性和可信度，增强用户信任")
        
        return suggestions

# ============ 关键词识别分类工具 ============

class KeywordIdentificationTool(BaseTool):
    """关键词识别与分类工具"""
    name: str = "keyword_identification_classification"
    description: str = """
    对代币进行全面的关键词识别和分类，包括：
    - 主要分类识别
    - 主题标签提取
    - 市场情绪关键词分析
    - 技术特征关键词
    - 社区文化关键词
    - 风险信号关键词
    - 流行标签识别
    """
    args_schema: Type[BaseModel] = KeywordAnalysisInput
    
    def _run(
        self, 
        token_name: Optional[str] = None, 
        token_symbol: Optional[str] = None, 
        project_description: Optional[str] = "",
        social_mentions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        
        import json
        final_args = {}
        all_inputs = [token_name, token_symbol, project_description, social_mentions]

        for item in all_inputs:
            if isinstance(item, str) and item.startswith('{'):
                try:
                    data = json.loads(item)
                    final_args.update(data)
                except (json.JSONDecodeError, TypeError):
                    pass
        
        # 使用原始参数填充
        if token_name and 'token_name' not in final_args: final_args['token_name'] = token_name
        if token_symbol and 'token_symbol' not in final_args: final_args['token_symbol'] = token_symbol
        if project_description and 'project_description' not in final_args: final_args['project_description'] = project_description
        if social_mentions and 'social_mentions' not in final_args: final_args['social_mentions'] = social_mentions

        # 内部验证
        if 'token_name' not in final_args or 'token_symbol' not in final_args:
            error_msg = f"KeywordIdentificationTool缺少必需参数。收到: name='{token_name}', symbol='{token_symbol}'"
            logger.error(error_msg)
            return {"error": error_msg}

        valid_name = final_args['token_name']
        valid_symbol = final_args['token_symbol']
        valid_description = final_args.get('project_description', "")
        valid_mentions = final_args.get('social_mentions') or []

        logger.info(f"进行关键词识别: {valid_name} ({valid_symbol})")

        # 合并所有文本内容
        all_text = f"{valid_name} {valid_symbol} {valid_description} {' '.join(valid_mentions)}".lower()
        
        # 主要分类识别
        primary_category = self._identify_primary_category(valid_name, valid_symbol, valid_description)
        
        # 主题标签识别
        theme_tags = self._extract_theme_tags(all_text)
        
        # 市场情绪关键词
        sentiment_keywords = self._extract_sentiment_keywords(all_text)
        
        # 技术关键词
        tech_keywords = self._extract_technology_keywords(all_text)
        
        # 社区关键词
        community_keywords = self._extract_community_keywords(all_text)
        
        # 风险信号关键词
        risk_keywords = self._extract_risk_keywords(all_text)
        
        # 流行标签
        trending_hashtags = self._extract_trending_hashtags(all_text, valid_mentions)
        
        return {
            "primary_category": primary_category,
            "theme_tags": theme_tags,
            "market_sentiment_keywords": sentiment_keywords,
            "technology_keywords": tech_keywords,
            "community_keywords": community_keywords,
            "risk_signal_keywords": risk_keywords,
            "trending_hashtags": trending_hashtags,
            "keyword_analysis_summary": self._generate_keyword_summary(
                primary_category, theme_tags, sentiment_keywords, tech_keywords
            )
        }
    
    def _identify_primary_category(self, name: str, symbol: str, description: str) -> str:
        """识别主要分类"""
        text = f"{name} {symbol} {description}".lower()
        
        # DeFi 代币
        if any(keyword in text for keyword in ['defi', 'swap', 'liquidity', 'yield', 'farm', 'stake']):
            return "DeFi Token"
        
        # 游戏代币
        if any(keyword in text for keyword in ['game', 'gaming', 'play', 'nft', 'metaverse']):
            return "Gaming Token"
        
        # AI代币
        if any(keyword in text for keyword in ['ai', 'artificial intelligence', 'machine learning', 'neural']):
            return "AI Token"
        
        # 动物主题Meme币
        animal_keywords = ['cat', 'dog', 'frog', 'bird', 'lion', 'tiger', 'bear', 'wolf', 'rabbit', 'mouse']
        if any(keyword in text for keyword in animal_keywords):
            return "Animal Theme Meme Coin"
        
        # 一般Meme币
        meme_keywords = ['meme', 'moon', 'rocket', 'diamond', 'hodl', 'ape', 'degen']
        if any(keyword in text for keyword in meme_keywords):
            return "Meme Coin"
        
        # 支付代币
        if any(keyword in text for keyword in ['pay', 'payment', 'cash', 'currency', 'money']):
            return "Payment Token"
        
        # 社交代币
        if any(keyword in text for keyword in ['social', 'community', 'creator', 'content']):
            return "Social Token"
        
        return "Utility Token"
    
    def _extract_theme_tags(self, text: str) -> List[str]:
        """提取主题标签"""
        tags = []
        
        # 技术主题
        tech_themes = {
            'blockchain': 'Blockchain',
            'web3': 'Web3',
            'defi': 'DeFi',
            'nft': 'NFT',
            'dao': 'DAO',
            'metaverse': 'Metaverse',
            'ai': 'Artificial Intelligence',
            'gamefi': 'GameFi'
        }
        
        # 动物主题
        animal_themes = {
            'cat': 'Cat Theme',
            'dog': 'Dog Theme', 
            'frog': 'Frog Theme',
            'bird': 'Bird Theme',
            'lion': 'Lion Theme',
            'bear': 'Bear Theme'
        }
        
        # 情感主题
        emotion_themes = {
            'love': 'Love Theme',
            'heart': 'Heart Theme',
            'happy': 'Happiness Theme',
            'peace': 'Peace Theme'
        }
        
        # 检查所有主题
        for keyword, tag in {**tech_themes, **animal_themes, **emotion_themes}.items():
            if keyword in text and tag not in tags:
                tags.append(tag)
        
        return tags[:10]  # 限制标签数量
    
    def _extract_sentiment_keywords(self, text: str) -> List[str]:
        """提取市场情绪关键词"""
        keywords = []
        
        # 积极情绪
        positive_words = ['moon', 'rocket', 'gem', 'diamond', 'bullish', 'pump', 'lambo', 'moon']
        # 消极情绪
        negative_words = ['rug', 'dump', 'bearish', 'scam', 'fail', 'dead']
        # 中性词汇
        neutral_words = ['hodl', 'dyor', 'buy', 'sell', 'trade', 'invest']
        
        for word in positive_words + negative_words + neutral_words:
            if word in text and word not in keywords:
                keywords.append(word)
        
        return keywords
    
    def _extract_technology_keywords(self, text: str) -> List[str]:
        """提取技术关键词"""
        keywords = []
        
        tech_words = [
            'erc-20', 'bep-20', 'smart contract', 'blockchain', 'consensus',
            'proof of stake', 'proof of work', 'mining', 'staking', 'yield',
            'liquidity', 'amm', 'dex', 'cex', 'bridge', 'layer2'
        ]
        
        for word in tech_words:
            if word in text and word not in keywords:
                keywords.append(word)
        
        return keywords
    
    def _extract_community_keywords(self, text: str) -> List[str]:
        """提取社区关键词"""
        keywords = []
        
        community_words = [
            'hodl', 'diamond hands', 'paper hands', 'ape', 'fomo', 'fud',
            'community', 'family', 'together', 'strong', 'united', 'team'
        ]
        
        for word in community_words:
            if word in text and word not in keywords:
                keywords.append(word)
        
        return keywords
    
    def _extract_risk_keywords(self, text: str) -> List[str]:
        """提取风险信号关键词"""
        keywords = []
        
        risk_words = [
            'anonymous', 'no audit', 'high tax', 'locked liquidity', 'rug pull',
            'scam', 'ponzi', 'pyramid', 'get rich quick', 'guaranteed profit'
        ]
        
        for word in risk_words:
            if word in text and word not in keywords:
                keywords.append(word)
        
        return keywords
    
    def _extract_trending_hashtags(self, text: str, social_mentions: List[str]) -> List[str]:
        """提取流行标签"""
        hashtags = []
        
        # 从社交媒体提及中提取hashtag
        for mention in social_mentions:
            hashtag_matches = re.findall(r'#\w+', mention)
            hashtags.extend(hashtag_matches)
        
        # 常见加密货币标签
        common_hashtags = [
            '#cryptocurrency', '#crypto', '#blockchain', '#defi', '#nft',
            '#web3', '#bitcoin', '#ethereum', '#bsc', '#memecoin'
        ]
        
        # 添加常见标签
        for tag in common_hashtags:
            if tag.lower().replace('#', '') in text and tag not in hashtags:
                hashtags.append(tag)
        
        return list(set(hashtags))[:15]  # 去重并限制数量
    
    def _generate_keyword_summary(self, category: str, themes: List[str], 
                                sentiment: List[str], tech: List[str]) -> str:
        """生成关键词分析总结"""
        return f"""
关键词分析总结：

🏷️ 主要分类: {category}
🎯 核心主题: {', '.join(themes[:5]) if themes else '无明显主题'}
📊 情绪倾向: {', '.join(sentiment[:5]) if sentiment else '中性'}
⚡ 技术特征: {', '.join(tech[:3]) if tech else '基础代币'}

该代币主要定位为{category}，具有{len(themes)}个主题标签，
情绪关键词显示{'积极' if any(word in sentiment for word in ['moon', 'gem', 'bullish']) else '中性'}倾向。
        """.strip()

# ============ 工具导出函数 ============

def get_narrative_scoring_tools() -> List[BaseTool]:
    """获取叙事评分相关工具"""
    return [
        MultiDimensionalNarrativeScoringTool(),
        KeywordIdentificationTool()
    ]

if __name__ == "__main__":
    # 测试工具
    scoring_tool = MultiDimensionalNarrativeScoringTool()
    keyword_tool = KeywordIdentificationTool()
    
    # 测试数据
    test_result = scoring_tool._run(
        token_name="CatCoin",
        token_symbol="CAT",
        token_description="A community-driven meme token featuring cute cats",
        community_info={"telegram_members": 5000, "twitter_followers": 3000},
        market_data={"contract_verified": True, "liquidity_usd": 100000, "holder_count": 2000}
    )
    
    print("叙事评分测试结果:")
    print(f"总分: {test_result['total_narrative_score']}/100")
    print(f"等级: {test_result['score_grade']}")
