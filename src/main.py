#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from src.analyzer import ExperimentAnalyzer
from src.generator import SolutionGenerator
from src.utils import setup_logging, extract_text_from_docx, save_solution

# 设置日志
logger = setup_logging()

@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output-dir", "-o", help="输出目录，默认为'test/output/[输入文件名]'")
@click.option("--api-key", "-k", help="DeepSeek API密钥(也可通过DEEPSEEK_API_KEY环境变量设置)")
@click.option("--verbose", "-v", is_flag=True, help="显示详细日志")
def cli(input_file, output_dir, api_key, verbose):
    """实验完成工具 - 自动分析实验要求并生成解决方案"""
    # 加载环境变量
    load_dotenv()
    
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    input_path = Path(input_file)
    
    try:
        # 确定输出目录
        if output_dir is None:
            output_dir = Path("experiment_output") / input_path.stem
        else:
            output_dir = Path(output_dir)
        
        click.echo(f"📝 正在处理实验要求文件: {input_path}")
        
        # 提取实验要求
        if input_path.suffix.lower() == '.docx':
            experiment_text = extract_text_from_docx(input_path)
        else:
            with open(input_path, 'r', encoding='utf-8') as f:
                experiment_text = f.read()
        
        click.echo(f"✓ 成功提取实验要求，长度: {len(experiment_text)}字符")
        
        # 分析实验
        analyzer = ExperimentAnalyzer(api_key=api_key)
        analysis = analyzer.analyze(experiment_text)
        click.echo(f"🔍 实验分析完成: {analysis['experiment_type']}")
        
        # 生成解决方案
        generator = SolutionGenerator(api_key=api_key)
        solution = generator.generate(analysis, experiment_text)
        click.echo("🚀 解决方案生成完成")
        
        # 保存解决方案
        solution_path = save_solution(solution, output_dir, analysis['experiment_type'])
        
        click.echo(f"\n✅ 实验解决方案已生成: {solution_path}")
        click.echo(f"实验类型: {analysis['experiment_type']}")
        click.echo(f"实验目标: {analysis['main_goal']}")
        
    except Exception as e:
        logger.error(f"处理失败: {e}", exc_info=True)
        click.echo(f"\n❌ 处理失败: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()