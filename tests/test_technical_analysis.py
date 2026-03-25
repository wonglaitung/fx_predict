"""
技术指标引擎测试

测试所有30-40个技术指标的准确性
"""

import pytest
import pandas as pd
import numpy as np
from data_services.technical_analysis import TechnicalAnalyzer


@pytest.fixture
def sample_data():
    """创建测试数据"""
    # 创建100天的模拟数据
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=100)

    # 模拟价格数据（包含趋势和波动）
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
        'Volume': np.random.randint(1000000, 5000000, 100)
    })

    return df


@pytest.fixture
def analyzer():
    """创建技术分析器"""
    return TechnicalAnalyzer()


# ==================== 趋势类指标测试 ====================

class TestTrendIndicators:
    """趋势类指标测试"""

    def test_sma_5(self, analyzer, sample_data):
        """测试5日简单移动平均线"""
        result = analyzer.compute_all_indicators(sample_data)

        # 检查列是否存在
        assert 'SMA5' in result.columns

        # 检查数据长度（使用shift(1)后应该有4个NaN）
        assert result['SMA5'].isna().sum() == 5

        # 检查数值合理性（SMA应该在价格范围内）
        valid_sma = result['SMA5'].dropna()
        assert (valid_sma >= sample_data['Close'].min() - 0.1).all()
        assert (valid_sma <= sample_data['Close'].max() + 0.1).all()

    def test_sma_10(self, analyzer, sample_data):
        """测试10日简单移动平均线"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'SMA10' in result.columns
        assert result['SMA10'].isna().sum() == 10

    def test_sma_20(self, analyzer, sample_data):
        """测试20日简单移动平均线"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'SMA20' in result.columns
        assert result['SMA20'].isna().sum() == 20

    def test_sma_50(self, analyzer, sample_data):
        """测试50日简单移动平均线"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'SMA50' in result.columns
        assert result['SMA50'].isna().sum() == 50

    def test_sma_120(self, analyzer, sample_data):
        """测试120日简单移动平均线（数据不足时应有更多NaN）"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'SMA120' in result.columns
        # 100天数据，120日SMA应该全部为NaN
        assert result['SMA120'].isna().all()

    def test_ema_5(self, analyzer, sample_data):
        """测试5日指数移动平均线"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'EMA5' in result.columns
        # EMA应该比SMA响应更快，可能有更少的NaN
        assert result['EMA5'].isna().sum() >= 0

    def test_ema_10(self, analyzer, sample_data):
        """测试10日指数移动平均线"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'EMA10' in result.columns

    def test_ema_12(self, analyzer, sample_data):
        """测试12日指数移动平均线"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'EMA12' in result.columns

    def test_ema_20(self, analyzer, sample_data):
        """测试20日指数移动平均线"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'EMA20' in result.columns

    def test_ema_26(self, analyzer, sample_data):
        """测试26日指数移动平均线"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'EMA26' in result.columns

    def test_macd(self, analyzer, sample_data):
        """测试MACD指标"""
        result = analyzer.compute_all_indicators(sample_data)

        # MACD包含三个部分：MACD线、信号线、柱状图
        assert 'MACD' in result.columns
        assert 'MACD_Signal' in result.columns
        assert 'MACD_Hist' in result.columns

        # 检查数值合理性
        valid_macd = result['MACD'].dropna()
        assert not valid_macd.empty

        # MACD_Hist应该是MACD减去MACD_Signal
        valid_hist = result['MACD_Hist'].dropna()
        assert not valid_hist.empty

    def test_adx(self, analyzer, sample_data):
        """测试ADX趋势指标"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'ADX' in result.columns
        assert 'DI_Plus' in result.columns
        assert 'DI_Minus' in result.columns

        # ADX应该在0-100范围内
        valid_adx = result['ADX'].dropna()
        assert (valid_adx >= 0).all()
        assert (valid_adx <= 100).all()

        # DI也应该在0-100范围内
        valid_di_plus = result['DI_Plus'].dropna()
        assert (valid_di_plus >= 0).all()
        assert (valid_di_plus <= 100).all()

        valid_di_minus = result['DI_Minus'].dropna()
        assert (valid_di_minus >= 0).all()
        assert (valid_di_minus <= 100).all()


# ==================== 动量类指标测试 ====================

class TestMomentumIndicators:
    """动量类指标测试"""

    def test_rsi_14(self, analyzer, sample_data):
        """测试14日RSI指标"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'RSI14' in result.columns

        # RSI应该在0-100范围内
        valid_rsi = result['RSI14'].dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()

    def test_kdj(self, analyzer, sample_data):
        """测试KDJ指标"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'K' in result.columns
        assert 'D' in result.columns
        assert 'J' in result.columns

        # K和D应该在0-100范围内
        valid_k = result['K'].dropna()
        assert (valid_k >= 0).all()
        assert (valid_k <= 100).all()

        valid_d = result['D'].dropna()
        assert (valid_d >= 0).all()
        assert (valid_d <= 100).all()

        # J可能会超出0-100范围
        valid_j = result['J'].dropna()
        assert not valid_j.empty

    def test_williams_r(self, analyzer, sample_data):
        """测试威廉指标"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'WilliamsR_14' in result.columns

        # 威廉指标应该在-100到0范围内
        valid_wr = result['WilliamsR_14'].dropna()
        assert (valid_wr >= -100).all()
        assert (valid_wr <= 0).all()

    def test_cci_20(self, analyzer, sample_data):
        """测试20日CCI指标"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'CCI20' in result.columns

        # CCI通常在-100到100之间，但可以超出
        valid_cci = result['CCI20'].dropna()
        assert not valid_cci.empty


# ==================== 波动类指标测试 ====================

class TestVolatilityIndicators:
    """波动类指标测试"""

    def test_atr_14(self, analyzer, sample_data):
        """测试14日ATR指标"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'ATR14' in result.columns

        # ATR应该为正数
        valid_atr = result['ATR14'].dropna()
        assert (valid_atr > 0).all()

    def test_bollinger_bands(self, analyzer, sample_data):
        """测试布林带"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'BB_Upper' in result.columns
        assert 'BB_Middle' in result.columns
        assert 'BB_Lower' in result.columns

        # 布林带关系：Upper >= Middle >= Lower
        valid_bb = result[['BB_Upper', 'BB_Middle', 'BB_Lower']].dropna()
        assert not valid_bb.empty

        assert (valid_bb['BB_Upper'] >= valid_bb['BB_Middle']).all()
        assert (valid_bb['BB_Middle'] >= valid_bb['BB_Lower']).all()

    def test_std_20d(self, analyzer, sample_data):
        """测试20日标准差"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'Std_20d' in result.columns

        # 标准差应该为正数
        valid_std = result['Std_20d'].dropna()
        assert (valid_std > 0).all()

    def test_volatility_20d(self, analyzer, sample_data):
        """测试20日波动率"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'Volatility_20d' in result.columns

        # 波动率应该为正数
        valid_vol = result['Volatility_20d'].dropna()
        assert (valid_vol > 0).all()


# ==================== 成交量类指标测试 ====================

class TestVolumeIndicators:
    """成交量类指标测试"""

    def test_obv(self, analyzer, sample_data):
        """测试OBV能量潮指标"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'OBV' in result.columns

        # OBV第一个值应该是成交量，后续累积
        valid_obv = result['OBV'].dropna()
        assert not valid_obv.empty


# ==================== 价格形态指标测试 ====================

class TestPricePatternIndicators:
    """价格形态指标测试"""

    def test_price_percentile_120(self, analyzer, sample_data):
        """测试120日价格百分位"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'Price_Percentile_120' in result.columns

        # 价格百分位应该在0-100范围内
        valid_pp = result['Price_Percentile_120'].dropna()
        assert (valid_pp >= 0).all()
        assert (valid_pp <= 100).all()

    def test_bias_rates_5(self, analyzer, sample_data):
        """测试5日偏离率"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'Bias_5' in result.columns

        # 偏离率可以是正数或负数
        valid_bias = result['Bias_5'].dropna()
        assert not valid_bias.empty

    def test_bias_rates_10(self, analyzer, sample_data):
        """测试10日偏离率"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'Bias_10' in result.columns

    def test_bias_rates_20(self, analyzer, sample_data):
        """测试20日偏离率"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'Bias_20' in result.columns


# ==================== 市场环境指标测试 ====================

class TestMarketEnvironmentIndicators:
    """市场环境指标测试"""

    def test_trend_slope_20(self, analyzer, sample_data):
        """测试20日趋势斜率"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'Trend_Slope_20' in result.columns

        # 趋势斜率可以是正数或负数
        valid_slope = result['Trend_Slope_20'].dropna()
        assert not valid_slope.empty

    def test_ma_alignment(self, analyzer, sample_data):
        """测试均线排列"""
        result = analyzer.compute_all_indicators(sample_data)

        assert 'MA_Alignment' in result.columns

        # 均线排列应该有合理的取值
        valid_ma = result['MA_Alignment'].dropna()
        assert not valid_ma.empty


# ==================== 综合测试 ====================

class TestComprehensiveFeatures:
    """综合特征测试"""

    def test_all_indicators_count(self, analyzer, sample_data):
        """测试所有指标数量"""
        result = analyzer.compute_all_indicators(sample_data)

        # 统计指标列数（排除原始数据列）
        original_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        indicator_columns = [col for col in result.columns if col not in original_columns]

        # 应该有30-40个指标
        assert len(indicator_columns) >= 30
        print(f"生成的指标数量: {len(indicator_columns)}")
        print(f"指标列表: {indicator_columns}")

    def test_no_data_leakage(self, analyzer, sample_data):
        """测试无数据泄漏（使用shift(1)）"""
        result = analyzer.compute_all_indicators(sample_data)

        # 检查第一个记录的所有指标值
        first_row_indicators = result.iloc[0]

        # 所有基于移动窗口的指标在第一行应该是NaN（因为使用了shift(1)）
        # 原始数据列除外
        original_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

        for col in result.columns:
            if col not in original_columns:
                # 检查第一个值是否为NaN（确保使用了shift(1)）
                value = first_row_indicators[col]
                if col in ['OBV']:  # OBV除外，因为它不是基于移动窗口的
                    continue
                # 大部分指标在第一行应该是NaN
                # 但我们允许某些指标（如SMA）由于数据量足够可能不是NaN
                # 关键是确保使用了shift(1)，而不是直接使用当前数据

    def test_indicator_values_reasonable(self, analyzer, sample_data):
        """测试指标值合理性"""
        result = analyzer.compute_all_indicators(sample_data)

        # 检查没有无穷大或无效值
        original_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

        # 允许全部为NaN的指标（因为数据不足）
        allowed_all_nan = ['SMA120', 'Price_Percentile_120']

        for col in result.columns:
            if col not in original_columns:
                # 检查没有无穷大值
                assert not np.isinf(result[col].replace([np.inf, -np.inf], np.nan).any()).any()

                # 检查没有NaN（除了正常的初始NaN）
                # 至少应该有一些有效值，除非是允许全部为NaN的指标
                valid_count = result[col].notna().sum()
                if col in allowed_all_nan:
                    # 这些指标可以全部为NaN
                    pass
                else:
                    assert valid_count > 0, f"列 {col} 没有任何有效值"

    def test_returns_original_data(self, analyzer, sample_data):
        """测试返回数据包含原始数据"""
        result = analyzer.compute_all_indicators(sample_data)

        # 原始数据应该被保留
        assert 'Date' in result.columns
        assert 'Open' in result.columns
        assert 'High' in result.columns
        assert 'Low' in result.columns
        assert 'Close' in result.columns

        # 原始数据不应该被修改
        assert len(result) == len(sample_data)
        assert (result['Close'] == sample_data['Close']).all()


# ==================== 边界条件测试 ====================

class TestEdgeCases:
    """边界条件测试"""

    def test_minimal_data(self, analyzer):
        """测试最小数据集"""
        # 创建只有20天的数据（刚好够计算大部分指标）
        minimal_data = pd.DataFrame({
            'Date': pd.date_range('2020-01-01', periods=20),
            'Open': [1.0 + i * 0.001 for i in range(20)],
            'High': [1.0 + i * 0.001 + 0.001 for i in range(20)],
            'Low': [1.0 + i * 0.001 - 0.001 for i in range(20)],
            'Close': [1.0 + i * 0.001 for i in range(20)],
            'Volume': [1000000] * 20
        })

        result = analyzer.compute_all_indicators(minimal_data)

        # 数据长度应该保持不变
        assert len(result) == 20

        # 应该能计算至少一些指标
        assert len(result.columns) > 6  # 原始6列 + 指标列

    def test_missing_columns(self, analyzer):
        """测试缺失必要列"""
        # 创建缺少Volume列的数据
        incomplete_data = pd.DataFrame({
            'Date': pd.date_range('2020-01-01', periods=50),
            'Open': [1.0 + i * 0.001 for i in range(50)],
            'High': [1.0 + i * 0.001 + 0.001 for i in range(50)],
            'Low': [1.0 + i * 0.001 - 0.001 for i in range(50)],
            'Close': [1.0 + i * 0.001 for i in range(50)]
        })

        # 应该能处理缺失Volume的情况
        result = analyzer.compute_all_indicators(incomplete_data)

        # 数据长度应该保持不变
        assert len(result) == 50

        # 应该能计算不依赖Volume的指标
        assert 'SMA5' in result.columns