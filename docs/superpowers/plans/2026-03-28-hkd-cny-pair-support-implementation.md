# HKD/CNY 货币对支持实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标：** 在 FX Predict 系统中添加港币/人民币（HKD/CNY）货币对支持，使其与现有 6 个货币对功能完全一致

**架构：** 采用配置驱动扩展方式，仅修改 `config.py` 和 `fetch_fx_data.py`，其他模块自动继承新货币对支持

**技术栈：** Python 3.10+, yfinance, CatBoost, Express (Dashboard)

---

## 文件结构映射

### 修改的文件
- `config.py` - 货币对配置字典
- `fetch_fx_data.py` - Yahoo Finance ticker 映射

### 扩展测试的文件
- `tests/test_excel_loader.py` - 添加 HKD 数据加载测试
- `tests/test_integration.py` - 添加 HKD 端到端测试
- `dashboard/tests/api/api.test.js` - 添加 Dashboard API 测试

### 自动处理的模块（无需修改）
- `data_services/excel_loader.py` - 已支持任意工作表和优雅降级
- `ml_services/fx_trading_model.py` - 自动遍历 CURRENCY_PAIRS
- `comprehensive_analysis.py` - 自动处理 HKD 分析
- `dashboard/server.js` - API 自动返回 HKD 数据

---

## 实施任务

### Task 1: 验证 Yahoo Finance HKD ticker

**目的：** 确认 Yahoo Finance 支持 HKD/CNY ticker（`HKDCNY=X`），避免配置后才发现不可用

**无文件修改**

- [ ] **Step 1: 运行验证脚本**

```bash
python3 -c "
import yfinance as yf
df = yf.download('HKDCNY=X', start='2025-01-01', end='2025-12-31', progress=False)
print(f'数据量: {len(df)}')
print(df.head())
"
```

- [ ] **Step 2: 验证输出**

**预期结果：**
- 显示数据量 > 0（至少有数据）
- 显示包含 Date、Open、High、Low、Close、Adj Close、Volume 列
- 如果输出为空或报错，说明 ticker 不可用，需要调整方案

- [ ] **Step 3: 记录验证结果（手动）**

如果 ticker 可用，继续后续任务；如果不可用，需要与用户讨论替代方案。

---

### Task 2: 修改 config.py 添加 HKD 配置

**文件：**
- Modify: `config.py:16-27` (CURRENCY_PAIRS 字典)
- Modify: `config.py:67-76` (DATA_CONFIG 字典)

- [ ] **Step 1: 读取 config.py 验证当前结构**

运行以下命令确认当前配置位置：
```bash
grep -n "CURRENCY_PAIRS = {" config.py
grep -n "supported_pairs.*EUR" config.py
grep -n "pair_symbols.*EUR" config.py
```

预期输出：
- 第 16 行附近：`CURRENCY_PAIRS = {`
- 第 67 行附近：`'supported_pairs': ['EUR'`
- 第 70 行附近：`'pair_symbols': {`

- [ ] **Step 2: 修改 CURRENCY_PAIRS 添加 HKD**

在 `config.py` 的 `CURRENCY_PAIRS` 字典中，在最后一项后添加：

```python
    'HKD': {'symbol': 'HKDCNY', 'name': '港币/人民币'}
```

**完整 CURRENCY_PAIRS 应该是：**
```python
CURRENCY_PAIRS = {
    'EUR': {'symbol': 'EURUSD', 'name': '欧元/美元'},
    'JPY': {'symbol': 'USDJPY', 'name': '美元/日元'},
    'AUD': {'symbol': 'AUDUSD', 'name': '澳元/美元'},
    'GBP': {'symbol': 'GBPUSD', 'name': '英镑/美元'},
    'CAD': {'symbol': 'USDCAD', 'name': '美元/加元'},
    'NZD': {'symbol': 'NZDUSD', 'name': '新西兰元/美元'},
    'HKD': {'symbol': 'HKDCNY', 'name': '港币/人民币'}
}
```

- [ ] **Step 3: 修改 DATA_CONFIG['supported_pairs'] 添加 HKD**

在 `config.py` 的 `DATA_CONFIG['supported_pairs']` 列表中，在最后添加 `'HKD'`：

```python
'supported_pairs': ['EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'NZD', 'HKD'],
```

- [ ] **Step 4: 修改 DATA_CONFIG['pair_symbols'] 添加 HKD 映射**

在 `config.py` 的 `DATA_CONFIG['pair_symbols']` 字典中，在最后一项后添加：

```python
    'HKD': 'HKDCNY'
```

**完整 pair_symbols 应该是：**
```python
'pair_symbols': {
    'EUR': 'EURUSD',
    'JPY': 'USDJPY',
    'GBP': 'GBPUSD',
    'AUD': 'AUDUSD',
    'CAD': 'USDCAD',
    'NZD': 'NZDUSD',
    'HKD': 'HKDCNY'
}
```

- [ ] **Step 5: 验证配置语法**

运行配置验证：
```bash
python3 -c "import config; config.validate_config()"
```

**预期输出：**
```
配置验证通过
```

- [ ] **Step 6: 提交配置修改**

```bash
git add config.py
git commit -m "feat: add HKD/CNY pair configuration"
```

---

### Task 3: 修改 fetch_fx_data.py 添加 HKD ticker

**文件：**
- Modify: `fetch_fx_data.py:23-33` (PAIR_TICKERS 字典)
- Modify: `fetch_fx_data.py:36-43` (PAIR_NAMES 字典)

- [ ] **Step 1: 读取 fetch_fx_data.py 验证当前结构**

运行以下命令确认当前配置位置：
```bash
grep -n "PAIR_TICKERS = {" fetch_fx_data.py
grep -n "PAIR_NAMES = {" fetch_fx_data.py
```

预期输出：
- 第 23 行附近：`PAIR_TICKERS = {`
- 第 36 行附近：`PAIR_NAMES = {`

- [ ] **Step 2: 修改 PAIR_TICKERS 添加 HKD**

在 `fetch_fx_data.py` 的 `PAIR_TICKERS` 字典中，在最后一项后添加：

```python
    'HKD': 'HKDCNY=X'
```

**完整 PAIR_TICKERS 应该是：**
```python
PAIR_TICKERS = {
    'EUR': 'EURUSD=X',
    'JPY': 'USDJPY=X',
    'AUD': 'AUDUSD=X',
    'GBP': 'GBPUSD=X',
    'CAD': 'USDCAD=X',
    'NZD': 'NZDUSD=X',
    'HKD': 'HKDCNY=X'
}
```

- [ ] **Step 3: 修改 PAIR_NAMES 添加 HKD**

在 `fetch_fx_data.py` 的 `PAIR_NAMES` 字典中，在最后一项后添加：

```python
    'HKD': 'HKD/CNY'
```

**完整 PAIR_NAMES 应该是：**
```python
PAIR_NAMES = {
    'EUR': 'EUR/USD',
    'JPY': 'USD/JPY',
    'AUD': 'AUD/USD',
    'GBP': 'GBP/USD',
    'CAD': 'USD/CAD',
    'NZD': 'NZD/USD',
    'HKD': 'HKD/CNY'
}
```

- [ ] **Step 4: 验证模块导入**

验证脚本可以正常导入：
```bash
python3 -c "from fetch_fx_data import PAIR_TICKERS, PAIR_NAMES; print('HKD' in PAIR_TICKERS)"
```

**预期输出：**
```
True
```

- [ ] **Step 5: 提交修改**

```bash
git add fetch_fx_data.py
git commit -m "feat: add HKD ticker to Yahoo Finance data fetcher"
```

---

### Task 4: 获取 HKD 数据

**目的：** 从 Yahoo Finance 获取 HKD/CNY 历史数据并验证

**无文件修改**

- [ ] **Step 1: 获取所有货币对数据（包括 HKD）**

运行数据获取脚本：
```bash
python3 fetch_fx_data.py --start-date 2020-01-01 --end-date 2026-03-28 --merge
```

**预期输出：**
```
正在获取 HKD/CNY (HKDCNY=X) 数据...
成功获取 HKD 数据: XXXX 条记录
...
成功获取: 7/7 个货币对
已合并所有数据到 data/raw/FXRate_20260328_yahoo.xlsx
```

- [ ] **Step 2: 验证合并文件包含 HKD 工作表**

```bash
python3 -c "
import pandas as pd
xls = pd.ExcelFile('data/raw/FXRate_20260328_yahoo.xlsx')
print('工作表:', xls.sheet_names)
print('包含 HKD:', 'HKD' in xls.sheet_names)
"
```

**预期输出：**
```
工作表: ['EUR', 'JPY', 'AUD', 'GBP', 'CAD', 'NZD', 'HKD']
包含 HKD: True
```

- [ ] **Step 3: 验证 HKD 数据质量**

```bash
python3 -c "
import pandas as pd
df = pd.read_excel('data/raw/FXRate_20260328_yahoo.xlsx', sheet_name='HKD')
print(f'HKD 数据量: {len(df)}')
print(f'列名: {df.columns.tolist()}')
print(f'日期范围: {df[\"Date\"].min()} 到 {df[\"Date\"].max()}')
print(f'缺失值: {df.isnull().sum().sum()}')
"
```

**预期输出：**
- 数据量 > 100（至少满足最小训练要求）
- 列名包含 Date 和 Close
- 无缺失值或缺失值很少

---

### Task 5: 运行完整流程训练 HKD 模型

**目的：** 训练 HKD 的 3 个周期模型（1天、5天、20天）

**无文件修改**

- [ ] **Step 1: 运行完整流程**

```bash
./run_full_pipeline.sh
```

**预期输出：**
```
开始训练货币对: HKD, 周期: 1d
...
开始训练货币对: HKD, 周期: 5d
...
开始训练货币对: HKD, 周期: 20d
...
成功训练所有模型
```

- [ ] **Step 2: 验证 HKD 模型文件已创建**

```bash
ls -la data/models/HKD_*.pkl
```

**预期输出：**
```
HKD_catboost_1d.pkl
HKD_catboost_5d.pkl
HKD_catboost_20d.pkl
```

- [ ] **Step 3: 验证 HKD 预测文件已创建**

```bash
ls -la data/predictions/HKD_*.json | head -5
```

**预期输出：**
```
HKD_multi_horizon_*.json
```

- [ ] **Step 4: 验证预测文件格式**

```bash
python3 -c "
import json
with open('data/predictions/HKD_multi_horizon_*.json', 'r') as f:
    data = json.load(f)
    print('货币对:', data['metadata']['pair'])
    print('名称:', data['metadata']['pair_name'])
    print('预测周期:', data['metadata']['horizons'])
    print('1天预测:', data['ml_predictions']['1_day']['prediction_text'])
"
```

**预期输出：**
```
货币对: HKD
名称: 港币/人民币
预测周期: [1, 5, 20]
1天预测: 上涨 或 下跌
```

---

### Task 6: 添加 HKD 数据加载测试

**文件：**
- Modify: `tests/test_excel_loader.py`

- [ ] **Step 1: 读取现有测试文件结构**

```bash
grep -n "class FXDataLoaderTest" tests/test_excel_loader.py
grep -n "def test_" tests/test_excel_loader.py | tail -5
```

- [ ] **Step 2: 在 test_excel_loader.py 末尾添加测试函数**

在 `tests/test_excel_loader.py` 文件末尾添加以下测试：

```python
def test_load_hkd_pair_success():
    """测试成功加载 HKD 工作表"""
    loader = FXDataLoader()
    df = loader.load_pair('HKD', 'data/raw/FXRate_20260328_yahoo.xlsx')
    assert len(df) > 0, "HKD 数据量应该大于 0"
    assert 'Date' in df.columns, "应该包含 Date 列"
    assert 'Close' in df.columns, "应该包含 Close 列"

def test_load_hkd_pair_missing_sheet():
    """测试 HKD 工作表不存在时抛出 ValueError"""
    import tempfile
    import os
    
    # 创建一个不含 HKD 工作表的临时文件
    loader = FXDataLoader()
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        # 复制 EUR 工作表到临时文件，不含 HKD
        df_eur = loader.load_pair('EUR', 'data/raw/FXRate_20260328_yahoo.xlsx')
        df_eur.to_excel(tmp.name, sheet_name='EUR', index=False)
        tmp_path = tmp.name
    
    try:
        with pytest.raises(ValueError, match="工作表不存在: HKD"):
            loader.load_pair('HKD', tmp_path)
    finally:
        os.unlink(tmp_path)
```

- [ ] **Step 3: 运行测试验证失败**

```bash
pytest tests/test_excel_loader.py::test_load_hkd_pair_success -v
pytest tests/test_excel_loader.py::test_load_hkd_pair_missing_sheet -v
```

**预期输出：**
```
PASSED test_load_hkd_pair_success
PASSED test_load_hkd_pair_missing_sheet
```

- [ ] **Step 4: 提交测试**

```bash
git add tests/test_excel_loader.py
git commit -m "test: add HKD data loading tests"
```

---

### Task 7: 添加 HKD 端到端集成测试

**文件：**
- Modify: `tests/test_integration.py`

- [ ] **Step 1: 读取现有集成测试**

```bash
grep -n "def test_" tests/test_integration.py | tail -3
```

- [ ] **Step 2: 在 test_integration.py 末尾添加测试函数**

在 `tests/test_integration.py` 文件末尾添加以下测试：

```python
def test_hkd_model_files_exist():
    """测试 HKD 模型文件已创建"""
    model_dir = Path('data/models')
    
    hkd_models = [
        model_dir / 'HKD_catboost_1d.pkl',
        model_dir / 'HKD_catboost_5d.pkl',
        model_dir / 'HKD_catboost_20d.pkl'
    ]
    
    for model_path in hkd_models:
        assert model_path.exists(), f"模型文件应该存在: {model_path}"

def test_hkd_prediction_files_exist():
    """测试 HKD 预测文件已创建"""
    prediction_dir = Path('data/predictions')
    
    # 查找所有 HKD 预测文件
    hkd_predictions = list(prediction_dir.glob('HKD_multi_horizon_*.json'))
    
    assert len(hkd_predictions) > 0, "应该至少有一个 HKD 预测文件"
    
    # 验证预测文件格式
    for pred_file in hkd_predictions:
        with open(pred_file, 'r') as f:
            data = json.load(f)
            assert data['metadata']['pair'] == 'HKD'
            assert data['metadata']['pair_name'] == '港币/人民币'
            assert '1_day' in data['ml_predictions']
            assert '5_day' in data['ml_predictions']
            assert '20_day' in data['ml_predictions']

def test_hkd_configuration():
    """测试 HKD 配置正确"""
    from config import CURRENCY_PAIRS, DATA_CONFIG
    
    assert 'HKD' in CURRENCY_PAIRS
    assert CURRENCY_PAIRS['HKD']['symbol'] == 'HKDCNY'
    assert CURRENCY_PAIRS['HKD']['name'] == '港币/人民币'
    assert 'HKD' in DATA_CONFIG['supported_pairs']
    assert DATA_CONFIG['pair_symbols']['HKD'] == 'HKDCNY'
```

- [ ] **Step 3: 运行测试**

```bash
pytest tests/test_integration.py::test_hkd_model_files_exist -v
pytest tests/test_integration.py::test_hkd_prediction_files_exist -v
pytest tests/test_integration.py::test_hkd_configuration -v
```

**预期输出：**
```
PASSED test_hkd_model_files_exist
PASSED test_hkd_prediction_files_exist
PASSED test_hkd_configuration
```

- [ ] **Step 4: 提交测试**

```bash
git add tests/test_integration.py
git commit -m "test: add HKD integration tests"
```

---

### Task 8: 添加 Dashboard API 测试

**文件：**
- Modify: `dashboard/tests/api/api.test.js`

- [ ] **Step 1: 读取现有 Dashboard 测试**

```bash
grep -n "describe.*pairs" dashboard/tests/api/api.test.js
grep -n "test(" dashboard/tests/api/api.test.js | tail -3
```

- [ ] **Step 2: 在 api.test.js 添加测试**

在 `dashboard/tests/api/api.test.js` 文件中添加以下测试（在现有的 pairs 测试之后）：

```javascript
test('GET /api/v1/pairs includes HKD', async () => {
  const response = await request(app).get('/api/v1/pairs');
  
  expect(response.status).toBe(200);
  expect(Array.isArray(response.body)).toBe(true);
  expect(response.body).toHaveLength(7); // 6 个原有 + HKD
  
  // 验证 HKD 存在
  const hkdPair = response.body.find(p => p.pair === 'HKD');
  expect(hkdPair).toBeDefined();
  expect(hkdPair.pair_name).toBe('港币/人民币');
});

test('GET /api/v1/pairs/HKD returns HKD details', async () => {
  const response = await request(app).get('/api/v1/pairs/HKD');
  
  expect(response.status).toBe(200);
  expect(response.body.metadata.pair).toBe('HKD');
  expect(response.body.metadata.pair_name).toBe('港币/人民币');
  expect(response.body.metadata.current_price).toBeDefined();
  expect(response.body.ml_predictions).toBeDefined();
  expect(response.body.ml_predictions['1_day']).toBeDefined();
  expect(response.body.ml_predictions['5_day']).toBeDefined();
  expect(response.body.ml_predictions['20_day']).toBeDefined();
});

test('GET /api/v1/strategies includes HKD', async () => {
  const response = await request(app).get('/api/v1/strategies');
  
  expect(response.status).toBe(200);
  expect(Array.isArray(response.body)).toBe(true);
  
  // 每个货币对应该有 3 个周期的策略
  response.body.forEach(strategy => {
    expect(strategy).toHaveProperty('pair');
    expect(strategy).toHaveProperty('short_term');
    expect(strategy).toHaveProperty('medium_term');
    expect(strategy).toHaveProperty('long_term');
  });
  
  // 验证 HKD 存在
  const hkdStrategy = response.body.find(s => s.pair === 'HKD');
  expect(hkdStrategy).toBeDefined();
});
```

- [ ] **Step 3: 运行 Dashboard 测试**

```bash
cd dashboard
npm test -- api.test.js
```

**预期输出：**
```
PASS  tests/api/api.test.js
  ✓ GET /api/v1/pairs includes HKD
  ✓ GET /api/v1/pairs/HKD returns HKD details
  ✓ GET /api/v1/strategies includes HKD
```

- [ ] **Step 4: 提交测试**

```bash
cd ..
git add dashboard/tests/api/api.test.js
git commit -m "test: add HKD Dashboard API tests"
```

---

### Task 9: 运行所有测试验证无回归

**目的：** 确保所有现有测试仍然通过，没有引入回归

**无文件修改**

- [ ] **Step 1: 运行所有 Python 测试**

```bash
pytest tests/ -v --tb=short
```

**预期输出：**
- 所有测试通过
- 至少有 118 个测试（115 个原有 + 3 个新增 HKD 测试）
- 无 FAIL 或 ERROR

- [ ] **Step 2: 运行 Dashboard 测试**

```bash
cd dashboard
npm test
```

**预期输出：**
- 所有测试通过
- 新增 3 个 HKD API 测试通过

- [ ] **Step 3: 检查测试覆盖率**

```bash
pytest tests/ --cov=. --cov-report=term --cov-report=html
```

**预期输出：**
- 覆盖率保持 >= 77%（当前基准）
- HTML 报告生成在 `htmlcov/index.html`

---

### Task 10: 启动 Dashboard 验证 HKD 显示

**目的：** 手动验证 Dashboard 正确显示 HKD/CNY 货币对

**无文件修改**

- [ ] **Step 1: 启动 Dashboard**

```bash
cd dashboard
npm start
```

**预期输出：**
```
Server running on http://localhost:3000
API endpoints:
  GET  /health
  GET  /api/v1/pairs
  GET  /api/v1/pairs/:pair
  ...
```

- [ ] **Step 2: 访问 Dashboard 并验证（手动）**

在浏览器中打开 `http://localhost:3000`，验证：

1. **货币对概览卡片**：
   - 应该看到 7 个卡片（EUR, JPY, AUD, GBP, CAD, NZD, HKD）
   - HKD 卡片显示"港币/人民币"
   - 显示当前价格、预测方向、概率、置信度
   - 显示简短分析摘要

2. **交易策略表格**：
   - 表格应该包含 HKD 行
   - 显示 HKD 的 1 天、5 天、20 天策略
   - 包含入场价、止损、止盈、建议、置信度

3. **点击 HKD 卡片**：
   - 侧边栏显示 HKD 完整分析
   - 显示基本信息、分析摘要、关键因素
   - 显示各周期详细分析（短线/中线/长线）

- [ ] **Step 3: 停止 Dashboard**

按 `Ctrl+C` 停止 Dashboard 服务

---

### Task 11: 测试数据缺失场景

**目的：** 验证当上传的文件缺少 HKD 工作表时，系统优雅降级

**无文件修改**

- [ ] **Step 1: 创建测试用的不完整数据文件**

```bash
python3 -c "
import pandas as pd

# 读取完整文件
xls = pd.ExcelFile('data/raw/FXRate_20260328_yahoo.xlsx')

# 创建一个新文件，只包含 EUR（不含 HKD）
with pd.ExcelWriter('data/raw/test_no_hkd.xlsx', engine='openpyxl') as writer:
    df_eur = pd.read_excel(xls, 'EUR')
    df_eur.to_excel(writer, sheet_name='EUR', index=False)

print('已创建测试文件: data/raw/test_no_hkd.xlsx')
print('工作表:', pd.ExcelFile('data/raw/test_no_hkd.xlsx').sheet_names)
"
```

- [ ] **Step 2: 测试加载不完整文件**

```bash
python3 -c "
from data_services.excel_loader import FXDataLoader

loader = FXDataLoader()
result = loader.load_all_pairs('data/raw/test_no_hkd.xlsx')

print('成功加载的货币对:', list(result.keys()))
print('HKD 在结果中:', 'HKD' in result)
"
```

**预期输出：**
```
WARNING - 加载货币对 HKD 失败: 工作表不存在: HKD
成功加载的货币对: ['EUR']
HKD 在结果中: False
```

- [ ] **Step 3: 清理测试文件**

```bash
rm data/raw/test_no_hkd.xlsx
```

---

### Task 12: 更新文档和提交所有更改

**文件：**
- Modify: `README.md` (可选，如果需要更新货币对列表)

- [ ] **Step 1: 检查 README 是否需要更新**

```bash
grep -n "支持的货币对" README.md
grep -n "EUR/USD" README.md
```

如果 README 中列出了支持的货币对，需要添加 HKD/CNY。

- [ ] **Step 2: 更新 README（如果需要）**

找到"支持的货币对"部分，添加：

```markdown
- **HKD/USD**（港币/人民币）
```

- [ ] **Step 3: 更新 AGENTS.md（如果需要）**

在 AGENTS.md 的"支持的货币对"部分添加：

```markdown
- **HKD/USD**（港币/人民币）
```

- [ ] **Step 4: 更新 progress.txt**

```bash
echo "$(date '+%Y-%m-%d') - 添加 HKD/CNY 货币对支持" >> progress.txt
```

- [ ] **Step 5: 查看所有未提交的更改**

```bash
git status
```

- [ ] **Step 6: 提交文档更新（如果有）**

```bash
git add README.md AGENTS.md progress.txt
git commit -m "docs: update documentation for HKD/CNY pair support"
```

- [ ] **Step 7: 查看最终提交历史**

```bash
git log --oneline -10
```

**预期提交列表：**
1. feat: add HKD/CNY pair configuration
2. feat: add HKD ticker to Yahoo Finance data fetcher
3. test: add HKD data loading tests
4. test: add HKD integration tests
5. test: add HKD Dashboard API tests
6. docs: update documentation for HKD/CNY pair support (如果修改了文档)

---

## 验收标准

完成后，验证以下标准：

- ✅ `config.py` 包含 HKD 配置
- ✅ `fetch_fx_data.py` 包含 HKD ticker
- ✅ Yahoo Finance 可以获取 HKD/CNY 数据
- ✅ `data/models/` 包含 3 个 HKD 模型文件（1d/5d/20d）
- ✅ `data/predictions/` 包含 HKD 预测文件
- ✅ Dashboard 正常显示 HKD/CNY 卡片和策略
- ✅ 所有测试通过（无回归）
- ✅ 数据缺失时系统优雅降级（警告 + 跳过）

---

## 故障排除

### 问题 1: Yahoo Finance ticker 不可用

**症状：** Task 1 验证失败，yfinance 返回空数据

**解决方案：**
- 检查 ticker 是否正确：`HKDCNY=X`
- 尝试不同的日期范围
- 联系用户确认是否需要使用其他数据源

### 问题 2: 模型训练失败

**症状：** Task 5 训练时报错

**解决方案：**
- 检查数据量是否充足（>= 100 条）
- 查看详细错误日志
- 检查是否有缺失值

### 问题 3: Dashboard 不显示 HKD

**症状：** Task 10 中 Dashboard 没有显示 HKD 卡片

**解决方案：**
- 确认预测文件已生成（Task 5）
- 重启 Dashboard 服务器
- 检查浏览器控制台是否有错误

### 问题 4: 测试失败

**症状：** Task 9 中有测试失败

**解决方案：**
- 运行单个测试查看详细错误：`pytest tests/test_xxx.py::test_name -v`
- 检查代码是否正确实现
- 查看测试输出中的错误信息

---

## 总结

本实施计划采用 TDD 方法，分 12 个任务逐步实现 HKD/CNY 货币对支持：

1. 验证 Yahoo Finance ticker 可用性
2. 修改配置文件（config.py, fetch_fx_data.py）
3. 获取并验证数据
4. 训练模型并生成预测
5. 添加单元测试
6. 添加集成测试
7. 添加 Dashboard 测试
8. 运行完整测试套件
9. 手动验证 Dashboard
10. 测试数据缺失场景
11. 更新文档

每个任务都包含明确的验证步骤和预期输出，确保实现质量。