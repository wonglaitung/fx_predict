# Docker 部署指南

本文档说明如何使用 Docker 部署 FX Predict 外汇智能分析系统。

## 功能特性

- **Dashboard 服务**：提供 Web 界面，实时显示外汇预测和分析结果
- **定时任务**：每小时自动执行 `run_full_pipeline.sh`，更新预测数据
- **配置管理**：通过 Volume 挂载 `.env` 和 `config.py` 文件，宿主机更新自动生效

## 前置要求

1. **Docker**：安装 Docker 20.10 或更高版本
2. **环境配置**：确保 `.env` 文件已配置好 `QWEN_API_KEY`

## 重要提示

**所有 Docker 相关文件都位于 `dashboard/docker/` 目录下。**

**使用 docker-deploy.sh 脚本时，请先进入该目录：**

```bash
cd dashboard/docker
./docker-deploy.sh build
./docker-deploy.sh up
```

**使用 docker-compose 时，请从该目录执行命令：**

```bash
cd dashboard/docker
docker-compose build
docker-compose up -d
```

## 部署方式

项目提供两种部署方式：

### 方式一：使用 docker-deploy.sh 脚本（推荐）

不需要安装 Docker Compose，使用提供的脚本即可。

### 方式二：使用 docker-compose

需要安装 Docker Compose，使用提供的 docker-compose.yml 配置文件。

## 快速开始

### 方式一：使用 docker-deploy.sh 脚本（推荐）

#### 1. 配置环境变量

确保项目根目录有 `.env` 文件：

```bash
cp .env.example .env
# 编辑 .env 文件，填入 QWEN_API_KEY
```

#### 2. 构建并启动服务

```bash
# 构建 Docker 镜像
./docker-deploy.sh build

# 启动容器（后台运行）
./docker-deploy.sh up

# 查看日志
./docker-deploy.sh logs

# 查看容器状态
./docker-deploy.sh status
```

#### 3. 访问 Dashboard

打开浏览器访问：`http://localhost:3000`

如果需要从外部访问，使用服务器 IP：`http://YOUR_SERVER_IP:3000`

### 方式二：使用 docker-compose

#### 1. 配置环境变量

确保项目根目录有 `.env` 文件：

```bash
cp .env.example .env
# 编辑 .env 文件，填入 QWEN_API_KEY
```

### 2. 构建并启动服务

```bash
# 进入 Docker 目录
cd dashboard/docker

# 构建镜像
docker-compose build

# 启动服务（后台运行）
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 3. 访问 Dashboard

打开浏览器访问：`http://localhost:3000`

如果需要从外部访问，使用服务器 IP：`http://YOUR_SERVER_IP:3000`

## 配置说明

### 端口配置

在 `dashboard/docker/docker-compose.yml` 中修改端口映射：

```yaml
ports:
  - "8080:3000"  # 将容器的 3000 端口映射到宿主机的 8080 端口
```

### 时区配置

在 `dashboard/docker/docker-compose.yml` 中修改时区：

```yaml
environment:
  - TZ=America/New_York  # 修改为你需要的时区
```

### 定时任务配置

默认每小时执行一次预测。如需修改，编辑 `docker-entrypoint.sh` 中的 cron 表达式：

```bash
# 默认：每小时执行一次
echo "0 * * * * cd /app && bash run_full_pipeline.sh >> /app/logs/pipeline.log 2>&1" > /tmp/crontab

# 修改为每 2 小时执行一次
echo "0 */2 * * * cd /app && bash run_full_pipeline.sh >> /app/logs/pipeline.log 2>&1" > /tmp/crontab
```

Cron 表达式格式：`分 时 日 月 周`

### 资源限制

在 `docker-compose.yml` 中调整资源限制：

```yaml
deploy:
  resources:
    limits:
      cpus: '4'      # 最大 4 核 CPU
      memory: 4G     # 最大 4GB 内存
    reservations:
      cpus: '1'      # 预留 1 核 CPU
      memory: 1G     # 预留 1GB 内存
```

## 常用命令

### docker-deploy.sh 脚本命令

```bash
# 构建镜像
./docker-deploy.sh build

# 启动容器（后台运行）
./docker-deploy.sh up

# 停止并删除容器
./docker-deploy.sh down

# 重启容器
./docker-deploy.sh restart

# 查看容器状态
./docker-deploy.sh ps

# 查看容器日志
./docker-deploy.sh logs

# 查看详细状态（包括健康检查和资源使用）
./docker-deploy.sh status

# 在容器中执行命令
./docker-deploy.sh exec bash

# 清理未使用的资源
./docker-deploy.sh clean

# 显示帮助信息
./docker-deploy.sh help
```

### docker-compose 命令（如果使用 docker-compose）

**重要：所有 docker-compose 命令都需要在 dashboard/docker/ 目录下执行。**

### 服务管理

```bash
# 进入 Docker 目录
cd dashboard/docker

# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f fx-predict
```

### 查看定时任务日志

```bash
# 查看 pipeline 执行日志（需要先 cd dashboard/docker）
docker-compose exec fx-predict cat /app/logs/pipeline.log

# 查看 cron 守护进程日志
docker-compose exec fx-predict cat /app/logs/cron.log
```

### 更新配置

```bash
# 1. 修改宿主机的 .env 文件（项目根目录）
vim ../.env

# 2. 重启服务使配置生效
docker-compose restart

# 或者重新构建（如果修改了代码）
docker-compose up -d --build
```

### 进入容器

```bash
# 进入容器 shell
docker-compose exec fx-predict /bin/bash

# 查看配置的 cron 任务
docker-compose exec fx-predict crontab -l
```

## 数据持久化

以下目录和文件通过 Volume 挂载，数据会保存在宿主机：

**配置文件（双向同步）：**
- `./.env`：环境变量配置文件（QWEN_API_KEY 等，只读模式）
- `./config.py`：系统配置文件（货币对、模型参数、技术指标等，读写模式）

**说明：**
- `.env` 是只读挂载（`:ro`），只能通过宿主机修改
- `config.py` 是读写挂载，容器内部和宿主机都可以修改，双向同步
- 容器内部修改 config.py 后，会立即同步到宿主机
- 宿主机修改 config.py 后，也会立即同步到容器内部

**数据目录：**
- `./data/raw/`：原始数据文件
- `./data/models/`：训练好的模型
- `./data/predictions/`：预测结果
- `./logs/`：日志文件

## 故障排查

### Dashboard 无法访问

```bash
# 检查服务状态（需要先 cd dashboard/docker）
docker-compose ps

# 查看日志
docker-compose logs fx-predict

# 检查端口占用
netstat -tulpn | grep 3000
```

### 定时任务未执行

```bash
# 检查 cron 是否运行
docker-compose exec fx-predict ps aux | grep cron

# 查看 cron 日志
docker-compose exec fx-predict cat /app/logs/cron.log

# 查看 pipeline 日志
docker-compose exec fx-predict cat /app/logs/pipeline.log

# 手动执行一次测试
docker-compose exec fx-predict bash /app/run_full_pipeline.sh
```

### 环境变量未生效

```bash
# 检查 .env 文件是否正确挂载
docker-compose exec fx-predict cat /app/.env

# 重启服务
docker-compose restart
```

### 配置文件未生效

由于 `.env` 和 `config.py` 通过 Volume 挂载，宿主机修改后会立即在容器中生效。

**修改 .env 文件（只读挂载）：**
```bash
# 编辑 .env 文件（在宿主机上）
vim ../../.env

# 容器内无法修改 .env，只能通过宿主机修改
# 修改后立即在容器中生效（无需重启）
```

**修改 config.py 文件（双向同步）：**
```bash
# 方法1：在宿主机上修改
vim ../../config.py

# 方法2：在容器内部修改
docker-compose exec fx-predict vim /app/config.py
# 或者
docker-compose exec fx-predict nano /app/config.py

# 两种方式都会双向同步，修改后立即生效
```

**注意：**
- `.env` 是只读挂载，只能通过宿主机修改
- `config.py` 是读写挂载，容器内部和宿主机都可以修改，双向同步
- 如果需要立即应用配置，可以重启容器：`docker-compose restart`
- 如果修改了端口等影响容器启动的配置，需要重建容器：
  ```bash
  docker-compose down
  docker-compose up -d
  ```

### 内存不足

```bash
# 查看容器资源使用
docker stats fx-predict-app

# 增加内存限制（修改 docker-compose.yml 后重启）
docker-compose up -d
```

## 生产环境部署

### 使用 HTTPS

建议使用反向代理（如 Nginx）提供 HTTPS：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 安全建议

1. **限制外部访问**：
   ```yaml
   # 在 docker-compose.yml 中添加
   networks:
     fx-predict-network:
       driver: bridge
       internal: false
   ```

2. **使用非 root 用户**（修改 Dockerfile）：
   ```dockerfile
   RUN addgroup -g 1000 -S appuser && \
       adduser -u 1000 -S appuser -G appuser
   USER appuser
   ```

3. **定期更新镜像**：
   ```bash
   # 需要先 cd dashboard/docker
   docker-compose pull
   docker-compose up -d
   ```

## 备份与恢复

### 备份数据

```bash
# 备份所有数据目录和配置文件（需要先 cd dashboard/docker，然后 cd .. 回到项目根目录）
tar -czf backup-$(date +%Y%m%d).tar.gz ../data/ ../logs/ ../.env ../config.py

# 备份到远程
scp backup-$(date +%Y%m%d).tar.gz user@backup-server:/backups/
```

### 恢复数据

```bash
# 解压备份
tar -xzf backup-20260327.tar.gz

# 重启服务
docker-compose restart
```

## 监控

### 健康检查

服务配置了健康检查，可以通过以下命令查看：

```bash
# 需要先 cd dashboard/docker
docker-compose ps
# 查看状态列，应该是 "healthy"
```

### 日志监控

```bash
# 实时查看所有日志
docker-compose logs -f

# 只看最近 100 行
docker-compose logs --tail=100
```

## 升级

### 更新代码

```bash
# 1. 拉取最新代码（需要先 cd .. 回到项目根目录）
git pull

# 2. 重新构建镜像（cd dashboard/docker）
docker-compose build

# 3. 重启服务
docker-compose up -d

# 4. 验证升级
docker-compose logs -f
```

### 滚动更新（零停机）

```bash
# 1. 启动新版本容器
docker-compose up -d --scale fx-predict=2

# 2. 停止旧版本容器
docker-compose up -d --scale fx-predict=1
```

## 性能优化

### 使用缓存加速构建

```dockerfile
# 在 Dockerfile 中添加
FROM node:18-alpine AS dashboard-builder
WORKDIR /app/dashboard
COPY dashboard/package*.json ./
RUN npm ci --only=production
COPY dashboard/ ./
```

### 减小镜像大小

```dockerfile
# 清理不必要的文件
RUN apk del --purge git curl && \
    rm -rf /var/cache/apk/*
```

## 故障恢复

### 容器崩溃自动重启

服务配置了 `restart: unless-stopped`，容器崩溃后会自动重启。

### 数据损坏

如果数据文件损坏，可以：

```bash
# 1. 停止服务
docker-compose down

# 2. 恢复备份
tar -xzf backup-20260327.tar.gz

# 3. 重启服务
docker-compose up -d
```

## 联系与支持

如遇到问题，请检查：
1. Docker 日志：`docker-compose logs`
2. 配置文件：`.env` 和 `docker-compose.yml`
3. 网络连接：确保可以访问通义千问 API

## 附录

### 完整的 docker-compose.yml 示例

```yaml
version: '3.8'

services:
  fx-predict:
    build:
      context: ../..
      dockerfile: dashboard/docker/Dockerfile
    container_name: fx-predict-app
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - PORT=3000
      - PYTHONUNBUFFERED=1
      - TZ=Asia/Shanghai
    volumes:
      - ./.env:/app/.env:ro
      - ./data/raw:/app/data/raw
      - ./data/models:/app/data/models
      - ./data/predictions:/app/data/predictions
      - ./logs:/app/logs
    networks:
      - fx-predict-network
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  fx-predict-network:
    driver: bridge

---

## 部署方式选择

### 推荐使用 docker-deploy.sh

**优势：**
- 不需要安装 Docker Compose
- 只需要 Docker 即可
- 脚本已包含所有必要功能
- 使用简单，命令清晰

**适用场景：**
- 快速部署
- 没有 Docker Compose 环境
- 单机部署

### 使用 docker-compose

**优势：**
- 标准的容器编排工具
- 更适合多容器应用
- 生态丰富，插件众多

**适用场景：**
- 已有 Docker Compose 环境
- 需要编排多个服务
- 生产环境部署

**选择建议：**
- 大多数情况下，使用 `docker-deploy.sh` 脚本即可满足需求
- 如果未来需要扩展到多容器应用，可以考虑迁移到 docker-compose
```