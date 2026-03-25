# FX Predict 阶段 2 设计文档

**日期**: 2026-03-25
**版本**: 2.0
**状态**: 待审查
**上一版本**: 1.0 (MVP)

---

## 1. 项目概述

在阶段 1 MVP 的基础上，阶段 2 重点关注**提升模型性能**和**增强系统功能**，通过多周期模型、Walk-forward 验证、回测系统和性能监控，构建一个更加可靠和可扩展的外汇预测系统。

### 1.1 核心目标

- **多周期模型**：实现 1 天、5 天、20 天三个独立的 CatBoost 模型
- **Walk-forward 验证**：真实评估模型预测能力，避免过拟合
- **回测系统**：验证交易策略的有效性，计算关键性能指标
- **性能监控**：追踪模型预测性能，支持持续优化

### 1.2 实施策略

采用**平衡推进**方法，分两个阶段实施：

| 阶段 | 内容 | 周期 | 目标 |
|------|------|------|------|
| **阶段 2.1** | 多周期模型 + Walk-forward 验证 | 2-3 周 | 提升模型性能和可靠性 |
| **阶段 2.2** | 回测系统 + 性能监控 | 2-3 周 | 增强系统功能和分析能力 |

---

## 2. 系统架构

### 2.1 目录结构（新增部分）

```
fx_predict/
├── ml_services/
│   ├── fx_trading_model.py        # 扩展支持多周期
│   ├── walk_forward_validator.py  # 新增：Walk-forward 验证器
│   ├── backtest_engine.py          # 新增：回测引擎
│   └── performance_monitor.py      # 新增：性能监控器
├── data/
│   ├── predictions/                # 预测历史
│   │   ├── EUR_1d_predictions.csv
│   │   ├── EUR_5d_predictions.csv
│   │   └── EUR_20d_predictions.csv
│   └── performance/                # 性能报告
│       ├── weekly_report.csv
│       └── monthly_report.csv
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-03-25-fx-predict-phase2-design.md
```

### 2.2 分层架构（更新）

| 层级 | 模块 | 职责 |
|------|------|------|
| **数据层** | `fx_data_loader.py` | Excel 数据加载、预处理 |
| **特征层** | `technical_analysis.py` | 计算技术指标、生成特征 |
| **模型层** | `fx_trading_model.py` | 多周期 CatBoost 训练、预测 |
| **验证层** | `walk_forward_validator.py` | Walk-forward 验证 |
| **回测层** | `backtest_engine.py` | 交易策略回测 |
| **监控层** | `performance_monitor.py` | 性能追踪和报告 |
| **整合层** | `comprehensive_analysis.py` | 整合多周期预测结果 |
| **接口层** | `qwen_engine.py` | 大模型调用 |

---

## 3. 核心组件设计

### 3.1 多周期模型设计

#### 3.1.1 目标

实现 1 天、5 天、20 天三个独立的 CatBoost 模型，提供不同时间视角的预测。

#### 3.1.2 模型架构

**模型独立性**：
- 每个周期训练独立的 CatBoost 模型
- 模型文件命名：`{pair}_model_{horizon}d.pkl`
  - 例如：`EUR_model_1d.pkl`、`EUR_model_5d.pkl`、`EUR_model_20d.pkl`
- 共 3 个模型 × 6 个货币对 = 18 个模型文件

**模型配置**：
```python
MULTI_HORIZON_CONFIG = {
    'horizons': [1, 5, 20],           # 支持的预测周期
    'default_horizon': 20,            # 默认周期
    'model_params': {
        1: {
            'iterations': 500,
            'depth': 4,
            'learning_rate': 0.05,
            'l2_leaf_reg': 3
        },
        5: {
            'iterations': 800,
            'depth': 5,
            'learning_rate': 0.05,
            'l2_leaf_reg': 3
        },
        20: {
            'iterations': 1000,
            'depth': 6,
            'learning_rate': 0.05,
            'l2_leaf_reg': 3
        }
    }
}
```

#### 3.1.3 接口设计

**扩展 `FXTradingModel` 类**：

```python
class FXTradingModel:
    """外汇交易模型（支持多周期）"""

    def __init__(self, config: dict = None, horizon: int = 20):
        """
        初始化模型

        Args:
            config: 模型配置字典
            horizon: 预测周期（天）- 新增参数
        """
        self.horizon = horizon
        # ... 其他初始化

    def train(self, pair: str, data: pd.DataFrame, horizon: int = None) -> dict:
        """
        训练模型

        Args:
            pair: 货币对代码
            data: 训练数据
            horizon: 预测周期（可选，默认使用实例的 horizon）

        Returns:
            训练指标字典
        """

    def predict(self, pair: str, data: pd.DataFrame, horizon: int = None) -> dict:
        """
        预测

        Args:
            pair: 货币对代码
            data: 预测数据
            horizon: 预测周期（可选，默认使用实例的 horizon）

        Returns:
            预测结果字典
        """
```

**扩展 `FeatureEngineer` 类**：

```python
class FeatureEngineer:
    """特征工程（支持多周期）"""

    def create_target(self, df: pd.DataFrame, horizon: int = 20) -> pd.Series:
        """
        创建目标变量：未来 horizon 天的涨跌

        Args:
            df: 原始数据
            horizon: 预测周期（天）- 支持不同周期

        Returns:
            目标序列（1=上涨, 0=下跌）
        """
        future_price = df['Close'].shift(-horizon)
        target = (future_price > df['Close']).astype(int)
        target.iloc[-horizon:] = np.nan
        return target
```

#### 3.1.4 使用示例

```python
# 训练多周期模型
model_1d = FXTradingModel(horizon=1)
model_5d = FXTradingModel(horizon=5)
model_20d = FXTradingModel(horizon=20)

model_1d.train('EUR', data)
model_5d.train('EUR', data)
model_20d.train('EUR', data)

# 预测
pred_1d = model_1d.predict('EUR', latest_data)
pred_5d = model_5d.predict('EUR', latest_data)
pred_20d = model_20d.predict('EUR', latest_data)

print(f"1天预测: {pred_1d['prediction']} (概率: {pred_1d['probability']:.2f})")
print(f"5天预测: {pred_5d['prediction']} (概率: {pred_5d['probability']:.2f})")
print(f"20天预测: {pred_20d['prediction']} (概率: {pred_20d['probability']:.2f})")
```

---

### 3.2 Walk-forward 验证设计

#### 3.2.1 目标

实现标准 Walk-forward 验证框架，真实评估模型预测能力，避免过拟合。

#### 3.2.2 验证策略

**标准 Walk-forward 验证**：
- 训练窗口：200 个交易日（约 10 个月）
- 预测窗口：20 个交易日（约 1 个月）
- 滚动步长：20 个交易日（每次移动 20 天）

**数据流示例**：
```
数据: [0, 1000]

第1轮:
  训练: [0, 200]
  预测: [200, 220]

第2轮:
  训练: [20, 220]
  预测: [220, 240]

第3轮:
  训练: [40, 240]
  预测: [240, 260]

...
```

#### 3.2.3 核心模块

**`WalkForwardValidator` 类设计**：

```python
class WalkForwardValidator:
    """Walk-forward 验证器"""

    def __init__(self, model: FXTradingModel,
                 train_window: int = 200,
                 test_window: int = 20,
                 step_size: int = 20):
        """
        初始化验证器

        Args:
            model: 待验证的模型
            train_window: 训练窗口大小
            test_window: 测试窗口大小
            step_size: 滚动步长
        """
        self.model = model
        self.train_window = train_window
        self.test_window = test_window
        self.step_size = step_size

    def validate(self, pair: str, data: pd.DataFrame) -> dict:
        """
        执行 Walk-forward 验证

        Args:
            pair: 货币对代码
            data: 完整数据集

        Returns:
            验证结果字典，包含：
            - predictions: 所有预测结果
            - actuals: 所有实际结果
            - metrics: 性能指标
            - detailed_results: 每一轮的详细结果
        """

    def _split_data(self, data: pd.DataFrame) -> list:
        """
        生成训练-测试分割

        Returns:
            分割列表 [(train_start, train_end, test_start, test_end), ...]
        """

    def _calculate_metrics(self, predictions: np.ndarray,
                          actuals: np.ndarray) -> dict:
        """
        计算性能指标

        Returns:
            性能指标字典
        """
```

#### 3.2.4 性能指标

**分类指标**：
- 准确率（Accuracy）
- 精确率（Precision）
- 召回率（Recall）
- F1 分数（F1 Score）
- AUC-ROC

**金融指标**：
- 最大回撤（Maximum Drawdown）
- 夏普比率（Sharpe Ratio）
- 信息比率（Information Ratio）
- 卡尔玛比率（Calmar Ratio）

#### 3.2.5 使用示例

```python
# 创建验证器
validator = WalkForwardValidator(
    model=FXTradingModel(horizon=20),
    train_window=200,
    test_window=20,
    step_size=20
)

# 执行验证
results = validator.validate('EUR', data)

# 输出性能指标
print(f"准确率: {results['metrics']['accuracy']:.2%}")
print(f"精确率: {results['metrics']['precision']:.2%}")
print(f"召回率: {results['metrics']['recall']:.2%}")
print(f"F1 分数: {results['metrics']['f1']:.2f}")

# 生成性能报告
validator.generate_report(results, 'performance_report.md')
```

---

### 3.3 回测系统设计

#### 3.3.1 目标

验证交易策略的有效性，计算关键性能指标，评估策略盈利能力。

#### 3.3.2 交易策略

**买入信号**：
- ML 预测上涨（prediction = 1）
- 预测概率 ≥ 0.60（高置信度）
- 技术信号支持（可选）

**卖出信号**：
- ML 预测下跌（prediction = 0）
- 达到止盈位（entry_price + take_profit）
- 达到止损位（entry_price - stop_loss）

**仓位管理**：
- 固定仓位：每次交易固定金额
- 风险比例仓位：根据 ATR 计算风险敞口

#### 3.3.3 核心模块

**`BacktestEngine` 类设计**：

```python
class BacktestEngine:
    """回测引擎"""

    def __init__(self, initial_capital: float = 10000,
                 position_size: float = 0.1):
        """
        初始化回测引擎

        Args:
            initial_capital: 初始资金
            position_size: 仓位比例（0-1）
        """
        self.initial_capital = initial_capital
        self.position_size = position_size
        self.trades = []

    def run_backtest(self, pair: str, data: pd.DataFrame,
                    predictions: pd.DataFrame) -> dict:
        """
        运行回测

        Args:
            pair: 货币对代码
            data: 价格数据
            predictions: 预测结果

        Returns:
            回测结果字典
        """

    def _execute_trade(self, signal: str, price: float, date: str):
        """执行交易"""

    def _calculate_performance(self) -> dict:
        """计算性能指标"""

    def _generate_report(self) -> dict:
        """生成回测报告"""
```

#### 3.3.4 回测输出

**交易日志**：
```
日期 | 类型 | 价格 | 数量 | 盈亏 | 累计盈亏
2026-01-01 | 买入 | 1.0850 | 1000 | - | -
2026-01-05 | 卖出 | 1.0880 | 1000 | +30 | +30
...
```

**性能图表**：
- 净值曲线
- 回撤曲线
- 每月收益分布

**统计报告**：
- 总收益率
- 年化收益率
- 胜率
- 平均盈亏比
- 最大回撤
- 夏普比率

---

### 3.4 性能监控系统设计

#### 3.4.1 目标

追踪模型预测性能，支持持续优化，识别性能下降的信号。

#### 3.4.2 核心功能

**数据存储**：
- 预测历史表：`{pair}_{horizon}d_predictions.csv`
- 实际结果表：`{pair}_{horizon}d_actuals.csv`
- 性能指标表：`performance_metrics.csv`

**监控指标**：
- 预测准确率（滚动 30/60/90 天）
- 预测概率分布
- 不同置信度下的准确率
- 模型性能趋势

#### 3.4.3 核心模块

**`PerformanceMonitor` 类设计**：

```python
class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, storage_dir: str = 'data/performance'):
        """
        初始化监控器

        Args:
            storage_dir: 存储目录
        """
        self.storage_dir = Path(storage_dir)

    def log_prediction(self, pair: str, horizon: int,
                     prediction: dict, date: str):
        """记录预测结果"""

    def log_actual(self, pair: str, horizon: int,
                  actual: int, date: str):
        """记录实际结果"""

    def calculate_metrics(self, pair: str, horizon: int,
                        window: int = 30) -> dict:
        """计算性能指标"""

    def generate_report(self, pair: str, horizon: int,
                      report_type: str = 'weekly') -> dict:
        """生成性能报告"""
```

#### 3.4.4 报告生成

**每周报告**：
- 过去 7 天的预测准确率
- 预测概率分布
- 置信度分析

**每月报告**：
- 过去 30 天的详细性能指标
- 模型性能趋势
- 重新训练建议

---

## 4. 数据流设计

### 4.1 完整数据流

```
┌─────────────────────────────────────────────────────────────┐
│                    阶段 2 数据流图                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Excel 文件                                                  │
│  FXRate_*.xlsx                                              │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────┐                                        │
│  │ FXDataLoader    │                                        │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │TechnicalAnalyzer│                                       │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │ FeatureEngineer │                                        │
│  └────────┬────────┘                                        │
│           │                                                 │
│    ┌──────┴──────┐                                          │
│    │             │                                          │
│    ▼             ▼                                          │
│ ┌────────┐  ┌─────────┐                                    │
│ │训练1天  │  │训练5天  │                                    │
│ │ 模型   │  │ 模型   │                                    │
│ └────────┘  └─────────┘                                    │
│    │             │                                          │
│    └──────┬──────┘                                          │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │训练20天模型    │                                        │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ├──────────────────┐                             │
│           ▼                  ▼                             │
│  ┌─────────────────┐  ┌──────────────┐                    │
│  │ WalkForward     │  │ 回测系统      │                    │
│  │ Validator       │  │ BacktestEngine│                    │
│  └────────┬────────┘  └──────┬───────┘                    │
│           │                  │                              │
│           └────────┬─────────┘                              │
│                    ▼                                        │
│        ┌──────────────────┐                                 │
│        │ 性能监控         │                                 │
│        │ PerformanceMonitor│                               │
│        └──────────────────┘                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 关键数据流

#### 4.2.1 多周期模型训练流程

```
数据加载 → 技术指标 → 特征工程 → 创建多周期目标
  ↓
训练 1 天模型 (model_1d.pkl)
训练 5 天模型 (model_5d.pkl)
训练 20 天模型 (model_20d.pkl)
  ↓
保存所有模型到 data/models/
```

#### 4.2.2 Walk-forward 验证流程

```
完整数据集
  ↓
生成训练-测试分割（200天训练 + 20天测试，滚动）
  ↓
每一轮：
  - 训练模型
  - 预测测试集
  - 记录预测和实际结果
  ↓
汇总所有预测结果
  ↓
计算性能指标（准确率、精确率、召回率、F1）
  ↓
生成验证报告
```

#### 4.2.3 回测流程

```
预测结果 + 价格数据
  ↓
应用交易策略
  ↓
执行交易（买入/卖出）
  ↓
计算盈亏
  ↓
计算性能指标（收益率、最大回撤、夏普比率）
  ↓
生成回测报告
```

#### 4.2.4 性能监控流程

```
新预测
  ↓
记录到预测历史表
  ↓
获取实际结果
  ↓
记录到实际结果表
  ↓
计算滚动性能指标（30/60/90天）
  ↓
生成性能报告
  ↓
识别性能下降信号
  ↓
发送重新训练建议
```

---

## 5. 配置管理

### 5.1 更新配置文件（config.py）

```python
# 多周期配置
MULTI_HORIZON_CONFIG = {
    'horizons': [1, 5, 20],
    'default_horizon': 20,
    'model_params': {
        1: {
            'iterations': 500,
            'depth': 4,
            'learning_rate': 0.05,
            'l2_leaf_reg': 3
        },
        5: {
            'iterations': 800,
            'depth': 5,
            'learning_rate': 0.05,
            'l2_leaf_reg': 3
        },
        20: {
            'iterations': 1000,
            'depth': 6,
            'learning_rate': 0.05,
            'l2_leaf_reg': 3
        }
    }
}

# Walk-forward 验证配置
WALK_FORWARD_CONFIG = {
    'train_window': 200,      # 训练窗口大小
    'test_window': 20,        # 测试窗口大小
    'step_size': 20,          # 滚动步长
    'min_data_points': 400    # 最小数据点数
}

# 回测配置
BACKTEST_CONFIG = {
    'initial_capital': 10000,  # 初始资金
    'position_size': 0.1,      # 仓位比例
    'transaction_cost': 0.0002, # 交易成本（0.02%）
    'slippage': 0.0001        # 滑点（0.01%）
}

# 性能监控配置
PERFORMANCE_MONITOR_CONFIG = {
    'storage_dir': 'data/performance',
    'report_intervals': {
        'daily': 1,
        'weekly': 7,
        'monthly': 30
    },
    'performance_thresholds': {
        'accuracy_warning': 0.50,
        'accuracy_critical': 0.45
    }
}

# 交易策略配置
TRADING_STRATEGY_CONFIG = {
    'buy_threshold': 0.60,      # 买入概率阈值
    'confidence_levels': {
        'high': 0.70,
        'medium': 0.60,
        'low': 0.50
    },
    'stop_loss_atr_multiplier': 2.0,   # 止损 ATR 倍数
    'take_profit_atr_multiplier': 2.0  # 止盈 ATR 倍数
}
```

---

## 6. 错误处理策略

### 6.1 新增异常类型

| 异常类型 | 处理策略 |
|---------|---------|
| `InsufficientDataError` | 数据不足，提示用户 |
| `ModelTrainingError` | 模型训练失败，记录详情并降级 |
| `ValidationError` | 验证失败，提供诊断信息 |
| `BacktestError` | 回测失败，检查数据一致性 |
| `PerformanceMonitorError` | 监控失败，记录警告 |

### 6.2 错误处理示例

```python
# Walk-forward 验证错误处理
try:
    results = validator.validate('EUR', data)
except InsufficientDataError as e:
    logger.error(f"数据不足进行验证: {e}")
    logger.info("建议: 至少需要 400 个数据点")
    return None
except ValidationError as e:
    logger.error(f"验证失败: {e}")
    # 生成诊断报告
    validator.generate_diagnostic_report()
    return None

# 回测错误处理
try:
    backtest_results = engine.run_backtest('EUR', data, predictions)
except BacktestError as e:
    logger.error(f"回测失败: {e}")
    # 检查数据一致性
    if not engine._validate_data_consistency(data, predictions):
        logger.error("数据和预测不一致")
    return None

# 性能监控错误处理
try:
    monitor.log_prediction(pair, horizon, prediction, date)
except PerformanceMonitorError as e:
    logger.warning(f"记录预测失败: {e}")
    # 继续执行，不影响主要功能
```

---

## 7. 测试策略

### 7.1 单元测试

```python
# tests/test_multi_horizon.py
def test_train_multi_horizon_models():
    """测试训练多周期模型"""
    model_1d = FXTradingModel(horizon=1)
    model_5d = FXTradingModel(horizon=5)
    model_20d = FXTradingModel(horizon=20)

    model_1d.train('EUR', data)
    model_5d.train('EUR', data)
    model_20d.train('EUR', data)

    assert model_1d.model is not None
    assert model_5d.model is not None
    assert model_20d.model is not None

def test_predict_multi_horizon():
    """测试多周期预测"""
    model = FXTradingModel(horizon=20)
    pred_1d = model.predict('EUR', data, horizon=1)
    pred_5d = model.predict('EUR', data, horizon=5)
    pred_20d = model.predict('EUR', data, horizon=20)

    assert 'prediction' in pred_1d
    assert 'prediction' in pred_5d
    assert 'prediction' in pred_20d

# tests/test_walk_forward.py
def test_walk_forward_validation():
    """测试 Walk-forward 验证"""
    validator = WalkForwardValidator(
        model=FXTradingModel(horizon=20),
        train_window=200,
        test_window=20,
        step_size=20
    )

    results = validator.validate('EUR', data)

    assert 'predictions' in results
    assert 'actuals' in results
    assert 'metrics' in results
    assert results['metrics']['accuracy'] >= 0

# tests/test_backtest.py
def test_backtest_engine():
    """测试回测引擎"""
    engine = BacktestEngine(
        initial_capital=10000,
        position_size=0.1
    )

    results = engine.run_backtest('EUR', data, predictions)

    assert 'final_capital' in results
    assert 'total_return' in results
    assert 'metrics' in results

# tests/test_performance_monitor.py
def test_performance_monitor():
    """测试性能监控"""
    monitor = PerformanceMonitor()

    monitor.log_prediction('EUR', 20, prediction, '2026-03-25')
    monitor.log_actual('EUR', 20, 1, '2026-04-14')

    metrics = monitor.calculate_metrics('EUR', 20, window=30)

    assert 'accuracy' in metrics
    assert 0 <= metrics['accuracy'] <= 1
```

### 7.2 集成测试

```python
# tests/test_integration_phase2.py
def test_end_to_end_multi_horizon():
    """端到端多周期模型测试"""
    # 1. 训练多周期模型
    model_1d = FXTradingModel(horizon=1)
    model_5d = FXTradingModel(horizon=5)
    model_20d = FXTradingModel(horizon=20)

    model_1d.train('EUR', data)
    model_5d.train('EUR', data)
    model_20d.train('EUR', data)

    # 2. Walk-forward 验证
    validator = WalkForwardValidator(model=model_20d)
    results = validator.validate('EUR', data)

    # 3. 回测
    engine = BacktestEngine()
    backtest_results = engine.run_backtest('EUR', data, predictions)

    # 4. 性能监控
    monitor = PerformanceMonitor()
    monitor.log_prediction('EUR', 20, prediction, date)
    monitor.log_actual('EUR', 20, actual, future_date)
    metrics = monitor.calculate_metrics('EUR', 20)

    assert results['metrics']['accuracy'] >= 0.55
    assert backtest_results['total_return'] > 0
    assert metrics['accuracy'] >= 0.5
```

### 7.3 测试覆盖率

```bash
# 目标覆盖率
# - 核心模块：≥ 75%
# - 新增模块：≥ 80%
# - 集成测试：覆盖主要流程
```

---

## 8. 实施计划

### 8.1 阶段 2.1：多周期模型 + Walk-forward 验证（2-3 周）

#### Week 1-2：多周期模型

**Task 1：扩展 FXTradingModel 支持多周期**
- [ ] 添加 `horizon` 参数到 `__init__`
- [ ] 修改 `train` 方法支持 `horizon` 参数
- [ ] 修改 `predict` 方法支持 `horizon` 参数
- [ ] 更新模型文件命名规范
- [ ] 单元测试
- [ ] 提交

**Task 2：扩展 FeatureEngineer 支持多周期**
- [ ] 修改 `create_target` 方法支持可变 `horizon`
- [ ] 验证目标变量正确性
- [ ] 单元测试
- [ ] 提交

**Task 3：实现多周期模型训练脚本**
- [ ] 创建 `train_multi_horizon.py` 脚本
- [ ] 支持命令行参数 `--horizon`
- [ ] 批量训练所有货币对
- [ ] 集成测试
- [ ] 提交

**Task 4：集成到综合分析系统**
- [ ] 更新 `ComprehensiveAnalyzer` 支持多周期
- [ ] 整合多周期预测结果
- [ ] 更新输出格式
- [ ] 集成测试
- [ ] 提交

#### Week 3：Walk-forward 验证

**Task 5：实现 WalkForwardValidator 类**
- [ ] 实现数据分割逻辑
- [ ] 实现验证循环
- [ ] 实现性能指标计算
- [ ] 实现报告生成
- [ ] 单元测试
- [ ] 提交

**Task 6：集成到模型训练流程**
- [ ] 添加验证选项到训练脚本
- [ ] 自动生成验证报告
- [ ] 集成测试
- [ ] 提交

**Task 7：文档更新**
- [ ] 更新 AGENTS.md
- [ ] 添加使用示例
- [ ] 提交

### 8.2 阶段 2.2：回测系统 + 性能监控（2-3 周）

#### Week 4：回测系统

**Task 8：实现 BacktestEngine 类**
- [ ] 实现交易执行逻辑
- [ ] 实现盈亏计算
- [ ] 实现性能指标计算
- [ ] 实现报告生成
- [ ] 单元测试
- [ ] 提交

**Task 9：集成回测系统**
- [ ] 添加回测选项到主脚本
- [ ] 生成回测报告
- [ ] 集成测试
- [ ] 提交

#### Week 5：性能监控

**Task 10：实现 PerformanceMonitor 类**
- [ ] 实现预测记录
- [ ] 实现实际结果记录
- [ ] 实现性能指标计算
- [ ] 实现报告生成
- [ ] 单元测试
- [ ] 提交

**Task 11：集成性能监控**
- [ ] 添加监控选项到主脚本
- [ ] 自动生成性能报告
- [ ] 集成测试
- [ ] 提交

#### Week 6：集成和优化

**Task 12：端到端集成测试**
- [ ] 完整流程测试
- [ ] 多货币对测试
- [ ] 性能测试
- [ ] 提交

**Task 13：文档更新**
- [ ] 更新 AGENTS.md
- [ ] 更新 progress.txt
- [ ] 更新 lessons.md
- [ ] 提交

**Task 14：代码优化**
- [ ] 性能优化
- [ ] 代码重构
- [ ] 测试覆盖率提升
- [ ] 提交

---

## 9. 依赖更新

### 9.1 requirements.txt 更新

```txt
# 现有依赖保持不变
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0
python-dotenv>=1.0.0
catboost>=1.2.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
requests>=2.31.0
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.7.0

# 新增依赖（阶段 2）
# 回测相关
pandas-ta>=0.3.14b0        # 技术分析库

# 性能监控
sqlite3                    # Python 内置，无需安装

# 报告生成
jinja2>=3.1.0              # 模板引擎
```

---

## 10. 使用示例

### 10.1 训练多周期模型

```bash
# 训练单个货币对的所有周期模型
python3 ml_services/fx_trading_model.py \
    --mode train \
    --pair EUR \
    --horizons 1,5,20

# 训练所有货币对的所有周期模型
python3 ml_services/fx_trading_model.py \
    --mode train \
    --horizons 1,5,20
```

### 10.2 Walk-forward 验证

```bash
# 对 20 天模型进行 Walk-forward 验证
python3 ml_services/fx_trading_model.py \
    --mode validate \
    --pair EUR \
    --horizon 20 \
    --train-window 200 \
    --test-window 20 \
    --step-size 20
```

### 10.3 回测

```bash
# 运行回测
python3 ml_services/backtest_engine.py \
    --pair EUR \
    --horizon 20 \
    --initial-capital 10000 \
    --position-size 0.1
```

### 10.4 性能监控

```bash
# 生成性能报告
python3 ml_services/performance_monitor.py \
    --pair EUR \
    --horizon 20 \
    --report-type monthly
```

### 10.5 Python API

```python
from ml_services.fx_trading_model import FXTradingModel
from ml_services.walk_forward_validator import WalkForwardValidator
from ml_services.backtest_engine import BacktestEngine
from ml_services.performance_monitor import PerformanceMonitor

# 1. 训练多周期模型
model_1d = FXTradingModel(horizon=1)
model_5d = FXTradingModel(horizon=5)
model_20d = FXTradingModel(horizon=20)

model_1d.train('EUR', data)
model_5d.train('EUR', data)
model_20d.train('EUR', data)

# 2. Walk-forward 验证
validator = WalkForwardValidator(model=model_20d)
results = validator.validate('EUR', data)
print(f"准确率: {results['metrics']['accuracy']:.2%}")

# 3. 回测
engine = BacktestEngine(initial_capital=10000)
backtest_results = engine.run_backtest('EUR', data, predictions)
print(f"总收益率: {backtest_results['total_return']:.2%}")

# 4. 性能监控
monitor = PerformanceMonitor()
monitor.log_prediction('EUR', 20, prediction, '2026-03-25')
monitor.log_actual('EUR', 20, 1, '2026-04-14')
metrics = monitor.calculate_metrics('EUR', 20)
print(f"30天准确率: {metrics['accuracy']:.2%}")
```

---

## 11. 成功标准

### 11.1 阶段 2.1 成功标准

| 指标 | 目标 | 验证方法 |
|------|------|---------|
| **多周期模型** | 3 个周期模型全部训练完成 | 单元测试 |
| **Walk-forward 验证** | 生成完整的验证报告 | 集成测试 |
| **模型准确率** | ≥ 55%（基准） | Walk-forward 验证 |
| **测试覆盖率** | ≥ 75% | pytest-cov |

### 11.2 阶段 2.2 成功标准

| 指标 | 目标 | 验证方法 |
|------|------|---------|
| **回测系统** | 正常运行，生成报告 | 集成测试 |
| **性能监控** | 数据收集正常 | 单元测试 |
| **报告生成** | 月度/周报告自动生成 | 手动验证 |
| **测试覆盖率** | ≥ 80% | pytest-cov |

### 11.3 整体成功标准

- 所有 14 个任务完成
- 所有测试通过
- 文档完整更新
- 代码提交到 GitHub
- 测试覆盖率 ≥ 75%
- Walk-forward 验证准确率 ≥ 55%

---

## 12. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| **训练时间过长** | 开发效率低 | 1. 并行训练多个模型<br>2. 使用更少的迭代次数<br>3. 在更小的数据集上验证 |
| **数据不足** | 验证结果不可靠 | 1. 使用数据增强（滑动窗口）<br>2. 减小训练窗口大小<br>3. 收集更多历史数据 |
| **模型性能下降** | 预测能力下降 | 1. 实现自动监控<br>2. 设置性能阈值警告<br>3. 自动触发重新训练 |
| **回测过拟合** | 实际交易效果差 | 1. 使用 Walk-forward 验证<br>2. 考虑交易成本和滑点<br>3. 使用样本外数据测试 |
| **性能监控数据过大** | 存储和性能问题 | 1. 使用数据库而非 CSV<br>2. 定期清理旧数据<br>3. 数据压缩 |

---

## 13. 与阶段 1 的兼容性

### 13.1 向后兼容

- 保持现有的 `FXTradingModel` 接口不变（`horizon=20` 为默认值）
- 现有的训练和预测脚本继续工作
- 现有的配置文件保持兼容

### 13.2 渐进式升级

- 新功能作为可选功能添加
- 用户可以选择使用新功能或继续使用旧功能
- 文档清楚标注新功能

---

## 14. 下一阶段规划（阶段 3）

### 14.1 潜在功能

| 功能模块 | 描述 | 优先级 |
|---------|------|--------|
| **实时数据源** | 集成在线外汇数据源 | 高 |
| **Web UI** | 可视化仪表板 | 中 |
| **API 服务** | RESTful API 接口 | 中 |
| **更多货币对** | 扩展到 10+ 货币对 | 低 |
| **多时间周期** | 小时级、分钟级预测 | 低 |

### 14.2 实施顺序

1. **实时数据源**（2-3 周）
2. **API 服务**（2 周）
3. **Web UI**（3-4 周）

---

## 15. 设计总结

### 15.1 阶段 2 核心交付物

1. **多周期模型**（3 个独立模型）
   - 1 天模型（model_1d.pkl）
   - 5 天模型（model_5d.pkl）
   - 20 天模型（model_20d.pkl）

2. **Walk-forward 验证**
   - `WalkForwardValidator` 类
   - 验证报告生成
   - 性能指标计算

3. **回测系统**
   - `BacktestEngine` 类
   - 交易策略实现
   - 回测报告生成

4. **性能监控**
   - `PerformanceMonitor` 类
   - 预测历史存储
   - 性能报告生成

5. **完整文档**
   - 代码注释
   - 使用示例
   - 测试用例

### 15.2 设计原则

- **渐进式增强**：在 MVP 基础上添加新功能
- **向后兼容**：保持现有接口不变
- **模块化设计**：每个新功能独立模块
- **可测试性**：完整的单元测试和集成测试
- **可扩展性**：预留接口支持未来扩展

---

**文档结束**
---

## 16. 一体化脚本设计

### 16.1 目标

提供一键式脚本，一次性完成训练、预测和报告生成，简化用户使用流程。

### 16.2 脚本设计

**脚本名称**：`run_pipeline.py`

**功能流程**：
```
1. 加载数据（Excel 文件）
2. 训练多周期模型（1天/5天/20天）
3. 预测最新数据
4. 综合分析（技术信号 + ML 预测）
5. 调用 LLM 生成分析解释
6. 生成完整报告（Markdown + CSV）
```

### 16.3 输出格式

**Markdown 报告**（`report_YYYYMMDD.md`）：

```markdown
# FX Predict 分析报告

生成时间：2026-03-25
报告类型：完整报告（多周期预测 + 技术分析 + LLM 解释）

---

## EUR/USD 分析

### 多周期预测

| 周期 | 预测 | 概率 | 置信度 | 建议 |
|------|------|------|--------|------|
| 1天 | 上涨 | 0.65 | 高 | 买入 |
| 5天 | 上涨 | 0.58 | 中 | 买入 |
| 20天 | 上涨 | 0.72 | 高 | 买入 |

### 技术指标分析

**趋势指标**：
- SMA5/SMA10/SMA20：多头排列
- EMA5 > EMA20：看涨趋势
- MACD：金叉，MACD 线上穿信号线

**动量指标**：
- RSI(14): 65.5（中性偏多）
- KDJ：K > D > J，超买区域
- ADX: 25（趋势强度中等）

**波动指标**：
- ATR(14): 0.0085
- 布林带：价格位于中轨附近

### 综合技术信号

**信号强度**: 75/100（强烈买入）

**信号来源**：
- RSI 超卖反转：+20
- 均线金叉：+15
- MACD 金叉：+10
- 多头排列：+10
- ADX 趋势确认：+5

### 交易建议

**建议**: 买入
**理由**: 多周期预测一致看涨，技术指标支撑，趋势强度中等

**入场价**: 1.0850
**止损位**: 1.0750（-0.0085 × 2）
**止盈位**: 1.0950（+0.0085 × 2）
**风险收益比**: 1:1

### LLM 分析

[通义千问生成的市场分析]

---

## JPY/USD 分析

[类似的格式...]

---

## 总体摘要

| 货币对 | 1天 | 5天 | 20天 | 综合建议 |
|--------|-----|-----|------|---------|
| EUR/USD | 上涨 | 上涨 | 上涨 | 买入 |
| JPY/USD | 下跌 | 观望 | 观望 | 观望 |
| AUD/USD | 上涨 | 上涨 | 上涨 | 买入 |
| GBP/USD | 观望 | 上涨 | 上涨 | 观望 |
| CAD/USD | 下跌 | 下跌 | 下跌 | 卖出 |
| NZD/USD | 观望 | 观望 | 上涨 | 观望 |

---

## 免责声明

本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。
```

**CSV 报告**（`predictions_YYYYMMDD.csv`）：

```csv
pair,horizon,prediction,probability,confidence,recommendation,entry_price,stop_loss,take_profit,analysis_date,target_date
EUR,1,1,0.65,high,buy,1.0850,1.0750,1.0950,2026-03-25,2026-03-26
EUR,5,1,0.58,medium,buy,1.0850,1.0750,1.0950,2026-03-25,2026-03-30
EUR,20,1,0.72,high,buy,1.0850,1.0750,1.0950,2026-03-25,2026-04-14
JPY,1,0,0.45,low,hold,149.50,150.00,149.00,2026-03-25,2026-03-26
JPY,5,0,0.50,medium,hold,149.50,150.00,149.00,2026-03-25,2026-03-30
JPY,20,0,0.52,medium,hold,149.50,150.00,149.00,2026-03-25,2026-04-14
...
```

### 16.4 命令行接口

```bash
# 运行完整流程（所有货币对，默认使用 Excel 文件）
python3 run_pipeline.py

# 指定数据文件
python3 run_pipeline.py --data FXRate_20260320.xlsx

# 指定货币对
python3 run_pipeline.py --data FXRate_20260320.xlsx --pairs EUR,JPY,AUD

# 指定输出目录
python3 run_pipeline.py --data FXRate_20260320.xlsx --output reports/

# 禁用 LLM（快速生成）
python3 run_pipeline.py --data FXRate_20260320.xlsx --no-llm

# 仅预测（不训练）
python3 run_pipeline.py --data FXRate_20260320.xlsx --skip-training

# 仅生成报告（使用已有模型）
python3 run_pipeline.py --data FXRate_20260320.xlsx --predict-only

# 详细模式（显示详细日志）
python3 run_pipeline.py --data FXRate_20260320.xlsx --verbose
```

### 16.5 参数说明

| 参数 | 说明 | 默认值 | 必需 |
|------|------|--------|------|
| `--data` | Excel 数据文件路径 | `FXRate_*.xlsx` | 否 |
| `--pairs` | 货币对列表（逗号分隔） | 所有支持的货币对 | 否 |
| `--horizons` | 预测周期（逗号分隔） | `1,5,20` | 否 |
| `--output` | 输出目录 | `data/predictions/` | 否 |
| `--no-llm` | 禁用 LLM 调用 | `False` | 否 |
| `--skip-training` | 跳过模型训练 | `False` | 否 |
| `--predict-only` | 仅预测，不训练 | `False` | 否 |
| `--verbose` | 详细模式 | `False` | 否 |

### 16.6 技术实现要点

#### 16.6.1 进度显示

```python
from tqdm import tqdm

# 并行训练多个模型
for pair in pairs:
    for horizon in horizons:
        with tqdm(total=100, desc=f"训练 {pair} {horizon}天模型") as pbar:
            model.train(pair, data, horizon=horizon)
            pbar.update(100)
```

#### 16.6.2 错误容忍

```python
# 单个模型失败不影响其他模型
for pair in pairs:
    for horizon in horizons:
        try:
            model.train(pair, data, horizon=horizon)
        except Exception as e:
            logger.error(f"训练 {pair} {horizon}天模型失败: {e}")
            continue
```

#### 16.6.3 增量更新

```python
# 如果模型已存在，跳过训练（可选）
def should_train(pair: str, horizon: int, force: bool = False) -> bool:
    if force:
        return True
    model_path = f"data/models/{pair}_model_{horizon}d.pkl"
    if Path(model_path).exists():
        logger.info(f"模型已存在，跳过训练: {model_path}")
        return False
    return True
```

### 16.7 使用示例

**Python API**：

```python
from run_pipeline import Pipeline

# 创建管道
pipeline = Pipeline(
    data_file='FXRate_20260320.xlsx',
    pairs=['EUR', 'JPY'],
    horizons=[1, 5, 20],
    output_dir='reports/'
)

# 运行完整流程
results = pipeline.run()

# 访问结果
for pair, pair_results in results.items():
    print(f"{pair}:")
    for horizon, pred in pair_results.items():
        print(f"  {horizon}天: {pred['recommendation']} (置信度: {pred['confidence']})")
```

### 16.8 成功标准

| 指标 | 目标 |
|------|------|
| 脚本可执行性 | 无错误完成所有步骤 |
| 报告完整性 | Markdown 和 CSV 都生成 |
| 报告准确性 | 所有预测数据正确 |
| 执行时间 | 5 分钟内完成（6 个货币对） |
| LLM 集成 | 成功生成分析解释（如果启用） |

---

