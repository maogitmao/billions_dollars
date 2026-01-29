#!/bin/bash
# 一键推送脚本

echo "📦 正在添加文件..."
git add .

echo "💾 正在提交..."
git commit -m "更新代码 $(date '+%Y-%m-%d %H:%M:%S')"

echo "🚀 正在推送到 GitHub..."
git push

echo "✅ 代码已成功推送到 GitHub！"
