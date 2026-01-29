#!/bin/bash
# 检查输入法配置

echo "=========================================="
echo "输入法诊断工具"
echo "=========================================="

echo -e "\n1. 检查当前环境变量："
echo "QT_IM_MODULE = ${QT_IM_MODULE:-未设置}"
echo "GTK_IM_MODULE = ${GTK_IM_MODULE:-未设置}"
echo "XMODIFIERS = ${XMODIFIERS:-未设置}"

echo -e "\n2. 检查已安装的输入法："
if command -v fcitx &> /dev/null; then
    echo "✅ fcitx 已安装: $(which fcitx)"
else
    echo "❌ fcitx 未安装"
fi

if command -v fcitx5 &> /dev/null; then
    echo "✅ fcitx5 已安装: $(which fcitx5)"
else
    echo "❌ fcitx5 未安装"
fi

if command -v ibus &> /dev/null; then
    echo "✅ ibus 已安装: $(which ibus)"
else
    echo "❌ ibus 未安装"
fi

echo -e "\n3. 检查输入法进程："
if pgrep -x "fcitx" > /dev/null; then
    echo "✅ fcitx 正在运行"
elif pgrep -x "fcitx5" > /dev/null; then
    echo "✅ fcitx5 正在运行"
elif pgrep -x "ibus-daemon" > /dev/null; then
    echo "✅ ibus 正在运行"
else
    echo "⚠️  没有检测到运行中的输入法进程"
fi

echo -e "\n4. 推荐的启动命令："
if pgrep -x "fcitx5" > /dev/null; then
    echo "QT_IM_MODULE=fcitx5 python3 main.py"
elif pgrep -x "fcitx" > /dev/null; then
    echo "QT_IM_MODULE=fcitx python3 main.py"
elif pgrep -x "ibus-daemon" > /dev/null; then
    echo "QT_IM_MODULE=ibus python3 main.py"
else
    echo "请先启动输入法服务"
fi

echo -e "\n=========================================="
