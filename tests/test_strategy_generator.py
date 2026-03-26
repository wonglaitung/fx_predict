import pytest
from ml_services.strategy_generator import TradingStrategyGenerator


def test_strategy_generator_initialization():
    """测试 StrategyGenerator 初始化"""
    generator = TradingStrategyGenerator()
    assert generator is not None


def test_generate_strategies():
    """测试生成交易方案"""
    generator = TradingStrategyGenerator()

    # 创建测试数据
    llm_result = {
        'summary': '测试摘要',
        'overall_assessment': '中性',
        'key_factors': ['因素1'],
        'horizon_analysis': {
            '1': {'recommendation': 'buy', 'confidence': 'medium', 'analysis': '分析1', 'key_points': ['关键点1']},
            '5': {'recommendation': 'hold', 'confidence': 'low', 'analysis': '分析2', 'key_points': ['关键点2']},
            '20': {'recommendation': 'sell', 'confidence': 'medium', 'analysis': '分析3', 'key_points': ['关键点3']}
        }
    }

    context = {
        'pair': 'EUR',
        'current_price': 1.1570,
        'technical_indicators': {
            'volatility': {'ATR14': 0.0100}
        }
    }

    strategies = generator.generate(llm_result, context)

    # 验证必需字段
    assert 'short_term' in strategies
    assert 'medium_term' in strategies
    assert 'long_term' in strategies

    # 验证字段顺序
    expected_order = ['name', 'horizon', 'recommendation', 'confidence',
                     'entry_price', 'stop_loss', 'take_profit',
                     'risk_reward_ratio', 'position_size', 'reasoning']

    for strategy_name, strategy in strategies.items():
        keys = list(strategy.keys())
        assert keys == expected_order, f"{strategy_name} 字段顺序不正确"


def test_position_size_mapping():
    """测试仓位大小映射"""
    generator = TradingStrategyGenerator()

    # 测试不同置信度对应的仓位
    assert generator._determine_position_size('high', 'low') == 'large'
    assert generator._determine_position_size('medium', 'low') == 'medium'
    assert generator._determine_position_size('low', 'low') == 'small'


def test_risk_reward_ratio():
    """测试风险回报比计算"""
    generator = TradingStrategyGenerator()

    # 测试买入场景
    price_levels = generator._calculate_price_levels(1, 1.1570, 0.0100, 'buy')
    assert price_levels['entry_price'] == 1.1570
    assert price_levels['stop_loss'] < price_levels['entry_price']
    assert price_levels['take_profit'] > price_levels['entry_price']
    assert abs(price_levels['risk_reward_ratio'] - 1.0) < 0.1