from typing import Dict, Any

import logging

logger = logging.getLogger(__name__)


class MultiHorizonPromptBuilder:
    """多周期 Prompt 构建器"""

    def __init__(self):
        """初始化构建器"""
        self.logger = logger

    def build(self, context: Dict[str, Any]) -> str:
        """
        构建多周期分析 Prompt

        Args:
            context: MultiHorizonContext 对象

        Returns:
            Prompt 字符串
        """
        pair = context['pair']
        current_price = context['current_price']
        data_date = context['data_date']
        predictions = context['predictions']
        indicators = context['technical_indicators']
        consistency = context['consistency_analysis']

        # 构建技术指标部分
        indicators_text = self._format_indicators(indicators)

        # 构建 ML 预测部分
        predictions_text = self._format_predictions(predictions)

        # 构建一致性分析部分
        consistency_text = self._format_consistency(consistency)

        # 构建完整 Prompt
        prompt = f"""你是一个资深外汇交易分析师。请对 {pair} 货币对进行全面的多周期分析：

=== 基本信息 ===
当前价格：{current_price:.4f}
数据日期：{data_date}

=== 完整技术指标 ==={indicators_text}

=== ML 预测结果 ==={predictions_text}

=== 预测一致性分析 ==={consistency_text}

=== 分析要求 ===

**输出格式要求（必须严格遵守）**

请以以下 JSON 格式输出（确保是有效的 JSON，不要包含任何额外文字）：
{{
  "summary": "综合摘要（50-100字）",
  "overall_assessment": "整体评估（谨慎乐观/乐观/悲观/中性）",
  "key_factors": ["因素1", "因素2", "因素3"],
  "horizon_analysis": {{
    "1": {{
      "recommendation": "buy/sell/hold",
      "confidence": "high/medium/low",
      "analysis": "简要分析（1-2句话）",
      "key_points": ["关键点1", "关键点2"]
    }},
    "5": {{
      "recommendation": "buy/sell/hold",
      "confidence": "high/medium/low",
      "analysis": "简要分析（1-2句话）",
      "key_points": ["关键点1", "关键点2"]
    }},
    "20": {{
      "recommendation": "buy/sell/hold",
      "confidence": "high/medium/low",
      "analysis": "简要分析（1-2句话）",
      "key_points": ["关键点1", "关键点2"]
    }}
  }}
}}

**分析内容要求：**

1. **综合摘要**
   - 简要概括整体市场状况
   - 50-100 字

2. **整体评估**
   - 市场整体趋势判断
   - 风险水平评估

3. **关键因素**
   - 列出 3-5 个影响决策的关键因素

4. **各周期建议**
   - 为每个周期（1天、5天、20天）提供独立的建议
   - 基于技术面、ML 预测和一致性分析
   - 给出简要理由

请以专业的市场分析师口吻输出，用中文回答。
"""

        return prompt

    def _format_indicators(self, indicators: Dict[str, Dict[str, float]]) -> str:
        """格式化技术指标"""
        text = ""

        for category, values in indicators.items():
            if not values:
                continue

            category_names = {
                'trend': '趋势类指标',
                'momentum': '动量类指标',
                'volatility': '波动类指标',
                'volume': '成交量类指标',
                'price_pattern': '价格形态指标',
                'market_environment': '市场环境指标'
            }

            text += f"\n{category_names.get(category, category)}：\n"
            for key, value in values.items():
                if isinstance(value, float):
                    text += f"- {key}: {value:.4f}\n"
                else:
                    text += f"- {key}: {value}\n"

        return text

    def _format_predictions(self, predictions: Dict[int, Any]) -> str:
        """格式化 ML 预测"""
        text = ""

        horizon_names = {1: '1天', 5: '5天', 20: '20天'}

        for horizon, pred in predictions.items():
            direction = '上涨' if pred['prediction'] == 1 else '下跌'
            text += f"\n- {horizon_names.get(horizon, f'{horizon}天')}：{direction}，概率 {pred['probability']:.2%}，置信度：{pred['confidence']}"

        return text

    def _format_consistency(self, consistency: Dict[str, Any]) -> str:
        """格式化一致性分析"""
        text = f"\n- 一致性评分：{consistency['score']:.2f}"
        text += f"\n- 解读：{consistency['interpretation']}"
        text += f"\n- 多数趋势：{consistency['majority_trend']}"

        return text