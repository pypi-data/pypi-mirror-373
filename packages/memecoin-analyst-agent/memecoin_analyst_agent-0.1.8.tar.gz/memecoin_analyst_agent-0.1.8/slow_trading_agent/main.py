"""
慢速交易工作流主程序
提供命令行接口和HTTP API接口
"""

import asyncio
import argparse
import logging
from typing import Dict, Any
from datetime import datetime
import json
import re

try:
    from .controller.slow_trading_controller import create_slow_trading_controller, AnalysisTask
    from .core.agent_executor import create_memecoin_analyst
except ImportError:
    # 当直接运行时使用绝对导入
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from controller.slow_trading_controller import create_slow_trading_controller, AnalysisTask
    from core.agent_executor import create_memecoin_analyst

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('slow_trading_agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ============ 回调函数 ============

def on_analysis_complete(task: AnalysisTask):
    """分析完成回调"""
    logger.info(f"🎉 分析完成: {task.token_discovery.token_address}")
    
    if task.result and task.result.get('parsed_report'):
        report = task.result['parsed_report']
        if 'multi_dimensional_scores' in report:
            scores = report['multi_dimensional_scores']
            overall_score = scores.get('overall_score', 'N/A')
            logger.info(f"📊 整体评分: {overall_score}")

def on_analysis_failed(task: AnalysisTask):
    """分析失败回调"""
    logger.error(f"❌ 分析失败: {task.token_discovery.token_address} - {task.error_message}")

# ============ 命令行接口 ============

async def run_single_analysis(token_address: str, context: str = ""):
    """运行单个代币分析"""
    print(f"\n🔍 开始分析代币: {token_address}")
    print("=" * 60)
    
    # 创建Agent并执行分析
    agent = create_memecoin_analyst()
    result = agent.analyze_token(token_address, context)
    
    # 显示结果
    print(f"分析状态: {result.get('status', 'unknown')}")
    print(f"分析时间: {result.get('analysis_time', 'N/A')}")
    print(f"工具调用次数: {len(result.get('tool_calls', []))}")
    
    # 尝试解析和显示AI分析报告
    if result.get('parsed_report'):
        report = result['parsed_report']
        print("\n" + "="*60)
        print("📋 AI分析报告")
        print("="*60)
        
        # 新增：代币基础信息概览
        if 'token_summary' in report:
            summary = report['token_summary']
            print(f"📊 代币基础信息概览 (数据来源: 链上API)")
            print("-" * 30)
            if 'basic_info' in summary:
                print(f"  名称: {summary['basic_info'].get('name', 'N/A')}")
                print(f"  符号: {summary['basic_info'].get('symbol', 'N/A')}")
            if 'market_data' in summary:
                # 增强版数据清理和转换
                def clean_and_convert(value):
                    if isinstance(value, (int, float)):
                        return float(value)
                    if isinstance(value, bool):
                        return 1.0 if value else 0.0
                    if not isinstance(value, str):
                        return 0.0
                    try:
                        # 移除 '$', ',', '%' 等非数字字符
                        cleaned_str = re.sub(r'[^\d.]', '', value)
                        return float(cleaned_str) if cleaned_str else 0.0
                    except (ValueError, TypeError):
                        return 0.0

                price_usd = clean_and_convert(summary['market_data'].get('price_usd', 0))
                market_cap = clean_and_convert(summary['market_data'].get('market_cap', 0))
                liquidity_usd = clean_and_convert(summary['market_data'].get('liquidity_usd', 0))

                print(f"  价格: ${price_usd:.8f}")
                print(f"  市值: ${market_cap:,.0f}")
                print(f"  流动性: ${liquidity_usd:,.0f}")
            if 'security_assessment' in summary:
                # 对安全评估中的数据也使用同样的清理逻辑
                is_honeypot = summary['security_assessment'].get('is_honeypot', False)
                buy_tax = clean_and_convert(summary['security_assessment'].get('buy_tax', 0))
                sell_tax = clean_and_convert(summary['security_assessment'].get('sell_tax', 0))
                holder_count = int(clean_and_convert(summary['security_assessment'].get('holder_count', 0)))

                print(f"\n🔒 安全状况:")
                print(f"  蜜罐风险: {'是' if is_honeypot else '否'}")
                print(f"  买入税: {buy_tax:.1f}%")
                print(f"  卖出税: {sell_tax:.1f}%")
                print(f"  持有者: {holder_count:,}人")
            print("-" * 30)
        
        # 叙事分析与总结
        if 'narrative_analysis_summary' in report:
            print(f"\n🎯 叙事分析与总结:")
            print(f"{report['narrative_analysis_summary']}")
        
        # 关键词识别与标签分类
        if 'keyword_identification_classification' in report:
            print(f"\n🏷️ 关键词识别与标签分类:")
            keywords = report['keyword_identification_classification']
            if isinstance(keywords, dict):
                for category, words in keywords.items():
                    print(f"  {category}: {words}")
            else:
                print(f"{keywords}")
        
        # 代币市值分析
        if 'market_cap_analysis' in report:
            print(f"\n📈 代币市值分析:")
            print(f"{report['market_cap_analysis']}")
        
        # 多维叙事评分
        if 'multi_dimensional_narrative_scores' in report:
            print(f"\n⭐ 多维叙事评分 (100分制):")
            scores = report['multi_dimensional_narrative_scores']
            if isinstance(scores, dict):
                for dimension, score in scores.items():
                    print(f"  {dimension}: {score}分")
                if 'total_score' in scores:
                    print(f"  总分: {scores['total_score']}/100")
            else:
                print(f"{scores}")
        
        print("\n" + "="*60)
    
    elif result.get('agent_output'):
        # 如果没有解析的报告，显示原始Agent输出
        print("\n📋 Agent原始输出:")
        print("-" * 60)
        print(result['agent_output'])
        print("-" * 60)
        
        # 尝试手动解析JSON
        try:
            output_text = result['agent_output']
            # 寻找可能的JSON部分
            json_patterns = [
                (r'```json\s*(.*?)\s*```', 1),  # ```json ... ```
                (r'\{.*\}', 0),  # 任何包含{}的部分
            ]
            
            parsed_json = None
            for pattern, group in json_patterns:
                matches = re.finditer(pattern, output_text, re.DOTALL)
                for match in matches:
                    try:
                        json_text = match.group(group).strip()
                        parsed_json = json.loads(json_text)
                        break
                    except:
                        continue
                if parsed_json:
                    break
            
            if parsed_json:
                print("\n✅ 成功解析JSON报告:")
                print(json.dumps(parsed_json, ensure_ascii=False, indent=2))
            else:
                print("\n❌ 无法从Agent输出中提取有效的JSON报告")
                
        except Exception as e:
            print(f"\n❌ JSON解析错误: {e}")
    
    else:
        print("\n❌ 未获得有效的分析报告")
        if result.get('error'):
            print(f"错误信息: {result['error']}")
        if result.get('parse_error'):
            print(f"解析错误: {result['parse_error']}")
    
    # 保存完整结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"analysis_result_{timestamp}.json"
    
    # 清理无法序列化的对象
    if 'intermediate_steps' in result:
        result['intermediate_steps'] = [str(step) for step in result['intermediate_steps']]
        
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 完整结果已保存至: {result_file}")
    return result

async def run_batch_processing():
    """运行批量处理模式"""
    print("\n🚀 启动慢速交易工作流批量处理")
    print("=" * 60)
    
    # 创建控制器
    controller = create_slow_trading_controller()
    controller.on_analysis_complete = on_analysis_complete
    controller.on_analysis_failed = on_analysis_failed
    
    # 添加一些测试代币
    test_tokens = [
        ("0x1234567890abcdef1234567890abcdef12345678", "测试代币1 - 猫主题Meme币", 8),
        ("0xabcdef1234567890abcdef1234567890abcdef12", "测试代币2 - 社区驱动项目", 6),
        ("0x567890abcdef1234567890abcdef1234567890ab", "测试代币3 - 新发射代币", 7)
    ]
    
    for token_address, context, priority in test_tokens:
        task_id = controller.add_token_for_analysis(
            token_address=token_address,
            source="manual",
            context=context,
            priority=priority
        )
        print(f"✅ 已添加任务: {task_id}")
    
    # 启动处理
    await controller.start_processing()
    
    print("\n📊 实时监控队列状态...")
    try:
        while controller.is_running:
            status = controller.get_queue_status()
            print(f"\r待处理: {status['pending_count']} | "
                  f"进行中: {status['active_count']} | "
                  f"已完成: {status['completed_count']} | "
                  f"失败: {status['failed_count']}", end="")
            
            # 如果所有任务都完成了，退出
            if (status['pending_count'] == 0 and 
                status['active_count'] == 0 and
                status['completed_count'] > 0):
                print("\n\n🎉 所有任务已完成!")
                break
            
            await asyncio.sleep(2)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  收到中断信号，正在停止...")
    
    finally:
        await controller.stop_processing()
        
        # 显示最终结果
        final_status = controller.get_queue_status()
        print(f"\n📈 最终统计:")
        print(f"  成功完成: {final_status['completed_count']}")
        print(f"  失败任务: {final_status['failed_count']}")
        
        # 显示成功任务的简要信息
        if controller.completed_tasks:
            print(f"\n✅ 成功分析的代币:")
            for task in controller.completed_tasks[-5:]:  # 显示最后5个
                token_addr = task.token_discovery.token_address
                duration = (task.completed_time - task.started_time).total_seconds()
                print(f"  {token_addr[-10:]}... (耗时: {duration:.1f}s)")

async def run_interactive_mode():
    """运行交互模式"""
    print("\n🎮 进入交互模式")
    print("输入代币地址进行分析，输入 'quit' 退出")
    print("=" * 60)
    
    while True:
        try:
            token_input = input("\n代币地址: ").strip()
            
            if token_input.lower() in ['quit', 'exit', 'q']:
                print("👋 退出交互模式")
                break
            
            if not token_input:
                continue
            
            # 简单验证地址格式
            if not token_input.startswith('0x') or len(token_input) != 42:
                print("❌ 请输入有效的BSC代币地址 (0x开头，42字符)")
                continue
            
            context = input("额外信息 (可选): ").strip()
            
            await run_single_analysis(token_input, context)
            
        except KeyboardInterrupt:
            print("\n👋 退出交互模式")
            break
        except Exception as e:
            print(f"❌ 分析出错: {e}")

# ============ 主程序入口 ============

async def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description="慢速交易工作流 - Memecoin智能分析系统")
    parser.add_argument("--mode", choices=["single", "batch", "interactive"], 
                       default="interactive", help="运行模式")
    parser.add_argument("--token", type=str, help="代币地址 (single模式)")
    parser.add_argument("--context", type=str, default="", help="额外上下文信息")
    
    args = parser.parse_args()
    
    print("🤖 慢速交易工作流 - Memecoin智能分析系统")
    print("基于LangChain + ReAct架构")
    print(f"运行模式: {args.mode}")
    
    try:
        if args.mode == "single":
            if not args.token:
                print("❌ single模式需要提供 --token 参数")
                return
            await run_single_analysis(args.token, args.context)
            
        elif args.mode == "batch":
            await run_batch_processing()
            
        elif args.mode == "interactive":
            await run_interactive_mode()
    
    except Exception as e:
        logger.error(f"程序异常: {e}")
        print(f"❌ 程序异常: {e}")

if __name__ == "__main__":
    asyncio.run(main())
