#!/bin/bash
# Linux/Mac环境设置脚本

echo "================================"
echo "  智能客服系统 - 环境设置"
echo "================================"
echo ""

# 检查Python版本
echo -e "\033[33m检查Python版本...\033[0m"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "\033[32m✓ $PYTHON_VERSION\033[0m"
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "\033[32m✓ $PYTHON_VERSION\033[0m"
    PYTHON_CMD=python
else
    echo -e "\033[31m✗ Python未安装\033[0m"
    exit 1
fi

# 创建虚拟环境
echo ""
echo -e "\033[33m创建Python虚拟环境...\033[0m"
if [ -d "venv" ]; then
    echo -e "\033[32m✓ 虚拟环境已存在\033[0m"
else
    $PYTHON_CMD -m venv venv
    echo -e "\033[32m✓ 虚拟环境创建成功\033[0m"
fi

# 激活虚拟环境
echo ""
echo -e "\033[33m激活虚拟环境...\033[0m"
source venv/bin/activate

# 升级pip
echo ""
echo -e "\033[33m升级pip...\033[0m"
pip install --upgrade pip > /dev/null 2>&1
echo -e "\033[32m✓ pip已升级\033[0m"

# 安装依赖
echo ""
echo -e "\033[33m安装项目依赖...\033[0m"
echo -e "\033[37m这可能需要几分钟，请耐心等待...\033[0m"
pip install -r requirements.txt
echo -e "\033[32m✓ 依赖安装完成\033[0m"

# 检查.env文件
echo ""
echo -e "\033[33m检查环境配置...\033[0m"
if [ -f ".env" ]; then
    echo -e "\033[32m✓ .env文件已存在\033[0m"
else
    echo -e "\033[33m! .env文件不存在，请手动创建或联系管理员\033[0m"
fi

# 创建必要目录
echo ""
echo -e "\033[33m创建数据目录...\033[0m"
mkdir -p data logs data/vector_store
echo -e "\033[32m✓ 目录创建完成\033[0m"

# 设置权限
chmod +x examples/*.py
chmod +x quickstart.py

# 完成
echo ""
echo "================================"
echo -e "\033[32m  环境设置完成！\033[0m"
echo "================================"
echo ""
echo -e "\033[33m下一步操作：\033[0m"
echo -e "\033[37m1. 初始化知识库: python examples/init_knowledge_base.py\033[0m"
echo -e "\033[37m2. 快速测试: python quickstart.py\033[0m"
echo -e "\033[37m3. 交互对话: python examples/simple_chat.py\033[0m"
echo ""

