import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class JSONFormatter:
    """JSON 格式化器"""

    def __init__(self):
        """初始化格式化器"""
        self.logger = logger

    def format(self, context: Dict[str, Any],
               llm_result: Dict[str, Any],
               strategies: Dict[str, Dict[str, Any]]) -> str:
        """
        格式化输出为 JSON

        Args:
            context: 多周期上下文
            llm_result: LLM 分析结果
            strategies: 交易方案

        Returns:
            JSON 字符串
        """
        self.logger.info("开始格式化 JSON 输出...")

        # 构建完整的 JSON 结构
        output = {
            'metadata': self._build_metadata(context),
            'ml_predictions': self._build_ml_predictions(context),
            'consistency_analysis': context['consistency_analysis'],
            'llm_analysis': self._build_llm_analysis(llm_result),
            'trading_strategies': self._build_trading_strategies(strategies),
            'technical_indicators': context['technical_indicators'],
            'risk_analysis': self._build_risk_analysis(context, strategies)
        }

        # 转换为 JSON 字符串
        json_str = json.dumps(output, ensure_ascii=False, indent=2)

        self.logger.info("JSON 格式化完成")
        return json_str

    def _build_metadata(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """构建元数据"""
        return {
            'pair': context['pair'],
            'pair_name': self._get_pair_name(context['pair']),
            'current_price': context['current_price'],
            'data_date': context['data_date'],
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'horizons': [1, 5, 20],
            'model_versions': {
                '1d': f"{context['pair']}_catboost_1d.pkl",
                '5d': f"{context['pair']}_catboost_5d.pkl",
                '20d': f"{context['pair']}_catboost_20d.pkl"
            }
        }

    def _build_ml_predictions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """构建 ML 预测"""
        horizon_names = {1: '1_day', 5: '5_day', 20: '20_day'}
        predictions = {}

        for horizon, pred in context['predictions'].items():
            predictions[horizon_names[horizon]] = {
                'horizon': horizon,
                'prediction': pred['prediction'],
                'prediction_text': '上涨' if pred['prediction'] == 1 else '下跌',
                'probability': pred['probability'],
                'confidence': pred['confidence'],
                'target_date': pred['target_date']
            }

        return predictions

    def _build_llm_analysis(self, llm_result: Dict[str, Any]) -> Dict[str, Any]:
        """构建 LLM 分析"""
        return {
            'summary': llm_result['summary'],
            'overall_assessment': llm_result['overall_assessment'],
            'key_factors': llm_result['key_factors'],
            'horizon_analysis': llm_result['horizon_analysis']
        }

    def _build_trading_strategies(self, strategies: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """构建交易方案"""
        return strategies

    def _build_risk_analysis(self, context: Dict[str, Any],
                           strategies: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """构建风险分析"""
        # 确定整体风险等级
        confidences = [s['confidence'] for s in strategies.values()]
        if 'high' in confidences:
            overall_risk = 'high'
        elif 'medium' in confidences:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'

        return {
            'overall_risk': overall_risk,
            'risk_factors': ['市场波动性', '预测不确定性'],
            'warnings': self._generate_warnings(context, strategies)
        }

    def _generate_warnings(self, context: Dict[str, Any],
                           strategies: Dict[str, Dict[str, Any]]) -> list:
        """生成警告"""
        warnings = []

        # 检查低置信度
        for horizon, strategy in strategies.items():
            if strategy['confidence'] == 'low':
                warnings.append(f"{strategy['name']} 置信度低，建议谨慎")

        # 检查一致性
        if context['consistency_analysis']['score'] < 0.5:
            warnings.append("各周期预测一致性较低，建议观望")

        return warnings

    def _get_pair_name(self, pair: str) -> str:
        """获取货币对名称"""
        pair_names = {
            'EUR': '欧元/美元',
            'JPY': '美元/日元',
            'AUD': '澳元/美元',
            'GBP': '英镑/美元',
            'CAD': '美元/加元',
            'NZD': '新西兰元/美元',
            'HKD': '港币/人民币'
        }
        return pair_names.get(pair, pair)

    def write_to_file(self, json_str: str, pair: str) -> str:
        """
        写入 JSON 文件

        Args:
            json_str: JSON 字符串
            pair: 货币对代码

        Returns:
            文件路径
        """
        # 创建输出目录
        output_dir = Path('data/predictions')
        output_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{pair}_multi_horizon_{timestamp}.json"
        file_path = output_dir / filename

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json_str)

        self.logger.info(f"JSON 文件已写入: {file_path}")
        return str(file_path)

    def validate_schema(self, data: dict) -> bool:
        """
        验证 JSON Schema

        Args:
            data: 数据字典

        Returns:
            是否有效
        """
        required_sections = [
            'metadata', 'ml_predictions', 'consistency_analysis',
            'llm_analysis', 'trading_strategies', 'technical_indicators',
            'risk_analysis'
        ]

        for section in required_sections:
            if section not in data:
                self.logger.error(f"缺少必需部分: {section}")
                return False

        return True