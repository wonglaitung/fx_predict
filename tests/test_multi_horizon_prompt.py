import pytest
from ml_services.multi_horizon_prompt import MultiHorizonPromptBuilder


def test_prompt_builder_initialization():
    """测试 PromptBuilder 初始化"""
    builder = MultiHorizonPromptBuilder()
    assert builder is not None


def test_build_prompt():
    """测试构建 Prompt"""
    # 创建测试上下文
    test_context = {
        'pair': 'EUR',
        'current_price': 1.1570,
        'data_date': '2026-03-20',
        'predictions': {
            1: {'prediction': 1, 'probability': 0.5132, 'confidence': 'medium', 'target_date': '2026-03-21'},
            5: {'prediction': 0, 'probability': 0.5000, 'confidence': 'low', 'target_date': '2026-03-25'},
            20: {'prediction': 0, 'probability': 0.5000, 'confidence': 'low', 'target_date': '2026-04-09'}
        },
        'technical_indicators': {
            'trend': {'SMA5': 1.1568, 'RSI14': 28.5},
            'momentum': {},
            'volatility': {},
            'volume': {},
            'price_pattern': {},
            'market_environment': {}
        },
        'consistency_analysis': {
            'score': 0.33,
            'interpretation': '低一致性',
            'all_same': False,
            'majority_trend': '下跌'
        }
    }

    builder = MultiHorizonPromptBuilder()
    prompt = builder.build(test_context)

    # 验证 Prompt 包含必要信息
    assert 'EUR' in prompt
    assert '1.1570' in prompt
    assert '1天' in prompt
    assert '5天' in prompt
    assert '20天' in prompt
    assert 'JSON 格式' in prompt