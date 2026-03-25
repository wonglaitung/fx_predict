# 大模型集成设计 - 双重验证分析系统

**日期**: 2026-03-25
**版本**: 1.0
**状态**: 设计完成

---

## 1. 功能概述

在现有 FX Predict 系统中补充缺失的大模型分析功能，构建完整的人机协作分析系统。大模型作为核心决策者，接收完整的技术指标数据和 ML 预测结果，生成自然语言格式的完整市场分析报告和交易建议。

**核心流程：**
```
技术指标数据 (35个) → LLM 定性分析
                    ↓
ML 预测结果 → LLM 双重验证 → 生成综合建议 + 完整分析报告
                    ↓
              自然语言输出
```

---

## 2. 设计背景

### 2.1 问题发现

虽然项目已经实现了：
- ✅ 大模型 API 封装（`qwen_engine.py`）
- ✅ 技术指标引擎（35 个指标）
- ✅ CatBoost 预测模型
- ✅ 综合分析器基础功能

**但是**，在 `comprehensive_analysis.py` 中并没有真正调用大模型进行分析。根据 MVP 设计文档，`ComprehensiveAnalyzer` 类应该包含 `generate_llm_analysis` 方法，但当前实现中缺失了这一功能。

### 2.2 设计目标

1. **补全 MVP 缺失功能**：实现设计文档中要求的 LLM 分析功能
2. **双重验证机制**：大模型定性分析 + ML 定量预测，相互印证
3. **人机协作**：大模型作为最终决策者，综合所有信息给出建议
4. **灵活可控**：通过命令行参数控制 LLM 行为（启用/禁用、输出长度）

---

## 3. 核心组件设计

### 3.1 新增方法：generate_llm_analysis

在 `ComprehensiveAnalyzer` 类中新增此方法：

```python
def generate_llm_analysis(self,
                         pair: str,
                         data: pd.DataFrame,
                         ml_prediction: Dict[str, Any],
                         length: str = 'long') -> Dict[str, Any]:
    """
    调用大模型进行双重验证分析

    步骤：
    1. 提取所有技术指标的当前值
    2. 构建 prompt，包含：
       - 货币对信息
       - 完整技术指标数据（35个）
       - ML 预测结果（方向、概率、置信度）
       - 当前价格
    3. 调用 LLM 生成分析
    4. 解析 LLM 输出，提取：
       - 建议方向
       - 置信度
       - 完整分析报告（自然语言）
       - 关键因素

    Args:
        pair: 货币对代码
        data: 包含所有技术指标的数据
        ml_prediction: ML 预测结果
        length: 分析长度 ('short' | 'medium' | 'long')

    Returns:
        {
            'recommendation': 'buy/sell/hold',
            'confidence': 'high/medium/low',
            'llm_report': str,  # 完整分析报告
            'key_factors': List[str]
        }

    Raises:
        ValueError: API 密钥未配置
        requests.exceptions.RequestException: API 调用失败
    """
```

**实现要点：**

1. **确保技术指标已计算**：
   ```python
   # 确保技术指标已计算
   if 'RSI14' not in data.columns:
       data = self.technical_analyzer.compute_all_indicators(data)
   ```

2. **提取技术指标**：从 `data` 中提取所有 35 个技术指标的最新值

3. **构建 Prompt**：根据 `length` 参数选择对应的 prompt 模板（详见第 4 节）

4. **调用 LLM**：使用 `qwen_engine.chat_with_llm` 发送请求

5. **性能监控**：
   ```python
   import time
   
   start_time = time.time()
   llm_response = chat_with_llm(prompt)
   elapsed = time.time() - start_time
   self.logger.info(f"LLM 调用耗时: {elapsed:.2f} 秒")
   ```

6. **解析 LLM 输出（JSON 格式）**：
   ```python
   import json
   
   # 解析 JSON 输出
   llm_response = chat_with_llm(prompt)
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
   ```

6. **错误处理**：如果 JSON 解析失败或格式不正确，抛出明确的异常

### 3.2 修改方法：analyze_pair

修改现有方法的签名和实现：

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
        data: 汇率数据（包含技术指标）
        ml_prediction: ML 预测结果
        use_llm: 是否使用大模型分析（默认 True）
        llm_length: LLM 分析长度（默认 'long'）

    Returns:
        {
            'pair': str,
            'current_price': float,
            'ml_prediction': int,  # 0/1
            'ml_probability': float,
            'ml_confidence': str,
            'llm_recommendation': str,  # buy/sell/hold
            'llm_confidence': str,
            'llm_report': str,  # 完整分析报告
            'consistency': bool,  # LLM 建议 vs ML 预测
            'final_recommendation': str,  # 优先使用 LLM 建议
            'entry_price': float,
            'stop_loss': float,
            'take_profit': float,
            'risk_reward_ratio': float,
            'analysis_date': str
        }

    Raises:
        ValueError: LLM 调用失败且 use_llm=True
    """
```

**修改要点：**

1. 添加参数 `use_llm` 和 `llm_length`
2. 如果 `use_llm=True`，调用 `generate_llm_analysis`
3. 比较 LLM 建议和 ML 预测的一致性
4. 优先使用 LLM 建议作为 `final_recommendation`
5. 在返回结果中包含 `llm_report` 字段
6. 如果 LLM 调用失败，抛出异常（根据用户要求 B）

### 3.3 修改主函数

修改 `comprehensive_analysis.py` 的 `__main__` 部分：

**新增命令行参数：**

```python
parser.add_argument('--no-llm', action='store_true',
                   help='禁用大模型分析（默认启用）')
parser.add_argument('--llm-length', type=str,
                   choices=['short', 'medium', 'long'],
                   default='long',
                   help='大模型分析长度（默认: long）')
```

**修改调用逻辑：**

```python
use_llm = not args.no_llm
llm_length = args.llm_length

result = analyzer.analyze_pair(pair, df, ml_prediction,
                               use_llm=use_llm,
                               llm_length=llm_length)
```

**修改输出格式：**

如果 `use_llm=True`，显示 LLM 分析报告：

```python
if use_llm and 'llm_report' in result:
    print(f"\n【大模型分析报告】\n")
    print(result['llm_report'])
```

---

## 4. Prompt 设计

### 4.1 Short Prompt（50-100 字）

```
你是一个外汇交易分析师。请分析 {pair} 货币对：

当前价格：{current_price}

技术指标摘要：
{technical_indicators_summary}

ML 预测：{'上涨' if ml_pred==1 else '下跌'}，概率 {ml_prob:.2%}

请给出简短建议（50-100字）和关键理由。
```

### 4.2 Medium Prompt（200-300 字）

```
你是一个外汇交易分析师。请分析 {pair} 货币对：

当前价格：{current_price}

关键技术指标：
- RSI(14): {rsi_value}
- MACD: {macd_value}
- 趋势：{trend_description}
- 支撑/阻力：{support_resistance}

ML 预测：{'上涨' if ml_pred==1 else '下跌'}，概率 {ml_prob:.2%}，置信度：{ml_conf}

请给出市场分析（200-300字），包括：
1. 技术面分析
2. 风险提示
3. 交易建议（buy/sell/hold）
```

### 4.3 Long Prompt（500+ 字）

```
你是一个资深外汇交易分析师。请对 {pair} 货币对进行全面分析：

=== 基本信息 ===
当前价格：{current_price}
分析日期：{analysis_date}

=== 完整技术指标 ===
趋势类指标：
- SMA5: {sma5}, SMA10: {sma10}, SMA20: {sma20}, SMA50: {sma50}
- EMA5: {ema5}, EMA20: {ema20}
- MACD: {macd}, MACD_Signal: {macd_signal}, MACD_Hist: {macd_hist}
- ADX: {adx}, DI_Plus: {di_plus}, DI_Minus: {di_minus}

动量类指标：
- RSI(14): {rsi}
- K: {k}, D: {d}, J: {j}
- Williams%R: {williams_r}
- CCI: {cci}

波动类指标：
- ATR(14): {atr}
- 布林带：上轨 {bb_upper}, 中轨 {bb_middle}, 下轨 {bb_lower}
- 波动率：{volatility}

价格形态：
- 价格百分位(120日): {price_percentile}
- 乖离率：Bias_5={bias_5}, Bias_20={bias_20}
- 趋势斜率：{trend_slope}

市场环境：
- 均线排列：{ma_alignment}

=== ML 预测结果 ===
预测方向：{'上涨' if ml_pred==1 else '下跌'}
预测概率：{ml_prob:.2%}
置信度：{ml_conf}

=== 分析要求 ===

**输出格式要求（必须严格遵守）**

请以以下 JSON 格式输出（确保是有效的 JSON，不要包含任何额外文字）：
```json
{
  "recommendation": "buy/sell/hold",
  "confidence": "high/medium/low",
  "analysis": "完整分析文本（500字以上）",
  "key_factors": ["因素1", "因素2", "因素3"]
}
```

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
```

---

## 5. 数据流设计

```
┌─────────────────────────────────────────────────────────────┐
│                    数据流（双重验证）                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Excel 数据                                                 │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────┐                                        │
│  │ 技术指标引擎    │──→ 35个技术指标                       │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ├──────────────┐                                  │
│           ▼              ▼                                  │
│  ┌──────────┐    ┌──────────┐                              │
│  │指标数据   │    │ ML 模型   │                              │
│  └────┬─────┘    └────┬─────┘                              │
│       │               │                                     │
│       └───────┬───────┘                                     │
│               ▼                                             │
│        ┌─────────────┐                                     │
│        │  构建上下文  │                                     │
│        │  - 完整指标  │                                     │
│        │  - ML 预测   │                                     │
│        └──────┬──────┘                                     │
│               ▼                                             │
│        ┌─────────────┐                                     │
│        │  大模型分析  │                                     │
│        │  - 定性分析  │                                     │
│        │  - 双重验证  │                                     │
│        └──────┬──────┘                                     │
│               ▼                                             │
│        ┌─────────────┐                                     │
│        │  解析输出    │                                     │
│        │  - 建议      │                                     │
│        │  - 置信度    │                                     │
│        │  - 分析报告  │                                     │
│        └──────┬──────┘                                     │
│               ▼                                             │
│  ┌──────────────────────────────────┐                      │
│  │  综合输出                         │                      │
│  │  - LLM 建议（优先）              │                      │
│  │  - 完整分析报告（自然语言）      │                      │
│  │  - 入场/止损/止盈价格           │                      │
│  └──────────────────────────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. 错误处理

根据用户要求，如果 LLM 调用失败，抛出异常并提示用户。

```python
try:
    llm_result = self.generate_llm_analysis(pair, data, ml_prediction, llm_length)
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

---

## 7. 输出格式示例

### 7.1 命令行输出（LLM 启用）

```bash
$ python3 comprehensive_analysis.py --pair EUR

=== EUR 综合分析 ===

当前价格：1.0850

【大模型分析报告】

EUR/USD 目前处于震荡上行趋势中。从技术面看，RSI(14) 为 55.3，处于中性偏强区域，表明多头力量逐步增强。MACD 线上穿信号线，形成金叉，这是短期看涨信号。均线系统呈现多头排列（SMA5 > SMA10 > SMA20 > SMA50），支撑价格上行。

ML 模型预测未来 20 天上涨概率为 68.5%（高置信度），与技术面分析一致，增强了看涨预期。

风险方面，当前价格接近布林带上轨（1.0870），存在短期回调风险。建议严格设置止损位 1.0750（基于 2 倍 ATR）。

关键因素：
1. MACD 金叉信号
2. 均线多头排列
3. ML 预测高概率上涨
4. 接近布林带上轨的短期风险

【交易建议】
建议：BUY
入场价：1.0850
止损位：1.0750
止盈位：1.0950
风险收益比：1:1

---
ML 预测：上涨（68.5%）
LLM 建议：BUY（高置信度）
一致性：✓ 是
```

### 7.2 命令行输出（LLM 禁用）

```bash
$ python3 comprehensive_analysis.py --pair EUR --no-llm

=== EUR 综合分析 ===

当前价格：1.0850

【交易建议】
建议：BUY（基于技术信号 + ML 预测）
入场价：1.0850
止损位：1.0750
止盈位：1.0950
风险收益比：1:1

---
技术信号：BUY（强度 65）
ML 预测：上涨（68.5%）
置信度：high
推理：技术信号 BUY (强度 65)，ML预测上涨 0.68（高置信度），方向一致
```

---

## 8. 改动范围

### 8.1 修改文件

**`comprehensive_analysis.py`**

1. **导入大模型引擎**（新增）：
   ```python
   from llm_services.qwen_engine import chat_with_llm
   ```

2. **新增方法 `generate_llm_analysis`**（约 150 行）：
   - 提取技术指标数据
   - 构建 Prompt
   - 调用 LLM
   - 解析输出

3. **修改方法 `analyze_pair`**（约 50 行改动）：
   - 添加参数 `use_llm` 和 `llm_length`
   - 集成 LLM 调用
   - 更新返回结果

4. **修改主函数**（约 30 行改动）：
   - 添加命令行参数
   - 修改调用逻辑
   - 更新输出格式

**总改动量：约 230 行**

### 8.2 新增测试

**`test_comprehensive_analysis.py`**

新增测试用例：

1. `test_generate_llm_analysis_short`
2. `test_generate_llm_analysis_medium`
3. `test_generate_llm_analysis_long`
4. `test_llm_output_parsing_valid_json`
5. `test_llm_invalid_json_format`
6. `test_llm_invalid_recommendation`
7. `test_llm_invalid_confidence`
8. `test_llm_timeout`
9. `test_llm_error_handling`
10. `test_analyze_pair_with_llm`
11. `test_analyze_pair_without_llm`

**Mock 测试策略：**
- 使用 `unittest.mock` 模拟 `chat_with_llm` 返回预定义的 JSON 响应
- 避免依赖真实 API 调用，确保测试独立性和可重复性
- 测试各种边界情况：无效 JSON、无效字段、超时等

**总测试用例：约 11 个**

---

## 9. 配置要求

### 9.1 环境变量

需要设置以下环境变量（已在 `.env.example` 中）：

```bash
QWEN_API_KEY=your_api_key_here
QWEN_CHAT_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
QWEN_CHAT_MODEL=qwen-plus-2025-12-01
MAX_TOKENS=32768
```

### 9.2 依赖

所有依赖已在 `requirements.txt` 中：
- `requests>=2.31.0`（HTTP 请求）
- `python-dotenv>=1.0.0`（环境变量管理）

---

## 10. 使用示例

### 10.1 默认使用 LLM（long 长度）

```bash
python3 comprehensive_analysis.py --pair EUR
```

### 10.2 使用 medium 长度

```bash
python3 comprehensive_analysis.py --pair EUR --llm-length medium
```

### 10.3 禁用 LLM

```bash
python3 comprehensive_analysis.py --pair EUR --no-llm
```

### 10.4 分析所有货币对

```bash
python3 comprehensive_analysis.py
```

---

## 11. 成功标准

| 标准 | 验证方法 |
|------|---------|
| LLM 分析功能可用 | 运行 `--with-llm` 成功生成分析报告 |
| 输出长度符合预期 | 检查 short/medium/long 输出字数 |
| 错误处理正确 | 未配置 API 密钥时抛出明确异常 |
| 双重验证实现 | 返回结果包含 LLM 建议、ML 预测、一致性 |
| 命令行参数有效 | `--no-llm` 和 `--llm-length` 正确工作 |
| 测试通过 | 新增 7 个测试用例全部通过 |

---

## 12. 风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| **LLM 调用延迟** | 提示用户可能需要等待，支持 `--no-llm` 禁用 |
| **API 调用失败** | 提供明确的错误信息，建议用户检查配置 |
| **LLM 输出解析失败** | 设计灵活的解析逻辑，支持多种输出格式 |
| **成本问题** | 在文档中说明 API 调用可能产生费用 |

---

## 13. 后续优化建议

### 13.1 短期优化

1. **添加 LLM 输出缓存**：相同分析结果缓存，减少 API 调用
2. **优化 Prompt**：根据实际使用反馈调整 prompt 模板
3. **添加更多输出格式**：支持 JSON、Markdown 等格式

### 13.2 长期优化

1. **支持更多 LLM**：扩展支持其他大模型（如 GPT-4）
2. **历史分析对比**：保存历史分析，支持对比和复盘
3. **个性化配置**：允许用户自定义 prompt 和输出格式

---

**文档结束**