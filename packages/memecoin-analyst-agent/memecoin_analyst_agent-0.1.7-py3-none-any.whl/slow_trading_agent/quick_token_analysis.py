#!/usr/bin/env python3
"""
快速代币分析工具
使用您提供的真实API快速分析任何BSC代币
"""

import asyncio
import sys
import os

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from enhanced_real_data_tools import EnhancedRealDataClient

async def quick_analyze(token_address: str):
    """快速分析代币"""
    print(f"🔍 快速分析代币: {token_address}")
    print("=" * 50)
    
    client = EnhancedRealDataClient()
    
    try:
        if not client.validate_bsc_address(token_address):
            print("❌ 无效的BSC地址格式")
            return
        
        print("📡 获取数据中...")
        
        # 并行获取数据
        basic_info, price_data, security_data = await asyncio.gather(
            client.get_token_basic_info_moralis(token_address),
            client.get_token_price_data_dex(token_address),
            client.get_security_analysis_goplus(token_address)
        )
        
        # 计算风险
        risk_analysis = client.calculate_risk_score(security_data, price_data)
        
        # 显示核心信息
        print(f"✅ 分析完成\n")
        
        print(f"📊 代币信息:")
        print(f"   名称: {basic_info['name']}")
        print(f"   符号: {basic_info['symbol']}")
        print(f"   价格: ${price_data['price_usd']:.8f}")
        print(f"   市值: ${price_data['market_cap']:,.0f}")
        print(f"   流动性: ${price_data['liquidity_usd']:,.0f}")
        
        print(f"\n🔒 安全状况:")
        print(f"   蜜罐: {'❌ 是' if security_data['is_honeypot'] else '✅ 否'}")
        print(f"   可交易: {'✅ 是' if security_data['can_buy'] and security_data['can_sell'] else '❌ 否'}")
        print(f"   税率: 买入{security_data['buy_tax']:.1f}% / 卖出{security_data['sell_tax']:.1f}%")
        print(f"   持有者: {security_data['holder_count']:,}人")
        
        print(f"\n⚠️ 风险评估:")
        print(f"   等级: {risk_analysis['risk_level']}")
        print(f"   评分: {risk_analysis['risk_score']}/20")
        print(f"   建议: {risk_analysis['recommendation']}")
        
        if risk_analysis['warnings']:
            print(f"   警告: {', '.join(risk_analysis['warnings'][:2])}")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return False
        
    finally:
        await client.close_session()

async def main():
    """主函数"""
    print("🚀 快速代币分析工具")
    print("🔗 使用您的真实API进行分析\n")
    
    if len(sys.argv) > 1:
        # 命令行模式
        token_address = sys.argv[1]
        await quick_analyze(token_address)
    else:
        # 交互模式
        print("请输入要分析的BSC代币地址:")
        print("(例如: 0x73e2e755cc32c407b22df58742b61bf8e50a4444)")
        
        while True:
            token_address = input("\n代币地址 (或输入 'quit' 退出): ").strip()
            
            if token_address.lower() in ['quit', 'exit', 'q']:
                print("👋 再见!")
                break
            
            if token_address:
                await quick_analyze(token_address)
                print("\n" + "-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
