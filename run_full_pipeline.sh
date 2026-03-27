#!/bin/bash

################################################################################
# 外汇智能分析系统 - 一体化 Shell 脚本
#
# 完整执行训练、预测和分析全流程，支持所有货币对。
################################################################################

# 设置 Python 路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
cd "${SCRIPT_DIR}"

set -e  # 遇到错误立即退出

# 加载 .env 文件（如果存在）
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 默认参数（环境变量优先，然后是默认值）
DATA_FILE="${DATA_FILE:-data/raw/FXRate_20260320.xlsx}"
USE_LLM=true
SKIP_TRAINING=false
SKIP_PREDICTION=false
SKIP_ANALYSIS=false

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
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

print_header() {
    echo ""
    echo "================================================================================"
    echo "$1"
    echo "================================================================================"
}

# 打印使用说明
print_usage() {
    cat << EOF
使用方法:
  $0 [选项]

选项:
  --data-file FILE       数据文件路径 (优先级最高，覆盖环境变量和默认值)
  --no-llm               禁用大模型分析 (默认启用)
  --skip-training        跳过训练步骤
  --skip-prediction      跳过预测步骤
  --skip-analysis        跳过分析步骤
  -h, --help             显示帮助信息

数据文件配置优先级:
  1. 命令行参数 --data-file (最高优先级)
  2. 环境变量 DATA_FILE (在 .env 文件中配置)
  3. config.py 中的默认值 (最低优先级)

默认行为:
  - 训练/预测所有周期（1天、5天、20天）
  - 启用大模型分析

示例:
  # 运行完整流程（训练 + 预测 + 分析，所有周期）
  $0

  # 跳过训练，只进行预测和分析
  $0 --skip-training

  # 跳过大模型分析
  $0 --no-llm

  # 指定数据文件（命令行参数，最高优先级）
  $0 --data-file FXRate_20260326.xlsx

  # 在 .env 文件中配置数据文件路径
  # 添加: DATA_FILE=FXRate_20260326.xlsx
EOF
    exit 0
}

# 训练所有货币对的模型
train_all_pairs() {
    print_header "开始训练所有货币对模型"

    local start_time=$(date +%s)

    # 货币对列表
    local pairs=("EUR" "JPY" "AUD" "GBP" "CAD" "NZD")

    for pair in "${pairs[@]}"; do
        print_info "训练 ${pair} 模型（所有周期）..."

        # 训练所有周期的模型
        if python3 -m ml_services.fx_trading_model \
            --mode train \
            --pair "$pair" \
            --all-horizons; then
            print_success "${pair} 所有周期模型训练完成"
        else
            print_error "${pair} 模型训练失败"
        fi

        echo ""
    done

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    print_header "所有模型训练完成"
    print_info "总耗时: ${duration} 秒"
}

# 对所有货币对进行预测
predict_all_pairs() {
    print_header "开始所有货币对预测"

    local start_time=$(date +%s)

    # 货币对列表
    local pairs=("EUR" "JPY" "AUD" "GBP" "CAD" "NZD")

    for pair in "${pairs[@]}"; do
        print_info "预测 ${pair}（所有周期）..."

        # 预测所有周期
        if python3 -m ml_services.fx_trading_model \
            --mode predict \
            --pair "$pair" \
            --all-horizons; then
            print_success "${pair} 所有周期预测完成"
        else
            print_error "${pair} 预测失败"
        fi

        echo ""
    done

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    print_header "所有预测完成"
    print_info "总耗时: ${duration} 秒"
}

# 对所有货币对进行综合分析
analyze_all_pairs() {
    print_header "开始所有货币对综合分析"

    local start_time=$(date +%s)

    # 构建命令参数
    local llm_args=""
    if [ "$USE_LLM" = false ]; then
        llm_args="--no-llm"
    fi

    # 分析所有货币对
    print_info "运行综合分析（6个货币对）..."

    if python3 -m comprehensive_analysis \
        --data_file "$DATA_FILE" \
        $llm_args; then
        print_success "所有综合分析完成"
    else
        print_error "综合分析失败"
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    print_info "分析耗时: ${duration} 秒"
}

# 运行完整流程
run_full_pipeline() {
    local script_start_time=$(date)
    local script_start_seconds=$(date +%s)

    print_header "外汇智能分析系统 - 完整流程"
    print_info "开始时间: $script_start_time"
    print_info "数据文件: $DATA_FILE"
    print_info "预测周期: 所有周期 (1天、5天、20天)"
    print_info "大模型: $([ "$USE_LLM" = true ] && echo "启用" || echo "禁用")"
    echo ""

    # 1. 训练
    if [ "$SKIP_TRAINING" = false ]; then
        train_all_pairs
    else
        print_warning "跳过训练步骤"
    fi

    # 2. 预测
    if [ "$SKIP_PREDICTION" = false ]; then
        predict_all_pairs
    else
        print_warning "跳过预测步骤"
    fi

    # 3. 分析
    if [ "$SKIP_ANALYSIS" = false ]; then
        analyze_all_pairs
    else
        print_warning "跳过分析步骤"
    fi

    # 汇总
    local script_end_time=$(date)
    local script_end_seconds=$(date +%s)
    local total_duration=$((script_end_seconds - script_start_seconds))

    print_header "完整流程完成"
    print_info "结束时间: $script_end_time"
    print_info "总耗时: $total_duration 秒"
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --data-file)
                DATA_FILE="$2"
                shift 2
                ;;
            --no-llm)
                USE_LLM=false
                shift
                ;;
            --skip-training)
                SKIP_TRAINING=true
                shift
                ;;
            --skip-prediction)
                SKIP_PREDICTION=true
                shift
                ;;
            --skip-analysis)
                SKIP_ANALYSIS=true
                shift
                ;;
            -h|--help)
                print_usage
                ;;
            *)
                print_error "未知选项: $1"
                print_usage
                exit 1
                ;;
        esac
    done
}

# 主函数
main() {
    # 解析参数
    parse_args "$@"
    
    # 运行完整流程
    run_full_pipeline
    
    return 0
}

# 执行主函数
main "$@"