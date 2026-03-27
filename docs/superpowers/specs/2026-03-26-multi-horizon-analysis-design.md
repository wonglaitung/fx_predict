# 多周期外汇智能分析系统设计文档

**日期**：2026-03-26  
**版本**：1.0  
**状态**：待审核  

## 1. 概述

### 1.1 目标

构建一个完整的多周期外汇汇率预测和分析系统，支持同时预测 1 天、5 天、20 天的汇率涨跌，并通过大模型进行双重验证分析，生成专业的市场分析报告和交易建议。

### 1.2 核心需求

1. **多周期预测**：同时预测 1 天、5 天、20 天的汇率走势
2. **双重验证分析**：以大模型为核心决策者，整合技术指标数据和 ML 预测结果
3. **自然语言输出**：生成专业的自然语言分析报告
4. **独立交易方案**：为每个周期生成独立的交易执行方案
5. **JSON 格式输出**：便于控制面板读取和展示

### 1.3 设计原则

- **多周期核心**：系统以多周期预测为核心，移除单周期预测功能
- **LLM 优先**：大模型作为核心决策者，ML 预测作为验证参考
- **结构化输出**：所有输出采用标准 JSON 格式
- **模块化设计**：清晰的模块划分，职责分离
- **容错性**：完善的错误处理和降级策略

## 2. 架构设计

### 2.1 数据流

```
Excel 数据
    │
    ▼
技术指标引擎 → 36个技术指标
    │
    ├──────────────┐
    ▼              ▼
指标数据        ML 模型（1天、5天、20天）
    │              │
    └──────┬───────┘
           ▼
    构建上下文（MultiHorizonContext）
    - 完整指标
    - ML 预测
           ▼
    大模型分析
    - 定性分析
    - 双重验证
           ▼
    解析输出
    - 建议
    - 置信度
    - 分析报告
           ▼
    综合输出（JSON）
    - LLM 建议（优先）
    - 完整分析报告（自然语言）
    - 入场/止损/止盈价格
```

### 2.2 核心数据结构

#### 2.2.1 MultiHorizonContext

多周期分析上下文对象，包含所有必要的分析数据。

```python
{
    'pair': str,                    # 货币对代码
    'current_price': float,         # 当前价格
    'data_date': str,              # 数据日期
    'predictions': {
        1: HorizonPrediction,       # 1 天预测结果
        5: HorizonPrediction,       # 5 天预测结果
        20: HorizonPrediction       # 20 天预测结果
    },
    'technical_indicators': {       # 完整技术指标（36个）
        'trend': {...},             # 趋势类指标（16个）
        'momentum': {...},          # 动量类指标（6个）
        'volatility': {...},        # 波动类指标（6个）
        'volume': {...},            # 成交量类指标（1个）
        'price_pattern': {...},     # 价格形态指标（4个）
        'market_environment': {...} # 市场环境指标（2个）
    },
    'consistency_analysis': {       # 一致性分析
        'score': float,             # 一致性评分 (0-1)
        'interpretation': str,      # 解释说明
        'all_same': bool,           # 是否全部相同
        'majority_trend': str       # 多数趋势
    }
}
```

#### 2.2.2 HorizonPrediction

单个周期的预测结果。

```python
{
    'horizon': int,                 # 周期天数
    'prediction': int,              # 0=下跌, 1=上涨
    'probability': float,           # 预测概率
    'confidence': str,              # high/medium/low
    'target_date': str,            # 目标日期
    'model_file': str              # 使用的模型文件
}
```

#### 2.2.3 LLMAnalysisResult

大模型分析结果。

**说明**：LLM 生成一个综合分析报告（500字以上），包含整体评估、技术面分析、ML 预测验证等。LLM 同时为每个周期提供独立的建议和简要分析。

```python
{
    'summary': str,                 # 综合摘要（50-100字）
    'overall_assessment': str,      # 整体评估
    'key_factors': list,           # 关键因素列表（3-5个）
    'horizon_analysis': {
        1: {                       # 1 天分析
            'recommendation': str,  # buy/sell/hold
            'confidence': str,
            'analysis': str,       # 详细分析文本
            'key_points': list     # 关键点列表
        },
        5: {...},                  # 5 天分析
        20: {...}                  # 20 天分析
    }
}
```

#### 2.2.4 HorizonTradingStrategy

单个周期的交易方案。

```python
{
    'horizon': int,
    'name': str,                   # 策略名称
    'recommendation': str,         # buy/sell/hold
    'confidence': str,
    'entry_price': float,
    'stop_loss': float,
    'take_profit': float,
    'risk_reward_ratio': float,
    'position_size': str,          # small/medium/large/none
    'reasoning': str               # 理由说明
}
```

### 2.3 最终 JSON 输出格式

```json
{
  "metadata": {
    "pair": "EUR",
    "pair_name": "欧元/美元",
    "current_price": 1.1570,
    "data_date": "2026-03-20",
    "analysis_date": "2026-03-26",
    "horizons": [1, 5, 20],
    "model_versions": {
      "1d": "EUR_catboost_1d.pkl",
      "5d": "EUR_catboost_5d.pkl",
      "20d": "EUR_catboost_20d.pkl"
    }
  },
  "ml_predictions": {
    "1_day": {
      "horizon": 1,
      "prediction": 1,
      "prediction_text": "上涨",
      "probability": 0.5132,
      "confidence": "medium",
      "target_date": "2026-03-21"
    },
    "5_day": {
      "horizon": 5,
      "prediction": 0,
      "prediction_text": "下跌",
      "probability": 0.5000,
      "confidence": "low",
      "target_date": "2026-03-25"
    },
    "20_day": {
      "horizon": 20,
      "prediction": 0,
      "prediction_text": "下跌",
      "probability": 0.5000,
      "confidence": "low",
      "target_date": "2026-04-09"
    }
  },
  "consistency_analysis": {
    "score": 0.33,
    "interpretation": "低一致性 - 短期看涨，中长期看跌",
    "all_same": false,
    "majority_trend": "下跌"
  },
  "llm_analysis": {
    "summary": "EUR/USD 当前处于震荡整理阶段，技术面显示短期存在反弹机会...",
    "overall_assessment": "谨慎乐观",
    "key_factors": [
      "RSI 接近超卖区域，存在反弹需求",
      "短期均线出现金叉信号",
      "中长期趋势依然偏弱"
    ],
    "horizon_analysis": {
      "1_day": {
        "recommendation": "buy",
        "confidence": "medium",
        "analysis": "1 天周期：技术指标显示短期超卖反弹信号，建议短线尝试做多...",
        "key_points": ["RSI < 30", "MACD 金叉"]
      },
      "5_day": {
        "recommendation": "hold",
        "confidence": "low",
        "analysis": "5 天周期：中期趋势不明确，建议观望等待方向确认...",
        "key_points": ["均线粘合", "波动率降低"]
      },
      "20_day": {
        "recommendation": "sell",
        "confidence": "medium",
        "analysis": "20 天周期：长期趋势向下，建议逢高做空...",
        "key_points": ["均线空头排列", "下降趋势线压制"]
      }
    }
  },
  "trading_strategies": {
    "short_term": {
      "name": "短线策略（1天）",
      "horizon": 1,
      "recommendation": "buy",
      "confidence": "medium",
      "entry_price": 1.1570,
      "stop_loss": 1.1470,
      "take_profit": 1.1670,
      "risk_reward_ratio": 1.0,
      "position_size": "small",
      "reasoning": "短线反弹机会，快进快出"
    },
    "medium_term": {
      "name": "中线策略（5天）",
      "horizon": 5,
      "recommendation": "hold",
      "confidence": "low",
      "entry_price": 1.1570,
      "stop_loss": 1.1420,
      "take_profit": 1.1720,
      "risk_reward_ratio": 1.0,
      "position_size": "none",
      "reasoning": "趋势不明确，建议观望"
    },
    "long_term": {
      "name": "长线策略（20天）",
      "horizon": 20,
      "recommendation": "sell",
      "confidence": "medium",
      "entry_price": 1.1570,
      "stop_loss": 1.1770,
      "take_profit": 1.1370,
      "risk_reward_ratio": 1.0,
      "position_size": "medium",
      "reasoning": "长期趋势向下，逢高做空"
    }
  },
  "technical_indicators": {
    "trend": {
      "sma5": 1.1568,
      "sma10": 1.1575,
      "sma20": 1.1582,
      "sma50": 1.1600,
      "ema5": 1.1569,
      "ema20": 1.1580,
      "macd": 0.0005,
      "macd_signal": 0.0003,
      "adx": 18.5
    },
    "momentum": {
      "rsi14": 28.5,
      "k": 25.3,
      "d": 28.7,
      "j": 18.5,
      "williams_r": -85.2,
      "cci20": -120.5
    },
    "volatility": {
      "atr14": 0.0080,
      "bb_upper": 1.1650,
      "bb_middle": 1.1575,
      "bb_lower": 1.1500,
      "volatility_20d": 0.0065
    }
  },
  "risk_analysis": {
    "overall_risk": "medium",
    "risk_factors": [
      "短期波动性较高",
      "中长期趋势不确定",
      "市场情绪分化"
    ],
    "warnings": [
      "5 天周期预测置信度低",
      "建议使用较小仓位"
    ]
  }
}
```

## 3. 模块设计

### 3.1 新增模块

#### 3.1.1 MultiHorizonContextBuilder

**职责**：构建多周期分析上下文对象

**输入**：
- 原始数据（DataFrame）
- 货币对代码（str）
- 技术分析器（TechnicalAnalyzer）
- ML 模型（FXTradingModel）

**输出**：MultiHorizonContext 对象

**功能**：
1. 计算所有技术指标（36个）
2. 调用三个周期的 ML 模型进行预测
3. 验证预测结果的一致性
4. 计算一致性评分
5. 聚合所有信息到上下文对象

**关键方法**：
```python
class MultiHorizonContextBuilder:
    def build(self, pair: str, data: pd.DataFrame) -> MultiHorizonContext:
        """构建多周期上下文"""
        # 1. 计算技术指标
        # 2. 获取 ML 预测
        # 3. 计算一致性
        # 4. 返回上下文对象
        pass
    
    def _calculate_consistency_score(self, predictions: dict) -> float:
        """计算预测一致性评分"""
        pass
    
    def _validate_predictions(self, predictions: dict) -> bool:
        """验证预测结果"""
        pass
```

#### 3.1.2 MultiHorizonPromptBuilder

**职责**：构建多周期分析的 LLM Prompt

**输入**：MultiHorizonContext 对象

**输出**：结构化的 Prompt 字符串

**功能**：
1. 组织技术指标信息（按类别分组）
2. 格式化三个周期的 ML 预测结果
3. 添加分析要求和输出格式说明
4. 优化 Prompt 结构以提高输出质量

**关键方法**：
```python
class MultiHorizonPromptBuilder:
    def build(self, context: MultiHorizonContext) -> str:
        """构建多周期分析 Prompt"""
        pass
    
    def _format_indicators(self, indicators: dict) -> str:
        """格式化技术指标"""
        pass
    
    def _format_predictions(self, predictions: dict) -> str:
        """格式化 ML 预测"""
        pass
    
    def _format_requirements(self) -> str:
        """格式化分析要求"""
        pass
```

#### 3.1.3 LLMAnalysisParser

**职责**：解析 LLM 的 JSON 输出

**输入**：LLM 返回的 JSON 字符串

**输出**：LLMAnalysisResult 对象

**功能**：
1. JSON 解析和验证
2. 字段完整性检查
3. 数据类型转换
4. 错误处理和重试机制

**关键方法**：
```python
class LLMAnalysisParser:
    def parse(self, json_str: str) -> LLMAnalysisResult:
        """解析 LLM 输出"""
        pass
    
    def _validate_json(self, json_str: str) -> bool:
        """验证 JSON 格式"""
        pass
    
    def _validate_fields(self, result: dict) -> bool:
        """验证必需字段"""
        pass
    
    def _handle_error(self, error: Exception) -> LLMAnalysisResult:
        """错误处理"""
        pass
```

#### 3.1.4 TradingStrategyGenerator

**职责**：生成交易执行方案

**输入**：
- LLMAnalysisResult 对象
- MultiHorizonContext 对象

**输出**：三个周期的交易方案字典

**功能**：
1. 解析 LLM 的交易建议
2. 计算入场价、止损位、止盈位
3. 计算风险回报比
4. 提供仓位管理建议

**关键方法**：
```python
class TradingStrategyGenerator:
    def generate(self, llm_result: LLMAnalysisResult, 
                 context: MultiHorizonContext) -> dict:
        """生成交易方案"""
        pass
    
    def _calculate_price_levels(self, horizon: int, 
                                 current_price: float,
                                 atr: float) -> dict:
        """计算价格水平"""
        pass
    
    def _determine_position_size(self, confidence: str, 
                                   risk_level: str) -> str:
        """确定仓位大小"""
        pass
```

#### 3.1.5 JSONFormatter

**职责**：格式化输出为标准 JSON 格式

**输入**：
- MultiHorizonContext 对象
- LLMAnalysisResult 对象
- 交易方案字典

**输出**：标准 JSON 字符串

**功能**：
1. 构建完整的 JSON 输出结构
2. 验证 JSON 格式正确性
3. 写入文件或返回字符串
4. 验证所有必需字段

**关键方法**：
```python
class JSONFormatter:
    def format(self, context: MultiHorizonContext,
               llm_result: LLMAnalysisResult,
               strategies: dict) -> str:
        """格式化输出为 JSON"""
        pass
    
    def write_to_file(self, json_str: str, pair: str) -> str:
        """写入 JSON 文件"""
        pass
    
    def validate_schema(self, data: dict) -> bool:
        """验证 JSON Schema"""
        pass
```

**职责**：生成交易执行方案

**输入**：
- LLMAnalysisResult 对象
- MultiHorizonContext 对象

**输出**：三个周期的交易方案字典

**功能**：
1. 解析 LLM 的交易建议
2. 计算入场价、止损位、止盈位
3. 计算风险回报比
4. 提供仓位管理建议

**关键方法**：
```python
class TradingStrategyGenerator:
    def generate(self, llm_result: LLMAnalysisResult, 
                 context: MultiHorizonContext) -> dict:
        """生成交易方案"""
        pass
    
    def _calculate_price_levels(self, horizon: int, 
                                 current_price: float,
                                 atr: float) -> dict:
        """计算价格水平"""
        pass
    
    def _determine_position_size(self, confidence: str, 
                                   risk_level: str) -> str:
        """确定仓位大小"""
        pass
```

### 3.2 重构模块

#### 3.2.1 FXTradingModel

**变更**：
- 移除：单周期预测方法 `predict()`
- 保留：`predict_all_horizons()` 方法
- 新增：模型验证方法 `validate_models()`

**关键变更**：
```python
class FXTradingModel:
    def predict_all_horizons(self, pair: str, 
                            data: pd.DataFrame) -> list:
        """预测所有周期"""
        pass
    
    def validate_models(self, pair: str) -> bool:
        """验证所有周期的模型是否存在"""
        pass
    
    # 移除 predict() 方法
```

#### 3.2.2 ComprehensiveAnalyzer

**变更**：
- 重构：以多周期为核心重新设计
- 移除：单周期分析逻辑
- 新增：使用 MultiHorizonContext 作为输入
- 简化：委托给新增的专门模块处理

**关键变更**：
```python
class ComprehensiveAnalyzer:
    def __init__(self):
        self.context_builder = MultiHorizonContextBuilder()
        self.prompt_builder = MultiHorizonPromptBuilder()
        self.llm_parser = LLMAnalysisParser()
        self.strategy_generator = TradingStrategyGenerator()
    
    def analyze_pair(self, pair: str, data: pd.DataFrame,
                    use_llm: bool = True) -> dict:
        """分析单个货币对（多周期）"""
        # 1. 构建上下文
        context = self.context_builder.build(pair, data)
        
        # 2. LLM 分析
        if use_llm:
            prompt = self.prompt_builder.build(context)
            llm_response = chat_with_llm(prompt)
            llm_result = self.llm_parser.parse(llm_response)
        else:
            llm_result = self._use_rule_engine(context)
        
        # 3. 生成交易方案
        strategies = self.strategy_generator.generate(
            llm_result, context
        )
        
        # 4. 格式化输出
        return self._format_output(context, llm_result, strategies)
    
    # 移除单周期相关方法
```

#### 3.2.3 命令行接口

**变更**：
- 移除：`--horizon` 参数（系统默认使用三个周期）
- 移除：`--all-horizons` 参数（成为默认行为）
- 简化：参数列表，减少用户选择负担

**向后兼容说明**：

1. **移除的参数**：
   - `--horizon`：系统默认使用三个周期（1天、5天、20天）
   - `--all-horizons`：这是默认行为，无需显式指定

2. **用户迁移指南**：
   - 旧命令：`python3 -m ml_services.fx_trading_model --mode train --pair EUR --horizon 20`
   - 新命令：`python3 -m ml_services.fx_trading_model --mode train --pair EUR`
   
   - 旧命令：`python3 -m comprehensive_analysis --pair EUR --all-horizons`
   - 新命令：`python3 -m comprehensive_analysis --pair EUR`

3. **自动处理**：
   - 系统自动训练和预测所有三个周期
   - 无需用户指定周期参数
   - 减少用户学习成本

4. **历史脚本处理**：
   - 如果用户的脚本中使用了 `--horizon` 参数，将收到错误提示
   - 错误信息将指导用户移除该参数
   - 提供迁移命令示例

**变更后的参数**：
```bash
# comprehensive_analysis.py
parser.add_argument('--pair', type=str, help='货币对代码')
parser.add_argument('--data_file', type=str, help='数据文件路径')
parser.add_argument('--no-llm', action='store_true', help='禁用 LLM')

# fx_trading_model.py
parser.add_argument('--mode', type=str, required=True, choices=['train', 'predict'])
parser.add_argument('--pair', type=str, required=True, help='货币对代码')
parser.add_argument('--data_file', type=str, help='数据文件路径')
# 移除 --horizon 和 --all-horizons

# run_full_pipeline.sh
--data-file FILE      # 数据文件路径
--no-llm              # 禁用 LLM
--skip-training       # 跳过训练
# 移除 --horizon 和 --all-horizons
```

## 4. 文件结构

### 4.1 新增文件

```
ml_services/
├── multi_horizon_context.py      # 多周期上下文构建器
├── multi_horizon_prompt.py       # Prompt 构建器
├── llm_parser.py                 # LLM 输出解析器
└── strategy_generator.py         # 交易方案生成器

tests/
├── test_multi_horizon_context.py
├── test_multi_horizon_prompt.py
├── test_llm_parser.py
└── test_strategy_generator.py
```

### 4.2 修改文件

```
ml_services/
└── fx_trading_model.py          # 移除单周期方法，验证逻辑

comprehensive_analysis.py         # 重构为多周期核心

run_full_pipeline.sh              # 简化参数

data/predictions/
└── {pair}_multi_horizon_{timestamp}.json  # 输出文件
```

### 4.3 文件命名规范

**模型文件**：`{pair}_catboost_{horizon}d.pkl`
- 示例：`EUR_catboost_1d.pkl`, `EUR_catboost_5d.pkl`, `EUR_catboost_20d.pkl`

**输出文件**：`{pair}_multi_horizon_{timestamp}.json`
- 示例：`EUR_multi_horizon_20260326_120000.json`

**测试文件**：`test_{module_name}.py`
- 示例：`test_multi_horizon_context.py`

## 5. 错误处理和降级策略

### 5.1 错误处理策略

#### 5.1.1 数据层错误

| 错误类型 | 处理方式 | 用户提示 |
|---------|---------|---------|
| 文件不存在 | 记录错误，抛出异常 | "文件不存在，请检查路径" |
| 数据格式错误 | 验证列名，提供具体错误 | "缺少必需列：Date, Close" |
| 数据不足 | 检查最小数据点数 | "数据不足，至少需要 100 条" |
| 模型缺失 | 警告，自动训练或使用默认值 | "模型缺失，使用默认预测" |

#### 5.1.2 ML 预测错误

| 错误类型 | 处理方式 | 降级策略 |
|---------|---------|---------|
| 模型加载失败 | 记录错误，继续其他周期 | 使用默认预测（概率 50%） |
| 预测失败 | 记录错误，跳过该周期 | 标记为 "unavailable" |
| 一致性检查失败 | 警告，不中断流程 | 设置一致性评分为 0 |

#### 5.1.3 LLM 调用错误

| 错误类型 | 处理方式 | 降级策略 |
|---------|---------|---------|
| API 密钥未配置 | 提供配置指导 | 使用规则引擎 |
| 网络错误 | 自动重试（3次） | 超时后使用规则引擎 |
| JSON 解析失败 | 记录原始响应 | 尝试修复或重新请求 |
| 输出格式错误 | 验证必需字段 | 缺失字段使用默认值 |

#### 5.1.4 JSON 输出错误

| 错误类型 | 处理方式 | 降级策略 |
|---------|---------|---------|
| 序列化失败 | 检查数据类型 | 转换为可序列化格式 |
| 文件写入失败 | 检查权限 | 输出到控制台 |
| 格式验证失败 | JSON Schema 验证 | 记录错误，继续输出 |

### 5.2 降级策略

#### 场景 1：LLM 不可用

**触发条件**：
- API 密钥未配置
- 网络连接失败
- LLM 服务不可用

**降级方案**：
```python
def _use_rule_engine(self, context: MultiHorizonContext) -> LLMAnalysisResult:
    """使用规则引擎生成分析"""
    # 基于 ML 预测和技术指标
    # 使用预设规则生成建议
    # 生成简化版分析报告
    pass
```

**输出影响**：
- 建议：基于 ML 概率和硬性约束
- 分析报告：简化版，缺少深度分析
- 置信度：基于 ML 置信度

#### 场景 2：部分周期模型缺失

**触发条件**：
- 某个周期的模型文件不存在
- 模型加载失败

**降级方案**：
```python
predictions = {}
for horizon in [1, 5, 20]:
    try:
        model = self.load_model(pair, horizon)
        predictions[horizon] = model.predict(data)
    except FileNotFoundError:
        predictions[horizon] = self._get_default_prediction(horizon)
        predictions[horizon]['source'] = 'default'
```

**输出影响**：
- 缺失周期使用默认预测
- 在输出中标记预测来源
- 降低整体置信度

#### 场景 3：LLM 输出质量不佳

**触发条件**：
- JSON 解析失败
- 必需字段缺失
- 字段值不在预期范围
- LLM 建议与 ML 预测严重冲突

**降级方案**：
```python
def _validate_and_fix_llm_output(self, result: dict, 
                                  ml_predictions: dict) -> dict:
    """验证并修复 LLM 输出"""
    # 1. 验证必需字段
    if 'recommendation' not in result:
        result['recommendation'] = self._infer_from_ml(ml_predictions)
        result['recommendation_source'] = 'ml_inference'
    
    if 'confidence' not in result:
        result['confidence'] = 'low'
    
    # 2. 验证字段值
    valid_recommendations = ['buy', 'sell', 'hold']
    if result['recommendation'] not in valid_recommendations:
        result['recommendation'] = 'hold'
        result['recommendation_source'] = 'default'
    
    valid_confidences = ['high', 'medium', 'low']
    if result['confidence'] not in valid_confidences:
        result['confidence'] = 'low'
    
    # 3. 处理 LLM 建议与 ML 预测冲突
    if self._has_severe_conflict(result, ml_predictions):
        result = self._apply_ml_priority(result, ml_predictions)
        result['conflict_resolved'] = True
        result['resolution_method'] = 'ml_priority'
    
    # 4. 降低整体置信度
    if 'recommendation_source' in result:
        result['confidence'] = self._downgrade_confidence(result['confidence'])
    
    return result

def _infer_from_ml(self, ml_predictions: dict) -> str:
    """从 ML 预测推断建议"""
    # 使用 ML 概率和硬性约束生成建议
    majority_vote = self._get_majority_trend(ml_predictions)
    if majority_vote == 1:
        return 'buy'
    elif majority_vote == 0:
        return 'sell'
    else:
        return 'hold'

def _has_severe_conflict(self, llm_result: dict, 
                          ml_predictions: dict) -> bool:
    """检测 LLM 建议与 ML 预测是否严重冲突"""
    # 如果 LLM 建议 buy，但 ML 平均预测概率 < 0.45
    if llm_result['recommendation'] == 'buy':
        avg_prob = self._get_average_probability(ml_predictions, 1)
        return avg_prob < 0.45
    
    # 如果 LLM 建议 sell，但 ML 平均预测概率 > 0.55
    if llm_result['recommendation'] == 'sell':
        avg_prob = self._get_average_probability(ml_predictions, 1)
        return avg_prob > 0.55
    
    return False

def _apply_ml_priority(self, llm_result: dict, 
                       ml_predictions: dict) -> dict:
    """应用 ML 优先策略"""
    # 使用 ML 预测 + 硬性约束生成建议
    recommendation = self._infer_from_ml(ml_predictions)
    llm_result['recommendation'] = recommendation
    llm_result['reasoning'] = f"LLM 输出质量不佳，使用 ML 预测：{recommendation}"
    return llm_result

def _downgrade_confidence(self, confidence: str) -> str:
    """降低置信度"""
    if confidence == 'high':
        return 'medium'
    elif confidence == 'medium':
        return 'low'
    else:
        return 'low'
```

**输出影响**：
- 使用 ML 预测填充缺失建议
- 处理冲突时优先使用 ML 预测
- 降低整体置信度评级
- 在输出中标记建议来源（LLM/ML/Default）
- 提供降级原因说明

## 6. 测试策略

### 6.1 单元测试

#### 6.1.1 MultiHorizonContextBuilder

```python
def test_build_context():
    """测试上下文构建"""
    builder = MultiHorizonContextBuilder()
    context = builder.build('EUR', test_data)
    
    assert context.pair == 'EUR'
    assert len(context.predictions) == 3
    assert 'technical_indicators' in context
    assert 'consistency_score' in context

def test_consistency_score():
    """测试一致性评分计算"""
    builder = MultiHorizonContextBuilder()
    
    # 所有预测相同
    predictions = {1: 1, 5: 1, 20: 1}
    score = builder._calculate_consistency_score(predictions)
    assert score == 1.0
    
    # 所有预测不同
    predictions = {1: 1, 5: 0, 20: 1}
    score = builder._calculate_consistency_score(predictions)
    assert score < 1.0
```

#### 6.1.2 MultiHorizonPromptBuilder

```python
def test_build_prompt():
    """测试 Prompt 构建"""
    builder = MultiHorizonPromptBuilder()
    prompt = builder.build(test_context)
    
    assert 'EUR' in prompt
    assert '1 天' in prompt
    assert '5 天' in prompt
    assert '20 天' in prompt
    assert 'JSON 格式' in prompt
```

#### 6.1.3 LLMAnalysisParser

```python
def test_parse_valid_json():
    """测试解析有效的 JSON"""
    parser = LLMAnalysisParser()
    result = parser.parse(valid_json_str)
    
    assert 'summary' in result
    assert 'overall_assessment' in result
    assert 'horizon_analysis' in result

def test_parse_invalid_json():
    """测试解析无效的 JSON"""
    parser = LLMAnalysisParser()
    result = parser.parse(invalid_json_str)
    
    # 应该返回默认值
    assert result['summary'] is not None

def test_parse_missing_fields():
    """测试解析缺少字段的 JSON"""
    parser = LLMAnalysisParser()
    result = parser.parse(json_with_missing_fields)
    
    # 缺失字段应该使用默认值
    assert result['overall_assessment'] == 'unknown'
```

#### 6.1.4 TradingStrategyGenerator

```python
def test_generate_strategies():
    """测试生成交易方案"""
    generator = TradingStrategyGenerator()
    strategies = generator.generate(llm_result, context)
    
    assert 'short_term' in strategies
    assert 'medium_term' in strategies
    assert 'long_term' in strategies
    
    # 验证必需字段
    for strategy in strategies.values():
        assert 'entry_price' in strategy
        assert 'stop_loss' in strategy
        assert 'take_profit' in strategy
        assert 'risk_reward_ratio' in strategy
        assert 'position_size' in strategy
        assert 'reasoning' in strategy

def test_position_size_mapping():
    """测试仓位大小映射"""
    generator = TradingStrategyGenerator()
    
    # 测试不同置信度对应的仓位
    test_cases = [
        ('high', 'large'),
        ('medium', 'medium'),
        ('low', 'small'),
        ('none', 'none')
    ]
    
    for confidence, expected_size in test_cases:
        position_size = generator._determine_position_size(confidence, 'low')
        assert position_size == expected_size

def test_risk_reward_ratio():
    """测试风险回报比计算"""
    generator = TradingStrategyGenerator()
    
    # 测试价格水平计算
    current_price = 1.1570
    atr = 0.0100
    
    price_levels = generator._calculate_price_levels(1, current_price, atr)
    
    # 验证风险回报比
    entry = price_levels['entry_price']
    stop_loss = price_levels['stop_loss']
    take_profit = price_levels['take_profit']
    
    if price_levels['recommendation'] == 'buy':
        risk = entry - stop_loss
        reward = take_profit - entry
    else:
        risk = stop_loss - entry
        reward = entry - take_profit
    
    ratio = reward / risk if risk > 0 else 0
    assert abs(ratio - 1.0) < 0.1  # 风险回报比应该接近 1:1
```

### 6.2 集成测试

#### 6.2.1 完整流程测试

```python
def test_end_to_end_workflow():
    """测试端到端工作流"""
    analyzer = ComprehensiveAnalyzer()
    
    # 1. 加载数据
    loader = FXDataLoader()
    data = loader.load_pair('EUR', test_file)
    
    # 2. 分析
    result = analyzer.analyze_pair('EUR', data, use_llm=False)
    
    # 3. 验证输出
    assert 'metadata' in result
    assert 'ml_predictions' in result
    assert 'llm_analysis' in result
    assert 'trading_strategies' in result
    
    # 4. 验证 JSON 格式
    import json
    json_str = json.dumps(result)
    parsed = json.loads(json_str)
    assert parsed == result
```

#### 6.2.2 多周期预测测试

```python
def test_multi_horizon_predictions():
    """测试多周期预测"""
    model = FXTradingModel()
    predictions = model.predict_all_horizons('EUR', test_data)
    
    assert len(predictions) == 3
    assert predictions[0]['horizon'] == 1
    assert predictions[1]['horizon'] == 5
    assert predictions[2]['horizon'] == 20
```

#### 6.2.3 LLM 分析测试

```python
def test_llm_analysis():
    """测试 LLM 分析"""
    analyzer = ComprehensiveAnalyzer()
    
    # 构建测试上下文
    context = build_test_context()
    
    # 生成 Prompt
    prompt = analyzer.prompt_builder.build(context)
    
    # 验证 Prompt
    assert '技术指标' in prompt
    assert 'ML 预测' in prompt
    assert '1 天' in prompt
    assert '5 天' in prompt
    assert '20 天' in prompt
```

#### 6.2.4 JSON 输出测试

```python
def test_json_serialization():
    """测试 JSON 序列化"""
    analyzer = ComprehensiveAnalyzer()
    result = analyzer.analyze_pair('EUR', test_data, use_llm=False)
    
    # 序列化
    import json
    json_str = json.dumps(result, ensure_ascii=False)
    
    # 反序列化
    parsed = json.loads(json_str)
    
    # 验证数据完整性
    assert parsed == result

def test_json_file_writing():
    """测试 JSON 文件写入"""
    analyzer = ComprehensiveAnalyzer()
    result = analyzer.analyze_pair('EUR', test_data, use_llm=False)
    
    # 写入文件
    formatter = JSONFormatter()
    file_path = formatter.write_to_file(json.dumps(result), 'EUR')
    
    # 验证文件存在
    import os
    assert os.path.exists(file_path)
    
    # 读取文件
    with open(file_path, 'r') as f:
        content = f.read()
    
    # 验证 JSON 格式
    parsed = json.loads(content)
    assert 'metadata' in parsed
    
    # 清理
    os.remove(file_path)

def test_json_schema_validation():
    """测试 JSON Schema 验证"""
    analyzer = ComprehensiveAnalyzer()
    result = analyzer.analyze_pair('EUR', test_data, use_llm=False)
    
    # 验证必需字段
    required_sections = [
        'metadata', 'ml_predictions', 'consistency_analysis',
        'llm_analysis', 'trading_strategies', 'technical_indicators',
        'risk_analysis'
    ]
    
    for section in required_sections:
        assert section in result
    
    # 验证元数据字段
    assert 'pair' in result['metadata']
    assert 'current_price' in result['metadata']
    assert 'data_date' in result['metadata']
    
    # 验证 ML 预测字段
    assert '1_day' in result['ml_predictions']
    assert '5_day' in result['ml_predictions']
    assert '20_day' in result['ml_predictions']
    
    # 验证交易策略字段
    assert 'short_term' in result['trading_strategies']
    assert 'medium_term' in result['trading_strategies']
    assert 'long_term' in result['trading_strategies']
    
    # 验证每个策略的字段顺序
    for strategy_name, strategy in result['trading_strategies'].items():
        keys = list(strategy.keys())
        expected_order = ['name', 'horizon', 'recommendation', 'confidence',
                         'entry_price', 'stop_loss', 'take_profit',
                         'risk_reward_ratio', 'position_size', 'reasoning']
        assert keys == expected_order, f"{strategy_name} 字段顺序不正确"

def test_json_output_consistency():
    """测试所有货币对的输出格式一致性"""
    analyzer = ComprehensiveAnalyzer()
    pairs = ['EUR', 'JPY', 'AUD']
    
    results = []
    for pair in pairs:
        data = load_test_data(pair)
        result = analyzer.analyze_pair(pair, data, use_llm=False)
        results.append(result)
    
    # 验证所有结果的结构相同
    first_keys = set(results[0].keys())
    for result in results[1:]:
        assert set(result.keys()) == first_keys
    
    # 验证所有结果的字段相同
    for section in results[0].keys():
        first_section_keys = set(results[0][section].keys())
        for result in results[1:]:
            assert set(result[section].keys()) == first_section_keys
```

### 6.3 数据验证测试

#### 6.3.1 预测一致性测试

```python
def test_consistency_calculation():
    """测试一致性计算"""
    builder = MultiHorizonContextBuilder()
    
    # 测试用例
    test_cases = [
        ({1: 1, 5: 1, 20: 1}, 1.0),  # 完全一致
        ({1: 0, 5: 0, 20: 0}, 1.0),  # 完全一致
        ({1: 1, 5: 0, 20: 1}, 0.5),  # 部分一致
        ({1: 1, 5: 0, 20: 0}, 0.33), # 低一致性
    ]
    
    for predictions, expected_score in test_cases:
        score = builder._calculate_consistency_score(predictions)
        assert abs(score - expected_score) < 0.01
```

#### 6.3.2 JSON 格式测试

```python
def test_json_schema_validation():
    """测试 JSON Schema 验证"""
    analyzer = ComprehensiveAnalyzer()
    result = analyzer.analyze_pair('EUR', test_data, use_llm=False)
    
    # 验证必需字段
    required_fields = [
        'metadata', 'ml_predictions', 'consistency_analysis',
        'llm_analysis', 'trading_strategies', 'technical_indicators'
    ]
    
    for field in required_fields:
        assert field in result
```

### 6.4 性能测试

#### 6.4.1 LLM 调用性能

```python
def test_llm_performance():
    """测试 LLM 调用性能"""
    import time
    
    start = time.time()
    result = analyzer.analyze_pair('EUR', test_data, use_llm=True)
    elapsed = time.time() - start
    
    # LLM 调用应该在合理时间内完成
    assert elapsed < 30.0
```

#### 6.4.2 内存使用测试

```python
def test_memory_usage():
    """测试内存使用"""
    import tracemalloc
    
    tracemalloc.start()
    
    analyzer = ComprehensiveAnalyzer()
    result = analyzer.analyze_pair('EUR', test_data, use_llm=False)
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # 内存使用应该在合理范围内
    assert peak < 100 * 1024 * 1024  # 100 MB
```

#### 6.4.3 并发处理测试

```python
def test_concurrent_processing():
    """测试并发处理多个货币对"""
    from concurrent.futures import ThreadPoolExecutor
    
    analyzer = ComprehensiveAnalyzer()
    pairs = ['EUR', 'JPY', 'AUD']
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(
            lambda pair: analyzer.analyze_pair(pair, load_data(pair)),
            pairs
        ))
    
    assert len(results) == 3
    for result in results:
        assert 'metadata' in result
```

## 7. 命令行接口

### 7.1 Python 模块

#### comprehensive_analysis.py

```bash
# 分析单个货币对
python3 -m comprehensive_analysis --pair EUR

# 分析所有货币对
python3 -m comprehensive_analysis

# 指定数据文件
python3 -m comprehensive_analysis --data-file FXRate_20260326.xlsx

# 禁用 LLM
python3 -m comprehensive_analysis --no-llm
```

#### fx_trading_model.py

```bash
# 训练所有周期的模型
python3 -m ml_services.fx_trading_model --mode train --pair EUR

# 预测所有周期
python3 -m ml_services.fx_trading_model --mode predict --pair EUR
```

### 7.2 Shell 脚本

```bash
# 运行完整流程
./run_full_pipeline.sh

# 跳过训练
./run_full_pipeline.sh --skip-training

# 禁用 LLM
./run_full_pipeline.sh --no-llm

# 指定数据文件
./run_full_pipeline.sh --data-file FXRate_20260326.xlsx
```

### 7.3 参数说明

| 参数 | 说明 | 默认值 | 必需 |
|-----|------|--------|------|
| --pair | 货币对代码 | 无 | 否（分析所有） |
| --data-file | 数据文件路径 | FXRate_20260320.xlsx | 否 |
| --no-llm | 禁用 LLM | False | 否 |
| --mode | train/predict | 无 | 是（模型） |

## 8. 迁移策略

### 8.1 阶段 1：准备阶段

**目标**：创建新模块的骨架代码

**任务**：
1. 创建新模块文件（4 个）
2. 创建测试文件（4 个）
3. 准备测试数据
4. 编写测试框架

**验收标准**：
- 所有新文件创建完成
- 测试框架可以运行
- 测试数据准备就绪

### 8.2 阶段 2：逐步迁移

**目标**：实现新模块的功能

**任务**：
1. 实现 `MultiHorizonContextBuilder`
   - 上下文构建逻辑
   - 一致性计算
   - 单元测试

2. 实现 `MultiHorizonPromptBuilder`
   - Prompt 构建逻辑
   - 格式化函数
   - 单元测试

3. 实现 `LLMAnalysisParser`
   - JSON 解析逻辑
   - 字段验证
   - 错误处理
   - 单元测试

4. 实现 `TradingStrategyGenerator`
   - 交易方案生成逻辑
   - 价格水平计算
   - 单元测试

5. 实现 `JSONFormatter`
   - JSON 格式化逻辑
   - Schema 验证
   - 单元测试

**验收标准**：
- 所有模块实现完成
- 单元测试通过率 ≥ 90%
- 代码覆盖率 ≥ 80%

### 8.3 阶段 3：集成测试

**目标**：集成所有新模块

**任务**：
1. 重构 `ComprehensiveAnalyzer`
2. 集成所有新模块
3. 编写集成测试
4. 端到端测试
5. 性能测试

**验收标准**：
- 集成测试通过
- 端到端测试通过
- 性能测试通过
- 无严重错误

### 8.4 阶段 4：清理和优化

**目标**：清理旧代码，优化性能

**任务**：
1. 移除单周期相关代码
2. 更新文档
3. 优化性能
4. 代码审查
5. 最终测试

**验收标准**：
- 单周期代码完全移除
- 文档更新完成
- 性能满足要求
- 所有测试通过

### 8.5 向后兼容

**保持不变**：
- 模型文件命名规范
- 数据文件格式
- 配置文件结构
- 技术指标计算逻辑

**变更内容**：
- 移除 `--horizon` 参数
- 移除单周期预测方法
- 输出格式改为 JSON
- 命令行接口简化

## 9. 日志和监控

### 9.1 日志级别

| 级别 | 用途 | 示例 |
|-----|------|------|
| DEBUG | 详细调试信息 | "上下文构建完成，包含 35 个指标" |
| INFO | 正常流程信息 | "开始训练 EUR 模型，周期 1 天" |
| WARNING | 非致命错误 | "模型 EUR_catboost_5d.pkl 不存在，使用默认预测" |
| ERROR | 严重错误 | "LLM API 调用失败：网络超时" |

### 9.2 关键指标

| 指标 | 说明 | 目标值 |
|-----|------|--------|
| 预测成功率 | ML 预测成功的比例 | ≥ 95% |
| LLM 调用成功率 | LLM 调用成功的比例 | ≥ 90% |
| 平均响应时间 | 完整分析的平均时间 | ≤ 30 秒 |
| JSON 格式正确率 | 输出 JSON 格式正确的比例 | 100% |
| 内存使用 | 分析过程中的内存峰值 | ≤ 100 MB |

### 9.3 日志格式

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

**示例**：
```
2026-03-26 12:00:00 - ml_services.multi_horizon_context - INFO - 开始构建 EUR 多周期上下文
2026-03-26 12:00:01 - ml_services.multi_horizon_context - INFO - 技术指标计算完成，共 35 个
2026-03-26 12:00:02 - ml_services.multi_horizon_context - INFO - ML 预测完成，3 个周期
2026-03-26 12:00:02 - ml_services.multi_horizon_context - INFO - 一致性评分：0.33
```

## 10. 风险和限制

### 10.1 技术风险

| 风险 | 影响 | 缓解措施 |
|-----|------|---------|
| LLM 输出不稳定 | 分析质量下降 | 多次重试、降级到规则引擎 |
| 模型文件缺失 | 预测准确性降低 | 自动训练、使用默认值 |
| 数据质量差 | 预测不可靠 | 数据验证、警告提示 |
| 网络不稳定 | LLM 调用失败 | 重试机制、离线模式 |

### 10.2 性能限制

| 限制 | 说明 | 影响 |
|-----|------|------|
| LLM 调用延迟 | 1-10 秒（含网络延迟） | 分析时间增加 |
| 内存使用 | 50-100 MB | 需要足够内存 |
| 并发处理 | 最多 3 个货币对 | 批量处理时间增加 |
| 完整分析时间 | 30-60 秒（含 LLM 调用） | 包含网络延迟 |

**性能优化策略**：
- 实现 ML 模型并行调用（同时调用三个周期）
- 缓存技术指标计算结果
- 优化 LLM Prompt 减少 token 使用
- 添加性能监控和告警机制

### 10.3 数据限制

| 限制 | 说明 | 要求 |
|-----|------|------|
| 最小数据量 | 100 条数据 | 数据不足无法训练 |
| 数据格式 | Excel（.xlsx） | 其他格式不支持 |
| 货币对数量 | 6 个（EUR, JPY, AUD, GBP, CAD, NZD） | 其他货币对需要额外训练 |

## 11. 成功标准

### 11.1 功能标准

- ✅ 支持三个周期的预测（1天、5天、20天）
- ✅ LLM 能够生成三个周期的独立分析
- ✅ 输出格式为标准 JSON
- ✅ 为每个周期生成独立的交易方案
- ✅ 包含完整的 35 个技术指标
- ✅ 实现双重验证机制

### 11.2 质量标准

- ✅ 单元测试通过率 ≥ 90%
- ✅ 集成测试通过率 ≥ 90%
- ✅ 代码覆盖率 ≥ 80%
- ✅ 无严重错误（ERROR 级别）
- ✅ JSON 格式正确率 100%

### 11.3 性能标准

- ✅ 完整分析时间 ≤ 60 秒（含 LLM 调用和网络延迟）
- ✅ LLM 调用成功率 ≥ 90%
- ✅ 内存使用 ≤ 100 MB
- ✅ 预测成功率 ≥ 95%

## 12. 后续优化方向

### 12.1 短期优化（1-2 周）

1. **优化 Prompt**：提高 LLM 输出质量
2. **缓存机制**：缓存技术指标计算结果
3. **并行处理**：并行调用三个周期的 ML 模型
4. **错误恢复**：增强错误恢复能力

### 12.2 中期优化（1-2 月）

1. **更多周期**：支持更多预测周期（如 3 天、10 天）
2. **实时数据**：支持实时数据源
3. **回测框架**：添加回测功能
4. **Web UI**：开发 Web 控制面板

### 12.3 长期优化（3-6 月）

1. **模型优化**：优化 ML 模型性能
2. **多模型集成**：集成多个 ML 模型
3. **自定义周期**：支持用户自定义预测周期
4. **API 服务**：提供 REST API 服务

## 13. 附录

### 13.1 技术指标清单（35 个）

**趋势类指标（16 个）**：
- SMA5, SMA10, SMA20, SMA50, SMA120 (5个)
- EMA5, EMA10, EMA12, EMA20, EMA26 (5个)
- MACD, MACD_Signal, MACD_Hist (3个)
- ADX, DI_Plus, DI_Minus (3个)

**动量类指标（6 个）**：
- RSI14, K, D, J, Williams_R_14, CCI20

**波动类指标（6 个）**：
- ATR14, BB_Upper, BB_Middle, BB_Lower
- Std_20d, Volatility_20d

**成交量类指标（1 个）**：
- OBV

**价格形态指标（4 个）**：
- Price_Percentile_120, Bias_5, Bias_10, Bias_20
- Trend_Slope_20

**市场环境指标（2 个）**：
- MA_Alignment, SMA5_cross_SMA20

**趋势类指标（16 个）**：
- SMA5, SMA10, SMA20, SMA50, SMA120 (5个)
- EMA5, EMA10, EMA12, EMA20, EMA26 (5个)
- MACD, MACD_Signal, MACD_Hist (3个)
- ADX, DI_Plus, DI_Minus (3个)

**动量类指标（6 个）**：
- RSI14, K, D, J, Williams_R_14, CCI20

**波动类指标（6 个）**：
- ATR14, BB_Upper, BB_Middle, BB_Lower
- Std_20d, Volatility_20d

**成交量类指标（1 个）**：
- OBV

**价格形态指标（5 个）**：
- Price_Percentile_120, Bias_5, Bias_10, Bias_20
- Trend_Slope_20

**市场环境指标（2 个）**：
- MA_Alignment, SMA5_cross_SMA20

### 13.2 配置参数

```python
# config.py
MODEL_CONFIG = {
    'horizons': [1, 5, 20],  # 预测周期
    'high_confidence_threshold': 0.60,
    'catboost_params': {
        'iterations': 1000,
        'depth': 6,
        'learning_rate': 0.05,
        'l2_leaf_reg': 3,
        'random_seed': 42,
        'verbose': False,
        'loss_function': 'Logloss',
        'eval_metric': 'Accuracy'
    }
}
```

### 13.3 输出文件路径

```
data/predictions/
├── EUR_multi_horizon_20260326_120000.json
├── JPY_multi_horizon_20260326_120001.json
├── AUD_multi_horizon_20260326_120002.json
├── GBP_multi_horizon_20260326_120003.json
├── CAD_multi_horizon_20260326_120004.json
└── NZD_multi_horizon_20260326_120005.json
```

---

**文档版本**：1.0  
**最后更新**：2026-03-26  
**审核状态**：待审核