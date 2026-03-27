# FX Predict Dashboard 设计文档

> **项目名称**: FX Predict Dashboard - 外汇智能分析看板
> **设计日期**: 2026-03-26
> **版本**: 1.0
> **设计师**: iFlow CLI

## 1. 项目概述

### 1.1 目标

构建一个专业的实时外汇分析看板，用于展示多周期外汇预测结果，支持实时监控和数据可视化。

### 1.2 核心特性

- **实时监控**: 自动刷新（5分钟）+ 手动刷新按钮
- **深色主题**: 专业交易员风格，深蓝灰色背景
- **数据可视化**: Chart.js 图表（雷达图、折线图、柱状图）
- **完整功能**: 6个货币对概览 + 交易策略对比 + 一致性分析 + 风险提示 + 技术指标
- **单页应用**: 所有功能在一个页面，使用标签页或折叠面板切换

### 1.3 技术栈

- **前端**: HTML + CSS + Vanilla JavaScript + Chart.js
- **后端**: Node.js + Express.js
- **数据源**: 直接读取 `data/predictions/` 下的 JSON 文件
- **部署**: 静态文件 + Node.js 服务器

### 1.4 目标用户

- 专业交易员
- 外汇分析师
- 投资者
- 研究人员

### 1.5 数据结构定义

所有 API 端点返回的 JSON 数据格式：

#### 1.5.1 完整数据结构（`/api/v1/pairs/:pair`）

```json
{
  "metadata": {
    "pair": "EUR",
    "pair_name": "EUR/USD",
    "current_price": 1.1570,
    "prediction_date": "2026-03-20"
  },
  "ml_predictions": {
    "1d": {
      "prediction": 1,
      "probability": 0.51,
      "confidence": "medium"
    },
    "5d": {
      "prediction": 1,
      "probability": 0.53,
      "confidence": "medium"
    },
    "20d": {
      "prediction": 1,
      "probability": 0.55,
      "confidence": "medium"
    }
  },
  "consistency_analysis": {
    "overall_consistency": 0.85,
    "consistent_horizons": ["5d", "20d"],
    "divergent_horizons": ["1d"],
    "strength": "Strong"
  },
  "llm_analysis": {
    "summary": "EUR/USD 显示出中期上涨趋势...",
    "overall_assessment": "buy",
    "key_factors": [
      "5日和20日预测一致",
      "趋势强度高",
      "风险可控"
    ],
    "horizon_analysis": {
      "1d": {
        "direction": "buy",
        "confidence": "medium",
        "reasoning": "短期波动但趋势向上"
      },
      "5d": {
        "direction": "buy",
        "confidence": "high",
        "reasoning": "中期趋势明确"
      },
      "20d": {
        "direction": "buy",
        "confidence": "high",
        "reasoning": "长期趋势持续"
      }
    }
  },
  "trading_strategies": [
    {
      "horizon": "1d",
      "direction": "buy",
      "entry_price": 1.1570,
      "stop_loss": 1.1540,
      "take_profit": 1.1600,
      "risk_reward": 1.0,
      "position_size": 10000,
      "confidence": "medium"
    },
    {
      "horizon": "5d",
      "direction": "buy",
      "entry_price": 1.1570,
      "stop_loss": 1.1500,
      "take_profit": 1.1640,
      "risk_reward": 1.14,
      "position_size": 10000,
      "confidence": "high"
    },
    {
      "horizon": "20d",
      "direction": "buy",
      "entry_price": 1.1570,
      "stop_loss": 1.1400,
      "take_profit": 1.1700,
      "risk_reward": 1.08,
      "position_size": 10000,
      "confidence": "high"
    }
  ],
  "technical_indicators": {
    "trend": {
      "SMA5": 1.1560,
      "SMA10": 1.1550,
      "SMA20": 1.1540,
      "SMA50": 1.1520,
      "SMA120": 1.1500,
      "EMA5": 1.1565,
      "EMA10": 1.1555,
      "EMA12": 1.1553,
      "EMA20": 1.1545,
      "EMA26": 1.1540,
      "MACD": 0.0025,
      "MACD_Signal": 0.0020,
      "MACD_Hist": 0.0005,
      "ADX": 25.0,
      "DI_Plus": 30.0,
      "DI_Minus": 15.0
    },
    "momentum": {
      "RSI14": 55.0,
      "K": 60.0,
      "D": 58.0,
      "J": 64.0,
      "Williams_R_14": -20.0,
      "CCI20": 50.0
    },
    "volatility": {
      "ATR14": 0.0030,
      "BB_Upper": 1.1600,
      "BB_Middle": 1.1540,
      "BB_Lower": 1.1480,
      "Std_20d": 0.0060,
      "Volatility_20d": 0.0052
    },
    "volume": {
      "OBV": 100000
    },
    "price_pattern": {
      "Price_Percentile_120": 75.0,
      "Bias_5": 0.09,
      "Bias_10": 0.17,
      "Bias_20": 0.26,
      "Trend_Slope_20": 0.00015
    },
    "market_environment": {
      "MA_Alignment": 0.9
    },
    "cross_signals": {
      "SMA5_cross_SMA20": 1,
      "Price_vs_Bollinger": 0.5
    }
  },
  "risk_analysis": {
    "warnings": [
      {
        "level": "medium",
        "message": "短期波动较大",
        "factor": "volatility"
      }
    ],
    "risk_level": "medium",
    "max_drawdown": 0.02,
    "stop_loss_distance": 0.003
  }
}
```

#### 1.5.2 货币对列表（`/api/v1/pairs`）

```json
{
  "pairs": [
    {
      "pair": "EUR",
      "pair_name": "EUR/USD",
      "last_update": "2026-03-26T12:34:56Z"
    },
    {
      "pair": "JPY",
      "pair_name": "USD/JPY",
      "last_update": "2026-03-26T12:34:56Z"
    }
  ]
}
```

#### 1.5.3 交易策略（`/api/v1/strategies`）

```json
{
  "strategies": {
    "EUR": [
      {
        "horizon": "1d",
        "direction": "buy",
        "entry_price": 1.1570,
        "stop_loss": 1.1540,
        "take_profit": 1.1600,
        "risk_reward": 1.0,
        "position_size": 10000,
        "confidence": "medium"
      }
    ],
    "JPY": [...]
  }
}
```

#### 1.5.4 一致性分析（`/api/v1/consistency`）

```json
{
  "consistency": {
    "EUR": {
      "overall_consistency": 0.85,
      "consistent_horizons": ["5d", "20d"],
      "divergent_horizons": ["1d"],
      "strength": "Strong"
    },
    "JPY": {...}
  }
}
```

#### 1.5.5 技术指标（`/api/v1/indicators/:pair`）

```json
{
  "indicators": {
    "trend": {
      "SMA5": 1.1560,
      "SMA10": 1.1550,
      "SMA20": 1.1540,
      "SMA50": 1.1520,
      "SMA120": 1.1500,
      "EMA5": 1.1565,
      "EMA10": 1.1555,
      "EMA12": 1.1553,
      "EMA20": 1.1545,
      "EMA26": 1.1540,
      "MACD": 0.0025,
      "MACD_Signal": 0.0020,
      "MACD_Hist": 0.0005,
      "ADX": 25.0,
      "DI_Plus": 30.0,
      "DI_Minus": 15.0
    },
    "momentum": {
      "RSI14": 55.0,
      "K": 60.0,
      "D": 58.0,
      "J": 64.0,
      "Williams_R_14": -20.0,
      "CCI20": 50.0
    },
    "volatility": {
      "ATR14": 0.0030,
      "BB_Upper": 1.1600,
      "BB_Middle": 1.1540,
      "BB_Lower": 1.1480,
      "Std_20d": 0.0060,
      "Volatility_20d": 0.0052
    },
    "volume": {
      "OBV": 100000
    },
    "price_pattern": {
      "Price_Percentile_120": 75.0,
      "Bias_5": 0.09,
      "Bias_10": 0.17,
      "Bias_20": 0.26,
      "Trend_Slope_20": 0.00015
    },
    "market_environment": {
      "MA_Alignment": 0.9
    },
    "cross_signals": {
      "SMA5_cross_SMA20": 1,
      "Price_vs_Bollinger": 0.5
    }
  }
}
```

#### 1.5.6 风险分析（`/api/v1/risk`）

```json
{
  "risks": {
    "EUR": {
      "warnings": [
        {
          "level": "medium",
          "message": "短期波动较大",
          "factor": "volatility"
        }
      ],
      "risk_level": "medium",
      "max_drawdown": 0.02,
      "stop_loss_distance": 0.003
    },
    "JPY": {...}
  }
}
```

#### 1.5.7 健康检查（`/health`）

```json
{
  "status": "ok",
  "uptime": 1234,
  "timestamp": "2026-03-26T12:34:56Z"
}
```

#### 1.5.8 错误响应

所有 API 错误的统一格式：

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "货币对代码无效",
    "details": "支持的货币对：EUR, JPY, AUD, GBP, CAD, NZD"
  }
}
```

## 2. 整体架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    前端 (Browser)                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  index.html (深色主题)                                │ │
│  │  - Header: 标题 + 刷新按钮 + 最后更新时间              │ │
│  │  - Main Content:                                      │ │
│  │    - 6个货币对概览卡片 (grid布局)                       │ │
│  │    - 选中货币对详情面板 (可折叠)                          │ │
│  │    - 交易策略对比表                                      │ │
│  │    - 一致性分析图                                        │ │
│  │    - 风险提示面板                                        │
│  │    - 技术指标图表                                        │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP API (JSON)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   后端 (Node.js + Express)                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  server.js                                            │ │
│  │  - GET /api/pairs - 所有货币对概览                      │ │
│  │  - GET /api/pairs/:pair - 单个货币对详情                │ │
│  │  - GET /api/strategies - 所有交易策略                   │ │
│  │  - GET /api/consistency - 一致性分析                    │ │
│  │  - GET /api/indicators/:pair - 技术指标                  │ │
│  │  - GET /api/risk - 风险分析                            │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 读取 JSON 文件
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              数据存储 (data/predictions/)                    │
│  - EUR_multi_horizon_*.json                               │
│  - JPY_multi_horizon_*.json                               │
│  - AUD_multi_horizon_*.json                               │
│  - GBP_multi_horizon_*.json                               │
│  - CAD_multi_horizon_*.json                               │
│  - NZD_multi_horizon_*.json                               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 数据流

```
用户请求 → 前端发送 HTTP GET → Express 服务器 
  → 数据加载器读取 JSON 文件 → 数据聚合器处理 
  → 返回 JSON 响应 → 前端更新 UI → Chart.js 渲染图表
```

### 2.3 文件结构

```
dashboard/
├── server.js              # Express API 服务器
├── public/
│   ├── index.html        # 主页面
│   ├── css/
│   │   └── styles.css    # 深色主题样式
│   └── js/
│       ├── app.js        # 主应用逻辑
│       ├── components.js # UI 组件
│       └── charts.js     # 图表渲染
├── package.json
└── README.md
```

## 3. 页面布局

### 3.1 整体布局

```
┌──────────────────────────────────────────────────────────────────────┐
│  📊 FX Predict Dashboard              [🔄 Refresh]  Last: 2026-03-26 12:00  │
├──────────────────────────────────────────────────────────────────────┤
│  概览面板 (6个卡片，2行3列)                                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                                 │
│  │ EUR/USD │ │ USD/JPY │ │ AUD/USD │                                 │
│  │ 1.1570  │ │ 158.36  │ │ 0.7095  │                                 │
│  │ ↗ 1d    │ │ ↗ 1d    │ │ ↗ 1d    │                                 │
│  │ ↑ 0.51% │ │ ↑ 0.67% │ │ ↑ 0.33% │                                 │
│  └─────────┘ └─────────┘ └─────────┘                                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                                 │
│  │ GBP/USD │ │ USD/CAD │ │ NZD/USD │                                 │
│  │ 1.3427  │ │ 1.3723  │ │ 0.5891  │                                 │
│  │ ↘ 1d    │ │ ↗ 1d    │ │ ↘ 1d    │                                 │
│  │ ↑ 0.44% │ │ ↑ 0.67% │ │ ↑ 0.33% │                                 │
│  └─────────┘ └─────────┘ └─────────┘                                 │
├──────────────────────────────────────────────────────────────────────┤
│  [点击任意货币对查看详情]                                                │
├──────────────────────────────────────────────────────────────────────┤
│  📈 交易策略对比                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐│
│  │  货币对 | 周期   | 建议   | 置信度 | 入场价   | 止损    | 止盈   │  ││
│  │  EUR   | 1天   | buy    | medium | 1.1570  | 1.1315  | 1.1825 │  ││
│  │  EUR   | 5天   | buy    | medium | 1.1570  | 1.1223  | 1.1917 │  ││
│  │  EUR   | 20天  | buy    | medium | 1.1570  | 1.0876  | 1.2264 │  ││
│  │  GBP   | 1天   | sell   | low    | 1.3427  | 1.3722  | 1.3132 │  ││
│  │  ...    | ...   | ...    | ...    | ...     | ...     | ...   │  ││
│  └────────────────────────────────────────────────────────────────────┘│
├──────────────────────────────────────────────────────────────────────┤
│  📊 一致性分析图 (雷达图)                                                │
│  ┌────────────────────────────────────────────────────────────────────┐│
│  │      1.0                                                        ││
│  │     ╱│╲                                                         ││
│  │    ╱ │ ╲                                                        ││
│  │   ╱  │  ╲  ← 一致性评分                                        ││
│  │  ╱   │   ╲                                                      ││
│  │ ─────┼───── ← 各货币对                                          ││
│  │   ↑  │                                                              ││
│  │ 上涨│下跌  ← 多数趋势                                           ││
│  └────────────────────────────────────────────────────────────────────┘│
├──────────────────────────────────────────────────────────────────────┤
│  ⚠️ 风险提示                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐│
│  │ • GBP 置信度低，建议谨慎                                          ││
│  │ • 部分货币对预测一致性较低                                        ││
│  │ • 市场波动性增加，注意仓位管理                                    ││
│  └────────────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────────┘
```

### 3.4 响应式设计

#### 3.4.1 断点定义

- **桌面（Desktop）**: > 1200px
- **平板（Tablet）**: 768px - 1200px
- **手机（Mobile）**: < 768px

#### 3.4.2 概览卡片布局

**桌面（> 1200px）**:
```
2行3列布局
┌─────────┐ ┌─────────┐ ┌─────────┐
│ EUR/USD │ │ USD/JPY │ │ AUD/USD │
└─────────┘ └─────────┘ └─────────┘
┌─────────┐ ┌─────────┐ ┌─────────┐
│ GBP/USD │ │ USD/CAD │ │ NZD/USD │
└─────────┘ └─────────┘ └─────────┘
```

**平板（768px - 1200px）**:
```
3行2列布局
┌─────────┐ ┌─────────┐
│ EUR/USD │ │ USD/JPY │
└─────────┘ └─────────┘
┌─────────┐ ┌─────────┐
│ AUD/USD │ │ GBP/USD │
└─────────┘ └─────────┘
┌─────────┐ ┌─────────┐
│ USD/CAD │ │ NZD/USD │
└─────────┘ └─────────┘
```

**手机（< 768px）**:
```
6行1列布局
┌─────────┐
│ EUR/USD │
└─────────┘
┌─────────┐
│ USD/JPY │
└─────────┘
┌─────────┐
│ AUD/USD │
└─────────┘
┌─────────┐
│ GBP/USD │
└─────────┘
┌─────────┐
│ USD/CAD │
└─────────┘
┌─────────┐
│ NZD/USD │
└─────────┘
```

#### 3.4.3 交易策略表格

**桌面（> 1200px）**:
- 完整显示所有列（货币对、周期、建议、置信度、入场价、止损、止盈）
- 宽度：100%

**平板（768px - 1200px）**:
- 显示主要列（货币对、周期、建议、置信度、入场价）
- 其他列使用折叠面板显示
- 宽度：100%

**手机（< 768px）**:
- 卡片式布局，每行一个货币对
- 点击展开显示完整信息
- 宽度：100%

#### 3.4.4 图表容器

**桌面（> 1200px）**:
- 一致性分析图和风险提示并排显示（2列）
- 图表宽度：50%
- 最小高度：300px

**平板（768px - 1200px）**:
- 一致性分析图和风险提示垂直堆叠（1列）
- 图表宽度：100%
- 最小高度：250px

**手机（< 768px）**:
- 所有图表垂直堆叠（1列）
- 图表宽度：100%
- 最小高度：200px

#### 3.4.5 CSS 媒体查询示例

```css
/* 默认样式（桌面优先） */
.overview-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

/* 平板样式 */
@media (max-width: 1200px) {
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 手机样式 */
@media (max-width: 768px) {
  .overview-cards {
    grid-template-columns: 1fr;
  }

  .trading-strategy-table {
    display: none;
  }

  .trading-strategy-cards {
    display: block;
  }
}
```

## 4. 前端组件设计

### 4.1 Header 组件

**功能**:
- 显示标题：`📊 FX Predict Dashboard`
- 刷新按钮：`[🔄 Refresh]`（带旋转动画）
- 最后更新时间：`Last: 2026-03-26 12:00`
- 自动刷新指示器：`Auto-refresh: 5min`

**交互**:
- 点击刷新按钮：手动触发数据刷新
- 旋转动画：刷新时显示
- 自动刷新：每 5 分钟自动更新

#### 4.1.1 自动刷新机制实现

**前端实现**:
```javascript
// 自动刷新定时器
let autoRefreshInterval;
const AUTO_REFRESH_INTERVAL = 5 * 60 * 1000; // 5 分钟

function startAutoRefresh() {
  // 清除旧的定时器
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
  }

  // 设置新的定时器
  autoRefreshInterval = setInterval(() => {
    refreshData();
  }, AUTO_REFRESH_INTERVAL);

  // 显示自动刷新指示器
  document.getElementById('auto-refresh-indicator').textContent =
    `Auto-refresh: 5min`;
}

function stopAutoRefresh() {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
    autoRefreshInterval = null;
  }

  // 隐藏自动刷新指示器
  document.getElementById('auto-refresh-indicator').textContent = '';
}

// 手动刷新
async function refreshData() {
  const refreshBtn = document.getElementById('refresh-btn');
  refreshBtn.classList.add('rotating');

  try {
    const data = await fetch('/api/v1/pairs').then(res => res.json());
    updateDashboard(data);
    document.getElementById('last-update').textContent =
      `Last: ${new Date().toLocaleString()}`;
  } catch (error) {
    console.error('Failed to refresh data:', error);
    showError('加载失败，请重试');
  } finally {
    refreshBtn.classList.remove('rotating');
  }
}

// 页面加载时启动自动刷新
document.addEventListener('DOMContentLoaded', () => {
  refreshData();
  startAutoRefresh();
});
```

**CSS 动画**:
```css
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.rotating {
  animation: rotate 1s linear infinite;
}
```

**注意事项**:
- 自动刷新在页面加载时自动启动
- 用户可以暂停/恢复自动刷新（可选功能）
- 手动刷新不会重置自动刷新定时器
- 页面隐藏时暂停自动刷新，节省资源

### 4.2 概览卡片组件

**功能**:
- 显示货币对名称和代码（如 `EUR/USD`）
- 显示当前价格（大字体，4位小数）
- 显示预测方向图标（↗ 上涨，↘ 下跌，→ 持平）
- 显示预测概率（百分比）
- 背景色：绿色（上涨）、红色（下跌）、灰色（持平）

**交互**:
- 悬停效果：显示详细预测信息
- 点击效果：展开详情面板

**数据映射**:
```javascript
{
  pair_name: "EUR/USD",
  current_price: 1.1570,
  prediction: 1,  // 0=下跌, 1=上涨
  probability: 0.5132, // 百分比
  confidence: "medium"
}
```

#### 4.2.1 图标风格统一

**设计原则**: 统一使用 Unicode 字符图标，不使用 emoji，保持专业风格。

**方向图标**:
- 上涨：`↗` (U+2197, North East Arrow)
- 下跌：`↘` (U+2198, South East Arrow)
- 持平：`→` (U+2192, Rightwards Arrow)
- 买：`▲` (U+25B2, Black Up-Pointing Triangle)
- 卖：`▼` (U+25BC, Black Down-Pointing Triangle)

**状态图标**:
- 成功：`✓` (U+2713, Check Mark)
- 警告：`⚠` (U+26A0, Warning Sign)
- 错误：`✕` (U+2715, Multiplication X)
- 信息：`ℹ` (U+2139, Information Source)

**操作图标**:
- 刷新：`↻` (U+21BB, Clockwise Open Circle Arrow)
- 关闭：`✕` (U+2715, Multiplication X)
- 展开：`▾` (U+25BE, Black Down-Pointing Small Triangle)
- 收起：`▴` (U+25B4, Black Up-Pointing Small Triangle)

**颜色映射**:
- 绿色（上涨/买/成功）：`#22c55e`
- 红色（下跌/卖/错误）：`#ef4444`
- 灰色（持平/信息）：`#94a3b8`
- 橙色（警告）：`#f59e0b`

**使用示例**:
```javascript
// 显示方向图标
function getDirectionIcon(prediction) {
  if (prediction === 1) return '↗';
  if (prediction === 0) return '↘';
  return '→';
}

// 显示置信度图标
function getConfidenceIcon(confidence) {
  switch (confidence) {
    case 'high': return '✓';
    case 'medium': return '⚠';
    case 'low': return '✕';
    default: return 'ℹ';
  }
}

// 显示操作图标
function getRefreshIcon(isLoading) {
  return isLoading ? '↻' : '↻';
}
```

### 4.3 交易策略表格组件

**功能**:
- 表格列：货币对、周期、建议、置信度、入场价、止损、止盈、风险回报比
- 排序功能：按货币对或置信度排序
- 筛选功能：只显示特定周期的策略
- 颜色编码：buy（绿色）、sell（红色）、hold（灰色）

**数据来源**: `trading_strategies` 字段

### 4.4 一致性分析图表组件

**功能**:
- 使用 Chart.js 雷达图
- X轴：6个货币对
- Y轴：一致性评分（0-1）
- 颜色映射：绿色（≥0.67）、黄色（0.33-0.67）、红色（<0.33）
- 图例：多数趋势（上涨/下跌/中性）

**数据来源**: `consistency_analysis` 字段

### 4.5 风险提示面板组件

**功能**:
- 警告列表（带图标）
- 滚动容器（最多显示5条）
- 按优先级排序（高风险优先）
- 自动隐藏（无警告时不显示）

**数据来源**: `risk_analysis.warnings` 字段

### 4.6 技术指标图表组件

**功能**:
- 折线图：价格走势 + 均线
- 柱状图：技术指标数值
- 时间范围：最近30天
- 图例：SMA5、SMA10、SMA20等

**数据来源**: `technical_indicators` 字段

#### 4.6.1 图表类型说明

**折线图（Line Chart）**:
- **用途**: 显示价格走势和均线
- **数据系列**:
  - 当前价格（主线，粗线）
  - SMA5（细线，蓝色）
  - SMA10（细线，绿色）
  - SMA20（细线，黄色）
  - SMA50（细线，橙色）
  - SMA120（细线，红色）
- **配置**:
  ```javascript
  {
    type: 'line',
    data: {
      labels: ['2026-02-20', '2026-02-21', ..., '2026-03-20'],
      datasets: [
        {
          label: 'Price',
          data: [1.1500, 1.1520, ..., 1.1570],
          borderColor: '#f1f5f9',
          borderWidth: 2,
          tension: 0.4
        },
        {
          label: 'SMA5',
          data: [1.1490, 1.1510, ..., 1.1560],
          borderColor: '#3b82f6',
          borderWidth: 1,
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: false,
          grid: { color: '#334155' }
        },
        x: {
          grid: { color: '#334155' }
        }
      }
    }
  }
  ```

**柱状图（Bar Chart）**:
- **用途**: 显示技术指标数值（RSI、MACD 等）
- **数据系列**:
  - RSI14（绿色，0-100 范围）
  - MACD（蓝色，正负值）
  - ATR14（橙色，正值）
- **配置**:
  ```javascript
  {
    type: 'bar',
    data: {
      labels: ['2026-02-20', '2026-02-21', ..., '2026-03-20'],
      datasets: [
        {
          label: 'RSI14',
          data: [45, 50, ..., 55],
          backgroundColor: '#22c55e'
        },
        {
          label: 'MACD',
          data: [0.0010, 0.0015, ..., 0.0025],
          backgroundColor: '#3b82f6'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: '#334155' }
        },
        x: {
          grid: { color: '#334155' }
        }
      }
    }
  }
  ```

**雷达图（Radar Chart）**:
- **用途**: 显示一致性分析（见 4.4 节）
- **数据系列**:
  - 1 天预测一致性
  - 5 天预测一致性
  - 20 天预测一致性
  - 整体一致性
- **配置**:
  ```javascript
  {
    type: 'radar',
    data: {
      labels: ['1d', '5d', '20d', 'Overall'],
      datasets: [
        {
          label: 'EUR/USD',
          data: [0.70, 0.85, 0.90, 0.85],
          backgroundColor: 'rgba(59, 130, 246, 0.2)',
          borderColor: '#3b82f6',
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          beginAtZero: true,
          max: 1,
          grid: { color: '#334155' },
          angleLines: { color: '#334155' },
          pointLabels: { color: '#f1f5f9' }
        }
      }
    }
  }
  ```

#### 4.6.2 图表容器设计

**单个图表容器**:
```html
<div class="chart-container">
  <h3 class="chart-title">价格走势 + 均线</h3>
  <div class="chart-canvas-wrapper">
    <canvas id="priceChart"></canvas>
  </div>
</div>
```

**多个图表并排**:
```html
<div class="charts-row">
  <div class="chart-container">
    <h3 class="chart-title">价格走势</h3>
    <div class="chart-canvas-wrapper">
      <canvas id="priceChart"></canvas>
    </div>
  </div>
  <div class="chart-container">
    <h3 class="chart-title">技术指标</h3>
    <div class="chart-canvas-wrapper">
      <canvas id="indicatorChart"></canvas>
    </div>
  </div>
</div>
```

**CSS 样式**:
```css
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

.chart-container {
  background: var(--bg-secondary);
  border-radius: 0.5rem;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.chart-title {
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.chart-canvas-wrapper {
  position: relative;
  height: 300px;
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
}
```

#### 4.6.3 图表数据更新

**更新数据**:
```javascript
function updateChart(chart, newData) {
  chart.data.labels = newData.labels;
  chart.data.datasets.forEach((dataset, index) => {
    dataset.data = newData.datasets[index].data;
  });
  chart.update();
}
```

**重新创建图表**:
```javascript
function recreateChart(canvasId, newConfig) {
  const canvas = document.getElementById(canvasId);
  const chart = Chart.getChart(canvas);

  if (chart) {
    chart.destroy();
  }

  new Chart(canvas, newConfig);
}
```

## 5. 后端设计

### 5.1 API 端点

**注意**: 所有 API 端点都使用 v1 版本前缀，便于未来版本升级。

```javascript
GET /health             // 健康检查
GET /api/v1/pairs       // 所有货币对概览
GET /api/v1/pairs/:pair // 单个货币对详情
GET /api/v1/strategies  // 所有交易策略
GET /api/v1/consistency // 一致性分析
GET /api/v1/indicators/:pair // 技术指标
GET /api/v1/risk        // 风险分析
```

#### 5.1.1 健康检查端点

**端点**: `GET /health`

**响应**:
```json
{
  "status": "ok",
  "uptime": 1234,
  "timestamp": "2026-03-26T12:34:56Z"
}
```

**实现**:
```javascript
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});
```

#### 5.1.2 货币对列表端点

**端点**: `GET /api/v1/pairs`

**响应**:
```json
{
  "pairs": [
    {
      "pair": "EUR",
      "pair_name": "EUR/USD",
      "last_update": "2026-03-26T12:34:56Z"
    }
  ]
}
```

#### 5.1.3 单个货币对详情端点

**端点**: `GET /api/v1/pairs/:pair`

**参数**:
- `pair`: 货币对代码（EUR, JPY, AUD, GBP, CAD, NZD）

**响应**: 完整数据结构（见 1.5.1 节）

**错误响应**:
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "货币对代码无效",
    "details": "支持的货币对：EUR, JPY, AUD, GBP, CAD, NZD"
  }
}
```

#### 5.1.4 交易策略端点

**端点**: `GET /api/v1/strategies`

**响应**:
```json
{
  "strategies": {
    "EUR": [
      {
        "horizon": "1d",
        "direction": "buy",
        "entry_price": 1.1570,
        "stop_loss": 1.1540,
        "take_profit": 1.1600,
        "risk_reward": 1.0,
        "position_size": 10000,
        "confidence": "medium"
      }
    ]
  }
}
```

#### 5.1.5 一致性分析端点

**端点**: `GET /api/v1/consistency`

**响应**:
```json
{
  "consistency": {
    "EUR": {
      "overall_consistency": 0.85,
      "consistent_horizons": ["5d", "20d"],
      "divergent_horizons": ["1d"],
      "strength": "Strong"
    }
  }
}
```

#### 5.1.6 技术指标端点

**端点**: `GET /api/v1/indicators/:pair`

**响应**: 技术指标数据（见 1.5.5 节）

#### 5.1.7 风险分析端点

**端点**: `GET /api/v1/risk`

**响应**: 风险分析数据（见 1.5.6 节）

#### 5.1.8 错误处理

所有端点的错误响应格式统一（见 1.5.8 节）。

**错误代码定义**:
- `INVALID_REQUEST`: 请求参数无效
- `NOT_FOUND`: 资源未找到
- `INTERNAL_ERROR`: 服务器内部错误
- `FILE_READ_ERROR`: 文件读取失败
- `DATA_PARSE_ERROR`: 数据解析失败

### 5.2 数据加载器

**功能**:
- 读取 `data/predictions/` 目录
- 解析 JSON 文件
- 缓存机制（避免重复读取）
- 文件监听（自动检测新文件）

**实现**:
```javascript
const fs = require('fs');
const path = require('path');

class DataLoader {
  loadAllPairs() {
    const files = fs.readdirSync('data/predictions/')
      .filter(f => f.endsWith('.json'));
    return files.map(f => JSON.parse(fs.readFileSync(f)));
  }
}
```

### 5.3 数据聚合器

**功能**:
- 合并多个货币对的数据
- 计算统计信息（平均一致性、上涨/下跌数量）
- 生成对比数据

**实现**:
```javascript
class DataAggregator {
  aggregatePairs(data) {
    return {
      pairs: data.map(d => ({
        pair: d.metadata.pair,
        pair_name: d.metadata.pair_name,
        current_price: d.metadata.current_price,
        predictions: d.ml_predictions
      })),
      stats: this.calculateStats(data)
    };
  }
}
```

### 5.4 实时数据更新机制

#### 5.4.1 文件监听（File Watcher）

**功能**: 监听 `data/predictions/` 目录，自动检测新文件生成。

**实现**:
```javascript
const chokidar = require('chokidar');

class DataWatcher {
  constructor(callback) {
    this.watcher = chokidar.watch('data/predictions/*.json', {
      ignored: /(^|[\/\\])\../,
      persistent: true
    });

    this.watcher
      .on('add', (path) => {
        console.log(`New file detected: ${path}`);
        callback('add', path);
      })
      .on('change', (path) => {
        console.log(`File changed: ${path}`);
        callback('change', path);
      });
  }

  stop() {
    this.watcher.close();
  }
}
```

**使用场景**:
- 当新的预测文件生成时，自动刷新数据
- 避免用户手动刷新，提升用户体验

**注意事项**:
- 文件监听会增加 CPU 使用，仅在开发环境启用
- 生产环境使用定时轮询（每 5 分钟）

#### 5.4.2 数据缓存机制

**功能**: 缓存已加载的数据，避免重复读取文件。

**实现**:
```javascript
class DataCache {
  constructor(ttl = 300000) { // 默认 5 分钟缓存
    this.cache = new Map();
    this.ttl = ttl;
  }

  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  set(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  clear() {
    this.cache.clear();
  }
}
```

**使用场景**:
- 缓存 API 响应，减少文件 I/O
- 提升响应速度

**注意事项**:
- 缓存时间设置为 5 分钟，与自动刷新周期一致
- 数据更新时清除缓存

#### 5.4.3 定时刷新机制

**功能**: 定时从数据源刷新数据，确保数据最新。

**实现**:
```javascript
setInterval(async () => {
  try {
    console.log('Auto-refreshing data...');
    const newData = await dataLoader.loadAllPairs();
    dataCache.clear();
    newData.forEach(item => {
      dataCache.set(item.metadata.pair, item);
    });
    console.log('Data refreshed successfully');
  } catch (error) {
    console.error('Failed to refresh data:', error);
  }
}, 300000); // 每 5 分钟
```

**使用场景**:
- 生产环境使用定时刷新，避免文件监听的 CPU 开销
- 与前端自动刷新同步

## 6. 错误处理

### 6.1 数据加载错误

- **JSON 文件不存在**: 显示友好错误信息，建议用户运行分析
- **JSON 格式错误**: 记录日志，显示默认空数据
- **文件读取失败**: 重试 3 次，超时后显示错误

### 6.2 API 错误

- **404 Not Found**: 返回 404 响应，前端显示"数据不可用"
- **500 Internal Error**: 记录详细日志，返回错误信息
- **网络超时**: 显示"加载失败，请重试"

### 6.3 前端错误

- **数据为空**: 显示"暂无数据"占位符
- **图表渲染失败**: 显示错误信息，隐藏图表
- **刷新失败**: 显示警告，保留当前数据

### 6.4 安全性设计

#### 6.4.1 XSS 防护

- **输入验证**: 所有用户输入（包括 URL 参数、表单数据）必须经过验证和转义
- **内容安全策略 (CSP)**: 配置 HTTP 头限制资源加载来源
- **DOM 操作**: 使用 `textContent` 而非 `innerHTML`，防止脚本注入

```javascript
// 示例：安全地渲染用户输入
function renderUserInput(input) {
  const element = document.createElement('div');
  element.textContent = input; // 自动转义
  return element;
}
```

#### 6.4.2 CORS 配置

- **白名单机制**: 只允许特定域名访问 API
- **方法限制**: 仅允许 GET 请求（数据只读，不需要 POST/PUT/DELETE）

```javascript
// server.js 中的 CORS 配置
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  methods: ['GET'],
  allowedHeaders: ['Content-Type']
}));
```

#### 6.4.3 数据验证

- **文件路径验证**: 防止路径遍历攻击
- **文件扩展名验证**: 只允许 `.json` 文件
- **JSON Schema 验证**: 验证返回的数据结构

```javascript
// 示例：文件路径验证
function validatePairCode(pair) {
  const validPairs = ['EUR', 'JPY', 'AUD', 'GBP', 'CAD', 'NZD'];
  if (!validPairs.includes(pair)) {
    throw new Error('Invalid pair code');
  }
}

// 示例：路径遍历防护
function getSafeFilePath(pair) {
  validatePairCode(pair);
  const dataDir = path.join(__dirname, '../data/predictions');
  const safePath = path.normalize(path.join(dataDir, `${pair}_multi_horizon_*.json`));
  if (!safePath.startsWith(dataDir)) {
    throw new Error('Path traversal detected');
  }
  return safePath;
}
```

#### 6.4.4 敏感数据保护

- **环境变量**: 配置信息（如 API 密钥、端口）存储在 `.env` 文件中，不提交到版本控制
- **日志脱敏**: 日志中不记录敏感信息（如完整的 API 密钥）

```bash
# .env 文件示例
PORT=3000
LOG_LEVEL=info
DATA_DIR=./data/predictions
ALLOWED_ORIGINS=http://localhost:3000,https://dashboard.example.com
```

#### 6.4.5 错误信息处理

- **通用错误消息**: 不暴露系统内部信息
- **错误代码**: 使用预定义的错误代码，而非详细错误描述

```javascript
// 示例：错误处理中间件
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message: '服务器内部错误，请稍后重试'
    }
  });
});
```

## 7. 测试策略

### 7.1 单元测试

- **后端 API 测试**: 每个 API 端点的响应验证
- **数据加载器测试**: 模拟文件读取和解析
- **前端组件测试**: DOM 操作和状态管理

### 7.2 集成测试

- **完整流程**: 从文件读取到 UI 显示
- **错误场景**: 文件缺失、格式错误、网络失败
- **自动刷新**: 验证自动更新功能

### 7.3 性能测试

### 7.3 性能测试

**测试工具**:
- **Lighthouse**: 前端性能测试（Chrome DevTools）
- **k6**: 负载测试和压力测试
- **Apache Bench (ab)**: API 性能测试

**测试指标**:
- **首次加载时间**: < 2 秒（Chrome 浏览器，4G 网络）
- **手动刷新时间**: < 500ms（Chrome 浏览器，4G 网络）
- **API 响应时间**: < 100ms（P95）
- **并发用户数**: ≥ 10（无性能下降）
- **内存使用**: < 256MB（Node.js 进程）
- **CPU 使用率**: < 50%（正常负载下）

**测试场景**:
```bash
# 使用 k6 进行负载测试
k6 run --vus 10 --duration 30s tests/load-test.js

# 使用 ab 测试 API 性能
ab -n 1000 -c 10 http://localhost:3000/api/v1/pairs

# 使用 Lighthouse 测试前端性能
lighthouse http://localhost:3000 --view
```

**性能优化策略**:
- **前端优化**:
  - 使用 CDN 加载 Chart.js
  - 压缩和合并 CSS/JS 文件
  - 图片懒加载（如果有）
  - 启用浏览器缓存

- **后端优化**:
  - 数据缓存（内存缓存，避免重复读取文件）
  - 响应压缩（gzip）
  - 连接池管理
  - 异步文件读取

- **网络优化**:
  - HTTP/2 支持
  - 静态资源缓存
  - 最小化 HTTP 请求

## 8. 部署策略

### 8.1 开发环境

```bash
# 安装依赖
npm install

# 启动服务器
node server.js

# 访问 http://localhost:3000
```

### 8.2 生产环境

- **进程管理**: 使用 PM2
- **反向代理**: Nginx
- **HTTPS**: SSL/TLS 支持

### 8.3 日志管理

#### 8.3.1 日志级别

- **ERROR**: 错误信息（API 失败、文件读取错误）
- **WARN**: 警告信息（数据缺失、性能下降）
- **INFO**: 一般信息（API 请求、数据刷新）
- **DEBUG**: 调试信息（仅开发环境）

#### 8.3.2 日志格式

```
[2026-03-26 12:34:56] [INFO] [api] GET /api/v1/pairs - 200 - 45ms
[2026-03-26 12:34:57] [ERROR] [api] GET /api/v1/pairs/INVALID - 404 - 10ms
[2026-03-26 12:34:58] [WARN] [data] EUR_multi_horizon_20260326_123456.json not found
```

#### 8.3.3 日志轮转

- **文件大小限制**: 10MB
- **保留文件数**: 5 个
- **日志文件**:
  - `logs/access.log`: 访问日志
  - `logs/error.log`: 错误日志
  - `logs/app.log`: 应用日志

#### 8.3.4 日志实现

```javascript
// server.js
const fs = require('fs');
const path = require('path');

// 日志函数
function log(level, category, message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${level}] [${category}] ${message}\n`;
  const logFile = level === 'ERROR' ? 'logs/error.log' : 'logs/app.log';

  fs.appendFileSync(logFile, logMessage);
  console.log(logMessage.trim());
}

// 使用示例
log('INFO', 'api', 'GET /api/v1/pairs - 200 - 45ms');
log('ERROR', 'api', 'GET /api/v1/pairs/INVALID - 404 - 10ms');
```

## 9. 深色主题设计

### 9.1 颜色方案

- **背景**: `#0f172a`（深蓝灰色）
- **卡片背景**: `#1e293b`（稍浅的蓝灰色）
- **文字**: `#f1f5f9`（浅灰色）
- **强调色**:
  - 上涨: `#22c55e`（绿色）
  - 下跌: `#ef4444`（红色）
  - 警告: `#f59e0b`（橙色）
  - 信息: `#3b82f6`（蓝色）

### 9.2 字体

- **标题**: `'Inter', sans-serif`
- **数字**: `'Roboto Mono', monospace`

### 9.3 CSS 变量

```css
:root {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --text-primary: #f1f5f9;
  --color-success: #22c55e;
  --color-danger: #ef4444;
  --color-warning: #f59e0b;
  --color-info: #3b82f6;
}
```

## 10. 依赖项

### 10.1 后端依赖

```json
{
  "dependencies": {
    "express": "4.18.2",
    "cors": "2.8.5",
    "dotenv": "16.3.1"
  },
  "devDependencies": {
    "nodemon": "3.0.1",
    "jest": "29.7.0",
    "supertest": "6.3.3",
    "eslint": "8.54.0"
  }
}
```

**依赖说明**:
- **express**: Web 框架
- **cors**: 跨域资源共享
- **dotenv**: 环境变量管理
- **nodemon**: 开发时自动重启服务器
- **jest**: 单元测试框架
- **supertest**: HTTP 测试
- **eslint**: 代码规范检查

### 10.2 前端依赖

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js"></script>
```

**CDN 版本锁定**: 使用固定版本号，避免自动更新导致兼容性问题。

### 10.3 配置文件

```
dashboard/
├── server.js
├── package.json
├── package-lock.json
├── .env
├── .env.example
├── .gitignore
├── public/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── app.js
│       ├── components.js
│       └── charts.js
├── tests/
│   ├── api/
│   │   └── api.test.js
│   ├── integration/
│   │   └── workflow.test.js
│   └── e2e/
│       └── dashboard.test.js
└── logs/
    ├── access.log
    └── error.log
```

### 10.4 环境配置

**.env 文件示例**:
```bash
# 服务器配置
PORT=3000
NODE_ENV=production

# 日志配置
LOG_LEVEL=info

# 数据配置
DATA_DIR=./data/predictions

# CORS 配置
ALLOWED_ORIGINS=http://localhost:3000,https://dashboard.example.com

# 缓存配置
CACHE_TTL=300000
```

**.env.example 文件**:
```bash
# 服务器配置
PORT=3000
NODE_ENV=development

# 日志配置
LOG_LEVEL=debug

# 数据配置
DATA_DIR=./data/predictions

# CORS 配置
ALLOWED_ORIGINS=http://localhost:3000

# 缓存配置
CACHE_TTL=300000
```

### 10.5 .gitignore

```gitignore
node_modules/
.env
*.log
.DS_Store
coverage/
```

## 11. 成功标准

### 11.1 功能标准

- [x] 实时监控：自动刷新（5分钟）+ 手动刷新按钮
- [x] 深色主题：专业交易员风格
- [x] 数据可视化：Chart.js 图表
- [x] 完整功能：6个货币对概览 + 交易策略对比 + 一致性分析 + 风险提示 + 技术指标
- [x] 错误处理：完善的错误处理和降级策略

### 11.2 性能标准

- [x] 首次加载 < 2秒（桌面端，Chrome 浏览器，4G 网络）
- [x] 手动刷新 < 500ms（桌面端，Chrome 浏览器，4G 网络）
- [x] 并发用户数 ≥ 10（无性能下降）
- [x] 内存使用 < 256MB（Node.js 进程）

### 11.3 测试标准

- [x] 单元测试覆盖率 ≥ 80%
- [x] 集成测试覆盖所有 API 端点
- [x] E2E 测试覆盖主要用户流程
- [x] 性能测试通过（负载测试）

### 11.4 安全标准

- [x] XSS 防护（输入验证、CSP）
- [x] CORS 配置（白名单机制）
- [x] 路径遍历防护
- [x] 错误信息不泄露系统细节
- [x] 环境变量保护（.env 不提交）

### 11.5 兼容性标准

- [x] 浏览器支持：Chrome、Firefox、Safari、Edge（最新版本）
- [x] 响应式设计：桌面（> 1200px）、平板（768-1200px）、手机（< 768px）
- [x] 操作系统：Windows、macOS、Linux

### 11.6 实现优先级

**MVP（必须实现）**:
- [x] 基础布局（Header + 概览卡片）
- [x] API 服务器（6 个端点）
- [x] 数据加载和解析
- [x] 错误处理
- [x] 深色主题
- [x] 手动刷新功能

**V1.1（高优先级）**:
- [ ] 交易策略表格
- [ ] 一致性分析图
- [ ] 风险提示面板
- [ ] 技术指标图表
- [ ] 自动刷新功能
- [ ] 响应式设计

**V1.2（中优先级）**:
- [ ] 详细预测面板（点击卡片展开）
- [ ] 图表交互（悬停提示、点击过滤）
- [ ] 数据缓存机制
- [ ] 日志管理

**V2.0（低优先级）**:
- [ ] WebSocket 实时更新
- [ ] 用户自定义配置
- [ ] 数据导出功能
- [ ] 历史数据查看

## 12. 后续扩展

- [ ] 实时监控：自动刷新（5分钟）+ 手动刷新按钮
- [ ] 深色主题：专业交易员风格
- [ ] 数据可视化：Chart.js 图表
- [ ] 完整功能：6个货币对概览 + 交易策略对比 + 一致性分析 + 风险提示 + 技术指标
- [ ] 错误处理：完善的错误处理和降级策略
- [ ] 性能：首次加载 < 2秒，手动刷新 < 500ms
- [ ] 测试：单元测试 + 集成测试 + 性能测试

## 12. 后续扩展

### 12.1 短期扩展

- 添加货币对筛选功能
- 添加时间范围选择器
- 添加导出功能（CSV/Excel）
- 添加历史数据对比

### 12.2 长期扩展

- 集成实时数据源
- 添加用户认证
- 添加交易记录功能
- 添加回测功能

---

**设计完成日期**: 2026-03-26
**设计师**: iFlow CLI