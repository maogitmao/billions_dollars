#!/bin/bash
# 安装脚本 - 支持fcitx5输入法

echo "=========================================="
echo "Billions Dollars - 安装脚本"
echo "=========================================="

echo -e "\n1. 检查Python版本..."
python3 --version

echo -e "\n2. 卸载pip安装的PyQt5（不包含fcitx5支持）..."
pip uninstall -y PyQt5 PyQt5-sip 2>/dev/null || echo "PyQt5未通过pip安装"

echo -e "\n3. 安装系统PyQt5包（包含fcitx5支持）..."
sudo apt update
sudo apt install -y python3-pyqt5 python3-pyqt5.qtchart

echo -e "\n4. 安装其他Python依赖..."
pip install -r requirements.txt --no-deps 2>/dev/null || pip install pandas requests matplotlib numpy

echo -e "\n5. 检查fcitx5..."
if pgrep -x "fcitx5" > /dev/null; then
    echo "✅ fcitx5 正在运行"
else
    echo "⚠️  fcitx5 未运行，请启动fcitx5"
fi

echo -e "\n=========================================="
echo "✅ 安装完成！"
echo "=========================================="
echo -e "\n启动程序："
echo "  bash start_with_ime.sh"
echo ""
