# 快速开始指南

## 🚀 5分钟上手

### 1. 检查环境

```bash
# 确认Python版本
python3 --version  # 需要 3.8+

# 进入项目目录
cd billions_dollars
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

如果安装速度慢，可以使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 运行程序

```bash
python3 main.py
```

### 4. 开始使用

#### 添加股票
1. 在左上角输入框输入股票代码（如：`600000`、`000001`、`600519`）
2. 点击"添加股票"按钮或按回车键
3. 股票会自动添加到列表并开始获取行情

#### 查看实时行情
- 行情每3秒自动刷新
- 红色表示上涨，绿色表示下跌
- 显示：代码、名称、涨幅、现价、涨跌、市值、流通值、振幅

#### 查看K线图
- 点击任意股票行
- 右侧会显示该股票的K线图
- 包含MA5、MA10、MA20均线
- 交易时段会显示实时动态均线

#### 删除股票
1. 点击选中要删除的股票
2. 点击"删除选中"按钮

#### 手动刷新
- 点击"🔄 刷新"按钮可立即刷新所有行情

---

## 📖 常见问题

### Q: 为什么有些股票显示"获取失败"？
A: 可能原因：
- 股票代码输入错误
- 网络连接问题
- 数据源暂时不可用（系统会自动切换数据源）

### Q: K线图为什么只显示部分数据？
A: 默认显示最近120个交易日的数据，可以使用工具栏的缩放功能查看更多细节。

### Q: 如何修改刷新间隔？
A: 编辑 `config.py` 文件，修改 `DATA_REFRESH_INTERVAL` 的值（单位：秒）。

### Q: 股票列表保存在哪里？
A: 保存在 `storage/config/stock_list.json`，程序会自动加载。

### Q: 如何查看日志？
A: 
- 界面日志：在左下角"系统日志"区域
- 文件日志：`storage/logs/app.log`

---

## 🎯 下一步

### 学习架构
阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 了解项目架构设计

### 开发新功能
阅读 [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) 学习如何扩展功能

### 查看进度
阅读 [PROJECT_STATUS.md](PROJECT_STATUS.md) 了解开发进度

---

## 💡 使用技巧

### 1. 快速添加多只股票
连续输入股票代码并按回车，无需点击按钮

### 2. K线图操作
- **缩放**: 使用工具栏的放大镜图标
- **平移**: 使用工具栏的十字箭头图标
- **保存**: 使用工具栏的保存图标导出图片
- **还原**: 使用工具栏的home图标恢复原始视图

### 3. 查看实时动态均线
在交易时段（9:30-11:30, 13:00-15:00），K线图会显示：
```
MA5:  59.40 → 59.45
      ↑静态   ↑动态（包含实时价格）
```

### 4. 日志复制
系统日志区域支持文本选择和复制，方便排查问题

---

## 🔧 故障排除

### 问题：程序无法启动
```bash
# 检查依赖是否完整安装
pip list | grep -E "PyQt5|pandas|matplotlib|akshare"

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### 问题：导入错误
```bash
# 确保在项目根目录运行
pwd  # 应该显示 .../billions_dollars

# 检查Python路径
python3 -c "import sys; print(sys.path)"
```

### 问题：数据获取失败
```bash
# 测试网络连接
ping hq.sinajs.cn

# 测试数据获取
python3 -c "
from data.fetchers import RealtimeFetcher
f = RealtimeFetcher()
print(f.get_realtime_quote('600000'))
"
```

---

## 📞 获取帮助

- **查看日志**: `storage/logs/app.log`
- **提交问题**: 联系开发者 huaanmy@163.com
- **查看文档**: 阅读项目根目录下的 `.md` 文件

---

## 🎉 开始探索

现在你已经掌握了基本使用方法，可以：

1. ✅ 添加你关注的股票
2. ✅ 观察实时行情变化
3. ✅ 分析K线图和均线
4. ⏳ 等待后续功能更新（AI分析、策略监控等）

祝你使用愉快！📈
