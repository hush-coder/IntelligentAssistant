#!/bin/bash

# 安装Poetry（如果尚未安装）
if ! command -v poetry &> /dev/null; then
    echo "Poetry未安装，正在安装..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# 如果.env文件不存在，则复制模板
if [ ! -f .env ]; then
    cp .env.template .env
    echo "请在.env文件中配置你的DeepSeek API密钥"
fi

# 使用Poetry安装依赖
poetry install

# 创建项目结构
mkdir -p /home/hushArch/IntelligentAssistant/test/input
mkdir -p /home/hushArch/IntelligentAssistant/test/output

# 为脚本添加执行权限
chmod +x scripts/setup.sh

echo "=========================================="
echo "实验完成工具安装完成！"
echo "请按以下步骤操作:"
echo "1. 编辑.env文件，添加你的DeepSeek API密钥"
echo "2. 运行示例: poetry run experiment-tool examples/linked_list_experiment.txt"
echo "=========================================="