import pandas as pd
import logging
from typing import Dict, Any
import json
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from data_services.technical_analysis import TechnicalAnalyzer
from ml_services.fx_trading_model import FXTradingModel
from llm_services.qwen_engine import chat_with_llm
from ml_services.multi_horizon_context import MultiHorizonContextBuilder
from ml_services.multi_horizon_prompt import MultiHorizonPromptBuilder
from ml_services.llm_parser import LLMAnalysisParser
from ml_services.strategy_generator import TradingStrategyGenerator
from ml_services.json_formatter import JSONFormatter

logger = logging.getLogger(__name__)


class ComprehensiveAnalyzer:
    """综合分析器 - 支持多周期分析"""

    def __init__(self):
        self.logger = logger
        self.technical_analyzer = TechnicalAnalyzer()
        self.model = FXTradingModel()
        self.context_builder = MultiHorizonContextBuilder()
        self.prompt_builder = MultiHorizonPromptBuilder()
        self.llm_parser = LLMAnalysisParser()
        self.strategy_generator = TradingStrategyGenerator()
        self.json_formatter = JSONFormatter()

    def generate_llm_analysis(self,
                             pair: str,
                             data: pd.DataFrame,
                             ml_prediction: Dict[str, Any],
                             length: str = 'long') -> Dict[str, Any]:
        """
        调用大模型进行双重验证分析
        """
        try:
            # 确保技术指标已计算
            if 'RSI14' not in data.columns:
                data = self.technical_analyzer.compute_all_indicators(data)
            
            # 构建 Prompt
            prompt = self._build_llm_prompt(pair, data, ml_prediction, length)
            
            # 调用 LLM（带性能监控）
            start_time = time.time()
            llm_response = chat_with_llm(prompt)
            elapsed = time.time() - start_time
            self.logger.info(f"LLM 调用耗时: {elapsed:.2f} 秒")
            
            # 解析 JSON 输出
            result = json.loads(llm_response)
            
            # 验证输出格式
            if result['recommendation'] not in ['buy', 'sell', 'hold']:
                raise ValueError(f"无效的 recommendation: {result['recommendation']}")
            if result['confidence'] not in ['high', 'medium', 'low']:
                raise ValueError(f"无效的 confidence: {result['confidence']}")
            if 'analysis' not in result or not result['analysis']:
                raise ValueError("LLM 输出缺少 analysis 字段")
            if 'key_factors' not in result or not isinstance(result['key_factors'], list):
                raise ValueError("LLM 输出缺少 key_factors 字段或格式错误")
            
            return {
                'recommendation': result['recommendation'],
                'confidence': result['confidence'],
                'llm_report': result['analysis'],
                'key_factors': result['key_factors']
            }
        
        except ValueError as e:
            raise ValueError(
                f"大模型分析失败：{str(e)}\n"
                f"请确保 QWEN_API_KEY 环境变量已设置，或使用 --no-llm 参数禁用大模型分析"
            )
        except json.JSONDecodeError as e:
            raise ValueError(
                f"大模型输出解析失败（JSON 格式错误）：{str(e)}\n"
                f"LLM 可能返回了非 JSON 格式的响应，请检查或重试"
            )
        except Exception as e:
            import requests
            if isinstance(e, requests.exceptions.RequestException):
                raise RuntimeError(
                    f"大模型 API 调用失败：{str(e)}\n"
                    f"请检查网络连接或稍后重试"
                )
            raise

    def _build_llm_prompt(self,
                         pair: str,
                         data: pd.DataFrame,
                         ml_prediction: Dict[str, Any],
                         length: str) -> str:
        """构建 LLM 分析的 Prompt"""
        latest = data.iloc[-1]
        current_price = float(latest['Close'])
        ml_pred = ml_prediction.get('prediction', 0)
        ml_prob = ml_prediction.get('probability', 0.5)
        ml_conf = ml_prediction.get('confidence', 'low')
        
        if length == 'short':
            prompt = f"""你是一个外汇交易分析师。请分析 {pair} 货币对：

当前价格：{current_price:.4f}

ML 预测：{'上涨' if ml_pred == 1 else '下跌'}，概率 {ml_prob:.2%}

请给出简短建议（50-100字）和关键理由。

请以以下 JSON 格式输出（确保是有效的 JSON，不要包含任何额外文字）：
{{
  "recommendation": "buy/sell/hold",
  "confidence": "high/medium/low",
  "analysis": "简短建议（50-100字）",
  "key_factors": ["因素1", "因素2", "因素3"]
}}
"""
        elif length == 'medium':
            rsi_value = latest.get('RSI14', 'N/A')
            macd_value = latest.get('MACD', 'N/A')
            
            prompt = f"""你是一个外汇交易分析师。请分析 {pair} 货币对：

当前价格：{current_price:.4f}

关键技术指标：
- RSI(14): {rsi_value}
- MACD: {macd_value}

ML 预测：{'上涨' if ml_pred == 1 else '下跌'}，概率 {ml_prob:.2%}，置信度：{ml_conf}

请给出市场分析（200-300字），包括：
1. 技术面分析
2. 风险提示
3. 交易建议（buy/sell/hold）

请以以下 JSON 格式输出（确保是有效的 JSON，不要包含任何额外文字）：
{{
  "recommendation": "buy/sell/hold",
  "confidence": "high/medium/low",
  "analysis": "市场分析文本（200-300字）",
  "key_factors": ["因素1", "因素2", "因素3"]
}}
"""
        else:  # long
            indicators = {
                '趋势类指标': {
                    'SMA5': latest.get('SMA5', 'N/A'),
                    'SMA10': latest.get('SMA10', 'N/A'),
                    'SMA20': latest.get('SMA20', 'N/A'),
                    'SMA50': latest.get('SMA50', 'N/A'),
                    'EMA5': latest.get('EMA5', 'N/A'),
                    'EMA20': latest.get('EMA20', 'N/A'),
                    'MACD': latest.get('MACD', 'N/A'),
                    'MACD_Signal': latest.get('MACD_Signal', 'N/A'),
                    'MACD_Hist': latest.get('MACD_Hist', 'N/A'),
                    'ADX': latest.get('ADX', 'N/A'),
                    'DI_Plus': latest.get('DI_Plus', 'N/A'),
                    'DI_Minus': latest.get('DI_Minus', 'N/A'),
                },
                '动量类指标': {
                    'RSI(14)': latest.get('RSI14', 'N/A'),
                    'K': latest.get('K', 'N/A'),
                    'D': latest.get('D', 'N/A'),
                    'J': latest.get('J', 'N/A'),
                    'Williams%R': latest.get('WilliamsR_14', 'N/A'),
                    'CCI': latest.get('CCI20', 'N/A'),
                },
                '波动类指标': {
                    'ATR(14)': latest.get('ATR14', 'N/A'),
                    '布林带上轨': latest.get('BB_Upper', 'N/A'),
                    '布林带中轨': latest.get('BB_Middle', 'N/A'),
                    '布林带下轨': latest.get('BB_Lower', 'N/A'),
                    '波动率': latest.get('Volatility_20d', 'N/A'),
                },
                '价格形态': {
                    '价格百分位(120日)': latest.get('Price_Percentile_120', 'N/A'),
                    'Bias_5': latest.get('Bias_5', 'N/A'),
                    'Bias_20': latest.get('Bias_20', 'N/A'),
                    '趋势斜率': latest.get('Trend_Slope_20', 'N/A'),
                },
                '市场环境': {
                    '均线排列': latest.get('MA_Alignment', 'N/A'),
                },
            }
            
            indicators_text = ""
            for category, values in indicators.items():
                indicators_text += f"\n{category}：\n"
                for key, value in values.items():
                    indicators_text += f"- {key}: {value}\n"
            
            prompt = f"""你是一个资深外汇交易分析师。请对 {pair} 货币对进行全面分析：

=== 基本信息 ===
当前价格：{current_price:.4f}
分析日期：{pd.Timestamp.now().strftime('%Y-%m-%d')}

=== 完整技术指标 ==={indicators_text}

=== ML 预测结果 ===
预测方向：{'上涨' if ml_pred == 1 else '下跌'}
预测概率：{ml_prob:.2%}
置信度：{ml_conf}

=== 分析要求 ===

**输出格式要求（必须严格遵守）**

请以以下 JSON 格式输出（确保是有效的 JSON，不要包含任何额外文字）：
{{
  "recommendation": "buy/sell/hold",
  "confidence": "high/medium/low",
  "analysis": "完整分析文本（500字以上）",
  "key_factors": ["因素1", "因素2", "因素3"]
}}

**分析内容要求：**

请提供完整的市场分析报告（500字以上），包括：

1. **技术面深度分析**
   - 趋势判断（多头/空头/震荡）
   - 关键技术指标解读
   - 支撑位和阻力位
   - 潜在反转信号

2. **ML 预测验证**
   - ML 预测与技术面的一致性
   - 预测可靠性评估

3. **风险分析**
   - 主要风险因素
   - 止损建议

4. **交易建议**
   - 明确建议（buy/sell/hold）
   - 入场价、止损位、止盈位
   - 仓位管理建议

5. **关键因素总结**
   - 列出 3-5 个影响决策的关键因素

请以专业的市场分析师口吻输出，用中文回答。
"""
        
        return prompt

    def analyze_pair(self,
                    pair: str,
                    data: pd.DataFrame,
                    use_llm: bool = True) -> Dict[str, Any]:
        """
        分析单个货币对 - 使用多周期工作流

        Args:
            pair: 货币对代码
            data: 原始数据
            use_llm: 是否使用大模型分析

        Returns:
            分析结果字典
        """
        # 1. 构建多周期上下文
        context = self.context_builder.build(pair, data)

        # 2. 调用 LLM 分析或规则引擎
        if use_llm:
            try:
                # 构建 Prompt
                prompt = self.prompt_builder.build(context)

                # 调用 LLM
                start_time = time.time()
                llm_response = chat_with_llm(prompt)
                elapsed = time.time() - start_time
                self.logger.info(f"LLM 调用耗时: {elapsed:.2f} 秒")

                # 解析 LLM 输出
                llm_result = self.llm_parser.parse(llm_response)
            except Exception as e:
                self.logger.warning(f"LLM 分析失败，使用规则引擎: {e}")
                llm_result = self._use_rule_engine(context)
        else:
            llm_result = self._use_rule_engine(context)

        # 3. 生成交易方案
        strategies = self.strategy_generator.generate(llm_result, context)

        # 4. 格式化为 JSON
        json_str = self.json_formatter.format(context, llm_result, strategies)

        # 5. 写入文件
        json_file = self.json_formatter.write_to_file(json_str, pair)

        # 6. 返回解析后的结果
        result = json.loads(json_str)
        result['json_file'] = json_file

        return result

    def _use_rule_engine(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用规则引擎作为 LLM 的后备方案

        Args:
            context: 多周期上下文

        Returns:
            规则引擎生成的分析结果
        """
        majority_trend = context['consistency_analysis']['majority_trend']
        if majority_trend == '上涨':
            recommendation = 'buy'
        elif majority_trend == '下跌':
            recommendation = 'sell'
        else:
            recommendation = 'hold'

        key_points = [f"{majority_trend}趋势", f"ML预测{majority_trend}", "一致性评分较低"]

        return {
            'summary': f"{context['pair']} {majority_trend}趋势，建议{recommendation}",
            'overall_assessment': '中性',
            'key_factors': [f"{majority_trend}趋势", "ML预测"],
            'horizon_analysis': {
                '1': {'recommendation': recommendation, 'confidence': 'medium', 'analysis': f'规则引擎：{majority_trend}趋势', 'key_points': key_points[:2]},
                '5': {'recommendation': recommendation, 'confidence': 'medium', 'analysis': f'规则引擎：{majority_trend}趋势', 'key_points': key_points[:2]},
                '20': {'recommendation': recommendation, 'confidence': 'medium', 'analysis': f'规则引擎：{majority_trend}趋势', 'key_points': key_points[:2]}
            }
        }

    def _generate_technical_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        """生成技术信号"""
        # 计算技术指标
        data = self.technical_analyzer.compute_all_indicators(data)

        # 简化的信号强度计算
        latest = data.iloc[-1]

        # 基于 RSI 的信号
        rsi_signal = 0
        if 'RSI14' in data.columns and not pd.isna(latest['RSI14']):
            if latest['RSI14'] < 30:
                rsi_signal = 20
            elif latest['RSI14'] > 70:
                rsi_signal = -20

        # 基于均线交叉的信号
        ma_signal = 0
        if 'SMA5' in data.columns and 'SMA20' in data.columns:
            if not pd.isna(latest['SMA5']) and not pd.isna(latest['SMA20']):
                if latest['SMA5'] > latest['SMA20']:
                    ma_signal = 15
                else:
                    ma_signal = -15

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
        """验证信号，应用硬性约束"""
        ml_prob = ml_prediction.get('probability', 0.5)
        ml_pred = ml_prediction.get('prediction', 0)

        if ml_prob <= 0.50:
            if technical_signal['signal'] == 'buy':
                self.logger.info(f"硬性约束：ML 概率 {ml_prob:.2f} ≤ 0.50，禁止买入")
                technical_signal['signal'] = 'hold'
                technical_signal['reason'] = 'ML 概率过低，违反硬性约束'
        elif ml_prob >= 0.60 and ml_pred == 1:
            if technical_signal['signal'] != 'buy':
                self.logger.info(f"高概率推荐：ML 概率 {ml_prob:.2f} ≥ 0.60，推荐买入")
                technical_signal['signal'] = 'buy'
                technical_signal['reason'] = 'ML 概率高，推荐买入'

        return technical_signal

    def _generate_recommendation(self, pair: str, data: pd.DataFrame,
                                technical_signal: Dict[str, Any],
                                ml_prediction: Dict[str, Any],
                                validated_signal: Dict[str, Any],
                                llm_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成综合建议"""
        current_price = float(data['Close'].iloc[-1])
        
        # 计算止损位和止盈位（基于 ATR）
        atr = data.get('ATR14', pd.Series([0.01] * len(data))).iloc[-1]
        stop_loss = current_price - (atr * 2)
        take_profit = current_price + (atr * 2)
        
        # 如果有 LLM 结果，优先使用 LLM 建议
        if llm_result:
            llm_recommendation = llm_result['recommendation']
            llm_confidence = llm_result['confidence']
            final_recommendation = llm_recommendation
            
            # 检查一致性
            ml_signal = 'buy' if ml_prediction.get('prediction') == 1 else 'sell'
            consistency = (llm_recommendation == ml_signal or 
                          llm_recommendation == 'hold')
        else:
            llm_recommendation = None
            llm_confidence = None
            final_recommendation = validated_signal['signal']
            
            # 检查一致性
            ml_signal = 'buy' if ml_prediction.get('prediction') == 1 else 'sell'
            consistency = (technical_signal['signal'] == ml_signal or
                          technical_signal['signal'] == 'hold')
        
        # 构建推理
        reasoning = (
            f"技术信号 {technical_signal['signal']} "
            f"(强度 {validated_signal['strength']:.0f})，"
            f"ML 预测 {ml_prediction['prediction']} "
            f"(概率 {ml_prediction['probability']:.2f})"
        )
        
        if 'reason' in validated_signal:
            reasoning += f"，{validated_signal['reason']}"
        
        result = {
            'pair': pair,
            'technical_signal': technical_signal['signal'],
            'technical_strength': validated_signal['strength'],
            'ml_prediction': ml_prediction['prediction'],
            'ml_probability': ml_prediction['probability'],
            'ml_confidence': ml_prediction.get('confidence', 'low'),
            'llm_recommendation': llm_recommendation,
            'llm_confidence': llm_confidence,
            'llm_report': llm_result['llm_report'] if llm_result else None,
            'key_factors': llm_result['key_factors'] if llm_result else None,
            'consistency': consistency,
            'final_recommendation': final_recommendation,
            'confidence': llm_confidence if llm_result else ml_prediction.get('confidence', 'low'),
            'reasoning': reasoning,
            'entry_price': current_price,
            'stop_loss': float(stop_loss),
            'take_profit': float(take_profit),
            'risk_reward_ratio': 1.0,
            'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d')
        }
        
        return result


if __name__ == "__main__":
    import argparse
    from data_services.excel_loader import FXDataLoader
    from config import DATA_CONFIG

    parser = argparse.ArgumentParser(description="外汇多周期综合分析")
    parser.add_argument('--pair', type=str, help='货币对代码（如 EUR、JPY 等）')
    parser.add_argument('--data_file', type=str, default=DATA_CONFIG['data_file'], help='数据文件路径')
    parser.add_argument('--no-llm', action='store_true',
                       help='禁用大模型分析（默认启用）')

    args = parser.parse_args()

    analyzer = ComprehensiveAnalyzer()
    use_llm = not args.no_llm

    if args.pair:
        loader = FXDataLoader()
        df = loader.load_pair(args.pair, args.data_file)

        if df is None or df.empty:
            print(f"错误: 无法加载货币对 {args.pair} 的数据")
            exit(1)

        # 使用新的多周期分析工作流
        result = analyzer.analyze_pair(args.pair, df, use_llm=use_llm)

        # 显示结果
        print(f"\n{'='*70}")
        print(f"{result['metadata']['pair_name']} 多周期综合分析")
        print(f"{'='*70}\n")

        print(f"【基本信息】")
        print(f"当前价格: {result['metadata']['current_price']:.4f}")
        print(f"数据日期: {result['metadata']['data_date']}")
        print(f"分析日期: {result['metadata']['analysis_date']}")
        print(f"分析周期: 1天、5天、20天\n")

        print(f"【ML 预测结果】")
        for horizon_key, pred in result['ml_predictions'].items():
            print(f"  {horizon_key.replace('_', ' ')}: {pred['prediction_text']} "
                  f"(概率: {pred['probability']:.2%}, 置信度: {pred['confidence']})")

        print(f"\n【预测一致性分析】")
        print(f"  一致性评分: {result['consistency_analysis']['score']:.2f}")
        print(f"  解读: {result['consistency_analysis']['interpretation']}")
        print(f"  多数趋势: {result['consistency_analysis']['majority_trend']}\n")

        print(f"【LLM 综合分析】")
        print(f"  摘要: {result['llm_analysis']['summary']}")
        print(f"  整体评估: {result['llm_analysis']['overall_assessment']}")
        print(f"  关键因素: {', '.join(result['llm_analysis']['key_factors'])}\n")

        print(f"【各周期建议】")
        horizon_names = {'1': '短线（1天）', '5': '中线（5天）', '20': '长线（20天）'}
        for horizon, analysis in result['llm_analysis']['horizon_analysis'].items():
            print(f"  {horizon_names.get(horizon, horizon)}:")
            print(f"    建议: {analysis['recommendation']} (置信度: {analysis['confidence']})")
            print(f"    分析: {analysis['analysis']}")
            print(f"    关键点: {', '.join(analysis['key_points'])}")
            print()

        print(f"【交易策略】")
        for strategy_key, strategy in result['trading_strategies'].items():
            print(f"  {strategy['name']}:")
            print(f"    建议: {strategy['recommendation']}")
            print(f"    入场价: {strategy['entry_price']:.4f}")
            print(f"    止损位: {strategy['stop_loss']:.4f}")
            print(f"    止盈位: {strategy['take_profit']:.4f}")
            print(f"    风险回报比: {strategy['risk_reward_ratio']:.2f}")
            print(f"    仓位大小: {strategy['position_size']}")
            print()

        print(f"【风险分析】")
        print(f"  整体风险等级: {result['risk_analysis']['overall_risk']}")
        print(f"  风险因素: {', '.join(result['risk_analysis']['risk_factors'])}")
        if result['risk_analysis']['warnings']:
            print(f"  警告: {', '.join(result['risk_analysis']['warnings'])}")
        print()

        print(f"{'='*70}")
        print(f"JSON 文件已保存: {result['json_file']}")
        print(f"{'='*70}\n")
    else:
        loader = FXDataLoader()
        all_data = loader.load_all_pairs(args.data_file)

        print(f"\n{'='*70}")
        print(f"所有货币对多周期综合分析")
        print(f"{'='*70}\n")

        for pair, df in all_data.items():
            try:
                result = analyzer.analyze_pair(pair, df, use_llm=use_llm)

                print(f"--- {result['metadata']['pair_name']} ---")
                print(f"当前价格: {result['metadata']['current_price']:.4f}")
                print(f"一致性评分: {result['consistency_analysis']['score']:.2f}")
                print(f"整体评估: {result['llm_analysis']['overall_assessment']}")

                # 显示各周期建议
                print("各周期建议:")
                horizon_names = {'1': '1天', '5': '5天', '20': '20天'}
                for horizon, analysis in result['llm_analysis']['horizon_analysis'].items():
                    print(f"  {horizon_names.get(horizon, horizon)}: {analysis['recommendation']} "
                          f"({analysis['confidence']})")

                # 显示短线交易策略
                short_term = result['trading_strategies']['short_term']
                print(f"短线策略: 入场 {short_term['entry_price']:.4f} | "
                      f"止损 {short_term['stop_loss']:.4f} | "
                      f"止盈 {short_term['take_profit']:.4f}")

                print(f"JSON 文件: {result['json_file']}")
                print()
            except Exception as e:
                logger.error(f"分析货币对 {pair} 失败: {e}")
                continue