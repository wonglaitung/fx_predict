#!/bin/bash

################################################################################
# FX Predict Docker 部署脚本
# 替代 docker-compose 功能
################################################################################

set -e

# 配置
IMAGE_NAME="fx-predict"
CONTAINER_NAME="fx-predict-app"
DASHBOARD_PORT="${DASHBOARD_PORT:-3000}"
TIMEZONE="${TIMEZONE:-Asia/Shanghai}"
# 脚本所在目录是 dashboard/docker/，项目根目录是它的父目录的父目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
用法: $0 [命令] [选项]

命令:
  build        构建 Docker 镜像
  up           启动容器（后台运行）
  down         停止并删除容器
  restart      重启容器
  stop         停止容器
  start        启动已停止的容器
  ps           查看容器状态
  logs         查看容器日志
  exec         在容器中执行命令
  status       查看详细状态
  clean        清理未使用的镜像和容器
  help         显示帮助信息

选项:
  --no-build   启动时不重新构建镜像
  --detach     后台运行（默认）
  --force      强制重建镜像
  --tail N     只显示最后 N 行日志

示例:
  # 构建镜像
  $0 build

  # 启动容器
  $0 up

  # 查看日志
  $0 logs

  # 重启容器
  $0 restart

  # 停止容器
  $0 down

  # 在容器中执行命令
  $0 exec bash

  # 查看状态
  $0 status
EOF
}

# 构建 Docker 镜像
build_image() {
    local force=false
    [[ "$1" == "--force" ]] && force=true

    print_info "构建 Docker 镜像..."
    
    # 切换到项目根目录运行 Docker 构建
    (
        cd "$PROJECT_DIR"
        if [ "$force" = true ]; then
            docker build --no-cache -t "$IMAGE_NAME" -f dashboard/docker/Dockerfile .
        else
            docker build -t "$IMAGE_NAME" -f dashboard/docker/Dockerfile .
        fi
    )

    if [ $? -eq 0 ]; then
        print_success "镜像构建成功: $IMAGE_NAME"
    else
        print_error "镜像构建失败"
        exit 1
    fi
}

# 启动容器
run_container() {
    local no_build=false
    [[ "$1" == "--no-build" ]] && no_build=true

    print_info "启动容器..."

    # 检查镜像是否存在
    if ! docker image inspect "$IMAGE_NAME" &> /dev/null; then
        print_warning "镜像不存在，开始构建..."
        build_image
    fi

    # 检查容器是否已运行
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        print_warning "容器已在运行"
        docker ps -f name="$CONTAINER_NAME"
        return
    fi

    # 创建必要的目录
    mkdir -p "$PROJECT_DIR/data/raw"
    mkdir -p "$PROJECT_DIR/data/models"
    mkdir -p "$PROJECT_DIR/data/predictions"
    mkdir -p "$PROJECT_DIR/logs"

    # 运行容器
    docker run -d \
        --name "$CONTAINER_NAME" \
        --restart unless-stopped \
        -p "$DASHBOARD_PORT:3000" \
        -e NODE_ENV=production \
        -e PORT=3000 \
        -e PYTHONUNBUFFERED=1 \
        -e TZ="$TIMEZONE" \
        -v "$PROJECT_DIR/.env:/app/.env" \
        -v "$PROJECT_DIR/config.py:/app/config.py" \
        -v "$PROJECT_DIR/data/raw:/app/data/raw" \
        -v "$PROJECT_DIR/data/models:/app/data/models" \
        -v "$PROJECT_DIR/data/predictions:/app/data/predictions" \
        -v "$PROJECT_DIR/logs:/app/logs" \
        --health-cmd="node -e \"require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})\"" \
        --health-interval=30s \
        --health-timeout=10s \
        --health-retries=3 \
        --health-start-period=40s \
        --log-driver json-file \
        --log-opt max-size=10m \
        --log-opt max-file=3 \
        "$IMAGE_NAME"

    if [ $? -eq 0 ]; then
        print_success "容器启动成功"
        print_info "Dashboard 访问地址: http://localhost:$DASHBOARD_PORT"
        print_info "查看日志: $0 logs"
    else
        print_error "容器启动失败"
        exit 1
    fi
}

# 停止并删除容器
stop_container() {
    print_info "停止容器..."

    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        docker stop "$CONTAINER_NAME"
        docker rm "$CONTAINER_NAME"
        print_success "容器已停止并删除"
    else
        print_warning "容器未运行"
    fi
}

# 重启容器
restart_container() {
    print_info "重启容器..."
    
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        docker restart "$CONTAINER_NAME"
        print_success "容器已重启"
    else
        print_warning "容器未运行，尝试启动..."
        run_container --no-build
    fi
}

# 查看容器状态
show_status() {
    print_info "容器状态:"
    docker ps -a -f name="$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    echo ""
    print_info "资源使用:"
    docker stats "$CONTAINER_NAME" --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

    echo ""
    print_info "健康检查:"
    docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "N/A"

    echo ""
    print_info "镜像信息:"
    docker image inspect "$IMAGE_NAME" --format='{{.Created}}' | xargs -I {} date -d {} +"%Y-%m-%d %H:%M:%S"
}

# 查看日志
show_logs() {
    local tail_lines=""
    [[ "$1" == "--tail" ]] && tail_lines="--tail $2"

    docker logs $tail_lines -f "$CONTAINER_NAME"
}

# 在容器中执行命令
exec_command() {
    local cmd="${1:-bash}"
    print_info "在容器中执行: $cmd"
    docker exec -it "$CONTAINER_NAME" $cmd
}

# 清理未使用的资源
clean_resources() {
    print_info "清理未使用的资源..."

    print_info "停止所有已停止的容器..."
    docker container prune -f

    print_info "删除未使用的镜像..."
    docker image prune -f

    print_info "删除未使用的卷..."
    docker volume prune -f

    print_success "清理完成"
}

# 主函数
main() {
    local command="$1"
    shift || true

    case "$command" in
        build)
            build_image "$@"
            ;;
        up)
            run_container "$@"
            ;;
        down)
            stop_container
            ;;
        restart)
            restart_container
            ;;
        stop)
            stop_container
            ;;
        start)
            run_container --no-build
            ;;
        ps)
            docker ps -a -f name="$CONTAINER_NAME"
            ;;
        logs)
            show_logs "$@"
            ;;
        exec)
            exec_command "$@"
            ;;
        status)
            show_status
            ;;
        clean)
            clean_resources
            ;;
        help|--help|-h)
            show_help
            ;;
        "")
            show_help
            ;;
        *)
            print_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
