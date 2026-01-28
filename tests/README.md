# 测试文件

本文件夹存放所有测试相关的文件。

## 测试文件

- `test_performance.py` - 性能测试脚本

## 运行测试

```bash
# 性能测试
python tests/test_performance.py --stocks 200 --workers 30

# 基准测试
python tests/test_performance.py --benchmark
```

## 添加新测试

所有测试文件统一放在此文件夹，命名规则：`test_*.py`
