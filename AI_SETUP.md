# AI大模型部署指南

## 系统要求

- GPU: RTX 2080 Ti (8GB) ✅
- 内存: 62GB ✅
- 系统: Ubuntu/Linux ✅

## 快速部署

### 方式1：一键部署（推荐）

```bash
bash setup_llm.sh
```

### 方式2：手动部署

```bash
# 1. 安装Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. 启动服务
ollama serve &

# 3. 下载模型（约8GB，首次需要几分钟）
ollama pull qwen2.5:14b-instruct-q4_K_M

# 4. 测试模型
ollama run qwen2.5:14b-instruct-q4_K_M "你好"
```

## 模型选择

### Qwen2.5-14B-Instruct-Q4_K_M（推荐）
- 参数量: 14B
- 量化: 4-bit
- 模型大小: ~8GB
- 显存占用: 6-7GB
- 性能: 优秀
- 适合: RTX 2080 Ti (8GB)

### 备选方案

如果显存不足，可以选择：
```bash
# 7B模型（更小）
ollama pull qwen2.5:7b-instruct

# 或使用更激进的量化
ollama pull qwen2.5:14b-instruct-q3_K_M
```

## 集成到程序

模型部署后，程序会自动检测并使用：

1. 启动Ollama服务：
```bash
ollama serve &
```

2. 启动交易面板：
```bash
bash start_with_ime.sh
```

3. 在AI输入框中提问，会自动使用本地大模型

## API测试

```bash
# 测试API
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:14b-instruct-q4_K_M",
  "prompt": "分析一下贵州茅台这只股票"
}'
```

## 性能优化

### GPU加速
Ollama会自动使用GPU加速，无需额外配置。

### 内存管理
```bash
# 查看模型占用
ollama ps

# 卸载模型释放显存
ollama stop qwen2.5:14b-instruct-q4_K_M
```

## 故障排查

### 问题1: 服务无法启动
```bash
# 检查端口占用
lsof -i :11434

# 重启服务
pkill ollama
ollama serve &
```

### 问题2: 显存不足
```bash
# 使用更小的模型
ollama pull qwen2.5:7b-instruct

# 或更激进的量化
ollama pull qwen2.5:14b-instruct-q3_K_M
```

### 问题3: 响应慢
- 首次加载需要时间（模型加载到显存）
- 后续请求会快很多
- 可以预热模型：`ollama run qwen2.5:14b-instruct-q4_K_M "你好"`

## 功能说明

程序会自动：
1. 检测Ollama服务是否运行
2. 如果服务可用，使用真实AI模型
3. 如果服务不可用，降级使用模拟回复
4. 在AI对话中自动包含当前股票信息

## 提示词优化

程序使用专门的股票分析提示词：
- 专业的技术分析
- 客观的市场评估
- 风险提示
- 不做具体买卖建议

## 下一步

部署完成后：
1. 测试AI对话功能
2. 询问股票分析
3. 查看技术指标解读
4. 体验智能助手

开始部署：
```bash
bash setup_llm.sh
```
