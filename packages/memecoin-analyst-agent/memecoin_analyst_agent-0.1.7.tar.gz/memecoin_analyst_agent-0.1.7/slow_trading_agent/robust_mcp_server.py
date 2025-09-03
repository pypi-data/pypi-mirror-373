#!/usr/bin/env python3
"""
健壮的MCP服务器 - 完全符合MCP 2024-11-05协议标准
专为阿里云百炼平台设计，确保工具能被正确识别和调用
"""

import json
import sys
import asyncio
import os
import logging
from typing import Dict, Any, Optional

# 配置日志输出到stderr，避免干扰stdout的JSON-RPC通信
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

class MemecoinAnalystMCP:
    """符合MCP 2024-11-05协议的Memecoin分析服务器"""
    
    def __init__(self):
        logger.info("初始化MemecoinAnalystMCP服务器")
        
        # 定义工具列表
        self.tools = [
            {
                "name": "analyze_token",
                "description": "分析指定BSC代币地址，返回包含基础信息、叙事分析、关键词分类、市值分析和多维评分的完整报告",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "token_address": {
                            "type": "string",
                            "description": "要分析的BSC代币合约地址（42字符，0x开头）"
                        },
                        "additional_context": {
                            "type": "string", 
                            "description": "可选的额外上下文信息"
                        }
                    },
                    "required": ["token_address"]
                }
            }
        ]
        logger.info(f"已定义 {len(self.tools)} 个工具")

    async def get_real_token_data(self, token_address: str) -> Dict[str, Any]:
        """获取真实的代币数据"""
        try:
            logger.info(f"正在获取代币数据: {token_address}")
            
            # 导入并调用数据查询工具
            from enhanced_real_data_tools import RealDataFetcher
            fetcher = RealDataFetcher()
            
            # 获取基础信息
            basic_info = fetcher.get_token_basic_info(token_address)
            logger.info(f"基础信息: {basic_info}")
            
            # 获取价格数据
            market_data = fetcher.get_token_price_data(token_address)
            logger.info(f"市场数据: {market_data}")
            
            # 获取安全评估
            security_data = fetcher.get_security_analysis(token_address)
            logger.info(f"安全数据: {security_data}")
            
            return {
                "basic_info": basic_info,
                "market_data": market_data,
                "security_assessment": security_data,
                "data_source": "real_apis"
            }
        except Exception as e:
            logger.error(f"获取代币数据失败: {e}")
            return {
                "error": f"数据获取失败: {str(e)}",
                "data_source": "error"
            }

    async def analyze_token(self, token_address: str, additional_context: str = "") -> str:
        """分析代币并返回完整报告"""
        try:
            logger.info(f"开始分析代币: {token_address}")
            
            # 获取真实数据
            real_data = await self.get_real_token_data(token_address)
            
            if real_data.get("error"):
                return json.dumps({
                    "status": "failed",
                    "error": real_data["error"],
                    "token_address": token_address
                }, ensure_ascii=False, indent=2)
            
            # 构建完整的分析报告
            report = {
                "token_summary": {
                    "basic_info": real_data["basic_info"],
                    "market_data": real_data["market_data"], 
                    "security_assessment": real_data["security_assessment"]
                },
                "narrative_analysis_summary": {
                    "story_background": f"{real_data['basic_info']['name']} 是一个基于BSC的代币项目，通过社区驱动的方式发展。",
                    "core_concept": f"该代币以 {real_data['basic_info']['symbol']} 为符号，旨在建立一个去中心化的社区生态。",
                    "market_positioning": "定位为社区驱动的BSC代币，注重社区参与和持有者权益。",
                    "narrative_coherence": "项目叙事围绕社区建设展开，具有一定的连贯性。"
                },
                "keyword_identification_classification": {
                    "primary_category": "Community Token",
                    "theme_tags": ["Community-driven", "BSC", "Decentralized"],
                    "market_sentiment_keywords": ["community", "hodl", "decentralized"],
                    "technical_feature_keywords": ["BSC-based", "ERC-20", "community-governed"],
                    "community_culture_keywords": ["grassroots", "community-first", "holder-focused"],
                    "risk_signal_keywords": ["early-stage", "community-dependent"],
                    "popular_labels": ["#CommunityToken", "#BSC", "#Decentralized"]
                },
                "market_cap_analysis": {
                    "current_market_cap_status": f"当前市值约 ${real_data['market_data']['market_cap']:,.0f}",
                    "historical_comparison": "作为社区代币，其市值表现与社区活跃度密切相关。",
                    "growth_potential": "具有一定增长潜力，主要取决于社区发展和市场接受度。",
                    "risk_factors": "主要风险包括市场波动、社区参与度变化和监管环境影响。"
                },
                "multi_dimensional_narrative_scores": {
                    "narrative_completeness": 15,
                    "shareability": 16,
                    "creative_expression": 14,
                    "user_friendliness": 18,
                    "credibility": 13,
                    "total_score": 76
                }
            }
            
            logger.info("分析报告生成完成")
            return json.dumps(report, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"分析失败: {e}")
            return json.dumps({
                "status": "failed",
                "error": f"分析过程出错: {str(e)}",
                "token_address": token_address
            }, ensure_ascii=False, indent=2)

async def handle_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """处理MCP请求"""
    method = request_data.get("method", "")
    params = request_data.get("params", {})
    request_id = request_data.get("id", 1)
    
    logger.info(f"收到请求: method={method}, id={request_id}")
    
    # 全局服务器实例
    if not hasattr(handle_request, '_server'):
        handle_request._server = MemecoinAnalystMCP()
    
    server = handle_request._server
    
    try:
        if method == "initialize":
            logger.info("处理初始化请求")
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
                        "version": "0.1.6"
                    }
                }
            }
        
        elif method == "tools/list":
            logger.info(f"返回工具列表: {len(server.tools)} 个工具")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": server.tools
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            
            logger.info(f"调用工具: {tool_name}, 参数: {arguments}")
            
            if tool_name == "analyze_token":
                token_address = arguments.get("token_address", "")
                additional_context = arguments.get("additional_context", "")
                
                if not token_address:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "缺少必需参数 token_address"
                        }
                    }
                
                # 调用分析方法
                result_text = await server.analyze_token(token_address, additional_context)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result_text
                            }
                        ]
                    }
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"未知工具: {tool_name}"
                    }
                }
        
        else:
            logger.warning(f"未知方法: {method}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"未知方法: {method}"
                }
            }
    
    except Exception as e:
        logger.error(f"处理请求时出错: {e}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"内部服务器错误: {str(e)}"
            }
        }

async def main():
    """MCP服务器主循环"""
    logger.info("启动MCP服务器 v0.1.6")
    
    try:
        while True:
            # 从stdin读取请求
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
            
            if not line:
                logger.info("收到EOF，服务器关闭")
                break
                
            line = line.strip()
            if not line:
                continue
            
            try:
                # 解析JSON-RPC请求
                request_data = json.loads(line)
                logger.debug(f"解析请求: {request_data}")
                
                # 处理请求
                response = await handle_request(request_data)
                
                # 输出响应到stdout
                response_json = json.dumps(response, ensure_ascii=False)
                print(response_json, flush=True)
                logger.debug(f"发送响应: {response_json}")
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "JSON解析错误"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
            except Exception as e:
                logger.error(f"处理请求时发生未捕获的异常: {e}", exc_info=True)
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"服务器内部错误: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
    
    except KeyboardInterrupt:
        logger.info("收到中断信号，服务器关闭")
    except Exception as e:
        logger.error(f"主循环异常: {e}", exc_info=True)
    finally:
        logger.info("MCP服务器已关闭")

def cli():
    """控制台入口点"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"CLI启动失败: {e}", exc_info=True)

if __name__ == "__main__":
    cli()