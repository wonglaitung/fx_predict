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
        consistency_analysis = self._calculate_consistency_analysis(predictions, data)

        # 4. 构建上下文
        latest = data.iloc[-1]
        # 优先使用 Date 列中的日期
        if 'Date' in latest:
            data_date_str = latest['Date'].strftime('%Y-%m-%d')
        elif hasattr(latest.name, 'strftime'):
            data_date_str = latest.name.strftime('%Y-%m-%d')
        else:
            data_date_str = datetime.now().strftime('%Y-%m-%d')
        
        context = {
            'pair': pair,
            'current_price': float(latest['Close']),
            'data_date': data_date_str,
            'predictions': predictions,
            'technical_indicators': self._organize_indicators(data),
            'consistency_analysis': consistency_analysis
        }

        self.logger.info(f"上下文构建完成，一致性评分: {consistency_analysis['score']:.2f}")
        return context

    def _get_default_prediction(self, horizon: int, data: pd.DataFrame) -> Dict[str, Any]:
        """获取默认预测"""
        current_price = data['Close'].iloc[-1]
        # 优先使用 Date 列中的日期
        if 'Date' in data.columns:
            data_date = data['Date'].iloc[-1]
        else:
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

    def _calculate_consistency_analysis(self, predictions: Dict[int, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """计算一致性分析（结合ML预测和技术指标）"""
        if not predictions:
            return {
                'score': 0.0,
                'interpretation': '无预测数据',
                'all_same': False,
                'majority_trend': 'unknown',
                'scores_by_horizon': {
                    '1d': 0.0,
                    '5d': 0.0,
                    '20d': 0.0,
                    'overall': 0.0
                },
                'technical_support': 0.0,
                'technical_indicators_summary': []
            }

        # 提取预测值
        preds = [p['prediction'] for p in predictions.values()]

        # 计算技术指标支持度
        technical_support = self._calculate_technical_support(data, predictions)
        self.logger.info(f"技术指标支持度: {technical_support:.2f}")

        # 计算基于预测概率和技术指标的一致性分数（每个时间周期）
        scores_by_horizon = {}
        total_score = 0.0
        horizon_count = 0

        for horizon, pred in predictions.items():
            # 基础分数：预测概率
            prob = pred.get('probability', 0.5)
            
            # 加上技术指标支持度（权重30%）
            adjusted_score = prob * 0.7 + technical_support * 0.3
            
            scores_by_horizon[f'{horizon}d'] = float(adjusted_score)
            total_score += adjusted_score
            horizon_count += 1

        # 计算整体一致性分数（各周期平均）
        overall_score = total_score / horizon_count if horizon_count > 0 else 0.0
        scores_by_horizon['overall'] = float(overall_score)

        # 计算整体一致性评分（基于预测方向的一致性）
        if len(set(preds)) == 1:
            # 所有预测相同
            direction_score = 1.0
            interpretation = '完全一致'
        elif preds.count(1) == 2 or preds.count(0) == 2:
            # 2/3 预测相同
            direction_score = 0.67
            interpretation = '部分一致 - 多数趋势占优'
        else:
            # 趋势分化
            direction_score = 0.33
            interpretation = '低一致性 - 趋势分化'

        # 判断多数趋势
        if preds.count(1) > preds.count(0):
            majority_trend = '上涨'
        elif preds.count(0) > preds.count(1):
            majority_trend = '下跌'
        else:
            majority_trend = '中性'

        # 生成技术指标摘要
        technical_summary = self._generate_technical_summary(data, predictions)

        return {
            'score': direction_score,  # 基于方向的一致性
            'interpretation': interpretation,
            'all_same': len(set(preds)) == 1,
            'majority_trend': majority_trend,
            'scores_by_horizon': scores_by_horizon,  # 基于概率和技术指标的分数
            'technical_support': technical_support,  # 技术指标支持度
            'technical_indicators_summary': technical_summary  # 技术指标摘要
        }

    def _calculate_technical_support(self, data: pd.DataFrame, predictions: Dict[int, Any]) -> float:
        """计算技术指标对预测的支持度"""
        latest = data.iloc[-1]
        support_score = 0.0
        indicators_count = 0

        # 获取多数趋势
        preds = [p['prediction'] for p in predictions.values()]
        majority_pred = 1 if preds.count(1) > preds.count(0) else 0

        # 1. 趋势指标支持度
        # MACD 柱状图
        if 'MACD_Hist' in latest and pd.notna(latest['MACD_Hist']):
            if majority_pred == 1 and latest['MACD_Hist'] > 0:
                support_score += 0.3
            elif majority_pred == 0 and latest['MACD_Hist'] < 0:
                support_score += 0.3
            indicators_count += 1

        # 均线排列
        if 'SMA5' in latest and 'SMA20' in latest and pd.notna(latest['SMA5']) and pd.notna(latest['SMA20']):
            if majority_pred == 1 and latest['SMA5'] > latest['SMA20']:
                support_score += 0.2
            elif majority_pred == 0 and latest['SMA5'] < latest['SMA20']:
                support_score += 0.2
            indicators_count += 1

        # 2. 动量指标支持度
        # RSI
        if 'RSI14' in latest and pd.notna(latest['RSI14']):
            rsi = latest['RSI14']
            if majority_pred == 1 and 30 < rsi < 70:
                support_score += 0.2  # RSI在中性区间，支持上涨
            elif majority_pred == 1 and rsi <= 30:
                support_score += 0.1  # RSI超卖，可能反弹
            elif majority_pred == 0 and rsi >= 70:
                support_score += 0.1  # RSI超买，可能下跌
            indicators_count += 1

        # 3. 价格形态支持度
        # 偏离率
        if 'Bias_5' in latest and pd.notna(latest['Bias_5']):
            if majority_pred == 1 and latest['Bias_5'] > -2:
                support_score += 0.15
            elif majority_pred == 0 and latest['Bias_5'] < 2:
                support_score += 0.15
            indicators_count += 1

        # 归一化支持度
        if indicators_count > 0:
            return min(1.0, support_score)
        return 0.0

    def _generate_technical_summary(self, data: pd.DataFrame, predictions: Dict[int, Any]) -> list:
        """生成技术指标摘要"""
        latest = data.iloc[-1]
        summary = []

        # 获取多数趋势
        preds = [p['prediction'] for p in predictions.values()]
        majority_trend = '上涨' if preds.count(1) > preds.count(0) else '下跌'

        # MACD
        if 'MACD_Hist' in latest and pd.notna(latest['MACD_Hist']):
            if latest['MACD_Hist'] > 0:
                summary.append(f"MACD柱状图为正，支持{majority_trend}")
            else:
                summary.append(f"MACD柱状图为负，可能压制{majority_trend}")

        # 均线
        if 'SMA5' in latest and 'SMA20' in latest and pd.notna(latest['SMA5']) and pd.notna(latest['SMA20']):
            if latest['SMA5'] > latest['SMA20']:
                summary.append(f"SMA5({latest['SMA5']:.4f}) > SMA20({latest['SMA20']:.4f})，多头排列")
            else:
                summary.append(f"SMA5({latest['SMA5']:.4f}) < SMA20({latest['SMA20']:.4f})，空头排列")

        # RSI
        if 'RSI14' in latest and pd.notna(latest['RSI14']):
            rsi = latest['RSI14']
            if rsi > 70:
                summary.append(f"RSI({rsi:.1f})超买，需警惕回调")
            elif rsi < 30:
                summary.append(f"RSI({rsi:.1f})超卖，可能反弹")
            else:
                summary.append(f"RSI({rsi:.1f})处于中性区间")

        # ATR（波动率）
        if 'ATR14' in latest and pd.notna(latest['ATR14']):
            atr = latest['ATR14']
            summary.append(f"ATR({atr:.6f})显示波动{'较高' if atr > 0.02 else '正常'}")

        return summary[:5]  # 最多返回5条摘要

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