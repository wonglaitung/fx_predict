# FX Predict - 外汇智能分析系统

## 项目概述

本项目是一个基于机器学习和人机协作的多周期外汇汇率预测系统，包含：

- **多周期预测系统**：同时预测 1天、5天、20天三个周期的汇率走势，支持多货币对独立建模
- **双重验证分析系统**：以大模型为核心决策者，整合 35 个技术指标和 ML 预测结果，生成专业自然语言分析报告
- **技术指标引擎**：计算 35 个专业技术指标（趋势、动量、波动、价格形态、市场环境），全部使用滞后数据防止数据泄漏
- **CatBoost 预测模型**：多周期 CatBoost 模型，每个货币对每个周期独立建模
- **大模型集成**：通义千问 API，提供技术面深度分析、ML 预测验证、风险分析和交易建议
- **交易方案生成器**：自动计算入场价、止损止盈（基于 ATR）、风险回报比
- **Web Dashboard**：Node.js + Express 实时可视化仪表盘，支持大模型分析展示
- **文件上传功能**：支持通过 Dashboard 上传 Excel 数据文件
- **Docker 部署**：提供完整的 Docker 部署方案，支持容器化运行
- **一体化脚本**：`run_full_pipeline.sh` 脚本实现训练、预测、分析全流程自动化

## 快速开始

### 安装依赖

**Python 依赖：**
```bash
pip install -r requirements.txt
```

**Dashboard 依赖（可选）：**
```bash
cd dashboard
npm install
```

### 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的通义千问 API 密钥：

```bash
cp .env.example .env
# 编辑 .env 文件，填入 QWEN_API_KEY
```

### 配置数据文件

系统支持三种方式配置数据文件路径，优先级从高到低：

**数据文件位置**：默认存放在 `data/raw/` 目录下

**1. 命令行参数（最高优先级）**

```bash
# 使用指定的数据文件（支持相对路径或仅文件名）
./run_full_pipeline.sh --data-file data/raw/FXRate_20260320.xlsx
./run_full_pipeline.sh --data-file FXRate_20260320.xlsx  # 系统会在 data/raw/ 查找

# Python 模块
python3 -m ml_services.fx_trading_model --mode train --pair EUR --data-file data/raw/FXRate_20260320.xlsx
python3 -m comprehensive_analysis --data-file FXRate_20260320.xlsx
```

**2. 环境变量（中等优先级）**

在 `.env` 文件中配置：

```bash
# 编辑 .env 文件，添加数据文件路径
DATA_FILE=data/raw/FXRate_20260320.xlsx
```

**3. 配置文件（最低优先级）**

在 `config.py` 中修改默认值：

```python
DATA_CONFIG = {
    'data_file': 'data/raw/FXRate_20260320.xlsx',  # 修改这里
    # ...
}
```

**使用建议：**
- 更新数据时，推荐使用命令行参数 `--data-file`，无需修改代码
- 如果经常使用同一个数据文件，可以在 `.env` 文件中配置
- 修改 `config.py` 中的默认值仅用于永久性更改
- 数据文件也可以通过 Dashboard 的 `/api/v1/upload` 接口上传，会自动保存到 `data/raw/` 目录

## Docker 部署（可选）

系统提供完整的 Docker 部署方案，支持容器化运行。

### 前置要求

- Docker 20.10 或更高版本
- 确保 `.env` 文件已配置好 `QWEN_API_KEY`

### 快速开始

**方式一：使用 docker-deploy.sh 脚本（推荐）**

```bash
# 进入 Docker 目录
cd dashboard/docker

# 构建 Docker 镜像
./docker-deploy.sh build

# 启动容器（后台运行）
./docker-deploy.sh up

# 查看日志
./docker-deploy.sh logs

# 访问 Dashboard
# http://localhost:3000
```

**方式二：使用 docker-compose**

```bash
# 进入 Docker 目录
cd dashboard/docker

# 构建并启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 访问 Dashboard
# http://localhost:3000
```

### Docker 功能特性

- **Dashboard 服务**：提供 Web 界面，实时显示外汇预测和分析结果
- **定时任务**：每小时自动执行 `run_full_pipeline.sh`，更新预测数据
- **配置管理**：通过 Volume 挂载 `.env` 文件，宿主机更新自动生效
- **数据持久化**：数据、模型、日志通过 Volume 挂载，容器删除不丢失

### Docker 常用命令

```bash
# 停止容器
./docker-deploy.sh down

# 重启容器
./docker-deploy.sh restart

# 查看容器状态
./docker-deploy.sh ps

# 查看详细状态
./docker-deploy.sh status

# 进入容器执行命令
./docker-deploy.sh exec bash

# 清理未使用的资源
./docker-deploy.sh clean
```

### 详细文档

完整的 Docker 部署文档请参考：`dashboard/docker/DOCKER.md`

### 一键运行完整流程（推荐）

```bash
# 运行完整流程（训练 + 预测 + 分析）
./run_full_pipeline.sh

# 跳过训练，只进行预测和分析（模型已存在时）
./run_full_pipeline.sh --skip-training

# 禁用大模型分析
./run_full_pipeline.sh --no-llm
```

### 启动 Dashboard（可选）

```bash
cd dashboard
npm start

# 访问 http://localhost:3000
```

Dashboard 功能：
- 实时显示货币对概览卡片（价格、预测、概率、置信度、分析摘要）
- 交易策略表格（各周期入场价、止损、止盈、建议、置信度）
- 技术指标图表（价格走势 + 均线、技术指标数值）
- 风险提示面板
- 点击卡片查看完整大模型分析（侧边栏详情）

### 单独运行各模块

```bash
# 训练单个货币对的所有周期模型
python3 -m ml_services.fx_trading_model --mode train --pair EUR

# 生成单个货币对的多周期预测
python3 -m ml_services.fx_trading_model --mode predict --pair EUR

# 综合分析（启用大模型）
python3 -m comprehensive_analysis --pair EUR

# 综合分析（禁用大模型）
python3 -m comprehensive_analysis --pair EUR --no-llm
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行集成测试
pytest tests/test_integration.py -v

# 运行测试并检查覆盖率
pytest tests/ --cov=. --cov-report=html --cov-report=term

# 查看覆盖率 HTML 报告
# 报告位置：htmlcov/index.html
```

### 运行 Dashboard 测试

```bash
cd dashboard
npm test
```

## Session Workflow

- **会话开始时必须执行以下操作：**
  - 读取 `progress.txt` 文件，了解项目当前进展
  - 审查 `lessons.md` 文件，检查是否有错误需要纠正
- **功能更新后：**
  - 更新 `progress.txt`，记录新的进展
  - 如有新的学习心得或经验教训，更新 `lessons.md`

## 项目结构

```
fx_predict/
├── run_full_pipeline.sh          # 一体化脚本（推荐）
├── data/                           # 数据目录
│   ├── raw/                       # 原始数据文件（Excel）
│   │   └── FXRate_20260320.xlsx   # 示例数据文件
│   ├── models/                    # 训练好的模型（CatBoost，18个模型）
│   │   ├── EUR_catboost_1d.pkl
│   │   ├── EUR_catboost_5d.pkl
│   │   ├── EUR_catboost_20d.pkl
│   │   ├── JPY_catboost_1d.pkl
│   │   └── ...（6货币对 × 3周期）
│   └── predictions/               # 预测结果（JSON格式）
│       ├── EUR_multi_horizon_*.json
│       ├── JPY_multi_horizon_*.json
│       └── ...
├── dashboard/                      # Web Dashboard（Node.js）
│   ├── server.js                  # Express API 服务器
│   ├── package.json               # Node.js 依赖
│   ├── public/                    # 前端资源
│   │   ├── index.html
│   │   ├── css/
│   │   └── js/
│   ├── docker/                    # Docker 部署文件
│   │   ├── Dockerfile             # Docker 镜像定义
│   │   ├── docker-compose.yml     # Docker Compose 配置
│   │   ├── docker-deploy.sh       # Docker 部署脚本
│   │   ├── docker-entrypoint.sh   # 容器启动脚本
│   │   ├── .dockerignore          # Docker 忽略文件
│   │   └── DOCKER.md              # Docker 部署文档
│   └── tests/                     # Dashboard 测试
├── data_services/                 # 数据服务层
│   ├── excel_loader.py           # Excel 数据加载器
│   └── technical_analysis.py     # 技术指标引擎（35个指标）
├── ml_services/                   # 机器学习服务层
│   ├── fx_trading_model.py       # CatBoost 模型（多周期）
│   ├── feature_engineering.py    # 特征工程（18个特征）
│   ├── base_model_processor.py   # 模型处理器
│   ├── multi_horizon_context.py  # 多周期上下文构建器
│   ├── multi_horizon_prompt.py   # LLM Prompt 构建器
│   ├── llm_parser.py             # LLM 输出解析器
│   ├── strategy_generator.py     # 交易方案生成器
│   └── json_formatter.py         # JSON 格式化器
├── llm_services/                  # 大模型服务层
│   └── qwen_engine.py            # 通义千问 API 封装
├── comprehensive_analysis.py      # 人机协作整合层（多周期）
├── config.py                      # 配置文件
├── requirements.txt               # Python 依赖
└── tests/                         # 测试文件（115个测试用例）
    ├── test_integration.py       # 集成测试
    ├── test_comprehensive_analysis.py
    ├── test_excel_loader.py
    ├── test_feature_engineering.py
    ├── test_fx_trading_model.py
    ├── test_technical_analysis.py
    ├── test_multi_horizon_context.py
    ├── test_multi_horizon_prompt.py
    ├── test_llm_parser.py
    ├── test_strategy_generator.py
    └── test_json_formatter.py
```

## 支持的货币对

- **EUR/USD**（欧元/美元）
- **USD/JPY**（美元/日元）
- **AUD/USD**（澳元/美元）
- **GBP/USD**（英镑/美元）
- **USD/CAD**（美元/加元）
- **NZD/USD**（新西兰元/美元）

**注意**：货币对代码使用基准货币（如 EUR、JPY 等）作为键名。

## 预测周期

系统支持三个预测周期：

- **短线（1天）**：预测 1 天后的汇率走势
- **中线（5天）**：预测 5 天后的汇率走势
- **长线（20天）**：预测 20 天后的汇率走势

每个货币对、每个周期都有独立的 CatBoost 模型。

## 技术指标（35个）

系统计算以下技术指标，所有指标均使用滞后数据（`.shift(1)`）防止数据泄漏：

### 趋势类指标（17个）

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
| Williams_R_14 | 威廉指标（14日，范围 -100 到 0） |
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

### 市场环境指标（1个）

| 指标 | 说明 |
|------|------|
| MA_Alignment | 均线排列强度（多头/空头排列） |

### 交叉特征（3个）

| 指标 | 说明 |
|------|------|
| SMA5_cross_SMA20 | 均线交叉信号（金叉/死叉） |
| Price_vs_Bollinger | 价格在布林带中的位置 |
| Price_vs_MA120 | 价格相对于120日均线的位置 |

## 多周期分析流程

系统采用**多周期双重验证分析机制**，同时预测 1天、5天、20天三个周期，以大模型为核心决策者，整合完整的技术指标数据和ML预测结果，生成自然语言格式的市场分析报告和交易建议。

### 工作流程

```
数据加载 → 技术指标计算（35个） → ML 多周期预测（1d/5d/20d）
                                              ↓
            多周期上下文构建 → 一致性分析 → LLM 分析
                                              ↓
              交易方案生成 → JSON 格式化输出
```

### 分析流程

1. **数据准备**：为每个周期计算技术指标和ML预测
2. **上下文构建**：整合35个技术指标、3个ML预测结果、当前价格等信息
3. **一致性分析**：
   - 评估各周期预测方向的一致性
   - 计算技术指标支持度
   - 生成整体一致性评分
4. **大模型分析**：
   - 技术面深度分析（趋势、支撑阻力、反转信号）
   - ML预测验证（一致性评估、可靠性判断）
   - 风险分析（风险因素、止损建议）
   - 交易建议（明确方向、入场/止损/止盈价格、仓位管理）
5. **交易方案生成**：
   - 基于ATR计算止损止盈
   - 风险回报比确保 1:1
   - 自动调整仓位大小
6. **JSON输出**：标准化格式输出所有分析结果

### 分析报告内容

每个货币对的分析输出包括：

- **元数据**：货币对代码、名称、当前价格、数据日期、分析日期
- **ML 预测**：3个周期的预测结果（方向、概率、置信度、目标日期）
- **一致性分析**：
  - 整体一致性评分（0.0-1.0）
  - 各周期一致性分数（基于预测概率 × 70% + 技术指标支持度 × 30%）
  - 技术指标摘要
- **LLM 分析**：
  - 整体评估（谨慎乐观、中性、谨慎悲观等）
  - 分析摘要（详细技术面分析）
  - 关键因素（3-5个核心因素）
  - 各周期分析（详细分析、建议、关键点）
- **交易策略**：
  - 短线策略（1天）：入场价、止损、止盈、风险回报比、仓位
  - 中线策略（5天）：入场价、止损、止盈、风险回报比、仓位
  - 长线策略（20天）：入场价、止损、止盈、风险回报比、仓位
- **技术指标**：完整的35个指标数值（按类别组织）
- **风险分析**：风险等级、风险因素、警告信息

### 决策优先级

系统优先使用**LLM建议**作为最终决策，ML预测作为验证参考。当LLM不可用时，降级到基于ML预测的规则引擎。

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
   - 交叉特征：`SMA5_cross_SMA20 = cross_signal.shift(1)`

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

### 3. 交易方案约束

- **止损止盈**：基于 ATR 计算，周期越长空间越大
  - 1天：1.1倍 ATR
  - 5天：1.5倍 ATR
  - 20天：3.0倍 ATR
- **风险回报比**：固定 1:1
- **仓位管理**：根据置信度自动调整
  - 高置信度：large（大仓位）
  - 中置信度：medium（中等仓位）
  - 低置信度：small（小仓位）
  - 未知置信度：none（不交易）

## Web Dashboard

### 启动 Dashboard

```bash
cd dashboard
npm start
```

访问 `http://localhost:3000` 查看 Dashboard。

### Dashboard 功能

1. **货币对概览卡片**：
   - 显示当前价格、预测方向、概率、置信度
   - 显示简短分析摘要（最多50字）
   - 点击卡片查看完整分析详情

2. **交易策略表格**：
   - 显示所有货币对的各周期策略
   - 包含入场价、止损、止盈、建议、置信度
   - 止损止盈基于ATR计算，风险回报比1:1

3. **技术指标图表**：
   - 价格走势图 + 均线（SMA5/SMA10/SMA20）
   - 技术指标数值图（RSI14/MACD/ATR14）

4. **风险提示面板**：
   - 显示各货币对的风险因素和警告

5. **大模型分析侧边栏**：
   - 点击货币对卡片打开
   - 显示基本信息、分析摘要、关键因素
   - 显示各周期详细分析（短线/中线/长线）
   - 包含置信度、建议、关键点

### Dashboard API

**注意**：服务器启动时会自动打印所有 API 端点信息，包括方法、路径、描述、参数和响应格式。

- `GET /health` - 健康检查
  - 描述：检查服务是否正常运行
  - 参数：无
  - 响应：`{ "status": "ok", "timestamp": "..." }`

- `GET /api/v1/pairs` - 获取所有货币对信息
  - 描述：获取所有货币对的基本信息和预测结果
  - 参数：无
  - 响应：货币对数组，包含价格、预测、置信度、LLM 分析等

- `GET /api/v1/pairs/:pair` - 获取单个货币对详细信息
  - 描述：获取指定货币对的详细信息
  - 参数：pair（货币对代码，如 EUR）
  - 响应：单个货币对的完整信息

- `GET /api/v1/strategies` - 获取交易策略

  - 描述：获取所有货币对的交易策略

  - 参数：无

  - 响应：包含入场价、止损、止盈、建议、置信度等



- `GET /api/v1/indicators/:pair` - 获取技术指标

  - 描述：获取指定货币对的技术指标数值

  - 参数：pair（货币对代码）

  - 响应：包含所有 35 个技术指标的数值

- `GET /api/v1/strategies/:pair/:horizon/indicators` - 获取策略关键指标
  - 描述：获取指定货币对和周期的关键技术指标（6个类别）
  - 参数：pair（货币对代码），horizon（周期，1/5/20）
  - 响应：包含支撑阻力、趋势强度、动量、波动性、关键均线、交易信号等
  - 缓存：TTL 5分钟，key 格式 `strategy_indicators:{pair}:{horizon}`

- `GET /api/v1/risk` - 获取风险分析

  - 描述：获取所有货币对的风险分析

  - 参数：无

  - 响应：包含风险等级、风险因素、警告信息等



- `POST /api/v1/upload` - 上传数据文件

  - 描述：上传 Excel 数据文件到服务器

  - 参数：file（表单数据，文件对象）

  - 文件格式：.xlsx

  - 文件大小限制：10MB

  - 响应：上传成功消息

  - 示例：

    ```bash

    curl -X POST http://localhost:3000/api/v1/upload \

      -F "file=@FXRate_20260327.xlsx"

    ```

  - 文件会自动保存到 `data/raw/` 目录，服务器缓存会被清除

## 测试覆盖率

### 覆盖率目标

- **总体覆盖率**：≥ 85%（当前：77%）
- **核心模块覆盖率**：≥ 70%
  - comprehensive_analysis.py: 92% ✅
  - ml_services/fx_trading_model.py: 91% ✅
  - data_services/excel_loader.py: 83% ✅
  - data_services/technical_analysis.py: 78% ✅ ✅
  - ml_services/base_model_processor.py: 74% ✅
  - **新模块覆盖率**：
    - multi_horizon_context.py: 100% ✅
    - multi_horizon_prompt.py: 98% ✅
    - llm_parser.py: 98% ✅
    - strategy_generator.py: 100% ✅
    - json_formatter.py: 99% ✅

### 测试统计

- **总测试数**：115 个
- **单元测试**：106 个
  - test_comprehensive_analysis.py: 4 个
  - test_excel_loader.py: 7 个
  - test_feature_engineering.py: 35 个
  - test_fx_trading_model.py: 6 个
  - test_technical_analysis.py: 42 个
  - test_multi_horizon_context.py: 6 个
  - test_multi_horizon_prompt.py: 4 个
  - test_llm_parser.py: 5 个
  - test_strategy_generator.py: 4 个
  - test_json_formatter.py: 8 个
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
- **文件输出**：`qwen_engine.log`（大模型调用日志）

## 特征工程

### 特征类别（18个特征）

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

7. **交叉特征**（2个）：
   - SMA5_cross_SMA20：均线交叉信号（金叉/死叉）
   - Price_vs_Bollinger：价格在布林带中的位置

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

- **支持周期**：1天、5天、20天
- **默认周期**：所有周期（多周期分析）
- **独立建模**：每个货币对、每个周期独立模型

### 数据分割

- **训练集**：80%
- **验证集**：20%
- **分割方式**：时间序列分割（不混洗）

### 模型数量

- **总模型数**：18 个（6个货币对 × 3个周期）
- **模型命名**：`{pair}_catboost_{horizon}d.pkl`
  - 示例：`EUR_catboost_1d.pkl`, `JPY_catboost_20d.pkl`

## JSON 输出格式

系统输出标准 JSON 格式，包含以下必需部分：

```json
{
  "metadata": {
    "pair": "EUR",
    "pair_name": "欧元/美元",
    "current_price": 1.1570,
    "data_date": "2026-03-20",
    "analysis_date": "2026-03-26",
    "horizons": [1, 5, 20]
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
    "5_day": {...},
    "20_day": {...}
  },
  "consistency_analysis": {
    "score": 1.0,
    "interpretation": "完全一致",
    "all_same": true,
    "majority_trend": "上涨",
    "scores_by_horizon": {
      "1d": 0.4942,
      "5d": 0.7505,
      "20d": 0.5112,
      "overall": 0.5853
    },
    "technical_support": 0.45,
    "technical_indicators_summary": [...]
  },
  "llm_analysis": {
    "summary": "...",
    "overall_assessment": "谨慎乐观",
    "key_factors": [...],
    "horizon_analysis": {
      "1": {...},
      "5": {...},
      "20": {...}
    }
  },
  "trading_strategies": {
    "short_term": {...},
    "medium_term": {...},
    "long_term": {...}
  },
  "technical_indicators": {
    "trend": {...},
    "momentum": {...},
    "volatility": {...},
    "volume": {...},
    "price_pattern": {...},
    "market_environment": {...}
  },
  "risk_analysis": {
    "overall_risk": "medium",
    "risk_factors": [...],
    "warnings": [...]
  }
}
```

## 常见问题

### 1. 如何更新数据文件

**问题**：数据文件过期了，如何使用新的数据文件？

**解决方案**：

**数据文件位置**：默认存放在 `data/raw/` 目录下

方式1：使用命令行参数（推荐）
```bash
# 运行完整流程，指定新的数据文件（支持相对路径或仅文件名）
./run_full_pipeline.sh --data-file data/raw/FXRate_20260326.xlsx
./run_full_pipeline.sh --data-file FXRate_20260326.xlsx  # 系统会在 data/raw/ 查找

# 单独运行模块
python3 -m ml_services.fx_trading_model --mode train --pair EUR --data-file data/raw/FXRate_20260326.xlsx
python3 -m comprehensive_analysis --data-file FXRate_20260326.xlsx
```

方式2：在 .env 文件中配置
```bash
# 编辑 .env 文件
DATA_FILE=data/raw/FXRate_20260326.xlsx
```

方式3：修改 config.py 中的默认值
```python
DATA_CONFIG = {
    'data_file': 'data/raw/FXRate_20260326.xlsx',  # 修改这里
    # ...
}
```

方式4：通过 Dashboard 上传（推荐用于 Web 界面用户）
```bash
# 启动 Dashboard
cd dashboard && npm start

# 使用 API 上传文件
curl -X POST http://localhost:3000/api/v1/upload \
  -F "file=@FXRate_20260326.xlsx"
```
文件会自动保存到 `data/raw/` 目录

**优先级**：命令行参数 > 环境变量 > 配置文件默认值

### 2. 数据文件格式

Excel 文件必须满足：
- 工作表名称为货币对代码（如 EUR、JPY）
- 包含 `Date` 和 `Close` 列
- 可选：`High`、`Low`、`Open` 列（系统会自动生成）
- 日期格式：MM/DD/YYYY

**文件位置**：将 Excel 文件放置在 `data/raw/` 目录下（如 `data/raw/FXRate_20260326.xlsx`）

### 3. 模型训练失败

可能原因：
- 数据点不足（至少需要 100 条）
- 缺少必要的列
- 数据格式错误

解决方案：
- 检查数据文件格式
- 确保数据量充足
- 查看日志输出

### 4. 测试失败

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

### 5. 大模型不可用

如果未配置 `QWEN_API_KEY`，大模型功能将不可用。系统会自动降级到基于 ML 预测的规则引擎，不影响核心功能（ML 预测和技术分析）。

### 6. Python 模块导入错误

运行脚本时遇到 `ModuleNotFoundError`，请确保使用 `-m` 参数：

```bash
# 错误方式
python3 ml_services/fx_trading_model.py

# 正确方式
python3 -m ml_services.fx_trading_model
```

### 7. Dashboard 无法启动

可能原因：
- Node.js 未安装
- 依赖未安装

解决方案：
```bash
cd dashboard
npm install
npm start
```

### 8. Dashboard 显示"暂无分析"

可能原因：
- 数据未生成：运行 `./run_full_pipeline.sh` 生成预测数据
- 服务器缓存：重启 Dashboard 服务器
- 浏览器缓存：硬刷新页面（Ctrl+Shift+R）

### 9. 止损止盈距离看起来不一致

**问题**：为什么有时止损大、止盈小？

**解答**：
- 对于 sell 策略：止损在入场价之上，止盈在入场价之下
- 对于 buy 策略：止损在入场价之下，止盈在入场价之上
- **实际距离完全相等**：风险回报比始终为 1:1
- 20天周期距离更大：因为周期越长，需要更大的止损止盈空间
- 基于 ATR 计算：ATR 乘数随周期增加（1天：1.1倍，5天：1.5倍，20天：3.0倍）

示例：
- JPY 20天 sell：入场 158.36，止损 167.86（+9.50），止盈 148.86（-9.50），距离完全相等

### 10. 如何使用 Docker 部署

**问题**：如何使用 Docker 部署项目？

**解决方案**：

```bash
# 进入 Docker 目录
cd dashboard/docker

# 使用 docker-deploy.sh 脚本（推荐）
./docker-deploy.sh build
./docker-deploy.sh up

# 或使用 docker-compose
docker-compose build
docker-compose up -d

# 访问 Dashboard
# http://localhost:3000
```

详细文档请参考：`dashboard/docker/DOCKER.md`

### 11. Docker 容器无法启动

**问题**：Docker 容器启动失败。

**可能原因**：
- .env 文件未配置或不正确
- 端口 3000 已被占用
- 数据文件不存在

**解决方案**：
```bash
# 检查 .env 文件
ls -la ../.env

# 检查端口占用
netstat -tulpn | grep 3000

# 检查数据文件
ls -la ../data/raw/FXRate_20260320.xlsx

# 查看容器日志
docker-compose logs fx-predict
# 或
./docker-deploy.sh logs
```

### 12. 如何查看 Docker 容器中的定时任务日志

**问题**：如何查看定时任务是否正常执行？

**解决方案**：
```bash
# 进入 Docker 目录
cd dashboard/docker

# 查看 pipeline 执行日志
docker-compose exec fx-predict cat /app/logs/pipeline.log

# 查看 cron 守护进程日志
docker-compose exec fx-predict cat /app/logs/cron.log

# 或使用 docker-deploy.sh
./docker-deploy.sh exec bash
# 在容器内查看日志
cat /app/logs/pipeline.log
cat /app/logs/cron.log
```

## 开发者

- **创建时间**：2026-03-25
- **版本**：4.0（多周期 + Dashboard + Docker）
- **Python 版本**：3.10+
- **Node.js 版本**：18+
- **Docker 版本**：20.10+
- **Python 框架**：CatBoost, Pandas, NumPy, Scikit-learn
- **Web 框架**：Express
- **前端技术**：HTML5, CSS3, JavaScript, Chart.js
- **测试框架**：pytest, Jest
- **容器化**：Docker, Docker Compose（可选）

## 许可证

本项目仅供学习和研究使用。