# -*- coding: utf-8 -*-

import json
import logging
import os

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class SolutionGenerator:
    """负责生成实验解决方案"""
    
    def __init__(self, api_key=None):
        """初始化解决方案生成器"""
        # 加载环境变量
        load_dotenv()
        
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("必须提供DeepSeek API密钥。请设置DEEPSEEK_API_KEY环境变量或者通过参数传入。")
            
        self.api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-coder")
    
    def generate(self, experiment_analysis, experiment_text):
        """根据实验分析生成解决方案"""
        prompt = f"""请根据以下实验要求和分析，生成完整的实验解决方案代码和解释。
        
        实验要求:
        {experiment_text}
        
        实验分析:
        {json.dumps(experiment_analysis, ensure_ascii=False)}
        
        生成的解决方案应包含:
        1. 完整的实现代码 
        2. 代码结构解释
        3. 实现思路说明
        4. 使用示例
        5. 测试用例
        
        请使用{experiment_analysis.get('programming_language', 'Python')}编程语言实现。代码应该符合现代编程规范，包含适当的注释和文档字符串。
        """
        
        return self._call_api(prompt)
    
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
            "max_tokens": 4000
        }
        
        try:
            logger.info("正在调用DeepSeek API生成解决方案...")
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