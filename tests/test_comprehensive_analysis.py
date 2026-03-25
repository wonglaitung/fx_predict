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

    # 创建模拟预测结果
    ml_prediction = {
        'pair': 'EUR',
        'prediction': 1,
        'probability': 0.65,
        'confidence': 'high'
    }

    # 分析
    result = analyzer.analyze_pair('EUR', data, ml_prediction)

    assert result is not None
    assert 'recommendation' in result
    assert result['recommendation'] in ['buy', 'sell', 'hold']
    assert 'confidence' in result


def test_signal_validation():
    """测试信号验证 - 硬性约束"""
    analyzer = ComprehensiveAnalyzer()

    # 低概率预测（应该禁止买入）
    ml_prediction = {
        'prediction': 1,
        'probability': 0.45,  # 低于 0.50
        'confidence': 'low'
    }

    # 创建测试数据（包含完整 OHLC 数据）
    data = pd.DataFrame({
        'Close': [1.0, 1.01, 1.02],
        'High': [1.01, 1.02, 1.03],
        'Low': [0.99, 1.00, 1.01]
    })

    result = analyzer.analyze_pair('EUR', data, ml_prediction)

    # 应该不推荐买入
    assert result['recommendation'] != 'buy'


def test_high_probability_recommendation():
    """测试高概率推荐"""
    analyzer = ComprehensiveAnalyzer()

    # 高概率预测
    ml_prediction = {
        'prediction': 1,
        'probability': 0.72,  # 高于 0.60
        'confidence': 'high'
    }

    # 创建测试数据（包含完整 OHLC 数据）
    data = pd.DataFrame({
        'Close': [1.0, 1.01, 1.02],
        'High': [1.01, 1.02, 1.03],
        'Low': [0.99, 1.00, 1.01]
    })

    result = analyzer.analyze_pair('EUR', data, ml_prediction)

    # 应该推荐买入
    assert result['recommendation'] == 'buy'