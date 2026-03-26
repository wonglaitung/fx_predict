import json
import logging

logger = logging.getLogger(__name__)


class LLMAnalysisParser:
    """LLM 输出解析器"""

    def __init__(self):
        """初始化解析器"""
        self.logger = logger

    def parse(self, json_str: str) -> dict:
        """
        解析 LLM 输出

        Args:
            json_str: LLM 返回的 JSON 字符串

        Returns:
            解析后的结果字典

        Raises:
            ValueError: JSON 格式错误或字段缺失
        """
        try:
            # 解析 JSON
            result = json.loads(json_str)

            # 验证必需字段
            self._validate_required_fields(result)

            # 验证字段值
            self._validate_field_values(result)

            self.logger.info("LLM 输出解析成功")
            return result

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 解析失败: {e}")
            # 返回默认值
            return self._get_default_result()
        except ValueError as e:
            self.logger.error(f"字段验证失败: {e}")
            return self._get_default_result()
        except Exception as e:
            self.logger.error(f"解析失败: {e}")
            return self._get_default_result()

    def _validate_required_fields(self, result: dict) -> None:
        """验证必需字段"""
        required_fields = ['summary', 'overall_assessment', 'key_factors', 'horizon_analysis']

        for field in required_fields:
            if field not in result:
                raise ValueError(f"缺少必需字段: {field}")

        # 验证 horizon_analysis
        if not isinstance(result['horizon_analysis'], dict):
            raise ValueError("horizon_analysis 必须是字典")

        required_horizons = [1, 5, 20]
        for horizon in required_horizons:
            if str(horizon) not in result['horizon_analysis']:
                raise ValueError(f"缺少周期 {horizon} 的分析")

            horizon_rec = result['horizon_analysis'][str(horizon)]
            required_horizon_fields = ['recommendation', 'confidence', 'analysis', 'key_points']
            for field in required_horizon_fields:
                if field not in horizon_rec:
                    raise ValueError(f"周期 {horizon} 缺少字段: {field}")

    def _validate_field_values(self, result: dict) -> None:
        """验证字段值"""
        # 验证 recommendation
        valid_recommendations = ['buy', 'sell', 'hold']
        for horizon, rec in result['horizon_analysis'].items():
            if rec['recommendation'] not in valid_recommendations:
                raise ValueError(f"无效的 recommendation: {rec['recommendation']}")

        # 验证 confidence
        valid_confidences = ['high', 'medium', 'low']
        for horizon, rec in result['horizon_analysis'].items():
            if rec['confidence'] not in valid_confidences:
                raise ValueError(f"无效的 confidence: {rec['confidence']}")

    def _get_default_result(self) -> dict:
        """获取默认结果"""
        return {
            'summary': '分析失败，使用默认建议',
            'overall_assessment': '未知',
            'key_factors': ['分析失败'],
            'horizon_analysis': {
                '1': {'recommendation': 'hold', 'confidence': 'low', 'analysis': '分析失败', 'key_points': []},
                '5': {'recommendation': 'hold', 'confidence': 'low', 'analysis': '分析失败', 'key_points': []},
                '20': {'recommendation': 'hold', 'confidence': 'low', 'analysis': '分析失败', 'key_points': []}
            }
        }