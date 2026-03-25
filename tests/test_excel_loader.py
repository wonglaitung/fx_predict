import pytest
import pandas as pd
import os
from data_services.excel_loader import FXDataLoader


def test_loader_initialization():
    """测试加载器初始化"""
    loader = FXDataLoader()
    assert loader is not None


def test_load_all_pairs():
    """测试加载所有货币对数据"""
    loader = FXDataLoader()

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
    loader = FXDataLoader()

    # 检查测试文件是否存在
    test_file = 'FXRate_20260320.xlsx'
    if not os.path.exists(test_file):
        pytest.skip(f"测试文件 {test_file} 不存在")

    # 加载 EUR 数据
    eur_data = loader.load_pair('EUR', test_file)

    if eur_data is not None:
        assert isinstance(eur_data, pd.DataFrame)
        assert len(eur_data) > 0


def test_file_not_found():
    """测试文件不存在时抛出异常"""
    loader = FXDataLoader()
    with pytest.raises(FileNotFoundError):
        loader.load_pair('EUR', 'nonexistent.xlsx')


def test_worksheet_not_found():
    """测试工作表不存在时抛出异常"""
    loader = FXDataLoader()
    test_file = 'FXRate_20260320.xlsx'
    if not os.path.exists(test_file):
        pytest.skip(f"测试文件 {test_file} 不存在")
    
    with pytest.raises(ValueError, match="工作表不存在"):
        loader.load_pair('INVALID', test_file)


def test_validate_data_format():
    """测试数据格式验证"""
    loader = FXDataLoader()

    # 创建测试数据
    test_data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=10),
        'Close': [1.0 + i * 0.01 for i in range(10)],
        'SMA5': [1.0 + i * 0.01 for i in range(10)]
    })

    # 验证数据格式
    is_valid = loader._validate_data_format(test_data)
    assert is_valid is True


def test_preprocess_data():
    """测试数据预处理效果"""
    loader = FXDataLoader()
    
    # 创建测试数据
    test_data = pd.DataFrame({
        'Date': ['03/20/2026', '03/21/2026', '03/19/2026'],
        'Close': ['1.0850', '1.0860', '1.0840'],
        'SMA5': [1.0840, 1.0845, 1.0835]
    })
    
    processed = loader._preprocess(test_data)
    
    # 检查日期格式
    assert processed['Date'].dtype == 'datetime64[ns]'
    
    # 检查数据类型
    assert pd.api.types.is_numeric_dtype(processed['Close'])
    assert pd.api.types.is_numeric_dtype(processed['SMA5'])
    
    # 检查排序（升序：旧数据在前）
    dates = processed['Date'].tolist()
    assert dates[0] < dates[1] < dates[2]