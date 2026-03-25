import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from ml_services.base_model_processor import BaseModelProcessor
from ml_services.feature_engineering import FeatureEngineer
from data_services.technical_analysis import TechnicalAnalyzer

import logging

logger = logging.getLogger(__name__)


class FXTradingModel:
    """外汇交易模型"""

    def __init__(self, config: dict = None):
        """
        初始化模型

        Args:
            config: 模型配置字典
        """
        from config import MODEL_CONFIG, INDICATOR_CONFIG

        self.config = config or MODEL_CONFIG
        self.horizon = self.config['horizon']
        self.indicator_config = INDICATOR_CONFIG

        self.model = None
        self.feature_engineer = FeatureEngineer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.model_processor = BaseModelProcessor()

        self.logger = logger

    def _get_confidence(self, probability: float) -> str:
        """
        根据概率计算置信度

        Args:
            probability: 预测概率

        Returns:
            high/medium/low
        """
        if probability >= self.config.get('high_confidence_threshold', 0.60):
            return 'high'
        elif probability >= 0.50:
            return 'medium'
        else:
            return 'low'

    def train(self, pair: str, data: pd.DataFrame) -> dict:
        """
        训练模型

        Args:
            pair: 货币对代码
            data: 训练数据（必须包含 Close, High, Low 列）

        Returns:
            训练指标字典
        """
        self.logger.info(f"开始训练 {pair} 模型...")

        # 1. 计算技术指标
        data = self.technical_analyzer.compute_all_indicators(data)

        # 2. 创建特征
        features = self.feature_engineer.create_features(data)

        # 3. 创建目标变量
        target = self.feature_engineer.create_target(data, horizon=self.horizon)

        # 4. 准备训练数据
        # 删除包含 NaN 的行
        valid_indices = ~(target.isna())
        features_valid = features[valid_indices]
        target_valid = target[valid_indices]

        # 获取特征列（排除非特征列）
        exclude_cols = ['Close', 'High', 'Low', 'Open', 'Volume', 'Date']
        feature_cols = [col for col in features_valid.columns if col not in exclude_cols]

        X = features_valid[feature_cols]
        y = target_valid

        # 5. 分割训练集和验证集
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )

        # 6. 训练 CatBoost 模型
        self.model = CatBoostClassifier(**self.config['catboost_params'])

        self.model.fit(
            X_train, y_train,
            eval_set=(X_val, y_val),
            early_stopping_rounds=50,
            verbose=False
        )

        # 7. 评估模型
        y_pred = self.model.predict(X_val)
        accuracy = accuracy_score(y_val, y_pred)

        # 8. 保存模型
        self.model_processor.save_model(self.model, pair, 'catboost')

        metrics = {
            'accuracy': accuracy,
            'feature_count': len(feature_cols),
            'train_samples': len(X_train),
            'val_samples': len(X_val)
        }

        self.logger.info(f"训练完成，准确率: {accuracy:.2%}")
        return metrics

    def predict(self, pair: str, data: pd.DataFrame) -> dict:
        """
        预测

        Args:
            pair: 货币对代码
            data: 预测数据（必须包含 Close, High, Low 列）

        Returns:
            预测结果字典
        """
        # 加载模型
        if self.model is None:
            try:
                self.model = self.model_processor.load_model(pair, 'catboost')
            except FileNotFoundError:
                self.logger.warning(f"模型不存在，使用默认预测")
                return self._get_default_prediction(pair, data)

        # 计算技术指标
        data = self.technical_analyzer.compute_all_indicators(data)

        # 创建特征
        features = self.feature_engineer.create_features(data)

        # 获取特征列
        exclude_cols = ['Close', 'High', 'Low', 'Open', 'Volume', 'Date']
        feature_cols = [col for col in features.columns if col not in exclude_cols]

        # 使用最后一行进行预测
        latest_data = features[feature_cols].iloc[-1:].copy()

        # 处理缺失值
        latest_data = latest_data.fillna(0)

        # 预测
        prediction = self.model.predict(latest_data)[0]
        probability = self.model.predict_proba(latest_data)[0][1]  # 正类概率

        # 计算置信度
        confidence = self._get_confidence(probability)

        # 硬性约束：ML probability ≤ 0.50 → 绝对禁止买入
        if probability <= 0.50:
            self.logger.info(f"硬性约束生效: {pair} probability {probability:.2%} ≤ 0.50，禁止买入")
            prediction = 0
            confidence = 'low'

        # 获取当前价格和目标日期
        current_price = data['Close'].iloc[-1]
        data_date = data.index[-1] if hasattr(data.index, 'to_pydatetime') else datetime.now()
        target_date = data_date + timedelta(days=self.horizon)

        result = {
            'pair': pair,
            'current_price': float(current_price),
            'prediction': int(prediction),
            'probability': float(probability),
            'confidence': confidence,
            'data_date': data_date.strftime('%Y-%m-%d'),
            'target_date': target_date.strftime('%Y-%m-%d')
        }

        self.logger.info(f"预测完成: {pair} - {prediction} ({probability:.2%})")
        return result

    def _get_default_prediction(self, pair: str, data: pd.DataFrame) -> dict:
        """
        获取默认预测（当模型不可用时）

        Args:
            pair: 货币对代码
            data: 数据

        Returns:
            默认预测结果
        """
        current_price = data['Close'].iloc[-1]
        data_date = datetime.now()
        target_date = data_date + timedelta(days=self.horizon)

        return {
            'pair': pair,
            'current_price': float(current_price),
            'prediction': 0,
            'probability': 0.5,
            'confidence': 'low',
            'data_date': data_date.strftime('%Y-%m-%d'),
            'target_date': target_date.strftime('%Y-%m-%d')
        }