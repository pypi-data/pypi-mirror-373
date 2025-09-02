"""
API配置模板
复制此文件为 api_config.py 并填入您的真实API密钥
"""

# BSCScan API (必需)
BSCSCAN_API_KEY = "1RXFCIISC3SG1JQ2BCSG7A6PRMA3IRCV3A"
BSCSCAN_BASE_URL = "https://api.bscscan.com/api"

# GoPlus Security API (必需，用于安全检测)
GOPLUS_API_KEY = ""  # 免费使用，无需API Key
GOPLUS_BASE_URL = "https://api.gopluslabs.io/api/v1"

# Moralis API (可选，用于高级数据)
# 申请地址: https://moralis.io/ (注册 → 创建项目 → 获取Web3 API Key)
# 免费额度: 40,000请求/月，足够个人使用
MORALIS_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjFkMTA0ODEyLTk1ODYtNDNjYi1iZTllLTQ4NDYwYWU1NjhmNCIsIm9yZ0lkIjoiNDY4NDM5IiwidXNlcklkIjoiNDgxODk3IiwidHlwZUlkIjoiNjA0YmM2OTEtMzA2ZC00NGRhLWIxZTItZmNhMWIzZTgzN2RiIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3NTY2NDk0NjIsImV4cCI6NDkxMjQwOTQ2Mn0.R61ANHSIdtHMyfzpZCCb7VNPFFOeiwmXY8-iPTj1aB8"
MORALIS_BASE_URL = "https://deep-index.moralis.io/api/v2"

# Twitter API v2 (可选，用于情绪分析)
# 申请地址: https://developer.twitter.com/ (需要详细申请表，审核1-7天)
# 免费额度: 500,000条推文/月
TWITTER_BEARER_TOKEN = ""  # 需要Bearer Token用于API v2
TWITTER_API_KEY = "GdCwyodB4IGUndm1KMoafVzXN"
TWITTER_API_SECRET = "XQ64RjyT5CoblNWBEkk1roHJsyXdkbeEUJ6YIV3jFiyOqwDPqz"

# 1inch API (可选，用于价格聚合)
ONEINCH_API_KEY = "YOUR_1INCH_API_KEY_HERE"
ONEINCH_BASE_URL = "https://api.1inch.dev"

# DexScreener API (免费，无需API Key)
DEXSCREENER_BASE_URL = "https://api.dexscreener.com/latest"

# CoinGecko API (可选，免费版有限制)
COINGECKO_API_KEY = "YOUR_COINGECKO_API_KEY_HERE"  # Pro版本
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# 请求配置
REQUEST_TIMEOUT = 10  # 秒
MAX_RETRIES = 3
RATE_LIMIT_DELAY = 1  # 秒，请求间隔

# 缓存配置
CACHE_ENABLED = True
CACHE_DURATION = 300  # 秒，5分钟缓存

# 优先级配置 (用于数据源选择)
DATA_SOURCE_PRIORITY = {
    "price_data": ["dexscreener", "1inch", "coingecko"],
    "token_info": ["bscscan", "moralis"],
    "security_check": ["goplus"],
    "social_data": ["twitter"]
}
