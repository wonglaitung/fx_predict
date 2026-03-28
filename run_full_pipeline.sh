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
FETCH_YAHOO=false
START_DATE="2020-01-01"
END_DATE="$(date +%Y-%m-%d)"
YAHOO_PAIRS="EUR JPY AUD GBP CAD NZD HKD"

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
  --fetch-yahoo          从 Yahoo Finance 获取最新数据
  --start-date DATE     获取数据开始日期 (格式: YYYY-MM-DD)
  --end-date DATE       获取数据结束日期 (格式: YYYY-MM-DD)
  --yahoo-pairs PAIRS    指定获取的货币对 (用空格分隔)
  --no-llm               禁用大模型分析 (默认启用)
  --skip-training        跳过训练步骤
  --skip-prediction      跳过预测步骤
  --skip-analysis        跳过分析步骤
  -h, --help             显示帮助信息

数据文件配置优先级:
  1. 命令行参数 --data-file (最高优先级)
  2. 环境变量 DATA_FILE (在 .env 文件中配置)
  3. config.py 中的默认值 (最低优先级)

Yahoo Finance 数据获取:
  使用 --fetch-yahoo 参数自动从 Yahoo Finance 获取最新数据
  可以配合 --start-date 和 --end-date 指定日期范围
  可以配合 --yahoo-pairs 指定要获取的货币对
  数据会自动保存到 data/raw/ 目录

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

  # 从 Yahoo Finance 获取最新数据并运行完整流程
  $0 --fetch-yahoo

  # 获取指定日期范围的数据
  $0 --fetch-yahoo --start-date 2025-01-01 --end-date 2026-03-27

  # 只获取特定货币对的数据
  $0 --fetch-yahoo --yahoo-pairs EUR JPY

  # 指定数据文件（命令行参数，最高优先级）
  $0 --data-file FXRate_20260326.yml

  # 在 .env 文件中配置数据文件路径
  # 添加: DATA_FILE=FXRate_20260326.xlsx
EOF
    exit 0
}

# 从 Yahoo Finance 获取数据
fetch_yahoo_data() {
    print_header "从 Yahoo Finance 获取数据"

    local start_time=$(date +%s)
    local output_file="data/raw/FXRate_$(date +%Y%m%d)_yahoo.xlsx"

    print_info "开始日期: $START_DATE"
    print_info "结束日期: $END_DATE"
    print_info "货币对: $YAHOO_PAIRS"
    print_info "输出文件: $output_file"
    echo ""

    # 构建命令参数
    local cmd="python3 fetch_fx_data.py --start-date $START_DATE --end-date $END_DATE --merge --output-file $output_file"

    # 添加货币对参数
    if [ -n "$YAHOO_PAIRS" ]; then
        cmd="$cmd --pairs $YAHOO_PAIRS"
    fi

    # 执行命令
    if eval $cmd; then
        print_success "数据获取完成: $output_file"
        
        # 更新 DATA_FILE 变量
        DATA_FILE="$output_file"
    else
        print_error "数据获取失败"
        exit 1
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    print_info "数据获取耗时: ${duration} 秒"
    echo ""
}

# 训练所有货币对的模型
train_all_pairs() {
    print_header "开始训练所有货币对模型"

    local start_time=$(date +%s)

    # 货币对列表
    local pairs=("EUR" "JPY" "AUD" "GBP" "CAD" "NZD" "HKD")

    for pair in "${pairs[@]}"; do
        print_info "训练 ${pair} 模型（所有周期）..."

        # 训练所有周期的模型
        if python3 -m ml_services.fx_trading_model \
            --mode train \
            --pair "$pair" \
            --all-horizons \
            --data_file "$DATA_FILE"; then
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
    local pairs=("EUR" "JPY" "AUD" "GBP" "CAD" "NZD" "HKD")

    for pair in "${pairs[@]}"; do
        print_info "预测 ${pair}（所有周期）..."

        # 预测所有周期
        if python3 -m ml_services.fx_trading_model \
            --mode predict \
            --pair "$pair" \
            --all-horizons \
            --data_file "$DATA_FILE"; then
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
    print_info "运行综合分析（7个货币对）..."

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

    # 0. 从 Yahoo Finance 获取数据（如果启用）
    if [ "$FETCH_YAHOO" = true ]; then
        fetch_yahoo_data
    fi

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
            --fetch-yahoo)
                FETCH_YAHOO=true
                shift
                ;;
            --start-date)
                START_DATE="$2"
                shift 2
                ;;
            --end-date)
                END_DATE="$2"
                shift 2
                ;;
            --yahoo-pairs)
                shift
                YAHOO_PAIRS=""
                while [[ $# -gt 0 && ! "$1" =~ ^- ]]; do
                    YAHOO_PAIRS="$YAHOO_PAIRS $1"
                    shift
                done
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