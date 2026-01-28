# Billions Dollars - 交易控制面板

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行程序
python main.py

# 3. 性能测试
python tests/test_performance.py
```

## 项目结构

```
billions_dollars/
├── main.py              # 主程序入口
├── config.py            # 全局配置
├── requirements.txt     # 依赖列表
│
├── docs/                # 📁 项目说明文档
│   ├── INSTALL.md       # 安装说明
│   ├── design.txt       # 设计笔记
│   └── notes.txt        # 开发笔记
│
├── tests/               # 📁 测试文件
│   └── test_performance.py  # 性能测试
│
├── reference/           # 📁 参考数据和历史数据
│   ├── historical/      # 历史数据（K线、行情等）
│   ├── reference_data/  # 参考数据（股票列表、行业分类等）
│   └── downloads/       # 下载的原始数据
│
├── mao_dev_tools/       # 📁 开发工具和参考文档
│   ├── ubuntu_commands.md   # Ubuntu命令速查
│   └── README.md        # 工具说明
│
├── core/                # 核心模块
│   ├── data_center.py   # 数据中心
│   ├── event_bus.py     # 事件总线
│   └── quote_manager.py # 行情管理器（线程池）
│
├── data/                # 数据模块
│   ├── fetchers/        # 数据获取器
│   ├── processors/      # 数据处理器
│   └── storage/         # 数据存储
│
├── gui/                 # GUI模块
│   ├── dialogs/         # 对话框
│   └── widgets/         # 控件
│
├── monitor/             # 监控模块
│   └── price_alert.py   # 价格预警
│
├── indicators/          # 技术指标
├── strategies/          # 交易策略
├── trading/             # 交易模块
└── utils/               # 工具函数
```

## 核心功能

- ✅ 实时行情监控（支持200+股票）
- ✅ K线图+MACD显示
- ✅ 线程池优化（30并发）
- ✅ 3秒刷新周期
- ✅ 100%成功率

## 性能指标

- 200只股票刷新：3秒
- CPU占用：40-50%
- 内存占用：200MB
- 成功率：100%

## 配置

编辑 `config.py` 调整参数：
```python
THREAD_POOL_CONFIG = {
    'max_workers': 30,  # 并发线程数
}
```

## 文档规则

⚠️ 本项目遵循"代码即文档"原则：
- 不创建冗余的说明文档
- 所有说明都在代码注释中
- 只保留必要的安装和测试说明

## 文件夹归类规则

- 📄 说明文档 → `docs/`
- 🧪 测试文件 → `tests/`
- 📊 参考数据/历史数据 → `reference/`
- 🔧 开发工具/命令参考 → `mao_dev_tools/`
- 💻 代码文件 → 对应的功能模块文件夹
