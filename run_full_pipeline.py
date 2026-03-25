#!/usr/bin/env python3
"""
外汇智能分析系统 - 一体化脚本

完整执行训练、预测和分析全流程，支持所有货币对。
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_services.excel_loader import FXDataLoader
from ml_services.fx_trading_model import FXTradingModel
from comprehensive_analysis import ComprehensiveAnalyzer
from config import MODEL_CONFIG

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def train_all_pairs(data_file: str, horizon: int = 20) -> Dict[str, Any]:
    """
    训练所有货币对的模型
    
    Args:
        data_file: 数据文件路径
        horizon: 预测周期（天）
    
    Returns:
        训练结果字典
    """
    logger.info("=" * 60)
    logger.info("开始训练所有货币对模型")
    logger.info("=" * 60)
    
    loader = FXDataLoader()
    all_data = loader.load_all_pairs(data_file)
    model = FXTradingModel(MODEL_CONFIG)
    
    results = {}
    
    for pair, df in all_data.items():
        try:
            logger.info(f"\n训练 {pair} 模型...")
            logger.info(f"数据点数: {len(df)}")
            
            result = model.train(pair, df, horizon=horizon)
            results[pair] = result
            
            logger.info(f"{pair} 训练完成")
            logger.info(f"准确率: {result.get('accuracy', 'N/A'):.4f}")
            
        except Exception as e:
            logger.error(f"{pair} 训练失败: {e}")
            results[pair] = {'error': str(e)}
    
    logger.info("\n" + "=" * 60)
    logger.info("所有模型训练完成")
    logger.info("=" * 60)
    
    return results


def predict_all_pairs(data_file: str, horizon: int = 20) -> Dict[str, Any]:
    """
    对所有货币对进行预测
    
    Args:
        data_file: 数据文件路径
        horizon: 预测周期（天）
    
    Returns:
        预测结果字典
    """
    logger.info("\n" + "=" * 60)
    logger.info("开始所有货币对预测")
    logger.info("=" * 60)
    
    loader = FXDataLoader()
    all_data = loader.load_all_pairs(data_file)
    model = FXTradingModel(MODEL_CONFIG)
    
    results = {}
    
    for pair, df in all_data.items():
        try:
            logger.info(f"\n预测 {pair}...")
            
            prediction = model.predict(pair, df)
            results[pair] = prediction
            
            logger.info(f"{pair} 预测完成")
            logger.info(f"预测方向: {'上涨' if prediction['prediction'] == 1 else '下跌'}")
            logger.info(f"预测概率: {prediction['probability']:.4f}")
            logger.info(f"置信度: {prediction.get('confidence', 'N/A')}")
            
        except Exception as e:
            logger.error(f"{pair} 预测失败: {e}")
            results[pair] = {'error': str(e)}
    
    logger.info("\n" + "=" * 60)
    logger.info("所有预测完成")
    logger.info("=" * 60)
    
    return results


def analyze_all_pairs(data_file: str, use_llm: bool = True, 
                      llm_length: str = 'long') -> Dict[str, Any]:
    """
    对所有货币对进行综合分析
    
    Args:
        data_file: 数据文件路径
        use_llm: 是否使用大模型分析
        llm_length: LLM 分析长度
    
    Returns:
        分析结果字典
    """
    logger.info("\n" + "=" * 60)
    logger.info("开始所有货币对综合分析")
    logger.info("=" * 60)
    
    loader = FXDataLoader()
    all_data = loader.load_all_pairs(data_file)
    model = FXTradingModel(MODEL_CONFIG)
    analyzer = ComprehensiveAnalyzer()
    
    results = {}
    
    for pair, df in all_data.items():
        try:
            logger.info(f"\n分析 {pair}...")
            
            # ML 预测
            ml_prediction = model.predict(pair, df)
            
            # 综合分析
            result = analyzer.analyze_pair(
                pair, df, ml_prediction,
                use_llm=use_llm,
                llm_length=llm_length
            )
            results[pair] = result
            
            # 输出详细分析
            logger.info("-" * 60)
            logger.info(f"货币对: {pair}")
            logger.info("-" * 60)
            logger.info(f"\n技术信号:")
            logger.info(f"  信号: {result['technical_signal']}")
            logger.info(f"  强度: {result['technical_strength']:.0f}")
            
            logger.info(f"\nML 预测:")
            logger.info(f"  方向: {'上涨' if result['ml_prediction'] == 1 else '下跌'}")
            logger.info(f"  概率: {result['ml_probability']:.4f}")
            logger.info(f"  置信度: {result['ml_confidence']}")
            
            if result.get('llm_recommendation'):
                logger.info(f"\n大模型建议:")
                logger.info(f"  建议: {result['llm_recommendation']}")
                logger.info(f"  置信度: {result['llm_confidence']}")
            
            logger.info(f"\n综合建议:")
            logger.info(f"  建议: {result['final_recommendation']}")
            logger.info(f"  置信度: {result['confidence']}")
            
            logger.info(f"\n交易参数:")
            logger.info(f"  入场价: {result['entry_price']:.4f}")
            logger.info(f"  止损位: {result['stop_loss']:.4f}")
            logger.info(f"  止盈位: {result['take_profit']:.4f}")
            logger.info(f"  风险收益比: {result['risk_reward_ratio']:.1f}")
            
            logger.info(f"\n一致性: {'是' if result['consistency'] else '否'}")
            logger.info(f"推理: {result['reasoning']}")
            
            if result.get('llm_report'):
                logger.info(f"\n{'='*60}")
                logger.info(f"大模型分析报告:")
                logger.info(f"{'='*60}")
                logger.info(f"\n{result['llm_report']}")
                
                if result.get('key_factors'):
                    logger.info(f"\n关键因素: {', '.join(result['key_factors'])}")
            
            logger.info("-" * 60)
            
        except Exception as e:
            logger.error(f"{pair} 分析失败: {e}")
            results[pair] = {'error': str(e)}
    
    logger.info("\n" + "=" * 60)
    logger.info("所有综合分析完成")
    logger.info("=" * 60)
    
    return results


def run_full_pipeline(data_file: str, horizon: int = 20,
                      use_llm: bool = True, llm_length: str = 'long',
                      skip_training: bool = False,
                      skip_prediction: bool = False,
                      skip_analysis: bool = False) -> Dict[str, Any]:
    """
    运行完整流程：训练 → 预测 → 分析
    
    Args:
        data_file: 数据文件路径
        horizon: 预测周期
        use_llm: 是否使用大模型分析
        llm_length: LLM 分析长度
        skip_training: 跳过训练
        skip_prediction: 跳过预测
        skip_analysis: 跳过分析
    
    Returns:
        所有结果字典
    """
    start_time = datetime.now()
    
    logger.info("=" * 60)
    logger.info("外汇智能分析系统 - 完整流程")
    logger.info("=" * 60)
    logger.info(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"数据文件: {data_file}")
    logger.info(f"预测周期: {horizon} 天")
    logger.info(f"大模型: {'启用' if use_llm else '禁用'}")
    if use_llm:
        logger.info(f"分析长度: {llm_length}")
    logger.info("=" * 60)
    
    all_results = {
        'train': {},
        'predict': {},
        'analyze': {}
    }
    
    # 1. 训练
    if not skip_training:
        all_results['train'] = train_all_pairs(data_file, horizon)
    else:
        logger.info("跳过训练步骤")
    
    # 2. 预测
    if not skip_prediction:
        all_results['predict'] = predict_all_pairs(data_file, horizon)
    else:
        logger.info("跳过预测步骤")
    
    # 3. 分析
    if not skip_analysis:
        all_results['analyze'] = analyze_all_pairs(
            data_file, use_llm, llm_length
        )
    else:
        logger.info("跳过分析步骤")
    
    # 汇总
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("\n" + "=" * 60)
    logger.info("完整流程完成")
    logger.info("=" * 60)
    logger.info(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"总耗时: {duration:.2f} 秒")
    logger.info("=" * 60)
    
    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="外汇智能分析系统 - 一体化脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 运行完整流程（训练 + 预测 + 分析）
  python3 run_full_pipeline.py
  
  # 跳过训练，只进行预测和分析
  python3 run_full_pipeline.py --skip-training
  
  # 跳过大模型分析
  python3 run_full_pipeline.py --no-llm
  
  # 使用 short 长度的大模型分析
  python3 run_full_pipeline.py --llm-length short
  
  # 指定数据文件和预测周期
  python3 run_full_pipeline.py --data-file FXRate_20260320.xlsx --horizon 10
        """
    )
    
    parser.add_argument(
        '--data-file',
        type=str,
        default='FXRate_20260320.xlsx',
        help='数据文件路径（默认: FXRate_20260320.xlsx）'
    )
    
    parser.add_argument(
        '--horizon',
        type=int,
        default=20,
        help='预测周期（天）（默认: 20）'
    )
    
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='禁用大模型分析（默认启用）'
    )
    
    parser.add_argument(
        '--llm-length',
        type=str,
        choices=['short', 'medium', 'long'],
        default='long',
        help='大模型分析长度（默认: long）'
    )
    
    parser.add_argument(
        '--skip-training',
        action='store_true',
        help='跳过训练步骤'
    )
    
    parser.add_argument(
        '--skip-prediction',
        action='store_true',
        help='跳过预测步骤'
    )
    
    parser.add_argument(
        '--skip-analysis',
        action='store_true',
        help='跳过分析步骤'
    )
    
    args = parser.parse_args()
    
    # 运行完整流程
    results = run_full_pipeline(
        data_file=args.data_file,
        horizon=args.horizon,
        use_llm=not args.no_llm,
        llm_length=args.llm_length,
        skip_training=args.skip_training,
        skip_prediction=args.skip_prediction,
        skip_analysis=args.skip_analysis
    )
    
    return 0


if __name__ == "__main__":
    sys.exit(main())