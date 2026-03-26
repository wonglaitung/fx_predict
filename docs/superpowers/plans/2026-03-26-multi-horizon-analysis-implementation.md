# 多周期外汇智能分析系统实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标:** 构建一个完整的多周期外汇汇率预测和分析系统，支持同时预测 1 天、5 天、20 天的汇率涨跌，通过大模型进行双重验证分析，生成专业的市场分析报告和交易建议，并输出标准 JSON 格式。

**架构:** 采用模块化设计，新增4个专门模块（MultiHorizonContextBuilder、MultiHorizonPromptBuilder、LLMAnalysisParser、TradingStrategyGenerator、JSONFormatter），重构3个现有模块（FXTradingModel、ComprehensiveAnalyzer、命令行接口），实现从数据输入到JSON输出的完整数据流。

**Tech Stack:** Python 3.10+, CatBoost, Pandas, NumPy, 通义千问 LLM API, JSON

---

## 文件结构

### 新增文件
```
ml_services/
├── multi_horizon_context.py      # 多周期上下文构建器
├── multi_horizon_prompt.py       # Prompt 构建器
├── llm_parser.py                 # LLM 输出解析器
├── strategy_generator.py         # 交易方案生成器
└── json_formatter.py             # JSON 格式化器

tests/
├── test_multi_horizon_context.py
├── test_multi_horizon_prompt.py
├── test_llm_parser.py
├── test_strategy_generator.py
└── test_json_formatter.py
```

### 修改文件
```
ml_services/
└── fx_trading_model.py          # 移除单周期方法，保留 predict_all_horizons

comprehensive_analysis.py         # 重构为多周期核心

run_full_pipeline.sh              # 简化参数

config.py                         # 保持不变

docs/superpowers/
└── specs/2026-03-26-multi-horizon-analysis-design.md  # 设计文档（已存在）
```

---

## Task 1: 创建 MultiHorizonContextBuilder 模块

**Files:**
- Create: `ml_services/multi_horizon_context.py`
- Test: `tests/test_multi_horizon_context.py`

**职责:** 构建多周期分析上下文对象，包含所有技术指标和ML预测结果，计算一致性评分。

- [ ] **Step 1: Write failing test for MultiHorizonContextBuilder initialization**

```python
# tests/test_multi_horizon_context.py
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ml_services.multi_horizon_context import MultiHorizonContextBuilder
from data_services.technical_analysis import TechnicalAnalyzer
from ml_services.fx_trading_model import FXTradingModel

def test_context_builder_initialization():
    """测试 MultiHorizonContextBuilder 初始化"""
    builder = MultiHorizonContextBuilder()
    assert builder is not None
    assert builder.technical_analyzer is not None
    assert builder.model is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_multi_horizon_context.py::test_context_builder_initialization -v`
Expected: FAIL with "No module named 'ml_services.multi_horizon_context'"

- [ ] **Step 3: Create MultiHorizonContextBuilder skeleton**

```python
# ml_services/multi_horizon_context.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_multi_horizon_context.py::test_context_builder_initialization -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ml_services/multi_horizon_context.py tests/test_multi_horizon_context.py
git commit -m "feat: add MultiHorizonContextBuilder skeleton"
```

- [ ] **Step 6: Write failing test for build method**

```python
# tests/test_multi_horizon_context.py
def test_build_context():
    """测试构建上下文"""
    # 创建测试数据
    dates = pd.date_range('2020-01-01', periods=150)
    close_prices = [1.0 + i * 0.001 for i in range(150)]
    
    test_data = pd.DataFrame({
        'Date': dates,
        'Close': close_prices,
        'Open': close_prices,
        'High': [c * 1.01 for c in close_prices],
        'Low': [c * 0.99 for c in close_prices]
    })
    
    builder = MultiHorizonContextBuilder()
    context = builder.build('EUR', test_data)
    
    # 验证基本结构
    assert context['pair'] == 'EUR'
    assert 'current_price' in context
    assert 'predictions' in context
    assert 'technical_indicators' in context
    assert 'consistency_analysis' in context
    
    # 验证预测数量
    assert len(context['predictions']) == 3
    assert 1 in context['predictions']
    assert 5 in context['predictions']
    assert 20 in context['predictions']
```

- [ ] **Step 7: Run test to verify it fails**

Run: `pytest tests/test_multi_horizon_context.py::test_build_context -v`
Expected: FAIL with "MultiHorizonContextBuilder has no attribute 'build'"

- [ ] **Step 8: Implement build method**

```python
# ml_services/multi_horizon_context.py
class MultiHorizonContextBuilder:
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
        self.logger.info(f"技术指标计算完成，共 36 个")
        
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
            'data_date': latest['Date'].strftime('%Y-%m-%d') if 'Date' in latest else datetime.now().strftime('%Y-%m-%d'),
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
            score = 1.0
            interpretation = '完全一致'
        elif preds.count(1) == 2 or preds.count(0) == 2:
            score = 0.67
            interpretation = '部分一致 - 多数趋势占优'
        else:
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
```

- [ ] **Step 9: Run test to verify it passes**

Run: `pytest tests/test_multi_horizon_context.py::test_build_context -v`
Expected: PASS

- [ ] **Step 10: Write failing test for consistency calculation**

```python
# tests/test_multi_horizon_context.py
def test_consistency_calculation():
    """测试一致性计算"""
    builder = MultiHorizonContextBuilder()
    
    # 测试用例
    test_cases = [
        ({1: {'prediction': 1}, 5: {'prediction': 1}, 20: {'prediction': 1}}, 1.0),
        ({1: {'prediction': 0}, 5: {'prediction': 0}, 20: {'prediction': 0}}, 1.0),
        ({1: {'prediction': 1}, 5: {'prediction': 0}, 20: {'prediction': 1}}, 0.67),
        ({1: {'prediction': 1}, 5: {'prediction': 0}, 20: {'prediction': 0}}, 0.33),
    ]
    
    for predictions, expected_score in test_cases:
        result = builder._calculate_consistency_analysis(predictions)
        assert abs(result['score'] - expected_score) < 0.01, f"Expected {expected_score}, got {result['score']}"
```

- [ ] **Step 11: Run test to verify it passes**

Run: `pytest tests/test_multi_horizon_context.py::test_consistency_calculation -v`
Expected: PASS

- [ ] **Step 12: Commit**

```bash
git add ml_services/multi_horizon_context.py tests/test_multi_horizon_context.py
git commit -m "feat: implement MultiHorizonContextBuilder with full functionality"
```

---

## Task 2: 创建 MultiHorizonPromptBuilder 模块

**Files:**
- Create: `ml_services/multi_horizon_prompt.py`
- Test: `tests/test_multi_horizon_prompt.py`

**职责:** 构建多周期分析的 LLM Prompt，格式化技术指标和ML预测结果。

- [ ] **Step 1: Write failing test for MultiHorizonPromptBuilder**

```python
# tests/test_multi_horizon_prompt.py
import pytest
from ml_services.multi_horizon_prompt import MultiHorizonPromptBuilder

def test_prompt_builder_initialization():
    """测试 PromptBuilder 初始化"""
    builder = MultiHorizonPromptBuilder()
    assert builder is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_multi_horizon_prompt.py::test_prompt_builder_initialization -v`
Expected: FAIL with "No module named 'ml_services.multi_horizon_prompt'"

- [ ] **Step 3: Create MultiHorizonPromptBuilder skeleton**

```python
# ml_services/multi_horizon_prompt.py
from typing import Dict, Any

import logging

logger = logging.getLogger(__name__)


class MultiHorizonPromptBuilder:
    """多周期 Prompt 构建器"""
    
    def __init__(self):
        """初始化构建器"""
        self.logger = logger
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_multi_horizon_prompt.py::test_prompt_builder_initialization -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ml_services/multi_horizon_prompt.py tests/test_multi_horizon_prompt.py
git commit -m "feat: add MultiHorizonPromptBuilder skeleton"
```

- [ ] **Step 6: Write failing test for build method**

```python
# tests/test_multi_horizon_prompt.py
def test_build_prompt():
    """测试构建 Prompt"""
    # 创建测试上下文
    test_context = {
        'pair': 'EUR',
        'current_price': 1.1570,
        'data_date': '2026-03-20',
        'predictions': {
            1: {'prediction': 1, 'probability': 0.5132, 'confidence': 'medium', 'target_date': '2026-03-21'},
            5: {'prediction': 0, 'probability': 0.5000, 'confidence': 'low', 'target_date': '2026-03-25'},
            20: {'prediction': 0, 'probability': 0.5000, 'confidence': 'low', 'target_date': '2026-04-09'}
        },
        'technical_indicators': {
            'trend': {'SMA5': 1.1568, 'RSI14': 28.5},
            'momentum': {},
            'volatility': {},
            'volume': {},
            'price_pattern': {},
            'market_environment': {}
        },
        'consistency_analysis': {
            'score': 0.33,
            'interpretation': '低一致性',
            'all_same': False,
            'majority_trend': '下跌'
        }
    }
    
    builder = MultiHorizonPromptBuilder()
    prompt = builder.build(test_context)
    
    # 验证 Prompt 包含必要信息
    assert 'EUR' in prompt
    assert '1.1570' in prompt
    assert '1 天' in prompt
    assert '5 天' in prompt
    assert '20 天' in prompt
    assert 'JSON 格式' in prompt
```

- [ ] **Step 7: Run test to verify it fails**

Run: `pytest tests/test_multi_horizon_prompt.py::test_build_prompt -v`
Expected: FAIL with "MultiHorizonPromptBuilder has no attribute 'build'"

- [ ] **Step 8: Implement build method**

```python
# ml_services/multi_horizon_prompt.py
class MultiHorizonPromptBuilder:
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
  "horizon_recommendations": {{
    "1": {{
      "recommendation": "buy/sell/hold",
      "confidence": "high/medium/low",
      "reasoning": "简要理由（1-2句话）"
    }},
    "5": {{
      "recommendation": "buy/sell/hold",
      "confidence": "high/medium/low",
      "reasoning": "简要理由（1-2句话）"
    }},
    "20": {{
      "recommendation": "buy/sell/hold",
      "confidence": "high/medium/low",
      "reasoning": "简要理由（1-2句话）"
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
```

- [ ] **Step 9: Run test to verify it passes**

Run: `pytest tests/test_multi_horizon_prompt.py::test_build_prompt -v`
Expected: PASS

- [ ] **Step 10: Commit**

```bash
git add ml_services/multi_horizon_prompt.py tests/test_multi_horizon_prompt.py
git commit -m "feat: implement MultiHorizonPromptBuilder with full functionality"
```

---

## Task 3: 创建 LLMAnalysisParser 模块

**Files:**
- Create: `ml_services/llm_parser.py`
- Test: `tests/test_llm_parser.py`

**职责:** 解析 LLM 的 JSON 输出，验证字段完整性。

- [ ] **Step 1: Write failing test for LLMAnalysisParser**

```python
# tests/test_llm_parser.py
import pytest
from ml_services.llm_parser import LLMAnalysisParser

def test_parser_initialization():
    """测试 Parser 初始化"""
    parser = LLMAnalysisParser()
    assert parser is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_llm_parser.py::test_parser_initialization -v`
Expected: FAIL with "No module named 'ml_services.llm_parser'"

- [ ] **Step 3: Create LLMAnalysisParser skeleton**

```python
# ml_services/llm_parser.py
import json
import logging

logger = logging.getLogger(__name__)


class LLMAnalysisParser:
    """LLM 输出解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.logger = logger
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_llm_parser.py::test_parser_initialization -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ml_services/llm_parser.py tests/test_llm_parser.py
git commit -m "feat: add LLMAnalysisParser skeleton"
```

- [ ] **Step 6: Write failing test for parse method**

```python
# tests/test_llm_parser.py
def test_parse_valid_json():
    """测试解析有效的 JSON"""
    parser = LLMAnalysisParser()
    
    valid_json = '''{
        "summary": "测试摘要",
        "overall_assessment": "中性",
        "key_factors": ["因素1", "因素2"],
        "horizon_recommendations": {
            "1": {"recommendation": "buy", "confidence": "medium", "reasoning": "理由1"},
            "5": {"recommendation": "hold", "confidence": "low", "reasoning": "理由2"},
            "20": {"recommendation": "sell", "confidence": "medium", "reasoning": "理由3"}
        }
    }'''
    
    result = parser.parse(valid_json)
    
    # 验证必需字段
    assert 'summary' in result
    assert 'overall_assessment' in result
    assert 'key_factors' in result
    assert 'horizon_recommendations' in result
    assert len(result['horizon_recommendations']) == 3
```

- [ ] **Step 7: Run test to verify it fails**

Run: `pytest tests/test_llm_parser.py::test_parse_valid_json -v`
Expected: FAIL with "LLMAnalysisParser has no attribute 'parse'"

- [ ] **Step 8: Implement parse method**

```python
# ml_services/llm_parser.py
class LLMAnalysisParser:
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
        required_fields = ['summary', 'overall_assessment', 'key_factors', 'horizon_recommendations']
        
        for field in required_fields:
            if field not in result:
                raise ValueError(f"缺少必需字段: {field}")
        
        # 验证 horizon_recommendations
        if not isinstance(result['horizon_recommendations'], dict):
            raise ValueError("horizon_recommendations 必须是字典")
        
        required_horizons = [1, 5, 20]
        for horizon in required_horizons:
            if str(horizon) not in result['horizon_recommendations']:
                raise ValueError(f"缺少周期 {horizon} 的推荐")
            
            horizon_rec = result['horizon_recommendations'][str(horizon)]
            required_horizon_fields = ['recommendation', 'confidence', 'reasoning']
            for field in required_horizon_fields:
                if field not in horizon_rec:
                    raise ValueError(f"周期 {horizon} 缺少字段: {field}")
    
    def _validate_field_values(self, result: dict) -> None:
        """验证字段值"""
        # 验证 recommendation
        valid_recommendations = ['buy', 'sell', 'hold']
        for horizon, rec in result['horizon_recommendations'].items():
            if rec['recommendation'] not in valid_recommendations:
                raise ValueError(f"无效的 recommendation: {rec['recommendation']}")
        
        # 验证 confidence
        valid_confidences = ['high', 'medium', 'low']
        for horizon, rec in result['horizon_recommendations'].items():
            if rec['confidence'] not in valid_confidences:
                raise ValueError(f"无效的 confidence: {rec['confidence']}")
    
    def _get_default_result(self) -> dict:
        """获取默认结果"""
        return {
            'summary': '分析失败，使用默认建议',
            'overall_assessment': '未知',
            'key_factors': ['分析失败'],
            'horizon_recommendations': {
                '1': {'recommendation': 'hold', 'confidence': 'low', 'reasoning': '分析失败'},
                '5': {'recommendation': 'hold', 'confidence': 'low', 'reasoning': '分析失败'},
                '20': {'recommendation': 'hold', 'confidence': 'low', 'reasoning': '分析失败'}
            }
        }
```

- [ ] **Step 9: Run test to verify it passes**

Run: `pytest tests/test_llm_parser.py::test_parse_valid_json -v`
Expected: PASS

- [ ] **Step 10: Write failing test for invalid JSON**

```python
# tests/test_llm_parser.py
def test_parse_invalid_json():
    """测试解析无效的 JSON"""
    parser = LLMAnalysisParser()
    
    invalid_json = '{ invalid json }'
    result = parser.parse(invalid_json)
    
    # 应该返回默认值
    assert 'summary' in result
    assert result['summary'] == '分析失败，使用默认建议'
```

- [ ] **Step 11: Run test to verify it passes**

Run: `pytest tests/test_llm_parser.py::test_parse_invalid_json -v`
Expected: PASS

- [ ] **Step 12: Commit**

```bash
git add ml_services/llm_parser.py tests/test_llm_parser.py
git commit -m "feat: implement LLMAnalysisParser with validation and error handling"
```

---

## Task 4: 创建 TradingStrategyGenerator 模块

**Files:**
- Create: `ml_services/strategy_generator.py`
- Test: `tests/test_strategy_generator.py`

**职责:** 生成交易执行方案，计算入场价、止损位、止盈位。

- [ ] **Step 1: Write failing test for TradingStrategyGenerator**

```python
# tests/test_strategy_generator.py
import pytest
from ml_services.strategy_generator import TradingStrategyGenerator

def test_strategy_generator_initialization():
    """测试 StrategyGenerator 初始化"""
    generator = TradingStrategyGenerator()
    assert generator is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_strategy_generator.py::test_strategy_generator_initialization -v`
Expected: FAIL with "No module named 'ml_services.strategy_generator'"

- [ ] **Step 3: Create TradingStrategyGenerator skeleton**

```python
# ml_services/strategy_generator.py
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class TradingStrategyGenerator:
    """交易方案生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.logger = logger
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_strategy_generator.py::test_strategy_generator_initialization -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ml_services/strategy_generator.py tests/test_strategy_generator.py
git commit -m "feat: add TradingStrategyGenerator skeleton"
```

- [ ] **Step 6: Write failing test for generate method**

```python
# tests/test_strategy_generator.py
def test_generate_strategies():
    """测试生成交易方案"""
    generator = TradingStrategyGenerator()
    
    # 创建测试数据
    llm_result = {
        'summary': '测试摘要',
        'overall_assessment': '中性',
        'key_factors': ['因素1'],
        'horizon_recommendations': {
            '1': {'recommendation': 'buy', 'confidence': 'medium', 'reasoning': '理由1'},
            '5': {'recommendation': 'hold', 'confidence': 'low', 'reasoning': '理由2'},
            '20': {'recommendation': 'sell', 'confidence': 'medium', 'reasoning': '理由3'}
        }
    }
    
    context = {
        'pair': 'EUR',
        'current_price': 1.1570,
        'technical_indicators': {
            'volatility': {'ATR14': 0.0100}
        }
    }
    
    strategies = generator.generate(llm_result, context)
    
    # 验证必需字段
    assert 'short_term' in strategies
    assert 'medium_term' in strategies
    assert 'long_term' in strategies
    
    # 验证字段顺序
    expected_order = ['name', 'horizon', 'recommendation', 'confidence',
                     'entry_price', 'stop_loss', 'take_profit',
                     'risk_reward_ratio', 'position_size', 'reasoning']
    
    for strategy_name, strategy in strategies.items():
        keys = list(strategy.keys())
        assert keys == expected_order, f"{strategy_name} 字段顺序不正确"
```

- [ ] **Step 7: Run test to verify it fails**

Run: `pytest tests/test_strategy_generator.py::test_generate_strategies -v`
Expected: FAIL with "TradingStrategyGenerator has no attribute 'generate'"

- [ ] **Step 8: Implement generate method**

```python
# ml_services/strategy_generator.py
class TradingStrategyGenerator:
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
            llm_rec = llm_result['horizon_recommendations'][str(horizon)]
            
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
                'reasoning': llm_rec['reasoning']
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
```

- [ ] **Step 9: Run test to verify it passes**

Run: `pytest tests/test_strategy_generator.py::test_generate_strategies -v`
Expected: PASS

- [ ] **Step 10: Write failing test for position_size mapping**

```python
# tests/test_strategy_generator.py
def test_position_size_mapping():
    """测试仓位大小映射"""
    generator = TradingStrategyGenerator()
    
    # 测试不同置信度对应的仓位
    assert generator._determine_position_size('high', 'low') == 'large'
    assert generator._determine_position_size('medium', 'low') == 'medium'
    assert generator._determine_position_size('low', 'low') == 'small'
```

- [ ] **Step 11: Run test to verify it passes**

Run: `pytest tests/test_strategy_generator.py::test_position_size_mapping -v`
Expected: PASS

- [ ] **Step 12: Write failing test for risk_reward_ratio**

```python
# tests/test_strategy_generator.py
def test_risk_reward_ratio():
    """测试风险回报比计算"""
    generator = TradingStrategyGenerator()
    
    # 测试买入场景
    price_levels = generator._calculate_price_levels(1, 1.1570, 0.0100, 'buy')
    assert price_levels['entry_price'] == 1.1570
    assert price_levels['stop_loss'] < price_levels['entry_price']
    assert price_levels['take_profit'] > price_levels['entry_price']
    assert abs(price_levels['risk_reward_ratio'] - 1.0) < 0.1
```

- [ ] **Step 13: Run test to verify it passes**

Run: `pytest tests/test_strategy_generator.py::test_risk_reward_ratio -v`
Expected: PASS

- [ ] **Step 14: Commit**

```bash
git add ml_services/strategy_generator.py tests/test_strategy_generator.py
git commit -m "feat: implement TradingStrategyGenerator with full functionality"
```

---

## Task 5: 创建 JSONFormatter 模块

**Files:**
- Create: `ml_services/json_formatter.py`
- Test: `tests/test_json_formatter.py`

**职责:** 格式化输出为标准 JSON 格式，写入文件。

- [ ] **Step 1: Write failing test for JSONFormatter**

```python
# tests/test_json_formatter.py
import pytest
import json
from ml_services.json_formatter import JSONFormatter

def test_formatter_initialization():
    """测试 JSONFormatter 初始化"""
    formatter = JSONFormatter()
    assert formatter is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_json_formatter.py::test_formatter_initialization -v`
Expected: FAIL with "No module named 'ml_services.json_formatter'"

- [ ] **Step 3: Create JSONFormatter skeleton**

```python
# ml_services/json_formatter.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_json_formatter.py::test_formatter_initialization -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ml_services/json_formatter.py tests/test_json_formatter.py
git commit -m "feat: add JSONFormatter skeleton"
```

- [ ] **Step 6: Write failing test for format method**

```python
# tests/test_json_formatter.py
def test_format_json():
    """测试格式化 JSON"""
    formatter = JSONFormatter()
    
    # 创建测试数据
    context = {
        'pair': 'EUR',
        'current_price': 1.1570,
        'data_date': '2026-03-20'
    }
    
    llm_result = {
        'summary': '测试摘要',
        'overall_assessment': '中性',
        'key_factors': ['因素1']
    }
    
    strategies = {
        'short_term': {
            'name': '短线策略',
            'horizon': 1,
            'recommendation': 'buy',
            'confidence': 'medium',
            'entry_price': 1.1570,
            'stop_loss': 1.1470,
            'take_profit': 1.1670,
            'risk_reward_ratio': 1.0,
            'position_size': 'small',
            'reasoning': '理由'
        }
    }
    
    result = formatter.format(context, llm_result, strategies)
    
    # 验证 JSON 格式
    parsed = json.loads(result)
    assert 'metadata' in parsed
    assert parsed['metadata']['pair'] == 'EUR'
```

- [ ] **Step 7: Run test to verify it fails**

Run: `pytest tests/test_json_formatter.py::test_format_json -v`
Expected: FAIL with "JSONFormatter has no attribute 'format'"

- [ ] **Step 8: Implement format method**

```python
# ml_services/json_formatter.py
class JSONFormatter:
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
            'horizon_analysis': {
                '1': {
                    'recommendation': llm_result['horizon_recommendations']['1']['recommendation'],
                    'confidence': llm_result['horizon_recommendations']['1']['confidence'],
                    'analysis': llm_result['horizon_recommendations']['1']['reasoning'],
                    'key_points': []
                },
                '5': {
                    'recommendation': llm_result['horizon_recommendations']['5']['recommendation'],
                    'confidence': llm_result['horizon_recommendations']['5']['confidence'],
                    'analysis': llm_result['horizon_recommendations']['5']['reasoning'],
                    'key_points': []
                },
                '20': {
                    'recommendation': llm_result['horizon_recommendations']['20']['recommendation'],
                    'confidence': llm_result['horizon_recommendations']['20']['confidence'],
                    'analysis': llm_result['horizon_recommendations']['20']['reasoning'],
                    'key_points': []
                }
            }
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
            'NZD': '新西兰元/美元'
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
```

- [ ] **Step 9: Run test to verify it passes**

Run: `pytest tests/test_json_formatter.py::test_format_json -v`
Expected: PASS

- [ ] **Step 10: Write failing test for write_to_file**

```python
# tests/test_json_formatter.py
def test_write_to_file():
    """测试写入文件"""
    import os
    from pathlib import Path
    
    formatter = JSONFormatter()
    
    json_str = '{"test": "data"}'
    file_path = formatter.write_to_file(json_str, 'EUR')
    
    # 验证文件存在
    assert os.path.exists(file_path)
    
    # 验证文件内容
    with open(file_path, 'r') as f:
        content = f.read()
    
    assert json.loads(content) == {"test": "data"}
    
    # 清理
    os.remove(file_path)
```

- [ ] **Step 11: Run test to verify it passes**

Run: `pytest tests/test_json_formatter.py::test_write_to_file -v`
Expected: PASS

- [ ] **Step 12: Commit**

```bash
git add ml_services/json_formatter.py tests/test_json_formatter.py
git commit -m "feat: implement JSONFormatter with full functionality"
```

---

## Task 6: 重构 FXTradingModel 模块

**Files:**
- Modify: `ml_services/fx_trading_model.py`
- Test: `tests/test_fx_trading_model.py`

**职责:** 移除单周期预测方法，添加 predict_horizon 方法。

- [ ] **Step 1: Read current fx_trading_model.py to understand structure**

Run: `head -50 ml_services/fx_trading_model.py`
Expected: Display first 50 lines of the file

- [ ] **Step 2: Add predict_horizon method**

```python
# ml_services/fx_trading_model.py
# 在 FXTradingModel 类中添加新方法

def predict_horizon(self, pair: str, data: pd.DataFrame, horizon: int) -> dict:
    """
    预测单个周期
    
    Args:
        pair: 货币对代码
        data: 预测数据
        horizon: 预测周期（天）
        
    Returns:
        预测结果字典
    """
    self.logger.info(f"开始预测 {pair} 周期 {horizon} 天...")
    
    # 加载模型
    model_file = f"{pair}_catboost_{horizon}d.pkl"
    try:
        self.model = self.model_processor.load_model(pair, f'catboost_{horizon}d')
    except FileNotFoundError:
        self.logger.warning(f"模型 {model_file} 不存在，使用默认预测")
        return self._get_default_prediction(horizon, data)
    
    # 计算技术指标
    data = self.technical_analyzer.compute_all_indicators(data)
    
    # 创建特征
    features = self.feature_engineer.create_features(data)
    
    # 获取特征列
    exclude_cols = ['Close', 'High', 'Low', 'Open', 'Volume', 'Date']
    feature_cols = [col for col in features.columns if col not in exclude_cols]
    
    # 使用最后一行进行预测
    latest_data = features[feature_cols].iloc[-1:].copy()
    latest_data = latest_data.fillna(0)
    
    # 预测
    prediction = self.model.predict(latest_data)[0]
    probability = self.model.predict_proba(latest_data)[0][1]
    
    # 计算置信度
    confidence = self._get_confidence(probability)
    
    # 获取当前价格和目标日期
    current_price = data['Close'].iloc[-1]
    data_date = data.index[-1] if hasattr(data.index, 'to_pydatetime') else datetime.now()
    target_date = data_date + timedelta(days=horizon)
    
    result = {
        'horizon': horizon,
        'prediction': int(prediction),
        'probability': float(probability),
        'confidence': confidence,
        'target_date': target_date.strftime('%Y-%m-%d'),
        'model_file': model_file
    }
    
    self.logger.info(f"预测完成: {pair} 周期 {horizon} - {prediction} ({probability:.2%})")
    return result

def _get_default_prediction(self, horizon: int, data: pd.DataFrame) -> dict:
    """获取默认预测（当模型不可用时）"""
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
```

- [ ] **Step 3: Write test for predict_horizon**

```python
# tests/test_fx_trading_model.py
def test_predict_horizon():
    """测试单个周期预测"""
    from data_services.excel_loader import FXDataLoader
    
    model = FXTradingModel()
    loader = FXDataLoader()
    
    # 加载测试数据
    data = loader.load_pair('EUR', 'FXRate_20260320.xlsx')
    
    # 预测 1 天周期
    result = model.predict_horizon('EUR', data, 1)
    
    # 验证结果
    assert 'horizon' in result
    assert result['horizon'] == 1
    assert 'prediction' in result
    assert 'probability' in result
    assert 'confidence' in result
    assert 'target_date' in result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_fx_trading_model.py::test_predict_horizon -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ml_services/fx_trading_model.py tests/test_fx_trading_model.py
git commit -m "feat: add predict_horizon method to FXTradingModel"
```

- [ ] **Step 6: Remove single-horizon predict method (if it exists)**

Check if single predict method exists and comment it out or remove it. Keep predict_all_horizons as the main method.

- [ ] **Step 7: Commit**

```bash
git add ml_services/fx_trading_model.py
git commit -m "refactor: remove single-horizon predict method, keep multi-horizon only"
```

---

## Task 7: 重构 ComprehensiveAnalyzer 模块

**Files:**
- Modify: `comprehensive_analysis.py`
- Test: `tests/test_comprehensive_analysis.py`

**职责:** 重构为多周期核心，集成所有新模块。

- [ ] **Step 1: Read current comprehensive_analysis.py structure**

Run: `head -100 comprehensive_analysis.py`
Expected: Display first 100 lines

- [ ] **Step 2: Update imports**

```python
# comprehensive_analysis.py
from ml_services.multi_horizon_context import MultiHorizonContextBuilder
from ml_services.multi_horizon_prompt import MultiHorizonPromptBuilder
from ml_services.llm_parser import LLMAnalysisParser
from ml_services.strategy_generator import TradingStrategyGenerator
from ml_services.json_formatter import JSONFormatter
```

- [ ] **Step 3: Update ComprehensiveAnalyzer __init__**

```python
# comprehensive_analysis.py
class ComprehensiveAnalyzer:
    """综合分析器"""
    
    def __init__(self):
        self.logger = logger
        self.technical_analyzer = TechnicalAnalyzer()
        self.model = FXTradingModel()
        
        # 新增模块
        self.context_builder = MultiHorizonContextBuilder()
        self.prompt_builder = MultiHorizonPromptBuilder()
        self.llm_parser = LLMAnalysisParser()
        self.strategy_generator = TradingStrategyGenerator()
        self.json_formatter = JSONFormatter()
```

- [ ] **Step 4: Update analyze_pair method for multi-horizon**

```python
# comprehensive_analysis.py
def analyze_pair(self, pair: str, data: pd.DataFrame,
                use_llm: bool = True, llm_length: str = 'long') -> dict:
    """
    分析单个货币对（多周期）
    
    Args:
        pair: 货币对代码
        data: 数据
        use_llm: 是否使用 LLM
        llm_length: LLM 分析长度（保留用于向后兼容）
        
    Returns:
        分析结果字典
    """
    self.logger.info(f"开始分析 {pair}（多周期）...")
    
    # 1. 构建上下文
    context = self.context_builder.build(pair, data)
    
    # 2. LLM 分析
    if use_llm:
        try:
            prompt = self.prompt_builder.build(context)
            from llm_services.qwen_engine import chat_with_llm
            
            import time
            start_time = time.time()
            llm_response = chat_with_llm(prompt)
            elapsed = time.time() - start_time
            self.logger.info(f"LLM 调用耗时: {elapsed:.2f} 秒")
            
            llm_result = self.llm_parser.parse(llm_response)
        except Exception as e:
            self.logger.warning(f"LLM 分析失败: {e}，使用规则引擎")
            llm_result = self._use_rule_engine(context)
    else:
        llm_result = self._use_rule_engine(context)
    
    # 3. 生成交易方案
    strategies = self.strategy_generator.generate(llm_result, context)
    
    # 4. 格式化输出
    json_str = self.json_formatter.format(context, llm_result, strategies)
    
    # 5. 写入文件
    file_path = self.json_formatter.write_to_file(json_str, pair)
    
    # 6. 返回解析后的结果
    import json
    result = json.loads(json_str)
    
    self.logger.info(f"分析完成，结果已保存到: {file_path}")
    return result

def _use_rule_engine(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """使用规则引擎（当 LLM 不可用时）"""
    # 基于 ML 预测生成建议
    majority_trend = context['consistency_analysis']['majority_trend']
    
    if majority_trend == '上涨':
        recommendation = 'buy'
    elif majority_trend == '下跌':
        recommendation = 'sell'
    else:
        recommendation = 'hold'
    
    return {
        'summary': f"{context['pair']} {majority_trend}趋势，建议{recommendation}",
        'overall_assessment': '中性',
        'key_factors': [f"{majority_trend}趋势", "ML预测"],
        'horizon_recommendations': {
            '1': {'recommendation': recommendation, 'confidence': 'medium', 'reasoning': '规则引擎'},
            '5': {'recommendation': recommendation, 'confidence': 'medium', 'reasoning': '规则引擎'},
            '20': {'recommendation': recommendation, 'confidence': 'medium', 'reasoning': '规则引擎'}
        }
    }
```

- [ ] **Step 5: Update main function**

```python
# comprehensive_analysis.py - __main__ 部分
if __name__ == "__main__":
    import argparse
    from data_services.excel_loader import FXDataLoader
    from config import DATA_CONFIG

    parser = argparse.ArgumentParser(description="外汇综合分析")
    parser.add_argument('--pair', type=str, help='货币对代码（如 EUR、JPY 等）')
    parser.add_argument('--data_file', type=str, default=DATA_CONFIG['data_file'], help='数据文件路径')
    parser.add_argument('--no-llm', action='store_true', help='禁用大模型分析（默认启用）')

    args = parser.parse_args()

    analyzer = ComprehensiveAnalyzer()
    use_llm = not args.no_llm

    if args.pair:
        loader = FXDataLoader()
        df = loader.load_pair(args.pair, args.data_file)

        if df is None or df.empty:
            print(f"错误: 无法加载货币对 {args.pair} 的数据")
            exit(1)

        result = analyzer.analyze_pair(args.pair, df, use_llm=use_llm)

        print(f"\n=== {args.pair} 多周期分析 ===")
        print(f"数据日期: {result['metadata']['data_date']}")
        print(f"当前价格: {result['metadata']['current_price']:.4f}")
        
        print(f"\n--- ML 预测 ---")
        for horizon_name, pred in result['ml_predictions'].items():
            print(f"{horizon_name}: {pred['prediction_text']} (概率: {pred['probability']:.2%})")
        
        print(f"\n--- 交易方案 ---")
        for strategy_name, strategy in result['trading_strategies'].items():
            print(f"\n{strategy['name']}:")
            print(f"  建议: {strategy['recommendation']}")
            print(f"  置信度: {strategy['confidence']}")
            print(f"  入场价: {strategy['entry_price']:.4f}")
            print(f"  止损位: {strategy['stop_loss']:.4f}")
            print(f"  止盈位: {strategy['take_profit']:.4f}")
            print(f"  风险回报比: {strategy['risk_reward_ratio']:.2f}")
            print(f"  仓位: {strategy['position_size']}")
            print(f"  理由: {strategy['reasoning']}")
        
        if use_llm:
            print(f"\n--- LLM 分析 ---")
            print(f"摘要: {result['llm_analysis']['summary']}")
            print(f"整体评估: {result['llm_analysis']['overall_assessment']}")
            print(f"关键因素: {', '.join(result['llm_analysis']['key_factors'])}")
    else:
        # 分析所有货币对
        loader = FXDataLoader()
        all_data = loader.load_all_pairs(args.data_file)

        print(f"\n=== 所有货币对多周期分析 ===")
        print(f"分析日期: {datetime.now().strftime('%Y-%m-%d')}\n")

        for pair, df in all_data.items():
            try:
                result = analyzer.analyze_pair(pair, df, use_llm=use_llm)
                print(f"--- {pair} ---")
                print(f"一致性评分: {result['consistency_analysis']['score']:.2f}")
                print(f"多数趋势: {result['consistency_analysis']['majority_trend']}")
                print(f"建议: {[s['recommendation'] for s in result['trading_strategies'].values()]}")
                print()
            except Exception as e:
                logger.error(f"分析货币对 {pair} 失败: {e}")
                print(f"--- {pair} ---")
                print(f"错误: {e}")
                print()
```

- [ ] **Step 6: Remove --llm-length and --date parameters**

Remove `--llm-length` and `--date` from argparse as they are no longer needed.

- [ ] **Step 7: Run integration test**

Run: `pytest tests/test_comprehensive_analysis.py -v`
Expected: All tests pass

- [ ] **Step 8: Commit**

```bash
git add comprehensive_analysis.py tests/test_comprehensive_analysis.py
git commit -m "refactor: update ComprehensiveAnalyzer for multi-horizon analysis"
```

---

## Task 8: 更新 run_full_pipeline.sh 脚本

**Files:**
- Modify: `run_full_pipeline.sh`

**职责:** 简化参数，移除 --horizon 和 --all-horizons。

- [ ] **Step 1: Read current script**

Run: `cat run_full_pipeline.sh | head -100`
Expected: Display first 100 lines

- [ ] **Step 2: Remove --horizon and --all-horizons parameters**

Update the script to remove these parameters and their usage.

- [ ] **Step 3: Update help text**

Update the help text to reflect that multi-horizon is the default behavior.

- [ ] **Step 4: Test script**

Run: `bash run_full_pipeline.sh --help`
Expected: Help displays without --horizon and --all-horizons

- [ ] **Step 5: Commit**

```bash
git add run_full_pipeline.sh
git commit -m "refactor: update shell script to remove --horizon parameters"
```

---

## Task 9: 训练所有周期的模型

**Files:**
- Modify: (no file modification, just execution)

**职责:** 训练 1天、5天、20天周期的所有货币对模型。

- [ ] **Step 1: Train all models for all pairs and horizons**

```bash
# 为所有货币对训练所有周期
for pair in EUR JPY AUD GBP CAD NZD; do
    for horizon in 1 5 20; do
        echo "Training ${pair} for ${horizon} days..."
        python3 -m ml_services.fx_trading_model --mode train --pair $pair --horizon $horizon
    done
done
```

- [ ] **Step 2: Verify models exist**

Run: `ls -la data/models/`
Expected: See all model files: *_catboost_1d.pkl, *_catboost_5d.pkl, *_catboost_20d.pkl

- [ ] **Step 3: Test model predictions**

```bash
# 测试预测
python3 -m comprehensive_analysis --pair EUR --no-llm
```

Expected: Should run successfully and output multi-horizon analysis

- [ ] **Step 4: Commit**

```bash
git add data/models/
git commit -m "feat: train all multi-horizon models (1d, 5d, 20d)"
```

---

## Task 10: 集成测试和验证

**Files:**
- Test: Run all tests

**职责:** 运行完整测试套件，确保所有功能正常。

- [ ] **Step 1: Run all tests**

```bash
pytest tests/ -v --tb=short
```

Expected: All tests pass

- [ ] **Step 2: Run integration test**

```bash
pytest tests/test_integration.py -v
```

Expected: All integration tests pass

- [ ] **Step 3: Test end-to-end workflow**

```bash
# 测试完整流程
python3 -m comprehensive_analysis --pair EUR
```

Expected: Should complete successfully and output JSON file

- [ ] **Step 4: Verify JSON output**

```bash
# 检查最新生成的 JSON 文件
ls -lt data/predictions/ | head -1
cat $(ls -t data/predictions/*.json | head -1) | python3 -m json.tool
```

Expected: Valid JSON with all required fields

- [ ] **Step 5: Update progress.txt**

Update `progress.txt` with the completed features.

- [ ] **Step 6: Commit**

```bash
git add progress.txt
git commit -m "docs: update progress.txt with multi-horizon implementation"
```

---

## Task 11: 清理和优化

**Files:**
- Modify: Various files for cleanup

**职责:** 清理旧代码，优化性能。

- [ ] **Step 1: Remove any remaining single-horizon references**

Search and remove any remaining references to single-horizon prediction.

- [ ] **Step 2: Update documentation**

Update AGENTS.md and README.md to reflect multi-horizon changes.

- [ ] **Step 3: Add error handling improvements**

Enhance error handling based on design doc requirements.

- [ ] **Step 4: Commit**

```bash
git add AGENTS.md README.md
git commit -m "docs: update documentation for multi-horizon feature"
```

---

## Task 12: 最终验证和发布

**Files:**
- Test: Final verification

**职责:** 最终验证所有功能，准备发布。

- [ ] **Step 1: Run full test suite with coverage**

```bash
pytest tests/ --cov=. --cov-report=html --cov-report=term
```

Expected: All tests pass, coverage ≥ 85%

- [ ] **Step 2: Test with all currency pairs**

```bash
python3 -m comprehensive_analysis
```

Expected: All pairs analyzed successfully

- [ ] **Step 3: Verify JSON Schema compliance**

Run JSON Schema validation tests.

Expected: All schema validations pass

- [ ] **Step 4: Check for any remaining issues**

Review any warnings or errors in logs.

- [ ] **Step 5: Commit final changes**

```bash
git add .
git commit -m "feat: complete multi-horizon analysis system implementation"
```

- [ ] **Step 6: Tag release**

```bash
git tag -a v2.0.0 -m "Multi-horizon analysis system"
git push origin v2.0.0
```

---

## Success Criteria

完成所有任务后，系统应该：

1. ✅ 支持同时预测 1 天、5 天、20 天的汇率走势
2. ✅ LLM 能够生成三个周期的独立建议和分析
3. ✅ 输出格式为标准 JSON，便于控制面板读取
4. ✅ 为每个周期生成独立的交易执行方案
5. ✅ 包含完整的 36 个技术指标
6. ✅ 实现双重验证机制（LLM + ML）
7. ✅ 移除单周期预测功能，系统默认使用三个周期
8. ✅ 完善的错误处理和降级策略
9. ✅ 测试覆盖率 ≥ 85%
10. ✅ 完整分析和性能标准达标