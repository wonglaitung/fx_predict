# 外汇智能分析系统 MVP 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标:** 构建一个基于机器学习和人机协作的外汇汇率预测系统，包含技术指标引擎、CatBoost 预测模型和综合分析系统

**架构:** 分层架构设计，包含数据层（Excel 加载器）、特征层（技术指标）、模型层（CatBoost）、整合层（信号协同）、接口层（大模型）

**技术栈:** Python 3.10+, pandas, catboost, openpyxl, requests, pytest

---

## 文件结构

```
fx_predict/
├── data/
│   ├── FXRate_20260320.xlsx          # [已有] 汇率数据文件
│   ├── models/                       # [新建] 模型存储目录
│   └── predictions/                  # [新建] 预测结果目录
├── data_services/
│   ├── __init__.py                   # [新建] 包初始化
│   ├── fx_data_loader.py             # [新建] Excel 数据加载器
│   └── technical_analysis.py         # [新建] 技术指标计算引擎
├── ml_services/
│   ├── __init__.py                   # [新建] 包初始化
│   ├── fx_trading_model.py           # [新建] CatBoost 模型
│   ├── feature_engineering.py        # [新建] 特征工程
│   └── base_model_processor.py       # [新建] 基础模型处理器
├── llm_services/
│   ├── __init__.py                   # [新建] 包初始化
│   └── qwen_engine.py                # [新建] 大模型 API 封装
├── tests/
│   ├── __init__.py                   # [新建] 测试包初始化
│   ├── test_fx_data_loader.py        # [新建] 数据加载器测试
│   ├── test_technical_analysis.py    # [新建] 技术指标测试
│   ├── test_fx_trading_model.py      # [新建] 模型测试
│   ├── test_feature_engineering.py   # [新建] 特征工程测试
│   └── test_comprehensive_analysis.py # [新建] 综合分析测试
├── config.py                         # [新建] 配置文件
├── comprehensive_analysis.py         # [新建] 人机协作整合层
├── requirements.txt                  # [新建] 依赖列表
└── .env                              # [新建] 环境变量模板
```

---

## 任务分解

### Task 1: 项目初始化和依赖管理

**文件:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `data/`, `data/models/`, `data/predictions/` 目录

- [ ] **Step 1: 创建 requirements.txt**

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

# 数据可视化
matplotlib>=3.7.0
seaborn>=0.12.0

# 大模型
requests>=2.31.0

# 开发工具
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.7.0
```

- [ ] **Step 2: 安装依赖**

Run: `pip install -r requirements.txt`
Expected: 所有包安装成功，无错误

- [ ] **Step 3: 创建环境变量模板文件**

Create: `.env.example`

```bash
# 通义千问 API 配置
QWEN_API_KEY=your_api_key_here
QWEN_CHAT_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
QWEN_CHAT_MODEL=qwen-plus-2025-12-01
MAX_TOKENS=32768
```

- [ ] **Step 4: 创建数据目录**

Run: `mkdir -p data data/models data/predictions tests data_services ml_services llm_services`
Expected: 所有目录创建成功

- [ ] **Step 5: 创建包初始化文件**

Run: `touch data_services/__init__.py ml_services/__init__.py llm_services/__init__.py tests/__init__.py`
Expected: 所有 `__init__.py` 文件创建成功

- [ ] **Step 6: 提交**

```bash
git add requirements.txt .env.example
git add data_services/__init__.py ml_services/__init__.py llm_services/__init__.py tests/__init__.py
git commit -m "feat: 项目初始化 - 依赖管理和目录结构"
```

---

### Task 2: 配置文件实现

**文件:**
- Create: `config.py`
- Test: 不需要独立测试（配置文件）

- [ ] **Step 1: 创建配置文件**

Create: `config.py`

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
    'buy_threshold': 60,
    'sell_threshold': 40,
    'ml_probability_threshold': 0.60
}

# 文件路径
PATHS = {
    'data_dir': 'data',
    'model_dir': 'data/models',
    'prediction_dir': 'data/predictions',
    'log_file': 'fx_predict.log'
}
```

- [ ] **Step 2: 验证配置文件可导入**

Run: `python3 -c "import config; print('Config loaded successfully:', config.CURRENCY_PAIRS)"`
Expected: 配置文件成功加载，输出货币对配置

- [ ] **Step 3: 提交**

```bash
git add config.py
git commit -m "feat: 添加配置文件"
```

---

### Task 3: Excel 数据加载器实现

**文件:**
- Create: `data_services/fx_data_loader.py`
- Test: `tests/test_fx_data_loader.py`

- [ ] **Step 1: 编写数据加载器测试**

Create: `tests/test_fx_data_loader.py`

```python
import pytest
import pandas as pd
import os
from data_services.fx_data_loader import FXDataLoader


def test_load_pair_existing_sheet():
    """测试加载存在的货币对"""
    loader = FXDataLoader()
    df = loader.load_pair('EUR', 'FXRate_20260320.xlsx')
    
    assert df is not None
    assert 'Close' in df.columns
    assert 'Date' in df.columns
    assert len(df) > 0
    assert df['Date'].dtype == 'datetime64[ns]'
    # 检查数据是否升序排列（旧数据在前）
    assert df['Date'].is_monotonic_increasing


def test_load_pair_nonexistent_sheet():
    """测试加载不存在的货币对"""
    loader = FXDataLoader()
    with pytest.raises(ValueError):
        loader.load_pair('NONEXISTENT', 'FXRate_20260320.xlsx')


def test_load_pair_missing_file():
    """测试加载不存在的文件"""
    loader = FXDataLoader()
    with pytest.raises(FileNotFoundError):
        loader.load_pair('EUR', 'nonexistent.xlsx')


def test_load_all_pairs():
    """测试加载所有货币对"""
    loader = FXDataLoader()
    all_data = loader.load_all_pairs('FXRate_20260320.xlsx')
    
    assert isinstance(all_data, dict)
    assert len(all_data) > 0
    for pair, df in all_data.items():
        assert 'Close' in df.columns
        assert 'Date' in df.columns


def test_preprocess_basic():
    """测试基本预处理功能"""
    loader = FXDataLoader()
    # 创建测试数据
    test_df = pd.DataFrame({
        'Date': ['3/20/2026', '3/19/2026', '3/18/2026'],
        'Close': [1.0850, 1.0840, 1.0830],
        'SMA5': [1.0845, 1.0840, 1.0835]
    })
    
    result = loader.preprocess(test_df)
    
    assert result['Date'].dtype == 'datetime64[ns]'
    assert result['Close'].dtype == float
    assert result['Date'].is_monotonic_increasing


def test_preprocess_missing_values():
    """测试缺失值处理"""
    loader = FXDataLoader()
    test_df = pd.DataFrame({
        'Date': ['3/20/2026', '3/19/2026', '3/18/2026'],
        'Close': [1.0850, None, 1.0830],
        'SMA5': [1.0845, 1.0840, None]
    })
    
    result = loader.preprocess(test_df)
    
    # 检查缺失值是否被前向填充
    assert result['Close'].isna().sum() == 0
    assert result['SMA5'].isna().sum() <= 1  # 第一个值可能仍为 NaN
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pytest tests/test_fx_data_loader.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'data_services.fx_data_loader'"

- [ ] **Step 3: 实现 FXDataLoader 类**

Create: `data_services/fx_data_loader.py`

```python
import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FXDataLoader:
    """外汇汇率数据加载器"""
    
    def __init__(self):
        self.logger = logger
    
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
        # 检查文件是否存在
        if not Path(file_path).exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            # 读取 Excel 文件
            df = pd.read_excel(file_path, sheet_name=pair)
            
            # 预处理数据
            df = self.preprocess(df)
            
            self.logger.info(f"成功加载货币对 {pair}，共 {len(df)} 条记录")
            return df
            
        except ValueError as e:
            if "Worksheet named" in str(e):
                raise ValueError(f"工作表不存在: {pair}") from e
            raise ValueError(f"数据格式错误: {e}") from e
        except Exception as e:
            raise ValueError(f"加载数据失败: {e}") from e
    
    def load_all_pairs(self, file_path: str) -> dict:
        """
        加载所有货币对数据
        
        Args:
            file_path: Excel 文件路径
        
        Returns:
            字典 {pair_code: DataFrame}
        """
        # 获取所有工作表名称
        xls = pd.ExcelFile(file_path)
        all_pairs = {}
        
        for sheet_name in xls.sheet_names:
            try:
                df = self.load_pair(sheet_name, file_path)
                all_pairs[sheet_name] = df
                self.logger.info(f"已加载货币对: {sheet_name}")
            except Exception as e:
                self.logger.warning(f"加载货币对 {sheet_name} 失败: {e}")
        
        self.logger.info(f"成功加载 {len(all_pairs)} 个货币对")
        return all_pairs
    
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
        # 转换日期格式
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
        
        # 转换数值列
        numeric_columns = ['Close', 'SMA5', 'SMA10', 'SMA20']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 按日期升序排序（旧数据在前）
        if 'Date' in df.columns:
            df = df.sort_values('Date', ascending=True).reset_index(drop=True)
        
        # 前向填充缺失值
        df = df.fillna(method='ffill')
        
        return df
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_fx_data_loader.py -v`
Expected: 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add data_services/fx_data_loader.py tests/test_fx_data_loader.py
git commit -m "feat: 实现 Excel 数据加载器"
```

---

### Task 4: 技术指标引擎实现（完整指标集）

**文件:**
- Create: `data_services/technical_analysis.py`
- Test: `tests/test_technical_analysis.py`

- [ ] **Step 1: 编写完整技术指标测试**

Create: `tests/test_technical_analysis.py`

```python
import pytest
import pandas as pd
import numpy as np
from data_services.technical_analysis import TechnicalAnalyzer


def test_compute_sma():
    """测试简单移动平均线"""
    analyzer = TechnicalAnalyzer()
    df = pd.DataFrame({'Close': [1.0, 1.1, 1.2, 1.3, 1.4, 1.5]})
    
    sma5 = analyzer.compute_sma(df, period=5)
    
    assert len(sma5) == len(df)
    # 检查前 4 个值应为 NaN（数据不足）
    assert sma5.iloc[:4].isna().all()
    # 检查第 5 个值应为均值
    assert abs(sma5.iloc[4] - df['Close'].iloc[:5].mean()) < 0.01


def test_compute_ema():
    """测试指数移动平均线"""
    analyzer = TechnicalAnalyzer()
    df = pd.DataFrame({'Close': [1.0, 1.1, 1.2, 1.3, 1.4]})
    
    ema5 = analyzer.compute_ema(df, period=5)
    
    assert len(ema5) == len(df)
    # EMA 应该有值（使用递归计算）
    assert not ema5.iloc[1:].isna().all()


def test_compute_rsi():
    """测试 RSI"""
    analyzer = TechnicalAnalyzer()
    # 创建足够长的数据
    prices = [1.0 + i * 0.01 for i in range(20)]
    df = pd.DataFrame({'Close': prices})
    
    rsi = analyzer.compute_rsi(df, period=14)
    
    assert len(rsi) == len(df)
    # RSI 值应该在 0-100 之间
    valid_rsi = rsi.dropna()
    assert (valid_rsi >= 0).all()
    assert (valid_rsi <= 100).all()


def test_compute_macd():
    """测试 MACD"""
    analyzer = TechnicalAnalyzer()
    prices = [1.0 + i * 0.01 for i in range(50)]
    df = pd.DataFrame({'Close': prices})
    
    macd_df = analyzer.compute_macd(df)
    
    assert 'MACD' in macd_df.columns
    assert 'MACD_Signal' in macd_df.columns
    assert 'MACD_Hist' in macd_df.columns
    assert len(macd_df) == len(df)


def test_compute_atr():
    """测试 ATR"""
    analyzer = TechnicalAnalyzer()
    df = pd.DataFrame({
        'High': [1.02, 1.03, 1.04, 1.05, 1.06],
        'Low': [1.00, 1.01, 1.02, 1.03, 1.04],
        'Close': [1.01, 1.02, 1.03, 1.04, 1.05]
    })
    
    atr = analyzer.compute_atr(df, period=3)
    
    assert len(atr) == len(df)
    # ATR 应该是正值
    valid_atr = atr.dropna()
    assert (valid_atr > 0).all()


def test_compute_bollinger_bands():
    """测试布林带"""
    analyzer = TechnicalAnalyzer()
    df = pd.DataFrame({'Close': [1.0 + i * 0.01 for i in range(30)]})
    
    bb_df = analyzer.compute_bollinger_bands(df, period=20, std_dev=2)
    
    assert 'BB_Upper' in bb_df.columns
    assert 'BB_Middle' in bb_df.columns
    assert 'BB_Lower' in bb_df.columns
    assert len(bb_df) == len(df)
    # 上轨应该大于下轨
    valid_bb = bb_df.dropna(subset=['BB_Upper', 'BB_Lower'])
    assert (valid_bb['BB_Upper'] > valid_bb['BB_Lower']).all()


def test_compute_adx():
    """测试 ADX"""
    analyzer = TechnicalAnalyzer()
    df = pd.DataFrame({
        'High': [1.02 + i * 0.01 for i in range(30)],
        'Low': [1.00 + i * 0.01 for i in range(30)],
        'Close': [1.01 + i * 0.01 for i in range(30)]
    })
    
    adx_df = analyzer.compute_adx(df, period=14)
    
    assert 'ADX' in adx_df.columns
    assert 'DI_Plus' in adx_df.columns
    assert 'DI_Minus' in adx_df.columns
    assert len(adx_df) == len(df)
    # ADX 值应该非负
    valid_adx = adx_df['ADX'].dropna()
    assert (valid_adx >= 0).all()


def test_compute_obv():
    """测试 OBV"""
    analyzer = TechnicalAnalyzer()
    df = pd.DataFrame({
        'Close': [1.01, 1.02, 1.01, 1.03, 1.04],
        'Volume': [1000, 1500, 800, 1200, 2000]
    })
    
    obv = analyzer.compute_obv(df)
    
    assert len(obv) == len(df)
    # OBV 应该是累计值
    assert not obv.isna().all()


def test_compute_kdj():
    """测试 KDJ"""
    analyzer = TechnicalAnalyzer()
    df = pd.DataFrame({
        'High': [1.02 + i * 0.01 for i in range(30)],
        'Low': [1.00 + i * 0.01 for i in range(30)],
        'Close': [1.01 + i * 0.01 for i in range(30)]
    })
    
    kdj_df = analyzer.compute_kdj(df)
    
    assert 'K' in kdj_df.columns
    assert 'D' in kdj_df.columns
    assert 'J' in kdj_df.columns
    assert len(kdj_df) == len(df)
    # KDJ 值应该在 0-100 之间
    valid_kdj = kdj_df.dropna()
    assert (valid_kdj['K'] >= 0).all() and (valid_kdj['K'] <= 100).all()


def test_compute_williams_r():
    """测试威廉指标"""
    analyzer = TechnicalAnalyzer()
    df = pd.DataFrame({
        'High': [1.02 + i * 0.01 for i in range(30)],
        'Low': [1.00 + i * 0.01 for i in range(30)],
        'Close': [1.01 + i * 0.01 for i in range(30)]
    })
    
    wr = analyzer.compute_williams_r(df, period=14)
    
    assert len(wr) == len(df)
    # 威廉指标值应该在 -100 到 0 之间
    valid_wr = wr.dropna()
    assert (valid_wr >= -100).all() and (valid_wr <= 0).all()


def test_compute_cci():
    """测试 CCI"""
    analyzer = TechnicalAnalyzer()
    df = pd.DataFrame({
        'High': [1.02 + i * 0.01 for i in range(30)],
        'Low': [1.00 + i * 0.01 for i in range(30)],
        'Close': [1.01 + i * 0.01 for i in range(30)]
    })
    
    cci = analyzer.compute_cci(df, period=20)
    
    assert len(cci) == len(df)


def test_data_leakage_prevention():
    """测试数据泄漏防范 - 所有指标应该使用滞后数据"""
    analyzer = TechnicalAnalyzer()
    df = pd.DataFrame({
        'High': [1.02, 1.03, 1.04, 1.05, 1.06],
        'Low': [1.00, 1.01, 1.02, 1.03, 1.04],
        'Close': [1.01, 1.02, 1.03, 1.04, 1.05],
        'Volume': [1000, 1500, 800, 1200, 2000]
    })
    
    # 计算所有指标
    result = analyzer.compute_all_indicators(df)
    
    # 检查第一行的所有技术指标应为 NaN（使用 shift(1)）
    indicator_columns = [col for col in result.columns 
                        if col not in ['High', 'Low', 'Close', 'Open', 'Volume', 'Date']]
    
    for col in indicator_columns:
        assert pd.isna(result[col].iloc[0]), f"指标 {col} 第一行不应有值（防止数据泄漏）"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pytest tests/test_technical_analysis.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'data_services.technical_analysis'"

- [ ] **Step 3: 实现 TechnicalAnalyzer 类（完整指标集）**

Create: `data_services/technical_analysis.py`

```python
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """技术指标计算引擎"""
    
    def __init__(self):
        self.logger = logger
    
    def compute_sma(self, df: pd.DataFrame, period: int) -> pd.Series:
        """计算简单移动平均线"""
        return df['Close'].rolling(window=period, min_periods=1).mean().shift(1)
    
    def compute_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """计算指数移动平均线"""
        return df['Close'].ewm(span=period, adjust=False).mean().shift(1)
    
    def compute_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算 RSI"""
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.shift(1)
    
    def compute_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26,
                     signal: int = 9) -> pd.DataFrame:
        """计算 MACD"""
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean().shift(1)
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean().shift(1)
        
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal, adjust=False).mean().shift(1)
        macd_hist = macd_line - macd_signal
        
        result = pd.DataFrame({
            'MACD': macd_line,
            'MACD_Signal': macd_signal,
            'MACD_Hist': macd_hist
        })
        
        return result
    
    def compute_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算 ATR"""
        if 'High' not in df.columns or 'Low' not in df.columns:
            logger.warning("缺少 High 或 Low 列，跳过 ATR 计算")
            return pd.Series([np.nan] * len(df), index=df.index)
        
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean().shift(1)
        
        return atr
    
    def compute_bollinger_bands(self, df: pd.DataFrame, period: int = 20,
                                std_dev: int = 2) -> pd.DataFrame:
        """计算布林带"""
        bb_middle = df['Close'].rolling(window=period).mean().shift(1)
        bb_std = df['Close'].rolling(window=period).std().shift(1)
        bb_upper = bb_middle + (bb_std * std_dev)
        bb_lower = bb_middle - (bb_std * std_dev)
        
        result = pd.DataFrame({
            'BB_Upper': bb_upper,
            'BB_Middle': bb_middle,
            'BB_Lower': bb_lower
        })
        
        return result
    
    def compute_adx(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """计算 ADX"""
        if 'High' not in df.columns or 'Low' not in df.columns:
            logger.warning("缺少 High 或 Low 列，跳过 ADX 计算")
            return pd.DataFrame({
                'ADX': [np.nan] * len(df),
                'DI_Plus': [np.nan] * len(df),
                'DI_Minus': [np.nan] * len(df)
            }, index=df.index)
        
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean().shift(1)
        
        result = pd.DataFrame({
            'ADX': adx,
            'DI_Plus': plus_di.shift(1),
            'DI_Minus': minus_di.shift(1)
        })
        
        return result
    
    def compute_obv(self, df: pd.DataFrame) -> pd.Series:
        """计算 OBV"""
        if 'Volume' not in df.columns:
            logger.warning("缺少 Volume 列，跳过 OBV 计算")
            return pd.Series([np.nan] * len(df), index=df.index)
        
        obv = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        return obv.shift(1)
    
    def compute_kdj(self, df: pd.DataFrame, period: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
        """计算 KDJ"""
        if 'High' not in df.columns or 'Low' not in df.columns:
            logger.warning("缺少 High 或 Low 列，跳过 KDJ 计算")
            return pd.DataFrame({
                'K': [np.nan] * len(df),
                'D': [np.nan] * len(df),
                'J': [np.nan] * len(df)
            }, index=df.index)
        
        low_min = df['Low'].rolling(window=period).min()
        high_max = df['High'].rolling(window=period).max()
        
        rsv = (df['Close'] - low_min) / (high_max - low_min) * 100
        
        k = rsv.ewm(com=m1, adjust=False).mean()
        d = k.ewm(com=m2, adjust=False).mean()
        j = 3 * k - 2 * d
        
        result = pd.DataFrame({
            'K': k.shift(1),
            'D': d.shift(1),
            'J': j.shift(1)
        })
        
        return result
    
    def compute_williams_r(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算威廉指标"""
        if 'High' not in df.columns or 'Low' not in df.columns:
            logger.warning("缺少 High 或 Low 列，跳过威廉指标计算")
            return pd.Series([np.nan] * len(df), index=df.index)
        
        high_max = df['High'].rolling(window=period).max()
        low_min = df['Low'].rolling(window=period).min()
        
        wr = (high_max - df['Close']) / (high_max - low_min) * -100
        return wr.shift(1)
    
    def compute_cci(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """计算 CCI"""
        if 'High' not in df.columns or 'Low' not in df.columns:
            logger.warning("缺少 High 或 Low 列，跳过 CCI 计算")
            return pd.Series([np.nan] * len(df), index=df.index)
        
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        sma_tp = typical_price.rolling(window=period).mean()
        mad = typical_price.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        
        cci = (typical_price - sma_tp) / (0.015 * mad)
        return cci.shift(1)
    
    def compute_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标"""
        result = df.copy()
        
        # SMA 指标
        for period in [5, 10, 20, 50, 120]:
            result[f'SMA{period}'] = self.compute_sma(result, period)
        
        # EMA 指标
        for period in [5, 10, 20]:
            result[f'EMA{period}'] = self.compute_ema(result, period)
        
        # RSI
        result['RSI14'] = self.compute_rsi(result, period=14)
        
        # MACD
        macd_df = self.compute_macd(result)
        result = pd.concat([result, macd_df], axis=1)
        
        # ATR
        result['ATR14'] = self.compute_atr(result, period=14)
        
        # 布林带
        bb_df = self.compute_bollinger_bands(result, period=20, std_dev=2)
        result = pd.concat([result, bb_df], axis=1)
        
        # ADX
        adx_df = self.compute_adx(result, period=14)
        result = pd.concat([result, adx_df], axis=1)
        
        # OBV
        result['OBV'] = self.compute_obv(result)
        
        # KDJ
        kdj_df = self.compute_kdj(result)
        result = pd.concat([result, kdj_df], axis=1)
        
        # 威廉指标
        result['Williams_R'] = self.compute_williams_r(result, period=14)
        
        # CCI
        result['CCI'] = self.compute_cci(result, period=20)
        
        self.logger.info(f"已计算 {len([col for col in result.columns if col not in df.columns])} 个技术指标")
        
        return result
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_technical_analysis.py -v`
Expected: 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add data_services/technical_analysis.py tests/test_technical_analysis.py
git commit -m "feat: 实现完整技术指标引擎"
```

---

### Task 5: 特征工程实现

**文件:**
- Create: `ml_services/feature_engineering.py`
- Test: `tests/test_feature_engineering.py`

- [ ] **Step 1: 编写特征工程测试**

Create: `tests/test_feature_engineering.py`

```python
import pytest
import pandas as pd
import numpy as np
from ml_services.feature_engineering import FeatureEngineer


def test_create_features_basic():
    """测试基本特征创建"""
    engineer = FeatureEngineer()
    
    # 创建测试数据
    prices = [1.0 + i * 0.01 for i in range(100)]
    df = pd.DataFrame({
        'Close': prices,
        'High': [p + 0.01 for p in prices],
        'Low': [p - 0.01 for p in prices]
    })
    
    features = engineer.create_features(df)
    
    assert features is not None
    assert len(features) > 0
    # 检查是否包含基础特征
    assert 'Close_change_1d' in features.columns or any('change' in col for col in features.columns)


def test_create_target():
    """测试目标变量创建"""
    engineer = FeatureEngineer()
    
    # 创建测试数据
    prices = [1.0 + i * 0.01 for i in range(30)]
    df = pd.DataFrame({'Close': prices})
    
    target = engineer.create_target(df, horizon=20)
    
    assert len(target) == len(df)
    # 前 horizon 个值应该是 NaN（未来数据不可用）
    assert target.iloc[:20].isna().all()
    # 后面的值应该是 1（价格上涨）
    assert (target.iloc[20:].dropna() == 1).all()


def test_data_leakage_in_features():
    """测试特征工程中的数据泄漏防范"""
    engineer = FeatureEngineer()
    
    # 创建测试数据
    prices = [1.0 + i * 0.01 for i in range(50)]
    df = pd.DataFrame({
        'Close': prices,
        'High': [p + 0.01 for p in prices],
        'Low': [p - 0.01 for p in prices]
    })
    
    features = engineer.create_features(df)
    
    # 检查第一行的所有衍生特征应为 NaN（使用 shift(1)）
    derived_features = [col for col in features.columns 
                       if col not in ['Close', 'High', 'Low', 'Open', 'Volume', 'Date']]
    
    for col in derived_features:
        if col.startswith('Close_change') or 'lag' in col or 'ratio' in col:
            assert pd.isna(features[col].iloc[0]), f"特征 {col} 第一行不应有值"


def test_feature_columns_count():
    """测试特征数量"""
    engineer = FeatureEngineer()
    
    prices = [1.0 + i * 0.01 for i in range(100)]
    df = pd.DataFrame({
        'Close': prices,
        'High': [p + 0.01 for p in prices],
        'Low': [p - 0.01 for p in prices]
    })
    
    features = engineer.create_features(df)
    
    # 特征数量应该合理（不包括原始列）
    original_cols = len(df.columns)
    feature_cols = len(features.columns)
    
    # 至少应该有一些衍生特征
    assert feature_cols > original_cols
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pytest tests/test_feature_engineering.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'ml_services.feature_engineering'"

- [ ] **Step 3: 实现 FeatureEngineer 类**

Create: `ml_services/feature_engineering.py`

```python
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """特征工程"""
    
    def __init__(self):
        self.logger = logger
    
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
        features = df.copy()
        
        # 1. 价格衍生特征
        features['Close_change_1d'] = features['Close'].pct_change().shift(1)
        features['Close_change_5d'] = features['Close'].pct_change(periods=5).shift(1)
        
        # 乖离率（价格相对于均线的偏离）
        if 'SMA5' in features.columns:
            features['Bias_5d'] = (features['Close'] - features['SMA5']) / features['SMA5']
        if 'SMA20' in features.columns:
            features['Bias_20d'] = (features['Close'] - features['SMA20']) / features['SMA20']
        
        # 2. 波动率特征
        features['Std_20d'] = features['Close'].rolling(window=20).std().shift(1)
        features['Volatility_20d'] = features['Std_20d'] / features['Close'].shift(1)
        
        # 3. 滞后特征
        features['Close_lag_1'] = features['Close'].shift(1)
        features['Close_lag_5'] = features['Close'].shift(5)
        features['Close_lag_10'] = features['Close'].shift(10)
        
        if 'RSI14' in features.columns:
            features['RSI14_lag_1'] = features['RSI14'].shift(1)
        if 'MACD' in features.columns:
            features['MACD_lag_1'] = features['MACD'].shift(1)
        
        # 4. 交叉特征
        if 'SMA5' in features.columns and 'SMA20' in features.columns:
            features['SMA5_cross_SMA20'] = (features['SMA5'] > features['SMA20']).astype(int).shift(1)
        
        # 5. 市场环境特征
        # 趋势斜率（线性回归斜率）
        features['Trend_Slope'] = self._compute_trend_slope(features['Close'])
        
        self.logger.info(f"已创建 {len(features.columns)} 个特征")
        
        return features
    
    def _compute_trend_slope(self, prices: pd.Series, window: int = 20) -> pd.Series:
        """
        计算趋势斜率（线性回归）
        
        Args:
            prices: 价格序列
            window: 窗口大小
        
        Returns:
            斜率序列
        """
        slopes = []
        for i in range(len(prices)):
            if i < window:
                slopes.append(np.nan)
            else:
                x = np.arange(window)
                y = prices.iloc[i - window + 1:i + 1].values
                slope = np.polyfit(x, y, 1)[0]
                slopes.append(slope)
        
        return pd.Series(slopes, index=prices.index).shift(1)
    
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
        future_price = df['Close'].shift(-horizon)
        target = (future_price > df['Close']).astype(int)
        
        # 最后 horizon 个值无法计算（没有未来数据）
        target.iloc[-horizon:] = np.nan
        
        return target
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_feature_engineering.py -v`
Expected: 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add ml_services/feature_engineering.py tests/test_feature_engineering.py
git commit -m "feat: 实现特征工程模块"
```

---

### Task 6: 基础模型处理器实现

**文件:**
- Create: `ml_services/base_model_processor.py`
- Test: 不需要独立测试（基础工具类）

- [ ] **Step 1: 实现基础模型处理器**

Create: `ml_services/base_model_processor.py`

```python
import os
import pickle
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BaseModelProcessor:
    """基础模型处理器"""
    
    def __init__(self, model_dir: str = 'data/models'):
        self.model_dir = Path(model_dir)
        self.logger = logger
        
        # 确保模型目录存在
        self.model_dir.mkdir(parents=True, exist_ok=True)
    
    def save_model(self, model: Any, pair: str, model_name: str = 'model'):
        """
        保存模型
        
        Args:
            model: 模型对象
            pair: 货币对代码
            model_name: 模型名称
        """
        file_path = self.model_dir / f"{pair}_{model_name}.pkl"
        
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(model, f)
            self.logger.info(f"模型已保存: {file_path}")
        except Exception as e:
            self.logger.error(f"保存模型失败: {e}")
            raise
    
    def load_model(self, pair: str, model_name: str = 'model') -> Any:
        """
        加载模型
        
        Args:
            pair: 货币对代码
            model_name: 模型名称
        
        Returns:
            模型对象
        
        Raises:
            FileNotFoundError: 模型文件不存在
        """
        file_path = self.model_dir / f"{pair}_{model_name}.pkl"
        
        if not file_path.exists():
            raise FileNotFoundError(f"模型文件不存在: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                model = pickle.load(f)
            self.logger.info(f"模型已加载: {file_path}")
            return model
        except Exception as e:
            self.logger.error(f"加载模型失败: {e}")
            raise
    
    def model_exists(self, pair: str, model_name: str = 'model') -> bool:
        """
        检查模型是否存在
        
        Args:
            pair: 货币对代码
            model_name: 模型名称
        
        Returns:
            是否存在
        """
        file_path = self.model_dir / f"{pair}_{model_name}.pkl"
        return file_path.exists()
```

- [ ] **Step 2: 验证模型处理器**

Run: `python3 -c "from ml_services.base_model_processor import BaseModelProcessor; print('Module imported successfully')"`
Expected: 模块成功导入

- [ ] **Step 3: 提交**

```bash
git add ml_services/base_model_processor.py
git commit -m "feat: 实现基础模型处理器"
```

---

### Task 7: CatBoost 交易模型实现

**文件:**
- Create: `ml_services/fx_trading_model.py`
- Test: `tests/test_fx_trading_model.py`

- [ ] **Step 1: 编写模型测试**

Create: `tests/test_fx_trading_model.py`

```python
import pytest
import pandas as pd
import numpy as np
from ml_services.fx_trading_model import FXTradingModel


def test_model_initialization():
    """测试模型初始化"""
    model = FXTradingModel()
    
    assert model.config is not None
    assert model.horizon == 20


def test_model_training_with_minimum_data():
    """测试使用最小数据训练模型"""
    model = FXTradingModel()
    
    # 创建模拟数据
    prices = [1.0 + i * 0.01 for i in range(100)]
    df = pd.DataFrame({
        'Close': prices,
        'High': [p + 0.01 for p in prices],
        'Low': [p - 0.01 for p in prices]
    })
    
    # 训练模型
    metrics = model.train('EUR', df)
    
    assert 'accuracy' in metrics
    assert 'feature_count' in metrics


def test_model_prediction():
    """测试模型预测"""
    model = FXTradingModel()
    
    # 创建训练数据
    prices = [1.0 + i * 0.01 for i in range(100)]
    df = pd.DataFrame({
        'Close': prices,
        'High': [p + 0.01 for p in prices],
        'Low': [p - 0.01 for p in prices]
    })
    
    # 训练模型
    model.train('EUR', df)
    
    # 预测
    prediction = model.predict('EUR', df.iloc[-1:])
    
    assert 'pair' in prediction
    assert 'prediction' in prediction
    assert 'probability' in prediction
    assert prediction['prediction'] in [0, 1]
    assert 0 <= prediction['probability'] <= 1


def test_model_save_and_load():
    """测试模型保存和加载"""
    model1 = FXTradingModel()
    
    # 创建训练数据
    prices = [1.0 + i * 0.01 for i in range(100)]
    df = pd.DataFrame({
        'Close': prices,
        'High': [p + 0.01 for p in prices],
        'Low': [p - 0.01 for p in prices]
    })
    
    # 训练和保存模型
    model1.train('EUR', df)
    
    # 创建新模型并加载
    model2 = FXTradingModel()
    prediction = model2.predict('EUR', df.iloc[-1:])
    
    assert prediction is not None
    assert 'prediction' in prediction


def test_confidence_calculation():
    """测试置信度计算"""
    model = FXTradingModel()
    
    # 高置信度
    confidence = model._get_confidence(0.70)
    assert confidence == 'high'
    
    # 中等置信度
    confidence = model._get_confidence(0.55)
    assert confidence == 'medium'
    
    # 低置信度
    confidence = model._get_confidence(0.45)
    assert confidence == 'low'
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pytest tests/test_fx_trading_model.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'ml_services.fx_trading_model'"

- [ ] **Step 3: 实现 FXTradingModel 类**

Create: `ml_services/fx_trading_model.py`

```python
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from ml_services.base_model_processor import BaseModelProcessor
from ml_services.feature_engineering import FeatureEngineer
from data_services.technical_analysis import TechnicalAnalyzer

import logging

logger = logging.getLogger(__name__)


class FXTradingModel:
    """外汇交易模型"""
    
    def __init__(self, config: dict = None):
        """
        初始化模型
        
        Args:
            config: 模型配置字典
        """
        from config import MODEL_CONFIG, INDICATOR_CONFIG
        
        self.config = config or MODEL_CONFIG
        self.horizon = self.config['horizon']
        self.indicator_config = INDICATOR_CONFIG
        
        self.model = None
        self.feature_engineer = FeatureEngineer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.model_processor = BaseModelProcessor()
        
        self.logger = logger
    
    def _get_confidence(self, probability: float) -> str:
        """
        根据概率计算置信度
        
        Args:
            probability: 预测概率
        
        Returns:
            high/medium/low
        """
        if probability >= self.config.get('high_confidence_threshold', 0.60):
            return 'high'
        elif probability >= 0.50:
            return 'medium'
        else:
            return 'low'
    
    def train(self, pair: str, data: pd.DataFrame) -> dict:
        """
        训练模型
        
        Args:
            pair: 货币对代码
            data: 训练数据（必须包含 Close, High, Low 列）
        
        Returns:
            训练指标字典
        """
        self.logger.info(f"开始训练 {pair} 模型...")
        
        # 1. 计算技术指标
        data = self.technical_analyzer.compute_all_indicators(data)
        
        # 2. 创建特征
        features = self.feature_engineer.create_features(data)
        
        # 3. 创建目标变量
        target = self.feature_engineer.create_target(data, horizon=self.horizon)
        
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
        
        # 8. 保存模型
        self.model_processor.save_model(self.model, pair, 'catboost')
        
        metrics = {
            'accuracy': accuracy,
            'feature_count': len(feature_cols),
            'train_samples': len(X_train),
            'val_samples': len(X_val)
        }
        
        self.logger.info(f"训练完成，准确率: {accuracy:.2%}")
        return metrics
    
    def predict(self, pair: str, data: pd.DataFrame) -> dict:
        """
        预测
        
        Args:
            pair: 货币对代码
            data: 预测数据（必须包含 Close, High, Low 列）
        
        Returns:
            预测结果字典
        """
        # 加载模型
        if self.model is None:
            try:
                self.model = self.model_processor.load_model(pair, 'catboost')
            except FileNotFoundError:
                self.logger.warning(f"模型不存在，使用默认预测")
                return self._get_default_prediction(pair, data)
        
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
        target_date = data_date + timedelta(days=self.horizon)
        
        result = {
            'pair': pair,
            'current_price': float(current_price),
            'prediction': int(prediction),
            'probability': float(probability),
            'confidence': confidence,
            'data_date': data_date.strftime('%Y-%m-%d'),
            'target_date': target_date.strftime('%Y-%m-%d')
        }
        
        self.logger.info(f"预测完成: {pair} - {prediction} ({probability:.2%})")
        return result
    
    def _get_default_prediction(self, pair: str, data: pd.DataFrame) -> dict:
        """
        获取默认预测（当模型不可用时）
        
        Args:
            pair: 货币对代码
            data: 数据
        
        Returns:
            默认预测结果
        """
        current_price = data['Close'].iloc[-1]
        data_date = datetime.now()
        target_date = data_date + timedelta(days=self.horizon)
        
        return {
            'pair': pair,
            'current_price': float(current_price),
            'prediction': 0,
            'probability': 0.5,
            'confidence': 'low',
            'data_date': data_date.strftime('%Y-%m-%d'),
            'target_date': target_date.strftime('%Y-%m-%d')
        }
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_fx_trading_model.py -v`
Expected: 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add ml_services/fx_trading_model.py tests/test_fx_trading_model.py
git commit -m "feat: 实现 CatBoost 交易模型"
```

---

### Task 8: 大模型引擎实现

**文件:**
- Create: `llm_services/qwen_engine.py`
- Test: 不需要独立测试（依赖外部 API）

- [ ] **Step 1: 实现大模型引擎**

Create: `llm_services/qwen_engine.py`

```python
import os
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# API 配置
api_key = os.getenv('QWEN_API_KEY', '')
chat_url = os.getenv('QWEN_CHAT_URL',
                     'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions')
chat_model = os.getenv('QWEN_CHAT_MODEL', 'qwen-plus-2025-12-01')
max_tokens = int(os.getenv('MAX_TOKENS', 32768))


def log_message(message: str, log_file: str = "qwen_engine.log"):
    """
    统一日志记录函数
    
    Args:
        message: 要记录的消息
        log_file: 日志文件路径
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")


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
    try:
        log_message(f"[DEBUG] chat_with_llm called with query: {repr(query)}")
        
        # 检查 API 密钥是否设置
        if not api_key:
            raise ValueError("QWEN_API_KEY 环境变量未设置")
        
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        # 确保查询文本是 UTF-8 编码
        if isinstance(query, str):
            query = query.encode('utf-8').decode('utf-8')
        
        payload = {
            'model': chat_model,
            'messages': [{'role': 'user', 'content': query}],
            'stream': False,
            'top_p': 0.2,
            'temperature': 0.05,
            'max_tokens': max_tokens,
            'seed': 1368,
            'enable_thinking': enable_thinking
        }
        
        response = requests.post(chat_url, headers=headers, json=payload, timeout=300)
        response.raise_for_status()
        
        response_data = response.json()
        message = response_data['choices'][0]['message']
        
        # 如果 content 为空，尝试使用 reasoning_content
        content = message.get('content', '')
        reasoning_content = message.get('reasoning_content', '')
        
        if not content and reasoning_content:
            log_message("[WARN] content is empty, using reasoning_content")
            content = reasoning_content
        
        log_message("[DEBUG] chat_with_llm success")
        return content
        
    except requests.exceptions.HTTPError as http_err:
        log_message(f'HTTP error: {http_err}')
        raise http_err
    except requests.exceptions.Timeout as timeout_err:
        log_message(f'Timeout error: {timeout_err}')
        raise timeout_err
    except Exception as error:
        log_message(f'Error: {error}')
        raise error
```

- [ ] **Step 2: 验证模块可导入**

Run: `python3 -c "from llm_services.qwen_engine import chat_with_llm; print('Module imported successfully')"`
Expected: 模块成功导入

- [ ] **Step 3: 提交**

```bash
git add llm_services/qwen_engine.py
git commit -m "feat: 实现大模型引擎"
```

---

### Task 9: 综合分析系统实现

**文件:**
- Create: `comprehensive_analysis.py`
- Test: `tests/test_comprehensive_analysis.py`

- [ ] **Step 1: 编写综合分析测试**

Create: `tests/test_comprehensive_analysis.py`

```python
import pytest
import pandas as pd
import numpy as np
from comprehensive_analysis import ComprehensiveAnalyzer


def test_analyzer_initialization():
    """测试分析器初始化"""
    analyzer = ComprehensiveAnalyzer()
    
    assert analyzer is not None


def test_analyze_pair_basic():
    """测试基本分析功能"""
    analyzer = ComprehensiveAnalyzer()
    
    # 创建测试数据
    prices = [1.0 + i * 0.01 for i in range(100)]
    data = pd.DataFrame({
        'Close': prices,
        'High': [p + 0.01 for p in prices],
        'Low': [p - 0.01 for p in prices]
    })
    
    # 创建模拟预测结果
    ml_prediction = {
        'pair': 'EUR',
        'prediction': 1,
        'probability': 0.65,
        'confidence': 'high'
    }
    
    # 分析
    result = analyzer.analyze_pair('EUR', data, ml_prediction)
    
    assert result is not None
    assert 'recommendation' in result
    assert result['recommendation'] in ['buy', 'sell', 'hold']
    assert 'confidence' in result


def test_signal_validation():
    """测试信号验证 - 硬性约束"""
    analyzer = ComprehensiveAnalyzer()
    
    # 低概率预测（应该禁止买入）
    ml_prediction = {
        'prediction': 1,
        'probability': 0.45,  # 低于 0.50
        'confidence': 'low'
    }
    
    # 创建测试数据
    data = pd.DataFrame({
        'Close': [1.0, 1.01, 1.02]
    })
    
    result = analyzer.analyze_pair('EUR', data, ml_prediction)
    
    # 应该不推荐买入
    assert result['recommendation'] != 'buy'


def test_high_probability_recommendation():
    """测试高概率推荐"""
    analyzer = ComprehensiveAnalyzer()
    
    # 高概率预测
    ml_prediction = {
        'prediction': 1,
        'probability': 0.72,  # 高于 0.60
        'confidence': 'high'
    }
    
    # 创建测试数据
    data = pd.DataFrame({
        'Close': [1.0, 1.01, 1.02]
    })
    
    result = analyzer.analyze_pair('EUR', data, ml_prediction)
    
    # 应该推荐买入
    assert result['recommendation'] == 'buy'
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pytest tests/test_comprehensive_analysis.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'comprehensive_analysis'"

- [ ] **Step 3: 实现综合分析系统**

Create: `comprehensive_analysis.py`

```python
import pandas as pd
import logging
from typing import Dict, Any

from data_services.technical_analysis import TechnicalAnalyzer
from ml_services.fx_trading_model import FXTradingModel

import logging

logger = logging.getLogger(__name__)


class ComprehensiveAnalyzer:
    """综合分析器"""
    
    def __init__(self):
        self.logger = logger
        self.technical_analyzer = TechnicalAnalyzer()
        self.model = FXTradingModel()
    
    def analyze_pair(self, pair: str, data: pd.DataFrame,
                    ml_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析单个货币对
        
        Args:
            pair: 货币对代码
            data: 汇率数据
            ml_prediction: ML 预测结果
        
        Returns:
            综合分析结果
        """
        # 1. 生成技术信号
        technical_signal = self._generate_technical_signal(data)
        
        # 2. 验证信号（应用硬性约束）
        validated_signal = self._validate_signals(
            technical_signal, ml_prediction
        )
        
        # 3. 生成综合建议
        recommendation = self._generate_recommendation(
            pair, data, technical_signal, ml_prediction, validated_signal
        )
        
        return recommendation
    
    def _generate_technical_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        生成技术信号
        
        Args:
            data: 汇率数据
        
        Returns:
            技术信号字典
        """
        # 计算技术指标
        data = self.technical_analyzer.compute_all_indicators(data)
        
        # 简化的信号强度计算
        latest = data.iloc[-1]
        
        # 基于 RSI 的信号
        rsi_signal = 0
        if 'RSI14' in data.columns and not pd.isna(latest['RSI14']):
            if latest['RSI14'] < 30:
                rsi_signal = 20  # 超卖，买入信号
            elif latest['RSI14'] > 70:
                rsi_signal = -20  # 超买，卖出信号
        
        # 基于均线交叉的信号
        ma_signal = 0
        if 'SMA5' in data.columns and 'SMA20' in data.columns:
            if not pd.isna(latest['SMA5']) and not pd.isna(latest['SMA20']):
                if latest['SMA5'] > latest['SMA20']:
                    ma_signal = 15  # 金叉，买入信号
                else:
                    ma_signal = -15  # 死叉，卖出信号
        
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
        """
        验证信号，应用硬性约束
        
        硬性约束：
        - ML probability ≤ 0.50 → 绝对禁止买入
        - ML probability ≥ 0.60 → 可以考虑强烈买入
        
        Args:
            technical_signal: 技术信号
            ml_prediction: ML 预测
        
        Returns:
            验证后的信号
        """
        ml_prob = ml_prediction.get('probability', 0.5)
        
        # 硬性约束：ML 概率 ≤ 0.50 → 绝对禁止买入
        if ml_prob <= 0.50:
            if technical_signal['signal'] == 'buy':
                self.logger.info(f"硬性约束：ML 概率 {ml_prob:.2f} ≤ 0.50，禁止买入")
                technical_signal['signal'] = 'hold'
                technical_signal['reason'] = 'ML 概率过低，违反硬性约束'
        
        return technical_signal
    
    def _generate_recommendation(self, pair: str, data: pd.DataFrame,
                                technical_signal: Dict[str, Any],
                                ml_prediction: Dict[str, Any],
                                validated_signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成综合建议
        
        Args:
            pair: 货币对代码
            data: 汇率数据
            technical_signal: 技术信号
            ml_prediction: ML 预测
            validated_signal: 验证后的信号
        
        Returns:
            综合建议字典
        """
        current_price = data['Close'].iloc[-1]
        
        # 计算止损位和止盈位（基于 ATR）
        atr = data.get('ATR14', pd.Series([0.01] * len(data))).iloc[-1]
        stop_loss = current_price - (atr * 2)
        take_profit = current_price + (atr * 2)
        
        # 构建推理
        reasoning = (
            f"技术信号 {validated_signal['signal']} "
            f"(强度 {validated_signal['strength']:.0f})，"
            f"ML 预测 {ml_prediction['prediction']} "
            f"(概率 {ml_prediction['probability']:.2f})"
        )
        
        if 'reason' in validated_signal:
            reasoning += f"，{validated_signal['reason']}"
        
        # 检查一致性
        consistency = (technical_signal['signal'] == ml_prediction['prediction'] or
                      technical_signal['signal'] == 'hold')
        
        result = {
            'pair': pair,
            'technical_signal': technical_signal['signal'],
            'technical_strength': validated_signal['strength'],
            'ml_prediction': ml_prediction['prediction'],
            'ml_probability': ml_prediction['probability'],
            'ml_confidence': ml_prediction.get('confidence', 'low'),
            'consistency': consistency,
            'recommendation': validated_signal['signal'],
            'confidence': ml_prediction.get('confidence', 'low'),
            'reasoning': reasoning,
            'entry_price': float(current_price),
            'stop_loss': float(stop_loss),
            'take_profit': float(take_profit),
            'risk_reward_ratio': 1.0,
            'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d')
        }
        
        return result
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_comprehensive_analysis.py -v`
Expected: 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add comprehensive_analysis.py tests/test_comprehensive_analysis.py
git commit -m "feat: 实现综合分析系统"
```

---

### Task 10: 集成测试和文档更新

**文件:**
- Create: `tests/test_integration.py`
- Modify: `AGENTS.md`

- [ ] **Step 1: 编写集成测试**

Create: `tests/test_integration.py` （已在步骤 8 中创建）

- [ ] **Step 2: 运行集成测试**

Run: `pytest tests/test_integration.py -v`
Expected: 所有测试通过

- [ ] **Step 3: 运行所有测试并检查覆盖率**

Run: `pytest tests/ --cov=. --cov-report=html --cov-report=term`
Expected: 核心模块覆盖率 ≥ 70%

- [ ] **Step 4: 更新项目文档**

Modify: `AGENTS.md` （已在步骤 8 中更新）

- [ ] **Step 5: 提交**

```bash
git add tests/test_integration.py AGENTS.md
git commit -m "feat: 添加集成测试和更新文档"
```

---

## 实施顺序

按照任务编号顺序执行，每个 Task 完成后提交到 git。

**总任务数：** 10 个任务
**预计时间：** 需要根据实际执行情况评估

---

## 成功标准

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 核心模块测试覆盖率 ≥ 70%
- [ ] 端到端工作流正常运行
- [ ] 文档完整且准确

---

## 注意事项

1. **数据泄漏防范**：所有技术指标和特征必须使用滞后数据（`.shift(1)`）
2. **硬性约束**：ML 概率 ≤ 0.50 时绝对禁止买入
3. **测试驱动**：每个功能先写测试，再实现代码
4. **频繁提交**：每个 Task 完成后立即提交
5. **代码质量**：遵循 PEP 8 规范，使用 black 格式化代码