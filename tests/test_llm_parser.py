import pytest
from ml_services.llm_parser import LLMAnalysisParser


def test_parser_initialization():
    """测试 Parser 初始化"""
    parser = LLMAnalysisParser()
    assert parser is not None