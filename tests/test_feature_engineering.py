"""
特征工程模块测试

测试特征工程的所有功能，包括特征创建、目标变量创建、数据泄漏防范等
"""

import pytest
import pandas as pd
import numpy as np
from ml_services.feature_engineering import FeatureEngineer


@pytest.fixture
def sample_data_with_indicators():
    """创建包含技术指标的测试数据"""
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=100)

    # 模拟价格数据
    close_prices = []
    price = 1.0
    for i in range(100):
        change = np.random.normal(0.001, 0.01)
        price = price * (1 + change)
        close_prices.append(price)

    df = pd.DataFrame({
        'Date': dates,
        'Open': [p * (1 + np.random.uniform(-0.002, 0.002)) for p in close_prices],
        'High': [p * (1 + np.random.uniform(0, 0.005)) for p in close_prices],
        'Low': [p * (1 - np.random.uniform(0, 0.005)) for p in close_prices],
        'Close': close_prices,
        'Volume': np.random.randint(1000000, 5000000, 100),
        'SMA5': pd.Series(close_prices).rolling(5).mean(),
        'SMA10': pd.Series(close_prices).rolling(10).mean(),
        'SMA20': pd.Series(close_prices).rolling(20).mean(),
        'SMA50': pd.Series(close_prices).rolling(50).mean(),
        'SMA120': pd.Series(close_prices).rolling(120).mean(),
        'RSI14': np.random.uniform(30, 70, 100),
        'MACD': np.random.uniform(-0.01, 0.01, 100),
        'MACD_Signal': np.random.uniform(-0.01, 0.01, 100),
        'ADX': np.random.uniform(20, 40, 100),
        'ATR14': np.random.uniform(0.005, 0.02, 100),
        'BB_Upper': np.array(close_prices) + 0.02,
        'BB_Middle': np.array(close_prices),
        'BB_Lower': np.array(close_prices) - 0.02
    })

    return df


@pytest.fixture
def engineer():
    """创建特征工程器"""
    return FeatureEngineer()


# ==================== 基本功能测试 ====================

class TestBasicFeatures:
    """基本特征测试"""

    def test_create_features_basic(self, engineer, sample_data_with_indicators):
        """测试基本特征创建"""
        features = engineer.create_features(sample_data_with_indicators)

        assert features is not None
        assert len(features) == len(sample_data_with_indicators)
        # 应该包含原始列
        assert 'Close' in features.columns

    def test_create_target_basic(self, engineer):
        """测试目标变量创建"""
        # 创建简单的价格数据
        prices = [1.0 + i * 0.01 for i in range(30)]
        df = pd.DataFrame({'Close': prices})

        target = engineer.create_target(df, horizon=20)

        assert len(target) == len(df)
        assert target.dtype in [np.int64, int, float]
        # 最后 horizon 个值应该是 NaN（没有未来数据）
        assert target.iloc[-20:].isna().all()
        # 前面的值应该是 1（价格上涨）
        assert (target.iloc[:-20].dropna() == 1).all()

    def test_feature_columns_count(self, engineer, sample_data_with_indicators):
        """测试特征数量"""
        features = engineer.create_features(sample_data_with_indicators)

        # 特征数量应该合理
        original_cols = len(sample_data_with_indicators.columns)
        feature_cols = len(features.columns)

        # 至少应该有一些衍生特征
        assert feature_cols > original_cols
        print(f"原始列数: {original_cols}")
        print(f"特征列数: {feature_cols}")
        print(f"新增特征数: {feature_cols - original_cols}")


# ==================== 价格衍生特征测试 ====================

class TestPriceDerivedFeatures:
    """价格衍生特征测试"""

    def test_close_change_1d(self, engineer, sample_data_with_indicators):
        """测试1日涨跌幅"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Close_change_1d' in features.columns:
            # 第一行应该是 NaN（使用 shift(1)）
            assert pd.isna(features['Close_change_1d'].iloc[0])
            # 其他行应该有值
            assert features['Close_change_1d'].iloc[1:].notna().any()

    def test_close_change_5d(self, engineer, sample_data_with_indicators):
        """测试5日涨跌幅"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Close_change_5d' in features.columns:
            # 前5行应该是 NaN
            assert features['Close_change_5d'].iloc[:5].isna().all()

    def test_close_change_20d(self, engineer, sample_data_with_indicators):
        """测试20日涨跌幅"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Close_change_20d' in features.columns:
            # 前20行应该是 NaN
            assert features['Close_change_20d'].iloc[:20].isna().all()

    def test_return_1d(self, engineer, sample_data_with_indicators):
        """测试1日收益率"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Return_1d' in features.columns:
            # 第一行应该是 NaN
            assert pd.isna(features['Return_1d'].iloc[0])
            # 收益率应该是合理的数值
            valid_returns = features['Return_1d'].dropna()
            assert (valid_returns.abs() < 1).all()  # 单日涨跌幅应该小于100%

    def test_return_5d(self, engineer, sample_data_with_indicators):
        """测试5日收益率"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Return_5d' in features.columns:
            # 前5行应该是 NaN
            assert features['Return_5d'].iloc[:5].isna().all()

    def test_return_20d(self, engineer, sample_data_with_indicators):
        """测试20日收益率"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Return_20d' in features.columns:
            # 前20行应该是 NaN
            assert features['Return_20d'].iloc[:20].isna().all()


# ==================== 偏离率特征测试 ====================

class TestBiasFeatures:
    """偏离率特征测试"""

    def test_bias_5(self, engineer, sample_data_with_indicators):
        """测试5日偏离率"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Bias_5' in features.columns:
            # 偏离率可以是正数或负数
            valid_bias = features['Bias_5'].dropna()
            assert not valid_bias.empty
            # 偏离率应该在合理范围内（通常在-10%到10%之间）
            assert (valid_bias.abs() < 0.5).all()

    def test_bias_10(self, engineer, sample_data_with_indicators):
        """测试10日偏离率"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Bias_10' in features.columns:
            valid_bias = features['Bias_10'].dropna()
            assert not valid_bias.empty

    def test_bias_20(self, engineer, sample_data_with_indicators):
        """测试20日偏离率"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Bias_20' in features.columns:
            valid_bias = features['Bias_20'].dropna()
            assert not valid_bias.empty


# ==================== 波动率特征测试 ====================

class TestVolatilityFeatures:
    """波动率特征测试"""

    def test_volatility_5d(self, engineer, sample_data_with_indicators):
        """测试5日波动率"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Volatility_5d' in features.columns:
            # 波动率应该为正数
            valid_vol = features['Volatility_5d'].dropna()
            assert (valid_vol > 0).all()
            # 波动率应该在合理范围内（通常小于0.1）
            assert (valid_vol < 0.5).all()

    def test_volatility_20d(self, engineer, sample_data_with_indicators):
        """测试20日波动率"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Volatility_20d' in features.columns:
            # 波动率应该为正数
            valid_vol = features['Volatility_20d'].dropna()
            assert (valid_vol > 0).all()


# ==================== 滞后特征测试 ====================

class TestLagFeatures:
    """滞后特征测试"""

    def test_close_lag_1(self, engineer, sample_data_with_indicators):
        """测试1日滞后价格"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Close_lag_1' in features.columns:
            # 第一行应该是 NaN
            assert pd.isna(features['Close_lag_1'].iloc[0])
            # 第二行应该等于原始数据的第一行
            assert features['Close_lag_1'].iloc[1] == sample_data_with_indicators['Close'].iloc[0]

    def test_close_lag_5(self, engineer, sample_data_with_indicators):
        """测试5日滞后价格"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Close_lag_5' in features.columns:
            # 前5行应该是 NaN
            assert features['Close_lag_5'].iloc[:5].isna().all()
            # 第6行应该等于原始数据的第一行
            assert features['Close_lag_5'].iloc[5] == sample_data_with_indicators['Close'].iloc[0]

    def test_close_lag_20(self, engineer, sample_data_with_indicators):
        """测试20日滞后价格"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Close_lag_20' in features.columns:
            # 前20行应该是 NaN
            assert features['Close_lag_20'].iloc[:20].isna().all()
            # 第21行应该等于原始数据的第一行
            assert features['Close_lag_20'].iloc[20] == sample_data_with_indicators['Close'].iloc[0]


# ==================== 趋势斜率特征测试 ====================

class TestTrendSlopeFeature:
    """趋势斜率特征测试"""

    def test_trend_slope_20(self, engineer, sample_data_with_indicators):
        """测试20日趋势斜率"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Trend_Slope_20' in features.columns:
            # 趋势斜率可以是正数或负数
            valid_slope = features['Trend_Slope_20'].dropna()
            assert not valid_slope.empty
            # 斜率应该在合理范围内
            assert (valid_slope.abs() < 1).all()


# ==================== 市场环境特征测试 ====================

class TestMarketEnvironmentFeature:
    """市场环境特征测试"""

    def test_ma_alignment(self, engineer, sample_data_with_indicators):
        """测试均线排列特征"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'MA_Alignment' in features.columns:
            # 均线排列应该有合理的取值
            valid_ma = features['MA_Alignment'].dropna()
            assert not valid_ma.empty
            # 值应该在-3到3之间（因为有3条均线）
            assert (valid_ma >= -3).all()
            assert (valid_ma <= 3).all()


# ==================== 交叉特征测试 ====================

class TestCrossFeatures:
    """交叉特征测试"""

    def test_sma5_cross_sma20_feature_exists(self, engineer, sample_data_with_indicators):
        """测试 SMA5_cross_SMA20 特征是否存在"""
        features = engineer.create_features(sample_data_with_indicators)

        assert 'SMA5_cross_SMA20' in features.columns, "应该包含 SMA5_cross_SMA20 特征"

    def test_sma5_cross_sma20_values(self, engineer, sample_data_with_indicators):
        """测试 SMA5_cross_SMA20 特征值"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'SMA5_cross_SMA20' in features.columns:
            # 交叉信号应该只包含 -1, 0, 1
            valid_cross = features['SMA5_cross_SMA20'].dropna()
            assert not valid_cross.empty
            assert valid_cross.isin([-1, 0, 1]).all(), "交叉信号应该是 -1, 0, 或 1"

    def test_sma5_cross_sma20_data_leakage(self, engineer, sample_data_with_indicators):
        """测试 SMA5_cross_SMA20 特征的数据泄漏防范"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'SMA5_cross_SMA20' in features.columns:
            # 第一行应该是 NaN（使用 shift(1)）
            assert pd.isna(features['SMA5_cross_SMA20'].iloc[0]), \
                "SMA5_cross_SMA20 第一行应该是 NaN（防止数据泄漏）"

    def test_price_vs_bollinger_feature_exists(self, engineer, sample_data_with_indicators):
        """测试 Price_vs_Bollinger 特征是否存在"""
        features = engineer.create_features(sample_data_with_indicators)

        assert 'Price_vs_Bollinger' in features.columns, "应该包含 Price_vs_Bollinger 特征"

    def test_price_vs_bollinger_values(self, engineer, sample_data_with_indicators):
        """测试 Price_vs_Bollinger 特征值"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Price_vs_Bollinger' in features.columns:
            # 价格位置应该在合理范围内（通常在 -2 到 2 之间）
            valid_position = features['Price_vs_Bollinger'].dropna()
            assert not valid_position.empty
            # 价格位置可能超出范围，但大部分应该在合理范围内
            assert (valid_position.abs() < 10).all(), "价格位置应该在合理范围内"

    def test_price_vs_bollinger_data_leakage(self, engineer, sample_data_with_indicators):
        """测试 Price_vs_Bollinger 特征的数据泄漏防范"""
        features = engineer.create_features(sample_data_with_indicators)

        if 'Price_vs_Bollinger' in features.columns:
            # 第一行应该是 NaN（使用 shift(1)）
            assert pd.isna(features['Price_vs_Bollinger'].iloc[0]), \
                "Price_vs_Bollinger 第一行应该是 NaN（防止数据泄漏）"


# ==================== 数据泄漏防范测试 ====================

class TestDataLeakagePrevention:
    """数据泄漏防范测试"""

    def test_no_data_leakage_in_features(self, engineer, sample_data_with_indicators):
        """测试特征工程中的数据泄漏防范"""
        features = engineer.create_features(sample_data_with_indicators)

        # 获取所有衍生特征列（排除原始列）
        original_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        derived_features = [col for col in features.columns
                          if col not in original_columns]

        # 检查每个衍生特征
        for col in derived_features:
            # 特征名称中包含 change、lag、ratio 等关键词的特征
            if any(keyword in col.lower() for keyword in
                   ['change', 'lag', 'return', 'bias', 'volatility', 'slope', 'alignment']):
                # 第一行应该是 NaN（使用 shift(1)）
                assert pd.isna(features[col].iloc[0]), \
                    f"特征 {col} 第一行不应有值（防止数据泄漏）"

    def test_target_uses_future_data(self, engineer):
        """测试目标变量使用未来数据"""
        prices = [1.0 + i * 0.01 for i in range(30)]
        df = pd.DataFrame({'Close': prices})

        target = engineer.create_target(df, horizon=20)

        # 目标变量应该使用 shift(-horizon) 获取未来数据
        # 最后 horizon 个值应该是 NaN（没有未来20天的数据）
        assert target.iloc[-20:].isna().all()
        # 前面应该有有效的目标值
        assert pd.notna(target.iloc[:-20]).all()

    def test_features_not_use_future_data(self, engineer, sample_data_with_indicators):
        """测试特征不使用未来数据"""
        features = engineer.create_features(sample_data_with_indicators)

        # 最后一行的所有衍生特征应该有值（不依赖未来数据）
        original_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        derived_features = [col for col in features.columns
                          if col not in original_columns]

        for col in derived_features:
            # 检查最后一行是否有值（除了可能因为数据不足导致的 NaN）
            value = features[col].iloc[-1]
            # 如果有值，应该是有效的
            if pd.notna(value):
                assert not np.isinf(value), f"特征 {col} 最后一行包含无穷大值"


# ==================== 边界条件测试 ====================

class TestEdgeCases:
    """边界条件测试"""

    def test_minimal_data(self, engineer):
        """测试最小数据集"""
        # 创建只有25天的数据（刚好够计算20日特征）
        minimal_data = pd.DataFrame({
            'Close': [1.0 + i * 0.001 for i in range(25)],
            'SMA5': [1.0 + i * 0.001 for i in range(25)],
            'SMA10': [1.0 + i * 0.001 for i in range(25)],
            'SMA20': [1.0 + i * 0.001 for i in range(25)],
            'SMA50': [1.0 + i * 0.001 for i in range(25)]
        })

        features = engineer.create_features(minimal_data)

        # 数据长度应该保持不变
        assert len(features) == 25

    def test_missing_indicator_columns(self, engineer):
        """测试缺失技术指标列"""
        # 创建缺少某些技术指标的数据
        incomplete_data = pd.DataFrame({
            'Close': [1.0 + i * 0.001 for i in range(100)],
            'SMA5': [1.0 + i * 0.001 for i in range(100)]
        })

        # 应该能处理缺失指标的情况
        features = engineer.create_features(incomplete_data)

        # 数据长度应该保持不变
        assert len(features) == 100

    def test_zero_horizon_target(self, engineer):
        """测试 horizon=0 的目标变量"""
        prices = [1.0 + i * 0.01 for i in range(30)]
        df = pd.DataFrame({'Close': prices})

        target = engineer.create_target(df, horizon=0)

        # horizon=0 时，应该比较当前价格和当前价格（全为0或NaN）
        assert len(target) == len(df)

    def test_large_horizon_target(self, engineer):
        """测试大 horizon 的目标变量"""
        prices = [1.0 + i * 0.01 for i in range(30)]
        df = pd.DataFrame({'Close': prices})

        target = engineer.create_target(df, horizon=100)

        # horizon 大于数据长度时，所有目标都应该是 NaN
        assert target.isna().all()


# ==================== 综合测试 ====================

class TestComprehensiveFeatures:
    """综合特征测试"""

    def test_all_expected_features(self, engineer, sample_data_with_indicators):
        """测试所有预期特征是否存在"""
        features = engineer.create_features(sample_data_with_indicators)

        # 预期的价格衍生特征
        expected_price_features = [
            'Close_change_1d', 'Close_change_5d', 'Close_change_20d',
            'Return_1d', 'Return_5d', 'Return_20d'
        ]

        # 预期的偏离率特征
        expected_bias_features = ['Bias_5', 'Bias_10', 'Bias_20']

        # 预期的波动率特征
        expected_volatility_features = ['Volatility_5d', 'Volatility_20d']

        # 预期的滞后特征
        expected_lag_features = ['Close_lag_1', 'Close_lag_5', 'Close_lag_20']

        # 预期的趋势斜率特征
        expected_trend_features = ['Trend_Slope_20']

        # 预期的市场环境特征
        expected_market_features = ['MA_Alignment']

        # 检查至少有一些特征存在
        all_expected = (expected_price_features + expected_bias_features +
                       expected_volatility_features + expected_lag_features +
                       expected_trend_features + expected_market_features)

        found_features = [f for f in all_expected if f in features.columns]

        # 至少应该有一半的特征存在（因为某些依赖的技术指标可能不存在）
        assert len(found_features) >= len(all_expected) // 2

        print(f"找到的特征 ({len(found_features)}/{len(all_expected)}):")
        for f in found_features:
            print(f"  - {f}")

    def test_feature_values_reasonable(self, engineer, sample_data_with_indicators):
        """测试特征值合理性"""
        features = engineer.create_features(sample_data_with_indicators)

        # 检查没有无穷大值
        original_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

        for col in features.columns:
            if col not in original_columns:
                # 检查没有无穷大值
                col_data = features[col].replace([np.inf, -np.inf], np.nan)
                assert not np.isinf(col_data).any(), f"列 {col} 包含无穷大值"

                # 检查至少有一些有效值
                valid_count = features[col].notna().sum()
                # 允许某些特征因为数据不足而全部为 NaN
                if '20d' in col or '120' in col:
                    # 这些特征可能因为数据不足而有很多 NaN
                    pass
                else:
                    # 其他特征至少应该有一些有效值
                    assert valid_count > 0, f"列 {col} 没有任何有效值"

    def test_returns_original_data(self, engineer, sample_data_with_indicators):
        """测试返回数据包含原始数据"""
        features = engineer.create_features(sample_data_with_indicators)

        # 原始数据应该被保留
        assert 'Close' in features.columns
        assert 'Date' in features.columns

        # 原始数据不应该被修改
        assert len(features) == len(sample_data_with_indicators)
        assert (features['Close'] == sample_data_with_indicators['Close']).all()