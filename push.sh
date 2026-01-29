#!/bin/bash
# 一键推送脚本 - 简洁版

git add . > /dev/null 2>&1
git commit -m "更新代码 $(date '+%Y-%m-%d %H:%M:%S')" > /dev/null 2>&1
git push > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ 推送成功！"
else
    echo "❌ 推送失败，请检查网络或查看详细信息"
fi
