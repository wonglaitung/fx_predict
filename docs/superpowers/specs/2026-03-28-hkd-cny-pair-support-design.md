# 设计文档：添加 HKD/CNY 货币对支持

**日期：** 2026-03-28
**状态：** 设计中
**作者：** iFlow CLI

---

## 1. 概述

### 1.1 背景

当前系统支持 6 个货币对（EUR/USD、USD/JPY、AUD/USD、GBP/USD、USD/CAD、NZD/USD）。用户希望添加港币/人民币（HKD/CNY）货币对支持。

### 1.2 需求

- 添加 HKD/CNY 作为第 7 个货币对
- 数据源：Yahoo Finance（`HKDCNY=X` ticker）
- 支持方式：通过配置驱动，最小化代码变更
- 缺失数据处理：记录警告日志，不影响其他货币对处理
- 预测周期：与现有货币对一致（1天、5天、20天）

### 1.3 目标

- 系统自动识别并支持 HKD/CNY
- 复用现有功能（数据加载、模型训练、预测、Dashboard、LLM 分析）
- 保持向后兼容，不影响现有 6 个货币对

---

## 2. 架构设计

### 2.1 整体架构

系统采用配置驱动的扩展方式。通过修改配置文件添加 HKD/CNY，核心逻辑无需变更。系统会自动识别新货币对，并复用所有现有功能。

```
Yahoo Finance → fetch_fx_data.py (HKDCNY=X) → 合并 Excel 文件
                                                    ↓
                        excel_loader.py 加载 (支持 HKD 工作表，缺失时警告)
                                                    ↓
                technical_analysis.py 计算 35 个技术指标
                                                    ↓
                fx_trading_model.py 训练 3 个周期模型 (1d/5d/20d)
                                                    ↓
                comprehensive_analysis.py 多周期预测 + LLM 分析
                                                    ↓
                Dashboard 显示 HKD/CNY 卡片和策略
```

### 2.2 设计原则

- **最小侵入**：仅修改配置文件，不改动核心逻辑
- **向后兼容**：现有功能完全不受影响
- **优雅降级**：数据缺失时警告并跳过，不中断流程
- **自动继承**：新货币对自动继承所有功能

---

## 3. 组件设计

### 3.1 config.py

**改动内容：**

```python
# 货币对配置
CURRENCY_PAIRS = {
    'EUR': {'symbol': 'EURUSD', 'name': '欧元/美元'},
    'JPY': {'symbol': 'USDJPY', 'name': '美元/日元'},
    'AUD': {'symbol': 'AUDUSD', 'name': '澳元/美元'},
    'GBP': {'symbol': 'GBPUSD', 'name': '英镑/美元'},
    'CAD': {'symbol': 'USDCAD', 'name': '美元/加元'},
    'NZD': {'symbol': 'NZDUSD', 'name': '新西兰元/美元'},
    'HKD': {'symbol': 'HKDCNY', 'name': '港币/人民币'}  # 新增
}

# 数据配置
DATA_CONFIG = {
    'data_file': 'data/raw/FXRate_20260320.xlsx',
    'supported_pairs': ['EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'NZD', 'HKD'],  # 新增 HKD
    'pair_symbols': {
        'EUR': 'EURUSD',
        'JPY': 'USDJPY',
        'GBP': 'GBPUSD',
        'AUD': 'AUDUSD',
        'CAD': 'USDCAD',
        'NZD': 'NZDUSD',
        'HKD': 'HKDCNY'  # 新增
    },
    # ... 其他配置保持不变
}
```

**影响：** 所有读取 `CURRENCY_PAIRS` 的模块自动支持 HKD

### 3.2 fetch_fx_data.py

**改动内容：**

```python
# 货币对映射：pair_code -> yfinance ticker
PAIR_TICKERS = {
    'EUR': 'EURUSD=X',
    'JPY': 'USDJPY=X',
    'AUD': 'AUDUSD=X',
    'GBP': 'GBPUSD=X',
    'CAD': 'USDCAD=X',
    'NZD': 'NZDUSD=X',
    'HKD': 'HKDCNY=X'  # 新增
}

# 货币对中文名称
PAIR_NAMES = {
    'EUR': 'EUR/USD',
    'JPY': 'USD/JPY',
    'AUD': 'AUD/USD',
    'GBP': 'GBP/USD',
    'CAD': 'USD/CAD',
    'NZD': 'NZD/USD',
    'HKD': 'HKD/CNY'  # 新增
}
```

**影响：** `fetch_all_pairs()` 自动获取 HKD 数据

### 3.3 其他组件（无需修改）

- **excel_loader.py**：已支持任意工作表名称，自动处理缺失（警告 + 跳过）
- **fx_trading_model.py**：遍历 `CURRENCY_PAIRS.keys()`，自动训练 HKD 模型
- **comprehensive_analysis.py**：自动处理 HKD 的多周期分析
- **dashboard/server.js**：API 自动返回 HKD 数据
- **dashboard/public/js/app.js**：自动渲染 HKD 卡片

---

## 4. 数据流设计

### 4.1 数据获取流程

```
用户执行: python3 fetch_fx_data.py --merge
         ↓
遍历 PAIR_TICKERS (包括 HKD)
         ↓
yfinance.download('HKDCNY=X', start_date, end_date)
         ↓
格式化为 Date/Close 列
         ↓
保存为单独文件: data/raw/HKD_data.xlsx
         ↓
合并到: data/raw/FXRate_{date}_yahoo.xlsx
         ↓
Excel 文件包含 HKD 工作表
```

### 4.2 数据加载流程（支持缺失）

```
用户上传文件或运行分析
         ↓
excel_loader.load_all_pairs(file_path)
         ↓
遍历所有工作表 (包括 HKD)
         ↓
工作表 HKD 存在？
  ├─ 是 → 加载数据，计算技术指标
  └─ 否 → 记录 WARNING 日志，跳过 HKD
         ↓
继续处理其他货币对
```

### 4.3 模型训练和预测流程

```
用户执行: ./run_full_pipeline.sh
         ↓
遍历 CURRENCY_PAIRS (包括 HKD)
         ↓
HKD 数据存在且充足？
  ├─ 是 → 训练 3 个模型 (1d/5d/20d)
  └─ 否 → 跳过 HKD，记录日志
         ↓
生成预测结果 JSON
         ↓
Dashboard 自动显示 HKD
```

---

## 5. 错误处理和边缘情况

### 5.1 数据缺失处理

**场景：** 上传的文件缺少 HKD 工作表

**处理流程：**
```
excel_loader.load_pair('HKD', file_path)
         ↓
抛出 ValueError("工作表不存在: HKD")
         ↓
load_all_pairs() 捕获异常
         ↓
记录 WARNING: "加载货币对 HKD 失败: 工作表不存在: HKD"
         ↓
继续处理其他货币对
```

**日志示例：**
```
WARNING - 加载货币对 HKD 失败: 工作表不存在: HKD
INFO - 成功加载 6 个货币对
```

### 5.2 Yahoo Finance 数据获取失败

**场景：** `yfinance.download()` 返回空数据

**处理流程：**
```
fetch_pair_data('HKD', start_date, end_date)
         ↓
yfinance.download('HKDCNY=X', ...) 返回空 DataFrame
         ↓
df.empty 为 True
         ↓
记录 WARNING: "未获取到 HKD 的数据"
         ↓
返回空 DataFrame
         ↓
合并时跳过 HKD
```

**日志示例：**
```
WARNING - 未获取到 HKD 的数据
INFO - 成功获取: 6/7 个货币对
```

### 5.3 模型训练失败

**场景：** HKD 数据不足（< 100 条）

**处理流程：**
```
fx_trading_model.train('HKD', horizon=1)
         ↓
数据点 < DATA_CONFIG['min_data_points']
         ↓
记录 ERROR: "数据点不足，至少需要 100 条"
         ↓
跳过 HKD，继续处理其他货币对
```

### 5.4 边缘情况处理

| 边缘情况 | 处理方式 |
|----------|----------|
| Yahoo Finance ticker 不存在 | 返回空 DataFrame，记录 WARNING，跳过 |
| 数据格式异常 | `excel_loader.py` 自动格式化，缺失列自动生成 |
| API 限流 | yfinance 内置重试，失败后记录日志 |
| 并发请求 | 按顺序获取，避免触发限流 |

---

## 6. 测试策略

### 6.1 单元测试

#### 6.1.1 配置测试（test_config.py - 新建）

```python
def test_hkd_in_currency_pairs():
    """验证 CURRENCY_PAIRS 包含 HKD"""
    assert 'HKD' in config.CURRENCY_PAIRS
    assert config.CURRENCY_PAIRS['HKD']['symbol'] == 'HKDCNY'
    assert config.CURRENCY_PAIRS['HKD']['name'] == '港币/人民币'

def test_hkd_in_supported_pairs():
    """验证 supported_pairs 包含 HKD"""
    assert 'HKD' in config.DATA_CONFIG['supported_pairs']

def test_hkd_pair_symbol():
    """验证 pair_symbols 包含 HKD"""
    assert 'HKD' in config.DATA_CONFIG['pair_symbols']
    assert config.DATA_CONFIG['pair_symbols']['HKD'] == 'HKDCNY'
```

#### 6.1.2 数据加载测试（扩展 test_excel_loader.py）

```python
def test_load_hkd_pair_success():
    """测试成功加载 HKD 工作表"""
    loader = FXDataLoader()
    df = loader.load_pair('HKD', 'test_data_with_hkd.xlsx')
    assert len(df) > 0
    assert 'Date' in df.columns
    assert 'Close' in df.columns

def test_load_hkd_pair_missing_sheet():
    """测试 HKD 工作表不存在时抛出 ValueError"""
    loader = FXDataLoader()
    with pytest.raises(ValueError, match="工作表不存在: HKD"):
        loader.load_pair('HKD', 'test_data_without_hkd.xlsx')

def test_load_all_pairs_missing_hkd():
    """测试缺少 HKD 工作表时记录警告并跳过"""
    loader = FXDataLoader()
    result = loader.load_all_pairs('test_data_without_hkd.xlsx')
    assert 'HKD' not in result
    assert len(result) == 6  # 只有其他 6 个货币对
```

#### 6.1.3 数据获取测试（test_fetch_fx_data.py - 新建）

```python
def test_fetch_hkd_pair_data():
    """测试从 Yahoo Finance 获取 HKD 数据"""
    df = fetch_pair_data('HKD', '2025-01-01', '2025-12-31')
    assert len(df) > 0
    assert 'Date' in df.columns
    assert 'Close' in df.columns

def test_fetch_hkd_pair_data_ticker_not_found():
    """测试 ticker 不存在时返回空 DataFrame"""
    df = fetch_pair_data('INVALID', '2025-01-01', '2025-12-31')
    assert df.empty
```

### 6.2 集成测试

#### 6.2.1 端到端测试（扩展 test_integration.py）

```python
def test_hkd_end_to_end_workflow():
    """测试 HKD 完整流程"""
    # 1. 获取数据
    results = fetch_all_pairs('2025-01-01', '2025-12-31')
    assert 'HKD' in results

    # 2. 训练模型
    for horizon in [1, 5, 20]:
        model = fx_trading_model.train('HKD', horizon=horizon)
        assert model is not None

    # 3. 生成预测
    predictions = fx_trading_model.predict('HKD')
    assert '1_day' in predictions
    assert '5_day' in predictions
    assert '20_day' in predictions

    # 4. LLM 分析
    analysis = comprehensive_analysis.analyze_pair('HKD')
    assert 'metadata' in analysis
    assert analysis['metadata']['pair'] == 'HKD'

def test_missing_hkd_data_degradation():
    """测试缺少 HKD 数据时的降级行为"""
    # 使用不含 HKD 的文件
    all_pairs = excel_loader.load_all_pairs('test_data_without_hkd.xlsx')
    assert 'HKD' not in all_pairs

    # 其他货币对正常处理
    assert 'EUR' in all_pairs
    assert len(all_pairs) == 6
```

#### 6.2.2 Dashboard 测试（扩展 dashboard/tests/api/api.test.js）

```javascript
test('GET /api/v1/pairs includes HKD', async () => {
  const response = await request(app).get('/api/v1/pairs');
  expect(response.status).toBe(200);
  expect(response.body).toHaveLength(7); // 6 个原有 + HKD
  expect(response.body.some(p => p.pair === 'HKD')).toBe(true);
});

test('GET /api/v1/pairs/HKD returns HKD details', async () => {
  const response = await request(app).get('/api/v1/pairs/HKD');
  expect(response.status).toBe(200);
  expect(response.body.metadata.pair).toBe('HKD');
  expect(response.body.metadata.pair_name).toBe('港币/人民币');
});
```

### 6.3 验收标准

- ✅ `config.py` 成功添加 HKD 配置
- ✅ `fetch_fx_data.py` 可以从 Yahoo Finance 获取 HKD/CNY 数据
- ✅ `run_full_pipeline.sh` 成功训练 HKD 的 3 个模型（1d/5d/20d）
- ✅ Dashboard 正常显示 HKD/CNY 卡片和策略
- ✅ 人工上传文件缺少 HKD 工作表时，系统记录警告并继续处理
- ✅ 所有现有测试通过（无回归）
- ✅ 新增测试通过

---

## 7. 实现影响和风险

### 7.1 向后兼容性

- ✅ 完全兼容，现有 6 个货币对不受任何影响
- ✅ 现有模型文件、预测文件、Dashboard 正常运行
- ✅ 无需迁移数据或修改现有工作流

### 7.2 性能影响

- ✅ 可忽略。增加 1 个货币对，训练时间增加约 15%（从 6 个增加到 7 个）
- ✅ Dashboard 查询性能不受影响（按需加载）

### 7.3 风险和缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| Yahoo Finance 不支持 HKD ticker | HKD 数据无法获取 | 低 | 先用 `yfinance` 验证 ticker 可用性 |
| HKD 数据质量差 | 模型性能不佳 | 中 | 训练后检查准确率，必要时调整参数 |
| 人工上传文件格式错误 | 加载失败 | 低 | `excel_loader.py` 已有完善的格式验证 |
| 配置错误导致系统崩溃 | 系统不可用 | 低 | `config.py` 已有 `validate_config()` 函数 |

### 7.4 依赖项

- yfinance（已安装，无需新增依赖）
- 无新增 Python 包或系统依赖

---

## 8. 实施步骤

### 8.1 配置文件修改

1. 修改 `config.py`：
   - 在 `CURRENCY_PAIRS` 添加 HKD 配置
   - 在 `DATA_CONFIG['supported_pairs']` 添加 'HKD'
   - 在 `DATA_CONFIG['pair_symbols']` 添加 HKD 映射

2. 修改 `fetch_fx_data.py`：
   - 在 `PAIR_TICKERS` 添加 `'HKD': 'HKDCNY=X'`
   - 在 `PAIR_NAMES` 添加 `'HKD': 'HKD/CNY'`

### 8.2 验证 Yahoo Finance ticker

```bash
# 测试 HKD ticker 是否可用
python3 -c "
import yfinance as yf
df = yf.download('HKDCNY=X', start='2025-01-01', end='2025-12-31', progress=False)
print(f'数据量: {len(df)}')
print(df.head())
"
```

### 8.3 获取数据

```bash
# 获取所有货币对数据（包括 HKD）
python3 fetch_fx_data.py --start-date 2020-01-01 --end-date 2026-03-28 --merge

# 验证数据文件
python3 -c "
import pandas as pd
xls = pd.ExcelFile('data/raw/FXRate_20260328_yahoo.xlsx')
print('工作表:', xls.sheet_names)
"
```

### 8.4 运行完整流程

```bash
# 训练模型并生成预测
./run_full_pipeline.sh --skip-training

# 验证模型文件
ls -la data/models/HKD_*.pkl

# 验证预测文件
ls -la data/predictions/HKD_*.json
```

### 8.5 测试和验证

```bash
# 运行所有测试
pytest tests/ -v

# 启动 Dashboard
cd dashboard && npm start

# 访问 http://localhost:3000 验证 HKD/CNY 显示
```

---

## 9. 后续扩展

如果未来需要为 HKD/CNY 自定义参数，可以：

1. 创建独立的配置文件 `config/hkd_cny.py`
2. 修改系统支持动态加载货币对配置
3. 自定义模型参数、预测周期等

---

## 10. 总结

本设计采用最小侵入式扩展方案，通过配置驱动添加 HKD/CNY 货币对支持：

- **核心改动**：仅修改 `config.py` 和 `fetch_fx_data.py`
- **自动继承**：数据加载、模型训练、预测、Dashboard 自动支持新货币对
- **优雅降级**：数据缺失时警告并跳过，不影响其他货币对
- **完整测试**：扩展现有测试用例，确保无回归

整个方案风险低、改动小、可快速交付。