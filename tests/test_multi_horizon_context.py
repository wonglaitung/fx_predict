import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ml_services.multi_horizon_context import MultiHorizonContextBuilder
from data_services.technical_analysis import TechnicalAnalyzer
from ml_services.fx_trading_model import FXTradingModel


def test_context_builder_initialization():
    """测试 MultiHorizonContextBuilder 初始化"""
    builder = MultiHorizonContextBuilder()
    assert builder is not None
    assert builder.technical_analyzer is not None
    assert builder.model is not None


def test_build_context():
    """测试构建上下文"""
    # 创建测试数据
    dates = pd.date_range('2020-01-01', periods=150)
    close_prices = [1.0 + i * 0.001 for i in range(150)]

    test_data = pd.DataFrame({
        'Date': dates,
        'Close': close_prices,
        'Open': close_prices,
        'High': [c * 1.01 for c in close_prices],
        'Low': [c * 0.99 for c in close_prices]
    })

    builder = MultiHorizonContextBuilder()
    context = builder.build('EUR', test_data)

    # 验证基本结构
    assert context['pair'] == 'EUR'
    assert 'current_price' in context
    assert 'predictions' in context
    assert 'technical_indicators' in context
    assert 'consistency_analysis' in context

    # 验证预测数量
    assert len(context['predictions']) == 3
    assert 1 in context['predictions']
    assert 5 in context['predictions']
    assert 20 in context['predictions']


def test_consistency_calculation():
    """测试一致性计算"""
    builder = MultiHorizonContextBuilder()

    # 测试用例
    test_cases = [
        ({1: {'prediction': 1}, 5: {'prediction': 1}, 20: {'prediction': 1}}, 1.0),
        ({1: {'prediction': 0}, 5: {'prediction': 0}, 20: {'prediction': 0}}, 1.0),
        ({1: {'prediction': 1}, 5: {'prediction': 0}, 20: {'prediction': 1}}, 0.67),
        ({1: {'prediction': 1}, 5: {'prediction': 0}, 20: {'prediction': 0}}, 0.67),
    ]

    for predictions, expected_score in test_cases:
        result = builder._calculate_consistency_analysis(predictions)
        assert abs(result['score'] - expected_score) < 0.01, f"Expected {expected_score}, got {result['score']}"