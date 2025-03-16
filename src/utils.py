# -*- coding: utf-8 -*-

import logging
import re
import sys
from pathlib import Path

import mammoth

def setup_logging():
    """设置日志记录"""
    logger = logging.getLogger("experiment_completion_tool")
    logger.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    
    # 文件处理器
    file_handler = logging.FileHandler("experiment_tool.log")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # 添加处理器到日志器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def extract_text_from_docx(docx_path):
    """从Word文档中提取文本内容"""
    try:
        with open(docx_path, "rb") as docx_file:
            result = mammoth.extract_raw_text(docx_file)
            return result.value
    except Exception as e:
        logging.error(f"提取Word文档内容失败: {e}")
        raise

def extract_code_blocks(text):
    """从文本中提取代码块"""
    pattern = r"```(\w+)\s*([\s\S]*?)\s*```"
    return re.findall(pattern, text)

def get_file_extension(language):
    """根据语言获取文件扩展名"""
    language = language.lower()
    extensions = {
        "python": ".py",
        "py": ".py",
        "c": ".c",
        "cpp": ".cpp",
        "c++": ".cpp",
        "java": ".java",
        "javascript": ".js",
        "js": ".js",
        "bash": ".sh",
        "shell": ".sh",
        "sh": ".sh"
    }
    return extensions.get(language, ".txt")

def save_solution(solution, output_dir, experiment_type):
    """保存解决方案到文件"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存完整解决方案
    solution_path = output_dir / "完整解决方案.md"
    with open(solution_path, "w", encoding="utf-8") as f:
        f.write(solution)
    
    # 尝试从解决方案中提取代码
    code_blocks = extract_code_blocks(solution)
    if code_blocks:
        code_dir = output_dir / "src"
        code_dir.mkdir(exist_ok=True)
        
        for i, (language, code) in enumerate(code_blocks):
            extension = get_file_extension(language)
            if i == 0 and "main" not in code.lower():
                filename = f"main{extension}"
            else:
                filename = f"module_{i+1}{extension}"
            
            code_path = code_dir / filename
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(code)
            logging.info(f"代码已保存到 {code_path}")
    
    logging.info(f"解决方案已保存到 {solution_path}")
    return solution_path