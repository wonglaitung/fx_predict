import pytest
import json
from ml_services.json_formatter import JSONFormatter


def test_formatter_initialization():
    """测试 JSONFormatter 初始化"""
    formatter = JSONFormatter()
    assert formatter is not None