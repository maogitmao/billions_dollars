#!/bin/bash
# 启动 Billions Dollars 交易面板（支持输入法）

echo "🚀 启动 Billions Dollars 交易控制面板..."
echo "📝 输入法支持已启用"

# 强制设置输入法环境变量（覆盖系统默认设置）
# 优先检测 fcitx5，然后是 fcitx，最后是 ibus
if pgrep -x "fcitx5" > /dev/null 2>&1; then
    # 强制使用fcitx5，即使系统默认是fcitx
    export QT_IM_MODULE=fcitx5
    export GTK_IM_MODULE=fcitx5
    export XMODIFIERS=@im=fcitx5
    echo "✅ 检测到 fcitx5 进程，强制使用 fcitx5"
elif pgrep -x "fcitx" > /dev/null 2>&1; then
    export QT_IM_MODULE=fcitx
    export GTK_IM_MODULE=fcitx
    export XMODIFIERS=@im=fcitx
    echo "✅ 使用 fcitx 输入法"
elif pgrep -x "ibus-daemon" > /dev/null 2>&1; then
    export QT_IM_MODULE=ibus
    export GTK_IM_MODULE=ibus
    export XMODIFIERS=@im=ibus
    echo "✅ 使用 ibus 输入法"
else
    # 如果没有运行中的进程，检查安装的输入法
    if command -v fcitx5 &> /dev/null; then
        export QT_IM_MODULE=fcitx5
        export GTK_IM_MODULE=fcitx5
        export XMODIFIERS=@im=fcitx5
        echo "✅ 使用 fcitx5 输入法（未检测到运行进程，可能需要手动启动）"
    elif command -v fcitx &> /dev/null; then
        export QT_IM_MODULE=fcitx
        export GTK_IM_MODULE=fcitx
        export XMODIFIERS=@im=fcitx
        echo "✅ 使用 fcitx 输入法（未检测到运行进程，可能需要手动启动）"
    elif command -v ibus &> /dev/null; then
        export QT_IM_MODULE=ibus
        export GTK_IM_MODULE=ibus
        export XMODIFIERS=@im=ibus
        echo "✅ 使用 ibus 输入法（未检测到运行进程，可能需要手动启动）"
    else
        export QT_IM_MODULE=xim
        export GTK_IM_MODULE=xim
        export XMODIFIERS=@im=xim
        echo "⚠️  未检测到输入法，使用 xim"
    fi
fi

echo "环境变量: QT_IM_MODULE=$QT_IM_MODULE"
echo ""

# 启动程序
python3 main.py
