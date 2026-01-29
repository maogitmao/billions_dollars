# Billions Dollars - 交易控制面板

## 最新更新 🎉

**2026-01-29 - 分时图平滑优化**

**问题**：分时图绘制时有卡顿感，不够细腻

**解决方案**：
- ✅ 数据密度提升5倍（1分钟间隔）
- ✅ 曲线平滑处理（三次样条插值）
- ✅ 性能优化（延迟绘制）
- ✅ 视觉优化（线条、颜色、网格）

**快速升级**：
```bash
bash upgrade_timeshare.sh
```

**详细说明**：查看 [`START_HERE.md`](START_HERE.md) | [`OPTIMIZATION_SUMMARY.md`](OPTIMIZATION_SUMMARY.md)

---

**2026-01-29 - 信息爬虫功能大幅增强 + 数据准确性保证**

新增功能：
- 📊 研究报告（机构评级、研究员观点）
- 💸 资金流向（主力、超大单、大单、中单、小单）
- 👥 股东信息（股东户数、人均持股、前十大持股比例）
- 💰 增强财务指标（PS、PCF、EPS、BVPS）

优化功能：
- 🏢 公司信息（真实数据替代占位符）
- 📢 公告信息（智能分类摘要）
- 📰 新闻资讯（严格筛选，只显示相关新闻）

数据准确性保证：
- ✅ 严格的新闻筛选（排除通用列表）
- ✅ 智能摘要生成（清理HTML，提取相关内容）
- ✅ 公告关键词映射（准确分类）
- ✅ 数据质量验证（确保准确性）

详见：[增强功能说明](docs/ENHANCEMENT_SUMMARY.md) | [数据准确性](docs/DATA_ACCURACY.md)

---

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 输入法支持（重要！）
# 如果使用fcitx5，需要安装系统PyQt5包（包含fcitx5插件）
sudo apt install python3-pyqt5 python3-pyqt5.qtchart

# 3. 运行程序（自动检测输入法）
bash start_with_ime.sh

# 4. 如果输入法不工作，运行诊断
bash check_ime.sh

# 5. 性能测试
python tests/test_performance.py
```

## 输入法问题解决

PyQt5的pip版本不包含fcitx5插件，需要安装系统版本：
```bash
# 卸载pip安装的PyQt5
pip uninstall PyQt5 PyQt5-sip

# 安装系统PyQt5（包含fcitx5支持）
sudo apt install python3-pyqt5 python3-pyqt5.qtchart

# 重新运行程序
bash start_with_ime.sh
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

- ✅ 实时行情监控（200+股票，1秒刷新）
- ✅ 分时图显示（3秒刷新）
- ✅ K线图+MACD（10秒刷新）
- ✅ AI对话助手（14B大模型）
- ✅ 信息爬虫（公告、新闻、研报、资金流向、股东信息）**← 新增强**
- ✅ 线程池优化（30并发）
- ✅ 输入法支持

### 信息爬虫详细功能

点击"📥 获取信息"按钮，可获取：

1. **公司信息**：名称、行业、主营业务、上市日期、换手率
2. **财务数据**：PE、PB、PS、PCF、ROE、EPS、BVPS、市值
3. **资金流向**：主力、超大单、大单、中单、小单净流入
4. **股东信息**：股东户数、人均持股、前十大持股比例
5. **研究报告**：机构、研究员、评级、日期（最多5条）
6. **公告信息**：标题、类型、摘要（最多20条）
7. **新闻资讯**：标题、来源、摘要（最多20条）

详见：[爬虫功能说明](docs/CRAWLER_FEATURES.md) | [使用指南](docs/USER_GUIDE.md)

## 性能指标

- 行情刷新：1秒
- 分时图：3秒
- K线图：10秒
- CPU：40-50%
- 内存：200MB

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
