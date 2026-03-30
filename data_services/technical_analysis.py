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

        # ==================== 高级形态识别指标 ====================

        # 头肩顶/底识别
        head_shoulders = self.compute_head_shoulders(result)
        result['Head_Shoulders_Top'] = head_shoulders['Head_Shoulders_Top']
        result['Head_Shoulders_Bottom'] = head_shoulders['Head_Shoulders_Bottom']

        # 双顶/双底识别
        double_top_bottom = self.compute_double_top_bottom(result)
        result['Double_Top'] = double_top_bottom['Double_Top']
        result['Double_Bottom'] = double_top_bottom['Double_Bottom']

        # 三角形整理
        triangle_pattern = self.compute_triangle_pattern(result)
        result['Triangle_Sym'] = triangle_pattern['Triangle_Sym']
        result['Triangle_Asc'] = triangle_pattern['Triangle_Asc']
        result['Triangle_Desc'] = triangle_pattern['Triangle_Desc']

        # ==================== 支撑阻力位识别指标 ====================

        # 历史高低点
        support_resistance = self.compute_support_resistance_levels(result)
        result['Support_Level'] = support_resistance['Support_Level']
        result['Resistance_Level'] = support_resistance['Resistance_Level']
        result['Price_vs_Support'] = support_resistance['Price_vs_Support']
        result['Price_vs_Resistance'] = support_resistance['Price_vs_Resistance']

        # 前期密集成交区
        congestion = self.compute_congestion_zone(result)
        result['Congestion_Zone'] = congestion['Congestion_Zone']
        result['Price_in_Congestion'] = congestion['Price_in_Congestion']

        # ==================== 成交量分析指标 ====================

        # 成交量分布
        if 'Volume' in result.columns:
            volume_dist = self.compute_volume_distribution(result)
            result['Volume_Distribution'] = volume_dist['Volume_Distribution']
            result['Volume_Profile'] = volume_dist['Volume_Profile']
        else:
            result['Volume_Distribution'] = np.nan
            result['Volume_Profile'] = np.nan

        # OBV背离
        if 'OBV' in result.columns:
            result['OBV_Divergence'] = self.compute_obv_divergence(result)
        else:
            result['OBV_Divergence'] = np.nan

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

    # ==================== 高级形态识别实现 ====================

    def compute_head_shoulders(self, df: pd.DataFrame,
                               lookback: int = 60) -> pd.DataFrame:
        """
        识别头肩顶/底形态

        头肩顶：三峰形态，中间峰（头）最高，两侧峰（肩）较低
        头肩底：三谷形态，中间谷（头）最低，两侧谷（肩）较高

        Args:
            df: 数据框（需包含 High, Low, Close）
            lookback: 回看周期

        Returns:
            DataFrame with columns: Head_Shoulders_Top, Head_Shoulders_Bottom
            （使用shift(1)防止数据泄漏）
            值为0-1之间的概率，表示形态的置信度
        """
        high = df['High'].shift(1)
        low = df['Low'].shift(1)
        close = df['Close'].shift(1)

        # 初始化结果
        hs_top = pd.Series(0.0, index=df.index)
        hs_bottom = pd.Series(0.0, index=df.index)

        # 滚动窗口检测
        for i in range(lookback, len(df)):
            window_high = high.iloc[i-lookback:i]
            window_low = low.iloc[i-lookback:i]
            window_close = close.iloc[i-lookback:i]

            # 寻找峰值（头肩顶）
            peaks = []
            for j in range(5, len(window_high) - 5):
                if window_high.iloc[j] == window_high.iloc[j-5:j+6].max():
                    peaks.append(j)

            # 至少需要3个峰值
            if len(peaks) >= 3:
                # 取最高的3个峰值
                peak_heights = [(p, window_high.iloc[p]) for p in peaks]
                peak_heights.sort(key=lambda x: x[1], reverse=True)
                top_3_peaks = [p[0] for p in peak_heights[:3]]
                top_3_peaks.sort()

                # 检查是否为头肩顶：中间最高，两侧较低
                if (len(top_3_peaks) == 3 and
                    top_3_peaks[1] - top_3_peaks[0] >= 5 and
                    top_3_peaks[2] - top_3_peaks[1] >= 5):

                    head = window_high.iloc[top_3_peaks[1]]
                    left_shoulder = window_high.iloc[top_3_peaks[0]]
                    right_shoulder = window_high.iloc[top_3_peaks[2]]

                    # 颈线
                    neckline = min(left_shoulder, right_shoulder)

                    # 头比肩高至少5%
                    if head > left_shoulder * 1.05 and head > right_shoulder * 1.05:
                        # 计算置信度（基于对称性和价格差）
                        symmetry = 1 - abs(left_shoulder - right_shoulder) / ((left_shoulder + right_shoulder) / 2)
                        confidence = min(1.0, symmetry)
                        hs_top.iloc[i] = confidence

            # 寻找谷值（头肩底）
            valleys = []
            for j in range(5, len(window_low) - 5):
                if window_low.iloc[j] == window_low.iloc[j-5:j+6].min():
                    valleys.append(j)

            # 至少需要3个谷值
            if len(valleys) >= 3:
                # 取最低的3个谷值
                valley_depths = [(v, window_low.iloc[v]) for v in valleys]
                valley_depths.sort(key=lambda x: x[1])
                top_3_valleys = [v[0] for v in valley_depths[:3]]
                top_3_valleys.sort()

                # 检查是否为头肩底：中间最低，两侧较高
                if (len(top_3_valleys) == 3 and
                    top_3_valleys[1] - top_3_valleys[0] >= 5 and
                    top_3_valleys[2] - top_3_valleys[1] >= 5):

                    head = window_low.iloc[top_3_valleys[1]]
                    left_shoulder = window_low.iloc[top_3_valleys[0]]
                    right_shoulder = window_low.iloc[top_3_valleys[2]]

                    # 颈线
                    neckline = max(left_shoulder, right_shoulder)

                    # 头比肩低至少5%
                    if head < left_shoulder * 0.95 and head < right_shoulder * 0.95:
                        # 计算置信度
                        symmetry = 1 - abs(left_shoulder - right_shoulder) / ((left_shoulder + right_shoulder) / 2)
                        confidence = min(1.0, symmetry)
                        hs_bottom.iloc[i] = confidence

        return pd.DataFrame({
            'Head_Shoulders_Top': hs_top,
            'Head_Shoulders_Bottom': hs_bottom
        })

    def compute_double_top_bottom(self, df: pd.DataFrame,
                                  lookback: int = 40) -> pd.DataFrame:
        """
        识别双顶/双底形态

        双顶：两个相似的高点，中间有回调
        双底：两个相似的低点，中间有反弹

        Args:
            df: 数据框（需包含 High, Low, Close）
            lookback: 回看周期

        Returns:
            DataFrame with columns: Double_Top, Double_Bottom
            （使用shift(1)防止数据泄漏）
            值为0-1之间的概率，表示形态的置信度
        """
        high = df['High'].shift(1)
        low = df['Low'].shift(1)
        close = df['Close'].shift(1)

        # 初始化结果
        double_top = pd.Series(0.0, index=df.index)
        double_bottom = pd.Series(0.0, index=df.index)

        # 滚动窗口检测
        for i in range(lookback, len(df)):
            window_high = high.iloc[i-lookback:i]
            window_low = low.iloc[i-lookback:i]
            window_close = close.iloc[i-lookback:i]

            # 寻找峰值（双顶）
            peaks = []
            for j in range(5, len(window_high) - 5):
                if window_high.iloc[j] == window_high.iloc[j-5:j+6].max():
                    peaks.append(j)

            # 检查双顶
            if len(peaks) >= 2:
                peak_heights = [(p, window_high.iloc[p]) for p in peaks]
                peak_heights.sort(key=lambda x: x[1], reverse=True)

                # 取最高的两个峰值
                top_2_peaks = peak_heights[:2]
                top_2_peaks.sort(key=lambda x: x[0])

                peak1_idx, peak1_price = top_2_peaks[0]
                peak2_idx, peak2_price = top_2_peaks[1]

                # 两个峰之间至少间隔5天
                if peak2_idx - peak1_idx >= 5:
                    # 检查价格相似性（误差在3%以内）
                    price_diff = abs(peak1_price - peak2_price) / ((peak1_price + peak2_price) / 2)
                    if price_diff < 0.03:
                        # 检查中间有回调（至少3%）
                        valley_idx = window_close.iloc[peak1_idx:peak2_idx].idxmin()
                        valley_price = window_close.loc[valley_idx]
                        avg_peak_price = (peak1_price + peak2_price) / 2

                        if valley_price < avg_peak_price * 0.97:
                            confidence = 1 - price_diff / 0.03
                            double_top.iloc[i] = min(1.0, confidence)

            # 寻找谷值（双底）
            valleys = []
            for j in range(5, len(window_low) - 5):
                if window_low.iloc[j] == window_low.iloc[j-5:j+6].min():
                    valleys.append(j)

            # 检查双底
            if len(valleys) >= 2:
                valley_depths = [(v, window_low.iloc[v]) for v in valleys]
                valley_depths.sort(key=lambda x: x[1])

                # 取最低的两个谷值
                bottom_2_valleys = valley_depths[:2]
                bottom_2_valleys.sort(key=lambda x: x[0])

                valley1_idx, valley1_price = bottom_2_valleys[0]
                valley2_idx, valley2_price = bottom_2_valleys[1]

                # 两个谷之间至少间隔5天
                if valley2_idx - valley1_idx >= 5:
                    # 检查价格相似性（误差在3%以内）
                    price_diff = abs(valley1_price - valley2_price) / ((valley1_price + valley2_price) / 2)
                    if price_diff < 0.03:
                        # 检查中间有反弹（至少3%）
                        peak_idx = window_close.iloc[valley1_idx:valley2_idx].idxmax()
                        peak_price = window_close.loc[peak_idx]
                        avg_valley_price = (valley1_price + valley2_price) / 2

                        if peak_price > avg_valley_price * 1.03:
                            confidence = 1 - price_diff / 0.03
                            double_bottom.iloc[i] = min(1.0, confidence)

        return pd.DataFrame({
            'Double_Top': double_top,
            'Double_Bottom': double_bottom
        })

    def compute_triangle_pattern(self, df: pd.DataFrame,
                                  lookback: int = 30) -> pd.DataFrame:
        """
        识别三角形整理形态

        对称三角形：高点下降，低点上升
        上升三角形：高点水平，低点上升
        下降三角形：高点下降，低点水平

        Args:
            df: 数据框（需包含 High, Low, Close）
            lookback: 回看周期

        Returns:
            DataFrame with columns: Triangle_Sym, Triangle_Asc, Triangle_Desc
            （使用shift(1)防止数据泄漏）
            值为0-1之间的概率，表示形态的置信度
        """
        high = df['High'].shift(1)
        low = df['Low'].shift(1)
        close = df['Close'].shift(1)

        # 初始化结果
        triangle_sym = pd.Series(0.0, index=df.index)
        triangle_asc = pd.Series(0.0, index=df.index)
        triangle_desc = pd.Series(0.0, index=df.index)

        # 滚动窗口检测
        for i in range(lookback, len(df)):
            window_high = high.iloc[i-lookback:i]
            window_low = low.iloc[i-lookback:i]
            window_close = close.iloc[i-lookback:i]

            # 提取局部高点和低点
            local_highs = []
            local_lows = []

            for j in range(5, len(window_high) - 5):
                if window_high.iloc[j] == window_high.iloc[j-5:j+6].max():
                    local_highs.append((j, window_high.iloc[j]))
                if window_low.iloc[j] == window_low.iloc[j-5:j+6].min():
                    local_lows.append((j, window_low.iloc[j]))

            # 至少需要3个高点和3个低点
            if len(local_highs) >= 3 and len(local_lows) >= 3:
                # 计算高点趋势（线性回归斜率）
                high_indices = [h[0] for h in local_highs[-5:]]
                high_prices = [h[1] for h in local_highs[-5:]]

                if len(high_indices) >= 3:
                    high_slope = np.polyfit(high_indices, high_prices, 1)[0]

                    # 计算低点趋势
                    low_indices = [l[0] for l in local_lows[-5:]]
                    low_prices = [l[1] for l in local_lows[-5:]]

                    if len(low_indices) >= 3:
                        low_slope = np.polyfit(low_indices, low_prices, 1)[0]

                        # 标准化斜率
                        avg_price = np.mean(window_close)
                        high_slope_norm = high_slope / avg_price * 100
                        low_slope_norm = low_slope / avg_price * 100

                        # 对称三角形：高点下降（负斜率），低点上升（正斜率）
                        if high_slope_norm < -0.01 and low_slope_norm > 0.01:
                            confidence = min(1.0, abs(high_slope_norm) + low_slope_norm)
                            triangle_sym.iloc[i] = confidence

                        # 上升三角形：高点水平（斜率接近0），低点上升（正斜率）
                        elif abs(high_slope_norm) < 0.01 and low_slope_norm > 0.02:
                            confidence = min(1.0, low_slope_norm * 20)
                            triangle_asc.iloc[i] = confidence

                        # 下降三角形：高点下降（负斜率），低点水平（斜率接近0）
                        elif high_slope_norm < -0.02 and abs(low_slope_norm) < 0.01:
                            confidence = min(1.0, abs(high_slope_norm) * 20)
                            triangle_desc.iloc[i] = confidence

        return pd.DataFrame({
            'Triangle_Sym': triangle_sym,
            'Triangle_Asc': triangle_asc,
            'Triangle_Desc': triangle_desc
        })

    # ==================== 支撑阻力位识别实现 ====================

    def compute_support_resistance_levels(self, df: pd.DataFrame,
                                          lookback: int = 60) -> pd.DataFrame:
        """
        识别历史高低点（支撑位和阻力位）

        支撑位：历史低点聚集区域
        阻力位：历史高点聚集区域

        Args:
            df: 数据框（需包含 High, Low, Close）
            lookback: 回看周期

        Returns:
            DataFrame with columns: Support_Level, Resistance_Level,
                                   Price_vs_Support, Price_vs_Resistance
            （使用shift(1)防止数据泄漏）
        """
        high = df['High'].shift(1)
        low = df['Low'].shift(1)
        close = df['Close'].shift(1)

        # 初始化结果
        support_level = pd.Series(np.nan, index=df.index)
        resistance_level = pd.Series(np.nan, index=df.index)
        price_vs_support = pd.Series(np.nan, index=df.index)
        price_vs_resistance = pd.Series(np.nan, index=df.index)

        # 滚动窗口检测
        for i in range(lookback, len(df)):
            window_high = high.iloc[i-lookback:i]
            window_low = low.iloc[i-lookback:i]
            window_close = close.iloc[i-lookback:i]

            # 找出所有局部低点
            local_lows = []
            for j in range(3, len(window_low) - 3):
                if window_low.iloc[j] == window_low.iloc[j-3:j+4].min():
                    local_lows.append(window_low.iloc[j])

            # 找出所有局部高点
            local_highs = []
            for j in range(3, len(window_high) - 3):
                if window_high.iloc[j] == window_high.iloc[j-3:j+4].max():
                    local_highs.append(window_high.iloc[j])

            # 计算支撑位（低点聚集区域）
            if len(local_lows) >= 3:
                # 对低点进行聚类
                low_array = np.array(local_lows)
                low_min, low_max = low_array.min(), low_array.max()
                low_range = low_max - low_min

                if low_range > 0:
                    # 使用直方图找出聚集区
                    hist, bins = np.histogram(low_array, bins=10)
                    max_bin = np.argmax(hist)

                    # 支撑位为聚集区的中心
                    support_idx = i
                    support_level.iloc[support_idx] = (bins[max_bin] + bins[max_bin + 1]) / 2

                    # 计算当前价格相对于支撑位的距离
                    current_price = close.iloc[i]
                    distance = (current_price - support_level.iloc[support_idx]) / current_price
                    price_vs_support.iloc[support_idx] = distance

            # 计算阻力位（高点聚集区域）
            if len(local_highs) >= 3:
                # 对高点进行聚类
                high_array = np.array(local_highs)
                high_min, high_max = high_array.min(), high_array.max()
                high_range = high_max - high_min

                if high_range > 0:
                    # 使用直方图找出聚集区
                    hist, bins = np.histogram(high_array, bins=10)
                    max_bin = np.argmax(hist)

                    # 阻力位为聚集区的中心
                    resistance_idx = i
                    resistance_level.iloc[resistance_idx] = (bins[max_bin] + bins[max_bin + 1]) / 2

                    # 计算当前价格相对于阻力位的距离
                    current_price = close.iloc[i]
                    distance = (current_price - resistance_level.iloc[resistance_idx]) / current_price
                    price_vs_resistance.iloc[resistance_idx] = distance

        return pd.DataFrame({
            'Support_Level': support_level,
            'Resistance_Level': resistance_level,
            'Price_vs_Support': price_vs_support,
            'Price_vs_Resistance': price_vs_resistance
        })

    def compute_congestion_zone(self, df: pd.DataFrame,
                                lookback: int = 40) -> pd.DataFrame:
        """
        识别前期密集成交区

        密集成交区：价格在一定范围内波动，成交量较大

        Args:
            df: 数据框（需包含 Close, High, Low, Volume）
            lookback: 回看周期

        Returns:
            DataFrame with columns: Congestion_Zone, Price_in_Congestion
            （使用shift(1)防止数据泄漏）
            Congestion_Zone: 密集成交区的价格范围（高-低）
            Price_in_Congestion: 当前价格是否在密集成交区内（0-1）
        """
        close = df['Close'].shift(1)
        high = df['High'].shift(1)
        low = df['Low'].shift(1)
        volume = df.get('Volume', pd.Series([1] * len(df))).shift(1)

        # 初始化结果
        congestion_zone = pd.Series(np.nan, index=df.index)
        price_in_congestion = pd.Series(0.0, index=df.index)

        # 滚动窗口检测
        for i in range(lookback, len(df)):
            window_close = close.iloc[i-lookback:i]
            window_high = high.iloc[i-lookback:i]
            window_low = low.iloc[i-lookback:i]
            window_volume = volume.iloc[i-lookback:i]

            # 计算价格波动范围
            price_range = window_high.max() - window_low.min()
            avg_price = window_close.mean()

            # 计算波动率
            volatility = price_range / avg_price

            # 如果波动率小于阈值（价格稳定），则可能存在密集成交区
            if volatility < 0.05:  # 5%的波动率阈值
                # 计算成交量加权平均价格
                avg_volume = window_volume.mean()
                volume_weight = window_volume / avg_volume

                # 密集成交区的高点和低点
                congestion_high = window_high.max()
                congestion_low = window_low.min()

                # 记录密集成交区
                congestion_idx = i
                congestion_zone.iloc[congestion_idx] = congestion_high - congestion_low

                # 检查当前价格是否在密集成交区内
                current_price = close.iloc[i]
                if congestion_low <= current_price <= congestion_high:
                    # 计算价格在密集成交区中的位置（0-1）
                    position = (current_price - congestion_low) / (congestion_high - congestion_low)
                    price_in_congestion.iloc[congestion_idx] = position

        return pd.DataFrame({
            'Congestion_Zone': congestion_zone,
            'Price_in_Congestion': price_in_congestion
        })

    # ==================== 成交量分析实现 ====================

    def compute_volume_distribution(self, df: pd.DataFrame,
                                    lookback: int = 20) -> pd.DataFrame:
        """
        计算成交量分布

        分析成交量在不同价格水平上的分布情况

        Args:
            df: 数据框（需包含 Close, Volume）
            lookback: 回看周期

        Returns:
            DataFrame with columns: Volume_Distribution, Volume_Profile
            （使用shift(1)防止数据泄漏）
            Volume_Distribution: 成交量分布的均匀程度（0-1，越高越均匀）
            Volume_Profile: 成交量趋势（正=增加，负=减少）
        """
        close = df['Close'].shift(1)
        volume = df['Volume'].shift(1)

        # 初始化结果
        volume_distribution = pd.Series(0.0, index=df.index)
        volume_profile = pd.Series(0.0, index=df.index)

        # 滚动窗口计算
        for i in range(lookback, len(df)):
            window_close = close.iloc[i-lookback:i]
            window_volume = volume.iloc[i-lookback:i]

            # 计算成交量分布（使用价格分段）
            price_min = window_close.min()
            price_max = window_close.max()
            price_range = price_max - price_min

            if price_range > 0:
                # 将价格分成5个区间
                bins = np.linspace(price_min, price_max, 6)
                volume_by_price = []

                for j in range(5):
                    # 找出每个价格区间的成交量
                    in_bin = (window_close >= bins[j]) & (window_close < bins[j + 1])
                    bin_volume = window_volume[in_bin].sum()
                    volume_by_price.append(bin_volume)

                # 计算分布的均匀程度（标准差越小越均匀）
                if sum(volume_by_price) > 0:
                    volume_array = np.array(volume_by_price)
                    volume_std = volume_array.std()
                    volume_mean = volume_array.mean()

                    if volume_mean > 0:
                        distribution_score = 1 - (volume_std / volume_mean)
                        volume_distribution.iloc[i] = max(0.0, min(1.0, distribution_score))

            # 计算成交量趋势（线性回归斜率）
            if len(window_volume) >= 3:
                x = np.arange(len(window_volume))
                y = window_volume.values

                # 线性回归
                slope = np.polyfit(x, y, 1)[0]

                # 标准化斜率
                avg_volume = window_volume.mean()
                if avg_volume > 0:
                    profile_score = slope / avg_volume * lookback
                    volume_profile.iloc[i] = profile_score

        return pd.DataFrame({
            'Volume_Distribution': volume_distribution,
            'Volume_Profile': volume_profile
        })

    def compute_obv_divergence(self, df: pd.DataFrame,
                               lookback: int = 14) -> pd.Series:
        """
        计算 OBV 背离

        价格创新高但 OBV 未创新高 = 看跌背离（潜在顶部）
        价格创新低但 OBV 未创新低 = 看涨背离（潜在底部）

        Args:
            df: 数据框（需包含 Close, OBV）
            lookback: 回看周期

        Returns:
            OBV背离序列（使用shift(1)防止数据泄漏）
            正值 = 看涨背离，负值 = 看跌背离，0 = 无背离
        """
        close = df['Close'].shift(1)
        obv = df['OBV'].shift(1)

        # 初始化结果
        divergence = pd.Series(0.0, index=df.index)

        # 滚动窗口检测
        for i in range(lookback, len(df)):
            window_close = close.iloc[i-lookback:i]
            window_obv = obv.iloc[i-lookback:i]

            # 寻找价格新高
            price_highs = []
            for j in range(3, len(window_close) - 3):
                if window_close.iloc[j] == window_close.iloc[j-3:j+4].max():
                    price_highs.append(j)

            # 寻找价格新低
            price_lows = []
            for j in range(3, len(window_close) - 3):
                if window_close.iloc[j] == window_close.iloc[j-3:j+4].min():
                    price_lows.append(j)

            # 检测看跌背离（价格新高但 OBV 未新高）
            if len(price_highs) >= 2:
                recent_high = price_highs[-1]
                previous_high = price_highs[-2]

                if (window_close.iloc[recent_high] > window_close.iloc[previous_high] and
                    window_obv.iloc[recent_high] < window_obv.iloc[previous_high]):
                    # 看跌背离，负值
                    divergence.iloc[i] = -1.0

            # 检测看涨背离（价格新低但 OBV 未新低）
            if len(price_lows) >= 2:
                recent_low = price_lows[-1]
                previous_low = price_lows[-2]

                if (window_close.iloc[recent_low] < window_close.iloc[previous_low] and
                    window_obv.iloc[recent_low] > window_obv.iloc[previous_low]):
                    # 看涨背离，正值
                    divergence.iloc[i] = 1.0

        return divergence


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
