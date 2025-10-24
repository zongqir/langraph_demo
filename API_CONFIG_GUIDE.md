# 🔑 API密钥配置指南

## 📍 配置方法

使用 `.env` 文件配置API密钥：

**步骤1：复制配置模板**
```bash
cp config.env .env
```

**步骤2：编辑 .env 文件**
```env
# 修改这里的API密钥
SILICONFLOW_API_KEY=你的API密钥
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
```

---

## 🚀 快速开始

```bash
# 1. 复制配置文件
cp config.env .env

# 2. 编辑 .env 文件（修改API密钥）
# Windows: notepad .env
# Linux/Mac: nano .env 或 vim .env

# 3. 运行
python quickstart.py
```

---

## 🔍 当前API密钥

您当前配置的API密钥是：
```
sk-rqjbncqjhegvtuuogbnpalmmpjwkqlzolqjqrwnevfavngly
```

这个密钥已经可以直接使用！

---

## ✅ 验证配置

运行快速测试验证配置：

```bash
python quickstart.py
```

---

## 🔐 安全建议

### ✅ 推荐做法
- 使用 `.env` 文件（已被 `.gitignore` 忽略）
- 不要将API密钥提交到Git
- 不要分享给他人

### ❌ 不要这样做
- 不要直接写在代码中
- 不要提交到版本控制

---

## 🎯 部署配置

### 本地开发
```bash
cp config.env .env
# 编辑 .env 文件
```

### Docker部署
创建 `.env` 文件，Docker Compose会自动读取：
```bash
cp config.env .env
docker-compose up
```

---

## 🆘 常见问题

### Q: 修改了配置但不生效？
**A**: 重启程序（Ctrl+C 然后重新运行）

### Q: API密钥在哪里获取？
**A**: 访问硅基流动官网 https://cloud.siliconflow.cn/ 注册并创建API密钥

### Q: 如何测试API密钥是否有效？
**A**: 运行 `python quickstart.py`，如果能正常对话说明有效

---

## 📝 配置说明

系统从 `.env` 文件读取配置，使用 Pydantic Settings 进行类型安全的配置管理。

配置文件示例：
```env
SILICONFLOW_API_KEY=你的密钥
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
DEFAULT_MODEL=Qwen/Qwen2.5-7B-Instruct
EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
HF_ENDPOINT=https://hf-mirror.com
LOG_LEVEL=INFO
```

---

## 🎉 立即开始

```bash
cp config.env .env
python quickstart.py
```

