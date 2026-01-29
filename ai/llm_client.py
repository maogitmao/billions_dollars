#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地大模型客户端 - 使用Ollama API

支持的模型：
- qwen2.5:14b (推荐，8GB显存)
- qwen2.5:7b-instruct (备选，4GB显存)

使用说明：
1. AI会自动使用程序中的实时行情数据
2. 询问具体股票时，提供股票代码（如：002342）
3. 询问"行情列表"或"这些股票"时，会分析列表中的股票
4. 选中股票后提问，会自动使用该股票的数据
"""

import requests
import json


class LLMClient:
    """本地大模型客户端"""
    
    def __init__(self, base_url="http://localhost:11434", model="qwen2.5:14b"):
        self.base_url = base_url
        self.model = model
        self.session = requests.Session()
    
    def chat(self, message, system_prompt=None, stream=False):
        """
        发送聊天消息
        
        Args:
            message: 用户消息
            system_prompt: 系统提示词（可选）
            stream: 是否流式输出
            
        Returns:
            str: AI回复
        """
        try:
            # 构建请求
            url = f"{self.base_url}/api/generate"
            
            # 构建完整提示词
            if system_prompt:
                prompt = f"{system_prompt}\n\n用户: {message}\n\nAI助手:"
            else:
                prompt = message
            
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": stream
            }
            
            # 发送请求（首次加载需要更长时间）
            response = self.session.post(url, json=data, timeout=60)
            
            if response.status_code != 200:
                return f"错误: API返回状态码 {response.status_code}"
            
            # 解析响应
            if stream:
                # 流式输出（暂不实现）
                return "流式输出暂不支持"
            else:
                # 非流式输出
                result = response.json()
                return result.get('response', '无响应')
                
        except requests.exceptions.ConnectionError:
            return "错误: 无法连接到Ollama服务，请确保Ollama正在运行"
        except requests.exceptions.Timeout:
            return "错误: 请求超时，模型可能正在加载"
        except Exception as e:
            return f"错误: {str(e)}"
    
    def check_status(self):
        """检查Ollama服务状态"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return True, f"服务正常，已安装 {len(models)} 个模型"
            else:
                return False, f"服务异常: {response.status_code}"
        except:
            return False, "服务未运行"


# 股票分析专用提示词
STOCK_ANALYSIS_PROMPT = """你是一个专业的股票分析AI助手。

【重要规则】
1. 用户提供的数据是实时行情数据，来自程序的实时获取
2. 必须基于用户提供的实时数据进行分析
3. 不要使用你训练数据中的过时信息
4. 如果用户提供了具体数据，就用这些数据，不要说"我无法访问实时数据"

【分析任务】
1. 分析股票的技术指标和走势
2. 基于提供的实时价格、涨跌幅等数据进行评估
3. 提供客观的市场分析
4. 给出风险提示
5. 不做具体的买卖建议

【回复风格】
- 简洁专业
- 重点突出
- 基于事实
- 客观中立

请用简洁专业的语言回答，重点突出关键信息。"""


if __name__ == '__main__':
    # 测试
    client = LLMClient()
    
    print("检查服务状态...")
    status, msg = client.check_status()
    print(f"状态: {msg}")
    
    if status:
        print("\n测试对话...")
        response = client.chat("你好，请简单介绍一下你自己")
        print(f"AI: {response}")
