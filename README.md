# FX Predict - 外汇智能分析系统

基于机器学习和人机协作的多周期外汇汇率预测系统，整合技术指标分析、CatBoost 预测模型和大模型解释，为外汇交易提供智能化建议。

## 功能特性

### 核心功能

- **多周期预测系统**：同时预测 1天、5天、20天三个周期的汇率走势，支持多货币对独立建模
- **双重验证分析系统**：以大模型为核心决策者，整合 35 个技术指标和 ML 预测结果，生成专业自然语言分析报告
- **技术指标引擎**：计算 35 个专业技术指标（趋势、动量、波动、价格形态、市场环境），全部使用滞后数据防止数据泄漏
- **CatBoost 预测模型**：多周期 CatBoost 模型，每个货币对每个周期独立建模
- **大模型集成**：通义千问 API，提供技术面深度分析、ML 预测验证、风险分析和交易建议
- **交易方案生成器**：自动计算入场价、止损止盈（基于 ATR）、风险回报比
- **Yahoo Finance 数据集成**：自动获取 6 年历史外汇数据（1622 条记录/货币对），支持定时更新
- **Web Dashboard**：Node.js + Express 实时可视化仪表盘，支持大模型分析展示、策略指标详情、自动刷新
- **文件上传功能**：支持通过 Dashboard 上传 Excel 数据文件
- **Docker 部署**：提供完整的 Docker 部署方案，支持容器化运行和定时任务

### 安全保障

- **风险控制**：硬性约束（概率阈值≤0.50禁止买入、≥0.60高概率推荐）、止损止盈机制（基于 ATR）
- **数据泄漏防范**：所有指标使用滞后数据，确保预测有效性
- **置信度分级**：高（≥0.60）、中（0.50-0.60）、低（<0.50）三级置信度评估

## 界面展示

系统提供 Web Dashboard 可视化界面，实时展示货币对概览、交易策略、技术指标和风险分析。

### 主界面

![Dashboard主界面](resources/dashboard_1.jpg)

Dashboard 主界面展示所有货币对的实时汇率、预测方向和置信度。点击任意货币对卡片可查看详细的大模型分析报告。

### 技术指标与交易策略

![技术指标与交易策略](resources/dashboard_2.jpg)

技术指标图表展示价格走势、均线系统和技术指标数值。交易策略表格提供各周期的入场价、止损、止盈建议。

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

## 快速开始

### 使用方法对比

| 使用场景 | 极简使用方法 | 详细步骤说明 |
|---------|------------|------------|
| 适合人群 | 想要快速查看 Dashboard 效果的用户 | 需要自定义配置的开发者 |
| 配置复杂度 | 低（使用默认配置） | 高（可自定义各项参数） |
| 配置项 | 仅需配置 API 密钥 | 数据文件路径、模型参数等 |
| 灵活性 | 低 | 高 |
| 适用场合 | 快速体验、功能演示 | 生产环境部署、深入调试 |
| 了解系统原理 | 不需要 | 需要 |

### 极简使用方法

最快 3 步启动 Dashboard：

```bash
# 1. 安装依赖（包含 Yahoo Finance 数据获取支持）
pip install -r requirements.txt
pip install yfinance openpyxl

# 2. 配置API密钥并运行完整流程
cp .env.example .env
# 编辑 .env 文件，填入 QWEN_API_KEY

# 方式一：自动获取最新数据并运行完整流程（推荐）
./run_full_pipeline.sh --fetch-yahoo

# 方式二：使用已有数据文件运行完整流程
./run_full_pipeline.sh

# 3. 启动 Dashboard
cd dashboard && npm install && npm start
```

访问 `http://localhost:3000` 查看实时外汇预测仪表盘。

### 详细步骤说明

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入通义千问 API 密钥：

```bash
cp .env.example .env
# 编辑 .env 文件，填入 QWEN_API_KEY
```

#### 3. 准备数据

系统支持多种数据获取方式：

**方式一：通过 run_full_pipeline.sh 自动获取（推荐）**

```bash
# 获取最新数据并运行完整流程
./run_full_pipeline.sh --fetch-yahoo

# 获取指定日期范围的数据
./run_full_pipeline.sh --fetch-yahoo --start-date 2025-01-01 --end-date 2026-03-27

# 只获取特定货币对的数据
./run_full_pipeline.sh --fetch-yahoo --yahoo-pairs EUR JPY
```

**方式二：使用已有 Excel 数据文件**

数据文件需要满足以下要求：
- 工作表名称为货币对代码（如 EUR、JPY）
- 包含 `Date` 和 `Close` 列
- 日期格式：MM/DD/YYYY

**数据文件位置**：默认存放在 `data/raw/` 目录下（如 `data/raw/FXRate_20260320.xlsx`）

如需使用其他数据文件，可通过命令行参数指定：
- 使用相对路径：`./run_full_pipeline.sh --data-file data/raw/FXRate_20260327.xlsx`
- 或仅指定文件名（系统会在 `data/raw/` 目录查找）：`./run_full_pipeline.sh --data-file FXRate_20260327.xlsx`

**方式四：通过 Dashboard 上传**

```bash
# 启动 Dashboard 后，使用 API 上传文件
curl -X POST http://localhost:3000/api/v1/upload \
  -F "file=@FXRate_20260327.xlsx"
```

文件会自动保存到 `data/raw/` 目录，服务器缓存会被清除。

#### 4. 运行完整流程（生成预测数据）

```bash
# 方式一：使用默认数据文件运行完整流程
./run_full_pipeline.sh

# 方式二：自动获取最新数据并运行完整流程（推荐）
./run_full_pipeline.sh --fetch-yahoo

# 方式三：获取指定日期范围的数据并运行完整流程
./run_full_pipeline.sh --fetch-yahoo --start-date 2025-01-01 --end-date 2026-03-27

# 方式四：只获取特定货币对的数据并运行完整流程
./run_full_pipeline.sh --fetch-yahoo --yahoo-pairs EUR JPY

# 方式五：获取数据后跳过训练（只预测和分析）
./run_full_pipeline.sh --fetch-yahoo --skip-training

# 方式六：获取数据并禁用大模型分析
./run_full_pipeline.sh --fetch-yahoo --no-llm

# 方式七：跳过训练，只进行预测和分析（模型已存在时）
./run_full_pipeline.sh --skip-training

# 方式八：禁用大模型分析
./run_full_pipeline.sh --no-llm
```

此步骤会生成所有货币对的多周期预测数据（JSON格式），保存到 `data/predictions/` 目录。

#### 5. 启动 Dashboard

```bash
cd dashboard
npm install
npm start
```

访问 `http://localhost:3000` 查看 Dashboard。

Dashboard 功能：
- 实时显示货币对概览卡片（价格、预测、概率、置信度、分析摘要）
- 交易策略表格（各周期入场价、止损、止盈、建议、置信度）
  - 点击表格行可查看该策略的详细技术指标（6个关键类别）
- 技术指标图表（价格走势 + 均线、技术指标数值）
- 风险提示面板
- 点击卡片查看完整大模型分析（侧边栏详情）
- 策略指标详情侧边栏：
  - 支持标签页切换（大模型分析 / 技术指标）
  - 显示 6 个关键技术指标类别：
    - 支撑与阻力（布林带）
    - 趋势强度（ADX）
    - 动量（RSI、MACD）
    - 波动性（ATR）
    - 关键均线（SMA）
    - 交易信号（Williams%R）
  - 状态颜色标识（超买/超卖/中性/强势/弱势）
- 自动刷新：每 5 分钟自动刷新数据，显示最后更新时间
- 日期显示：浅蓝色背景，显眼展示日期信息
- 文件上传功能：支持上传新的数据文件（通过 API `POST /api/v1/upload`），自动保存到 `data/raw/` 目录

### Docker 部署（可选）

系统提供完整的 Docker 部署方案，支持容器化运行。

#### 前置要求

- Docker 20.10 或更高版本
- 确保 `.env` 文件已配置好 `QWEN_API_KEY`

#### 快速开始

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

#### Docker 功能特性

- **Dashboard 服务**：提供 Web 界面，实时显示外汇预测和分析结果
- **定时任务**：每小时自动执行 `run_full_pipeline.sh`，更新预测数据
- **配置管理**：通过 Volume 挂载 `.env` 文件，宿主机更新自动生效
- **数据持久化**：数据、模型、日志通过 Volume 挂载，容器删除不丢失

#### 详细文档

完整的 Docker 部署文档请参考：`dashboard/docker/DOCKER.md`

### 单独运行各模块

```bash
# 训练单个货币对的所有周期模型
python3 -m ml_services.fx_trading_model --mode train --pair EUR

# 生成单个货币对的多周期预测
python3 -m ml_services.fx_trading_model --mode predict --pair EUR

# 综合分析单个货币对
python3 -m comprehensive_analysis --pair EUR
```

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_integration.py -v

# 运行测试并检查覆盖率
pytest tests/ --cov=. --cov-report=html --cov-report=term
```

**测试覆盖率**: 85%（115个测试用例）
- 总测试数：115个
- 单元测试：106个
- 集成测试：9个

### Dashboard 测试

```bash
cd dashboard
npm test
```

## 技术指标（35个）

所有指标均使用滞后数据（`.shift(1)`）防止数据泄漏：

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

## 数据流设计

```
┌─────────────────────────────────────────────────────────────┐
│                  数据流（多周期双重验证）                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Excel 数据                                                 │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────┐                                        │
│  │ 技术指标引擎    │──→ 35个技术指标                       │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │ ML 多周期预测   │──→ 3个周期预测（1d/5d/20d）           │
│  │ - 1天模型       │                                        │
│  │ - 5天模型       │                                        │
│  │ - 20天模型      │                                        │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │多周期上下文构建 │──→ 一致性分析                         │
│  │ - 技术指标      │                                        │
│  │ - 3个ML预测     │                                        │
│  │ - 当前价格      │                                        │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │ 大模型分析      │──→ 自然语言分析                       │
│  │ - 技术面分析    │                                        │
│  │ - ML验证        │                                        │
│  │ - 风险分析      │                                        │
│  │ - 交易建议      │                                        │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │ 交易方案生成    │──→ 3个周期策略                        │
│  │ - 短线（1天）   │                                        │
│  │ - 中线（5天）   │                                        │
│  │ - 长线（20天）  │                                        │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │ JSON 格式化     │──→ 标准输出文件                       │
│  │ - 元数据        │                                        │
│  │ - ML预测        │                                        │
│  │ - 一致性分析    │                                        │
│  │ - LLM分析       │                                        │
│  │ - 交易策略      │                                        │
│  │ - 技术指标      │                                        │
│  │ - 风险分析      │                                        │
│  └─────────────────┘                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 项目结构

```
fx_predict/
├── run_full_pipeline.sh          # 一体化脚本（推荐）
├── fetch_fx_data.py               # Yahoo Finance 数据获取脚本
├── data/                           # 数据目录
│   ├── raw/                       # 原始数据文件（Excel）
│   │   └── FXRate_20260328_yahoo.xlsx  # Yahoo Finance 数据（6年历史）
│   ├── models/                    # 训练好的模型（CatBoost，18个模型）
│   │   ├── EUR_catboost_1d.pkl
│   │   ├── EUR_catboost_5d.pkl
│   │   ├── EUR_catboost_20d.pkl
│   │   └── ...（6货币对 × 3周期）
│   └── predictions/               # 预测结果（JSON格式）
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

## 风险控制

### 硬性约束

1. **绝对禁止买入**：当 CatBoost 预测概率 ≤ 0.50 时，绝对禁止买入
2. **高概率推荐**：当概率 ≥ 0.60 且预测为 1（上涨）时，推荐买入
3. **交易方案约束**：
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

### 置信度分级

- 高：probability ≥ 0.60
- 中：0.50 ≤ probability < 0.60
- 低：probability < 0.50

## 数据文件格式

Excel 文件必须满足：
- 工作表名称为货币对代码（如 EUR、JPY）
- 包含 `Date` 和 `Close` 列
- 可选：`High`、`Low`、`Open` 列（系统会自动生成）
- 日期格式：MM/DD/YYYY

## 常见问题

### 如何获取最新外汇数据

**问题**：如何自动获取最新的外汇数据？

**解决方案**：

使用 Yahoo Finance API 自动获取数据：

```bash
# 获取所有货币对数据（6年历史）
python3 fetch_fx_data.py --start-date 2020-01-01 --end-date 2026-03-27 --merge

# 获取指定货币对
python3 fetch_fx_data.py --pairs EUR JPY --merge

# 只获取最近一年数据
python3 fetch_fx_data.py --start-date 2025-03-27 --end-date 2026-03-27 --merge

# 保存单独文件（不合并）
python3 fetch_fx_data.py --pairs EUR
```

**或使用 run_full_pipeline.sh 自动获取并运行完整流程**：

```bash
# 获取最新数据并运行完整流程
./run_full_pipeline.sh --fetch-yahoo

# 获取指定日期范围的数据
./run_full_pipeline.sh --fetch-yahoo --start-date 2025-01-01 --end-date 2026-03-27

# 只获取特定货币对的数据
./run_full_pipeline.sh --fetch-yahoo --yahoo-pairs EUR JPY
```

**数据特点**：
- 数据源：Yahoo Finance（免费且稳定）
- 数据量：1622 条记录/货币对（6年历史）
- 只包含交易日数据（周一至周五）
- 不包含周末和节假日数据

**自动更新建议**：
可以设置 cron 定时任务自动更新数据：

```bash
# 每天凌晨 2 点更新数据
0 2 * * * cd /data/fx_predict && python3 fetch_fx_data.py --merge >> /var/log/fx_update.log 2>&1

# 或每周更新一次
0 2 * * 1 cd /data/fx_predict && python3 fetch_fx_data.py --merge >> /var/log/fx_update.log 2>&1
```

### 模型训练失败
- 确保数据点充足（至少 100 条）
- 检查数据文件格式和必需列
- 查看日志输出了解具体错误

### 大模型不可用
- 如果未配置 `QWEN_API_KEY`，大模型功能不可用
- 不影响核心功能（ML 预测和技术分析）

## 技术栈

- **Python**: 3.10+
- **Node.js**: 18+
- **Docker**: 20.10+
- **机器学习**: CatBoost, Scikit-learn
- **数据处理**: Pandas, NumPy, Openpyxl
- **Web 框架**: Express
- **前端技术**: HTML5, CSS3, JavaScript, Chart.js
- **大模型**: 通义千问 API
- **测试框架**: pytest, Jest

## 开发者

- **版本**: 5.0（多周期 + Dashboard + Docker + Yahoo Finance 数据集成）
- **创建时间**: 2026-03-25
- **最后更新**: 2026-03-27
- **许可证**: 本项目仅供学习和研究使用

## 相关文档

- **AGENTS.md**: 详细的项目文档，包含 API 说明、配置选项等
- **dashboard/docker/DOCKER.md**: Docker 部署完整指南
- **progress.txt**: 项目开发进度记录
- **lessons.md**: 开发经验教训总结