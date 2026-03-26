from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class TradingStrategyGenerator:
    """交易方案生成器"""

    def __init__(self):
        """初始化生成器"""
        self.logger = logger

    def generate(self, llm_result: Dict[str, Any],
                 context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        生成交易方案

        Args:
            llm_result: LLM 分析结果
            context: 多周期上下文

        Returns:
            交易方案字典
        """
        self.logger.info("开始生成交易方案...")

        # 获取 ATR（用于计算止损止盈）
        atr = context['technical_indicators'].get('volatility', {}).get('ATR14', 0.01)
        current_price = context['current_price']

        # 生成各周期的交易方案
        strategies = {}
        horizon_names = {1: 'short_term', 5: 'medium_term', 20: 'long_term'}
        horizon_display = {1: '短线（1天）', 5: '中线（5天）', 20: '长线（20天）'}

        for horizon, strategy_name in horizon_names.items():
            llm_rec = llm_result['horizon_analysis'][str(horizon)]

            # 计算价格水平
            price_levels = self._calculate_price_levels(
                horizon,
                current_price,
                atr,
                llm_rec['recommendation']
            )

            # 确定仓位大小
            position_size = self._determine_position_size(
                llm_rec['confidence'],
                'medium'
            )

            # 构建交易方案
            strategies[strategy_name] = {
                'name': f"{horizon_display[horizon]}策略",
                'horizon': horizon,
                'recommendation': llm_rec['recommendation'],
                'confidence': llm_rec['confidence'],
                'entry_price': price_levels['entry_price'],
                'stop_loss': price_levels['stop_loss'],
                'take_profit': price_levels['take_profit'],
                'risk_reward_ratio': price_levels['risk_reward_ratio'],
                'position_size': position_size,
                'reasoning': llm_rec['analysis']  # 使用 analysis 字段
            }

        self.logger.info("交易方案生成完成")
        return strategies

    def _calculate_price_levels(self, horizon: int,
                                 current_price: float,
                                 atr: float,
                                 recommendation: str) -> Dict[str, float]:
        """计算价格水平"""
        # 根据周期调整 ATR 乘数
        atr_multiplier = 1.0 + (horizon / 20.0) * 2.0  # 1天: 1.0, 5天: 1.5, 20天: 3.0

        if recommendation == 'buy':
            stop_loss = current_price - atr * atr_multiplier
            take_profit = current_price + atr * atr_multiplier
        elif recommendation == 'sell':
            stop_loss = current_price + atr * atr_multiplier
            take_profit = current_price - atr * atr_multiplier
        else:  # hold
            stop_loss = current_price - atr * atr_multiplier
            take_profit = current_price + atr * atr_multiplier

        # 计算风险回报比
        if recommendation == 'buy':
            risk = current_price - stop_loss
            reward = take_profit - current_price
        elif recommendation == 'sell':
            risk = stop_loss - current_price
            reward = current_price - take_profit
        else:
            risk = abs(current_price - stop_loss)
            reward = abs(take_profit - current_price)

        risk_reward_ratio = reward / risk if risk > 0 else 1.0

        return {
            'entry_price': current_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_reward_ratio': round(risk_reward_ratio, 2)
        }

    def _determine_position_size(self, confidence: str,
                                   risk_level: str) -> str:
        """确定仓位大小"""
        if confidence == 'high':
            return 'large'
        elif confidence == 'medium':
            return 'medium'
        elif confidence == 'low':
            return 'small'
        else:
            return 'none'