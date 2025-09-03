"""
慢速交易工作流主控制器
负责调度和管理整个慢速交易分析流程
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

try:
    from ..core.agent_executor import MemecoinAnalystAgent, create_memecoin_analyst
    from ..memory.analysis_memory import AnalysisMemoryManager, create_analysis_memory_manager
except ImportError:
    # 当模块被直接导入时使用绝对导入
    import sys
    import os
    # 添加slow_trading_agent根目录到路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from core.agent_executor import MemecoinAnalystAgent, create_memecoin_analyst
    from memory.analysis_memory import AnalysisMemoryManager, create_analysis_memory_manager

logger = logging.getLogger(__name__)

# ============ 数据结构定义 ============

class AnalysisStatus(Enum):
    """分析状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TokenDiscovery:
    """代币发现记录"""
    token_address: str
    discovery_source: str  # "websocket", "manual", "scheduled"
    discovery_time: datetime
    additional_context: str = ""
    priority: int = 5  # 1-10, 10最高优先级

@dataclass
class AnalysisTask:
    """分析任务"""
    task_id: str
    token_discovery: TokenDiscovery
    status: AnalysisStatus
    created_time: datetime
    started_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0

# ============ 主控制器类 ============

class SlowTradingController:
    """慢速交易工作流主控制器"""
    
    def __init__(
        self,
        agent_config: Dict[str, Any] = None,
        max_concurrent_analyses: int = 2,
        analysis_timeout_minutes: int = 10,
        max_retries: int = 2,
        data_dir: str = "slow_trading_data",
        enable_memory: bool = True
    ):
        """
        初始化慢速交易控制器
        
        Args:
            agent_config: Agent配置参数
            max_concurrent_analyses: 最大并发分析数
            analysis_timeout_minutes: 分析超时时间（分钟）
            max_retries: 最大重试次数
            data_dir: 数据存储目录
        """
        self.agent_config = agent_config or {}
        self.max_concurrent_analyses = max_concurrent_analyses
        self.analysis_timeout = timedelta(minutes=analysis_timeout_minutes)
        self.max_retries = max_retries
        
        # 创建数据目录
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 任务管理
        self.pending_tasks: List[AnalysisTask] = []
        self.active_tasks: Dict[str, AnalysisTask] = {}
        self.completed_tasks: List[AnalysisTask] = []
        self.failed_tasks: List[AnalysisTask] = []
        
        # Agent实例（延迟初始化）
        self._agent: Optional[MemecoinAnalystAgent] = None
        
        # 记忆模块
        self.enable_memory = enable_memory
        self._memory_manager: Optional[AnalysisMemoryManager] = None
        
        # 回调函数
        self.on_analysis_complete: Optional[Callable[[AnalysisTask], None]] = None
        self.on_analysis_failed: Optional[Callable[[AnalysisTask], None]] = None
        
        # 运行状态
        self.is_running = False
        self.worker_tasks: List[asyncio.Task] = []
        
        logger.info("SlowTradingController初始化完成")

    @property
    def agent(self) -> MemecoinAnalystAgent:
        """获取Agent实例（懒加载）"""
        if self._agent is None:
            # 将memory_manager传递给Agent
            agent_config_with_memory = {**self.agent_config}
            if self.enable_memory:
                agent_config_with_memory["memory_manager"] = self.memory_manager
            self._agent = create_memecoin_analyst(**agent_config_with_memory)
        return self._agent

    @property
    def memory_manager(self) -> Optional[AnalysisMemoryManager]:
        """获取记忆管理器实例（懒加载）"""
        if self.enable_memory and self._memory_manager is None:
            memory_db_path = self.data_dir / "analysis_memory.db"
            self._memory_manager = create_analysis_memory_manager(str(memory_db_path))
        return self._memory_manager

    # ============ 任务管理 ============

    def add_token_for_analysis(
        self,
        token_address: str,
        source: str = "manual",
        context: str = "",
        priority: int = 5
    ) -> str:
        """
        添加代币到分析队列
        
        Args:
            token_address: 代币合约地址
            source: 发现来源
            context: 额外上下文
            priority: 优先级
            
        Returns:
            任务ID
        """
        # 检查是否已存在
        for task in self.pending_tasks + list(self.active_tasks.values()) + self.completed_tasks:
            if task.token_discovery.token_address.lower() == token_address.lower():
                logger.info(f"代币已存在于队列中: {token_address}")
                return task.task_id
        
        # 创建新任务
        discovery = TokenDiscovery(
            token_address=token_address,
            discovery_source=source,
            discovery_time=datetime.now(),
            additional_context=context,
            priority=priority
        )
        
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{token_address[-6:]}"
        task = AnalysisTask(
            task_id=task_id,
            token_discovery=discovery,
            status=AnalysisStatus.PENDING,
            created_time=datetime.now()
        )
        
        # 按优先级插入队列
        inserted = False
        for i, pending_task in enumerate(self.pending_tasks):
            if priority > pending_task.token_discovery.priority:
                self.pending_tasks.insert(i, task)
                inserted = True
                break
        
        if not inserted:
            self.pending_tasks.append(task)
        
        logger.info(f"新增分析任务: {task_id} ({token_address}), 优先级: {priority}")
        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        # 查找任务
        task = None
        for task_list in [self.pending_tasks, list(self.active_tasks.values()), 
                         self.completed_tasks, self.failed_tasks]:
            for t in task_list:
                if t.task_id == task_id:
                    task = t
                    break
            if task:
                break
        
        if not task:
            return None
        
        return {
            "task_id": task.task_id,
            "token_address": task.token_discovery.token_address,
            "status": task.status.value,
            "created_time": task.created_time.isoformat(),
            "started_time": task.started_time.isoformat() if task.started_time else None,
            "completed_time": task.completed_time.isoformat() if task.completed_time else None,
            "retry_count": task.retry_count,
            "has_result": task.result is not None,
            "error_message": task.error_message
        }

    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        return {
            "pending_count": len(self.pending_tasks),
            "active_count": len(self.active_tasks),
            "completed_count": len(self.completed_tasks),
            "failed_count": len(self.failed_tasks),
            "is_running": self.is_running,
            "next_tasks": [
                {
                    "task_id": task.task_id,
                    "token_address": task.token_discovery.token_address,
                    "priority": task.token_discovery.priority
                }
                for task in self.pending_tasks[:5]  # 显示前5个待处理任务
            ]
        }

    # ============ 工作流执行 ============

    async def start_processing(self):
        """启动处理循环"""
        if self.is_running:
            logger.warning("处理循环已在运行")
            return
        
        self.is_running = True
        logger.info("启动慢速交易工作流处理")
        
        # 启动记忆模块验证循环
        if self.memory_manager:
            await self.memory_manager.start_verification_loop(check_interval_hours=6)
            logger.info("记忆验证循环已启动")
        
        # 启动工作线程
        for i in range(self.max_concurrent_analyses):
            worker_task = asyncio.create_task(self._worker_loop(f"worker_{i}"))
            self.worker_tasks.append(worker_task)
        
        # 启动监控任务
        monitor_task = asyncio.create_task(self._monitor_loop())
        self.worker_tasks.append(monitor_task)

    async def stop_processing(self):
        """停止处理循环"""
        if not self.is_running:
            return
        
        logger.info("停止慢速交易工作流处理")
        self.is_running = False
        
        # 停止记忆模块验证循环
        if self.memory_manager:
            await self.memory_manager.stop_verification_loop()
            logger.info("记忆验证循环已停止")
        
        # 取消所有工作任务
        for task in self.worker_tasks:
            task.cancel()
        
        # 等待任务完成
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks.clear()

    async def _worker_loop(self, worker_name: str):
        """工作线程循环"""
        logger.info(f"启动工作线程: {worker_name}")
        
        while self.is_running:
            try:
                # 获取下一个任务
                if not self.pending_tasks:
                    await asyncio.sleep(1)
                    continue
                
                task = self.pending_tasks.pop(0)
                task.status = AnalysisStatus.IN_PROGRESS
                task.started_time = datetime.now()
                self.active_tasks[task.task_id] = task
                
                logger.info(f"{worker_name} 开始处理任务: {task.task_id}")
                
                # 执行分析
                try:
                    result = await self._execute_analysis(task)
                    await self._handle_analysis_success(task, result)
                    
                except Exception as e:
                    await self._handle_analysis_failure(task, str(e))
                
            except asyncio.CancelledError:
                logger.info(f"工作线程被取消: {worker_name}")
                break
            except Exception as e:
                logger.error(f"工作线程异常: {worker_name}, {e}")
                await asyncio.sleep(5)

    async def _monitor_loop(self):
        """监控循环，处理超时任务"""
        while self.is_running:
            try:
                current_time = datetime.now()
                timeout_tasks = []
                
                for task_id, task in self.active_tasks.items():
                    if task.started_time and (current_time - task.started_time) > self.analysis_timeout:
                        timeout_tasks.append(task_id)
                
                # 处理超时任务
                for task_id in timeout_tasks:
                    task = self.active_tasks.pop(task_id)
                    await self._handle_analysis_failure(task, "分析超时")
                
                await asyncio.sleep(30)  # 每30秒检查一次
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"监控循环异常: {e}")
                await asyncio.sleep(10)

    async def _execute_analysis(self, task: AnalysisTask) -> Dict[str, Any]:
        """执行代币分析"""
        token_address = task.token_discovery.token_address
        context = task.token_discovery.additional_context
        
        # 在独立的线程中执行同步的Agent分析
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            self.agent.analyze_token, 
            token_address, 
            context
        )
        
        return result

    async def _handle_analysis_success(self, task: AnalysisTask, result: Dict[str, Any]):
        """处理分析成功"""
        task.status = AnalysisStatus.COMPLETED
        task.completed_time = datetime.now()
        task.result = result
        
        # 从活跃任务中移除
        self.active_tasks.pop(task.task_id, None)
        self.completed_tasks.append(task)
        
        # 保存结果
        await self._save_analysis_result(task)
        
        # 记录到记忆模块
        if self.memory_manager and result.get('parsed_report'):
            try:
                memory_id = await self.memory_manager.record_analysis(result)
                logger.info(f"分析结果已记录到记忆模块: {memory_id}")
            except Exception as e:
                logger.error(f"记录到记忆模块失败: {e}")
        
        # 调用回调
        if self.on_analysis_complete:
            try:
                self.on_analysis_complete(task)
            except Exception as e:
                logger.error(f"分析完成回调异常: {e}")
        
        logger.info(f"分析完成: {task.task_id} ({task.token_discovery.token_address})")

    async def _handle_analysis_failure(self, task: AnalysisTask, error_message: str):
        """处理分析失败"""
        task.error_message = error_message
        task.retry_count += 1
        
        # 从活跃任务中移除
        self.active_tasks.pop(task.task_id, None)
        
        # 判断是否重试
        if task.retry_count <= self.max_retries:
            task.status = AnalysisStatus.PENDING
            # 降低优先级并重新加入队列
            task.token_discovery.priority = max(1, task.token_discovery.priority - 1)
            self.pending_tasks.append(task)
            logger.warning(f"分析失败，将重试: {task.task_id}, 错误: {error_message}")
        else:
            task.status = AnalysisStatus.FAILED
            task.completed_time = datetime.now()
            self.failed_tasks.append(task)
            
            # 调用失败回调
            if self.on_analysis_failed:
                try:
                    self.on_analysis_failed(task)
                except Exception as e:
                    logger.error(f"分析失败回调异常: {e}")
            
            logger.error(f"分析最终失败: {task.task_id}, 错误: {error_message}")

    # ============ 数据持久化 ============

    async def _save_analysis_result(self, task: AnalysisTask):
        """保存分析结果"""
        try:
            result_file = self.data_dir / f"{task.task_id}_result.json"
            
            save_data = {
                "task_info": {
                    "task_id": task.task_id,
                    "token_address": task.token_discovery.token_address,
                    "discovery_source": task.token_discovery.discovery_source,
                    "discovery_time": task.token_discovery.discovery_time.isoformat(),
                    "analysis_time": task.completed_time.isoformat() if task.completed_time else None,
                    "retry_count": task.retry_count
                },
                "analysis_result": task.result
            }
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"分析结果已保存: {result_file}")
            
        except Exception as e:
            logger.error(f"保存分析结果失败: {e}")

    def load_historical_results(self, days: int = 7) -> List[Dict[str, Any]]:
        """加载历史分析结果"""
        results = []
        cutoff_time = datetime.now() - timedelta(days=days)
        
        try:
            for result_file in self.data_dir.glob("*_result.json"):
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 检查时间范围
                    analysis_time_str = data.get("task_info", {}).get("analysis_time")
                    if analysis_time_str:
                        analysis_time = datetime.fromisoformat(analysis_time_str)
                        if analysis_time >= cutoff_time:
                            results.append(data)
                
                except Exception as e:
                    logger.warning(f"加载结果文件失败: {result_file}, {e}")
        
        except Exception as e:
            logger.error(f"加载历史结果失败: {e}")
        
        return sorted(results, key=lambda x: x.get("task_info", {}).get("analysis_time", ""), reverse=True)

    # ============ 记忆查询接口 ============

    def get_prediction_accuracy_stats(self, days_back: int = 30) -> Dict[str, Any]:
        """获取预测准确性统计"""
        if not self.memory_manager:
            return {"error": "记忆模块未启用"}
        
        try:
            return self.memory_manager.get_historical_accuracy(days_back)
        except Exception as e:
            logger.error(f"获取准确性统计失败: {e}")
            return {"error": str(e)}

    def get_learning_insights(self) -> Dict[str, Any]:
        """获取学习洞察"""
        if not self.memory_manager:
            return {"error": "记忆模块未启用"}
        
        try:
            return self.memory_manager.generate_learning_insights()
        except Exception as e:
            logger.error(f"获取学习洞察失败: {e}")
            return {"error": str(e)}

    async def get_token_performance_history(self, token_address: str) -> Dict[str, Any]:
        """获取特定代币的表现历史"""
        if not self.memory_manager:
            return {"error": "记忆模块未启用"}
        
        try:
            record = self.memory_manager.db.get_analysis_record(token_address)
            if not record:
                return {"error": "未找到该代币的分析记录"}
            
            return {
                "analysis_record": {
                    "token_address": record.token_address,
                    "token_symbol": record.token_symbol,
                    "analysis_time": record.analysis_time.isoformat(),
                    "predicted_outcome": record.predicted_outcome,
                    "predicted_scores": record.predicted_scores,
                    "outcome_status": record.outcome_status.value,
                    "accuracy_score": record.accuracy_score
                }
            }
        except Exception as e:
            logger.error(f"获取代币表现历史失败: {e}")
            return {"error": str(e)}

# ============ 工厂函数 ============

def create_slow_trading_controller(
    agent_api_key: str = "sk-b5f98f958e914b589f4fd8ffd25915ab",
    agent_model: str = "qwen-plus",
    max_concurrent: int = 2
) -> SlowTradingController:
    """
    创建慢速交易控制器的工厂函数
    """
    agent_config = {
        "api_key": agent_api_key,
        "model": agent_model,
        "verbose": True
    }
    
    return SlowTradingController(
        agent_config=agent_config,
        max_concurrent_analyses=max_concurrent
    )
