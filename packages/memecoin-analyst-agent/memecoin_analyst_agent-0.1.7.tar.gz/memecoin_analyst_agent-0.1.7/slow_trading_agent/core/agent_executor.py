"""
Agent执行器模块
集成LLM、工具和Prompt，创建可运行的ReAct Agent
"""

from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime
import sys
import os

# This ensures that the 'slow_trading_agent' directory is on the path
# allowing for absolute imports from 'tools' etc.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.streamlined_agent_prompt import create_streamlined_prompt
from enhanced_real_data_tools import create_real_data_tools
from tools.sentiment_analysis_tools import NarrativeAnalysisTool
from tools.optimistic_scoring_tools import get_optimistic_narrative_tools
from tools.narrative_scoring_tools import KeywordIdentificationTool
from tools.memory_tools import MarketCapPredictionTool
from enhanced_real_data_tools import QuickTokenAnalysisTool

logger = logging.getLogger(__name__)

# ============ 自定义回调处理器 ============

class TradingAgentCallback(BaseCallbackHandler):
    """交易Agent的回调处理器，用于记录分析过程"""
    
    def __init__(self):
        self.analysis_log = []
        self.start_time = None
        self.tool_calls = []
        
    def on_agent_action(self, action, **kwargs):
        """记录Agent执行的动作"""
        self.tool_calls.append({
            "tool": action.tool,
            "input": action.tool_input,
            "timestamp": datetime.now().isoformat()
        })
        logger.info(f"Agent调用工具: {action.tool}")
        
    def on_tool_end(self, output, **kwargs):
        """记录工具执行结果"""
        if self.tool_calls:
            self.tool_calls[-1]["output"] = str(output)[:200] + "..." if len(str(output)) > 200 else str(output)
            
    def on_agent_finish(self, finish, **kwargs):
        """记录Agent完成分析"""
        end_time = datetime.now()
        if self.start_time:
            duration = (end_time - self.start_time).total_seconds()
            logger.info(f"分析完成，耗时: {duration:.2f}秒")

# ============ Agent执行器类 ============

class MemecoinAnalystAgent:
    """Memecoin分析师Agent"""
    
    def __init__(
        self,
        llm_model: str = "qwen-plus",
        api_key: str = "sk-b5f98f958e914b589f4fd8ffd25915ab",
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature: float = 0.0,
        max_iterations: int = 15, # 减少迭代次数以加快速度
        verbose: bool = True,
        memory_manager=None
    ):
        """
        初始化Memecoin分析师Agent
        
        Args:
            llm_model: 使用的大语言模型
            api_key: API密钥
            base_url: API基础URL
            temperature: 模型温度参数
            max_iterations: 最大迭代次数
            verbose: 是否显示详细日志
        """
        self.llm = ChatOpenAI(
            model=llm_model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_retries=3,  # 添加重试次数
            request_timeout=60.0  # 增加超时时间
        )
        
        # 收集核心工具（精简版）
        self.tools = []
        # 只保留四项核心分析所需的最少工具
        
        # 基础数据工具（代币信息和价格）
        self.tools.extend(create_real_data_tools())
        
        # 叙事分析工具
        self.tools.append(NarrativeAnalysisTool())
        
        # 乐观版多维叙事评分 & 关键词识别工具
        self.tools.extend(get_optimistic_narrative_tools())
        self.tools.append(KeywordIdentificationTool())

        # 市值预测工具
        self.tools.append(MarketCapPredictionTool())
        
        # 创建精简版Prompt模板
        self.prompt = create_streamlined_prompt()
        
        # 创建ReAct Agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # 创建Agent执行器
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            max_iterations=max_iterations,
            verbose=verbose,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
        
        logger.info(f"MemecoinAnalystAgent初始化完成，加载了{len(self.tools)}个工具")

    def analyze_token(self, token_address: str, additional_context: str = "") -> Dict[str, Any]:
        """
        分析指定的代币
        
        Args:
            token_address: 代币合约地址
            additional_context: 额外的上下文信息
            
        Returns:
            分析结果字典
        """
        callback = TradingAgentCallback()
        callback.start_time = datetime.now()
        
        try:
            import time
            
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    # 预获取token_summary，作为可靠基础数据传递给Agent
                    prefetch_observation = None
                    try:
                        quick_tool = QuickTokenAnalysisTool()
                        quick_raw = quick_tool._run(token_address)
                        if isinstance(quick_raw, str):
                            quick_json = json.loads(quick_raw)
                        else:
                            quick_json = quick_raw
                        if isinstance(quick_json, dict) and quick_json.get("status") == "success":
                            prefetch_observation = quick_json.get("token_summary") or quick_json
                            # 记录到tool_calls，保证可见性
                            callback.tool_calls.append({
                                "tool": "quick_token_analysis(prefetch)",
                                "input": token_address,
                                "timestamp": datetime.now().isoformat(),
                                "output": json.dumps(prefetch_observation)[:200] + ("..." if len(json.dumps(prefetch_observation))>200 else "")
                            })
                        else:
                            # 记录失败
                            callback.tool_calls.append({
                                "tool": "quick_token_analysis(prefetch)",
                                "input": token_address,
                                "timestamp": datetime.now().isoformat(),
                                "output": str(quick_json)[:200]
                            })
                    except Exception as _:
                        pass

                    # 构建分析任务描述（明确参数格式要求，避免传错字段）
                    pre_observation_block = (
                        f"已预获取的token_summary供你使用（无需重复获取）：\n{json.dumps(prefetch_observation, ensure_ascii=False)}\n\n"
                        if prefetch_observation else ""
                    )
                    task_description = f"""
                    请分析以下代币：{token_address}
                    
                    {additional_context if additional_context else ""}
                    
                    {pre_observation_block}
                    必须遵循：
                    - 第一步先使用 quick_token_analysis（若已在上方提供token_summary，可直接使用）。
                    - 当调用 narrative_analysis 时，参数格式必须为：{{"token_symbol": "<symbol>", "token_address": "{token_address}"}}
                    - 当调用 keyword_identification_classification 时，参数格式必须为：{{"token_symbol": "<symbol>"}}
                    - 当调用 market_cap_prediction_analysis 时，参数格式必须为：{{"current_market_cap": <数字>, "token_category": "<分类>"}}
                    - 报告中所有字段必须来源于工具的Observation。
                    
                    请按照你的标准工作流程进行全面分析，最终生成完整的JSON格式报告。
                    """
                    
                    logger.info(f"开始分析代币: {token_address}")
                    
                    # 执行分析
                    result = self.agent_executor.invoke(
                        {"input": task_description},
                        config={"callbacks": [callback]}
                    )
                    
                    # 如果未调用任何工具，强制重试一次并显式要求调用quick_token_analysis
                    if not callback.tool_calls:
                        logger.warning("首次执行未发生任何工具调用，将以更严格的指令重试一次...")
                        strict_task = task_description + "\n\n重要：你必须首先调用 quick_token_analysis（失败时调用 get_comprehensive_token_data）。在看到工具的Observation之前，严禁输出Final Answer。"
                        result = self.agent_executor.invoke(
                            {"input": strict_task},
                            config={"callbacks": [callback]}
                        )
                    
                    # 如果依然没有工具调用，直接返回失败，禁止输出编造报告
                    if not callback.tool_calls:
                        logger.error("本次分析未调用任何工具，拒绝生成报告。")
                        return {
                            "token_address": token_address,
                            "analysis_time": datetime.now().isoformat(),
                            "status": "failed",
                            "error": "未调用任何工具，已拒绝输出以避免编造数据",
                            "tool_calls": []
                        }
                    
                    # 如果成功，跳出重试循环
                    break
                    
                except Exception as e:
                    error_msg = str(e)
                    if attempt < max_retries and ("peer closed connection" in error_msg.lower() or 
                                                "connection" in error_msg.lower() or 
                                                "timeout" in error_msg.lower() or
                                                "chunked read" in error_msg.lower()):
                        logger.warning(f"网络连接错误，第{attempt + 1}次重试... 错误: {error_msg}")
                        time.sleep(3)  # 等待3秒后重试
                        continue
                    else:
                        # 如果不是网络错误或已达到最大重试次数，抛出异常
                        raise e
            
            # 解析结果
            analysis_result = {
                "token_address": token_address,
                "analysis_time": datetime.now().isoformat(),
                "status": "completed",
                "agent_output": result["output"],
                "tool_calls": callback.tool_calls,
                "intermediate_steps": result.get("intermediate_steps", [])
            }
            
            # 始终尝试从最终输出和中间步骤中解析JSON报告
            parsed_report = None
            
            # 1. 尝试从Agent的最终输出解析
            output_text = result.get("output", "")
            try:
                if "```json" in output_text:
                    json_start = output_text.find("```json") + 7
                    json_end = output_text.rfind("```")
                    json_text = output_text[json_start:json_end].strip()
                    parsed_report = json.loads(json_text)
                elif output_text.strip().startswith('{'):
                    json_start = output_text.find("{")
                    json_end = output_text.rfind("}") + 1
                    json_text = output_text[json_start:json_end]
                    parsed_report = json.loads(json_text)
                
                # 如果解析出的JSON不是有效的报告，则将其作废
                if parsed_report and not self._is_valid_analysis_report(parsed_report):
                    parsed_report = None
            except json.JSONDecodeError:
                parsed_report = None
            
            # 2. 如果最终输出中没有找到报告，则从中间步骤中提取
            if not parsed_report:
                logger.warning("无法从Agent最终输出中解析有效报告，正在尝试从中间步骤中提取...")
                intermediate_steps = result.get("intermediate_steps", [])
                parsed_report = self._extract_json_from_steps(intermediate_steps)

            # 3. 将最终解析结果存入分析报告
            if parsed_report:
                analysis_result["parsed_report"] = parsed_report
                analysis_result["agent_output"] = json.dumps(parsed_report, ensure_ascii=False, indent=2) # 用干净的JSON覆盖原始输出
                logger.info("✅ 成功从Agent的执行过程中提取到完整的AI分析报告！")
            else:
                analysis_result["parse_error"] = "无法从Agent的输出和中间步骤中找到有效的JSON报告。"
                logger.error(f"❌ {analysis_result['parse_error']}")

            logger.info(f"代币分析完成: {token_address}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"代币分析失败: {e}")
            return {
                "token_address": token_address,
                "analysis_time": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e),
                "tool_calls": callback.tool_calls
            }

    def batch_analyze_tokens(self, token_addresses: List[str]) -> List[Dict[str, Any]]:
        """
        批量分析多个代币
        
        Args:
            token_addresses: 代币地址列表
            
        Returns:
            分析结果列表
        """
        results = []
        
        for i, token_address in enumerate(token_addresses, 1):
            logger.info(f"批量分析进度: {i}/{len(token_addresses)} - {token_address}")
            
            try:
                result = self.analyze_token(token_address)
                results.append(result)
                
            except Exception as e:
                logger.error(f"批量分析中的代币失败: {token_address}, 错误: {e}")
                results.append({
                    "token_address": token_address,
                    "status": "failed",
                    "error": str(e)
                })
        
        logger.info(f"批量分析完成，成功: {len([r for r in results if r.get('status') == 'completed'])}/{len(token_addresses)}")
        return results

    def get_agent_info(self) -> Dict[str, Any]:
        """获取Agent的信息"""
        return {
            "model": self.llm.model_name,
            "tools_count": len(self.tools),
            "available_tools": [tool.name for tool in self.tools],
            "max_iterations": self.agent_executor.max_iterations,
            "agent_type": "ReAct"
        }
    
    def _extract_json_from_steps(self, intermediate_steps: List) -> Dict[str, Any]:
        """从中间步骤中提取有效的JSON报告"""
        # 首先尝试从最后几个步骤中查找完整的JSON
        for step in reversed(intermediate_steps):
            if isinstance(step, str):
                step_text = step
            elif hasattr(step, 'log'):
                step_text = step.log
            elif isinstance(step, tuple) and len(step) >= 1:
                step_text = str(step[0])
            else:
                continue
            
            # 查找包含四个核心部分的JSON
            if ('{' in step_text and '}' in step_text and 
                'narrative_analysis_summary' in step_text and
                'multi_dimensional_narrative_scores' in step_text):
                
                # 尝试多种JSON提取方法
                json_candidates = []
                
                # 方法1: 提取```json...```块
                import re
                json_blocks = re.findall(r'```json\s*(.*?)\s*```', step_text, re.DOTALL)
                json_candidates.extend(json_blocks)
                
                # 方法2: 提取最大的{}块
                brace_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', step_text, re.DOTALL)
                json_candidates.extend(brace_matches)
                
                # 方法3: 从第一个{到最后一个}
                if '{' in step_text and '}' in step_text:
                    json_start = step_text.find('{')
                    json_end = step_text.rfind('}') + 1
                    json_candidates.append(step_text[json_start:json_end])
                
                # 尝试解析每个候选JSON
                for json_text in json_candidates:
                    try:
                        parsed = json.loads(json_text.strip())
                        if self._is_valid_analysis_report(parsed):
                            logger.info("成功从中间步骤提取到有效的分析报告")
                            return parsed
                    except:
                        continue
        
        return None
    
    def _is_valid_analysis_report(self, data: Dict[str, Any]) -> bool:
        """验证是否是有效的分析报告 - 专注于四个核心部分"""
        required_keys = [
            "narrative_analysis_summary", 
            "keyword_identification_classification",
            "market_cap_analysis",
            "multi_dimensional_narrative_scores"
        ]
        return all(key in data for key in required_keys)

# ============ 工厂函数 ============

def create_memecoin_analyst(
    api_key: str = "sk-b5f98f958e914b589f4fd8ffd25915ab",
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
    model: str = "qwen-plus",
    verbose: bool = True,
    memory_manager=None
) -> MemecoinAnalystAgent:
    """
    创建Memecoin分析师Agent的工厂函数
    
    Args:
        api_key: API密钥
        base_url: API基础URL
        model: 模型名称
        verbose: 是否显示详细日志
        
    Returns:
        配置好的MemecoinAnalystAgent实例
    """
    return MemecoinAnalystAgent(
        llm_model=model,
        api_key=api_key,
        base_url=base_url,
        verbose=verbose,
        memory_manager=memory_manager
    )

# ============ 测试和演示函数 ============

def demo_analysis():
    """演示分析功能"""
    agent = create_memecoin_analyst()
    
    # 演示单个代币分析
    test_token = "0x1234567890abcdef1234567890abcdef12345678"
    result = agent.analyze_token(test_token, "这是一个新发现的猫主题Meme币")
    
    print("=== 分析结果演示 ===")
    print(f"代币地址: {result['token_address']}")
    print(f"分析状态: {result['status']}")
    print(f"工具调用次数: {len(result.get('tool_calls', []))}")
    
    if result.get('parsed_report'):
        print("成功解析JSON报告")
        report = result['parsed_report']
        if 'multi_dimensional_scores' in report:
            scores = report['multi_dimensional_scores']
            print(f"整体评分: {scores.get('overall_score', 'N/A')}")
    
    return result

if __name__ == "__main__":
    # 运行演示
    demo_analysis()
