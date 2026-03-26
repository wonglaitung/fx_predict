import pytest
from ml_services.multi_horizon_prompt import MultiHorizonPromptBuilder


def test_prompt_builder_initialization():
    """测试 PromptBuilder 初始化"""
    builder = MultiHorizonPromptBuilder()
    assert builder is not None