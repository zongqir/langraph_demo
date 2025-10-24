# API密钥配置脚本
# 用于快速配置硅基流动API密钥

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  API密钥配置工具" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已有.env文件
if (Test-Path ".env") {
    Write-Host "检测到已有 .env 文件" -ForegroundColor Yellow
    $overwrite = Read-Host "是否覆盖? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "已取消配置" -ForegroundColor Gray
        exit
    }
}

# 提示用户输入API密钥
Write-Host ""
Write-Host "请输入您的硅基流动API密钥：" -ForegroundColor Yellow
Write-Host "（如果直接回车，将使用项目中已配置的密钥）" -ForegroundColor Gray
Write-Host ""
$apiKey = Read-Host "API密钥"

# 如果用户没有输入，使用默认密钥
if ([string]::IsNullOrWhiteSpace($apiKey)) {
    $apiKey = "sk-rqjbncqjhegvtuuogbnpalmmpjwkqlzolqjqrwnevfavngly"
    Write-Host ""
    Write-Host "使用默认API密钥" -ForegroundColor Green
}

# 创建.env文件
$envContent = @"
# 硅基流动API配置
SILICONFLOW_API_KEY=$apiKey
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1

# 模型配置
DEFAULT_MODEL=Qwen/Qwen2.5-7B-Instruct
EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5

# 系统配置
LOG_LEVEL=INFO
MAX_CONVERSATION_HISTORY=10
VECTOR_STORE_PATH=./data/vector_store

# 业务配置
CUSTOMER_SERVICE_NAME=智能客服小助手
COMPANY_NAME=示例科技有限公司
"@

$envContent | Out-File -FilePath ".env" -Encoding utf8

Write-Host ""
Write-Host "✓ .env 文件创建成功！" -ForegroundColor Green
Write-Host ""

# 验证配置
Write-Host "验证配置..." -ForegroundColor Yellow
try {
    $result = python -c "from config import settings; print(f'API密钥: {settings.siliconflow_api_key[:20]}...')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 配置验证成功！" -ForegroundColor Green
        Write-Host $result -ForegroundColor Gray
    } else {
        Write-Host "! 配置验证失败，但文件已创建" -ForegroundColor Yellow
    }
} catch {
    Write-Host "! 无法验证配置，但文件已创建" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  配置完成！" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "1. 运行快速测试: python quickstart.py" -ForegroundColor White
Write-Host "2. 开始对话: python examples\simple_chat.py" -ForegroundColor White
Write-Host ""

