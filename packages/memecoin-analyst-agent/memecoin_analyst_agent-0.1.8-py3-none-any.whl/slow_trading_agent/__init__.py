"""
慢速交易工作流 - 基于LangChain + ReAct架构的Memecoin智能分析系统

主要组件:
- tools: 各类分析工具 (数据查询、情绪分析、风险评估)
- core: Agent核心 (Prompt模板、执行器)
- controller: 工作流控制器 (任务调度、批量处理)
"""

from .core.agent_executor import MemecoinAnalystAgent, create_memecoin_analyst
from .controller.slow_trading_controller import SlowTradingController, create_slow_trading_controller
from .memory.analysis_memory import AnalysisMemoryManager, create_analysis_memory_manager

__version__ = "1.0.0"
__author__ = "Memecoin Trading Team"

# 导出主要接口
__all__ = [
    "MemecoinAnalystAgent",
    "create_memecoin_analyst", 
    "SlowTradingController",
    "create_slow_trading_controller",
    "AnalysisMemoryManager",
    "create_analysis_memory_manager"
]
