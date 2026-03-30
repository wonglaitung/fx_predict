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

## 快速开始

### 1. 配置环境变量

确保项目根目录有 `.env` 文件：

```bash
cp .env.example .env
# 编辑 .env 文件，填入 QWEN_API_KEY
```

### 2. 构建并启动服务

```bash
# 进入 Docker 目录
cd dashboard/docker

# 构建 Docker 镜像
./docker-deploy.sh build

# 启动容器（后台运行）
./docker-deploy.sh up

# 查看日志
./docker-deploy.sh logs

# 查看容器状态
./docker-deploy.sh status
```

### 3. 访问 Dashboard

打开浏览器访问：`http://localhost:3000`

如果需要从外部访问，使用服务器 IP：`http://YOUR_SERVER_IP:3000`

## 配置说明

### 端口配置

使用环境变量修改端口：

```bash
export DASHBOARD_PORT=8080
./docker-deploy.sh up
```

或者在 `docker-deploy.sh` 脚本开头修改：
```bash
DASHBOARD_PORT="${DASHBOARD_PORT:-8080}"
```

### 时区配置

使用环境变量修改时区：

```bash
export TIMEZONE=America/New_York
./docker-deploy.sh up
```

或者在 `docker-deploy.sh` 脚本开头修改：
```bash
TIMEZONE="${TIMEZONE:-America/New_York}"
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

在 `docker-deploy.sh` 的 `run_container` 函数中修改资源限制：

```bash
docker run -d \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    --cpus="4" \
    --memory="4g" \
    --memory-reservation="1g" \
    ...
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

### 查看定时任务日志

```bash
# 查看 pipeline 执行日志
./docker-deploy.sh exec cat /app/logs/pipeline.log

# 查看 cron 守护进程日志
./docker-deploy.sh exec cat /app/logs/cron.log
```

### 更新配置

```bash
# 1. 修改宿主机的 .env 文件（项目根目录）
vim ../.env

# 2. 重启服务使配置生效
./docker-deploy.sh restart

# 或者重新构建（如果修改了代码）
./docker-deploy.sh down
./docker-deploy.sh build
./docker-deploy.sh up
```

### 进入容器

```bash
# 进入容器 shell
./docker-deploy.sh exec bash

# 查看配置的 cron 任务
./docker-deploy.sh exec crontab -l
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
# 检查服务状态
./docker-deploy.sh ps

# 查看日志
./docker-deploy.sh logs

# 检查端口占用
netstat -tulpn | grep 3000
```

### 定时任务未执行

```bash
# 检查 cron 是否运行
./docker-deploy.sh exec ps aux | grep cron

# 查看 cron 日志
./docker-deploy.sh exec cat /app/logs/cron.log

# 查看 pipeline 日志
./docker-deploy.sh exec cat /app/logs/pipeline.log

# 手动执行一次测试
./docker-deploy.sh exec bash /app/run_full_pipeline.sh
```

### 环境变量未生效

```bash
# 检查 .env 文件是否正确挂载
./docker-deploy.sh exec cat /app/.env

# 重启服务
./docker-deploy.sh restart
```

### 配置文件未生效

由于 `.env` 和 `config.py` 通过 Volume 挂载，宿主机修改后会立即在容器中生效。

**修改 .env 文件（只读挂载）：**
```bash
# 编辑 .env 文件（在宿主机上）
vim ../.env

# 容器内无法修改 .env，只能通过宿主机修改
# 修改后立即在容器中生效（无需重启）
```

**修改 config.py 文件（双向同步）：**
```bash
# 方法1：在宿主机上修改
vim ../config.py

# 方法2：在容器内部修改
./docker-deploy.sh exec vim /app/config.py
# 或者
./docker-deploy.sh exec nano /app/config.py

# 两种方式都会双向同步，修改后立即生效
```

**注意：**
- `.env` 是只读挂载，只能通过宿主机修改
- `config.py` 是读写挂载，容器内部和宿主机都可以修改，双向同步
- 如果需要立即应用配置，可以重启容器：`./docker-deploy.sh restart`
- 如果修改了端口等影响容器启动的配置，需要重建容器：
  ```bash
  ./docker-deploy.sh down
  ./docker-deploy.sh up
  ```

### 内存不足

```bash
# 查看容器资源使用
./docker-deploy.sh status

# 增加内存限制（修改 docker-deploy.sh 后重启）
./docker-deploy.sh restart
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
   - 使用防火墙规则限制访问
   - 配置反向代理的访问控制

2. **使用非 root 用户**（修改 Dockerfile）：
   ```dockerfile
   RUN addgroup -g 1000 -S appuser && \
       adduser -u 1000 -S appuser -G appuser
   USER appuser
   ```

3. **定期更新镜像**：
   ```bash
   ./docker-deploy.sh build --force
   ./docker-deploy.sh up
   ```

## 备份与恢复

### 备份数据

```bash
# 备份所有数据目录和配置文件
tar -czf backup-$(date +%Y%m%d).tar.gz ../../data/ ../../logs/ ../../.env ../../config.py

# 备份到远程
scp backup-$(date +%Y%m%d).tar.gz user@backup-server:/backups/
```

### 恢复数据

```bash
# 解压备份
tar -xzf backup-20260327.tar.gz

# 重启服务
./docker-deploy.sh restart
```

## 监控

### 健康检查

服务配置了健康检查，可以通过以下命令查看：

```bash
./docker-deploy.sh status
# 查看状态列，应该是 "healthy"
```

### 日志监控

```bash
# 实时查看所有日志
./docker-deploy.sh logs

# 只看最近 100 行
./docker-deploy.sh logs --tail 100
```

## 升级

### 更新代码

```bash
# 1. 拉取最新代码（回到项目根目录）
cd ../..
git pull

# 2. 回到 Docker 目录
cd dashboard/docker

# 3. 重新构建镜像
./docker-deploy.sh build

# 4. 重启服务
./docker-deploy.sh up

# 5. 验证升级
./docker-deploy.sh logs
```

## 性能优化

### 使用缓存加速构建

Dockerfile 已经配置了多阶段构建和缓存优化。

### 减小镜像大小

Dockerfile 使用 Debian 12 slim 基础镜像，并清理了不必要的文件。

## 故障恢复

### 容器崩溃自动重启

服务配置了 `restart: unless-stopped`，容器崩溃后会自动重启。

### 数据损坏

如果数据文件损坏，可以：

```bash
# 1. 停止服务
./docker-deploy.sh down

# 2. 恢复备份
tar -xzf backup-20260327.tar.gz

# 3. 重启服务
./docker-deploy.sh up
```

## 联系与支持

如遇到问题，请检查：
1. Docker 日志：`./docker-deploy.sh logs`
2. 配置文件：`.env` 和 `config.py`
3. 网络连接：确保可以访问通义千问 API

---

## 部署方式

### 使用 docker-deploy.sh

**优势：**
- 不需要安装 Docker Compose
- 只需要 Docker 即可
- 脚本已包含所有必要功能
- 使用简单，命令清晰

**适用场景：**
- 快速部署
- 单机部署
- 生产环境