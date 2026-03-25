# FX Predict - 外汇智能分析系统

## 项目概述

本项目是一个基于机器学习和人机协作的外汇汇率预测系统，包含：

- **技术指标引擎**：计算 35 个经过验证的技术指标
- **CatBoost 预测模型**：20 天周期，预测汇率涨跌方向
- **人机协作系统**：整合 ML 预测和技术信号，生成交易建议
- **大模型集成**：提供市场分析和建议解释

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的通义千问 API 密钥：

```bash
cp .env.example .env
# 编辑 .env 文件，填入 QWEN_API_KEY
```

### 运行示例

```bash
# 训练模型
python3 ml_services/fx_trading_model.py --mode train --pair EUR --horizon 20

# 生成预测
python3 ml_services/fx_trading_model.py --mode predict --pair EUR

# 综合分析
python3 comprehensive_analysis.py --date 2026-03-25
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行集成测试
pytest tests/test_integration.py -v

# 运行测试并检查覆盖率
pytest tests/ --cov=. --cov-report=html --cov-report=term
```

## 项目结构

```
fx_predict/
├── data/                           # 数据目录
│   ├── models/                    # 训练好的模型（CatBoost）
│   └── predictions/               # 预测结果
├── data_services/                 # 数据服务层
│   ├── excel_loader.py           # Excel 数据加载器（支持自动生成 OHLC）
│   └── technical_analysis.py     # 技术指标计算引擎（35 个指标）
├── ml_services/                   # 机器学习服务层
│   ├── fx_trading_model.py       # CatBoost 模型
│   ├── feature_engineering.py    # 特征工程（价格、偏离率、波动率、趋势）
│   └── base_model_processor.py   # 基础模型处理器（模型保存/加载）
├── llm_services/                  # 大模型服务层
│   └── qwen_engine.py            # 通义千问 API 封装
├── comprehensive_analysis.py      # 人机协作整合层
├── config.py                      # 配置文件
├── requirements.txt               # 依赖列表
└── tests/                         # 测试文件（88 个测试用例）
    ├── test_integration.py       # 集成测试（9 个端到端测试）
    ├── test_comprehensive_analysis.py
    ├── test_excel_loader.py
    ├── test_feature_engineering.py
    ├── test_fx_trading_model.py
    └── test_technical_analysis.py
```

## 支持的货币对

- **EUR/USD**（欧元/美元）
- **USD/JPY**（美元/日元）
- **AUD/USD**（澳元/美元）
- **GBP/USD**（英镑/美元）
- **USD/CAD**（美元/加元）
- **NZD/USD**（新西兰元/美元）

**注意**：货币对代码使用基准货币（如 EUR、JPY 等）作为键名。

## 技术指标（35个）

系统计算以下技术指标，所有指标均使用滞后数据（`.shift(1)`）防止数据泄漏：

### 趋势类指标（11个）

| 指标 | 说明 |
|------|------|
| SMA5, SMA10, SMA20, SMA50, SMA120 | 简单移动平均线（5/10/20/50/120日） |
| EMA5, EMA10, EMA12, EMA20, EMA26 | 指数移动平均线（5/10/12/20/26日） |
| MACD | 移动平均收敛发散指标 |
| MACD_Signal | MACD 信号线（9日 EMA） |
| MACD_Hist | MACD 柱状图 |
| ADX | 平均趋向指数（14日） |
| DI_Plus | 上升方向线 |
| DI_Minus | 下降方向线 |

### 动量类指标（7个）

| 指标 | 说明 |
|------|------|
| RSI14 | 相对强弱指标（14日，范围 0-100） |
| K | 随机指标 K 值 |
| D | 随机指标 D 值 |
| J | 随机指标 J 值 |
| WilliamsR_14 | 威廉指标（14日，范围 -100 到 0） |
| CCI20 | 顺势指标（20日） |

### 波动类指标（6个）

| 指标 | 说明 |
|------|------|
| ATR14 | 平均真实波幅（14日） |
| BB_Upper | 布林带上轨（20日，2倍标准差） |
| BB_Middle | 布林带中轨（20日 SMA） |
| BB_Lower | 布林带下轨（20日，2倍标准差） |
| Std_20d | 20日标准差 |
| Volatility_20d | 20日波动率（标准差/均价） |

### 成交量类指标（1个）

| 指标 | 说明 |
|------|------|
| OBV | 能量潮（On-Balance Volume） |

### 价格形态指标（5个）

| 指标 | 说明 |
|------|------|
| Price_Percentile_120 | 价格百分位（120日滚动百分位） |
| Bias_5 | 5日乖离率 |
| Bias_10 | 10日乖离率 |
| Bias_20 | 20日乖离率 |
| Trend_Slope_20 | 趋势斜率（20日线性回归斜率） |

### 市场环境指标（2个）

| 指标 | 说明 |
|------|------|
| MA_Alignment | 均线排列强度（多头/空头排列） |
| （综合 SMA5/SMA10/SMA20/SMA50） | |

## 数据泄漏防范

**关键原则**：所有技术指标和特征都使用滞后数据（`.shift(1)`），确保不使用未来信息。

### 具体措施

1. **技术指标层**：
   - 所有指标计算使用 `.shift(1)`
   - 示例：`SMA5 = df['Close'].rolling(5).mean().shift(1)`

2. **特征工程层**：
   - 价格衍生特征：`Close_change_1d = df['Close'].diff(1).shift(1)`
   - 偏离率特征：`Bias_5 = ((Close - SMA5) / SMA5).shift(1)`
   - 滞后特征：`Close_lag_1 = df['Close'].shift(1)`

3. **训练阶段**：
   - 目标变量使用 `shift(-horizon)`（仅用于训练，预测时不可用）
   - 特征和目标完全分离，避免前瞻性偏差

4. **预测阶段**：
   - 仅使用历史数据（不包含未来信息）
   - 最后一个数据点的指标基于历史计算

### 验证方法

集成测试包含 `test_data_leakage_prevention()`，验证：
- 至少 70% 的指标在第一行是 NaN
- 所有滞后特征在第一行是 NaN
- 至少 50% 的价格衍生特征在第一行是 NaN

## 硬性约束

系统应用以下硬性约束以控制风险：

### 1. 绝对禁止买入约束

**规则**：当 CatBoost 预测概率 ≤ 0.50 时，绝对禁止买入。

**实现**：
```python
if ml_probability <= 0.50:
    recommendation = 'hold'  # 或 'sell'
    reason = 'ML 概率过低，违反硬性约束'
```

**测试**：集成测试 `test_hard_constraints()` 验证此约束。

### 2. 高概率推荐约束

**规则**：当 CatBoost 预测概率 ≥ 0.60 且预测为 1（上涨）时，推荐买入。

**实现**：
```python
if ml_probability >= 0.60 and ml_prediction == 1:
    recommendation = 'buy'
    reason = 'ML 概率高，推荐买入'
```

**测试**：集成测试 `test_hard_constraints()` 验证此约束。

### 3. 其他约束

- **止损止盈**：基于 ATR 计算（2倍 ATR）
- **风险回报比**：默认 1:1
- **置信度分级**：
  - 高：probability ≥ 0.60
  - 中：0.50 ≤ probability < 0.60
  - 低：probability < 0.50

## 测试覆盖率

### 覆盖率目标

- **总体覆盖率**：≥ 85%（当前：85%）
- **核心模块覆盖率**：≥ 70%
  - comprehensive_analysis.py: 92% ✅
  - data_services/excel_loader.py: 83% ✅
  - data_services/technical_analysis.py: 78% ✅
  - ml_services/base_model_processor.py: 74% ✅
  - ml_services/fx_trading_model.py: 91% ✅

### 测试统计

- **总测试数**：88 个
- **单元测试**：79 个
  - test_comprehensive_analysis.py: 4 个
  - test_excel_loader.py: 7 个
  - test_feature_engineering.py: 29 个
  - test_fx_trading_model.py: 6 个
  - test_technical_analysis.py: 33 个
- **集成测试**：9 个
  - test_end_to_end_workflow: 端到端工作流
  - test_multiple_pairs_workflow: 多货币对工作流
  - test_hard_constraints: 硬性约束验证
  - test_data_leakage_prevention: 数据泄漏防范验证
  - test_error_handling_and_edge_cases: 错误处理和边界情况
  - test_model_consistency: 模型一致性
  - test_feature_importance_and_count: 特征数量和类型
  - test_technical_indicator_validation: 技术指标有效性验证
  - test_full_system_with_all_pairs: 完整系统测试

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_integration.py -v

# 运行测试并生成覆盖率报告
pytest tests/ --cov=. --cov-report=html --cov-report=term

# 查看覆盖率 HTML 报告
# 报告位置：htmlcov/index.html
```

## 日志配置

### 日志级别

- **INFO**：一般信息（如模型训练、预测）
- **WARNING**：警告信息（如模型不存在、数据不足）
- **ERROR**：错误信息（如数据加载失败）

### 日志格式

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### 配置位置

日志配置在 `config.py` 中：

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 日志输出

- **控制台输出**：实时显示
- **文件输出**：`fx_predict.log`（如果需要）

## 特征工程

### 特征类别

1. **价格衍生特征**（6个）：
   - Close_change_1d/5d/20d：价格变化
   - Return_1d/5d/20d：收益率

2. **偏离率特征**（3个）：
   - Bias_5/10/20：价格相对于均线的偏离程度

3. **波动率特征**（2个）：
   - Volatility_5d/20d：标准差/均价

4. **滞后特征**（3个）：
   - Close_lag_1/5/20：历史价格

5. **趋势斜率特征**（1个）：
   - Trend_Slope_20：线性回归斜率

6. **市场环境特征**（1个）：
   - MA_Alignment：均线排列强度

### 特征验证

集成测试 `test_feature_importance_and_count()` 验证：
- 特征数量 ≥ 10
- 包含所有特征类别
- 特征值无无穷大值

## 模型配置

### CatBoost 参数

```python
{
    'iterations': 1000,
    'depth': 6,
    'learning_rate': 0.05,
    'l2_leaf_reg': 3,
    'random_seed': 42,
    'verbose': False,
    'loss_function': 'Logloss',
    'eval_metric': 'Accuracy'
}
```

### 预测周期

- **默认**：20 天
- **可配置**：通过 `--horizon` 参数调整

### 数据分割

- **训练集**：80%
- **验证集**：20%
- **分割方式**：时间序列分割（不混洗）

## 常见问题

### 1. 数据文件格式

Excel 文件必须满足：
- 工作表名称为货币对代码（如 EUR、JPY）
- 包含 `Date` 和 `Close` 列
- 可选：`High`、`Low`、`Open` 列（系统会自动生成）
- 日期格式：MM/DD/YYYY

### 2. 模型训练失败

可能原因：
- 数据点不足（至少需要 100 条）
- 缺少必要的列
- 数据格式错误

解决方案：
- 检查数据文件格式
- 确保数据量充足
- 查看日志输出

### 3. 测试失败

可能原因：
- 数据文件不存在
- 依赖未安装
- 环境配置错误

解决方案：
```bash
# 安装依赖
pip install -r requirements.txt

# 检查数据文件
ls -la FXRate_20260320.xlsx

# 运行单个测试查看详细错误
pytest tests/test_integration.py::test_end_to_end_workflow -v -s
```

### 4. 大模型不可用

如果未配置 `QWEN_API_KEY`，大模型功能将不可用，但不影响核心功能（ML 预测和技术分析）。

## 开发者

- **创建时间**：2026-03-25
- **版本**：1.0 (MVP)
- **Python 版本**：3.10+
- **框架**：CatBoost, Pandas, NumPy

## 许可证

本项目仅供学习和研究使用。