# PowerShell环境设置脚本
# Windows用户使用此脚本设置环境变量

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  智能客服系统 - 环境设置" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python版本
Write-Host "检查Python版本..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python未安装或未添加到PATH" -ForegroundColor Red
    exit 1
}

# 创建虚拟环境
Write-Host ""
Write-Host "创建Python虚拟环境..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ 虚拟环境已存在" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✓ 虚拟环境创建成功" -ForegroundColor Green
}

# 激活虚拟环境
Write-Host ""
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# 升级pip
Write-Host ""
Write-Host "升级pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip | Out-Null
Write-Host "✓ pip已升级" -ForegroundColor Green

# 安装依赖
Write-Host ""
Write-Host "安装项目依赖..." -ForegroundColor Yellow
Write-Host "这可能需要几分钟，请耐心等待..." -ForegroundColor Gray
pip install -r requirements.txt
Write-Host "✓ 依赖安装完成" -ForegroundColor Green

# 检查.env文件
Write-Host ""
Write-Host "检查环境配置..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env文件已存在" -ForegroundColor Green
} else {
    Write-Host "! .env文件不存在，请手动创建或联系管理员" -ForegroundColor Yellow
}

# 创建必要目录
Write-Host ""
Write-Host "创建数据目录..." -ForegroundColor Yellow
$dirs = @("data", "logs", "data\vector_store")
foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "✓ 创建目录: $dir" -ForegroundColor Green
    }
}

# 完成
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  环境设置完成！" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作：" -ForegroundColor Yellow
Write-Host "1. 初始化知识库: python examples\init_knowledge_base.py" -ForegroundColor White
Write-Host "2. 快速测试: python quickstart.py" -ForegroundColor White
Write-Host "3. 交互对话: python examples\simple_chat.py" -ForegroundColor White
Write-Host ""

