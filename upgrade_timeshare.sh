#!/bin/bash
# 分时图优化升级脚本

echo "=========================================="
echo "分时图平滑优化 - 升级脚本"
echo "=========================================="
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到python3，请先安装Python"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"
echo ""

# 安装scipy依赖
echo "📦 安装scipy依赖..."
pip3 install scipy>=1.10.0

if [ $? -eq 0 ]; then
    echo "✅ scipy安装成功"
else
    echo "❌ scipy安装失败"
    exit 1
fi

echo ""

# 验证scipy
echo "🔍 验证scipy安装..."
python3 -c "import scipy; print(f'scipy版本: {scipy.__version__}')"

if [ $? -eq 0 ]; then
    echo "✅ scipy验证成功"
else
    echo "❌ scipy验证失败"
    exit 1
fi

echo ""

# 运行测试
echo "🧪 运行分时图平滑测试..."
python3 tests/test_timeshare_smooth.py

echo ""
echo "=========================================="
echo "升级完成！"
echo "=========================================="
echo ""
echo "📝 优化内容："
echo "  1. 数据密度提升：5分钟 → 1分钟间隔"
echo "  2. 曲线平滑：使用三次样条插值"
echo "  3. 性能优化：延迟绘制，减少卡顿"
echo "  4. 视觉优化：更细腻的线条和网格"
echo ""
echo "🚀 启动程序："
echo "  bash start_with_ime.sh"
echo ""
echo "📖 详细说明："
echo "  docs/TIMESHARE_OPTIMIZATION.md"
echo ""
