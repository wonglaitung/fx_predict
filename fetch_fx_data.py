#!/usr/bin/env python3
"""
外汇数据获取脚本

使用 yfinance 库从 Yahoo Finance 获取外汇历史数据
支持货币对：EUR/USD, USD/JPY, AUD/USD, GBP/USD, USD/CAD, NZD/USD
"""

import yfinance as yf
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime, timedelta
import argparse
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 货币对映射：pair_code -> yfinance ticker
PAIR_TICKERS = {
    'EUR': 'EURUSD=X',
    'JPY': 'USDJPY=X',
    'AUD': 'AUDUSD=X',
    'GBP': 'GBPUSD=X',
    'CAD': 'USDCAD=X',
    'NZD': 'NZDUSD=X'
}

# 货币对中文名称
PAIR_NAMES = {
    'EUR': 'EUR/USD',
    'JPY': 'USD/JPY',
    'AUD': 'AUD/USD',
    'GBP': 'GBP/USD',
    'CAD': 'USD/CAD',
    'NZD': 'NZD/USD'
}


def fetch_pair_data(pair_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    获取单个货币对的历史数据

    Args:
        pair_code: 货币对代码 (EUR, JPY, AUD, GBP, CAD, NZD)
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)

    Returns:
        DataFrame，包含 Date, Open, High, Low, Close, Adj Close, Volume 列
    """
    ticker = PAIR_TICKERS.get(pair_code)
    if not ticker:
        raise ValueError(f"不支持的货币对: {pair_code}")

    logger.info(f"正在获取 {PAIR_NAMES[pair_code]} ({ticker}) 数据...")

    try:
        # 下载日线数据
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)

        if df.empty:
            logger.warning(f"未获取到 {pair_code} 的数据")
            return pd.DataFrame()

        # 重置索引，将 Date 作为列
        df = df.reset_index()

        # 处理 MultiIndex 列（如果存在）
        if isinstance(df.columns, pd.MultiIndex):
            # 将 MultiIndex 转换为单层列名
            df.columns = df.columns.get_level_values(0)

        # 确保列名符合系统要求
        if 'Date' not in df.columns:
            logger.warning(f"{pair_code} 数据缺少 Date 列")
            return pd.DataFrame()

        # 格式化日期列为 MM/DD/YYYY
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%m/%d/%Y')

        # 只保留需要的列
        required_columns = ['Date', 'Close']
        if all(col in df.columns for col in required_columns):
            df = df[required_columns]
            logger.info(f"成功获取 {pair_code} 数据: {len(df)} 条记录")
            return df
        else:
            logger.error(f"{pair_code} 数据缺少必需列: {required_columns}")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"获取 {pair_code} 数据失败: {e}")
        return pd.DataFrame()


def fetch_all_pairs(start_date: str, end_date: str, output_dir: str = 'data/raw') -> dict:
    """
    获取所有货币对的历史数据

    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        output_dir: 输出目录

    Returns:
        字典 {pair_code: DataFrame}
    """
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = {}

    for pair_code in PAIR_TICKERS.keys():
        df = fetch_pair_data(pair_code, start_date, end_date)

        if not df.empty:
            # 保存为 Excel 文件
            output_file = output_path / f'{pair_code}_data.xlsx'
            df.to_excel(output_file, index=False)
            logger.info(f"已保存 {pair_code} 数据到 {output_file}")
            results[pair_code] = df
        else:
            logger.warning(f"跳过 {pair_code}，未获取到数据")

    return results


def merge_to_single_file(data: dict, output_file: str = 'data/raw/FXRate.xlsx'):
    """
    将所有货币对数据合并到一个 Excel 文件中

    Args:
        data: 字典 {pair_code: DataFrame}
        output_file: 输出文件路径
    """
    if not data:
        logger.warning("没有数据可合并")
        return

    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 使用 ExcelWriter 写入多个工作表
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for pair_code, df in data.items():
                df.to_excel(writer, sheet_name=pair_code, index=False)

        logger.info(f"已合并所有数据到 {output_file}")

    except Exception as e:
        logger.error(f"合并数据失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='获取外汇历史数据')
    parser.add_argument('--start-date', type=str, default='2020-01-01',
                        help='开始日期 (YYYY-MM-DD)，默认: 2020-01-01')
    parser.add_argument('--end-date', type=str, default=None,
                        help='结束日期 (YYYY-MM-DD)，默认: 今天')
    parser.add_argument('--output-dir', type=str, default='data/raw',
                        help='输出目录，默认: data/raw')
    parser.add_argument('--merge', action='store_true',
                        help='是否合并到单个文件')
    parser.add_argument('--output-file', type=str, default='data/raw/FXRate.xlsx',
                        help='合并后的文件路径，默认: data/raw/FXRate.xlsx')
    parser.add_argument('--pairs', type=str, nargs='+', default=list(PAIR_TICKERS.keys()),
                        help=f'要获取的货币对，默认: {list(PAIR_TICKERS.keys())}')

    args = parser.parse_args()

    # 设置结束日期
    if args.end_date:
        end_date = args.end_date
    else:
        end_date = datetime.now().strftime('%Y-%m-%d')

    logger.info(f"开始获取外汇数据")
    logger.info(f"日期范围: {args.start_date} 到 {end_date}")
    logger.info(f"货币对: {', '.join(args.pairs)}")
    logger.info(f"输出目录: {args.output_dir}")

    # 获取数据
    results = {}

    for pair_code in args.pairs:
        if pair_code not in PAIR_TICKERS:
            logger.warning(f"跳过不支持的货币对: {pair_code}")
            continue

        df = fetch_pair_data(pair_code, args.start_date, end_date)

        if not df.empty:
            # 保存为 Excel 文件
            output_file = Path(args.output_dir) / f'{pair_code}_data.xlsx'
            output_file.parent.mkdir(parents=True, exist_ok=True)
            df.to_excel(output_file, index=False)
            logger.info(f"已保存 {pair_code} 数据到 {output_file}")
            results[pair_code] = df

    # 合并数据（如果需要）
    if args.merge and results:
        merge_to_single_file(results, args.output_file)

    # 输出统计信息
    logger.info("=" * 60)
    logger.info("数据获取完成")
    logger.info(f"成功获取: {len(results)}/{len(args.pairs)} 个货币对")
    for pair_code, df in results.items():
        logger.info(f"  {PAIR_NAMES[pair_code]}: {len(df)} 条记录")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()