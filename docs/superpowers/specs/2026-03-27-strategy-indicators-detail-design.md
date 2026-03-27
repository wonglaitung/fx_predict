# 交易策略技术指标详情设计文档

## 概述

为交易策略表格添加交互功能，点击表格行时在侧边栏显示该周期策略的关键技术指标详情。

## 背景

当前Dashboard的交易策略表格显示了各货币对的短线、中线、长线策略（入场价、止损、止盈、建议、置信度），但用户无法查看该策略基于哪些技术指标做出决策。

## 目标

- 点击交易策略表格的某一行，侧边栏打开并显示该周期策略的关键技术指标
- 支持在"大模型分析"和"技术指标详情"两个标签页之间切换
- 从35个技术指标中提取并显示6个关键类别的指标：支撑/阻力、趋势强度、动量信号、波动性、关键均线、信号

## 架构设计

### 交互流程

```
用户点击表格行
    ↓
前端调用 GET /api/v1/strategies/:pair/:horizon/indicators
    ↓
后端检查缓存（DataCache）
    ├─ 缓存命中 → 返回缓存数据
    └─ 缓存未命中 → 加载JSON文件 → 提取关键指标 → 缓存结果 → 返回
    ↓
前端接收JSON数据
    ↓
前端切换到"技术指标"标签页
    ↓
前端渲染6个指标卡片
    ↓
显示在侧边栏
```

### 组件关系

```
┌─────────────────────────────────────────────────────────────┐
│                        Dashboard                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐         ┌─────────────┐                   │
│  │  表格行点击  │────────▶│  API调用     │                   │
│  └─────────────┘         └─────────────┘                   │
│                                 │                            │
│                                 ▼                            │
│  ┌─────────────┐         ┌─────────────┐                   │
│  │  侧边栏     │◀────────│  后端处理   │                   │
│  │  (标签页)   │         └─────────────┘                   │
│  └─────────────┘                                       │    │
│         │                                             │    │
│         ▼                                             ▼    │
│  ┌─────────────┐         ┌─────────────┐                   │
│  │  大模型分析  │         │  技术指标   │                   │
│  │  (现有)     │         │  (新增)     │                   │
│  └─────────────┘         └─────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

## API设计

### 新端点：`GET /api/v1/strategies/:pair/:horizon/indicators`

#### 参数

- `pair`: 货币对代码（EUR, JPY, AUD, GBP, CAD, NZD）
- `horizon`: 周期（1, 5, 20）

#### 响应格式

```json
{
  "pair": "EUR",
  "pair_name": "欧元/美元",
  "horizon": 5,
  "horizon_name": "中线（5天）",
  "current_price": 1.1570,
  "key_indicators": {
    "support_resistance": {
      "bb_upper": 1.1625,
      "bb_middle": 1.1570,
      "bb_lower": 1.1515,
      "price_position": "中轨",
      "interpretation": "价格在中轨附近，波动正常"
    },
    "trend_strength": {
      "adx": 23.5,
      "trend": "无趋势",
      "ma_alignment": 0.3,
      "interpretation": "趋势较弱，均线排列不明显"
    },
    "momentum": {
      "rsi14": 45.3,
      "rsi_status": "中性",
      "macd": 0.0002,
      "macd_signal": 0.0001,
      "interpretation": "动量中性，无明显方向"
    },
    "volatility": {
      "atr14": 0.0231,
      "volatility_20d": 0.0200,
      "interpretation": "波动率中等"
    },
    "key_ma": {
      "sma5": 1.1568,
      "sma10": 1.1570,
      "sma20": 1.1572,
      "sma120": 1.1657,
      "interpretation": "短期均线接近，长期均线在上形成阻力"
    },
    "signals": {
      "williams_r": -45.2,
      "status": "中性",
      "cci20": -10.5,
      "interpretation": "无明显信号，观望为主"
    }
  },
  "overall_summary": "中线策略（5天）当前技术面中性偏多，价格在布林带中轨附近，ADX显示趋势较弱。RSI14为45.3处于中性区域，建议等待更明确的信号。"
}
```

#### 缓存策略

- 使用DataCache类，TTL 5分钟
- 缓存键：`strategy_indicators:${pair}:${horizon}`
- 文件上传时自动清除缓存

#### 错误处理

- 400：参数验证失败（无效的货币对或周期）
- 404：数据文件不存在
- 500：服务器内部错误

## 前端UI设计

### 侧边栏结构更新

```html
<!-- 侧边栏头部（添加标签页） -->
<div class="sidebar-header">
  <h2 class="sidebar-title">分析详情</h2>
  <div class="sidebar-tabs">
    <button class="tab-btn active" data-tab="llm">大模型分析</button>
    <button class="tab-btn" data-tab="indicators">技术指标</button>
  </div>
  <button id="closeSidebar" class="close-btn">&times;</button>
</div>

<!-- 侧边栏内容（添加两个标签页） -->
<div id="sidebarContent" class="sidebar-content">
  <div id="llmTab" class="tab-content active">
    <!-- 大模型分析内容（现有） -->
  </div>
  <div id="indicatorsTab" class="tab-content">
    <!-- 技术指标详情内容（新增） -->
  </div>
</div>
```

### 技术指标详情页面布局

```
┌─────────────────────────────────────┐
│  欧元/美元 - 中线（5天）            │
│  当前价格: 1.1570                  │
├─────────────────────────────────────┤
│  [整体摘要文本...]                  │
├─────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  │
│  │ 支撑/阻力    │  │ 趋势强度     │  │
│  │ • 布林带...  │  │ • ADX...    │  │
│  └─────────────┘  └─────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  │
│  │ 动量信号     │  │ 波动性       │  │
│  │ • RSI14...  │  │ • ATR14...  │  │
│  └─────────────┘  └─────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  │
│  │ 关键均线     │  │ 信号        │  │
│  │ • SMA5...   │  │ • Williams..│  │
│  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────┘
```

### 关键指标提取逻辑

#### 支撑/阻力

- 布林带上轨（BB_Upper）
- 布林带中轨（BB_Middle）
- 布林带下轨（BB_Lower）
- 价格位置（根据当前价格相对于布林带的位置判断）
- 解释说明

#### 趋势强度

- ADX（平均趋向指数）
- 趋势状态（ADX > 25为强势，< 20为弱势）
- 均线排列强度（MA_Alignment）
- 解释说明

#### 动量信号

- RSI14（相对强弱指标）
- RSI状态（> 70为超买，< 30为超卖）
- MACD
- MACD信号
- 解释说明

#### 波动性

- ATR14（平均真实波幅）
- 20日波动率（Volatility_20d）
- 解释说明

#### 关键均线

- SMA5、SMA10、SMA20、SMA120
- 解释说明

#### 信号

- Williams%R（威廉指标）
- Williams%R状态
- CCI20
- 解释说明

### CSS样式要点

- 标签页：`.sidebar-tabs`, `.tab-btn`, `.tab-content`
- 策略信息头部：`.strategy-indicators-header`, `.strategy-info`
- 整体摘要：`.overall-summary`
- 指标卡片网格：`.indicator-cards`（2列），`.indicator-card`
- 指标数值行：`.indicator-row`, `.indicator-row.highlight`（高亮关键行）
- 状态样式：`.value.status-超买`, `.value.status-超卖`, `.value.status-中性`等
- 卡片解释：`.card-interpretation`
- 响应式：移动端使用1列网格

### JavaScript功能

- `setupStrategyTableRowClick()`: 设置表格行点击事件
- `openStrategyIndicators(pair, horizon)`: 打开策略技术指标详情
- `switchTab(tabName)`: 切换标签页
- `renderStrategyIndicators(data)`: 渲染技术指标内容
- `renderIndicatorCard(title, indicators)`: 渲染单个指标卡片
- `formatIndicatorLabel(key)`: 格式化指标标签（英文→中文）

## 后端实现

### 新增函数

#### `extractKeyIndicators(indicators, strategy)`

从35个技术指标中提取关键指标，并添加解释说明。

**输入：**
- `indicators`: 完整的技术指标对象（6个类别）
- `strategy`: 该周期策略对象（包含entry_price等）

**输出：**
- 6个关键指标类别的结构化数据，每个包含数值和解释

#### `generateOverallSummary(pairName, horizon, indicators, strategy)`

生成整体摘要文本。

**输入：**
- `pairName`: 货币对名称
- `horizon`: 周期
- `indicators`: 关键指标
- `strategy`: 策略信息

**输出：**
- 整体摘要文本（中文化）

#### `getHorizonName(horizon)`

获取周期的中文名称。

**输入：**
- `horizon`: 周期（1, 5, 20）

**输出：**
- 周期中文名称（如"短线（1天）"）

### 缓存管理

- 使用现有的DataCache类
- 缓存键格式：`strategy_indicators:${pair}:${horizon}`
- TTL：5分钟（300秒）
- 文件上传时清除所有缓存

## 数据流

```
用户点击表格行（EUR/USD, 5天）
    ↓
前端调用 GET /api/v1/strategies/EUR/5/indicators
    ↓
后端检查缓存 strategy_indicators:EUR:5
    ├─ 缓存命中 → 返回缓存数据
    └─ 缓存未命中
        ↓
    加载 EUR_multi_horizon_*.json
        ↓
    提取 technical_indicators 和 trading_strategies
        ↓
    调用 extractKeyIndicators() 提取关键指标
        ↓
    调用 generateOverallSummary() 生成摘要
        ↓
    缓存结果
        ↓
    返回JSON
    ↓
前端接收数据
    ↓
前端调用 switchTab('indicators')
    ↓
前端调用 renderStrategyIndicators(data)
    ↓
侧边栏显示6个指标卡片
```

## 错误处理

### 前端错误处理

- API调用失败：显示alert提示"加载技术指标失败，请稍后重试"
- 数据格式错误：console.error记录错误详情
- 网络超时：显示加载状态，10秒后超时提示

### 后端错误处理

- 400 Bad Request：参数验证失败（无效的货币对或周期）
  ```json
  {
    "error": {
      "code": "INVALID_REQUEST",
      "message": "货币对代码无效",
      "details": "支持的货币对：EUR, JPY, AUD, GBP, CAD, NZD"
    }
  }
  ```

- 404 Not Found：数据文件不存在
  ```json
  {
    "error": {
      "code": "NOT_FOUND",
      "message": "数据未找到"
    }
  }
  ```

- 500 Internal Server Error：服务器内部错误
  ```json
  {
    "error": {
      "code": "INTERNAL_ERROR",
      "message": "服务器内部错误"
    }
  }
  ```

## 测试策略

### 单元测试

#### 后端函数测试

1. **`extractKeyIndicators`函数测试**
   - 测试正常情况：传入完整的技术指标和策略
   - 测试边界情况：某些指标为null或undefined
   - 验证输出结构：包含6个关键类别
   - 验证数值格式：小数点后位数正确

2. **`generateOverallSummary`函数测试**
   - 测试不同方向的摘要生成（buy/sell/hold）
   - 测试不同状态的摘要生成（超买/超卖/中性）
   - 验证输出文本：中文化正确，语法通顺

3. **缓存机制测试**
   - 测试首次请求：从数据文件加载
   - 测试缓存命中：第二次请求返回缓存数据
   - 测试缓存失效：5分钟后缓存过期

### 集成测试

1. **API端点测试**
   - 测试正常请求：返回正确的JSON结构
   - 测试参数验证：无效的货币对返回400
   - 测试参数验证：无效的周期返回400
   - 测试数据不存在：返回404

2. **前端渲染测试**
   - 测试侧边栏打开：侧边栏从右侧滑入
   - 测试标签页切换：大模型分析和技术指标标签正确切换
   - 测试指标卡片渲染：6个卡片正确显示
   - 测试高亮显示：关键行（价格位置、RSI14、SMA120、Williams%R）正确高亮

3. **交互测试**
   - 测试表格行点击：侧边栏打开并显示技术指标
   - 测试多次点击同一行：使用缓存，响应更快
   - 测试标签页切换：内容正确切换，状态保持

### 手动测试

1. **功能测试**
   - 点击每个货币对的每个周期策略行
   - 验证侧边栏正确打开
   - 验证技术指标正确显示
   - 验证标签页切换功能
   - 验证侧边栏关闭功能

2. **性能测试**
   - 测试首次加载时间（应< 500ms）
   - 测试缓存加载时间（应< 100ms）
   - 测试侧边栏打开动画流畅度

3. **兼容性测试**
   - 测试不同浏览器（Chrome, Firefox, Safari, Edge）
   - 测试不同分辨率（桌面、平板、手机）

## 文件变更清单

### 后端文件

#### `dashboard/server.js`

**新增内容：**
- 新API端点：`GET /api/v1/strategies/:pair/:horizon/indicators`
- 新函数：`extractKeyIndicators(indicators, strategy)`
- 新函数：`generateOverallSummary(pairName, horizon, indicators, strategy)`
- 新函数：`getHorizonName(horizon)`

**修改内容：**
- 文件上传端点：添加缓存清除逻辑（所有缓存）
- API端点文档打印：添加新端点信息

### 前端文件

#### `dashboard/public/index.html`

**修改内容：**
- 侧边栏头部：添加标签页按钮（`.sidebar-tabs`, `.tab-btn`）
- 侧边栏内容：添加两个标签内容区域（`#llmTab`, `#indicatorsTab`）

#### `dashboard/public/css/styles.css`

**新增样式：**
```css
/* 标签页 */
.sidebar-tabs { ... }
.tab-btn { ... }
.tab-btn.active { ... }
.tab-content { ... }
.tab-content.active { ... }

/* 策略信息头部 */
.strategy-indicators-header { ... }
.strategy-info h3 { ... }
.current-price { ... }

/* 整体摘要 */
.overall-summary { ... }

/* 指标卡片网格 */
.indicator-cards { ... }
.indicator-card { ... }
.indicator-card .card-title { ... }

/* 指标数值行 */
.indicator-row { ... }
.indicator-row.highlight { ... }
.indicator-row .label { ... }
.indicator-row .value { ... }

/* 状态样式 */
.value.status-超买 { ... }
.value.status-超卖 { ... }
.value.status-中性 { ... }
.value.status-强势 { ... }
.value.status-弱势 { ... }

/* 卡片解释 */
.card-interpretation { ... }

/* 响应式 */
@media (max-width: 768px) {
  .indicator-cards { ... }
}
```

#### `dashboard/public/js/components.js`

**新增函数：**
```javascript
function setupStrategyTableRowClick()
function openStrategyIndicators(pair, horizon)
function switchTab(tabName)
function renderStrategyIndicators(data)
function renderIndicatorCard(title, indicators)
function formatIndicatorLabel(key)
```

**修改函数：**
- `renderOverviewCards()`: 可能需要调整以支持表格行点击（如果需要的话）

#### `dashboard/public/js/app.js`

**修改内容：**
- 在初始化时调用 `setupStrategyTableRowClick()`

## 实施步骤

### 第一步：后端实现

1. 在`server.js`中添加新API端点
2. 实现`extractKeyIndicators`函数
3. 实现`generateOverallSummary`函数
4. 实现`getHorizonName`函数
5. 更新文件上传缓存清除逻辑
6. 更新API端点文档打印
7. 测试API端点

### 第二步：前端HTML结构更新

1. 更新侧边栏头部，添加标签页按钮
2. 更新侧边栏内容结构，添加两个标签内容区域
3. 测试HTML结构

### 第三步：前端CSS样式实现

1. 实现标签页样式
2. 实现策略信息头部样式
3. 实现整体摘要样式
4. 实现指标卡片网格样式
5. 实现指标数值行样式
6. 实现状态样式
7. 实现卡片解释样式
8. 实现响应式样式
9. 测试样式效果

### 第四步：前端JavaScript功能实现

1. 实现`setupStrategyTableRowClick`函数
2. 实现`openStrategyIndicators`函数
3. 实现`switchTab`函数
4. 实现`renderStrategyIndicators`函数
5. 实现`renderIndicatorCard`函数
6. 实现`formatIndicatorLabel`函数
7. 在`app.js`中调用初始化函数
8. 测试交互功能

### 第五步：集成测试

1. 测试完整流程（点击表格行 → 侧边栏打开 → 显示指标）
2. 测试标签页切换
3. 测试缓存机制
4. 测试错误处理
5. 测试响应式布局

### 第六步：文档更新

1. 更新README.md，添加新功能说明
2. 更新AGENTS.md，添加API端点文档
3. 更新progress.txt，记录完成进度

## 预期效果

### 用户体验

1. 点击交易策略表格的某一行，侧边栏立即打开
2. 侧边栏显示"大模型分析"和"技术指标"两个标签页
3. 默认显示"技术指标"标签页（因为是点击表格行打开的）
4. 用户可以在两个标签页之间切换
5. 技术指标详情页面显示6个卡片，每个卡片包含关键指标和解释

### 性能

1. 首次加载时间：< 500ms（API调用 + 渲染）
2. 缓存加载时间：< 100ms
3. 侧边栏打开动画流畅（< 300ms）

### 可维护性

1. 代码结构清晰，职责分明
2. 函数命名规范，易于理解
3. 注释完整，便于维护
4. 测试覆盖充分

## 风险和限制

### 技术风险

1. **数据源依赖**：技术指标数据来源于预测文件，如果预测文件格式变化，需要同步更新代码
2. **缓存一致性**：文件上传后需要清除缓存，否则可能显示旧数据
3. **侧边栏宽度限制**：500px宽度可能限制信息的展示，需要优化布局

### 设计限制

1. **关键指标选择**：从35个指标中选择了6个类别，可能无法满足所有用户的需求
2. **解释说明生成**：基于简单的规则生成解释，可能不够准确或详细
3. **实时性**：缓存时间为5分钟，可能不是最新数据

## 未来改进

1. **自定义指标选择**：允许用户自定义显示哪些指标
2. **图表可视化**：为关键指标添加图表（如RSI历史走势）
3. **实时更新**：使用WebSocket实现实时数据更新
4. **导出功能**：允许用户导出技术指标详情为PDF或Excel
5. **对比功能**：支持多个货币对的技术指标对比