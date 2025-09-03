"""
分析记忆模块
用于记录分析历史、跟踪价格表现、验证分析准确性
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
from pathlib import Path
import sqlite3
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# ============ 数据结构定义 ============

class AnalysisOutcome(Enum):
    """分析结果验证状态"""
    PENDING = "pending"           # 等待验证
    ACCURATE = "accurate"         # 预测准确
    PARTIALLY_ACCURATE = "partial"  # 部分准确
    INACCURATE = "inaccurate"     # 预测错误
    INSUFFICIENT_DATA = "insufficient"  # 数据不足

@dataclass
class TokenAnalysisRecord:
    """代币分析记录"""
    token_address: str
    token_symbol: str
    analysis_time: datetime
    
    # 原始分析结果
    analysis_report: Dict[str, Any]
    predicted_scores: Dict[str, float]  # sentiment_score, risk_score, overall_score等
    predicted_outcome: str              # 预期表现: bullish, bearish, neutral
    
    # 价格跟踪数据
    initial_price_usd: float
    initial_market_cap: float
    initial_liquidity: float
    
    # 验证结果
    outcome_status: AnalysisOutcome = AnalysisOutcome.PENDING
    verification_time: Optional[datetime] = None
    actual_performance: Optional[Dict[str, Any]] = None
    accuracy_score: Optional[float] = None

@dataclass
class PriceCheckpoint:
    """价格检查点"""
    token_address: str
    timestamp: datetime
    price_usd: float
    market_cap: float
    volume_24h: float
    price_change_pct: Dict[str, float]  # 1h, 24h, 7d, 30d

@dataclass
class PerformanceMetrics:
    """性能指标"""
    max_price: float
    min_price: float
    max_market_cap: float
    current_price: float
    total_return_pct: float
    max_drawdown_pct: float
    volatility: float
    days_tracked: int

# ============ 记忆数据库管理 ============

class AnalysisMemoryDB:
    """分析记忆数据库管理器"""
    
    def __init__(self, db_path: str = "memory/analysis_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            # 分析记录表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token_address TEXT NOT NULL,
                    token_symbol TEXT,
                    analysis_time TEXT NOT NULL,
                    analysis_report TEXT NOT NULL,
                    predicted_scores TEXT,
                    predicted_outcome TEXT,
                    initial_price_usd REAL,
                    initial_market_cap REAL,
                    initial_liquidity REAL,
                    outcome_status TEXT DEFAULT 'pending',
                    verification_time TEXT,
                    actual_performance TEXT,
                    accuracy_score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 价格历史表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token_address TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    price_usd REAL,
                    market_cap REAL,
                    volume_24h REAL,
                    price_change_1h REAL,
                    price_change_24h REAL,
                    price_change_7d REAL,
                    price_change_30d REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (token_address) REFERENCES analysis_records (token_address)
                )
            """)
            
            # 性能统计表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_stats (
                    token_address TEXT PRIMARY KEY,
                    max_price REAL,
                    min_price REAL,
                    max_market_cap REAL,
                    current_price REAL,
                    total_return_pct REAL,
                    max_drawdown_pct REAL,
                    volatility REAL,
                    days_tracked INTEGER,
                    last_updated TEXT,
                    FOREIGN KEY (token_address) REFERENCES analysis_records (token_address)
                )
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_token_address ON analysis_records(token_address)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_analysis_time ON analysis_records(analysis_time)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_price_timestamp ON price_history(token_address, timestamp)")
    
    def save_analysis_record(self, record: TokenAnalysisRecord) -> int:
        """保存分析记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO analysis_records (
                    token_address, token_symbol, analysis_time, analysis_report,
                    predicted_scores, predicted_outcome, initial_price_usd,
                    initial_market_cap, initial_liquidity, outcome_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.token_address,
                record.token_symbol,
                record.analysis_time.isoformat(),
                json.dumps(record.analysis_report),
                json.dumps(record.predicted_scores),
                record.predicted_outcome,
                record.initial_price_usd,
                record.initial_market_cap,
                record.initial_liquidity,
                record.outcome_status.value
            ))
            return cursor.lastrowid
    
    def save_price_checkpoint(self, checkpoint: PriceCheckpoint):
        """保存价格检查点"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO price_history (
                    token_address, timestamp, price_usd, market_cap, volume_24h,
                    price_change_1h, price_change_24h, price_change_7d, price_change_30d
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                checkpoint.token_address,
                checkpoint.timestamp.isoformat(),
                checkpoint.price_usd,
                checkpoint.market_cap,
                checkpoint.volume_24h,
                checkpoint.price_change_pct.get('1h', 0),
                checkpoint.price_change_pct.get('24h', 0),
                checkpoint.price_change_pct.get('7d', 0),
                checkpoint.price_change_pct.get('30d', 0)
            ))
    
    def get_analysis_record(self, token_address: str) -> Optional[TokenAnalysisRecord]:
        """获取分析记录"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM analysis_records 
                WHERE token_address = ? 
                ORDER BY analysis_time DESC 
                LIMIT 1
            """, (token_address,))
            row = cursor.fetchone()
            
            if row:
                return TokenAnalysisRecord(
                    token_address=row['token_address'],
                    token_symbol=row['token_symbol'],
                    analysis_time=datetime.fromisoformat(row['analysis_time']),
                    analysis_report=json.loads(row['analysis_report']),
                    predicted_scores=json.loads(row['predicted_scores']),
                    predicted_outcome=row['predicted_outcome'],
                    initial_price_usd=row['initial_price_usd'],
                    initial_market_cap=row['initial_market_cap'],
                    initial_liquidity=row['initial_liquidity'],
                    outcome_status=AnalysisOutcome(row['outcome_status']),
                    verification_time=datetime.fromisoformat(row['verification_time']) if row['verification_time'] else None,
                    actual_performance=json.loads(row['actual_performance']) if row['actual_performance'] else None,
                    accuracy_score=row['accuracy_score']
                )
        return None
    
    def get_tokens_for_verification(self, days_back: int = 7) -> List[str]:
        """获取需要验证的代币列表"""
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT DISTINCT token_address 
                FROM analysis_records 
                WHERE analysis_time >= ? 
                AND outcome_status = 'pending'
            """, (cutoff_date,))
            return [row[0] for row in cursor.fetchall()]
    
    def update_performance_stats(self, token_address: str, stats: PerformanceMetrics):
        """更新性能统计"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO performance_stats (
                    token_address, max_price, min_price, max_market_cap,
                    current_price, total_return_pct, max_drawdown_pct,
                    volatility, days_tracked, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                token_address, stats.max_price, stats.min_price,
                stats.max_market_cap, stats.current_price,
                stats.total_return_pct, stats.max_drawdown_pct,
                stats.volatility, stats.days_tracked,
                datetime.now().isoformat()
            ))

# ============ 核心记忆管理器 ============

class AnalysisMemoryManager:
    """分析记忆管理器"""
    
    def __init__(self, db_path: str = "memory/analysis_memory.db"):
        self.db = AnalysisMemoryDB(db_path)
        self.is_running = False
        self.verification_task = None
        
        logger.info("AnalysisMemoryManager初始化完成")
    
    async def record_analysis(self, analysis_result: Dict[str, Any]) -> int:
        """记录新的分析结果"""
        try:
            # 从分析结果中提取关键信息
            token_address = analysis_result.get('token_address', '')
            parsed_report = analysis_result.get('parsed_report', {})
            
            if not parsed_report:
                logger.warning(f"分析结果无法解析，跳过记录: {token_address}")
                return -1
            
            # 提取基础信息
            token_info = parsed_report.get('token_analysis', {}).get('basic_info', {})
            market_data = parsed_report.get('token_analysis', {}).get('market_data', {})
            scores = parsed_report.get('multi_dimensional_scores', {})
            
            # 预测结果
            overall_score = scores.get('overall_score', 5.0)
            sentiment_score = scores.get('sentiment_score', 0.5)
            
            # 根据评分判断预期表现
            predicted_outcome = self._determine_predicted_outcome(overall_score, sentiment_score)
            
            # 创建记录
            record = TokenAnalysisRecord(
                token_address=token_address,
                token_symbol=token_info.get('symbol', 'UNKNOWN'),
                analysis_time=datetime.fromisoformat(analysis_result.get('analysis_time')),
                analysis_report=parsed_report,
                predicted_scores=scores,
                predicted_outcome=predicted_outcome,
                initial_price_usd=market_data.get('price_usd', 0.0),
                initial_market_cap=market_data.get('market_cap', 0.0),
                initial_liquidity=market_data.get('liquidity_usd', 0.0)
            )
            
            # 保存到数据库
            record_id = self.db.save_analysis_record(record)
            
            # 创建初始价格检查点
            initial_checkpoint = PriceCheckpoint(
                token_address=token_address,
                timestamp=datetime.now(),
                price_usd=record.initial_price_usd,
                market_cap=record.initial_market_cap,
                volume_24h=market_data.get('volume_24h', 0.0),
                price_change_pct={'1h': 0, '24h': 0, '7d': 0, '30d': 0}
            )
            self.db.save_price_checkpoint(initial_checkpoint)
            
            logger.info(f"记录分析结果: {token_address} ({record.token_symbol}), 预期: {predicted_outcome}")
            return record_id
            
        except Exception as e:
            logger.error(f"记录分析结果失败: {e}")
            return -1
    
    def _determine_predicted_outcome(self, overall_score: float, sentiment_score: float) -> str:
        """根据评分判断预期表现"""
        if overall_score >= 7.0 and sentiment_score >= 0.7:
            return "bullish"
        elif overall_score <= 4.0 or sentiment_score <= 0.3:
            return "bearish"
        else:
            return "neutral"
    
    async def start_verification_loop(self, check_interval_hours: int = 6):
        """启动验证循环"""
        if self.is_running:
            logger.warning("验证循环已在运行")
            return
        
        self.is_running = True
        self.verification_task = asyncio.create_task(
            self._verification_loop(check_interval_hours)
        )
        logger.info(f"启动验证循环，间隔: {check_interval_hours}小时")
    
    async def stop_verification_loop(self):
        """停止验证循环"""
        if self.verification_task:
            self.verification_task.cancel()
            try:
                await self.verification_task
            except asyncio.CancelledError:
                pass
        
        self.is_running = False
        logger.info("验证循环已停止")
    
    async def _verification_loop(self, check_interval_hours: int):
        """验证循环主逻辑"""
        while self.is_running:
            try:
                await self._perform_verification_cycle()
                await asyncio.sleep(check_interval_hours * 3600)  # 转换为秒
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"验证循环异常: {e}")
                await asyncio.sleep(300)  # 出错后等待5分钟再继续
    
    async def _perform_verification_cycle(self):
        """执行一轮验证"""
        logger.info("开始执行验证循环")
        
        # 获取需要验证的代币
        tokens_to_verify = self.db.get_tokens_for_verification(days_back=30)
        logger.info(f"找到 {len(tokens_to_verify)} 个代币需要验证")
        
        for token_address in tokens_to_verify:
            try:
                await self._verify_token_performance(token_address)
                await asyncio.sleep(2)  # 避免API限流
                
            except Exception as e:
                logger.error(f"验证代币 {token_address} 失败: {e}")
    
    async def _verify_token_performance(self, token_address: str):
        """验证单个代币的表现"""
        # 获取分析记录
        record = self.db.get_analysis_record(token_address)
        if not record:
            return
        
        # 模拟获取当前价格数据（实际应该调用price query tool）
        current_data = await self._fetch_current_price_data(token_address)
        if not current_data:
            return
        
        # 创建价格检查点
        checkpoint = PriceCheckpoint(
            token_address=token_address,
            timestamp=datetime.now(),
            price_usd=current_data['price_usd'],
            market_cap=current_data['market_cap'],
            volume_24h=current_data['volume_24h'],
            price_change_pct=current_data['price_changes']
        )
        self.db.save_price_checkpoint(checkpoint)
        
        # 计算性能指标
        performance = self._calculate_performance_metrics(record, current_data)
        self.db.update_performance_stats(token_address, performance)
        
        # 验证分析准确性
        accuracy = self._assess_prediction_accuracy(record, performance)
        
        logger.info(f"验证完成: {token_address}, 准确度: {accuracy:.2f}")
    
    async def _fetch_current_price_data(self, token_address: str) -> Optional[Dict[str, Any]]:
        """获取当前价格数据（模拟）"""
        # 这里应该调用实际的价格查询工具
        # 目前返回模拟数据
        import random
        base_price = random.uniform(0.0001, 0.01)
        
        return {
            'price_usd': base_price,
            'market_cap': base_price * 1000000000,  # 假设10亿代币
            'volume_24h': random.uniform(10000, 500000),
            'price_changes': {
                '1h': random.uniform(-10, 10),
                '24h': random.uniform(-50, 100),
                '7d': random.uniform(-80, 300),
                '30d': random.uniform(-90, 1000)
            }
        }
    
    def _calculate_performance_metrics(self, record: TokenAnalysisRecord, current_data: Dict[str, Any]) -> PerformanceMetrics:
        """计算性能指标"""
        current_price = current_data['price_usd']
        initial_price = record.initial_price_usd
        
        total_return = ((current_price - initial_price) / initial_price * 100) if initial_price > 0 else 0
        
        # 这里简化计算，实际应该基于历史价格数据
        return PerformanceMetrics(
            max_price=max(current_price, initial_price),
            min_price=min(current_price, initial_price),
            max_market_cap=current_data['market_cap'],
            current_price=current_price,
            total_return_pct=total_return,
            max_drawdown_pct=abs(min(0, total_return)),
            volatility=abs(total_return) / 30,  # 简化的波动率计算
            days_tracked=(datetime.now() - record.analysis_time).days
        )
    
    def _assess_prediction_accuracy(self, record: TokenAnalysisRecord, performance: PerformanceMetrics) -> float:
        """评估预测准确性"""
        predicted_outcome = record.predicted_outcome
        actual_return = performance.total_return_pct
        
        # 判断实际表现
        if actual_return > 50:
            actual_outcome = "bullish"
        elif actual_return < -20:
            actual_outcome = "bearish"
        else:
            actual_outcome = "neutral"
        
        # 计算准确性分数
        if predicted_outcome == actual_outcome:
            accuracy = 1.0
        elif (predicted_outcome == "neutral") or (actual_outcome == "neutral"):
            accuracy = 0.5  # 部分准确
        else:
            accuracy = 0.0  # 完全错误
        
        return accuracy
    
    def get_historical_accuracy(self, days_back: int = 30) -> Dict[str, Any]:
        """获取历史准确性统计"""
        # 这里需要查询数据库获取历史验证结果
        # 返回准确性统计
        return {
            "total_predictions": 0,
            "accurate_predictions": 0,
            "accuracy_rate": 0.0,
            "avg_return_predicted_bullish": 0.0,
            "avg_return_predicted_bearish": 0.0,
            "best_prediction": None,
            "worst_prediction": None
        }
    
    def generate_learning_insights(self) -> Dict[str, Any]:
        """生成学习洞察"""
        accuracy_stats = self.get_historical_accuracy()
        
        return {
            "performance_summary": accuracy_stats,
            "improvement_suggestions": [
                "根据历史数据优化评分权重",
                "改进市场情绪分析准确性",
                "加强风险评估模型"
            ],
            "successful_patterns": [
                "高社区活跃度 + 低风险评分的代币表现较好",
                "流动性充足的代币波动性较小"
            ]
        }

# ============ 工厂函数 ============

def create_analysis_memory_manager(db_path: str = "memory/analysis_memory.db") -> AnalysisMemoryManager:
    """创建分析记忆管理器"""
    return AnalysisMemoryManager(db_path)
