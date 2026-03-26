import pytest
import pandas as pd
import numpy as np
from ml_services.fx_trading_model import FXTradingModel


def test_model_initialization():
    """测试模型初始化"""
    model = FXTradingModel()

    assert model.config is not None
    assert model.horizon == 20


def test_model_training_with_minimum_data():
    """测试使用最小数据训练模型"""
    model = FXTradingModel()

    # 创建模拟数据 - 包含上涨和下跌
    np.random.seed(42)
    n = 150
    price = 1.0
    prices = []
    for i in range(n):
        # 模拟随机涨跌
        change = np.random.normal(0, 0.005)  # 0.5% 的波动率
        price = price * (1 + change)
        prices.append(price)

    df = pd.DataFrame({
        'Close': prices,
        'High': [p * 1.001 for p in prices],  # 模拟最高价
        'Low': [p * 0.999 for p in prices]    # 模拟最低价
    })

    # 训练模型
    metrics = model.train('EUR', df)

    assert 'accuracy' in metrics
    assert 'feature_count' in metrics


def test_model_prediction():
    """测试模型预测"""
    model = FXTradingModel()

    # 创建训练数据 - 包含上涨和下跌
    np.random.seed(42)
    n = 150
    price = 1.0
    prices = []
    for i in range(n):
        change = np.random.normal(0, 0.005)
        price = price * (1 + change)
        prices.append(price)

    df = pd.DataFrame({
        'Close': prices,
        'High': [p * 1.001 for p in prices],
        'Low': [p * 0.999 for p in prices]
    })

    # 训练模型
    model.train('EUR', df)

    # 预测
    prediction = model.predict('EUR', df.iloc[-1:])

    assert 'pair' in prediction
    assert 'prediction' in prediction
    assert 'probability' in prediction
    assert prediction['prediction'] in [0, 1]
    assert 0 <= prediction['probability'] <= 1


def test_model_save_and_load():
    """测试模型保存和加载"""
    model1 = FXTradingModel()

    # 创建训练数据 - 包含上涨和下跌
    np.random.seed(42)
    n = 150
    price = 1.0
    prices = []
    for i in range(n):
        change = np.random.normal(0, 0.005)
        price = price * (1 + change)
        prices.append(price)

    df = pd.DataFrame({
        'Close': prices,
        'High': [p * 1.001 for p in prices],
        'Low': [p * 0.999 for p in prices]
    })

    # 训练和保存模型
    model1.train('EUR', df)

    # 创建新模型并加载
    model2 = FXTradingModel()
    prediction = model2.predict('EUR', df.iloc[-1:])

    assert prediction is not None
    assert 'prediction' in prediction


def test_confidence_calculation():
    """测试置信度计算"""
    model = FXTradingModel()

    # 高置信度
    confidence = model._get_confidence(0.70)
    assert confidence == 'high'

    # 中等置信度
    confidence = model._get_confidence(0.55)
    assert confidence == 'medium'

    # 低置信度
    confidence = model._get_confidence(0.45)
    assert confidence == 'low'


def test_hard_constraint_no_buy_when_low_probability():
    """测试硬性约束：ML probability ≤ 0.50 时绝对禁止买入"""
    model = FXTradingModel()

    # 创建训练数据 - 包含上涨和下跌
    np.random.seed(42)
    n = 150
    price = 1.0
    prices = []
    for i in range(n):
        change = np.random.normal(0, 0.005)
        price = price * (1 + change)
        prices.append(price)

    df = pd.DataFrame({
        'Close': prices,
        'High': [p * 1.001 for p in prices],
        'Low': [p * 0.999 for p in prices]
    })

    # 训练模型
    model.train('EUR', df)

    # 预测
    prediction = model.predict('EUR', df.iloc[-1:])

    # 硬性约束：如果 probability ≤ 0.50，prediction 应该是 0（不买入）
    if prediction['probability'] <= 0.50:
        assert prediction['prediction'] == 0, "ML probability ≤ 0.50 时绝对禁止买入"
        assert prediction['confidence'] == 'low'


def test_predict_horizon():
    """测试单个周期预测"""
    from data_services.excel_loader import FXDataLoader

    model = FXTradingModel()
    loader = FXDataLoader()

    # 加载测试数据
    data = loader.load_pair('EUR', 'FXRate_20260320.xlsx')

    # 预测 1 天周期
    result = model.predict_horizon('EUR', data, 1)

    # 验证结果
    assert 'horizon' in result
    assert result['horizon'] == 1
    assert 'prediction' in result
    assert 'probability' in result
    assert 'confidence' in result
    assert 'target_date' in result