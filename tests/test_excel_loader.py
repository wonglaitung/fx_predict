import pytest
import pandas as pd
import os
from data_services.excel_loader import ExcelDataLoader


def test_loader_initialization():
    """测试加载器初始化"""
    loader = ExcelDataLoader()
    assert loader is not None


def test_load_all_pairs():
    """测试加载所有货币对数据"""
    loader = ExcelDataLoader()

    # 检查测试文件是否存在
    test_file = 'FXRate_20260320.xlsx'
    if not os.path.exists(test_file):
        pytest.skip(f"测试文件 {test_file} 不存在")

    # 加载数据
    all_data = loader.load_all_pairs(test_file)

    assert all_data is not None
    assert isinstance(all_data, dict)
    assert len(all_data) > 0


def test_load_single_pair():
    """测试加载单个货币对数据"""
    loader = ExcelDataLoader()

    # 检查测试文件是否存在
    test_file = 'FXRate_20260320.xlsx'
    if not os.path.exists(test_file):
        pytest.skip(f"测试文件 {test_file} 不存在")

    # 加载 EUR 数据
    eur_data = loader.load_single_pair(test_file, 'EUR')

    if eur_data is not None:
        assert isinstance(eur_data, pd.DataFrame)
        assert len(eur_data) > 0


def test_validate_data_format():
    """测试数据格式验证"""
    loader = ExcelDataLoader()

    # 创建测试数据
    test_data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=10),
        'Close': [1.0 + i * 0.01 for i in range(10)],
        'SMA5': [1.0 + i * 0.01 for i in range(10)]
    })

    # 验证数据格式
    is_valid = loader._validate_data_format(test_data)
    assert is_valid is True