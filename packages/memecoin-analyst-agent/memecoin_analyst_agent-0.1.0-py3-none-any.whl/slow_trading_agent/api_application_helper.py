#!/usr/bin/env python3
"""
API申请助手
提供各个API服务的申请指导和状态检查
"""

import webbrowser
import time
from datetime import datetime

def print_section(title, content="", separator="="):
    """打印格式化的部分标题"""
    print(f"\n{separator * 60}")
    print(f"  {title}")
    print(f"{separator * 60}")
    if content:
        print(content)

class APIApplicationHelper:
    """API申请助手类"""
    
    def __init__(self):
        self.apis = {
            'bscscan': {
                'name': 'BSCScan API',
                'importance': '必需',
                'url': 'https://bscscan.com/myapikey',
                'time_required': '5分钟',
                'approval_time': '立即',
                'free_quota': '100,000请求/天',
                'difficulty': '简单'
            },
            'dexscreener': {
                'name': 'DexScreener API',
                'importance': '必需',
                'url': 'https://api.dexscreener.com/',
                'time_required': '0分钟',
                'approval_time': '无需申请',
                'free_quota': '无限制',
                'difficulty': '无需申请'
            },
            'goplus': {
                'name': 'GoPlus Security API',
                'importance': '必需',
                'url': 'https://api.gopluslabs.io/',
                'time_required': '0分钟',
                'approval_time': '无需申请',
                'free_quota': '1,000请求/天',
                'difficulty': '无需申请'
            },
            'moralis': {
                'name': 'Moralis API',
                'importance': '推荐',
                'url': 'https://moralis.io/',
                'time_required': '10分钟',
                'approval_time': '立即',
                'free_quota': '40,000请求/月',
                'difficulty': '简单'
            },
            'twitter': {
                'name': 'Twitter API v2',
                'importance': '可选',
                'url': 'https://developer.twitter.com/',
                'time_required': '30分钟',
                'approval_time': '1-7天',
                'free_quota': '500,000推文/月',
                'difficulty': '中等'
            }
        }
    
    def show_overview(self):
        """显示API申请概览"""
        print_section("🔑 API申请概览")
        
        print("📊 API重要性分级:")
        print("🔴 必需: 核心功能必需，影响基本代币分析")
        print("🟡 推荐: 增强功能，提供更丰富的数据")
        print("🟢 可选: 高级功能，用于专业分析\n")
        
        print(f"{'API名称':<20} {'重要性':<8} {'申请时间':<10} {'审核时间':<10} {'免费额度':<15}")
        print("-" * 70)
        
        for api_id, info in self.apis.items():
            importance_icon = "🔴" if info['importance'] == '必需' else "🟡" if info['importance'] == '推荐' else "🟢"
            print(f"{info['name']:<20} {importance_icon}{info['importance']:<7} {info['time_required']:<10} {info['approval_time']:<10} {info['free_quota']:<15}")
    
    def show_application_order(self):
        """显示推荐的申请顺序"""
        print_section("📋 推荐申请顺序")
        
        order = [
            ('bscscan', '🔴 第一优先级', '必须申请，5分钟完成，立即可用'),
            ('dexscreener', '✅ 无需申请', '免费使用，直接调用API'),
            ('goplus', '✅ 无需申请', '免费使用，直接调用API'),
            ('moralis', '🟡 第二优先级', '增强功能，10分钟申请，立即可用'),
            ('twitter', '🟢 第三优先级', '社交功能，需要详细申请，审核1-7天')
        ]
        
        for i, (api_id, priority, description) in enumerate(order, 1):
            info = self.apis[api_id]
            print(f"{i}. {priority} - {info['name']}")
            print(f"   {description}")
            print(f"   申请地址: {info['url']}")
            print()
    
    def guide_bscscan_application(self):
        """BSCScan API申请指导"""
        print_section("🔑 BSCScan API申请指导 (必需)")
        
        steps = [
            "1. 打开BSCScan官网 (https://bscscan.com/)",
            "2. 点击右上角 'Sign in' 注册账户",
            "3. 验证邮箱完成注册",
            "4. 登录后访问 API Keys页面 (https://bscscan.com/myapikey)",
            "5. 点击 'Add' 按钮创建新的API Key",
            "6. 输入应用名称: 'Memecoin Analyst'",
            "7. 立即获得API密钥，复制保存"
        ]
        
        for step in steps:
            print(f"   {step}")
        
        print(f"\n📋 预期结果:")
        print(f"   • API密钥格式: YQU5QI4EGAS4IN22ZNU67BK7JMMF1IXNDR")
        print(f"   • 免费额度: 5请求/秒，100,000请求/天")
        print(f"   • 足够支持日常代币分析需求")
        
        response = input(f"\n是否现在打开BSCScan申请页面? (y/n): ")
        if response.lower() == 'y':
            webbrowser.open('https://bscscan.com/myapikey')
            print("✅ 已在浏览器中打开BSCScan API申请页面")
    
    def guide_moralis_application(self):
        """Moralis API申请指导"""
        print_section("🔧 Moralis API申请指导 (推荐)")
        
        steps = [
            "1. 访问Moralis官网 (https://moralis.io/)",
            "2. 点击 'Start for Free' 注册账户",
            "3. 验证邮箱地址",
            "4. 选择用户类型: 'Developer'",
            "5. 项目用途: 'Cryptocurrency Token Analysis'",
            "6. 主要用例: 'DeFi/Token Analytics'",
            "7. 创建新项目: 'Memecoin Analyst'",
            "8. 选择网络: 'Ethereum + BSC'",
            "9. 进入项目设置 → API Keys",
            "10. 复制 'Web3 API Key'"
        ]
        
        for step in steps:
            print(f"   {step}")
        
        print(f"\n📋 免费版功能:")
        print(f"   • 40,000请求/月 (约1,300请求/天)")
        print(f"   • 代币元数据查询")
        print(f"   • 历史价格数据")
        print(f"   • 持有者分析")
        print(f"   • 所有核心API功能")
        
        response = input(f"\n是否现在打开Moralis申请页面? (y/n): ")
        if response.lower() == 'y':
            webbrowser.open('https://moralis.io/')
            print("✅ 已在浏览器中打开Moralis申请页面")
    
    def guide_twitter_application(self):
        """Twitter API申请指导"""
        print_section("🐦 Twitter API申请指导 (可选)")
        
        print("⚠️ 注意: Twitter API申请相对复杂，需要详细说明用途")
        
        steps = [
            "1. 访问Twitter开发者平台 (https://developer.twitter.com/)",
            "2. 使用Twitter账户登录 (需要手机验证)",
            "3. 申请开发者账户",
            "4. 选择用例: 'Making a bot' 或 'Academic research'",
            "5. 详细填写申请表 (参考文档中的模板)",
            "6. 等待审核 (1-7天)",
            "7. 审核通过后创建应用",
            "8. 获取API密钥和Bearer Token"
        ]
        
        for step in steps:
            print(f"   {step}")
        
        print(f"\n📝 申请表关键点:")
        print(f"   • 强调学术研究和市场分析目的")
        print(f"   • 说明数据用于情绪分析，不存储个人信息")
        print(f"   • 避免提及自动化交易")
        print(f"   • 提供清晰的使用场景描述")
        
        print(f"\n📋 免费版功能:")
        print(f"   • 500,000条推文/月")
        print(f"   • 基础搜索 (7天历史)")
        print(f"   • 用户和推文查询")
        print(f"   • 实时推文监控")
        
        response = input(f"\n是否现在打开Twitter开发者申请页面? (y/n): ")
        if response.lower() == 'y':
            webbrowser.open('https://developer.twitter.com/')
            print("✅ 已在浏览器中打开Twitter开发者申请页面")
    
    def check_api_status(self):
        """检查API申请状态"""
        print_section("📊 API申请状态检查")
        
        try:
            from api_config import (
                BSCSCAN_API_KEY, MORALIS_API_KEY, TWITTER_BEARER_TOKEN
            )
            
            status = {
                'BSCScan': '✅ 已配置' if BSCSCAN_API_KEY and BSCSCAN_API_KEY != 'YOUR_BSCSCAN_API_KEY_HERE' else '❌ 未配置',
                'Moralis': '✅ 已配置' if MORALIS_API_KEY and MORALIS_API_KEY != 'YOUR_MORALIS_API_KEY_HERE' else '❌ 未配置',
                'Twitter': '✅ 已配置' if TWITTER_BEARER_TOKEN and TWITTER_BEARER_TOKEN != 'YOUR_TWITTER_BEARER_TOKEN_HERE' else '❌ 未配置',
                'DexScreener': '✅ 免费可用',
                'GoPlus': '✅ 免费可用'
            }
            
            for api, stat in status.items():
                print(f"{api:<15}: {stat}")
            
            configured_count = sum(1 for stat in status.values() if '✅' in stat)
            print(f"\n📈 配置进度: {configured_count}/5 ({configured_count/5*100:.0f}%)")
            
            if configured_count >= 3:
                print("🎉 核心API已配置，可以开始使用基本功能！")
            else:
                print("⚠️ 建议至少配置BSCScan API以获取真实数据")
                
        except ImportError:
            print("⚠️ 未找到api_config.py文件")
            print("请先复制api_config_template.py为api_config.py并配置API密钥")
    
    def interactive_guide(self):
        """交互式申请指导"""
        print_section("🚀 互动式API申请助手")
        
        while True:
            print(f"\n请选择操作:")
            print(f"1. 查看API概览")
            print(f"2. 查看申请顺序")
            print(f"3. BSCScan API申请指导 (必需)")
            print(f"4. Moralis API申请指导 (推荐)")
            print(f"5. Twitter API申请指导 (可选)")
            print(f"6. 检查当前配置状态")
            print(f"7. 运行API连接测试")
            print(f"0. 退出")
            
            choice = input(f"\n请输入选择 (0-7): ").strip()
            
            if choice == '1':
                self.show_overview()
            elif choice == '2':
                self.show_application_order()
            elif choice == '3':
                self.guide_bscscan_application()
            elif choice == '4':
                self.guide_moralis_application()
            elif choice == '5':
                self.guide_twitter_application()
            elif choice == '6':
                self.check_api_status()
            elif choice == '7':
                print("正在运行API连接测试...")
                import subprocess
                subprocess.run(['python3', 'test_api_connections.py'])
            elif choice == '0':
                print("👋 感谢使用API申请助手！")
                break
            else:
                print("❌ 无效选择，请输入0-7之间的数字")

def main():
    """主函数"""
    helper = APIApplicationHelper()
    
    print("🔑 Memecoin智能分析Agent - API申请助手")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    helper.interactive_guide()

if __name__ == "__main__":
    main()
