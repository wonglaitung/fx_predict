import pandas as pd
import logging
from typing import Dict, Any

from data_services.technical_analysis import TechnicalAnalyzer
from ml_services.fx_trading_model import FXTradingModel
import json
import time
from llm_services.qwen_engine import chat_with_llm

import logging

logger = logging.getLogger(__name__)


class ComprehensiveAnalyzer:
    """综合分析器"""

    def __init__(self):
        self.logger = logger
        self.technical_analyzer = TechnicalAnalyzer()
        self.model = FXTradingModel()

    def generate_llm_analysis(self,
                             pair: str,
                             data: pd.DataFrame,
                             ml_prediction: Dict[str, Any],
                             length: str = 'long') -> Dict[str, Any]:
        """
        调用大模型进行双重验证分析

        Args:
            pair: 货币对代码
            data: 包含技术指标的数据
            ml_prediction: ML 预测结果
            length: 分析长度 ('short' | 'medium' | 'long')

        Returns:
            {
                'recommendation': 'buy/sell/hold',
                'confidence': 'high/medium/low',
                'llm_report': str,
                'key_factors': List[str]
            }

        Raises:
            ValueError: API 密钥未配置或输出格式错误
            requests.exceptions.RequestException: API 调用失败
        """
        # 暂时返回空字典，稍后实现
        return {}

    def analyze_pair(self, pair: str, data: pd.DataFrame,
                    ml_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析单个货币对

        Args:
            pair: 货币对代码
            data: 汇率数据
            ml_prediction: ML 预测结果

        Returns:
            综合分析结果
        """
        # 1. 生成技术信号
        technical_signal = self._generate_technical_signal(data)

        # 2. 验证信号（应用硬性约束）
        validated_signal = self._validate_signals(
            technical_signal, ml_prediction
        )

        # 3. 生成综合建议
        recommendation = self._generate_recommendation(
            pair, data, technical_signal, ml_prediction, validated_signal
        )

        return recommendation

    def _generate_technical_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        生成技术信号

        Args:
            data: 汇率数据

        Returns:
            技术信号字典
        """
        # 计算技术指标
        data = self.technical_analyzer.compute_all_indicators(data)

        # 简化的信号强度计算
        latest = data.iloc[-1]

        # 基于 RSI 的信号
        rsi_signal = 0
        if 'RSI14' in data.columns and not pd.isna(latest['RSI14']):
            if latest['RSI14'] < 30:
                rsi_signal = 20  # 超卖，买入信号
            elif latest['RSI14'] > 70:
                rsi_signal = -20  # 超买，卖出信号

        # 基于均线交叉的信号
        ma_signal = 0
        if 'SMA5' in data.columns and 'SMA20' in data.columns:
            if not pd.isna(latest['SMA5']) and not pd.isna(latest['SMA20']):
                if latest['SMA5'] > latest['SMA20']:
                    ma_signal = 15  # 金叉，买入信号
                else:
                    ma_signal = -15  # 死叉，卖出信号

        # 综合信号强度（0-100）
        signal_strength = 50 + rsi_signal + ma_signal
        signal_strength = max(0, min(100, signal_strength))

        # 生成买卖信号
        if signal_strength >= 60:
            signal = 'buy'
        elif signal_strength <= 40:
            signal = 'sell'
        else:
            signal = 'hold'

        return {
            'signal': signal,
            'strength': signal_strength
        }

    def _validate_signals(self, technical_signal: Dict[str, Any],
                        ml_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证信号，应用硬性约束

        硬性约束：
        - ML probability ≤ 0.50 → 绝对禁止买入
        - ML probability ≥ 0.60 → 可以考虑强烈买入

        Args:
            technical_signal: 技术信号
            ml_prediction: ML 预测

        Returns:
            验证后的信号
        """
        ml_prob = ml_prediction.get('probability', 0.5)
        ml_pred = ml_prediction.get('prediction', 0)

        # 硬性约束：ML 概率 ≤ 0.50 → 绝对禁止买入
        if ml_prob <= 0.50:
            if technical_signal['signal'] == 'buy':
                self.logger.info(f"硬性约束：ML 概率 {ml_prob:.2f} ≤ 0.50，禁止买入")
                technical_signal['signal'] = 'hold'
                technical_signal['reason'] = 'ML 概率过低，违反硬性约束'
        # 高概率推荐：ML 概率 ≥ 0.60 且预测为 1（上涨）→ 推荐买入
        elif ml_prob >= 0.60 and ml_pred == 1:
            if technical_signal['signal'] != 'buy':
                self.logger.info(f"高概率推荐：ML 概率 {ml_prob:.2f} ≥ 0.60，推荐买入")
                technical_signal['signal'] = 'buy'
                technical_signal['reason'] = 'ML 概率高，推荐买入'

        return technical_signal

    def _generate_recommendation(self, pair: str, data: pd.DataFrame,
                                technical_signal: Dict[str, Any],
                                ml_prediction: Dict[str, Any],
                                validated_signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成综合建议

        Args:
            pair: 货币对代码
            data: 汇率数据
            technical_signal: 技术信号
            ml_prediction: ML 预测
            validated_signal: 验证后的信号

        Returns:
            综合建议字典
        """
        current_price = data['Close'].iloc[-1]

        # 计算止损位和止盈位（基于 ATR）
        atr = data.get('ATR14', pd.Series([0.01] * len(data))).iloc[-1]
        stop_loss = current_price - (atr * 2)
        take_profit = current_price + (atr * 2)

        # 构建推理
        reasoning = (
            f"技术信号 {validated_signal['signal']} "
            f"(强度 {validated_signal['strength']:.0f})，"
            f"ML 预测 {ml_prediction['prediction']} "
            f"(概率 {ml_prediction['probability']:.2f})"
        )

        if 'reason' in validated_signal:
            reasoning += f"，{validated_signal['reason']}"

        # 检查一致性
        # 将 ML prediction (0/1) 转换为 'sell'/'buy'
        ml_signal = 'buy' if ml_prediction.get('prediction') == 1 else 'sell'
        consistency = (technical_signal['signal'] == ml_signal or
                      technical_signal['signal'] == 'hold')

        result = {
            'pair': pair,
            'technical_signal': technical_signal['signal'],
            'technical_strength': validated_signal['strength'],
            'ml_prediction': ml_prediction['prediction'],
            'ml_probability': ml_prediction['probability'],
            'ml_confidence': ml_prediction.get('confidence', 'low'),
            'consistency': consistency,
            'recommendation': validated_signal['signal'],
            'confidence': ml_prediction.get('confidence', 'low'),
            'reasoning': reasoning,
            'entry_price': float(current_price),
            'stop_loss': float(stop_loss),
            'take_profit': float(take_profit),
            'risk_reward_ratio': 1.0,
            'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d')
        }

        return result


if __name__ == "__main__":
    import argparse
    from data_services.excel_loader import FXDataLoader
    from ml_services.fx_trading_model import FXTradingModel
    from config import MODEL_CONFIG

    parser = argparse.ArgumentParser(description="外汇综合分析")
    parser.add_argument('--date', type=str, default=None, help='分析日期（YYYY-MM-DD）')
    parser.add_argument('--pair', type=str, help='货币对代码（如 EUR、JPY 等）')
    parser.add_argument('--data_file', type=str, default='FXRate_20260320.xlsx', help='数据文件路径')

    args = parser.parse_args()

    analyzer = ComprehensiveAnalyzer()

    # 如果指定了货币对，只分析该货币对
    if args.pair:
        loader = FXDataLoader()
        df = loader.load_pair(args.pair, args.data_file)

        if df is None or df.empty:
            print(f"错误: 无法加载货币对 {args.pair} 的数据")
            exit(1)

        # 创建模型
        model = FXTradingModel(MODEL_CONFIG)

        # 生成预测
        ml_prediction = model.predict(args.pair, df)

        # 综合分析
        result = analyzer.analyze_pair(args.pair, df, ml_prediction)

        print(f"\n=== {args.pair} 综合分析 ===")
        print(f"技术信号: {result['technical_signal']} (强度: {result['technical_strength']:.0f})")
        print(f"ML预测: {'上涨' if result['ml_prediction'] == 1 else '下跌'} (概率: {result['ml_probability']:.2f})")
        print(f"置信度: {result['ml_confidence']}")
        print(f"一致性: {'是' if result['consistency'] else '否'}")
        print(f"\n建议: {result['recommendation']}")
        print(f"入场价: {result['entry_price']:.4f}")
        print(f"止损位: {result['stop_loss']:.4f}")
        print(f"止盈位: {result['take_profit']:.4f}")
        print(f"\n推理: {result['reasoning']}")
    else:
        # 分析所有货币对
        loader = FXDataLoader()
        all_data = loader.load_all_pairs(args.data_file)

        model = FXTradingModel(MODEL_CONFIG)

        print(f"\n=== 所有货币对综合分析 ===")
        print(f"分析日期: {args.date or pd.Timestamp.now().strftime('%Y-%m-%d')}\n")

        for pair, df in all_data.items():
            try:
                ml_prediction = model.predict(pair, df)
                result = analyzer.analyze_pair(pair, df, ml_prediction)

                print(f"--- {pair} ---")
                print(f"建议: {result['recommendation'].upper()} | "
                      f"入场: {result['entry_price']:.4f} | "
                      f"止损: {result['stop_loss']:.4f} | "
                      f"止盈: {result['take_profit']:.4f}")
                print(f"技术: {result['technical_signal']} ({result['technical_strength']:.0f}) | "
                      f"ML: {'上涨' if result['ml_prediction'] == 1 else '下跌'} ({result['ml_probability']:.2f})")
                print()
            except Exception as e:
                logger.error(f"分析货币对 {pair} 失败: {e}")
                continue