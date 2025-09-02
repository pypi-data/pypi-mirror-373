#!/usr/bin/env python3
"""
健壮的MCP服务器 - 移植完整的本地Agent逻辑以确保云端一致性
"""

import json
import sys
import asyncio
import os
import logging
import traceback
from typing import Dict, Any, Union

# 确保在任何情况下都能正确导入Agent核心
try:
    from slow_trading_agent.core.agent_executor import create_memecoin_analyst, MemecoinAnalystAgent
except (ImportError, ModuleNotFoundError):
    # 兼容直接运行或通过uvx部署时的路径问题
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from slow_trading_agent.core.agent_executor import create_memecoin_analyst, MemecoinAnalystAgent

# 配置日志（强制输出到stderr，避免干扰MCP的stdout通信）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

class MemecoinAgentMCP:
    """
    一个健壮的MCP服务器，它包装了完整的MemecoinAnalystAgent。
    这确保了完整的ReAct分析过程在服务器端执行，与本地环境保持一致。
    """
    
    def __init__(self):
        self._agent: Union[MemecoinAnalystAgent, None] = None
        self.tools = [
            {
                "name": "analyze_token",
                "description": "对指定的BSC代币地址进行完整、深入的AI分析，并返回一份结构化的JSON分析报告。",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "token_address": {"type": "string", "description": "要分析的BSC代币合约地址。"},
                        "additional_context": {"type": "string", "description": "关于此代币的任何已知附加上下文信息（可选）。"}
                    },
                    "required": ["token_address"]
                }
            }
        ]

    async def _safe_api_call(self, func, *args, **kwargs):
        """安全的API调用包装器，防止None值导致的错误"""
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # 如果结果是None，返回安全的空字典
            if result is None:
                logger.warning(f"API调用 {func.__name__} 返回None，使用空字典替代")
                return {}
            
            return result
        except Exception as e:
            logger.error(f"API调用 {func.__name__} 失败: {e}")
            return {}

    def _get_agent_instance(self) -> MemecoinAnalystAgent:
        """
        懒加载并返回MemecoinAnalystAgent的单例。
        从阿里云百炼平台的环境变量中读取配置。
        """
        if self._agent is None:
            logger.info("首次调用，正在初始化MemecoinAnalystAgent实例...")
            
            # 从环境变量中读取配置，并提供安全的默认值
            api_key = os.environ.get("OPENAI_API_KEY")
            base_url = os.environ.get("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
            model = os.environ.get("AGENT_MODEL", "qwen-plus")
            
            if not api_key:
                logger.error("关键环境变量 OPENAI_API_KEY 未设置！Agent可能无法工作。")
                # 在没有API密钥的情况下，Agent将无法初始化LLM，后续调用会失败
                # 这种失败会被捕获并以错误信息形式返回
            
            # 创建完整的Agent实例（加入兜底保护，避免初始化失败返回None）
            try:
                self._agent = create_memecoin_analyst(
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                    verbose=True  # 在云端开启详细日志以方便调试
                )
                logger.info(f"Agent实例创建成功，模型: '{model}', 端点: '{base_url}'")
            except Exception as e:
                logger.error(f"Agent实例创建失败: {e}")
                # 提供一个轻量的兜底对象，保证后续调用不会返回None
                class _FallbackAgent:
                    def analyze_token(self, token_address: str, additional_context: str = ""):
                        return {
                            "token_address": token_address,
                            "status": "failed",
                            "error": f"Agent初始化失败: {str(e)}"
                        }
                self._agent = _FallbackAgent()  # type: ignore
        return self._agent

    async def analyze_token_in_executor(self, token_address: str, additional_context: str = "") -> Dict[str, Any]:
        """在asyncio的执行器中运行同步的Agent分析，以避免阻塞事件循环。"""
        try:
            loop = asyncio.get_running_loop()
            agent = self._get_agent_instance()
            
            # 使用安全的API调用包装器
            def safe_agent_analyze():
                try:
                    result = agent.analyze_token(token_address, additional_context)
                    if result is None:
                        logger.warning("Agent.analyze_token 返回None，使用默认结构")
                        return {
                            "status": "error",
                            "message": "分析失败：Agent返回空结果",
                            "token_address": token_address
                        }
                    return result
                except Exception as e:
                    logger.error(f"Agent分析过程出错: {e}")
                    return {
                        "status": "error", 
                        "message": f"分析出错: {str(e)}",
                        "token_address": token_address
                    }
            
            # run_in_executor用于在独立的线程中运行阻塞的同步代码
            result = await loop.run_in_executor(
                None,  # 使用默认的ThreadPoolExecutor
                safe_agent_analyze
            )
            return result
        except Exception as e:
            logger.error(f"analyze_token_in_executor 失败: {e}")
            return {
                "status": "error",
                "message": f"执行器错误: {str(e)}",
                "token_address": token_address
            }

async def safe_handle_request(data: Dict[str, Any], analyst: MemecoinAgentMCP) -> Dict[str, Any]:
    """安全地处理来自百炼平台的MCP请求"""
    # 额外的输入验证防护
    if not data:
        logger.error("收到空的请求数据")
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32600, "message": "无效请求：数据为空"}
        }
    
    request_id = data.get("id", 1) if data else 1
    try:
        method = data.get("method", "")
        params = data.get("params", {})
        
        # 确保params不是None
        if params is None:
            params = {}
        
        logger.info(f"收到请求: method={method}, id={request_id}")
        
        # MCP 初始化握手：告知平台本服务具备 tools 能力
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "memecoin-analyst",
                        "version": "0.1.0"
                    }
                }
            }
        
        # 简单探活
        if method == "ping":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"ok": True}
            }
        
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": analyst.tools}
            }
        
        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            
            # 确保arguments不是None
            if arguments is None:
                arguments = {}
            
            logger.info(f"调用工具: {tool_name}, 参数: {arguments}")
            
            content = ""
            if tool_name == "analyze_token":
                token_address = arguments.get("token_address", "")
                additional_context = arguments.get("additional_context", "")
                
                # 进一步的参数与类型校验，防止 NoneType 传入
                if token_address is None:
                    token_address = ""
                if additional_context is None:
                    additional_context = ""
                if not isinstance(token_address, str):
                    token_address = str(token_address)
                if not isinstance(additional_context, str):
                    additional_context = str(additional_context)
                
                if not token_address:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32602, "message": "缺少必需参数 token_address"}
                    }
                
                # 调用完整的Agent进行分析
                agent_result = await analyst.analyze_token_in_executor(
                    token_address,
                    additional_context
                )
                
                # 确保agent_result不是None
                if agent_result is None:
                    logger.error("analyze_token_in_executor返回None")
                    agent_result = {
                        "status": "error",
                        "error": "分析失败：返回空结果",
                        "token_address": token_address
                    }
                
                # 根据Agent的分析结果决定最终输出
                status_val = agent_result.get("status") if isinstance(agent_result, dict) else None
                parsed = agent_result.get("parsed_report") if isinstance(agent_result, dict) else None
                if status_val == "completed" and parsed:
                    # 成功，返回解析好的JSON报告字符串
                    final_report_json = parsed
                    
                    # 确保final_report_json不是None
                    if final_report_json is None:
                        logger.error("parsed_report是None")
                        final_report_json = {
                            "status": "error",
                            "error": "报告解析失败",
                            "token_address": token_address
                        }
                    
                    content = json.dumps(final_report_json, ensure_ascii=False, indent=2)
                    logger.info("Agent分析成功，返回完整报告JSON。")
                else:
                    # 失败，返回结构化的错误信息JSON
                    error_info = {
                        "status": "failed",
                        "error": agent_result.get("error") if isinstance(agent_result, dict) else "Agent返回格式异常",
                        "details": agent_result.get("parse_error") if isinstance(agent_result, dict) else "无法解析Agent返回"
                    }
                    content = json.dumps(error_info, ensure_ascii=False, indent=2)
                    logger.error(f"Agent分析失败或无法解析报告: {content}")
            else:
                content = json.dumps({"status": "failed", "error": f"不支持的工具: {tool_name}"})

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": content}]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }
    
    except Exception as e:
        logger.error(f"请求处理时发生严重异常: {e}", exc_info=True)
        traceback.print_exc()
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": f"Internal server error: {str(e)}"}
        }

async def main():
    """主函数 - MCP服务器入口"""
    analyst = MemecoinAgentMCP()
    logger.info("健壮版MCP服务器启动，内含完整Agent实例。")
    
    try:
        while True:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                logger.info("接收到EOF，正在关闭服务器。")
                break
            
            if not line.strip():
                continue
                
            try:
                data = json.loads(line)
                response = await safe_handle_request(data, analyst)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                logger.error(f"JSON解析错误: {line.strip()}")
                print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}}), flush=True)
            except Exception as e:
                logger.error(f"主循环中发生未捕获的异常: {e}", exc_info=True)
                print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": f"Unhandled server error: {e}"}}), flush=True)
    
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("接收到中断信号，服务器关闭。")
    finally:
        logger.info("服务器已关闭。")

def cli():
    """为 `pyproject.toml` 的 `console_scripts` 提供的同步入口点。"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    cli()
