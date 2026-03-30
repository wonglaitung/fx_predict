"""
特征工程模块

为机器学习模型创建所有必需的特征。

重要：
1. 所有特征计算必须使用 .shift(1) 防止数据泄漏
2. create_target 方法仅用于训练阶段，预测阶段不可使用！
"""

import pandas as pd
import numpy as np
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """特征工程器"""

    def __init__(self):
        """初始化特征工程器"""
        self.logger = logger

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        创建特征集

        特征类别：
        1. 价格衍生特征：Close_change_1d, Close_change_5d, Close_change_20d,
                         Return_1d, Return_5d, Return_20d
        2. 偏离率特征：Bias_5, Bias_10, Bias_20
        3. 波动率特征：Volatility_5d, Volatility_20d
        4. 滞后特征：Close_lag_1, Close_lag_5, Close_lag_20
        5. 趋势斜率特征：Trend_Slope_20
        6. 市场环境特征：MA_Alignment
        7. 交叉特征：SMA5_cross_SMA20（均线交叉信号）, Price_vs_Bollinger（价格与布林带位置）
        8. 高级形态识别特征（7个）：
           - Head_Shoulders_Top: 头肩顶识别（0-1置信度）
           - Head_Shoulders_Bottom: 头肩底识别（0-1置信度）
           - Double_Top: 双顶识别（0-1置信度）
           - Double_Bottom: 双底识别（0-1置信度）
           - Triangle_Sym: 对称三角形识别（0-1置信度）
           - Triangle_Asc: 上升三角形识别（0-1置信度）
           - Triangle_Desc: 下降三角形识别（0-1置信度）
        9. 支撑阻力位识别特征（6个）：
           - Support_Level: 支撑位价格
           - Resistance_Level: 阻力位价格
           - Price_vs_Support: 当前价格相对于支撑位的距离（百分比）
           - Price_vs_Resistance: 当前价格相对于阻力位的距离（百分比）
           - Congestion_Zone: 密集成交区的价格范围
           - Price_in_Congestion: 当前价格是否在密集成交区内（0-1）
        10. 成交量分析特征（3个）：
            - Volume_Distribution: 成交量分布的均匀程度（0-1）
            - Volume_Profile: 成交量趋势（正=增加，负=减少）
            - OBV_Divergence: OBV背离（正值=看涨，负值=看跌，0=无背离）

        Args:
            df: 包含技术指标的数据（至少需要 Close 列）

        Returns:
            特征 DataFrame（包含原始数据和新创建的特征）

        Notes:
            - 所有特征必须使用滞后数据（.shift(1)），防止数据泄漏
            - 返回的特征 DataFrame 不包含目标变量
            - 高级形态识别、支撑阻力位识别和成交量分析特征由 technical_analysis.py 计算生成
        """
        features = df.copy()

        # ==================== 1. 价格衍生特征 ====================

        # 涨跌幅（价格变化）
        features['Close_change_1d'] = self._compute_price_change(features, periods=1).shift(1)
        features['Close_change_5d'] = self._compute_price_change(features, periods=5).shift(1)
        features['Close_change_20d'] = self._compute_price_change(features, periods=20).shift(1)

        # 收益率（百分比变化）
        features['Return_1d'] = self._compute_return(features, periods=1).shift(1)
        features['Return_5d'] = self._compute_return(features, periods=5).shift(1)
        features['Return_20d'] = self._compute_return(features, periods=20).shift(1)

        # ==================== 2. 偏离率特征 ====================

        # 偏离率：价格相对于移动平均线的偏离程度
        if 'SMA5' in features.columns:
            features['Bias_5'] = self._compute_bias(features, period=5, ma_col='SMA5').shift(1)
        if 'SMA10' in features.columns:
            features['Bias_10'] = self._compute_bias(features, period=10, ma_col='SMA10').shift(1)
        if 'SMA20' in features.columns:
            features['Bias_20'] = self._compute_bias(features, period=20, ma_col='SMA20').shift(1)

        # ==================== 3. 波动率特征 ====================

        # 波动率：标准差/均价
        features['Volatility_5d'] = self._compute_volatility(features, period=5).shift(1)
        features['Volatility_20d'] = self._compute_volatility(features, period=20).shift(1)

        # ==================== 4. 滞后特征 ====================

        # 滞后价格
        features['Close_lag_1'] = features['Close'].shift(1)
        features['Close_lag_5'] = features['Close'].shift(5)
        features['Close_lag_20'] = features['Close'].shift(20)

        # ==================== 5. 趋势斜率特征 ====================

        # 趋势斜率：线性回归斜率
        features['Trend_Slope_20'] = self._compute_trend_slope(features, period=20).shift(1)

        # ==================== 6. 市场环境特征 ====================

        # 均线排列：多头/空头排列强度
        if all(col in features.columns for col in ['SMA5', 'SMA10', 'SMA20', 'SMA50']):
            features['MA_Alignment'] = self._compute_ma_alignment(features).shift(1)

        # ==================== 7. 交叉特征 ====================

        # SMA5与SMA20交叉信号（金叉/死叉）
        if all(col in features.columns for col in ['SMA5', 'SMA20']):
            features['SMA5_cross_SMA20'] = self._compute_sma_cross_signal(features).shift(1)

        # 价格相对于布林带的位置
        if all(col in features.columns for col in ['Close', 'BB_Upper', 'BB_Middle', 'BB_Lower']):
            features['Price_vs_Bollinger'] = self._compute_bollinger_position(features).shift(1)

        self.logger.info(f"特征创建完成，原始列数: {len(df.columns)}, 特征列数: {len(features.columns)}")

        return features

    def create_target(self, df: pd.DataFrame, horizon: int = 20) -> pd.Series:
        """
        创建目标变量：未来 horizon 天的涨跌

        Args:
            df: 原始数据（必须包含 Close 列）
            horizon: 预测周期（天）

        Returns:
            目标序列（1=上涨, 0=下跌）

        Notes:
            - 使用 shift(-horizon) 获取未来数据
            - **警告**：此方法仅用于训练阶段，预测阶段不可使用！
            - 预测时目标变量无法获取，应由模型预测生成
            - 计算方式：比较当前价格和 horizon 天后的价格
        """
        # 计算未来价格
        future_price = df['Close'].shift(-horizon)

        # 初始化为 NaN
        target = pd.Series(np.nan, index=df.index, dtype=float)

        # 计算目标：未来价格 > 当前价格 则为 1（上涨），否则为 0（下跌）
        valid_mask = future_price.notna()
        target[valid_mask] = (future_price[valid_mask] > df['Close'][valid_mask]).astype(float)

        # 由于使用了 shift(-horizon)，最后 horizon 个值会变成 NaN
        # （因为没有足够的数据来计算未来 horizon 天的价格）
        self.logger.info(f"目标变量创建完成，预测周期: {horizon} 天")

        return target

    # ==================== 私有辅助方法 ====================

    def _compute_price_change(self, df: pd.DataFrame, periods: int = 1) -> pd.Series:
        """
        计算价格变化（绝对值）

        Args:
            df: 数据框
            periods: 周期

        Returns:
            价格变化序列
        """
        change = df['Close'].diff(periods=periods)
        return change

    def _compute_return(self, df: pd.DataFrame, periods: int = 1) -> pd.Series:
        """
        计算收益率（百分比变化）

        Args:
            df: 数据框
            periods: 周期

        Returns:
            收益率序列
        """
        return df['Close'].pct_change(periods=periods)

    def _compute_bias(self, df: pd.DataFrame, period: int, ma_col: str) -> pd.Series:
        """
        计算偏离率（乖离率）

        偏离率 = (当前价格 - 移动平均线) / 移动平均线

        Args:
            df: 数据框
            period: 周期
            ma_col: 移动平均线列名

        Returns:
            偏离率序列
        """
        if ma_col not in df.columns:
            # 如果没有预计算的移动平均线，则计算
            ma = df['Close'].rolling(window=period).mean()
        else:
            ma = df[ma_col]

        bias = (df['Close'] - ma) / ma
        return bias

    def _compute_volatility(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        计算波动率（标准差/均价）

        Args:
            df: 数据框
            period: 周期

        Returns:
            波动率序列
        """
        std = df['Close'].rolling(window=period).std()
        mean = df['Close'].rolling(window=period).mean()

        volatility = std / mean
        return volatility

    def _compute_trend_slope(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        计算趋势斜率（线性回归斜率）

        Args:
            df: 数据框
            period: 周期

        Returns:
            趋势斜率序列
        """
        def slope_func(x):
            """计算序列的线性回归斜率"""
            if len(x) < 2:
                return np.nan

            x_values = np.arange(len(x))
            y_values = x.values

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

        # 使用滚动窗口计算斜率
        slope = df['Close'].rolling(window=period).apply(slope_func, raw=False)
        return slope

    def _compute_ma_alignment(self, df: pd.DataFrame) -> pd.Series:
        """
        计算均线排列强度

        多头排列：SMA5 > SMA10 > SMA20 > SMA50
        空头排列：SMA5 < SMA10 < SMA20 < SMA50

        Returns:
            均线排列序列（正值表示多头排列强度，负值表示空头排列强度）
        """
        sma5 = df['SMA5']
        sma10 = df['SMA10']
        sma20 = df['SMA20']
        sma50 = df['SMA50']

        # 计算多头排列强度（每个条件满足+1，不满足-1）
        bullish_score = pd.Series(0, index=df.index)
        bullish_score += (sma5 > sma10).astype(int)
        bullish_score += (sma10 > sma20).astype(int)
        bullish_score += (sma20 > sma50).astype(int)

        # 计算空头排列强度
        bearish_score = pd.Series(0, index=df.index)
        bearish_score += (sma5 < sma10).astype(int)
        bearish_score += (sma10 < sma20).astype(int)
        bearish_score += (sma20 < sma50).astype(int)

        # 综合得分（多头为正，空头为负）
        alignment = bullish_score - bearish_score

        return alignment

    def _compute_sma_cross_signal(self, df: pd.DataFrame) -> pd.Series:
        """
        计算 SMA5 与 SMA20 的交叉信号

        金叉（买入信号）：SMA5 上穿 SMA20
        死叉（卖出信号）：SMA5 下穿 SMA20

        Returns:
            交叉信号序列（1=金叉，-1=死叉，0=无交叉）
        """
        sma5 = df['SMA5']
        sma20 = df['SMA20']

        # 计算交叉信号
        # 使用 diff() 检测变化，然后判断是否交叉
        cross_signal = pd.Series(0, index=df.index)

        # 检测金叉（SMA5 从下方穿过 SMA20）
        golden_cross = (sma5 > sma20) & (sma5.shift(1) <= sma20.shift(1))

        # 检测死叉（SMA5 从上方穿过 SMA20）
        death_cross = (sma5 < sma20) & (sma5.shift(1) >= sma20.shift(1))

        cross_signal[golden_cross] = 1
        cross_signal[death_cross] = -1

        return cross_signal

    def _compute_bollinger_position(self, df: pd.DataFrame) -> pd.Series:
        """
        计算价格相对于布林带的位置

        返回值范围：
        - > 1：价格在上轨之上（超买）
        - 0.5 - 1：价格在中轨和上轨之间
        - -0.5 - 0.5：价格在中轨附近
        - -1 - -0.5：价格在下轨和中轨之间
        - < -1：价格在下轨之下（超卖）

        Returns:
            价格位置序列（标准化值）
        """
        close = df['Close']
        bb_upper = df['BB_Upper']
        bb_lower = df['BB_Lower']
        bb_middle = df['BB_Middle']

        # 计算布林带宽度
        bb_width = bb_upper - bb_lower

        # 计算价格位置（标准化到 -1 到 1 之间）
        # 位置 = (价格 - 中轨) / (上轨 - 下轨) * 2
        position = (close - bb_middle) / bb_width * 2

        return position


# ==================== 辅助函数 ====================

def validate_features(features: pd.DataFrame) -> bool:
    """
    验证特征数据的有效性

    Args:
        features: 包含特征的数据框

    Returns:
        True 如果数据有效，False 否则
    """
    # 检查是否有无穷大值
    for col in features.columns:
        if features[col].dtype in ['float64', 'int64']:
            if np.isinf(features[col]).any():
                logger.error(f"列 {col} 包含无穷大值")
                return False

    # 检查波动率特征是否为正数
    volatility_cols = [col for col in features.columns if 'Volatility' in col]
    for col in volatility_cols:
        valid_vol = features[col].dropna()
        if (valid_vol < 0).any():
            logger.error(f"波动率特征 {col} 包含负值")
            return False

    # 检查收益率特征是否在合理范围内（-100% 到 +100%）
    return_cols = [col for col in features.columns if 'Return' in col]
    for col in return_cols:
        valid_return = features[col].dropna()
        if (valid_return.abs() > 1).any():
            logger.warning(f"收益率特征 {col} 包含超过100%的变化")

    return True


if __name__ == '__main__':
    # 测试代码
    print("特征工程模块测试")

    # 创建测试数据
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=100)

    close_prices = []
    price = 1.0
    for i in range(100):
        change = np.random.normal(0.001, 0.01)
        price = price * (1 + change)
        close_prices.append(price)

    test_data = pd.DataFrame({
        'Date': dates,
        'Close': close_prices,
        'Open': [p * (1 + np.random.uniform(-0.002, 0.002)) for p in close_prices],
        'High': [p * (1 + np.random.uniform(0, 0.005)) for p in close_prices],
        'Low': [p * (1 - np.random.uniform(0, 0.005)) for p in close_prices],
        'Volume': np.random.randint(1000000, 5000000, 100),
        'SMA5': pd.Series(close_prices).rolling(5).mean(),
        'SMA10': pd.Series(close_prices).rolling(10).mean(),
        'SMA20': pd.Series(close_prices).rolling(20).mean(),
        'SMA50': pd.Series(close_prices).rolling(50).mean(),
        'SMA120': pd.Series(close_prices).rolling(120).mean()
    })

    # 创建特征
    engineer = FeatureEngineer()
    features = engineer.create_features(test_data)

    print(f"\n原始数据列数: {len(test_data.columns)}")
    print(f"特征数据列数: {len(features.columns)}")
    print(f"新增特征数: {len(features.columns) - len(test_data.columns)}")

    # 显示特征列表
    original_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    feature_columns = [col for col in features.columns if col not in original_columns]
    print(f"\n特征列表 ({len(feature_columns)}个):")
    for i, col in enumerate(feature_columns, 1):
        print(f"  {i}. {col}")

    # 创建目标变量
    target = engineer.create_target(test_data, horizon=20)
    print(f"\n目标变量创建完成")
    print(f"目标变量长度: {len(target)}")
    print(f"有效目标数: {target.notna().sum()}")
    print(f"上涨天数: {(target == 1).sum()}")
    print(f"下跌天数: {(target == 0).sum()}")

    # 验证特征
    is_valid = validate_features(features)
    print(f"\n特征验证: {'通过' if is_valid else '失败'}")

    # 显示部分结果
    print("\n最后10天的部分特征:")
    display_columns = ['Date', 'Close', 'Close_change_1d', 'Return_5d',
                      'Bias_5', 'Volatility_20d', 'Trend_Slope_20']
    available_columns = [col for col in display_columns if col in features.columns]
    print(features[available_columns].tail(10).to_string())
