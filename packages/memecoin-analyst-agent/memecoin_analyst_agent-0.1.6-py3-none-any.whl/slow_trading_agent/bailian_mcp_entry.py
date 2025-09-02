"""
Memecoin智能分析Agent - 阿里云百炼MCP服务入口点
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import json

# 确保在任何情况下都能正确导入
try:
    from slow_trading_agent.core.agent_executor import create_memecoin_analyst
except ImportError:
    import sys
    import os
    # 将项目根目录添加到sys.path
    # 假设此脚本位于 slow_trading_agent/ 目录下
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from slow_trading_agent.core.agent_executor import create_memecoin_analyst

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BailianMcpAgent:
    """
    一个适配阿里云百炼MCP协议的Agent包装器。
    它直接暴露Agent的核心功能作为可调用的工具。
    """

    def __init__(self):
        """
        初始化Agent实例。
        这里的初始化是轻量级的，实际的工具和模型将在首次调用时懒加载。
        """
        self._agent = None
        logger.info("BailianMcpAgent has been initialized.")

    @property
    def agent(self):
        """懒加载Agent实例，确保只在需要时创建"""
        if self._agent is None:
            logger.info("Lazy loading MemecoinAnalystAgent...")
            # 从环境变量中获取API密钥和模型配置（如果百炼平台支持）
            # 否则使用默认值
            self._agent = create_memecoin_analyst(
                verbose=True # 在百炼日志中打印详细过程
            )
            logger.info("MemecoinAnalystAgent created successfully.")
        return self._agent

    def _format_error_output(self, error: Exception) -> str:
        """格式化错误输出"""
        error_report = {
            "status": "failed",
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        return json.dumps(error_report, ensure_ascii=False, indent=2)

    def analyze_token(self, token_address: str, additional_context: str = "") -> str:
        """
        MCP工具：分析指定的BSC代币地址。

        :param token_address: 要分析的BSC代币合约地址。
        :param additional_context: (可选) 关于此代币的任何已知附加上下文信息。
        :return: JSON格式的分析报告字符串。
        """
        logger.info(f"Received request for analyze_token with address: {token_address}")
        try:
            # 调用核心Agent的分析方法
            # 这是同步执行的，百炼MCP会处理它
            result = self.agent.analyze_token(token_address, additional_context)

            # 提取并格式化最终的报告
            if result.get("status") == "completed" and result.get("parsed_report"):
                # 如果成功并解析出报告，直接返回报告
                return json.dumps(result["parsed_report"], ensure_ascii=False, indent=2)
            elif result.get("status") == "completed":
                # 如果成功但没有解析出报告，返回原始输出
                return json.dumps({
                    "status": "completed_with_parsing_error",
                    "raw_output": result.get("agent_output"),
                    "tool_calls": result.get("tool_calls")
                }, ensure_ascii=False, indent=2)
            else:
                # 如果失败，返回包含错误信息的完整结果
                return json.dumps(result, ensure_ascii=False, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error during token analysis for {token_address}: {e}", exc_info=True)
            return self._format_error_output(e)

# 创建一个全局实例供uvx使用
memecoin_analyst_app = BailianMcpAgent()
