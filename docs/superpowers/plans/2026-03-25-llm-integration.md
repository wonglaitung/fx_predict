# 大模型集成实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 FX Predict 系统中实现大模型分析功能，构建双重验证的人机协作分析系统

**Architecture:** 大模型作为核心决策者，接收完整的技术指标数据和 ML 预测结果，生成自然语言格式的完整市场分析报告和交易建议。通过 JSON 格式确保结构化输出，支持三种分析长度（short/medium/long）。

**Tech Stack:** Python 3.10+, Pandas, Requests, JSON, CatBoost, 通义千问 API

---

## 文件结构映射

**修改文件：**
1. `comprehensive_analysis.py` - 主要实现文件（约 230 行改动）
   - 新增 `generate_llm_analysis` 方法
   - 修改 `analyze_pair` 方法签名和实现
   - 修改 `__main__` 函数的命令行参数和输出逻辑

2. `tests/test_comprehensive_analysis.py` - 测试文件
   - 新增 11 个测试用例
   - 使用 Mock 模拟 LLM 响应

**依赖文件（无需修改）：**
- `llm_services/qwen_engine.py` - 已存在，提供 `chat_with_llm` 接口
- `data_services/technical_analysis.py` - 已存在，提供技术指标计算
- `config.py` - 已存在，提供配置管理

---

## Task 1: 添加 LLM 导入和基础方法签名

**Files:**
- Modify: `comprehensive_analysis.py:1-10`
- Test: `tests/test_comprehensive_analysis.py`

- [ ] **Step 1: 在文件顶部添加 LLM 导入**

```python
# 在现有导入后添加
import json
import time
from llm_services.qwen_engine import chat_with_llm
```

- [ ] **Step 2: 添加 `generate_llm_analysis` 方法签名**

在 `ComprehensiveAnalyzer` 类中，`analyze_pair` 方法之前添加：

```python
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
```

- [ ] **Step 3: 运行现有测试确保没有破坏**

Run: `pytest tests/test_comprehensive_analysis.py -v`
Expected: 所有现有测试通过

- [ ] **Step 4: 提交**

```bash
git add comprehensive_analysis.py
git commit -m "feat: add LLM integration method signature"
```

---

## Task 2: 实现技术指标确保逻辑

**Files:**
- Modify: `comprehensive_analysis.py:generate_llm_analysis`
- Test: `tests/test_comprehensive_analysis.py`

- [ ] **Step 1: 编写测试 - 确保技术指标已计算**

```python
def test_generate_llm_analysis_ensures_indicators():
    """测试 generate_llm_analysis 确保技术指标已计算"""
    analyzer = ComprehensiveAnalyzer()
    
    # 创建不含技术指标的测试数据
    data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=100),
        'Open': [1.0] * 100,
        'High': [1.01] * 100,
        'Low': [0.99] * 100,
        'Close': [1.0] * 100,
        'Volume': [1000000] * 100
    })
    
    ml_prediction = {
        'prediction': 1,
        'probability': 0.65,
        'confidence': 'high'
    }
    
    # Mock chat_with_llm
    from unittest.mock import patch
    
    mock_response = json.dumps({
        'recommendation': 'buy',
        'confidence': 'high',
        'analysis': 'test analysis',
        'key_factors': ['factor1', 'factor2']
    })
    
    with patch('llm_services.qwen_engine.chat_with_llm', return_value=mock_response):
        result = analyzer.generate_llm_analysis('EUR', data, ml_prediction)
    
    # 验证技术指标已被计算
    assert 'RSI14' in data.columns
    assert result['recommendation'] == 'buy'
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_comprehensive_analysis.py::test_generate_llm_analysis_ensures_indicators -v`
Expected: FAIL (技术指标未被计算)

- [ ] **Step 3: 实现技术指标确保逻辑**

在 `generate_llm_analysis` 方法开头添加：

```python
def generate_llm_analysis(self,
                         pair: str,
                         data: pd.DataFrame,
                         ml_prediction: Dict[str, Any],
                         length: str = 'long') -> Dict[str, Any]:
    """
    调用大模型进行双重验证分析
    """
    # 确保技术指标已计算
    if 'RSI14' not in data.columns:
        data = self.technical_analyzer.compute_all_indicators(data)
    
    # 暂时返回空字典
    return {}
```

- [ ] **Step 4: 运行测试验证部分通过**

Run: `pytest tests/test_comprehensive_analysis.py::test_generate_llm_analysis_ensures_indicators -v`
Expected: PASS (技术指标已计算，但返回空字典)

- [ ] **Step 5: 提交**

```bash
git add comprehensive_analysis.py tests/test_comprehensive_analysis.py
git commit -m "feat: ensure technical indicators are computed before LLM analysis"
```

---

## Task 3: 实现 Prompt 构建逻辑

**Files:**
- Modify: `comprehensive_analysis.py:generate_llm_analysis`
- Test: `tests/test_comprehensive_analysis.py`

- [ ] **Step 1: 添加辅助方法 - 构建 Prompt**

在 `ComprehensiveAnalyzer` 类中添加私有方法：

```python
def _build_llm_prompt(self,
                     pair: str,
                     data: pd.DataFrame,
                     ml_prediction: Dict[str, Any],
                     length: str) -> str:
    """
    构建 LLM 分析的 Prompt
    
    Args:
        pair: 货币对代码
        data: 包含技术指标的数据
        ml_prediction: ML 预测结果
        length: 分析长度 ('short' | 'medium' | 'long')
    
    Returns:
        Prompt 字符串
    """
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
        # 构建关键技术指标摘要
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
        # 构建完整技术指标数据
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
        
        # 构建 indicators 文本
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
```

- [ ] **Step 2: 编写测试 - Prompt 构建**

```python
def test_build_llm_prompt_short():
    """测试构建 short 长度的 Prompt"""
    analyzer = ComprehensiveAnalyzer()
    
    data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=100),
        'Close': [1.0] * 100
    })
    
    ml_prediction = {
        'prediction': 1,
        'probability': 0.65,
        'confidence': 'high'
    }
    
    prompt = analyzer._build_llm_prompt('EUR', data, ml_prediction, 'short')
    
    # 验证关键内容
    assert 'EUR' in prompt
    assert '1.0000' in prompt
    assert '上涨' in prompt
    assert '65.00%' in prompt
    assert 'JSON 格式' in prompt
    assert 'recommendation' in prompt
```

- [ ] **Step 3: 运行测试验证通过**

Run: `pytest tests/test_comprehensive_analysis.py::test_build_llm_prompt_short -v`
Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add comprehensive_analysis.py tests/test_comprehensive_analysis.py
git commit -m "feat: add prompt building logic for LLM analysis"
```

---

## Task 4: 实现 LLM 调用和性能监控

**Files:**
- Modify: `comprehensive_analysis.py:generate_llm_analysis`
- Test: `tests/test_comprehensive_analysis.py`

- [ ] **Step 1: 编写测试 - LLM 调用和性能监控**

```python
def test_generate_llm_analysis_with_performance_monitoring():
    """测试 LLM 调用和性能监控"""
    analyzer = ComprehensiveAnalyzer()
    
    data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=100),
        'Open': [1.0] * 100,
        'High': [1.01] * 100,
        'Low': [0.99] * 100,
        'Close': [1.0] * 100,
        'RSI14': [50.0] * 100,
        'MACD': [0.001] * 100,
        'MACD_Signal': [0.0005] * 100,
        'MACD_Hist': [0.0005] * 100,
        'ATR14': [0.01] * 100,
        'BB_Upper': [1.02] * 100,
        'BB_Middle': [1.0] * 100,
        'BB_Lower': [0.98] * 100,
        'Price_Percentile_120': [50.0] * 100,
        'Bias_5': [0.0] * 100,
        'Bias_20': [0.0] * 100,
        'Trend_Slope_20': [0.0001] * 100,
        'MA_Alignment': [1.0] * 100,
        'K': [50.0] * 100,
        'D': [50.0] * 100,
        'J': [50.0] * 100,
        'WilliamsR_14': [-50.0] * 100,
        'CCI20': [0.0] * 100,
        'Volatility_20d': [0.01] * 100,
        'SMA5': [1.0] * 100,
        'SMA10': [1.0] * 100,
        'SMA20': [1.0] * 100,
        'SMA50': [1.0] * 100,
        'EMA5': [1.0] * 100,
        'EMA20': [1.0] * 100,
        'DI_Plus': [20.0] * 100,
        'DI_Minus': [15.0] * 100,
        'ADX': [25.0] * 100,
        'Volume': [1000000] * 100
    })
    
    ml_prediction = {
        'prediction': 1,
        'probability': 0.65,
        'confidence': 'high'
    }
    
    # Mock chat_with_llm
    mock_response = json.dumps({
        'recommendation': 'buy',
        'confidence': 'high',
        'analysis': '这是一个完整的市场分析报告...',
        'key_factors': ['因素1', '因素2', '因素3']
    })
    
    from unittest.mock import patch, MagicMock
    
    with patch('llm_services.qwen_engine.chat_with_llm', return_value=mock_response):
        with patch('time.time', side_effect=[0, 2.5]):  # 模拟 2.5 秒耗时
            result = analyzer.generate_llm_analysis('EUR', data, ml_prediction, 'long')
    
    # 验证结果
    assert result['recommendation'] == 'buy'
    assert result['confidence'] == 'high'
    assert 'analysis' in result
    assert 'key_factors' in result
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_comprehensive_analysis.py::test_generate_llm_analysis_with_performance_monitoring -v`
Expected: FAIL (LLM 调用和性能监控未实现)

- [ ] **Step 3: 实现 LLM 调用和性能监控**

在 `generate_llm_analysis` 方法中添加：

```python
def generate_llm_analysis(self,
                         pair: str,
                         data: pd.DataFrame,
                         ml_prediction: Dict[str, Any],
                         length: str = 'long') -> Dict[str, Any]:
    """
    调用大模型进行双重验证分析
    """
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
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_comprehensive_analysis.py::test_generate_llm_analysis_with_performance_monitoring -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add comprehensive_analysis.py tests/test_comprehensive_analysis.py
git commit -m "feat: implement LLM calling with performance monitoring"
```

---

## Task 5: 添加错误处理

**Files:**
- Modify: `comprehensive_analysis.py:generate_llm_analysis`
- Test: `tests/test_comprehensive_analysis.py`

- [ ] **Step 1: 编写测试 - API 密钥未配置**

```python
def test_generate_llm_analysis_no_api_key():
    """测试 API 密钥未配置"""
    analyzer = ComprehensiveAnalyzer()
    
    data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=100),
        'RSI14': [50.0] * 100,
        'Close': [1.0] * 100
    })
    
    ml_prediction = {
        'prediction': 1,
        'probability': 0.65,
        'confidence': 'high'
    }
    
    # Mock chat_with_llm 抛出 ValueError
    from unittest.mock import patch
    
    with patch('llm_services.qwen_engine.chat_with_llm', 
               side_effect=ValueError("QWEN_API_KEY 环境变量未设置")):
        with pytest.raises(ValueError) as exc_info:
            analyzer.generate_llm_analysis('EUR', data, ml_prediction)
    
    assert "大模型分析失败" in str(exc_info.value)
```

- [ ] **Step 2: 编写测试 - JSON 解析错误**

```python
def test_generate_llm_analysis_invalid_json():
    """测试 JSON 解析错误"""
    analyzer = ComprehensiveAnalyzer()
    
    data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=100),
        'RSI14': [50.0] * 100,
        'Close': [1.0] * 100
    })
    
    ml_prediction = {
        'prediction': 1,
        'probability': 0.65,
        'confidence': 'high'
    }
    
    # Mock chat_with_llm 返回无效 JSON
    from unittest.mock import patch
    
    with patch('llm_services.qwen_engine.chat_with_llm', return_value="这不是有效的 JSON"):
        with pytest.raises(ValueError) as exc_info:
            analyzer.generate_llm_analysis('EUR', data, ml_prediction)
    
    assert "JSON 格式错误" in str(exc_info.value)
```

- [ ] **Step 3: 编写测试 - 无效 recommendation**

```python
def test_generate_llm_analysis_invalid_recommendation():
    """测试无效的 recommendation"""
    analyzer = ComprehensiveAnalyzer()
    
    data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=100),
        'RSI14': [50.0] * 100,
        'Close': [1.0] * 100
    })
    
    ml_prediction = {
        'prediction': 1,
        'probability': 0.65,
        'confidence': 'high'
    }
    
    # Mock chat_with_llm 返回无效 recommendation
    mock_response = json.dumps({
        'recommendation': 'invalid',
        'confidence': 'high',
        'analysis': 'test',
        'key_factors': []
    })
    
    from unittest.mock import patch
    
    with patch('llm_services.qwen_engine.chat_with_llm', return_value=mock_response):
        with pytest.raises(ValueError) as exc_info:
            analyzer.generate_llm_analysis('EUR', data, ml_prediction)
    
    assert "无效的 recommendation" in str(exc_info.value)
```

- [ ] **Step 4: 运行测试验证失败**

Run: `pytest tests/test_comprehensive_analysis.py::test_generate_llm_analysis_no_api_key -v`
Run: `pytest tests/test_comprehensive_analysis.py::test_generate_llm_analysis_invalid_json -v`
Run: `pytest tests/test_comprehensive_analysis.py::test_generate_llm_analysis_invalid_recommendation -v`
Expected: FAIL (错误处理未实现)

- [ ] **Step 5: 实现错误处理**

在 `generate_llm_analysis` 方法中添加 try-except 包装：

```python
def generate_llm_analysis(self,
                         pair: str,
                         data: pd.DataFrame,
                         ml_prediction: Dict[str, Any],
                         length: str = 'long') -> Dict[str, Any]:
    """
    调用大模型进行双重验证分析
    """
    # 确保技术指标已计算
    if 'RSI14' not in data.columns:
        data = self.technical_analyzer.compute_all_indicators(data)
    
    try:
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
        # API 密钥未配置或 LLM 输出格式错误
        raise ValueError(
            f"大模型分析失败：{str(e)}\n"
            f"请确保 QWEN_API_KEY 环境变量已设置，或使用 --no-llm 参数禁用大模型分析"
        )
    except json.JSONDecodeError as e:
        # JSON 解析失败
        raise ValueError(
            f"大模型输出解析失败（JSON 格式错误）：{str(e)}\n"
            f"LLM 可能返回了非 JSON 格式的响应，请检查或重试"
        )
    except requests.exceptions.RequestException as e:
        # API 调用失败（包括超时）
        raise RuntimeError(
            f"大模型 API 调用失败：{str(e)}\n"
            f"请检查网络连接或稍后重试"
        )
```

- [ ] **Step 6: 运行测试验证通过**

Run: `pytest tests/test_comprehensive_analysis.py::test_generate_llm_analysis_no_api_key -v`
Run: `pytest tests/test_comprehensive_analysis.py::test_generate_llm_analysis_invalid_json -v`
Run: `pytest tests/test_comprehensive_analysis.py::test_generate_llm_analysis_invalid_recommendation -v`
Expected: PASS

- [ ] **Step 7: 提交**

```bash
git add comprehensive_analysis.py tests/test_comprehensive_analysis.py
git commit -m "feat: add comprehensive error handling for LLM integration"
```

---

## Task 6: 修改 analyze_pair 方法签名和实现

**Files:**
- Modify: `comprehensive_analysis.py:analyze_pair`
- Test: `tests/test_comprehensive_analysis.py`

- [ ] **Step 1: 编写测试 - analyze_pair 带 LLM 参数**

```python
def test_analyze_pair_with_llm():
    """测试 analyze_pair 使用 LLM 分析"""
    analyzer = ComprehensiveAnalyzer()
    
    data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=100),
        'RSI14': [50.0] * 100,
        'Close': [1.0] * 100,
        'Open': [1.0] * 100,
        'High': [1.01] * 100,
        'Low': [0.99] * 100,
        'ATR14': [0.01] * 100
    })
    
    ml_prediction = {
        'prediction': 1,
        'probability': 0.65,
        'confidence': 'high'
    }
    
    # Mock generate_llm_analysis
    mock_llm_result = {
        'recommendation': 'buy',
        'confidence': 'high',
        'llm_report': '完整的市场分析报告...',
        'key_factors': ['因素1', '因素2']
    }
    
    from unittest.mock import patch
    
    with patch.object(analyzer, 'generate_llm_analysis', return_value=mock_llm_result):
        result = analyzer.analyze_pair('EUR', data, ml_prediction, use_llm=True)
    
    # 验证返回结果包含 LLM 信息
    assert 'llm_recommendation' in result
    assert 'llm_confidence' in result
    assert 'llm_report' in result
    assert result['llm_recommendation'] == 'buy'
    assert result['final_recommendation'] == 'buy'
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_comprehensive_analysis.py::test_analyze_pair_with_llm -v`
Expected: FAIL (方法签名未修改)

- [ ] **Step 3: 修改 analyze_pair 方法签名**

```python
def analyze_pair(self,
                pair: str,
                data: pd.DataFrame,
                ml_prediction: Dict[str, Any],
                use_llm: bool = True,
                llm_length: str = 'long') -> Dict[str, Any]:
    """
    分析单个货币对
    
    Args:
        pair: 货币对代码
        data: 汇率数据
        ml_prediction: ML 预测结果
        use_llm: 是否使用大模型分析（默认 True）
        llm_length: LLM 分析长度（默认 'long'）
    
    Returns:
        综合分析结果
    """
```

- [ ] **Step 4: 实现 LLM 集成逻辑**

在 `analyze_pair` 方法的 `_generate_recommendation` 之前添加：

```python
# 1. 生成技术信号
technical_signal = self._generate_technical_signal(data)

# 2. 如果启用 LLM，调用 LLM 分析
llm_result = None
if use_llm:
    llm_result = self.generate_llm_analysis(pair, data, ml_prediction, llm_length)

# 3. 验证信号（应用硬性约束）
validated_signal = self._validate_signals(
    technical_signal, ml_prediction
)

# 4. 生成综合建议
recommendation = self._generate_recommendation(
    pair, data, technical_signal, ml_prediction, validated_signal, llm_result
)
```

- [ ] **Step 5: 修改 _generate_recommendation 方法签名和实现**

```python
def _generate_recommendation(self, pair: str, data: pd.DataFrame,
                            technical_signal: Dict[str, Any],
                            ml_prediction: Dict[str, Any],
                            validated_signal: Dict[str, Any],
                            llm_result: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    生成综合建议
    
    Args:
        pair: 货币对代码
        data: 汇率数据
        technical_signal: 技术信号
        ml_prediction: ML 预测
        validated_signal: 验证后的信号
        llm_result: LLM 分析结果（可选）
    
    Returns:
        综合建议字典
    """
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
```

- [ ] **Step 6: 运行测试验证通过**

Run: `pytest tests/test_comprehensive_analysis.py::test_analyze_pair_with_llm -v`
Expected: PASS

- [ ] **Step 7: 提交**

```bash
git add comprehensive_analysis.py tests/test_comprehensive_analysis.py
git commit -m "feat: integrate LLM analysis into analyze_pair method"
```

---

## Task 7: 修改主函数添加命令行参数

**Files:**
- Modify: `comprehensive_analysis.py:__main__`
- Test: 手动测试

- [ ] **Step 1: 添加命令行参数**

在 `__main__` 函数的参数解析部分添加：

```python
parser.add_argument('--no-llm', action='store_true',
                   help='禁用大模型分析（默认启用）')
parser.add_argument('--llm-length', type=str,
                   choices=['short', 'medium', 'long'],
                   default='long',
                   help='大模型分析长度（默认: long）')
```

- [ ] **Step 2: 修改调用逻辑**

在 `if args.pair:` 部分的调用中添加参数：

```python
use_llm = not args.no_llm
llm_length = args.llm_length

result = analyzer.analyze_pair(pair, df, ml_prediction,
                               use_llm=use_llm,
                               llm_length=llm_length)
```

在 `else:` 部分也添加同样的参数传递。

- [ ] **Step 3: 修改输出逻辑**

在输出部分添加 LLM 分析报告显示：

```python
if use_llm and 'llm_report' in result and result['llm_report']:
    print(f"\n【大模型分析报告】\n")
    print(result['llm_report'])
    print(f"\n关键因素：{', '.join(result['key_factors'] or [])}")
```

- [ ] **Step 4: 手动测试**

Run: `python3 comprehensive_analysis.py --pair EUR --no-llm`
Expected: 成功运行，不显示 LLM 分析报告

Run: `python3 comprehensive_analysis.py --pair EUR --llm-length short`
Expected: 成功运行，显示 LLM 分析报告（short 长度）

- [ ] **Step 5: 提交**

```bash
git add comprehensive_analysis.py
git commit -m "feat: add command line arguments for LLM control"
```

---

## Task 8: 添加更多测试用例

**Files:**
- Modify: `tests/test_comprehensive_analysis.py`

- [ ] **Step 1: 添加测试 - 不同长度**

```python
def test_generate_llm_analysis_short():
    """测试 short 长度分析"""
    analyzer = ComprehensiveAnalyzer()
    
    data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=100),
        'RSI14': [50.0] * 100,
        'Close': [1.0] * 100
    })
    
    ml_prediction = {
        'prediction': 1,
        'probability': 0.65,
        'confidence': 'high'
    }
    
    mock_response = json.dumps({
        'recommendation': 'buy',
        'confidence': 'high',
        'analysis': '简短分析...',
        'key_factors': []
    })
    
    from unittest.mock import patch
    
    with patch('llm_services.qwen_engine.chat_with_llm', return_value=mock_response):
        result = analyzer.generate_llm_analysis('EUR', data, ml_prediction, 'short')
    
    assert result['recommendation'] == 'buy'
    # 验证分析长度在 50-100 字之间
    assert 50 <= len(result['llm_report']) <= 100


def test_generate_llm_analysis_medium():
    """测试 medium 长度分析"""
    analyzer = ComprehensiveAnalyzer()
    
    data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=100),
        'RSI14': [50.0] * 100,
        'Close': [1.0] * 100
    })
    
    ml_prediction = {
        'prediction': 1,
        'probability': 0.65,
        'confidence': 'high'
    }
    
    mock_response = json.dumps({
        'recommendation': 'buy',
        'confidence': 'high',
        'analysis': '中等长度分析...',
        'key_factors': ['因素1']
    })
    
    from unittest.mock import patch
    
    with patch('llm_services.qwen_engine.chat_with_llm', return_value=mock_response):
        result = analyzer.generate_llm_analysis('EUR', data, ml_prediction, 'medium')
    
    assert result['recommendation'] == 'buy'
```

- [ ] **Step 2: 添加测试 - 无效 confidence**

```python
def test_generate_llm_analysis_invalid_confidence():
    """测试无效的 confidence"""
    analyzer = ComprehensiveAnalyzer()
    
    data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=100),
        'RSI14': [50.0] * 100,
        'Close': [1.0] * 100
    })
    
    ml_prediction = {
        'prediction': 1,
        'probability': 0.65,
        'confidence': 'high'
    }
    
    mock_response = json.dumps({
        'recommendation': 'buy',
        'confidence': 'invalid',
        'analysis': 'test',
        'key_factors': []
    })
    
    from unittest.mock import patch
    
    with patch('llm_services.qwen_engine.chat_with_llm', return_value=mock_response):
        with pytest.raises(ValueError) as exc_info:
            analyzer.generate_llm_analysis('EUR', data, ml_prediction)
    
    assert "无效的 confidence" in str(exc_info.value)
```

- [ ] **Step 3: 添加测试 - 超时**

```python
def test_llm_timeout():
    """测试 LLM 超时"""
    analyzer = ComprehensiveAnalyzer()
    
    data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=100),
        'RSI14': [50.0] * 100,
        'Close': [1.0] * 100
    })
    
    ml_prediction = {
        'prediction': 1,
        'probability': 0.65,
        'confidence': 'high'
    }
    
    from unittest.mock import patch
    import requests
    
    with patch('llm_services.qwen_engine.chat_with_llm',
               side_effect=requests.exceptions.Timeout("Connection timeout")):
        with pytest.raises(RuntimeError) as exc_info:
            analyzer.generate_llm_analysis('EUR', data, ml_prediction)
    
    assert "API 调用失败" in str(exc_info.value)
```

- [ ] **Step 4: 运行所有新测试**

Run: `pytest tests/test_comprehensive_analysis.py::test_generate_llm_analysis_short -v`
Run: `pytest tests/test_comprehensive_analysis.py::test_generate_llm_analysis_medium -v`
Run: `pytest tests/test_comprehensive_analysis.py::test_generate_llm_analysis_invalid_confidence -v`
Run: `pytest tests/test_comprehensive_analysis.py::test_llm_timeout -v`
Expected: PASS

- [ ] **Step 5: 运行所有测试确保没有破坏**

Run: `pytest tests/test_comprehensive_analysis.py -v`
Expected: 所有测试通过

- [ ] **Step 6: 提交**

```bash
git add tests/test_comprehensive_analysis.py
git commit -m "test: add comprehensive test cases for LLM integration"
```

---

## Task 9: 运行完整测试套件

**Files:**
- Test: 所有测试文件

- [ ] **Step 1: 运行所有测试**

Run: `pytest tests/ -v`
Expected: 所有测试通过

- [ ] **Step 2: 运行测试覆盖率**

Run: `pytest tests/ --cov=. --cov-report=term`
Expected: 覆盖率保持在 85% 以上

- [ ] **Step 3: 手动端到端测试**

Run: `python3 comprehensive_analysis.py --pair EUR --llm-length long`
Expected: 成功显示完整的 LLM 分析报告

Run: `python3 comprehensive_analysis.py --no-llm`
Expected: 成功运行，不显示 LLM 分析报告

- [ ] **Step 4: 提交最终版本**

```bash
git add .
git commit -m "feat: complete LLM integration with comprehensive testing"
```

---

## Task 10: 更新文档

**Files:**
- Modify: `progress.txt`
- Modify: `AGENTS.md`（可选）

- [ ] **Step 1: 更新 progress.txt**

在进度文件中添加：

```markdown
## 最后更新

- 日期：2026-03-25
- 更新者：iFlow CLI
- 更新内容：
  - **实现大模型集成功能**：添加 `generate_llm_analysis` 方法
  - **双重验证机制**：大模型定性分析 + ML 定量预测
  - **JSON 输出格式**：确保结构化输出和解析
  - **性能监控**：记录 LLM 调用耗时
  - **错误处理**：完善的异常处理和用户提示
  - **命令行参数**：`--no-llm` 和 `--llm-length`
  - **测试覆盖**：新增 11 个测试用例
```

- [ ] **Step 2: 更新 AGENTS.md（可选）**

在功能列表中添加：

```markdown
### 核心功能

- **大模型集成** ✅
  - 通义千问 API 集成
  - 双重验证分析（技术指标 + ML 预测）
  - 自然语言市场分析报告
  - 可配置分析长度（short/medium/long）
  - 完善的错误处理
```

- [ ] **Step 3: 提交文档更新**

```bash
git add progress.txt AGENTS.md
git commit -m "docs: update documentation for LLM integration"
```

---

## Task 11: 最终验证和清理

**Files:**
- All

- [ ] **Step 1: 检查所有未提交的更改**

Run: `git status`
Expected: 没有未提交的更改

- [ ] **Step 2: 运行完整测试套件**

Run: `pytest tests/ -v --tb=short`
Expected: 所有测试通过

- [ ] **Step 3: 检查代码风格**

Run: `python3 -m flake8 comprehensive_analysis.py`（如果安装了 flake8）
Expected: 没有风格问题

- [ ] **Step 4: 手动验证完整工作流**

```bash
# 1. 训练模型（如果需要）
python3 ml_services/fx_trading_model.py --mode train --pair EUR

# 2. 运行综合分析（带 LLM）
python3 comprehensive_analysis.py --pair EUR --llm-length long

# 3. 运行综合分析（不带 LLM）
python3 comprehensive_analysis.py --pair EUR --no-llm

# 4. 分析所有货币对
python3 comprehensive_analysis.py
```

Expected: 所有命令成功执行

- [ ] **Step 5: 创建最终提交**

```bash
git add .
git commit -m "feat: LLM integration complete - dual verification analysis system"
```

---

## 实施完成检查清单

- [ ] 所有 11 个任务完成
- [ ] 所有测试通过
- [ ] 代码覆盖率 ≥ 85%
- [ ] 手动端到端测试通过
- [ ] 文档已更新
- [ ] 没有未提交的更改
- [ ] 功能符合设计文档要求

---

**预计总耗时：** 2-3 小时

**关键里程碑：**
1. Task 5 完成：核心功能实现
2. Task 7 完成：命令行接口就绪
3. Task 9 完成：测试覆盖完整
4. Task 11 完成：功能验证通过