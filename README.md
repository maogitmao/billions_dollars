# Billions Dollars

基于本地大模型的智能量化交易监控系统

## 项目简介

Billions Dollars 是一个模块化的量化交易监控系统，集成了实时数据采集、技术指标计算、策略分析和本地大模型智能预警功能。

## 核心特性

### 已实现功能 ✅
- **实时行情监控** - 多数据源（新浪、网易、腾讯）自动切换
- **K线图表** - 支持MA均线、实时动态计算
- **股票管理** - 自选股添加/删除/持久化
- **市值显示** - 总市值、流通市值（亿元单位）
- **模块化架构** - 清晰的代码组织，易于扩展

### 开发中功能 🚧
- **多周期K线** - 分时、5分钟、15分钟、30分钟、60分钟、周K、月K
- **技术指标** - MACD、KDJ、RSI、BOLL等
- **策略引擎** - 可配置的交易策略系统
- **本地大模型** - AI智能分析与预警
- **监控预警** - 实时信号检测与提醒
- **交易接口** - 券商API对接（可选）

## 项目架构

```
billions_dollars/
├── core/           # 核心模块（事件总线、数据中心）
├── data/           # 数据层（获取、存储、处理）
├── indicators/     # 技术指标计算
├── strategies/     # 交易策略
├── ai/             # AI模型集成
├── monitor/        # 监控预警
├── trading/        # 交易执行
├── gui/            # 用户界面
└── utils/          # 工具模块
```

详细架构说明请查看 [ARCHITECTURE.md](ARCHITECTURE.md)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行程序

```bash
python3 main.py
```

### 3. 使用说明

1. **添加股票** - 在输入框输入股票代码（如：600000、000001）
2. **查看行情** - 实时行情每3秒自动刷新
3. **查看K线** - 点击股票行即可显示K线图
4. **删除股票** - 选中股票后点击"删除选中"按钮

## 配置说明

全局配置文件：`config.py`

主要配置项：
- `DATA_REFRESH_INTERVAL` - 数据刷新间隔（默认3秒）
- `KLINE_DEFAULT_COUNT` - K线默认数量（默认120）
- `AI_MODEL_TYPE` - AI模型类型（ollama/lmstudio）
- `MONITOR_ENABLED` - 是否启用监控

## 数据存储

- **股票列表**: `storage/config/stock_list.json`
- **数据库**: `storage/database/stocks.db`
- **日志**: `storage/logs/app.log`
- **缓存**: `storage/cache/`

## 开发指南

### 添加新功能

1. **新数据源** - 在 `data/fetchers/` 添加获取器
2. **新指标** - 在 `indicators/` 添加计算函数
3. **新策略** - 在 `strategies/` 继承 `BaseStrategy`
4. **新组件** - 在 `gui/widgets/` 添加自定义组件

### 使用事件总线

```python
from core.event_bus import event_bus, EventType

# 订阅事件
event_bus.subscribe(EventType.QUOTE_UPDATED, callback)

# 发布事件
event_bus.publish(EventType.QUOTE_UPDATED, data)
```

### 使用数据中心

```python
from core.data_center import data_center

# 获取数据
quote = data_center.get_quote('600000')
kline = data_center.get_kline('600000', 'daily')
```

详细开发指南请查看 [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

## 技术栈

- **Python** 3.8+
- **GUI** PyQt5
- **数据处理** pandas, numpy
- **图表** matplotlib
- **数据获取** requests, akshare
- **AI** Ollama / LM Studio（本地大模型）

## 系统要求

- Python 3.8 或更高版本
- 2GB+ 内存
- 网络连接（用于获取行情数据）
- （可选）本地大模型环境

## 跨平台支持

✅ **Linux** - 原生开发环境  
✅ **Windows** - 完全兼容，直接复制运行  
✅ **macOS** - 理论支持（未测试）

## 打包发布

### Windows
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "BillionsDollars" main.py
```

### Linux
```bash
pip install pyinstaller
pyinstaller --onefile --name "BillionsDollars" main.py
```

## 更新日志

### v1.0.0 (2026-01-28)
- ✅ 实时行情监控
- ✅ K线图表显示
- ✅ 股票列表管理
- ✅ 模块化架构重构

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 作者

mao <huaanmy@163.com>

---

**注意**: 本系统仅供学习研究使用，不构成投资建议。投资有风险，入市需谨慎。
