#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
全局配置文件

⚠️ 项目规则：不创建说明文档（README.md等），代码即文档
"""

import os
from pathlib import Path

# ==================== 路径配置 ====================
BASE_DIR = Path(__file__).parent.absolute()
STORAGE_DIR = BASE_DIR / 'storage'
DATABASE_DIR = STORAGE_DIR / 'database'
CACHE_DIR = STORAGE_DIR / 'cache'
LOGS_DIR = STORAGE_DIR / 'logs'
CONFIG_DIR = STORAGE_DIR / 'config'

# 参考数据路径
REFERENCE_DIR = BASE_DIR / 'reference'
HISTORICAL_DIR = REFERENCE_DIR / 'historical'
REFERENCE_DATA_DIR = REFERENCE_DIR / 'reference_data'
DOWNLOADS_DIR = REFERENCE_DIR / 'downloads'

# 确保目录存在
for dir_path in [STORAGE_DIR, DATABASE_DIR, CACHE_DIR, LOGS_DIR, CONFIG_DIR,
                 REFERENCE_DIR, HISTORICAL_DIR, REFERENCE_DATA_DIR, DOWNLOADS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ==================== 数据配置 ====================
# 实时数据刷新间隔（秒）
DATA_REFRESH_INTERVAL = 3

# K线默认获取数量
KLINE_DEFAULT_COUNT = 120

# 数据源优先级
DATA_SOURCE_PRIORITY = ['sina', 'netease', 'tencent', 'eastmoney']

# 数据缓存时间（秒）
CACHE_EXPIRE_TIME = 60

# ==================== 监控配置 ====================
# 是否启用监控
MONITOR_ENABLED = True

# 监控间隔（秒）
MONITOR_INTERVAL = 1

# 最大监控股票数量
MAX_MONITOR_STOCKS = 200

# 线程池配置
THREAD_POOL_CONFIG = {
    'max_workers': 30,  # 最大并发线程数（根据网络情况调整，推荐20-50）
    'timeout': 5,       # 单个请求超时时间（秒）
}

# ==================== AI配置 ====================
# 本地大模型配置
AI_MODEL_TYPE = 'ollama'  # ollama / lmstudio / custom
AI_MODEL_NAME = 'qwen2.5:7b'
AI_API_URL = 'http://localhost:11434'
AI_TEMPERATURE = 0.7
AI_MAX_TOKENS = 2000

# AI分析间隔（秒）
AI_ANALYSIS_INTERVAL = 60

# ==================== 数据库配置 ====================
DB_PATH = str(DATABASE_DIR / 'stocks.db')
DB_POOL_SIZE = 10

# ==================== 日志配置 ====================
LOG_LEVEL = 'INFO'  # DEBUG / INFO / WARNING / ERROR
LOG_FILE = str(LOGS_DIR / 'app.log')
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# ==================== GUI配置 ====================
# 窗口大小
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

# 主题
THEME = 'light'  # light / dark

# ==================== 交易配置 ====================
# 券商类型
BROKER_TYPE = None  # 'eastmoney' / 'tonghuashun' / None

# 风控配置
MAX_POSITION_RATIO = 0.3  # 单只股票最大仓位比例
MAX_LOSS_RATIO = 0.05     # 最大亏损比例

# ==================== 策略配置 ====================
# 默认策略
DEFAULT_STRATEGY = 'ma_cross'

# 策略参数
STRATEGY_PARAMS = {
    'ma_cross': {
        'short_period': 5,
        'long_period': 20
    },
    'breakthrough': {
        'period': 20,
        'threshold': 0.02
    }
}

# ==================== 文件路径 ====================
STOCK_LIST_FILE = str(CONFIG_DIR / 'stock_list.json')
STRATEGIES_FILE = str(CONFIG_DIR / 'strategies.json')
SETTINGS_FILE = str(CONFIG_DIR / 'settings.json')

# ==================== 市场配置 ====================
# 交易时间段
TRADING_HOURS = [
    ('09:30', '11:30'),
    ('13:00', '15:00')
]

# 集合竞价时间
CALL_AUCTION_HOURS = [
    ('09:15', '09:25'),
    ('14:57', '15:00')
]

# ==================== 技术指标配置 ====================
# 默认均线周期
MA_PERIODS = [5, 10, 20, 30, 60, 120, 250]

# MACD参数
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# KDJ参数
KDJ_N = 9
KDJ_M1 = 3
KDJ_M2 = 3

# RSI参数
RSI_PERIOD = 14

# BOLL参数
BOLL_PERIOD = 20
BOLL_STD = 2

# ==================== 预警配置 ====================
# 预警方式
ALERT_METHODS = ['log', 'sound', 'popup']  # log / sound / popup / email

# 声音文件
ALERT_SOUND_FILE = None

# ==================== 开发配置 ====================
DEBUG = False
TEST_MODE = False

# ==================== 版本信息 ====================
VERSION = '1.0.0'
APP_NAME = 'Billions Dollars'
AUTHOR = 'mao'
