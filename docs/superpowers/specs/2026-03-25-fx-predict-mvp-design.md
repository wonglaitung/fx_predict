# 外汇智能分析系统 - 阶段 1 MVP 设计文档

**日期**: 2026-03-25
**版本**: 1.0
**状态**: 待审查

---

## 1. 项目概述

构建一个基于机器学习和人机协作的外汇汇率预测系统，通过技术指标、CatBoost 模型和大模型分析，为外汇交易提供数据驱动的买卖建议。

### 1.1 核心目标

- **技术指标引擎**：计算 30-40 个经过验证的技术指标
- **预测模型**：CatBoost 20 天模型，预测汇率涨跌方向
- **人机协作**：整合 ML 预测和技术信号，生成交易建议
- **数据管理**：基于 Excel 文件的手动数据更新

### 1.2 实施策略

采用**渐进式 MVP** 方法，分三个阶段实施：

| 阶段 | 内容 | 目标 |
|------|------|------|
| **阶段 1 (MVP)** | 基础技术指标 + CatBoost 20天模型 + 简单建议生成 | 快速验证外汇预测可行性 |
| **阶段 2** | 扩展到多周期模型 + Walk-forward 验证 | 提升模型性能和可靠性 |
| **阶段 3** | 完整人机协作 + 性能监控 + 板块分析 | 构建完整系统 |

---

## 2. 系统架构

### 2.1 目录结构

```
fx_predict/
├── data/                           # 数据目录
│   ├── FXRate_*.xlsx              # 汇率数据文件
│   ├── models/                    # 训练好的模型
│   └── predictions/               # 预测结果
├── data_services/                 # 数据服务层
│   ├── fx_data_loader.py          # Excel 数据加载器
│   └── technical_analysis.py      # 技术指标计算引擎
├── ml_services/                   # 机器学习服务层
│   ├── fx_trading_model.py        # CatBoost 模型（20天）
│   ├── feature_engineering.py     # 特征工程
│   └── base_model_processor.py    # 基础模型处理器
├── llm_services/                  # 大模型服务层
│   └── qwen_engine.py             # 通义千问 API 封装
├── comprehensive_analysis.py      # 人机协作整合层
├── config.py                      # 配置文件
├── requirements.txt               # 依赖列表
└── AGENTS.md                      # 项目文档
```

### 2.2 分层架构

| 层级 | 模块 | 职责 |
|------|------|------|
| **数据层** | `fx_data_loader.py` | Excel 数据加载、预处理 |
| **特征层** | `technical_analysis.py` | 计算技术指标、生成特征 |
| **模型层** | `fx_trading_model.py` | CatBoost 训练、预测 |
| **整合层** | `comprehensive_analysis.py` | 整合 ML 预测 + 技术信号 |
| **接口层** | `qwen_engine.py` | 大模型调用 |

---

## 3. 核心组件设计

### 3.0 Excel 数据格式说明

**文件结构：** Excel 文件包含多个工作表（sheets），每个工作表对应一个货币对。

| 工作表名称 | 货币对代码 | 汇率符号 | 说明 |
|-----------|-----------|---------|------|
| EUR | EUR | EURUSD | 欧元/美元 |
| JPY | JPY | USDJPY | 美元/日元 |
| AUD | AUD | AUDUSD | 澳元/美元 |
| GBP | GBP | GBPUSD | 英镑/美元 |
| CAD | CAD | USDCAD | 美元/加元 |
| NZD | NZD | NZDUSD | 新西兰元/美元 |

**数据列格式：**
每个工作表包含以下列：

| 列名 | 类型 | 说明 | 示例 |
|------|------|------|------|
| Date | 日期 | 交易日期 | 3/20/2026 |
| SMA5 | 数值 | 5日简单移动平均线 | 1.0845 |
| SMA10 | 数值 | 10日简单移动平均线 | 1.0840 |
| SMA20 | 数值 | 20日简单移动平均线 | 1.0835 |
| Close | 数值 | 当日收盘汇率 | 1.0850 |

**注意事项：**
- 日期格式：MM/DD/YYYY（美式日期格式）
- 数据顺序：降序（最新数据在前）
- 汇率精度：4-5 位小数
- 缺失值：部分早期数据的 SMA20 可能缺失（数据不足 20 个交易日）

---

### 3.1 数据加载器 (`fx_data_loader.py`)

**职责：** 从 Excel 文件加载汇率数据，支持多货币对。

#### 接口设计

```python
class FXDataLoader:
    """外汇汇率数据加载器"""

    def load_pair(self, pair: str, file_path: str) -> pd.DataFrame:
        """
        加载单个货币对数据

        Args:
            pair: 货币对代码，对应 Excel 工作表名称（如 'EUR', 'JPY', 'AUD' 等）
            file_path: Excel 文件路径

        Returns:
            DataFrame，包含 Date、Close、SMA5、SMA10、SMA20 等列

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 数据格式错误或工作表不存在

        Notes:
            - pair 参数对应 Excel 的工作表名称
            - 返回的数据已按日期升序排序（旧数据在前）
            - 缺失值已使用前向填充处理
        """

    def load_all_pairs(self, file_path: str) -> dict:
        """
        加载所有货币对数据

        Args:
            file_path: Excel 文件路径

        Returns:
            字典 {pair_code: DataFrame}
        """

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        预处理数据

        - 日期格式化（MM/DD/YYYY → datetime）
        - 数据排序（升序：旧数据在前）
        - 缺失值处理（前向填充）
        - 数据类型转换

        Args:
            df: 原始数据

        Returns:
            预处理后的数据
        """
```

#### 数据格式

```python
# 输出 DataFrame 格式
{
    'Date': datetime,   # 交易日期
    'Close': float,     # 收盘汇率
    'Open': float,      # 开盘汇率（如有）
    'High': float,      # 最高汇率（如有）
    'Low': float,       # 最低汇率（如有）
    'Volume': float     # 成交量（如有）
}
```

### 3.2 技术指标引擎 (`technical_analysis.py`)

**职责：** 计算技术指标，为预测模型提供特征。

#### 指标分类

| 类别 | 指标 | 用途 |
|------|------|------|
| **趋势类** | SMA(5,10,20,50,120), EMA(5,10,20), MACD, ADX | 判断趋势方向和强度 |
| **动量类** | RSI(14), KDJ, 威廉指标(14), CCI | 判断超买超卖 |
| **波动类** | ATR(14), 布林带(20,2), 波动率 | 判断波动水平 |
| **成交量类** | OBV, 成交量比率 | 判断资金流向 |
| **价格形态** | 价格百分位, 乖离率, 支撑阻力位 | 判断价格位置 |
| **市场环境** | 趋势斜率, 均线排列强度 | 识别市场状态 |

#### 接口设计

```python
class TechnicalAnalyzer:
    """技术指标计算引擎"""

    def compute_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有技术指标

        Args:
            df: 原始数据（需包含 Close, Open, High, Low 列）

        Returns:
            包含所有指标的 DataFrame

        Notes:
            - 所有指标使用滞后数据（.shift(1)），防止数据泄漏
            - 返回的 DataFrame 会包含原始数据和新计算的所有指标
        """

    def compute_sma(self, df: pd.DataFrame, period: int) -> pd.Series:
        """计算简单移动平均线"""

    def compute_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """计算指数移动平均线"""

    def compute_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26,
                     signal: int = 9) -> pd.DataFrame:
        """
        计算 MACD

        Returns:
            DataFrame with columns: MACD, MACD_Signal, MACD_Hist
        """

    def compute_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算 RSI"""

    def compute_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算 ATR"""

    def compute_adx(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算 ADX

        Returns:
            DataFrame with columns: ADX, DI_Plus, DI_Minus
        """

    def compute_bollinger_bands(self, df: pd.DataFrame, period: int = 20,
                                std_dev: int = 2) -> pd.DataFrame:
        """
        计算布林带

        Returns:
            DataFrame with columns: BB_Upper, BB_Middle, BB_Lower
        """
```

#### 数据泄漏防范

**原则：** 所有技术指标必须使用滞后数据，确保不使用未来信息。

```python
# 错误示例（数据泄漏）
df['SMA5'] = df['Close'].rolling(window=5).mean()

# 正确示例（无数据泄漏）
df['SMA5'] = df['Close'].rolling(window=5).mean().shift(1)
```

### 3.3 CatBoost 模型 (`fx_trading_model.py`)

**职责：** 训练和预测汇率涨跌方向（20 天）。

#### 模型配置

```python
MODEL_CONFIG = {
    'model_type': 'catboost',
    'horizon': 20,                    # 预测周期
    'task_type': 'classification',    # 二分类：上涨/下跌
    'params': {
        'iterations': 500,
        'learning_rate': 0.05,
        'depth': 6,
        'l2_leaf_reg': 3,
        'random_seed': 42
    }
}
```

#### 特征工程

```python
class FeatureEngineer:
    """特征工程"""

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        创建特征集

        特征类别：
        1. 技术指标特征：SMA5, SMA10, SMA20, SMA50, SMA120, EMA5, EMA10, EMA20,
                         RSI14, MACD, MACD_Signal, MACD_Hist, ADX, ATR14,
                         BB_Upper, BB_Middle, BB_Lower, OBV, KDJ, CCI, 威廉指标
        2. 价格衍生特征：Close_change_1d（日涨跌幅）, Close_change_5d（5日涨跌幅）,
                         乖离率_5d, 乖离率_10d, 乖离率_20d
        3. 波动率特征：ATR14, Std_20d（20日标准差）, Volatility_20d（20日波动率）
        4. 交叉特征：SMA5_cross_SMA20（均线交叉信号）, Price_vs_Bollinger（价格与布林带位置）
        5. 滞后特征：Close_lag_1, Close_lag_5, Close_lag_10（历史价格）,
                      RSI14_lag_1, MACD_lag_1（滞后指标）
        6. 市场环境特征：Trend_Slope（趋势斜率）, MA_Alignment（均线排列强度）

        Args:
            df: 包含技术指标的数据

        Returns:
            特征 DataFrame

        Notes:
            - 所有特征必须使用滞后数据（.shift(1)），防止数据泄漏
            - 返回的特征 DataFrame 不包含目标变量
        """

    def create_target(self, df: pd.DataFrame, horizon: int = 20) -> pd.Series:
        """
        创建目标变量：未来 horizon 天的涨跌

        Args:
            df: 原始数据
            horizon: 预测周期（天）

        Returns:
            目标序列（1=上涨, 0=下跌）

        Notes:
            - 使用 shift(-horizon) 获取未来数据
            - **警告**：此方法仅用于训练阶段，预测阶段不可使用！
            - 预测时目标变量无法获取，应由模型预测生成
        """
```

#### 接口设计

```python
class FXTradingModel:
    """外汇交易模型"""

    def __init__(self, config: dict = None):
        """
        初始化模型

        Args:
            config: 模型配置字典
        """

    def train(self, pair: str, data: pd.DataFrame) -> dict:
        """
        训练模型

        Args:
            pair: 货币对代码
            data: 训练数据（必须包含特征和目标）

        Returns:
            训练指标字典
        """

    def predict(self, pair: str, data: pd.DataFrame) -> dict:
        """
        预测

        Args:
            pair: 货币对代码
            data: 预测数据（必须包含特征）

        Returns:
            预测结果字典
        """

    def save_model(self, pair: str, model: object, path: str):
        """保存模型"""

    def load_model(self, pair: str, path: str):
        """加载模型"""
```

#### 输出格式

```python
{
    'pair': 'EURUSD',
    'current_price': 1.0850,
    'prediction': 1,              # 1=上涨, 0=下跌
    'probability': 0.65,          # 上涨概率
    'confidence': 'high',         # high/medium/low
    'data_date': '2026-03-20',
    'target_date': '2026-04-09'
}
```

### 3.4 人机协作整合层 (`comprehensive_analysis.py`)

**职责：** 整合 ML 预测和技术信号，生成交易建议。

#### 核心流程

```
1. 技术信号分析
   ├─ 计算技术指标
   ├─ 生成交易信号（买入/卖出/观望）
   └─ 计算信号强度（0-100）

2. ML 预测整合
   ├─ 获取 CatBoost 预测结果
   ├─ 计算置信度（probability → confidence）
   └─ 评估模型不确定性

3. 信号协同验证
   ├─ 检查技术信号与 ML 预测一致性
   ├─ 应用硬性约束（probability ≤ 0.50 → 禁止买入）
   └─ 生成综合信号

4. 大模型分析
   ├─ 整合技术面 + ML 预测 + 市场环境
   ├─ 生成市场分析报告
   └─ 生成具体交易建议
```

#### 接口设计

```python
class ComprehensiveAnalyzer:
    """综合分析器"""

    def analyze_pair(self, pair: str, data: pd.DataFrame,
                    ml_prediction: dict) -> dict:
        """
        分析单个货币对

        Args:
            pair: 货币对代码
            data: 汇率数据
            ml_prediction: ML 预测结果

        Returns:
            综合分析结果
        """

    def generate_signals(self, technical_data: pd.DataFrame,
                        ml_prediction: dict) -> dict:
        """
        生成交易信号

        Returns:
            信号字典
        """

    def validate_signals(self, signals: dict) -> dict:
        """
        验证信号，应用硬性约束

        硬性约束：
        - ML probability ≤ 0.50 → 绝对禁止买入
        - ML probability ≥ 0.60 → 可以考虑强烈买入
        """

    def generate_llm_analysis(self, context: dict) -> str:
        """
        调用大模型生成分析报告

        Args:
            context: 分析上下文（技术面、ML预测、市场环境等）

        Returns:
            分析报告文本
        """
```

#### 决策框架

```
┌─────────────────────────────────────────────────────────┐
│                    信号协同验证流程                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  技术信号强度              ML 预测概率                    │
│       │                        │                        │
│       └────────────────┬───────┘                        │
│                        ▼                                │
│               ┌───────────────┐                         │
│               │  一致性检查   │                         │
│               └───────┬───────┘                         │
│                       │                                 │
│    ┌──────────────────┼──────────────────┐             │
│    ▼                  ▼                  ▼             │
│ ┌────────┐       ┌────────┐       ┌────────┐           │
│ │ 强烈买入 │       │ 买入/观望 │       │  卖出   │           │
│ │一致性强 │       │ 一致性中 │       │一致性强 │           │
│ └────────┘       └────────┘       └────────┘           │
│                                                         │
│ 硬性约束：                                              │
│ - ML probability ≤ 0.50 → 绝对禁止买入                   │
│ - ML probability ≥ 0.60 → 可以考虑强烈买入               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### 输出格式

```python
{
    'pair': 'EURUSD',
    'technical_signal': 'buy',           # buy/sell/hold
    'technical_strength': 75,            # 0-100
    'ml_prediction': 1,                  # 1=up, 0=down
    'ml_probability': 0.68,
    'ml_confidence': 'high',
    'consistency': True,                 # 技术信号与 ML 预测一致
    'recommendation': 'buy',             # buy/sell/hold
    'confidence': 'high',                # high/medium/low
    'reasoning': '技术信号买入（强度75），ML预测上涨概率0.68（高置信度），方向一致',
    'entry_price': 1.0850,
    'stop_loss': 1.0750,
    'take_profit': 1.0950,
    'risk_reward_ratio': 1.0,
    'analysis_date': '2026-03-25'
}
```

### 3.5 大模型引擎 (`qwen_engine.py`)

**职责：** 封装通义千问 API，提供分析能力。

#### 接口设计

```python
def chat_with_llm(query: str, enable_thinking: bool = True) -> str:
    """
    调用大模型生成响应

    Args:
        query: 用户查询
        enable_thinking: 是否启用推理模式

    Returns:
        模型响应文本

    Raises:
        ValueError: API 密钥未设置
        requests.exceptions.RequestException: API 调用失败
    """
```

#### 配置

```python
# API 配置
api_key = os.getenv('QWEN_API_KEY', '')
chat_url = os.getenv('QWEN_CHAT_URL',
                     'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions')
chat_model = os.getenv('QWEN_CHAT_MODEL', 'qwen-plus-2025-12-01')
max_tokens = int(os.getenv('MAX_TOKENS', 32768))

# 调用参数
payload = {
    'model': chat_model,
    'messages': [{'role': 'user', 'content': query}],
    'stream': False,
    'top_p': 0.2,
    'temperature': 0.05,          # 低温度保证稳定性
    'max_tokens': max_tokens,
    'enable_thinking': enable_thinking
}
```

#### 使用场景

1. **市场分析**：分析当前市场环境、趋势、风险
2. **建议解释**：解释交易建议的理由和依据
3. **风险管理**：提供风险控制建议和仓位管理
4. **复盘分析**：分析历史交易结果，总结经验教训

---

## 4. 数据流设计

### 4.1 数据流图

```
┌─────────────────────────────────────────────────────────────┐
│                        数据流图                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Excel 文件                                                  │
│  FXRate_*.xlsx                                              │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────┐                                        │
│  │ fx_data_loader   │                                        │
│  │                 │                                        │
│  │ - 加载原始数据   │                                        │
│  │ - 预处理         │                                        │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │technical_analysis│                                       │
│  │                 │                                        │
│  │ - 计算技术指标   │                                        │
│  │ - 生成特征       │                                        │
│  └─────┬───────────┘                                        │
│        │                                                   │
│        ├──────────────────────┐                            │
│        ▼                      ▼                            │
│  ┌──────────┐          ┌──────────┐                        │
│  │ 特征集    │          │ 技术信号  │                        │
│  └────┬─────┘          └────┬─────┘                        │
│       │                    │                               │
│       ▼                    ▼                               │
│  ┌─────────────────┐  ┌──────────────┐                     │
│  │ fx_trading_model│  │ 信号生成器   │                     │
│  │                 │  │              │                     │
│  │ - 训练/预测     │  │ - 买卖信号   │                     │
│  │ - 计算概率      │  │ - 信号强度   │                     │
│  └────┬────────────┘  └──────┬───────┘                     │
│       │                      │                             │
│       └──────────┬───────────┘                             │
│                  ▼                                          │
│        ┌─────────────────┐                                  │
│        │comprehensive_    │                                  │
│        │analysis         │                                  │
│        │                 │                                  │
│        │ - 信号协同验证   │                                  │
│        │ - 综合分析      │                                  │
│        └─────┬───────────┘                                  │
│              │                                              │
│              ├──────────────┐                               │
│              ▼              ▼                               │
│        ┌──────────┐  ┌──────────┐                          │
│        │交易建议  │  │LLM 分析  │                          │
│        └──────────┘  └──────────┘                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 数据流关键点

1. **原始数据 → 预处理数据**
   - 日期格式化（MM/DD/YYYY → datetime）
   - 数据排序（升序：旧数据在前）
   - 缺失值处理（前向填充）
   - 数据类型转换（Close → float）

2. **预处理数据 → 特征集**
   - 计算所有技术指标
   - 创建衍生特征（涨跌幅、乖离率等）
   - 应用 `.shift(1)` 防止数据泄漏
   - 生成目标变量（未来 20 天涨跌）

3. **特征集 → ML 预测**
   - 训练模型（使用历史数据）
   - 预测当前数据（获取概率和方向）
   - 计算置信度（high/medium/low）

4. **技术指标 → 技术信号**
   - 多指标综合评分
   - 信号强度归一化（0-100）
   - 生成买卖信号（buy/sell/hold）

5. **ML 预测 + 技术信号 → 综合分析**
   - 一致性检查
   - 硬性约束验证
   - 生成最终交易建议

---

## 5. 错误处理策略

### 5.1 异常分类

| 异常类型 | 处理策略 |
|---------|---------|
| `FileNotFoundError` | 文件不存在，提示用户 |
| `ValueError` | 数据格式错误，记录详情 |
| `ModelNotFoundError` | 模型不存在，返回默认预测 |
| `APITimeoutError` | API 超时，返回默认响应 |
| `DataLeakageWarning` | 数据泄漏警告，记录日志 |

### 5.2 错误处理示例

```python
# 数据加载错误
try:
    df = loader.load_pair('EURUSD', 'FXRate.xlsx')
except FileNotFoundError:
    logger.error(f"文件不存在: {file_path}")
    return None
except ValueError as e:
    logger.error(f"数据格式错误: {e}")
    return None

# 技术指标计算错误
if len(df) < 20:
    raise ValueError("数据不足，至少需要 20 个交易日")

# 模型预测错误
if not os.path.exists(model_path):
    logger.warning(f"模型不存在: {model_path}")
    return {'prediction': 0, 'probability': 0.5}

# 大模型调用错误
try:
    response = chat_with_llm(query)
except requests.exceptions.Timeout:
    logger.warning("LLM 调用超时")
    return "LLM 服务暂时不可用"
```

### 5.3 日志记录

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fx_predict.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

---

## 6. 测试策略

### 6.1 单元测试

```python
# tests/test_fx_data_loader.py
def test_load_pair():
    loader = FXDataLoader()
    df = loader.load_pair('EURUSD', 'test_data.xlsx')
    assert df is not None
    assert 'Close' in df.columns
    assert len(df) > 0

# tests/test_technical_analysis.py
def test_compute_rsi():
    analyzer = TechnicalAnalyzer()
    df = pd.DataFrame({'Close': [1.0, 1.1, 1.2, 1.3, 1.4]})
    rsi = analyzer.compute_rsi(df, period=14)
    assert 0 <= rsi.iloc[-1] <= 100
    assert not rsi.isna().any()

# tests/test_fx_trading_model.py
def test_predict():
    model = FXTradingModel()
    prediction = model.predict('EURUSD', test_data)
    assert 'prediction' in prediction
    assert 'probability' in prediction
    assert prediction['prediction'] in [0, 1]
```

### 6.2 集成测试

```python
# tests/test_integration.py
def test_end_to_end():
    # 1. 加载数据
    loader = FXDataLoader()
    df = loader.load_pair('EURUSD', 'test_data.xlsx')

    # 2. 计算技术指标
    analyzer = TechnicalAnalyzer()
    df = analyzer.compute_all_indicators(df)

    # 3. 训练模型
    model = FXTradingModel()
    model.train('EURUSD', df)

    # 4. 预测
    prediction = model.predict('EURUSD', df)

    # 5. 综合分析
    comprehensive = ComprehensiveAnalyzer()
    result = comprehensive.analyze_pair('EURUSD', df, prediction)

    assert result['recommendation'] in ['buy', 'sell', 'hold']
```

### 6.3 测试覆盖率

```bash
# 运行测试
pytest tests/ --cov=. --cov-report=html

# 目标覆盖率
# - 核心模块：≥ 80%
# - 工具模块：≥ 60%
```

---

## 7. 配置管理

### 7.1 配置文件 (`config.py`)

```python
# 货币对配置
CURRENCY_PAIRS = {
    'EUR': {'symbol': 'EURUSD', 'name': '欧元/美元'},
    'JPY': {'symbol': 'USDJPY', 'name': '美元/日元'},
    'AUD': {'symbol': 'AUDUSD', 'name': '澳元/美元'},
    'GBP': {'symbol': 'GBPUSD', 'name': '英镑/美元'},
    'CAD': {'symbol': 'USDCAD', 'name': '美元/加元'},
    'NZD': {'symbol': 'NZDUSD', 'name': '新西兰元/美元'}
}

# 模型配置
MODEL_CONFIG = {
    'horizon': 20,
    'model_type': 'catboost',
    'catboost_params': {
        'iterations': 500,
        'learning_rate': 0.05,
        'depth': 6,
        'l2_leaf_reg': 3,
        'random_seed': 42,
        'verbose': False
    }
}

# 技术指标配置
INDICATOR_CONFIG = {
    'SMA_PERIODS': [5, 10, 20, 50, 120],
    'RSI_PERIOD': 14,
    'MACD_FAST': 12,
    'MACD_SLOW': 26,
    'MACD_SIGNAL': 9,
    'ATR_PERIOD': 14,
    'ADX_PERIOD': 14
}

# 信号阈值
SIGNAL_CONFIG = {
    'buy_threshold': 60,        # 信号强度 ≥ 60 → 买入
    'sell_threshold': 40,       # 信号强度 ≤ 40 → 卖出
    'ml_probability_threshold': 0.60  # ML 概率 ≥ 0.60 → 高置信度
}

# 文件路径
PATHS = {
    'data_dir': 'data',
    'model_dir': 'data/models',
    'prediction_dir': 'data/predictions',
    'log_file': 'fx_predict.log'
}
```

### 7.2 环境变量

```bash
# .env 文件
QWEN_API_KEY=your_api_key_here
QWEN_CHAT_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
QWEN_CHAT_MODEL=qwen-plus-2025-12-01
MAX_TOKENS=32768
```

---

## 8. 依赖列表 (`requirements.txt`)

```txt
# 核心依赖
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0

# 环境变量
python-dotenv>=1.0.0

# 机器学习
catboost>=1.2.0
scikit-learn>=1.3.0

# 数据可视化（可选）
matplotlib>=3.7.0
seaborn>=0.12.0

# 大模型
requests>=2.31.0

# 开发工具
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.7.0
```

---

## 9. 使用示例

### 9.1 命令行使用

```bash
# 从项目根目录运行
cd /data/fx_predict

# 训练所有货币对的 CatBoost 20 天模型
python3 ml_services/fx_trading_model.py --mode train --horizon 20 --model-type catboost

# 训练单个货币对
python3 ml_services/fx_trading_model.py --mode train --pair EURUSD --horizon 20

# 预测所有货币对
python3 ml_services/fx_trading_model.py --mode predict --horizon 20

# 预测单个货币对
python3 ml_services/fx_trading_model.py --mode predict --pair EURUSD

# 生成综合交易建议
python3 comprehensive_analysis.py --date 2026-03-25
```

**注意**：所有命令都应从项目根目录 `/data/fx_predict` 运行，以确保模块导入路径正确。

### 9.2 Python API

```python
from data_services.fx_data_loader import FXDataLoader
from data_services.technical_analysis import TechnicalAnalyzer
from ml_services.fx_trading_model import FXTradingModel
from comprehensive_analysis import ComprehensiveAnalyzer

# 1. 加载数据
loader = FXDataLoader()
data = loader.load_all_pairs('data/FXRate.xlsx')

# 2. 计算技术指标
analyzer = TechnicalAnalyzer()
for pair, df in data.items():
    data[pair] = analyzer.compute_all_indicators(df)

# 3. 训练模型
model = FXTradingModel()
for pair, df in data.items():
    model.train(pair, df)

# 4. 预测
predictions = {}
for pair, df in data.items():
    predictions[pair] = model.predict(pair, df)

# 5. 综合分析
comprehensive = ComprehensiveAnalyzer()
recommendations = {}
for pair, df in data.items():
    recommendations[pair] = comprehensive.analyze_pair(
        pair, df, predictions[pair]
    )

# 6. 输出建议
for pair, rec in recommendations.items():
    print(f"{pair}: {rec['recommendation']} (置信度: {rec['confidence']})")
```

---

## 10. 成功标准

### 10.1 阶段 1 MVP

| 指标 | 目标 | 验证方法 |
|------|------|---------|
| **技术指标** | 覆盖 30-40 个指标 | 单元测试 + 代码审查 |
| **模型准确率** | ≥ 55%（基准） | Walk-forward 验证 |
| **模型稳定性** | 标准差 ≤ 5% | Walk-forward 验证 |
| **预测速度** | 单货币对 < 1 秒 | 性能测试 |
| **信号质量** | 买卖信号可解释 | 手工验证 |
| **代码质量** | 测试覆盖率 ≥ 70% | pytest-cov |
| **文档完整** | 所有模块有文档 | 代码审查 |

### 10.2 关键成功因素

1. **数据质量**
   - Excel 数据格式正确
   - 技术指标计算准确
   - 无数据泄漏

2. **模型性能**
   - 准确率达到预期
   - 预测结果稳定
   - 泛化能力强

3. **系统可用性**
   - 接口清晰易用
   - 错误处理完善
   - 日志记录完整

4. **可扩展性**
   - 模块化设计
   - 易于添加新指标
   - 支持多周期预测

---

## 11. 下一阶段规划（阶段 2）

### 11.1 扩展功能

| 功能模块 | 描述 | 优先级 |
|---------|------|--------|
| **多周期模型** | 支持 1 天、5 天预测 | 高 |
| **Walk-forward 验证** | 模型性能评估 | 高 |
| **性能监控** | 预测准确率追踪 | 中 |
| **回测系统** | 策略回测 | 中 |
| **数据更新** | 支持在线数据源 | 低 |

### 11.2 实施顺序

1. **多周期模型**（2-3 周）
   - 扩展特征工程支持不同周期
   - 训练 1 天、5 天模型
   - 对比模型性能

2. **Walk-forward 验证**（1-2 周）
   - 实现 Walk-forward 分割
   - 评估模型真实预测能力
   - 生成性能报告

3. **性能监控**（1 周）
   - 保存预测历史
   - 定期评估准确率
   - 生成月度报告

---

## 12. 风险与缓解

| 风险 | 影响 | 具体缓解措施 |
|------|------|-----------|
| **数据不足** | 模型性能差 | 1. 至少收集 2-3 年历史数据（500+ 个交易日）<br>2. 增加 2-3 个主流货币对（如 USDCHF）<br>3. 使用数据增强技术（如滑动窗口） |
| **数据泄漏** | 准确率虚高 | 1. 检查清单：所有技术指标都使用 shift(1)？<br>2. 训练前删除包含 NaN 的行<br>3. 严格区分训练集和测试集<br>4. 使用 Walk-forward 验证而非简单随机分割 |
| **过拟合** | 泛化能力差 | 1. 使用 Walk-forward 验证评估真实预测能力<br>2. CatBoost 正则化参数：l2_leaf_reg=3, depth=6<br>3. 早停策略（early_stopping_rounds=50）<br>4. 特征选择：只使用重要性前 500 个特征 |
| **LLM 不可用** | 无法生成分析 | 1. 实现降级机制：LLM 失败时使用纯技术分析 + ML 预测<br>2. 设置超时（300 秒）和重试机制（最多 3 次）<br>3. 缓存 LLM 响应，减少 API 调用 |
| **外汇市场特性** | 股票指标不适用 | 1. 调整指标参数：ATR 周期从 14 改为 20（外汇波动更大）<br>2. 添加外汇特色指标：货币对相关性、非农数据影响<br>3. 区分直接报价（如 EURUSD）和间接报价（如 USDJPY） |
| **Excel 数据格式变化** | 数据加载失败 | 1. 在数据加载器中添加格式验证<br>2. 提供数据格式示例文档<br>3. 实现数据格式检查和自动修复功能 |

---

## 13. 设计总结

### 13.1 MVP 核心交付物

1. **技术指标引擎**（`technical_analysis.py`）
   - 30-40 个技术指标
   - 数据泄漏防范
   - 单元测试覆盖

2. **CatBoost 模型**（`fx_trading_model.py`）
   - 20 天预测周期
   - 训练/预测接口
   - 模型持久化

3. **人机协作系统**（`comprehensive_analysis.py`）
   - 信号协同验证
   - 硬性约束机制
   - 综合建议生成

4. **大模型集成**（`qwen_engine.py`）
   - 市场分析
   - 建议解释
   - 风险提示

5. **完整文档**
   - 代码注释
   - 使用示例
   - 测试用例

### 13.2 设计原则

- **YAGNI**：只实现当前需要的功能
- **模块化**：每个组件职责单一，易于维护
- **可扩展**：为未来扩展预留接口
- **可靠性**：完善的错误处理和日志记录
- **可测试**：清晰的测试策略和覆盖率目标

---

**文档结束**