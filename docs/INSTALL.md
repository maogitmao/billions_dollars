# 安装指南

## 快速安装

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行程序
python main.py

# 3. 性能测试（可选）
python test_performance.py --stocks 200 --workers 30
```

## 依赖说明

### 必需依赖
- Python 3.7+
- PyQt5 (GUI框架)
- pandas (数据处理)
- matplotlib (图表)
- requests (网络请求)
- akshare (数据源)

### 推荐安装
```bash
pip install pyarrow  # 消除pandas警告，提升性能
```

## 系统要求
- 内存: 8GB+
- 网络: 稳定连接

## 配置调整

编辑 `config.py`:
```python
THREAD_POOL_CONFIG = {
    'max_workers': 30,  # 并发线程数：20-50
}
```

## 常见问题

### Q: ImportError: No module named 'PyQt5'
```bash
pip install PyQt5
```

### Q: pandas警告
```bash
pip install pyarrow
```

### Q: 网络连接失败
- 检查防火墙
- 确保可访问国内金融网站

