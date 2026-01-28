# Billions Dollars - 系统架构设计

## 项目概述
基于本地大模型的智能量化交易监控系统

## 核心目标
1. 实时数据采集与存储
2. 多维度技术指标计算
3. 本地大模型智能分析
4. 交易信号监控与预警
5. 可视化展示与交易操作

---

## 目录结构设计

```
billions_dollars/
│
├── main.py                      # 主入口（命令行版本）
├── gui_main.py                  # GUI入口
├── config.py                    # 全局配置
├── requirements.txt             # 依赖列表
│
├── core/                        # 核心模块
│   ├── __init__.py
│   ├── data_center.py          # 数据中心（统一数据管理）
│   ├── strategy_engine.py      # 策略引擎
│   ├── signal_manager.py       # 信号管理器
│   └── event_bus.py            # 事件总线（模块间通信）
│
├── data/                        # 数据层
│   ├── __init__.py
│   ├── fetchers/               # 数据获取器
│   │   ├── __init__.py
│   │   ├── realtime_fetcher.py      # 实时行情
│   │   ├── kline_fetcher.py         # K线数据
│   │   ├── tick_fetcher.py          # 分时数据
│   │   ├── market_fetcher.py        # 盘口数据
│   │   ├── fund_flow_fetcher.py     # 资金流向
│   │   └── fundamental_fetcher.py   # 基本面数据
│   │
│   ├── storage/                # 数据存储
│   │   ├── __init__.py
│   │   ├── db_manager.py       # 数据库管理
│   │   ├── cache_manager.py    # 缓存管理
│   │   └── file_storage.py     # 文件存储
│   │
│   └── processors/             # 数据处理
│       ├── __init__.py
│       ├── cleaner.py          # 数据清洗
│       ├── validator.py        # 数据验证
│       └── aggregator.py       # 数据聚合
│
├── indicators/                  # 技术指标模块
│   ├── __init__.py
│   ├── base.py                 # 指标基类
│   ├── trend.py                # 趋势指标（MA、EMA、MACD）
│   ├── momentum.py             # 动量指标（RSI、KDJ、CCI）
│   ├── volatility.py           # 波动率指标（BOLL、ATR）
│   ├── volume.py               # 成交量指标（OBV、VOL）
│   └── custom.py               # 自定义指标
│
├── strategies/                  # 策略模块
│   ├── __init__.py
│   ├── base_strategy.py        # 策略基类
│   ├── ma_strategy.py          # 均线策略
│   ├── breakthrough_strategy.py # 突破策略
│   ├── volume_price_strategy.py # 量价策略
│   └── custom_strategy.py      # 自定义策略
│
├── ai/                         # AI模块
│   ├── __init__.py
│   ├── model_manager.py        # 模型管理器
│   ├── prompt_builder.py       # 提示词构建
│   ├── analyzer.py             # AI分析器
│   └── predictor.py            # AI预测器
│
├── monitor/                    # 监控模块
│   ├── __init__.py
│   ├── stock_monitor.py        # 股票监控器
│   ├── signal_detector.py      # 信号检测器
│   ├── alert_manager.py        # 预警管理器
│   └── scheduler.py            # 任务调度器
│
├── trading/                    # 交易模块
│   ├── __init__.py
│   ├── broker_api.py           # 券商接口
│   ├── order_manager.py        # 订单管理
│   ├── position_manager.py     # 持仓管理
│   └── risk_control.py         # 风控模块
│
├── gui/                        # GUI模块
│   ├── __init__.py
│   ├── main_window.py          # 主窗口
│   ├── widgets/                # 自定义组件
│   │   ├── __init__.py
│   │   ├── quote_table.py      # 行情表格
│   │   ├── kline_chart.py      # K线图表
│   │   ├── signal_panel.py     # 信号面板
│   │   ├── ai_chat.py          # AI对话框
│   │   └── trade_panel.py      # 交易面板
│   │
│   └── dialogs/                # 对话框
│       ├── __init__.py
│       ├── strategy_config.py  # 策略配置
│       └── stock_selector.py   # 股票选择器
│
├── utils/                      # 工具模块
│   ├── __init__.py
│   ├── logger.py               # 日志工具
│   ├── time_utils.py           # 时间工具
│   ├── math_utils.py           # 数学工具
│   └── decorators.py           # 装饰器
│
├── tests/                      # 测试模块
│   ├── __init__.py
│   ├── test_data.py
│   ├── test_indicators.py
│   └── test_strategies.py
│
└── storage/                    # 数据存储目录
    ├── database/               # 数据库文件
    ├── cache/                  # 缓存文件
    ├── logs/                   # 日志文件
    └── config/                 # 配置文件
        ├── stock_list.json     # 股票列表
        ├── strategies.json     # 策略配置
        └── settings.json       # 系统设置
```

---

## 核心模块说明

### 1. Core（核心层）
**职责**：系统核心逻辑，模块间协调

- **DataCenter**: 数据中心，统一管理所有数据源
- **StrategyEngine**: 策略引擎，执行策略逻辑
- **SignalManager**: 信号管理，收集、过滤、分发交易信号
- **EventBus**: 事件总线，模块间解耦通信

### 2. Data（数据层）
**职责**：数据获取、存储、处理

- **Fetchers**: 多数据源获取器（实时、历史、基本面）
- **Storage**: 数据持久化（数据库、缓存、文件）
- **Processors**: 数据预处理（清洗、验证、聚合）

### 3. Indicators（指标层）
**职责**：技术指标计算

- 统一的指标接口
- 支持自定义指标
- 指标缓存机制

### 4. Strategies（策略层）
**职责**：交易策略实现

- 策略基类定义标准接口
- 内置常用策略
- 支持策略组合

### 5. AI（智能层）
**职责**：本地大模型集成

- 模型加载与管理
- 数据转换为自然语言
- AI分析结果解析

### 6. Monitor（监控层）
**职责**：实时监控与预警

- 多股票并发监控
- 信号实时检测
- 多级预警机制

### 7. Trading（交易层）
**职责**：交易执行与管理

- 券商API对接
- 订单管理
- 风险控制

### 8. GUI（界面层）
**职责**：用户交互界面

- 模块化组件设计
- 数据可视化
- 交互操作

---

## 数据流设计

```
数据源 → Fetchers → DataCenter → Storage
                        ↓
                   Processors
                        ↓
                   Indicators
                        ↓
                   Strategies
                        ↓
                  SignalManager
                        ↓
                   AI Analyzer
                        ↓
                  AlertManager
                        ↓
                   GUI Display
```

---

## 事件驱动架构

使用事件总线实现模块解耦：

```python
# 事件类型
- DATA_UPDATED          # 数据更新
- SIGNAL_GENERATED      # 信号产生
- ALERT_TRIGGERED       # 预警触发
- ORDER_EXECUTED        # 订单执行
- STRATEGY_CHANGED      # 策略变更
```

---

## 配置管理

### config.py 全局配置
```python
# 数据配置
DATA_REFRESH_INTERVAL = 3  # 秒
KLINE_DEFAULT_COUNT = 120

# 监控配置
MONITOR_ENABLED = True
MONITOR_INTERVAL = 1  # 秒

# AI配置
AI_MODEL_PATH = "./models/qwen"
AI_TEMPERATURE = 0.7

# 数据库配置
DB_PATH = "./storage/database/stocks.db"
CACHE_SIZE = 1000
```

---

## 扩展性设计

### 1. 插件化策略
- 策略继承基类
- 动态加载策略
- 策略热更新

### 2. 多数据源支持
- 统一数据接口
- 自动故障切换
- 数据源优先级

### 3. 模块化AI
- 支持多种大模型
- 可切换模型
- 自定义提示词模板

---

## 性能优化

1. **数据缓存**: Redis/内存缓存减少重复请求
2. **异步处理**: 多线程/协程处理数据获取
3. **增量更新**: 只更新变化的数据
4. **数据库索引**: 优化查询性能
5. **懒加载**: 按需加载历史数据

---

## 开发阶段规划

### Phase 1: 数据基础（当前）
- [x] 实时行情获取
- [x] K线数据获取
- [ ] 重构为模块化结构
- [ ] 添加数据存储
- [ ] 完善技术指标

### Phase 2: 监控系统
- [ ] 策略引擎
- [ ] 信号检测
- [ ] 预警系统

### Phase 3: AI集成
- [ ] 本地大模型接入
- [ ] 数据分析
- [ ] 智能预测

### Phase 4: 交易功能
- [ ] 券商API对接
- [ ] 订单管理
- [ ] 风控系统

### Phase 5: 优化完善
- [ ] 性能优化
- [ ] 回测系统
- [ ] 策略优化

---

## 技术栈

- **语言**: Python 3.8+
- **GUI**: PyQt5
- **数据**: pandas, numpy
- **图表**: matplotlib
- **数据库**: SQLite / PostgreSQL
- **缓存**: Redis (可选)
- **AI**: Ollama / LM Studio (本地大模型)
- **网络**: requests, aiohttp
- **测试**: pytest

---

## 注意事项

1. **模块独立性**: 每个模块可独立测试和替换
2. **接口标准化**: 统一的数据格式和接口规范
3. **错误处理**: 完善的异常处理和日志记录
4. **文档完善**: 每个模块都有详细文档
5. **代码规范**: 遵循PEP8，使用类型提示

---

最后更新: 2026-01-28
