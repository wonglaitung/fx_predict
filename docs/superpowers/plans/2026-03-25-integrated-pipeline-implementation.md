# 一体化脚本和多周期模型实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现一键式脚本，一次性完成多周期模型训练、预测和完整报告生成

**Architecture:** 扩展现有 FXTradingModel 支持多周期（1天/5天/20天），创建一体化脚本 run_pipeline.py 整合训练、预测、分析和报告生成流程

**Tech Stack:** Python 3.10+, CatBoost, Pandas, Click, tqdm, jinja2

---

## 文件结构

### 修改的文件
- `ml_services/feature_engineering.py` - 扩展 `create_target()` 方法支持可变周期
- `ml_services/fx_trading_model.py` - 扩展支持多周期训练和预测
- `config.py` - 添加 MULTI_HORIZON_CONFIG 配置

### 新增的文件
- `run_pipeline.py` - 一体化脚本主文件
- `tests/test_multi_horizon.py` - 多周期模型测试
- `tests/test_run_pipeline.py` - 脚本集成测试

---

## Task 1: 更新配置文件

**Files:**
- Modify: `config.py:120-135`

- [ ] **Step 1: 添加多周期配置到 config.py**

在 `config.py` 中添加以下配置（在现有配置后）：

```python
# 多周期模型配置
MULTI_HORIZON_CONFIG = {
    'horizons': [1, 5, 20],           # 支持的预测周期（天）
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

# 报告配置
REPORT_CONFIG = {
    'output_dir': 'data/predictions',
    'markdown_template': 'report_template.md',
    'include_llm_analysis': True,
    'include_technical_indicators': True
}
```

- [ ] **Step 2: 验证配置文件语法**

运行：`python3 -c "from config import MULTI_HORIZON_CONFIG, REPORT_CONFIG; print('配置加载成功')"`
预期输出：`配置加载成功`

- [ ] **Step 3: 提交**

```bash
git add config.py
git commit -m "feat: 添加多周期模型和报告配置"
```

---

## Task 2: 扩展特征工程支持多周期

**Files:**
- Modify: `ml_services/feature_engineering.py:75-95`
- Test: `tests/test_feature_engineering.py`

- [ ] **Step 1: 编写多周期目标变量测试**

在 `tests/test_feature_engineering.py` 中添加：

```python
def test_create_target_multi_horizon():
    """测试创建不同周期的目标变量"""
    engineer = FeatureEngineer()
    
    # 创建测试数据
    prices = [1.0 + i * 0.01 for i in range(100)]
    df = pd.DataFrame({'Close': prices})
    
    # 测试 1 天周期
    target_1d = engineer.create_target(df, horizon=1)
    assert target_1d.iloc[-2] == 1  # 最后一个有效值应该是上涨
    assert target_1d.iloc[-1] is pd.NA  # 最后一个值应该是 NaN
    
    # 测试 5 天周期
    target_5d = engineer.create_target(df, horizon=5)
    assert target_5d.iloc[-6] is not pd.NA
    assert target_5d.iloc[-1] is pd.NA
    
    # 测试 20 天周期
    target_20d = engineer.create_target(df, horizon=20)
    assert target_20d.iloc[-21] is not pd.NA
    assert target_20d.iloc[-1] is pd.NA

def test_create_target_value_ranges():
    """测试目标变量取值范围"""
    engineer = FeatureEngineer()
    
    df = pd.DataFrame({'Close': [1.0 + i * 0.01 for i in range(100)]})
    
    for horizon in [1, 5, 20]:
        target = engineer.create_target(df, horizon=horizon)
        # 排除 NaN 值
        valid_target = target.dropna()
        assert valid_target.isin([0, 1]).all()
```

- [ ] **Step 2: 运行测试确认失败**

运行：`pytest tests/test_feature_engineering.py::test_create_target_multi_horizon -v`
预期：FAIL（方法尚未修改）

- [ ] **Step 3: 修改 create_target 方法**

在 `ml_services/feature_engineering.py` 中，找到 `create_target` 方法（约第 75 行），修改为：

```python
def create_target(self, df: pd.DataFrame, horizon: int = 20) -> pd.Series:
    """
    创建目标变量：未来 horizon 天的涨跌
    
    Args:
        df: 原始数据
        horizon: 预测周期（天），支持 1, 5, 20 等不同周期
    
    Returns:
        目标序列（1=上涨, 0=下跌）
    
    Notes:
        - 使用 shift(-horizon) 获取未来数据
        - **警告**：此方法仅用于训练阶段，预测阶段不可使用！
        - 预测时目标变量无法获取，应由模型预测生成
        - 最后 horizon 个值无法计算（没有未来数据），设为 NaN
    """
    future_price = df['Close'].shift(-horizon)
    target = (future_price > df['Close']).astype(int)
    
    # 最后 horizon 个值无法计算（没有未来数据）
    target.iloc[-horizon:] = np.nan
    
    self.logger.info(f"已创建 {horizon} 天周期目标变量，有效样本数: {target.notna().sum()}")
    
    return target
```

- [ ] **Step 4: 运行测试验证通过**

运行：`pytest tests/test_feature_engineering.py::test_create_target_multi_horizon tests/test_feature_engineering.py::test_create_target_value_ranges -v`
预期：PASS

- [ ] **Step 5: 提交**

```bash
git add ml_services/feature_engineering.py tests/test_feature_engineering.py
git commit -m "feat: 扩展特征工程支持多周期目标变量"
```

---

## Task 3: 扩展 FXTradingModel 支持多周期

**Files:**
- Modify: `ml_services/fx_trading_model.py:15-35, 60-90, 120-150`
- Test: `tests/test_multi_horizon.py`

- [ ] **Step 1: 编写多周期模型测试**

创建 `tests/test_multi_horizon.py`：

```python
import pytest
import pandas as pd
import numpy as np
from ml_services.fx_trading_model import FXTradingModel


def test_model_initialization_with_horizon():
    """测试模型初始化支持不同周期"""
    model_1d = FXTradingModel(horizon=1)
    assert model_1d.horizon == 1
    
    model_5d = FXTradingModel(horizon=5)
    assert model_5d.horizon == 5
    
    model_20d = FXTradingModel(horizon=20)
    assert model_20d.horizon == 20


def test_train_multi_horizon_models():
    """测试训练多周期模型"""
    # 创建测试数据
    prices = [1.0 + i * 0.01 for i in range(200)]
    data = pd.DataFrame({
        'Close': prices,
        'High': [p + 0.01 for p in prices],
        'Low': [p - 0.01 for p in prices]
    })
    
    # 训练不同周期的模型
    model_1d = FXTradingModel(horizon=1)
    model_5d = FXTradingModel(horizon=5)
    model_20d = FXTradingModel(horizon=20)
    
    metrics_1d = model_1d.train('EUR', data)
    metrics_5d = model_5d.train('EUR', data)
    metrics_20d = model_20d.train('EUR', data)
    
    assert 'accuracy' in metrics_1d
    assert 'accuracy' in metrics_5d
    assert 'accuracy' in metrics_20d
    assert model_1d.model is not None
    assert model_5d.model is not None
    assert model_20d.model is not None


def test_predict_multi_horizon():
    """测试多周期预测"""
    # 创建测试数据
    prices = [1.0 + i * 0.01 for i in range(200)]
    data = pd.DataFrame({
        'Close': prices,
        'High': [p + 0.01 for p in prices],
        'Low': [p - 0.01 for p in prices]
    })
    
    # 训练模型
    model = FXTradingModel(horizon=20)
    model.train('EUR', data)
    
    # 使用实例默认周期预测
    pred_20d = model.predict('EUR', data.iloc[-1:])
    assert pred_20d['target_date'] == pred_20d['data_date'].replace(day=pred_20d['data_date'].day + 20)
    
    # 覆盖周期预测
    pred_5d = model.predict('EUR', data.iloc[-1:], horizon=5)
    assert pred_5d['target_date'] == pred_5d['data_date'].replace(day=pred_5d['data_date'].day + 5)
    
    pred_1d = model.predict('EUR', data.iloc[-1:], horizon=1)
    assert pred_1d['target_date'] == pred_1d['data_date'].replace(day=pred_1d['data_date'].day + 1)


def test_model_file_naming():
    """测试模型文件命名规范"""
    model_1d = FXTradingModel(horizon=1)
    model_20d = FXTradingModel(horizon=20)
    
    # 获取模型文件名
    model_file_1d = model_1d.model_processor.model_dir / 'EUR_model_1d.pkl'
    model_file_20d = model_20d.model_processor.model_dir / 'EUR_model_20d.pkl'
    
    assert '1d' in str(model_file_1d)
    assert '20d' in str(model_file_20d)
```

- [ ] **Step 2: 运行测试确认失败**

运行：`pytest tests/test_multi_horizon.py -v`
预期：FAIL（模型尚未修改）

- [ ] **Step 3: 修改 FXTradingModel.__init__ 方法**

在 `ml_services/fx_trading_model.py` 中，修改 `__init__` 方法（约第 15 行）：

```python
def __init__(self, config: dict = None, horizon: int = 20):
    """
    初始化模型
    
    Args:
        config: 模型配置字典
        horizon: 预测周期（天），默认 20 天
    """
    from config import MODEL_CONFIG, INDICATOR_CONFIG, MULTI_HORIZON_CONFIG
    
    self.horizon = horizon
    self.config = config or MODEL_CONFIG
    self.config['horizon'] = horizon
    
    # 根据周期调整模型参数
    if horizon in MULTI_HORIZON_CONFIG['model_params']:
        self.config['catboost_params'].update(
            MULTI_HORIZON_CONFIG['model_params'][horizon]
        )
    
    self.indicator_config = INDICATOR_CONFIG
    
    self.model = None
    self.feature_engineer = FeatureEngineer()
    self.technical_analyzer = TechnicalAnalyzer()
    self.model_processor = BaseModelProcessor()
    
    self.logger = logger
```

- [ ] **Step 4: 修改 train 方法支持 horizon 参数**

在 `ml_services/fx_trading_model.py` 中，修改 `train` 方法（约第 60 行）：

```python
def train(self, pair: str, data: pd.DataFrame, horizon: int = None) -> dict:
    """
    训练模型
    
    Args:
        pair: 货币对代码
        data: 训练数据（必须包含 Close, High, Low 列）
        horizon: 预测周期（天），可选，默认使用实例的 horizon
    
    Returns:
        训练指标字典
    """
    # 使用参数或实例的 horizon
    train_horizon = horizon if horizon is not None else self.horizon
    self.logger.info(f"开始训练 {pair} 模型（{train_horizon}天周期）...")
    
    # 1. 计算技术指标
    data = self.technical_analyzer.compute_all_indicators(data)
    
    # 2. 创建特征
    features = self.feature_engineer.create_features(data)
    
    # 3. 创建目标变量（使用指定的周期）
    target = self.feature_engineer.create_target(data, horizon=train_horizon)
    
    # 4. 准备训练数据
    # 删除包含 NaN 的行
    valid_indices = ~(target.isna())
    features_valid = features[valid_indices]
    target_valid = target[valid_indices]
    
    # 获取特征列（排除非特征列）
    exclude_cols = ['Close', 'High', 'Low', 'Open', 'Volume', 'Date']
    feature_cols = [col for col in features_valid.columns if col not in exclude_cols]
    
    X = features_valid[feature_cols]
    y = target_valid
    
    # 5. 分割训练集和验证集
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )
    
    # 6. 训练 CatBoost 模型
    self.model = CatBoostClassifier(**self.config['catboost_params'])
    
    self.model.fit(
        X_train, y_train,
        eval_set=(X_val, y_val),
        early_stopping_rounds=50,
        verbose=False
    )
    
    # 7. 评估模型
    y_pred = self.model.predict(X_val)
    accuracy = accuracy_score(y_val, y_pred)
    
    # 8. 保存模型（包含周期信息）
    model_name = f'{pair}_model_{train_horizon}d'
    self.model_processor.save_model(self.model, pair, model_name)
    
    metrics = {
        'accuracy': accuracy,
        'feature_count': len(feature_cols),
        'train_samples': len(X_train),
        'val_samples': len(X_val),
        'horizon': train_horizon
    }
    
    self.logger.info(f"训练完成（{train_horizon}天），准确率: {accuracy:.2%}")
    return metrics
```

- [ ] **Step 5: 修改 predict 方法支持 horizon 参数**

在 `ml_services/fx_trading_model.py` 中，修改 `predict` 方法（约第 120 行）：

```python
def predict(self, pair: str, data: pd.DataFrame, horizon: int = None) -> dict:
    """
    预测
    
    Args:
        pair: 货币对代码
        data: 预测数据（必须包含 Close, High, Low 列）
        horizon: 预测周期（天），可选，默认使用实例的 horizon
    
    Returns:
        预测结果字典
    """
    # 使用参数或实例的 horizon
    predict_horizon = horizon if horizon is not None else self.horizon
    model_name = f'{pair}_model_{predict_horizon}d'
    
    # 加载模型
    if self.model is None:
        try:
            self.model = self.model_processor.load_model(pair, model_name)
        except FileNotFoundError:
            self.logger.warning(f"模型不存在: {model_name}，使用默认预测")
            return self._get_default_prediction(pair, data, predict_horizon)
    
    # 计算技术指标
    data = self.technical_analyzer.compute_all_indicators(data)
    
    # 创建特征
    features = self.feature_engineer.create_features(data)
    
    # 获取特征列
    exclude_cols = ['Close', 'High', 'Low', 'Open', 'Volume', 'Date']
    feature_cols = [col for col in features.columns if col not in exclude_cols]
    
    # 使用最后一行进行预测
    latest_data = features[feature_cols].iloc[-1:].copy()
    
    # 处理缺失值
    latest_data = latest_data.fillna(0)
    
    # 预测
    prediction = self.model.predict(latest_data)[0]
    probability = self.model.predict_proba(latest_data)[0][1]  # 正类概率
    
    # 计算置信度
    confidence = self._get_confidence(probability)
    
    # 获取当前价格和目标日期
    current_price = data['Close'].iloc[-1]
    data_date = data.index[-1] if hasattr(data.index, 'to_pydatetime') else datetime.now()
    
    # 计算目标日期
    if isinstance(data_date, str):
        data_date = datetime.strptime(data_date, '%Y-%m-%d')
    target_date = data_date + timedelta(days=predict_horizon)
    
    result = {
        'pair': pair,
        'current_price': float(current_price),
        'prediction': int(prediction),
        'probability': float(probability),
        'confidence': confidence,
        'horizon': predict_horizon,
        'data_date': data_date.strftime('%Y-%m-%d'),
        'target_date': target_date.strftime('%Y-%m-%d')
    }
    
    self.logger.info(f"预测完成（{predict_horizon}天）: {pair} - {prediction} ({probability:.2%})")
    return result


def _get_default_prediction(self, pair: str, data: pd.DataFrame, horizon: int = 20) -> dict:
    """
    获取默认预测（当模型不可用时）
    
    Args:
        pair: 货币对代码
        data: 数据
        horizon: 预测周期（天）
    
    Returns:
        默认预测结果
    """
    current_price = data['Close'].iloc[-1]
    data_date = datetime.now()
    target_date = data_date + timedelta(days=horizon)
    
    return {
        'pair': pair,
        'current_price': float(current_price),
        'prediction': 0,
        'probability': 0.5,
        'confidence': 'low',
        'horizon': horizon,
        'data_date': data_date.strftime('%Y-%m-%d'),
        'target_date': target_date.strftime('%Y-%m-%d')
    }
```

- [ ] **Step 6: 运行测试验证通过**

运行：`pytest tests/test_multi_horizon.py -v`
预期：PASS

- [ ] **Step 7: 提交**

```bash
git add ml_services/fx_trading_model.py tests/test_multi_horizon.py
git commit -m "feat: 扩展 FXTradingModel 支持多周期训练和预测"
```

---

## Task 4: 创建一体化脚本框架

**Files:**
- Create: `run_pipeline.py`
- Test: `tests/test_run_pipeline.py`

- [ ] **Step 1: 编写脚本测试**

创建 `tests/test_run_pipeline.py`：

```python
import pytest
import os
import pandas as pd
from run_pipeline import Pipeline


def test_pipeline_initialization():
    """测试 Pipeline 初始化"""
    pipeline = Pipeline(data_file='FXRate_20260320.xlsx')
    assert pipeline is not None
    assert pipeline.pairs is not None
    assert pipeline.horizons == [1, 5, 20]


def test_pipeline_load_data():
    """测试 Pipeline 加载数据"""
    pipeline = Pipeline(data_file='FXRate_20260320.xlsx')
    data = pipeline.load_data()
    assert data is not None
    assert isinstance(data, dict)
    assert len(data) > 0


def test_pipeline_train_models():
    """测试 Pipeline 训练模型"""
    pipeline = Pipeline(
        data_file='FXRate_20260320.xlsx',
        pairs=['EUR'],
        horizons=[20]
    )
    
    # 加载数据
    data = pipeline.load_data()
    
    # 训练模型
    results = pipeline.train_models(data)
    
    assert 'EUR' in results
    assert 20 in results['EUR']
    assert 'accuracy' in results['EUR'][20]


def test_pipeline_generate_report():
    """测试 Pipeline 生成报告"""
    pipeline = Pipeline(
        data_file='FXRate_20260320.xlsx',
        pairs=['EUR'],
        horizons=[20]
    )
    
    # 模拟预测结果
    predictions = {
        'EUR': {
            20: {
                'pair': 'EUR',
                'prediction': 1,
                'probability': 0.65,
                'confidence': 'high',
                'recommendation': 'buy',
                'entry_price': 1.0850,
                'stop_loss': 1.0750,
                'take_profit': 1.0950,
                'data_date': '2026-03-25',
                'target_date': '2026-04-14'
            }
        }
    }
    
    # 生成报告
    report_path = pipeline.generate_markdown_report(predictions)
    
    assert os.path.exists(report_path)
    assert report_path.endswith('.md')
```

- [ ] **Step 2: 运行测试确认失败**

运行：`pytest tests/test_run_pipeline.py -v`
预期：FAIL（脚本尚未创建）

- [ ] **Step 3: 创建一体化脚本框架**

创建 `run_pipeline.py`：

```python
#!/usr/bin/env python3
"""
FX Predict 一体化脚本

一次性完成多周期模型训练、预测和报告生成
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_services.excel_loader import FXDataLoader
from data_services.technical_analysis import TechnicalAnalyzer
from ml_services.fx_trading_model import FXTradingModel
from comprehensive_analysis import ComprehensiveAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Pipeline:
    """一体化预测管道"""
    
    def __init__(self, data_file: str = None,
                 pairs: List[str] = None,
                 horizons: List[int] = None,
                 output_dir: str = 'data/predictions',
                 use_llm: bool = True,
                 skip_training: bool = False,
                 predict_only: bool = False):
        """
        初始化管道
        
        Args:
            data_file: Excel 数据文件路径
            pairs: 货币对列表
            horizons: 预测周期列表
            output_dir: 输出目录
            use_llm: 是否使用 LLM 生成分析
            skip_training: 跳过模型训练
            predict_only: 仅预测，不训练
        """
        from config import DATA_CONFIG, MULTI_HORIZON_CONFIG, REPORT_CONFIG
        
        self.data_file = data_file or self._find_data_file()
        self.pairs = pairs or list(DATA_CONFIG['supported_pairs'])
        self.horizons = horizons or MULTI_HORIZON_CONFIG['horizons']
        self.output_dir = output_dir
        self.use_llm = use_llm
        self.skip_training = skip_training
        self.predict_only = predict_only
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.loader = FXDataLoader()
        self.technical_analyzer = TechnicalAnalyzer()
        self.comprehensive_analyzer = ComprehensiveAnalyzer()
        
        self.models = {}
        self.predictions = {}
        
        logger.info(f"Pipeline 初始化完成: {len(self.pairs)} 个货币对, {len(self.horizons)} 个周期")
    
    def _find_data_file(self) -> str:
        """查找数据文件"""
        # 搜索常见的数据文件名
        possible_names = [
            'FXRate_20260320.xlsx',
            'FXRate_*.xlsx',
            'FXRate.xlsx'
        ]
        
        import glob
        for pattern in possible_names:
            matches = glob.glob(pattern)
            if matches:
                logger.info(f"找到数据文件: {matches[0]}")
                return matches[0]
        
        raise FileNotFoundError("未找到数据文件")
    
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """
        加载数据
        
        Returns:
            货币对数据字典
        """
        logger.info(f"正在加载数据: {self.data_file}")
        
        try:
            all_data = self.loader.load_all_pairs(self.data_file)
            logger.info(f"成功加载 {len(all_data)} 个货币对")
            return all_data
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            raise
    
    def train_models(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Dict[int, dict]]:
        """
        训练多周期模型
        
        Args:
            data: 货币对数据字典
        
        Returns:
            训练指标字典 {pair: {horizon: metrics}}
        """
        training_results = {}
        
        for pair in self.pairs:
            if pair not in data:
                logger.warning(f"跳过不存在的货币对: {pair}")
                continue
            
            training_results[pair] = {}
            
            for horizon in self.horizons:
                try:
                    logger.info(f"训练 {pair} {horizon}天模型...")
                    
                    model = FXTradingModel(horizon=horizon)
                    metrics = model.train(pair, data[pair])
                    
                    training_results[pair][horizon] = metrics
                    
                    # 保存模型引用
                    self.models[f"{pair}_{horizon}d"] = model
                    
                    logger.info(f"{pair} {horizon}天模型训练完成: 准确率 {metrics['accuracy']:.2%}")
                    
                except Exception as e:
                    logger.error(f"训练 {pair} {horizon}天模型失败: {e}")
                    continue
        
        return training_results
    
    def predict(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Dict[int, dict]]:
        """
        预测
        
        Args:
            data: 货币对数据字典
        
        Returns:
            预测结果字典 {pair: {horizon: prediction}}
        """
        predictions = {}
        
        for pair in self.pairs:
            if pair not in data:
                continue
            
            predictions[pair] = {}
            
            for horizon in self.horizons:
                try:
                    logger.info(f"预测 {pair} {horizon}天...")
                    
                    model = FXTradingModel(horizon=horizon)
                    prediction = model.predict(pair, data[pair])
                    
                    predictions[pair][horizon] = prediction
                    
                    logger.info(f"{pair} {horizon}天预测: {prediction['recommendation']} (置信度: {prediction['confidence']})")
                    
                except Exception as e:
                    logger.error(f"预测 {pair} {horizon}天失败: {e}")
                    continue
        
        return predictions
    
    def generate_markdown_report(self, predictions: Dict[str, Dict[int, dict]]) -> str:
        """
        生成 Markdown 报告
        
        Args:
            predictions: 预测结果字典
        
        Returns:
            报告文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d')
        report_path = os.path.join(self.output_dir, f'report_{timestamp}.md')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            # 写入报告头部
            f.write(f"# FX Predict 分析报告\n\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"报告类型：完整报告（多周期预测 + 技术分析")
            f.write(f"{' + LLM 解释' if self.use_llm else ''}）\n\n")
            f.write("---\n\n")
            
            # 写入每个货币对的分析
            for pair in self.pairs:
                if pair not in predictions:
                    continue
                
                f.write(f"## {pair}/USD 分析\n\n")
                
                # 多周期预测表格
                f.write("### 多周期预测\n\n")
                f.write("| 周期 | 预测 | 概率 | 置信度 | 建议 |\n")
                f.write("|------|------|------|--------|------|\n")
                
                for horizon in sorted(predictions[pair].keys()):
                    pred = predictions[pair][horizon]
                    f.write(f"| {horizon}天 | {self._format_prediction(pred['prediction'])} | "
                           f"{pred['probability']:.2f} | {pred['confidence']} | "
                           f"{pred['recommendation']} |\n")
                
                f.write("\n")
            
            # 免责声明
            f.write("---\n\n")
            f.write("## 免责声明\n\n")
            f.write("本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。\n")
        
        logger.info(f"Markdown 报告已生成: {report_path}")
        return report_path
    
    def generate_csv_report(self, predictions: Dict[str, Dict[int, dict]]) -> str:
        """
        生成 CSV 报告
        
        Args:
            predictions: 预测结果字典
        
        Returns:
            报告文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d')
        csv_path = os.path.join(self.output_dir, f'predictions_{timestamp}.csv')
        
        # 准备 CSV 数据
        csv_data = []
        for pair in self.pairs:
            if pair not in predictions:
                continue
            
            for horizon in sorted(predictions[pair].keys()):
                pred = predictions[pair][horizon]
                csv_data.append({
                    'pair': pair,
                    'horizon': horizon,
                    'prediction': pred['prediction'],
                    'probability': pred['probability'],
                    'confidence': pred['confidence'],
                    'recommendation': pred['recommendation'],
                    'entry_price': pred.get('current_price', ''),
                    'stop_loss': pred.get('stop_loss', ''),
                    'take_profit': pred.get('take_profit', ''),
                    'analysis_date': pred['data_date'],
                    'target_date': pred['target_date']
                })
        
        # 写入 CSV
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        logger.info(f"CSV 报告已生成: {csv_path}")
        return csv_path
    
    def _format_prediction(self, prediction: int) -> str:
        """格式化预测结果"""
        return '上涨' if prediction == 1 else '下跌'
    
    def run(self) -> Dict[str, Dict[int, dict]]:
        """
        运行完整流程
        
        Returns:
            预测结果字典
        """
        logger.info("=" * 60)
        logger.info("开始运行 FX Predict 流程")
        logger.info("=" * 60)
        
        # 1. 加载数据
        data = self.load_data()
        
        # 2. 训练模型（如果需要）
        if not self.skip_training and not self.predict_only:
            training_results = self.train_models(data)
        
        # 3. 预测
        predictions = self.predict(data)
        
        # 4. 生成报告
        md_report_path = self.generate_markdown_report(predictions)
        csv_report_path = self.generate_csv_report(predictions)
        
        logger.info("=" * 60)
        logger.info("流程完成")
        logger.info(f"Markdown 报告: {md_report_path}")
        logger.info(f"CSV 报告: {csv_report_path}")
        logger.info("=" * 60)
        
        return predictions


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='FX Predict 一体化预测脚本')
    
    parser.add_argument('--data', type=str, default=None,
                       help='Excel 数据文件路径')
    parser.add_argument('--pairs', type=str, default=None,
                       help='货币对列表（逗号分隔）')
    parser.add_argument('--horizons', type=int, nargs='+', default=[1, 5, 20],
                       help='预测周期列表（天）')
    parser.add_argument('--output', type=str, default='data/predictions',
                       help='输出目录')
    parser.add_argument('--no-llm', action='store_true',
                       help='禁用 LLM 调用')
    parser.add_argument('--skip-training', action='store_true',
                       help='跳过模型训练')
    parser.add_argument('--predict-only', action='store_true',
                       help='仅预测，不训练')
    parser.add_argument('--verbose', action='store_true',
                       help='详细模式')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 解析货币对
    pairs = None
    if args.pairs:
        pairs = [p.strip() for p in args.pairs.split(',')]
    
    # 创建管道
    pipeline = Pipeline(
        data_file=args.data,
        pairs=pairs,
        horizons=args.horizons,
        output_dir=args.output,
        use_llm=not args.no_llm,
        skip_training=args.skip_training,
        predict_only=args.predict_only
    )
    
    # 运行流程
    try:
        predictions = pipeline.run()
        return 0
    except Exception as e:
        logger.error(f"流程执行失败: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 4: 运行测试验证通过**

运行：`pytest tests/test_run_pipeline.py -v`
预期：PASS

- [ ] **Step 5: 设置脚本可执行权限**

运行：`chmod +x run_pipeline.py`

- [ ] **Step 6: 提交**

```bash
git add run_pipeline.py tests/test_run_pipeline.py
git commit -m "feat: 创建一体化脚本框架"
```

---

## Task 5: 集成测试和验证

**Files:**
- Test: `tests/test_run_pipeline.py`

- [ ] **Step 1: 添加端到端集成测试**

在 `tests/test_run_pipeline.py` 中添加：

```python
import pytest
import os
from run_pipeline import Pipeline


def test_end_to_end_pipeline():
    """测试完整的端到端流程"""
    # 创建管道
    pipeline = Pipeline(
        data_file='FXRate_20260320.xlsx',
        pairs=['EUR'],
        horizons=[20],
        output_dir='data/test_predictions',
        use_llm=False  # 测试时不使用 LLM
    )
    
    # 运行完整流程
    predictions = pipeline.run()
    
    # 验证预测结果
    assert 'EUR' in predictions
    assert 20 in predictions['EUR']
    assert 'prediction' in predictions['EUR'][20]
    assert 'probability' in predictions['EUR'][20]
    assert 'confidence' in predictions['EUR'][20]
    
    # 验证报告文件已生成
    assert os.path.exists('data/test_predictions')
    
    # 清理
    import shutil
    shutil.rmtree('data/test_predictions', ignore_errors=True)


def test_pipeline_multi_horizon():
    """测试多周期预测流程"""
    pipeline = Pipeline(
        data_file='FXRate_20260320.xlsx',
        pairs=['EUR'],
        horizons=[1, 5, 20],
        output_dir='data/test_predictions',
        use_llm=False,
        predict_only=True  # 仅预测，不训练
    )
    
    predictions = pipeline.run()
    
    # 验证所有周期的预测都已生成
    assert 'EUR' in predictions
    assert 1 in predictions['EUR']
    assert 5 in predictions['EUR']
    assert 20 in predictions['EUR']
    
    # 清理
    import shutil
    shutil.rmtree('data/test_predictions', ignore_errors=True)


def test_pipeline_skip_training():
    """测试跳过训练模式"""
    pipeline = Pipeline(
        data_file='FXRate_20260320.xlsx',
        pairs=['EUR'],
        horizons=[20],
        output_dir='data/test_predictions',
        skip_training=True  # 跳过训练
    )
    
    # 应该只进行预测，不训练
    predictions = pipeline.run()
    
    assert 'EUR' in predictions
    
    # 清理
    import shutil
    shutil.rmtree('data/test_predictions', ignore_errors=True)
```

- [ ] **Step 2: 运行集成测试**

运行：`pytest tests/test_run_pipeline.py::test_end_to_end_pipeline tests/test_run_pipeline.py::test_pipeline_multi_horizon tests/test_run_pipeline.py::test_pipeline_skip_training -v`
预期：PASS

- [ ] **Step 3: 手动验证脚本**

运行：`python3 run_pipeline.py --pairs EUR --horizons 20 --no-llm --verbose`
预期：成功执行并生成报告

- [ ] **Step 4: 提交**

```bash
git add tests/test_run_pipeline.py
git commit -m "test: 添加一体化脚本集成测试"
```

---

## Task 6: 文档更新

**Files:**
- Modify: `AGENTS.md`
- Modify: `progress.txt`
- Modify: `lessons.md`

- [ ] **Step 1: 更新 AGENTS.md**

在 `AGENTS.md` 的"快速开始"部分添加：

```markdown
### 一体化脚本（推荐）

```bash
# 运行完整流程（所有货币对，所有周期）
python3 run_pipeline.py

# 运行指定货币对和周期
python3 run_pipeline.py --pairs EUR,JPY,AUD --horizons 1 5 20

# 跳过训练（仅使用已有模型）
python3 run_pipeline.py --skip-training

# 禁用 LLM（快速生成）
python3 run_pipeline.py --no-llm

# 查看帮助
python3 run_pipeline.py --help
```

输出：
- Markdown 报告：`data/predictions/report_YYYYMMDD.md`
- CSV 报告：`data/predictions/predictions_YYYYMMDD.csv`
```

- [ ] **Step 2: 更新 progress.txt**

在 `progress.txt` 中添加阶段 2 进度：

```markdown
## 阶段 2 进度

### 已完成任务（阶段 2.1）

- [x] Task 1: 更新配置文件（多周期配置）
- [x] Task 2: 扩展特征工程支持多周期
- [x] Task 3: 扩展 FXTradingModel 支持多周期
- [x] Task 4: 创建一体化脚本框架
- [x] Task 5: 集成测试和验证
- [x] Task 6: 文档更新

### 待完成任务（阶段 2.2）

- [ ] Task 7: 实现 WalkForwardValidator
- [ ] Task 8: 实现回测系统
- [ ] Task 9: 实现性能监控
```

- [ ] **Step 3: 更新 lessons.md**

在 `lessons.md` 中添加经验教训：

```markdown
## 阶段 2 经验教训

### 多周期模型

1. **命名规范**：模型文件名应包含周期信息（如 `EUR_model_1d.pkl`）
2. **参数调整**：不同周期需要不同的模型参数（短周期用更简单的模型）
3. **向后兼容**：保持现有接口不变，新功能作为可选参数

### 一体化脚本

1. **错误容忍**：单个模型失败不应影响其他模型
2. **进度显示**：使用 tqdm 显示进度，提升用户体验
3. **报告生成**：同时生成 Markdown（可读）和 CSV（机器可读）报告
```

- [ ] **Step 4: 提交**

```bash
git add AGENTS.md progress.txt lessons.md
git commit -m "docs: 更新阶段 2 文档（一体化脚本和多周期模型）"
```

---

## Task 7: 最终验证

- [ ] **Step 1: 运行所有测试**

运行：`pytest tests/ -v --cov=. --cov-report=term`

预期：
- 所有测试通过
- 核心模块覆盖率 ≥ 75%

- [ ] **Step 2: 验证脚本功能**

运行：`python3 run_pipeline.py --pairs EUR --horizons 1 5 20 --no-llm`

验证：
- Markdown 报告生成
- CSV 报告生成
- 多周期预测正确

- [ ] **Step 3: 提交最终版本**

```bash
git add .
git commit -m "feat: 完成一体化脚本和多周期模型实现"
```

---

## 成功标准

| 指标 | 目标 | 验证方法 |
|------|------|---------|
| 多周期模型 | 1天/5天/20天模型全部可训练 | 单元测试 |
| 一体化脚本 | 一次性完成训练、预测、报告 | 集成测试 |
| 报告生成 | Markdown 和 CSV 报告都生成 | 手动验证 |
| 测试覆盖率 | ≥ 75% | pytest-cov |
| 向后兼容 | 现有功能不受影响 | 回归测试 |

---

EOF
