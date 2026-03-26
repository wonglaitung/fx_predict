import pytest
import pandas as pd
import numpy as np
from comprehensive_analysis import ComprehensiveAnalyzer


def test_analyzer_initialization():
    """测试分析器初始化"""
    analyzer = ComprehensiveAnalyzer()

    assert analyzer is not None


def test_analyze_pair_basic():
    """测试基本分析功能"""
    analyzer = ComprehensiveAnalyzer()

    # 创建测试数据
    prices = [1.0 + i * 0.01 for i in range(100)]
    data = pd.DataFrame({
        'Close': prices,
        'High': [p + 0.01 for p in prices],
        'Low': [p - 0.01 for p in prices]
    })

    # 分析（使用规则引擎，因为LLM不可用）
    result = analyzer.analyze_pair('EUR', data, use_llm=False)

    assert result is not None
    assert 'llm_analysis' in result
    assert 'horizon_analysis' in result['llm_analysis']
    # 检查 1-day horizon 的推荐
    assert '1' in result['llm_analysis']['horizon_analysis']
    recommendation_1d = result['llm_analysis']['horizon_analysis']['1']['recommendation']
    assert recommendation_1d in ['buy', 'sell', 'hold']
    assert 'confidence' in result['llm_analysis']['horizon_analysis']['1']


def test_signal_validation():
    """测试信号验证 - 硬性约束"""
    analyzer = ComprehensiveAnalyzer()

    # 创建测试数据（包含完整 OHLC 数据）
    # 使用足够的数据来计算所有技术指标
    prices = [1.0 + i * 0.01 for i in range(150)]
    data = pd.DataFrame({
        'Close': prices,
        'High': [p + 0.01 for p in prices],
        'Low': [p - 0.01 for p in prices]
    })

    # 分析（使用规则引擎）
    result = analyzer.analyze_pair('EUR', data, use_llm=False)

    # 验证结果结构
    assert result is not None
    assert 'llm_analysis' in result
    assert 'horizon_analysis' in result['llm_analysis']
    # 检查至少有一个horizon
    assert len(result['llm_analysis']['horizon_analysis']) > 0


def test_high_probability_recommendation():
    """测试高概率推荐"""
    analyzer = ComprehensiveAnalyzer()

    # 创建测试数据（包含完整 OHLC 数据）
    # 使用足够的数据来计算所有技术指标
    prices = [1.0 + i * 0.01 for i in range(150)]
    data = pd.DataFrame({
        'Close': prices,
        'High': [p + 0.01 for p in prices],
        'Low': [p - 0.01 for p in prices]
    })

    # 分析（使用规则引擎）
    result = analyzer.analyze_pair('EUR', data, use_llm=False)

    # 验证结果结构
    assert result is not None
    assert 'llm_analysis' in result
    assert 'horizon_analysis' in result['llm_analysis']
    # 检查 1-day horizon 的推荐
    assert '1' in result['llm_analysis']['horizon_analysis']
    recommendation_1d = result['llm_analysis']['horizon_analysis']['1']['recommendation']
    assert recommendation_1d in ['buy', 'sell', 'hold']