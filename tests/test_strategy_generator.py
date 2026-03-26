import pytest
from ml_services.strategy_generator import TradingStrategyGenerator


def test_strategy_generator_initialization():
    """测试 StrategyGenerator 初始化"""
    generator = TradingStrategyGenerator()
    assert generator is not None