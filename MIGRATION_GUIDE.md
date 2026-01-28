# 代码重构迁移指南

## 重构概述

项目已从扁平结构重构为模块化架构，以支持后续大规模功能扩展。

## 目录结构变化

### 旧结构
```
billions_dollars/
├── gui_main.py
├── realtime_fetcher.py
├── kline_fetcher.py
├── quote_worker.py
└── stock_list.json
```

### 新结构
```
billions_dollars/
├── config.py                    # 全局配置
├── gui_main.py                  # GUI入口（保持兼容）
├── quote_worker.py              # 工作线程（保持兼容）
│
├── core/                        # 核心模块
│   ├── event_bus.py            # 事件总线
│   └── data_center.py          # 数据中心
│
├── data/                        # 数据层
│   └── fetchers/               # 数据获取器
│       ├── realtime_fetcher.py # 实时行情（已迁移）
│       └── kline_fetcher.py    # K线数据（已迁移）
│
├── utils/                       # 工具模块
│   ├── logger.py               # 日志工具
│   └── time_utils.py           # 时间工具
│
└── storage/                     # 数据存储
    └── config/
        └── stock_list.json     # 股票列表（已迁移）
```

## 导入路径变化

### 数据获取器
```python
# 旧
from realtime_fetcher import RealtimeFetcher
from kline_fetcher import KLineFetcher

# 新
from data.fetchers.realtime_fetcher import RealtimeFetcher
from data.fetchers.kline_fetcher import KLineFetcher
```

### 配置
```python
# 旧
STOCK_LIST_FILE = 'stock_list.json'

# 新
from config import STOCK_LIST_FILE
```

### 核心模块
```python
# 新增
from core.event_bus import event_bus, EventType
from core.data_center import data_center
```

### 工具
```python
# 新增
from utils.logger import get_logger
from utils.time_utils import is_trading_time
```

## 兼容性说明

### ✅ 完全兼容
- `gui_main.py` - 已更新导入路径，功能不变
- `quote_worker.py` - 已更新导入路径，功能不变
- 所有现有功能正常工作

### 📦 文件迁移
- `realtime_fetcher.py` → `data/fetchers/realtime_fetcher.py`
- `kline_fetcher.py` → `data/fetchers/kline_fetcher.py`
- `stock_list.json` → `storage/config/stock_list.json`（自动创建）

### 🆕 新增模块
- `config.py` - 全局配置管理
- `core/event_bus.py` - 事件驱动通信
- `core/data_center.py` - 统一数据管理
- `utils/logger.py` - 日志系统
- `utils/time_utils.py` - 时间工具

## 运行方式

### 不变
```bash
python gui_main.py
```

### 新增（未来）
```bash
python main.py --mode gui        # GUI模式
python main.py --mode cli        # 命令行模式
python main.py --mode monitor    # 监控模式
```

## 后续开发指南

### 1. 添加新的数据获取器
在 `data/fetchers/` 目录下创建新文件：
```python
# data/fetchers/tick_fetcher.py
class TickFetcher:
    def get_tick_data(self, stock_code):
        pass
```

### 2. 添加新的技术指标
在 `indicators/` 目录下创建：
```python
# indicators/trend.py
def calculate_ma(df, period):
    return df['close'].rolling(period).mean()
```

### 3. 添加新的策略
在 `strategies/` 目录下创建：
```python
# strategies/ma_strategy.py
from strategies.base_strategy import BaseStrategy

class MAStrategy(BaseStrategy):
    def analyze(self, data):
        pass
```

### 4. 使用事件总线
```python
from core.event_bus import event_bus, EventType

# 订阅事件
def on_quote_updated(data):
    print(f"行情更新: {data}")

event_bus.subscribe(EventType.QUOTE_UPDATED, on_quote_updated)

# 发布事件
event_bus.publish(EventType.QUOTE_UPDATED, {'stock_code': '600000'})
```

### 5. 使用数据中心
```python
from core.data_center import data_center

# 获取数据
quote = data_center.get_quote('600000')
kline = data_center.get_kline('600000', 'daily')

# 更新数据
data_center.update_quote('600000', quote_data)
```

## 测试

### 测试现有功能
```bash
python gui_main.py
```
确认：
- ✅ 添加股票正常
- ✅ 实时行情刷新正常
- ✅ K线图显示正常
- ✅ 股票列表保存/加载正常

### 测试新模块
```bash
python -m pytest tests/
```

## 注意事项

1. **配置文件位置变化**
   - 旧: `./stock_list.json`
   - 新: `./storage/config/stock_list.json`
   - 首次运行会自动创建新位置

2. **日志文件**
   - 新增日志文件: `./storage/logs/app.log`
   - 支持日志轮转（最大10MB，保留5个备份）

3. **向后兼容**
   - 所有现有功能保持不变
   - 可以逐步迁移到新架构

4. **性能影响**
   - 重构后性能无明显变化
   - 事件总线和数据中心使用线程锁保证安全

## 下一步计划

1. ✅ 完成基础架构重构
2. ⏳ 添加更多数据获取器（分时、盘口、资金流向）
3. ⏳ 实现技术指标计算模块
4. ⏳ 开发策略引擎
5. ⏳ 集成本地大模型
6. ⏳ 实现监控预警系统

---

最后更新: 2026-01-28
