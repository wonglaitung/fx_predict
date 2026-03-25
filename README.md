# FX Predict - 外汇智能分析系统

基于机器学习和人机协作的外汇汇率预测系统，整合技术指标分析、CatBoost 预测模型和大模型解释，为外汇交易提供智能化建议。

## 功能特性

- **技术指标引擎**：计算 35 个专业技术指标（趋势、动量、波动、价格形态等）
- **CatBoost 预测模型**：20 天周期预测汇率涨跌方向
- **人机协作系统**：整合 ML 预测和技术信号，生成交易建议
- **大模型集成**：提供市场分析和建议解释
- **风险控制**：硬性约束（概率阈值、止损止盈）
- **数据泄漏防范**：所有指标使用滞后数据，确保预测有效性

## 支持的货币对

- EUR/USD（欧元/美元）
- USD/JPY（美元/日元）
- AUD/USD（澳元/美元）
- GBP/USD（英镑/美元）
- USD/CAD（美元/加元）
- NZD/USD（新西兰元/美元）

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量（可选）

复制 `.env.example` 为 `.env` 并填入通义千问 API 密钥：

```bash
cp .env.example .env
# 编辑 .env 文件，填入 QWEN_API_KEY
```

### 训练模型

```bash
python3 ml_services/fx_trading_model.py --mode train --pair EUR --horizon 20
```

### 生成预测

```bash
python3 ml_services/fx_trading_model.py --mode predict --pair EUR
```

### 综合分析

```bash
python3 comprehensive_analysis.py --date 2026-03-25
```

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行测试并检查覆盖率
pytest tests/ --cov=. --cov-report=html --cov-report=term
```

**测试覆盖率**: 85%（88 个测试用例）

## 技术指标（35个）

所有指标均使用滞后数据防止数据泄漏：

### 趋势类（11个）
- SMA/EMA（5/10/12/20/26/50/120日）
- MACD、MACD_Signal、MACD_Hist
- ADX、DI_Plus、DI_Minus

### 动量类（7个）
- RSI14、K、D、J、WilliamsR_14、CCI20

### 波动类（6个）
- ATR14、布林带、Std_20d、Volatility_20d

### 成交量类（1个）
- OBV（能量潮）

### 价格形态类（5个）
- Price_Percentile_120、Bias（5/10/20）、Trend_Slope_20

### 市场环境类（2个）
- MA_Alignment

## 项目结构

```
fx_predict/
├── data/                           # 数据目录
│   ├── models/                    # 训练好的模型
│   └── predictions/               # 预测结果
├── data_services/                 # 数据服务层
│   ├── excel_loader.py           # Excel 数据加载器
│   └── technical_analysis.py     # 技术指标引擎
├── ml_services/                   # 机器学习服务层
│   ├── fx_trading_model.py       # CatBoost 模型
│   ├── feature_engineering.py    # 特征工程
│   └── base_model_processor.py   # 模型处理器
├── llm_services/                  # 大模型服务层
│   └── qwen_engine.py            # 通义千问 API
├── comprehensive_analysis.py      # 人机协作整合层
├── config.py                      # 配置文件
├── requirements.txt               # 依赖列表
└── tests/                         # 测试文件（88 个测试用例）
```

## 风险控制

### 硬性约束

1. **绝对禁止买入**：当 CatBoost 预测概率 ≤ 0.50 时，禁止买入
2. **高概率推荐**：当概率 ≥ 0.60 且预测为上涨时，推荐买入
3. **止损止盈**：基于 ATR 计算（2倍 ATR）

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

### 模型训练失败
- 确保数据点充足（至少 100 条）
- 检查数据文件格式和必需列
- 查看日志输出了解具体错误

### 大模型不可用
- 如果未配置 `QWEN_API_KEY`，大模型功能不可用
- 不影响核心功能（ML 预测和技术分析）

## 技术栈

- **Python**: 3.10+
- **机器学习**: CatBoost
- **数据处理**: Pandas, NumPy
- **大模型**: 通义千问 API

## 开发者

- **版本**: 1.0 (MVP)
- **创建时间**: 2026-03-25

## 许可证

本项目仅供学习和研究使用。