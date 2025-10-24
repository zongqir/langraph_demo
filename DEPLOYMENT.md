# 🚀 生产部署指南

本文档提供将智能客服系统部署到生产环境的详细步骤和最佳实践。

---

## 📋 目录

- [部署架构](#部署架构)
- [环境准备](#环境准备)
- [部署方式](#部署方式)
- [性能优化](#性能优化)
- [监控告警](#监控告警)
- [安全加固](#安全加固)

---

## 🏗️ 部署架构

### 最小部署（单机）

```
┌─────────────────────────────────────┐
│         Nginx (反向代理)             │
│              :80/:443               │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│      FastAPI应用服务器               │
│      (uvicorn + 智能客服Agent)       │
│              :8000                  │
└──────────────┬──────────────────────┘
               ↓
┌──────────────┴──────────────────────┐
│         数据层                       │
│  ┌──────────┐    ┌─────────────┐   │
│  │  FAISS   │    │   Redis     │   │
│  │ 向量库    │    │  会话缓存   │   │
│  └──────────┘    └─────────────┘   │
└─────────────────────────────────────┘
```

### 推荐部署（分布式）

```
                  ┌─────────────┐
                  │   负载均衡   │
                  │  (Nginx)    │
                  └──────┬──────┘
                         ↓
         ┌───────────────┼───────────────┐
         ↓               ↓               ↓
    ┌────────┐      ┌────────┐     ┌────────┐
    │ API-1  │      │ API-2  │     │ API-N  │
    │FastAPI │      │FastAPI │     │FastAPI │
    └────┬───┘      └────┬───┘     └────┬───┘
         │               │               │
         └───────────────┼───────────────┘
                         ↓
              ┌──────────────────────┐
              │    共享服务层          │
              │  ┌────────────────┐  │
              │  │   Milvus       │  │
              │  │   向量数据库    │  │
              │  └────────────────┘  │
              │  ┌────────────────┐  │
              │  │   Redis        │  │
              │  │   会话管理      │  │
              │  └────────────────┘  │
              │  ┌────────────────┐  │
              │  │   RabbitMQ     │  │
              │  │   消息队列      │  │
              │  └────────────────┘  │
              └──────────────────────┘
```

---

## 💻 环境准备

### 系统要求

| 组件 | 最小配置 | 推荐配置 |
|------|---------|---------|
| **CPU** | 4核 | 8核+ |
| **内存** | 8GB | 16GB+ |
| **磁盘** | 50GB SSD | 100GB+ SSD |
| **操作系统** | Ubuntu 20.04+ | Ubuntu 22.04 LTS |
| **Python** | 3.9+ | 3.11 |

### 依赖服务

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# 安装Nginx
sudo apt install nginx -y

# 安装Redis
sudo apt install redis-server -y

# 安装监控工具
sudo apt install htop iotop -y
```

---

## 🔧 部署方式

### 方式1: 传统部署

#### 1. 克隆代码

```bash
cd /opt
sudo git clone https://github.com/your-repo/langraph_demo.git
cd langraph_demo
sudo chown -R $USER:$USER .
```

#### 2. 创建虚拟环境

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. 配置环境变量

```bash
cp .env.example .env
nano .env  # 修改配置
```

#### 4. 初始化知识库

```bash
python examples/init_knowledge_base.py
```

#### 5. 创建systemd服务

创建 `/etc/systemd/system/customer-service.service`：

```ini
[Unit]
Description=Intelligent Customer Service System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/langraph_demo
Environment="PATH=/opt/langraph_demo/venv/bin"
ExecStart=/opt/langraph_demo/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable customer-service
sudo systemctl start customer-service
sudo systemctl status customer-service
```

#### 6. 配置Nginx

创建 `/etc/nginx/sites-available/customer-service`：

```nginx
upstream customer_service {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://customer_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # 静态文件
    location /static {
        alias /opt/langraph_demo/static;
    }

    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/customer-service /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 方式2: Docker部署

#### 1. 创建Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要目录
RUN mkdir -p data logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SILICONFLOW_API_KEY=${SILICONFLOW_API_KEY}
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app
    restart: unless-stopped

volumes:
  redis_data:
```

#### 3. 构建和启动

```bash
docker-compose up -d
docker-compose logs -f
```

### 方式3: Kubernetes部署

#### 1. 创建ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: customer-service-config
data:
  SILICONFLOW_BASE_URL: "https://api.siliconflow.cn/v1"
  DEFAULT_MODEL: "Qwen/Qwen2.5-7B-Instruct"
```

#### 2. 创建Secret

```bash
kubectl create secret generic customer-service-secret \
  --from-literal=SILICONFLOW_API_KEY=your-api-key
```

#### 3. 创建Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: customer-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: customer-service
  template:
    metadata:
      labels:
        app: customer-service
    spec:
      containers:
      - name: app
        image: your-registry/customer-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: SILICONFLOW_API_KEY
          valueFrom:
            secretKeyRef:
              name: customer-service-secret
              key: SILICONFLOW_API_KEY
        envFrom:
        - configMapRef:
            name: customer-service-config
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

#### 4. 创建Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: customer-service
spec:
  selector:
    app: customer-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## ⚡ 性能优化

### 1. API服务优化

#### 使用Gunicorn + Uvicorn

```bash
pip install gunicorn

gunicorn api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300 \
  --keep-alive 5
```

#### 配置文件 `gunicorn.conf.py`

```python
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 300
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
```

### 2. 缓存策略

#### Redis缓存实现

```python
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache_response(expire=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"chat:{args[0]}:{kwargs.get('session_id')}"
            
            # 检查缓存
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            redis_client.setex(cache_key, expire, json.dumps(result))
            
            return result
        return wrapper
    return decorator
```

### 3. 向量数据库优化

#### 使用Milvus替代FAISS

```python
from pymilvus import connections, Collection

# 连接Milvus
connections.connect("default", host="localhost", port="19530")

# 创建集合
collection = Collection("knowledge_base")

# 搜索
search_params = {
    "metric_type": "L2",
    "params": {"nprobe": 10}
}

results = collection.search(
    data=[query_vector],
    anns_field="embedding",
    param=search_params,
    limit=5
)
```

### 4. 模型优化

#### 使用量化模型

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=quantization_config
)
```

---

## 📊 监控告警

### 1. 应用监控

#### 使用Prometheus + Grafana

安装Prometheus客户端：

```bash
pip install prometheus-client
```

添加监控指标：

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# 定义指标
REQUEST_COUNT = Counter('customer_service_requests_total', 'Total requests')
REQUEST_DURATION = Histogram('customer_service_request_duration_seconds', 'Request duration')
ACTIVE_SESSIONS = Gauge('customer_service_active_sessions', 'Active sessions')

# 在代码中使用
@app.post("/chat")
async def chat(message: str):
    REQUEST_COUNT.inc()
    start_time = time.time()
    
    try:
        response = await process_chat(message)
        return response
    finally:
        REQUEST_DURATION.observe(time.time() - start_time)
```

### 2. 日志监控

#### ELK Stack集成

Logstash配置：

```conf
input {
  file {
    path => "/opt/langraph_demo/logs/*.log"
    type => "customer_service"
  }
}

filter {
  json {
    source => "message"
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "customer-service-%{+YYYY.MM.dd}"
  }
}
```

### 3. 告警配置

#### AlertManager规则

```yaml
groups:
- name: customer_service
  rules:
  - alert: HighErrorRate
    expr: rate(customer_service_errors_total[5m]) > 0.05
    for: 5m
    annotations:
      summary: "High error rate detected"
      
  - alert: SlowResponse
    expr: histogram_quantile(0.95, customer_service_request_duration_seconds) > 5
    for: 5m
    annotations:
      summary: "95th percentile response time > 5s"
```

---

## 🔒 安全加固

### 1. API安全

#### 添加认证中间件

```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != "your-secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials
```

#### 限流

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request):
    pass
```

### 2. 数据安全

#### 敏感信息脱敏

```python
import re

def mask_sensitive_data(text: str) -> str:
    # 脱敏手机号
    text = re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', text)
    # 脱敏身份证
    text = re.sub(r'(\d{6})\d{8}(\d{4})', r'\1********\2', text)
    return text
```

### 3. HTTPS配置

#### Let's Encrypt证书

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🔍 健康检查

### API健康检查端点

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/ready")
async def readiness_check():
    # 检查依赖服务
    checks = {
        "redis": check_redis(),
        "vector_db": check_vector_db(),
        "llm": check_llm()
    }
    
    if all(checks.values()):
        return {"status": "ready", "checks": checks}
    else:
        raise HTTPException(status_code=503, detail="Not ready")
```

---

## 📈 扩容策略

### 水平扩展

1. **增加API服务器**
   ```bash
   # 使用负载均衡器分发流量
   upstream backend {
       server 10.0.1.1:8000;
       server 10.0.1.2:8000;
       server 10.0.1.3:8000;
   }
   ```

2. **向量数据库分片**
   - 按业务类型分片（产品/FAQ/技术）
   - 按时间分片（最近/历史）

3. **读写分离**
   - 主库处理写入
   - 从库处理查询

### 垂直扩展

- 升级服务器配置
- 使用GPU加速模型推理
- 优化内存使用

---

## 🐛 故障排查

### 常见问题

1. **内存溢出**
   ```bash
   # 查看内存使用
   free -h
   
   # 调整进程数
   workers = 2  # 减少worker数量
   ```

2. **响应超时**
   ```bash
   # 增加超时时间
   timeout = 600
   
   # 检查慢查询
   tail -f logs/app.log | grep "duration"
   ```

3. **连接数过多**
   ```bash
   # 调整连接池
   max_connections = 100
   
   # 启用连接复用
   keepalive_timeout = 65
   ```

---

## 📝 运维检查清单

### 日常检查

- [ ] 检查服务状态
- [ ] 查看错误日志
- [ ] 监控资源使用
- [ ] 检查磁盘空间
- [ ] 验证备份完整性

### 每周检查

- [ ] 审查性能指标
- [ ] 更新安全补丁
- [ ] 清理旧日志
- [ ] 优化数据库
- [ ] 测试恢复流程

### 每月检查

- [ ] 容量规划
- [ ] 安全审计
- [ ] 性能测试
- [ ] 文档更新
- [ ] 灾难恢复演练

---

**部署如有问题，请参考项目文档或提交Issue。**

