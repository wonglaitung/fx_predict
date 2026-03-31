#!/bin/bash

# 显示当前 Dashboard 正在展示的预测文件

echo "========================================"
echo "Dashboard 当前展示的预测文件"
echo "========================================"
echo ""

# 定义货币对列表
pairs=("EUR" "JPY" "AUD" "GBP" "CAD" "NZD" "HKD")

# 遍历每个货币对
for pair in "${pairs[@]}"; do
    # 获取该货币对的最新文件
    latest_file=$(ls -lt data/predictions/${pair}_multi_horizon_*.json 2>/dev/null | head -1 | awk '{print $NF}')
    
    if [ -n "$latest_file" ]; then
        # 提取文件名和修改时间
        filename=$(basename "$latest_file")
        mod_time=$(ls -l "$latest_file" | awk '{print $6, $7, $8}')
        file_size=$(ls -lh "$latest_file" | awk '{print $5}')
        
        echo "【${pair}】"
        echo "  文件名: $filename"
        echo "  大小:   $file_size"
        echo "  时间:   $mod_time"
        echo ""
    else
        echo "【${pair}】"
        echo "  未找到文件"
        echo ""
    fi
done

echo "========================================"
echo "总计: ${#pairs[@]} 个货币对"
echo "========================================"