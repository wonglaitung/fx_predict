import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime, timedelta

from data_services.technical_analysis import TechnicalAnalyzer
from ml_services.fx_trading_model import FXTradingModel

import logging

logger = logging.getLogger(__name__)


class MultiHorizonContextBuilder:
    """多周期上下文构建器"""

    def __init__(self):
        """初始化构建器"""
        self.technical_analyzer = TechnicalAnalyzer()
        self.model = FXTradingModel()
        self.logger = logger

    def build(self, pair: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        构建多周期上下文

        Args:
            pair: 货币对代码
            data: 原始数据

        Returns:
            MultiHorizonContext 对象
        """
        self.logger.info(f"开始构建 {pair} 多周期上下文...")

        # 1. 计算技术指标
        data = self.technical_analyzer.compute_all_indicators(data)
        self.logger.info(f"技术指标计算完成，共 35 个")

        # 2. 获取 ML 预测
        predictions = {}
        for horizon in [1, 5, 20]:
            try:
                pred = self.model.predict_horizon(pair, data, horizon)
                predictions[horizon] = pred
            except Exception as e:
                self.logger.warning(f"周期 {horizon} 预测失败: {e}")
                predictions[horizon] = self._get_default_prediction(horizon, data)

        self.logger.info(f"ML 预测完成，共 {len(predictions)} 个周期")

        # 3. 计算一致性分析
        consistency_analysis = self._calculate_consistency_analysis(predictions)

        # 4. 构建上下文
        latest = data.iloc[-1]
        context = {
            'pair': pair,
            'current_price': float(latest['Close']),
            'data_date': latest['Date'].strftime('%Y-%m-%d') if 'Date' in latest else (latest.name.strftime('%Y-%m-%d') if hasattr(latest.name, 'strftime') else datetime.now().strftime('%Y-%m-%d')),
            'predictions': predictions,
            'technical_indicators': self._organize_indicators(data),
            'consistency_analysis': consistency_analysis
        }

        self.logger.info(f"上下文构建完成，一致性评分: {consistency_analysis['score']:.2f}")
        return context

    def _get_default_prediction(self, horizon: int, data: pd.DataFrame) -> Dict[str, Any]:
        """获取默认预测"""
        current_price = data['Close'].iloc[-1]
        data_date = datetime.now()
        target_date = data_date + timedelta(days=horizon)

        return {
            'horizon': horizon,
            'prediction': 0,
            'probability': 0.50,
            'confidence': 'low',
            'target_date': target_date.strftime('%Y-%m-%d'),
            'model_file': 'default'
        }

    def _calculate_consistency_analysis(self, predictions: Dict[int, Any]) -> Dict[str, Any]:
        """计算一致性分析"""
        if not predictions:
            return {
                'score': 0.0,
                'interpretation': '无预测数据',
                'all_same': False,
                'majority_trend': 'unknown'
            }

        # 提取预测值
        preds = [p['prediction'] for p in predictions.values()]

        # 计算一致性评分
        if len(set(preds)) == 1:
            # 所有预测相同
            score = 1.0
            interpretation = '完全一致'
        elif preds.count(1) == 2 or preds.count(0) == 2:
            # 2/3 预测相同
            score = 0.67
            interpretation = '部分一致 - 多数趋势占优'
        else:
            # 趋势分化
            score = 0.33
            interpretation = '低一致性 - 趋势分化'

        # 判断多数趋势
        if preds.count(1) > preds.count(0):
            majority_trend = '上涨'
        elif preds.count(0) > preds.count(1):
            majority_trend = '下跌'
        else:
            majority_trend = '中性'

        return {
            'score': score,
            'interpretation': interpretation,
            'all_same': len(set(preds)) == 1,
            'majority_trend': majority_trend
        }

    def _organize_indicators(self, data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """组织技术指标"""
        latest = data.iloc[-1]
        indicators = {
            'trend': {},
            'momentum': {},
            'volatility': {},
            'volume': {},
            'price_pattern': {},
            'market_environment': {}
        }

        # 趋势类指标
        trend_cols = ['SMA5', 'SMA10', 'SMA20', 'SMA50', 'SMA120',
                     'EMA5', 'EMA10', 'EMA12', 'EMA20', 'EMA26',
                     'MACD', 'MACD_Signal', 'MACD_Hist', 'ADX', 'DI_Plus', 'DI_Minus']
        for col in trend_cols:
            if col in latest and pd.notna(latest[col]):
                indicators['trend'][col] = float(latest[col])

        # 动量类指标
        momentum_cols = ['RSI14', 'K', 'D', 'J', 'WilliamsR_14', 'CCI20']
        for col in momentum_cols:
            if col in latest and pd.notna(latest[col]):
                indicators['momentum'][col] = float(latest[col])

        # 波动类指标
        volatility_cols = ['ATR14', 'BB_Upper', 'BB_Middle', 'BB_Lower', 'Std_20d', 'Volatility_20d']
        for col in volatility_cols:
            if col in latest and pd.notna(latest[col]):
                indicators['volatility'][col] = float(latest[col])

        # 成交量类指标
        if 'OBV' in latest and pd.notna(latest['OBV']):
            indicators['volume']['OBV'] = float(latest['OBV'])

        # 价格形态指标
        pattern_cols = ['Price_Percentile_120', 'Bias_5', 'Bias_10', 'Bias_20', 'Trend_Slope_20']
        for col in pattern_cols:
            if col in latest and pd.notna(latest[col]):
                indicators['price_pattern'][col] = float(latest[col])

        # 市场环境指标
        env_cols = ['MA_Alignment', 'SMA5_cross_SMA20']
        for col in env_cols:
            if col in latest and pd.notna(latest[col]):
                indicators['market_environment'][col] = float(latest[col])

        return indicators