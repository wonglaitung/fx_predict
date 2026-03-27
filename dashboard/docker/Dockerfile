# 多阶段构建：第一阶段构建 Dashboard
FROM node:18-alpine AS dashboard-builder

WORKDIR /app/dashboard

# 复制 Dashboard 依赖文件
COPY dashboard/package*.json ./

# 安装 Dashboard 依赖
RUN npm ci --only=production

# 复制 Dashboard 源代码
COPY dashboard/ ./

# ========================================
# 第二阶段：最终镜像
FROM node:18-alpine

# 安装 Python 3 和必要工具
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash \
    curl \
    && rm -rf /var/cache/apk/*

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY requirements.txt ./
COPY run_full_pipeline.sh ./
COPY comprehensive_analysis.py ./
COPY config.py ./
COPY data_services/ ./data_services/
COPY ml_services/ ./ml_services/
COPY llm_services/ ./llm_services/

# 安装 Python 依赖
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

# 从第一阶段复制 Dashboard
COPY --from=dashboard-builder /app/dashboard ./dashboard

# 创建必要的目录
RUN mkdir -p data/raw data/models data/predictions logs

# 复制启动脚本
COPY dashboard/docker/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 设置环境变量
ENV NODE_ENV=production
ENV PORT=3000
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# 启动入口点
ENTRYPOINT ["docker-entrypoint.sh"]