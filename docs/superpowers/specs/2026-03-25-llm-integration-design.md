# 大模型集成设计文档

**日期**: 2026-03-25
**版本**: 1.0
**状态**: 设计中

---

## 1. 概述

### 1.1 目标

在现有的综合分析系统中集成大模型（通义千问），为外汇交易建议提供深度分析和解释。

### 1.2 范围

- 在 `ComprehensiveAnalyzer` 类中添加大模型集成功能
- 支持自动集成和显式调用两种方式
- 生成包含市场环境、建议理由、风险提示的分析报告

### 1.3 约束

- 大模型调用失败时抛出异常
- 仅传递关键指标摘要作为上下文
- 返回结果中添加 `llm_analysis` 字段

---

## 2. 架构设计

### 2.1 组件结构

```
ComprehensiveAnalyzer
├── analyze_pair()               # 现有方法（扩展）
├── analyze_with_llm()           # 新增：显式调用大模型
└── _generate_llm_analysis()     # 新增：私有方法
```

### 2.2 方法签名

```python
def analyze_pair(self, pair: str, data: pd.DataFrame,
                ml_prediction: dict,
                enable_llm: bool = True) -> dict:
    """
    分析单个货币对
    
    Args:
        pair: 货币对代码
        data: 汇率数据
        ml_prediction: ML 预测结果
        enable_llm: 是否启用大模型分析（默认 True）
    
    Returns:
        综合分析结果字典（包含 llm_analysis 字段，如果 enable_llm=True）
    
    Raises:
        Exception: 当 enable_llm=True 且大模型调用失败时抛出异常
    """
    pass

def analyze_with_llm(self, pair: str, data: pd.DataFrame,
                     ml_prediction: dict,
                     technical_signal: dict) -> str:
    """
    单独调用大模型生成分析报告
    
    Args:
        pair: 货币对代码
        data: 汇率数据
        ml_prediction: ML 预测结果
        technical_signal: 技术信号
    
    Returns:
        大模型分析报告文本
    
    Raises:
        Exception: 大模型调用失败时抛出异常
    """
    pass

def _generate_llm_analysis(self, pair: str, data: pd.DataFrame,
                          ml_prediction: dict,
                          technical_signal: dict,
                          validated_signal: dict) -> str:
    """
    生成大模型分析报告（私有方法）
    
    Args:
        pair: 货币对代码
        data: 汇率数据
        ml_prediction: ML 预测结果
        technical_signal: 技术信号
        validated_signal: 验证后的信号
    
    Returns:
        分析报告文本
    
    Raises:
        Exception: 大模型调用失败时抛出异常
    """
    pass
```

---

## 3. 数据流设计

### 3.1 主流程（analyze_pair）

```
analyze_pair()
  ├─ 技术信号生成
  ├─ ML 预测整合
  ├─ 信号协同验证
  ├─ [enable_llm=True] 大模型分析
  │   └─ _generate_llm_analysis()
  │       ├─ 构建上下文
  │       ├─ 调用 chat_with_llm()
  │       └─ 返回分析报告
  └─ 综合建议生成
```

### 3.2 独立流程（analyze_with_llm）

```
analyze_with_llm()
  └─ _generate_llm_analysis()
      ├─ 构建上下文
      ├─ 调用 chat_with_llm()
      └─ 返回分析报告
```

---

## 4. 上下文构建

### 4.1 关键指标摘要

传递给大模型的上下文包括：

| 类别 | 指标 | 说明 |
|------|------|------|
| 基础信息 | 货币对、当前价格、日期 | 基本交易信息 |
| 技术信号 | RSI、均线交叉、信号强度 | 技术面分析 |
| ML 预测 | 方向（上涨/下跌）、概率、置信度 | 模型预测 |
| 交易建议 | 买入/卖出/观望 | 最终建议 |
| 风险管理 | 止损位、止盈位、风险收益比 | 风险控制 |

### 4.2 Prompt 模板

```python
prompt = f"""
请分析 {pair} 货币对的交易机会：

**市场环境：**
- 当前价格：{current_price}
- 交易日期：{analysis_date}
- 目标日期：{target_date}

**技术分析：**
- RSI：{rsi_value}（{rsi_status}）
- 均线排列：{ma_alignment}
- 技术信号：{technical_signal}（强度：{strength}/100）

**机器学习预测：**
- 预测方向：{'上涨' if prediction == 1 else '下跌'}
- 上涨概率：{probability:.2%}
- 模型置信度：{confidence}

**交易建议：**
- 建议操作：{recommendation.upper()}
- 入场价格：{entry_price:.4f}
- 止损位置：{stop_loss:.4f}
- 止盈位置：{take_profit:.4f}
- 风险收益比：1:{risk_reward:.2f}

**请提供：**
1. 市场环境分析（趋势、波动、关键支撑/阻力位）
2. 支持该交易建议的技术面和基本面理由
3. 潜在风险提示和注意事项
4. 仓位管理建议（如适用）

请保持分析客观、专业，避免过度乐观或悲观的情绪化表述。
"""
```

---

## 5. 错误处理

### 5.1 异常类型

| 异常 | 原因 | 处理方式 |
|------|------|---------|
| `ValueError` | API 密钥未配置 | 抛出异常，提示用户配置 QWEN_API_KEY |
| `requests.exceptions.Timeout` | API 调用超时 | 记录日志，抛出异常 |
| `requests.exceptions.HTTPError` | HTTP 错误（4xx/5xx） | 记录日志，抛出异常 |
| `Exception` | 其他未知错误 | 记录日志，抛出异常 |

### 5.2 日志记录

```python
import logging

logger = logging.getLogger(__name__)

# 成功时
logger.info(f"大模型分析成功: {pair}")

# 失败时
logger.error(f"大模型分析失败: {pair} - {error}")
```

---

## 6. 配置管理

### 6.1 配置项

在 `config.py` 中添加：

```python
# 大模型集成配置
LLM_INTEGRATION_CONFIG = {
    'enabled': True,          # 默认启用大模型
    'timeout': 300,          # API 调用超时时间（秒）
    'enable_thinking': True,  # 启用推理模式
}
```

### 6.2 环境变量

依赖现有的 `LLM_CONFIG`：

```python
LLM_CONFIG = {
    'api_key': os.getenv('QWEN_API_KEY', ''),
    'chat_url': os.getenv('QWEN_CHAT_URL', ...),
    'chat_model': os.getenv('QWEN_CHAT_MODEL', ...),
    'max_tokens': int(os.getenv('MAX_TOKENS', 32768)),
}
```

---

## 7. 返回值结构

### 7.1 analyze_pair() 返回值

```python
{
    # 现有字段
    'pair': str,
    'technical_signal': str,
    'technical_strength': int,
    'ml_prediction': int,
    'ml_probability': float,
    'ml_confidence': str,
    'consistency': bool,
    'recommendation': str,
    'confidence': str,
    'reasoning': str,
    'entry_price': float,
    'stop_loss': float,
    'take_profit': float,
    'risk_reward_ratio': float,
    'analysis_date': str,
    
    # 新增字段
    'llm_analysis': str  # 大模型分析报告（仅当 enable_llm=True）
}
```

### 7.2 analyze_with_llm() 返回值

```python
str  # 大模型分析报告文本
```

---

## 8. 测试策略

### 8.1 单元测试

**文件**: `tests/test_comprehensive_analysis.py`

```python
def test_analyze_pair_with_llm_enabled():
    """测试启用大模型的分析"""
    # Mock 大模型调用
    # 验证 llm_analysis 字段存在

def test_analyze_pair_with_llm_disabled():
    """测试禁用大模型的分析"""
    # 验证 llm_analysis 字段不存在

def test_analyze_with_llm():
    """测试独立调用大模型"""
    # Mock 大模型调用
    # 验证返回值

def test_llm_context_building():
    """测试上下文构建逻辑"""
    # 验证传递给大模型的上下文格式

def test_llm_error_handling():
    """测试大模型错误处理"""
    # Mock API 调用失败
    # 验证异常抛出
```

### 8.2 集成测试

```python
def test_end_to_end_with_llm():
    """测试端到端工作流（含大模型）"""
    # 完整工作流：数据加载 → 技术指标 → ML 预测 → 综合分析（含大模型）
```

### 8.3 Mock 策略

使用 `unittest.mock` 模拟大模型调用：

```python
from unittest.mock import patch

@patch('llm_services.qwen_engine.chat_with_llm')
def test_analyze_with_llm_mock(mock_chat):
    mock_chat.return_value = "模拟的分析报告"
    # 测试逻辑...
```

---

## 9. 使用示例

### 9.1 自动集成（默认）

```python
from data_services.excel_loader import FXDataLoader
from ml_services.fx_trading_model import FXTradingModel
from comprehensive_analysis import ComprehensiveAnalyzer

loader = FXDataLoader()
model = FXTradingModel()
analyzer = ComprehensiveAnalyzer()

# 加载数据
data = loader.load_pair('EUR', 'FXRate_20260320.xlsx')

# ML 预测
ml_pred = model.predict('EUR', data)

# 综合分析（自动启用大模型）
result = analyzer.analyze_pair('EUR', data, ml_pred)

print(result['llm_analysis'])  # 大模型分析报告
```

### 9.2 禁用大模型

```python
# 禁用大模型分析
result = analyzer.analyze_pair('EUR', data, ml_pred, enable_llm=False)

# result 不包含 llm_analysis 字段
```

### 9.3 独立调用大模型

```python
# 先获取技术信号和 ML 预测
technical_signal = analyzer._generate_technical_signal(data)
ml_pred = model.predict('EUR', data)

# 单独调用大模型
llm_report = analyzer.analyze_with_llm('EUR', data, ml_pred, technical_signal)

print(llm_report)
```

---

## 10. 实施步骤

### Step 1: 扩展 ComprehensiveAnalyzer

- 在 `comprehensive_analysis.py` 中添加新方法
- 实现 `_generate_llm_analysis()` 私有方法
- 修改 `analyze_pair()` 方法签名

### Step 2: 实现上下文构建

- 提取关键指标
- 构建 Prompt 模板
- 实现上下文序列化

### Step 3: 集成大模型调用

- 导入 `llm_services.qwen_engine`
- 调用 `chat_with_llm()`
- 实现错误处理和日志记录

### Step 4: 更新返回值

- 在 `analyze_pair()` 返回字典中添加 `llm_analysis` 字段
- 确保 `enable_llm=False` 时不添加该字段

### Step 5: 编写测试

- 添加单元测试（Mock 大模型）
- 添加集成测试
- 验证错误处理路径

### Step 6: 更新文档

- 更新 `AGENTS.md`
- 更新 `README.md` 使用示例
- 更新 `progress.txt`

---

## 11. 成功标准

- [ ] `analyze_pair()` 支持 `enable_llm` 参数
- [ ] `analyze_with_llm()` 独立方法正常工作
- [ ] 大模型调用失败时正确抛出异常
- [ ] 返回值包含 `llm_analysis` 字段（当启用时）
- [ ] 测试覆盖率 ≥ 85%
- [ ] 文档更新完整

---

## 12. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| **API 调用慢** | 分析耗时增加 | 设置超时（300秒），提供 disable 选项 |
| **API 费用** | 产生额外成本 | 默认启用，但用户可禁用 |
| **响应质量不稳定** | 分析报告质量下降 | 优化 Prompt 模板，提供清晰指令 |
| **Token 超限** | API 调用失败 | 控制上下文长度，仅传递关键指标 |

---

**文档结束**