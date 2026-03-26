import pytest
import json
from ml_services.json_formatter import JSONFormatter


def test_formatter_initialization():
    """测试 JSONFormatter 初始化"""
    formatter = JSONFormatter()
    assert formatter is not None


def test_format_json():
    """测试格式化 JSON"""
    formatter = JSONFormatter()

    # 创建测试数据
    context = {
        'pair': 'EUR',
        'current_price': 1.1570,
        'data_date': '2026-03-20',
        'predictions': {1: {'prediction': 1, 'probability': 0.51, 'confidence': 'medium', 'target_date': '2026-03-21'}},
        'technical_indicators': {'trend': {}, 'momentum': {}, 'volatility': {}, 'volume': {}, 'price_pattern': {}, 'market_environment': {}},
        'consistency_analysis': {'score': 1.0, 'interpretation': '完全一致', 'all_same': True, 'majority_trend': '上涨'}
    }

    llm_result = {
        'summary': '测试摘要',
        'overall_assessment': '中性',
        'key_factors': ['因素1'],
        'horizon_analysis': {
            '1': {'recommendation': 'buy', 'confidence': 'medium', 'analysis': '分析1', 'key_points': ['点1']},
            '5': {'recommendation': 'hold', 'confidence': 'low', 'analysis': '分析2', 'key_points': ['点2']},
            '20': {'recommendation': 'sell', 'confidence': 'medium', 'analysis': '分析3', 'key_points': ['点3']}
        }
    }

    strategies = {
        'short_term': {
            'name': '短线策略',
            'horizon': 1,
            'recommendation': 'buy',
            'confidence': 'medium',
            'entry_price': 1.1570,
            'stop_loss': 1.1470,
            'take_profit': 1.1670,
            'risk_reward_ratio': 1.0,
            'position_size': 'small',
            'reasoning': '理由'
        },
        'medium_term': {
            'name': '中线策略',
            'horizon': 5,
            'recommendation': 'hold',
            'confidence': 'low',
            'entry_price': 1.1570,
            'stop_loss': 1.1470,
            'take_profit': 1.1670,
            'risk_reward_ratio': 1.0,
            'position_size': 'small',
            'reasoning': '理由'
        },
        'long_term': {
            'name': '长线策略',
            'horizon': 20,
            'recommendation': 'sell',
            'confidence': 'medium',
            'entry_price': 1.1570,
            'stop_loss': 1.1670,
            'take_profit': 1.1470,
            'risk_reward_ratio': 1.0,
            'position_size': 'small',
            'reasoning': '理由'
        }
    }

    result = formatter.format(context, llm_result, strategies)

    # 验证 JSON 格式
    parsed = json.loads(result)
    assert 'metadata' in parsed
    assert parsed['metadata']['pair'] == 'EUR'


def test_write_to_file():
    """测试写入文件"""
    import os
    from pathlib import Path

    formatter = JSONFormatter()

    json_str = '{"test": "data"}'
    file_path = formatter.write_to_file(json_str, 'EUR')

    # 验证文件存在
    assert os.path.exists(file_path)

    # 验证文件内容
    with open(file_path, 'r') as f:
        content = f.read()

    assert json.loads(content) == {"test": "data"}

    # 清理
    os.remove(file_path)