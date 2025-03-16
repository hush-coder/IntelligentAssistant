# -*- coding: utf-8 -*-

import json
import logging
import os
import re

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class ExperimentAnalyzer:
    """负责分析实验要求，识别实验类型和关键要求"""
    
    def __init__(self, api_key=None):
        """初始化实验分析器"""
        # 加载环境变量
        load_dotenv()
        
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("必须提供DeepSeek API密钥。请设置DEEPSEEK_API_KEY环境变量或者通过参数传入。")
            
        self.api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-coder")
    
    def analyze(self, experiment_text):
        """分析实验要求，识别实验类型和关键要求"""
        prompt = f"""请分析以下实验要求，识别实验类型、目标和关键要求。
        实验要求:
        {experiment_text}
        
        请以JSON格式返回，包含以下字段:
        - experiment_type: 实验类型(例如: 数据结构、算法、网络编程等)
        - main_goal: 实验主要目标
        - key_requirements: 关键要求(数组)
        - programming_language: 建议使用的编程语言
        """
        
        response = self._call_api(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # 如果返回的不是有效JSON，尝试提取和解析
            logger.warning("API返回的不是有效JSON，尝试提取和解析")
            return self._extract_json_from_text(response)
    
    def _call_api(self, prompt):
        """调用DeepSeek API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        try:
            logger.info("正在调用DeepSeek API进行实验分析...")
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            logger.info("API调用成功")
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API调用失败: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"错误详情: {e.response.text}")
            raise
    
    def _extract_json_from_text(self, text):
        """从文本中提取JSON内容"""
        # 尝试提取被```json和```包围的内容
        json_pattern = r"```json\s*([\s\S]*?)\s*```"
        match = re.search(json_pattern, text)
        
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        
        # 尝试找到 { 开始到 } 结束的部分
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except:
            pass
            
        # 如果都失败，返回简单的结构
        return {
            "experiment_type": "未能准确识别",
            "main_goal": "完成实验要求",
            "key_requirements": ["实现所需功能"],
            "programming_language": "Python"
        }