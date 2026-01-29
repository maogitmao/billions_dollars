#!/bin/bash
# 部署本地大模型 - Qwen2.5-14B

echo "=========================================="
echo "部署本地大模型 - Qwen2.5-14B"
echo "=========================================="

echo -e "\n检查系统配置..."
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader)"
echo "显存: $(nvidia-smi --query-gpu=memory.total --format=csv,noheader)"
echo "内存: $(free -h | grep Mem | awk '{print $2}')"

echo -e "\n1. 安装Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama已安装"
    ollama --version
else
    echo "正在安装Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

echo -e "\n2. 启动Ollama服务..."
# 检查服务是否运行
if pgrep -x "ollama" > /dev/null; then
    echo "✅ Ollama服务已运行"
else
    echo "启动Ollama服务..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

echo -e "\n3. 下载Qwen2.5-14B模型（量化版本，适合8GB显存）..."
echo "提示：首次下载约8GB，需要几分钟"
ollama pull qwen2.5:14b-instruct-q4_K_M

echo -e "\n4. 测试模型..."
echo "测试问题：你好，请介绍一下你自己"
ollama run qwen2.5:14b-instruct-q4_K_M "你好，请介绍一下你自己" --verbose

echo -e "\n=========================================="
echo "✅ 模型部署完成！"
echo "=========================================="
echo -e "\n模型信息："
echo "  名称: qwen2.5:14b-instruct-q4_K_M"
echo "  大小: ~8GB"
echo "  量化: Q4_K_M（4-bit量化）"
echo "  显存占用: ~6-7GB"
echo ""
echo "使用方法："
echo "  ollama run qwen2.5:14b-instruct-q4_K_M"
echo ""
echo "API调用："
echo "  curl http://localhost:11434/api/generate -d '{\"model\":\"qwen2.5:14b-instruct-q4_K_M\",\"prompt\":\"你好\"}'"
echo ""
