"""
技术指标计算引擎

计算30-40个技术指标，包括趋势、动量、波动、成交量等类别的指标。

重要：所有指标使用 .shift(1) 防止数据泄漏！
"""

import pandas as pd
import numpy as np
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """技术指标计算引擎"""

    def __init__(self):
        """初始化技术分析器"""
        self.logger = logger

    def compute_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有技术指标

        Args:
            df: 原始数据（需包含 Date, Close, Open, High, Low 列）

        Returns:
            包含所有指标的 DataFrame

        Notes:
            - 所有指标使用滞后数据（.shift(1)），防止数据泄漏
            - 返回的 DataFrame 会包含原始数据和新计算的所有指标
        """
        # 创建副本以避免修改原始数据
        result = df.copy()

        # 确保数据按日期排序
        if 'Date' in result.columns:
            result = result.sort_values('Date').reset_index(drop=True)

        # ==================== 趋势类指标 ====================

        # SMA (简单移动平均线)
        result['SMA5'] = self.compute_sma(result, period=5)
        result['SMA10'] = self.compute_sma(result, period=10)
        result['SMA20'] = self.compute_sma(result, period=20)
        result['SMA50'] = self.compute_sma(result, period=50)
        result['SMA120'] = self.compute_sma(result, period=120)

        # EMA (指数移动平均线)
        result['EMA5'] = self.compute_ema(result, period=5)
        result['EMA10'] = self.compute_ema(result, period=10)
        result['EMA12'] = self.compute_ema(result, period=12)
        result['EMA20'] = self.compute_ema(result, period=20)
        result['EMA26'] = self.compute_ema(result, period=26)

        # MACD
        macd_data = self.compute_macd(result)
        result['MACD'] = macd_data['MACD']
        result['MACD_Signal'] = macd_data['MACD_Signal']
        result['MACD_Hist'] = macd_data['MACD_Hist']

        # ADX
        adx_data = self.compute_adx(result)
        result['ADX'] = adx_data['ADX']
        result['DI_Plus'] = adx_data['DI_Plus']
        result['DI_Minus'] = adx_data['DI_Minus']

        # ==================== 动量类指标 ====================

        # RSI
        result['RSI14'] = self.compute_rsi(result, period=14)

        # KDJ
        kdj_data = self.compute_kdj(result)
        result['K'] = kdj_data['K']
        result['D'] = kdj_data['D']
        result['J'] = kdj_data['J']

        # Williams %R
        result['Williams_R_14'] = self.compute_williams_r(result, period=14)

        # CCI
        result['CCI20'] = self.compute_cci(result, period=20)

        # ==================== 波动类指标 ====================

        # ATR
        result['ATR14'] = self.compute_atr(result, period=14)

        # Bollinger Bands
        bb_data = self.compute_bollinger_bands(result, period=20, std_dev=2)
        result['BB_Upper'] = bb_data['BB_Upper']
        result['BB_Middle'] = bb_data['BB_Middle']
        result['BB_Lower'] = bb_data['BB_Lower']

        # Std_20d (20日标准差)
        result['Std_20d'] = self.compute_std(result, period=20)

        # Volatility_20d (20日波动率)
        result['Volatility_20d'] = self.compute_volatility(result, period=20)

        # ==================== 成交量类指标 ====================

        # OBV (能量潮)
        if 'Volume' in result.columns:
            result['OBV'] = self.compute_obv(result)
        else:
            result['OBV'] = np.nan

        # ==================== 价格形态指标 ====================

        # Price_Percentile
        result['Price_Percentile_120'] = self.compute_price_percentile(result, period=120)

        # Bias_Rates (偏离率)
        result['Bias_5'] = self.compute_bias_rates(result, period=5)
        result['Bias_10'] = self.compute_bias_rates(result, period=10)
        result['Bias_20'] = self.compute_bias_rates(result, period=20)

        # ==================== 市场环境指标 ====================

        # Trend_Slope
        result['Trend_Slope_20'] = self.compute_trend_slope(result, period=20)

        # MA_Alignment
        result['MA_Alignment'] = self.compute_ma_alignment(result)

        self.logger.info(f"计算完成，共生成 {len(result.columns) - len(df.columns)} 个指标")

        return result

    # ==================== 趋势类指标实现 ====================

    def compute_sma(self, df: pd.DataFrame, period: int) -> pd.Series:
        """
        计算简单移动平均线

        Args:
            df: 数据框
            period: 周期

        Returns:
            SMA序列（使用shift(1)防止数据泄漏）
        """
        sma = df['Close'].rolling(window=period).mean().shift(1)
        return sma

    def compute_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """
        计算指数移动平均线

        Args:
            df: 数据框
            period: 周期

        Returns:
            EMA序列（使用shift(1)防止数据泄漏）
        """
        ema = df['Close'].ewm(span=period, adjust=False).mean().shift(1)
        return ema

    def compute_macd(self, df: pd.DataFrame, fast: int = 12,
                     slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        计算 MACD 指标

        Args:
            df: 数据框
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            DataFrame with columns: MACD, MACD_Signal, MACD_Hist
            （所有值都使用shift(1)防止数据泄漏）
        """
        # 计算快线和慢线EMA
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean().shift(1)
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean().shift(1)

        # MACD线
        macd_line = ema_fast - ema_slow

        # 信号线
        macd_signal = macd_line.ewm(span=signal, adjust=False).mean().shift(1)

        # MACD柱状图
        macd_hist = macd_line - macd_signal

        return pd.DataFrame({
            'MACD': macd_line,
            'MACD_Signal': macd_signal,
            'MACD_Hist': macd_hist
        })

    def compute_adx(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算 ADX (Average Directional Index) 趋势指标

        Args:
            df: 数据框（需包含 High, Low, Close）
            period: 周期

        Returns:
            DataFrame with columns: ADX, DI_Plus, DI_Minus
            （所有值都使用shift(1)防止数据泄漏）
        """
        # 计算 True Range
        high = df['High']
        low = df['Low']
        close = df['Close']

        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # 计算 +DM 和 -DM
        high_diff = high.diff()
        low_diff = -low.diff()

        plus_dm = ((high_diff > low_diff) & (high_diff > 0)) * high_diff
        minus_dm = ((low_diff > high_diff) & (low_diff > 0)) * low_diff

        # 平滑处理
        atr = tr.rolling(window=period).mean().shift(1)
        plus_di = 100 * (plus_dm.rolling(window=period).mean().shift(1) / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean().shift(1) / atr)

        # 计算 DX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)

        # 计算 ADX
        adx = dx.rolling(window=period).mean().shift(1)

        return pd.DataFrame({
            'ADX': adx,
            'DI_Plus': plus_di,
            'DI_Minus': minus_di
        })

    # ==================== 动量类指标实现 ====================

    def compute_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        计算 RSI (Relative Strength Index)

        Args:
            df: 数据框
            period: 周期

        Returns:
            RSI序列（使用shift(1)防止数据泄漏）
        """
        delta = df['Close'].diff()

        # 分离涨跌
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # 计算平均涨跌
        avg_gain = gain.rolling(window=period).mean().shift(1)
        avg_loss = loss.rolling(window=period).mean().shift(1)

        # 计算 RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def compute_kdj(self, df: pd.DataFrame, period: int = 9,
                    m1: int = 3, m2: int = 3) -> pd.DataFrame:
        """
        计算 KDJ 指标

        Args:
            df: 数据框（需包含 High, Low, Close）
            period: 周期
            m1: K值平滑周期
            m2: D值平滑周期

        Returns:
            DataFrame with columns: K, D, J
            （所有值都使用shift(1)防止数据泄漏）
        """
        # 计算最高价和最低价
        high_low = df['High'].rolling(window=period).max().shift(1)
        low_low = df['Low'].rolling(window=period).min().shift(1)

        # 计算RSV
        rsv = (df['Close'].shift(1) - low_low) / (high_low - low_low) * 100

        # 计算K, D, J
        k = rsv.ewm(com=m1 - 1, adjust=False).mean().shift(1)
        d = k.ewm(com=m2 - 1, adjust=False).mean().shift(1)
        j = 3 * k - 2 * d

        return pd.DataFrame({
            'K': k,
            'D': d,
            'J': j
        })

    def compute_williams_r(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        计算 Williams %R 威廉指标

        Args:
            df: 数据框（需包含 High, Low, Close）
            period: 周期

        Returns:
            Williams %R序列（使用shift(1)防止数据泄漏）
        """
        high_high = df['High'].rolling(window=period).max().shift(1)
        low_low = df['Low'].rolling(window=period).min().shift(1)
        close = df['Close'].shift(1)

        williams_r = (high_high - close) / (high_high - low_low) * -100

        return williams_r

    def compute_cci(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        计算 CCI (Commodity Channel Index)

        Args:
            df: 数据框（需包含 High, Low, Close）
            period: 周期

        Returns:
            CCI序列（使用shift(1)防止数据泄漏）
        """
        # 计算典型价格
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3

        # 计算SMA
        sma_tp = typical_price.rolling(window=period).mean().shift(1)

        # 计算平均绝对偏差
        mad = typical_price.rolling(window=period).apply(
            lambda x: np.mean(np.abs(x - x.mean()))
        ).shift(1)

        # 计算CCI
        cci = (typical_price.shift(1) - sma_tp) / (0.015 * mad)

        return cci

    # ==================== 波动类指标实现 ====================

    def compute_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        计算 ATR (Average True Range)

        Args:
            df: 数据框（需包含 High, Low, Close）
            period: 周期

        Returns:
            ATR序列（使用shift(1)防止数据泄漏）
        """
        high = df['High']
        low = df['Low']
        close = df['Close']

        # 计算True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # 计算ATR
        atr = tr.rolling(window=period).mean().shift(1)

        return atr

    def compute_bollinger_bands(self, df: pd.DataFrame, period: int = 20,
                                std_dev: int = 2) -> pd.DataFrame:
        """
        计算布林带

        Args:
            df: 数据框
            period: 周期
            std_dev: 标准差倍数

        Returns:
            DataFrame with columns: BB_Upper, BB_Middle, BB_Lower
            （所有值都使用shift(1)防止数据泄漏）
        """
        # 计算中轨（SMA）
        middle = df['Close'].rolling(window=period).mean().shift(1)

        # 计算标准差
        std = df['Close'].rolling(window=period).std().shift(1)

        # 计算上下轨
        upper = middle + std_dev * std
        lower = middle - std_dev * std

        return pd.DataFrame({
            'BB_Upper': upper,
            'BB_Middle': middle,
            'BB_Lower': lower
        })

    def compute_std(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        计算标准差

        Args:
            df: 数据框
            period: 周期

        Returns:
            标准差序列（使用shift(1)防止数据泄漏）
        """
        std = df['Close'].rolling(window=period).std().shift(1)
        return std

    def compute_volatility(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        计算波动率（标准差/均价）

        Args:
            df: 数据框
            period: 周期

        Returns:
            波动率序列（使用shift(1)防止数据泄漏）
        """
        std = df['Close'].rolling(window=period).std().shift(1)
        mean = df['Close'].rolling(window=period).mean().shift(1)
        volatility = std / mean

        return volatility

    # ==================== 成交量类指标实现 ====================

    def compute_obv(self, df: pd.DataFrame) -> pd.Series:
        """
        计算 OBV (On-Balance Volume) 能量潮

        Args:
            df: 数据框（需包含 Close, Volume）

        Returns:
            OBV序列（使用shift(1)防止数据泄漏）
        """
        # 计算价格变化
        price_change = df['Close'].diff()

        # OBV计算
        obv = pd.Series(index=df.index, dtype=float)
        obv.iloc[0] = df['Volume'].iloc[0]

        for i in range(1, len(df)):
            if price_change.iloc[i] > 0:
                obv.iloc[i] = obv.iloc[i-1] + df['Volume'].iloc[i]
            elif price_change.iloc[i] < 0:
                obv.iloc[i] = obv.iloc[i-1] - df['Volume'].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]

        # 使用shift(1)防止数据泄漏
        return obv.shift(1)

    # ==================== 价格形态指标实现 ====================

    def compute_price_percentile(self, df: pd.DataFrame, period: int = 120) -> pd.Series:
        """
        计算价格百分位

        Args:
            df: 数据框
            period: 周期

        Returns:
            价格百分位序列（使用shift(1)防止数据泄漏）
        """
        # 计算滚动百分位
        def percentile_func(x):
            current = x.iloc[-1]
            percentile = (x <= current).sum() / len(x) * 100
            return percentile

        # 使用rolling窗口和apply计算
        percentile = df['Close'].rolling(window=period).apply(
            lambda x: percentile_func(x),
            raw=False
        ).shift(1)

        return percentile

    def compute_bias_rates(self, df: pd.DataFrame, period: int) -> pd.Series:
        """
        计算偏离率（乖离率）

        Args:
            df: 数据框
            period: 周期

        Returns:
            偏离率序列（使用shift(1)防止数据泄漏）
        """
        sma = df['Close'].rolling(window=period).mean().shift(1)
        close = df['Close'].shift(1)

        bias = (close - sma) / sma * 100

        return bias

    # ==================== 市场环境指标实现 ====================

    def compute_trend_slope(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        计算趋势斜率（线性回归斜率）

        Args:
            df: 数据框
            period: 周期

        Returns:
            趋势斜率序列（使用shift(1)防止数据泄漏）
        """
        # 使用线性回归计算斜率
        def slope_func(x):
            # x是价格序列
            if len(x) < 2:
                return np.nan

            # 线性回归：y = a + bx
            x_values = np.arange(len(x))
            y_values = x.values

            # 计算斜率
            n = len(x_values)
            if n == 0:
                return np.nan

            x_mean = np.mean(x_values)
            y_mean = np.mean(y_values)

            numerator = np.sum((x_values - x_mean) * (y_values - y_mean))
            denominator = np.sum((x_values - x_mean) ** 2)

            if denominator == 0:
                return np.nan

            slope = numerator / denominator
            return slope

        # 计算滚动斜率
        slope = df['Close'].rolling(window=period).apply(
            slope_func,
            raw=False
        ).shift(1)

        return slope

    def compute_ma_alignment(self, df: pd.DataFrame) -> pd.Series:
        """
        计算均线排列强度

        多头排列：SMA5 > SMA10 > SMA20 > SMA50
        空头排列：SMA5 < SMA10 < SMA20 < SMA50

        Returns:
            均线排列序列（使用shift(1)防止数据泄漏）
            正值表示多头排列强度，负值表示空头排列强度
        """
        sma5 = df['SMA5']
        sma10 = df['SMA10']
        sma20 = df['SMA20']
        sma50 = df['SMA50']

        # 计算多头排列强度（每个条件满足+1，不满足-1）
        bullish_score = 0
        bullish_score += (sma5 > sma10).astype(int) * 1
        bullish_score += (sma10 > sma20).astype(int) * 1
        bullish_score += (sma20 > sma50).astype(int) * 1

        # 计算空头排列强度
        bearish_score = 0
        bearish_score += (sma5 < sma10).astype(int) * 1
        bearish_score += (sma10 < sma20).astype(int) * 1
        bearish_score += (sma20 < sma50).astype(int) * 1

        # 综合得分（多头为正，空头为负）
        alignment = bullish_score - bearish_score

        return alignment


# ==================== 辅助函数 ====================

def validate_technical_indicators(df: pd.DataFrame) -> bool:
    """
    验证技术指标数据的有效性

    Args:
        df: 包含技术指标的数据框

    Returns:
        True 如果数据有效，False 否则
    """
    # 检查是否有无穷大值
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            if np.isinf(df[col]).any():
                logger.error(f"列 {col} 包含无穷大值")
                return False

    # 检查RSI是否在0-100范围内
    if 'RSI14' in df.columns:
        valid_rsi = df['RSI14'].dropna()
        if (valid_rsi < 0).any() or (valid_rsi > 100).any():
            logger.error("RSI超出有效范围")
            return False

    # 检查ADX是否在0-100范围内
    if 'ADX' in df.columns:
        valid_adx = df['ADX'].dropna()
        if (valid_adx < 0).any() or (valid_adx > 100).any():
            logger.error("ADX超出有效范围")
            return False

    # 检查布林带关系
    if all(col in df.columns for col in ['BB_Upper', 'BB_Middle', 'BB_Lower']):
        valid_bb = df[['BB_Upper', 'BB_Middle', 'BB_Lower']].dropna()
        if (valid_bb['BB_Upper'] < valid_bb['BB_Middle']).any():
            logger.error("布林带上轨应大于等于中轨")
            return False
        if (valid_bb['BB_Middle'] < valid_bb['BB_Lower']).any():
            logger.error("布林带中轨应大于等于下轨")
            return False

    return True


if __name__ == '__main__':
    # 测试代码
    print("技术指标引擎测试")

    # 创建测试数据
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=200)
    close_prices = []
    price = 1.0
    for i in range(200):
        change = np.random.normal(0.001, 0.01)
        price = price * (1 + change)
        close_prices.append(price)

    test_data = pd.DataFrame({
        'Date': dates,
        'Open': [p * (1 + np.random.uniform(-0.002, 0.002)) for p in close_prices],
        'High': [p * (1 + np.random.uniform(0, 0.005)) for p in close_prices],
        'Low': [p * (1 - np.random.uniform(0, 0.005)) for p in close_prices],
        'Close': close_prices,
        'Volume': np.random.randint(1000000, 5000000, 200)
    })

    # 计算指标
    analyzer = TechnicalAnalyzer()
    result = analyzer.compute_all_indicators(test_data)

    print(f"\n原始数据列数: {len(test_data.columns)}")
    print(f"生成后列数: {len(result.columns)}")
    print(f"新增指标数: {len(result.columns) - len(test_data.columns)}")

    # 显示指标列表
    original_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    indicator_columns = [col for col in result.columns if col not in original_columns]
    print(f"\n指标列表 ({len(indicator_columns)}个):")
    for i, col in enumerate(indicator_columns, 1):
        print(f"  {i}. {col}")

    # 验证数据
    is_valid = validate_technical_indicators(result)
    print(f"\n数据验证: {'通过' if is_valid else '失败'}")

    # 显示部分结果
    print("\n最后10天的部分指标:")
    display_columns = ['Date', 'Close', 'SMA5', 'SMA20', 'RSI14', 'MACD', 'ADX', 'ATR14']
    available_columns = [col for col in display_columns if col in result.columns]
    print(result[available_columns].tail(10).to_string())
