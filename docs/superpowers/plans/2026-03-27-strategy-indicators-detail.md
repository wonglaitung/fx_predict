# 交易策略技术指标详情实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为交易策略表格添加交互功能，点击表格行时在侧边栏显示该周期策略的关键技术指标详情

**Architecture:** 新增后端API端点提取关键技术指标，前端使用标签页侧边栏展示，支持卡片点击和表格行点击两种触发方式

**Tech Stack:** Node.js/Express (后端), 原生JavaScript/CSS (前端), DataCache (缓存)

---

## 文件结构

### 后端文件
- **Modify:** `dashboard/server.js`
  - 新增API端点：`GET /api/v1/strategies/:pair/:horizon/indicators`
  - 新增函数：`extractKeyIndicators()` - 从35个指标中提取6个关键类别
  - 新增函数：`generateOverallSummary()` - 生成整体摘要
  - 新增函数：`getHorizonName()` - 获取周期中文名
  - 修改：文件上传端点 - 添加`strategy_indicators`缓存清除

### 前端文件
- **Modify:** `dashboard/public/index.html`
  - 修改侧边栏头部 - 添加标签页按钮
  - 修改侧边栏内容 - 添加两个标签内容区域

- **Modify:** `dashboard/public/css/styles.css`
  - 新增：标签页样式（`.sidebar-tabs`, `.tab-btn`, `.tab-content`）
  - 新增：策略信息头部样式（`.strategy-indicators-header`）
  - 新增：整体摘要样式（`.overall-summary`）
  - 新增：指标卡片网格样式（`.indicator-cards`, `.indicator-card`）
  - 新增：指标数值行样式（`.indicator-row`, `.indicator-row.highlight`）
  - 新增：状态样式（`.value.status-超买`等）
  - 新增：卡片解释样式（`.card-interpretation`）
  - 新增：加载指示器样式（`.loader`）
  - 新增：响应式样式

- **Modify:** `dashboard/public/js/components.js`
  - 新增：全局状态变量（`currentSidebarTrigger`, `currentSidebarData`, `currentActiveTab`）
  - 新增：`setupStrategyTableRowClick()` - 设置表格行点击事件
  - 新增：`openStrategyIndicators(pair, horizon)` - 打开策略技术指标详情
  - 新增：`openSidebar(trigger, data)` - 统一的侧边栏打开函数
  - 新增：`updateSidebarState(trigger, data, defaultTab)` - 更新侧边栏状态
  - 新增：`switchTab(tabName)` - 切换标签页
  - 新增：`renderStrategyIndicators(data)` - 渲染技术指标内容
  - 新增：`renderIndicatorCard(title, indicators)` - 渲染单个指标卡片
  - 新增：`formatIndicatorLabel(key)` - 格式化指标标签
  - 新增：`showLoadingState()` - 显示加载状态
  - 新增：`hideLoadingState()` - 隐藏加载状态
  - 修改：`openAnalysisSidebar(pair)` - 改为调用`openSidebar('card', pair)`

- **Modify:** `dashboard/public/js/app.js`
  - 新增：在初始化时调用`setupStrategyTableRowClick()`

---

## Task 1: 后端 - 新增API端点和辅助函数

**Files:**
- Modify: `dashboard/server.js`

- [ ] **Step 1: 在server.js中添加新的API端点**

在文件末尾的app.get端点列表中添加：

```javascript
// Get strategy indicators for a specific pair and horizon
app.get('/api/v1/strategies/:pair/:horizon/indicators', (req, res) => {
  try {
    const { pair, horizon } = req.params;
    const validPairs = ['EUR', 'JPY', 'AUD', 'GBP', 'CAD', 'NZD'];
    const validHorizons = ['1', '5', '20'];
    
    // Validate parameters
    if (!validPairs.includes(pair)) {
      return res.status(400).json({
        error: {
          code: 'INVALID_REQUEST',
          message: '货币对代码无效',
          details: '支持的货币对：EUR, JPY, AUD, GBP, CAD, NZD'
        }
      });
    }
    
    if (!validHorizons.includes(horizon)) {
      return res.status(400).json({
        error: {
          code: 'INVALID_REQUEST',
          message: '周期参数无效',
          details: '支持的周期：1, 5, 20'
        }
      });
    }
    
    // Check cache
    const cacheKey = `strategy_indicators:${pair}:${horizon}`;
    const cached = dataCache.get(cacheKey);
    if (cached) {
      return res.json(cached);
    }
    
    // Load data
    const data = dataLoader.loadPair(pair);
    
    // Get technical indicators and trading strategies
    const indicators = data.technical_indicators || {};
    const metadata = data.metadata || {};
    const strategies = data.trading_strategies || {};
    
    // Get strategy for the horizon
    const strategyMap = {
      '1': strategies.short_term,
      '5': strategies.medium_term,
      '20': strategies.long_term
    };
    const strategy = strategyMap[horizon] || {};
    
    // Extract key indicators
    const keyIndicators = extractKeyIndicators(indicators, strategy);
    
    // Generate overall summary
    const overallSummary = generateOverallSummary(
      metadata.pair_name,
      horizon,
      keyIndicators,
      strategy
    );
    
    const response = {
      pair: metadata.pair,
      pair_name: metadata.pair_name,
      horizon: parseInt(horizon),
      horizon_name: getHorizonName(horizon),
      current_price: metadata.current_price,
      key_indicators: keyIndicators,
      overall_summary: overallSummary
    };
    
    // Cache the result
    dataCache.set(cacheKey, response);
    
    res.json(response);
  } catch (error) {
    logError(`Failed to load strategy indicators for ${pair}/${horizon}: ${error.message}`);
    
    if (error.message.includes('No data found')) {
      return res.status(404).json({
        error: {
          code: 'NOT_FOUND',
          message: '数据未找到'
        }
      });
    }
    
    res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: '服务器内部错误'
      }
    });
  }
});
```

- [ ] **Step 2: 添加extractKeyIndicators函数**

在DataLoader类定义之后添加：

```javascript
// Extract key indicators from full technical indicators
function extractKeyIndicators(indicators, strategy) {
  const trend = indicators.trend || {};
  const momentum = indicators.momentum || {};
  const volatility = indicators.volatility || {};
  const pricePattern = indicators.price_pattern || {};
  const marketEnvironment = indicators.market_environment || {};
  
  const currentPrice = strategy.entry_price || 0;
  
  // Calculate price position in Bollinger Bands
  const bbUpper = trend.BB_Upper || 0;
  const bbMiddle = trend.BB_Middle || 0;
  const bbLower = trend.BB_Lower || 0;
  let pricePosition = '未知';
  if (currentPrice > bbUpper) pricePosition = '上轨之上';
  else if (currentPrice < bbLower) pricePosition = '下轨之下';
  else pricePosition = '中轨附近';
  
  // Determine RSI status
  const rsi14 = momentum.RSI14 || 50;
  let rsiStatus = '中性';
  if (rsi14 > 70) rsiStatus = '超买';
  else if (rsi14 < 30) rsiStatus = '超卖';
  
  // Determine trend status
  const adx = trend.ADX || 0;
  let trendStatus = '无趋势';
  if (adx > 25) trendStatus = '强势';
  else if (adx < 20) trendStatus = '弱势';
  
  // Determine Williams%R status
  const williamsR = momentum.Williams_R_14 || -50;
  let williamsStatus = '中性';
  if (williamsR > -20) williamsStatus = '超买';
  else if (williamsR < -80) williamsStatus = '超卖';
  
  return {
    support_resistance: {
      bb_upper: bbUpper,
      bb_middle: bbMiddle,
      bb_lower: bbLower,
      price_position: pricePosition,
      interpretation: `价格${pricePosition === '中轨附近' ? '在中轨附近' : pricePosition === '上轨之上' ? '突破上轨，可能回调' : '跌破下轨，可能反弹'}，布林带宽度正常。`
    },
    trend_strength: {
      adx: adx.toFixed(2),
      trend: trendStatus,
      ma_alignment: marketEnvironment.MA_Alignment || 0,
      interpretation: trendStatus === '强势' ? 'ADX显示趋势强劲，适合趋势交易。' : 
                     trendStatus === '弱势' ? 'ADX显示趋势较弱，适合区间交易。' : 
                     'ADX显示无明显趋势，建议观望。'
    },
    momentum: {
      rsi14: rsi14.toFixed(1),
      rsi_status: rsiStatus,
      macd: trend.MACD?.toFixed(6) || 0,
      macd_signal: trend.MACD_Signal?.toFixed(6) || 0,
      interpretation: rsiStatus === '超买' ? 'RSI超买，可能回调。' :
                     rsiStatus === '超卖' ? 'RSI超卖，可能反弹。' :
                     'RSI中性，等待更明确信号。'
    },
    volatility: {
      atr14: volatility.ATR14?.toFixed(4) || 0,
      volatility_20d: volatility.Volatility_20d?.toFixed(4) || 0,
      interpretation: volatility.Volatility_20d > 0.02 ? '波动率较高，注意风险。' : '波动率正常。'
    },
    key_ma: {
      sma5: trend.SMA5?.toFixed(4) || 0,
      sma10: trend.SMA10?.toFixed(4) || 0,
      sma20: trend.SMA20?.toFixed(4) || 0,
      sma120: trend.SMA120?.toFixed(4) || 0,
      interpretation: `${trend.SMA120 > currentPrice ? 'SMA120在上形成阻力' : 'SMA120在下形成支撑'}，短期均线${trend.SMA5 > trend.SMA20 ? '多头排列' : '空头排列'}。`
    },
    signals: {
      williams_r: williamsR.toFixed(1),
      status: williamsStatus,
      cci20: momentum.CCI20?.toFixed(1) || 0,
      interpretation: williamsStatus === '超买' ? 'Williams%R超买信号。' :
                     williamsStatus === '超卖' ? 'Williams%R超卖信号。' :
                     'Williams%R中性，无明确信号。'
    }
  };
}
```

- [ ] **Step 3: 添加generateOverallSummary函数**

在extractKeyIndicators函数之后添加：

```javascript
// Generate overall summary text
function generateOverallSummary(pairName, horizon, indicators, strategy) {
  const horizonName = getHorizonName(horizon);
  const direction = strategy.direction || 'hold';
  const directionText = direction === 'buy' ? '偏多' : direction === 'sell' ? '偏空' : '中性';
  
  const trendStrength = indicators.trend_strength.trend;
  const rsiStatus = indicators.momentum.rsi_status;
  const pricePosition = indicators.support_resistance.price_position;
  
  return `${pairName}${horizonName}当前技术面${directionText}，价格${pricePosition}，ADX显示${trendStrength}。RSI14为${indicators.momentum.rsi14}处于${rsiStatus}区域，建议${rsiStatus === '中性' ? '等待更明确的信号' : '注意可能的反转信号'}。`;
}
```

- [ ] **Step 4: 添加getHorizonName函数**

在generateOverallSummary函数之后添加：

```javascript
// Get Chinese name for horizon
function getHorizonName(horizon) {
  const names = {
    '1': '短线（1天）',
    '5': '中线（5天）',
    '20': '长线（20天）'
  };
  return names[horizon] || `${horizon}天`;
}
```

- [ ] **Step 5: 修改文件上传端点，添加strategy_indicators缓存清除**

找到文件上传端点（`app.post('/api/v1/upload'...`），在`dataCache.clear();`之后添加：

```javascript
// Clear all caches including strategy_indicators
dataCache.clearByPattern('strategy_indicators:');
```

- [ ] **Step 6: 更新API端点文档打印**

找到打印API端点信息的代码块，在`apiEndpoints`数组中添加：

```javascript
{
  method: 'GET',
  path: '/api/v1/strategies/:pair/:horizon/indicators',
  description: '获取指定货币对和周期的关键技术指标',
  params: [
    { name: 'pair', type: 'string', description: '货币对代码 (EUR, JPY, AUD, GBP, CAD, NZD)' },
    { name: 'horizon', type: 'string', description: '预测周期 (1, 5, 20)' }
  ],
  response: '{ pair, pair_name, horizon, horizon_name, current_price, key_indicators, overall_summary }'
},
```

- [ ] **Step 7: 测试API端点**

重启Dashboard服务器，测试新端点：

```bash
cd /data/fx_predict/dashboard
npm start
```

在另一个终端测试：

```bash
# 测试正常请求
curl http://localhost:3000/api/v1/strategies/EUR/5/indicators

# 测试无效货币对
curl http://localhost:3000/api/v1/strategies/XXX/5/indicators

# 测试无效周期
curl http://localhost:3000/api/v1/strategies/EUR/99/indicators
```

预期：
- 正常请求返回JSON数据包含6个关键指标类别
- 无效货币对返回400错误
- 无效周期返回400错误

- [ ] **Step 8: 提交后端更改**

```bash
git add dashboard/server.js
git commit -m "feat: add API endpoint for strategy indicators detail

- Add GET /api/v1/strategies/:pair/:horizon/indicators endpoint
- Add extractKeyIndicators() function to extract 6 key indicator categories
- Add generateOverallSummary() function to generate summary text
- Add getHorizonName() function for Chinese horizon names
- Update file upload handler to clear strategy_indicators cache
- Update API documentation on server startup"
```

---

## Task 2: 前端 - 更新侧边栏HTML结构

**Files:**
- Modify: `dashboard/public/index.html`

- [ ] **Step 1: 备份并修改侧边栏头部**

找到`<div id="analysisSidebar" class="sidebar">`块，修改头部部分：

```html
<!-- 原代码 -->
<div class="sidebar-header">
  <h2 class="sidebar-title">大模型分析详情</h2>
  <button id="closeSidebar" class="close-btn">&times;</button>
</div>

<!-- 修改为 -->
<div class="sidebar-header">
  <h2 class="sidebar-title" id="sidebarTitle">大模型分析详情</h2>
  <div class="sidebar-tabs" id="sidebarTabs">
    <button class="tab-btn" data-tab="llm">大模型分析</button>
    <button class="tab-btn" data-tab="indicators">技术指标</button>
  </div>
  <button id="closeSidebar" class="close-btn">&times;</button>
</div>
```

- [ ] **Step 2: 修改侧边栏内容区域**

找到`<div id="sidebarContent" class="sidebar-content">`块，修改内容：

```html
<!-- 原代码 -->
<div id="sidebarContent" class="sidebar-content">
  <!-- Content will be populated by JavaScript -->
</div>

<!-- 修改为 -->
<div id="sidebarContent" class="sidebar-content">
  <div id="llmTab" class="tab-content">
    <!-- 大模型分析内容（现有，由JS填充） -->
  </div>
  <div id="indicatorsTab" class="tab-content">
    <!-- 技术指标详情内容（新增，由JS填充） -->
  </div>
</div>
```

- [ ] **Step 3: 提交HTML更改**

```bash
git add dashboard/public/index.html
git commit -m "feat: add tab-based sidebar structure for analysis

- Add sidebar tabs (大模型分析 and 技术指标)
- Add dynamic sidebar title element
- Split sidebar content into two tab areas
- Support both LLM analysis and technical indicators in sidebar"
```

---

## Task 3: 前端 - 添加标签页CSS样式

**Files:**
- Modify: `dashboard/public/css/styles.css`

- [ ] **Step 1: 添加标签页样式**

在`.close-btn`样式之后添加：

```css
/* Sidebar Tabs */
.sidebar-tabs {
  display: none; /* Initially hidden, shown for strategy trigger */
  flex-direction: row;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.tab-btn {
  flex: 1;
  padding: 0.5rem 0.75rem;
  background-color: var(--bg-primary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.tab-btn:hover {
  border-color: var(--color-info);
  color: var(--text-primary);
}

.tab-btn.active {
  background-color: var(--color-info);
  color: white;
  border-color: var(--color-info);
}

.tab-content {
  display: none;
}

.tab-content.active {
  display: block;
}
```

- [ ] **Step 2: 添加策略信息头部样式**

在`.sidebar-list-item::before`样式之后添加：

```css
/* Strategy Indicators Header */
.strategy-indicators-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.strategy-info h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.current-price {
  font-size: 0.875rem;
  color: var(--text-secondary);
}
```

- [ ] **Step 3: 添加整体摘要样式**

在`.current-price`样式之后添加：

```css
/* Overall Summary */
.overall-summary {
  background-color: var(--bg-primary);
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
  line-height: 1.6;
  color: var(--text-secondary);
  font-size: 0.875rem;
}
```

- [ ] **Step 4: 添加指标卡片网格样式**

在`.overall-summary`样式之后添加：

```css
/* Indicator Cards */
.indicator-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.indicator-card {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1rem;
}

.indicator-card .card-title {
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--text-primary);
}

.indicator-values {
  margin-bottom: 0.5rem;
}

.indicator-row {
  display: flex;
  justify-content: space-between;
  padding: 0.25rem 0;
  font-size: 0.8rem;
}

.indicator-row.highlight {
  background-color: rgba(59, 130, 246, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  margin: 0.25rem -0.5rem;
}

.indicator-row .label {
  color: var(--text-secondary);
}

.indicator-row .value {
  color: var(--text-primary);
  font-family: 'Roboto Mono', monospace;
}
```

- [ ] **Step 5: 添加状态样式**

在`.indicator-row .value`样式之后添加：

```css
/* Status Styles */
.value.status-超买 {
  color: var(--color-danger);
}

.value.status-超卖 {
  color: var(--color-success);
}

.value.status-中性 {
  color: var(--text-secondary);
}

.value.status-强势 {
  color: var(--color-success);
}

.value.status-弱势 {
  color: var(--color-danger);
}
```

- [ ] **Step 6: 添加卡片解释样式**

在`.value.status-弱势`样式之后添加：

```css
/* Card Interpretation */
.card-interpretation {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-color);
  font-size: 0.75rem;
  color: var(--text-secondary);
  line-height: 1.5;
}
```

- [ ] **Step 7: 添加加载指示器样式**

在`.card-interpretation`样式之后添加：

```css
/* Loading Indicator */
.loader {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top-color: var(--color-info);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 0.5rem;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

- [ ] **Step 8: 添加响应式样式**

在`.card-hint`样式之后添加：

```css
/* Responsive Design for Indicator Cards */
@media (max-width: 768px) {
  .indicator-cards {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 9: 测试CSS样式**

硬刷新浏览器（Ctrl+Shift+R），检查：

1. 侧边栏标签页按钮正确显示
2. 标签页切换动画流畅
3. 加载指示器旋转动画正常
4. 移动端（<768px）指标卡片单列显示

- [ ] **Step 10: 提交CSS更改**

```bash
git add dashboard/public/css/styles.css
git commit -m "feat: add styles for sidebar tabs and indicator cards

- Add tab button and content styles with active states
- Add strategy indicators header and overall summary styles
- Add indicator card grid layout (2 columns, 1 on mobile)
- Add indicator row styles with highlight for key values
- Add status color styles (超买/超卖/中性/强势/弱势)
- Add card interpretation and loading indicator styles
- Add responsive design for mobile devices"
```

---

## Task 4: 前端 - 添加JavaScript功能（表格行点击）

**Files:**
- Modify: `dashboard/public/js/components.js`

- [ ] **Step 1: 添加全局状态变量**

在文件开头添加：

```javascript
// Global sidebar state
let currentSidebarTrigger = null; // 'card' | 'strategy'
let currentSidebarData = null;    // Current sidebar data
let currentActiveTab = null;      // 'llm' | 'indicators'
```

- [ ] **Step 2: 添加setupStrategyTableRowClick函数**

在`renderOverviewCards`函数之后添加：

```javascript
// Setup click handlers for strategy table rows
function setupStrategyTableRowClick() {
  const tableRows = document.querySelectorAll('#strategiesTable tbody tr');
  
  tableRows.forEach(row => {
    // Set cursor style
    row.style.cursor = 'pointer';
    
    // Add hover effect
    row.addEventListener('mouseenter', () => {
      row.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
    });
    
    row.addEventListener('mouseleave', () => {
      row.style.backgroundColor = '';
    });
    
    // Add click event
    row.addEventListener('click', async (event) => {
      event.preventDefault();
      event.stopPropagation();
      
      // Extract data from row attributes
      const pair = row.getAttribute('data-pair');
      const horizon = row.getAttribute('data-horizon');
      
      if (!pair || !horizon) {
        console.error('Missing pair or horizon in table row');
        return;
      }
      
      // Show loading state
      showLoadingState();
      
      try {
        // Load strategy indicators data
        const response = await fetch(`/api/v1/strategies/${pair}/${horizon}/indicators`);
        if (!response.ok) {
          throw new Error(`Failed to load indicators: ${response.status}`);
        }
        const data = await response.json();
        
        // Open sidebar with strategy trigger
        openSidebar('strategy', data);
        
      } catch (error) {
        console.error('Error loading strategy indicators:', error);
        hideLoadingState();
        alert('加载技术指标失败，请稍后重试');
      }
    });
  });
}
```

- [ ] **Step 3: 添加openStrategyIndicators函数**

在`setupStrategyTableRowClick`函数之后添加：

```javascript
// Open strategy indicators in sidebar
async function openStrategyIndicators(pair, horizon) {
  showLoadingState();
  
  try {
    const response = await fetch(`/api/v1/strategies/${pair}/${horizon}/indicators`);
    if (!response.ok) {
      throw new Error(`Failed to load indicators: ${response.status}`);
    }
    const data = await response.json();
    
    openSidebar('strategy', data);
    
  } catch (error) {
    console.error('Error loading strategy indicators:', error);
    hideLoadingState();
    alert('加载技术指标失败，请稍后重试');
  }
}
```

- [ ] **Step 4: 添加showLoadingState函数**

在`openStrategyIndicators`函数之后添加：

```javascript
// Show loading state in sidebar
function showLoadingState() {
  const sidebar = document.getElementById('analysisSidebar');
  
  // Create loader element
  const loader = document.createElement('div');
  loader.id = 'sidebarLoader';
  loader.innerHTML = '<div class="loader"></div><p>加载中...</p>';
  loader.style.cssText = `
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    color: var(--text-secondary);
    z-index: 10;
  `;
  
  sidebar.appendChild(loader);
}
```

- [ ] **Step 5: 添加hideLoadingState函数**

在`showLoadingState`函数之后添加：

```javascript
// Hide loading state in sidebar
function hideLoadingState() {
  const loader = document.getElementById('sidebarLoader');
  if (loader) {
    loader.remove();
  }
}
```

- [ ] **Step 6: 提交表格行点击功能**

```bash
git add dashboard/public/js/components.js
git commit -m "feat: add table row click for strategy indicators

- Add global sidebar state variables (trigger, data, active tab)
- Add setupStrategyTableRowClick() for table row click handlers
- Add openStrategyIndicators() to load and display indicators
- Add showLoadingState() and hideLoadingState() for UX
- Add hover effect for table rows"
```

---

## Task 5: 前端 - 添加侧边栏状态管理和标签页切换

**Files:**
- Modify: `dashboard/public/js/components.js`

- [ ] **Step 1: 添加openSidebar函数（统一打开函数）**

在`hideLoadingState`函数之后添加：

```javascript
// Unified function to open sidebar
function openSidebar(trigger, data) {
  // Update global state
  currentSidebarTrigger = trigger;
  currentSidebarData = data;
  
  // Determine default tab based on trigger
  const defaultTab = trigger === 'strategy' ? 'indicators' : 'llm';
  currentActiveTab = defaultTab;
  
  // Update sidebar title
  const titleElement = document.getElementById('sidebarTitle');
  if (trigger === 'strategy') {
    titleElement.textContent = `${data.pair_name} - ${data.horizon_name}`;
  } else {
    titleElement.textContent = '大模型分析详情';
  }
  
  // Render content based on trigger
  if (trigger === 'strategy') {
    renderStrategyIndicators(data);
  } else {
    renderSidebarContent(data);
  }
  
  // Switch to default tab
  switchTab(defaultTab);
  
  // Show sidebar
  document.getElementById('analysisSidebar').classList.add('sidebar-open');
  document.getElementById('sidebarOverlay').classList.add('sidebar-overlay-open');
  
  // Hide loading state
  hideLoadingState();
}
```

- [ ] **Step 2: 修改openAnalysisSidebar函数**

找到现有的`openAnalysisSidebar`函数，修改为：

```javascript
// Original function - modify to call openSidebar
function openAnalysisSidebar(pair) {
  // Load pair data
  const pairs = window.pairsData || [];
  const pairData = pairs.find(p => p.pair === pair);
  
  if (!pairData) {
    console.error('Pair data not found:', pair);
    return;
  }
  
  // Open sidebar with card trigger
  openSidebar('card', pairData);
}
```

- [ ] **Step 3: 添加switchTab函数**

在`openSidebar`函数之后添加：

```javascript
// Switch between sidebar tabs
function switchTab(tabName) {
  // Update current active tab
  currentActiveTab = tabName;
  
  // Update tab button states
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.getAttribute('data-tab') === tabName) {
      btn.classList.add('active');
    }
  });
  
  // Update tab content visibility
  document.querySelectorAll('.tab-content').forEach(content => {
    content.classList.remove('active');
  });
  
  const activeTab = document.getElementById(`${tabName}Tab`);
  if (activeTab) {
    activeTab.classList.add('active');
  }
  
  // Show/hide tabs based on trigger
  const tabsElement = document.getElementById('sidebarTabs');
  if (currentSidebarTrigger === 'strategy') {
    tabsElement.style.display = 'flex';
  } else {
    tabsElement.style.display = 'none';
  }
}
```

- [ ] **Step 4: 添加renderStrategyIndicators函数**

在`switchTab`函数之后添加：

```javascript
// Render strategy indicators content
function renderStrategyIndicators(data) {
  const container = document.getElementById('indicatorsTab');
  
  if (!container) {
    console.error('indicatorsTab not found');
    return;
  }
  
  container.innerHTML = `
    <div class="strategy-indicators-header">
      <div class="strategy-info">
        <h3>${data.pair_name} - ${data.horizon_name}</h3>
        <p class="current-price">当前价格: ${data.current_price.toFixed(4)}</p>
      </div>
    </div>
    
    <div class="overall-summary">
      <p>${data.overall_summary}</p>
    </div>
    
    <div class="indicator-cards">
      ${renderIndicatorCard('支撑/阻力', data.key_indicators.support_resistance)}
      ${renderIndicatorCard('趋势强度', data.key_indicators.trend_strength)}
      ${renderIndicatorCard('动量信号', data.key_indicators.momentum)}
      ${renderIndicatorCard('波动性', data.key_indicators.volatility)}
      ${renderIndicatorCard('关键均线', data.key_indicators.key_ma)}
      ${renderIndicatorCard('信号', data.key_indicators.signals)}
    </div>
  `;
}
```

- [ ] **Step 5: 添加renderIndicatorCard函数**

在`renderStrategyIndicators`函数之后添加：

```javascript
// Render a single indicator card
function renderIndicatorCard(title, indicators) {
  const indicatorRows = Object.entries(indicators)
    .filter(([key, value]) => typeof value === 'number' || typeof value === 'string')
    .map(([key, value]) => {
      const label = formatIndicatorLabel(key);
      const isHighlight = ['price_position', 'rsi14', 'sma120', 'williams_r'].includes(key);
      const statusClass = typeof indicators.status === 'string' ? `status-${indicators.status}` : '';
      
      return `
        <div class="indicator-row ${isHighlight ? 'highlight' : ''}">
          <span class="label">${label}</span>
          <span class="value ${statusClass}">${value}</span>
        </div>
      `;
    }).join('');
  
  const interpretation = indicators.interpretation || '';
  
  return `
    <div class="indicator-card">
      <h4 class="card-title">${title}</h4>
      <div class="indicator-values">
        ${indicatorRows}
      </div>
      ${interpretation ? `<p class="card-interpretation">${interpretation}</p>` : ''}
    </div>
  `;
}
```

- [ ] **Step 6: 添加formatIndicatorLabel函数**

在`renderIndicatorCard`函数之后添加：

```javascript
// Format indicator label (English to Chinese)
function formatIndicatorLabel(key) {
  const labels = {
    'bb_upper': '布林带上轨',
    'bb_middle': '布林带中轨',
    'bb_lower': '布林带下轨',
    'price_position': '价格位置',
    'adx': 'ADX',
    'trend': '趋势状态',
    'ma_alignment': '均线排列',
    'rsi14': 'RSI14',
    'rsi_status': 'RSI状态',
    'macd': 'MACD',
    'macd_signal': 'MACD信号',
    'atr14': 'ATR14',
    'volatility_20d': '20日波动率',
    'sma5': 'SMA5',
    'sma10': 'SMA10',
    'sma20': 'SMA20',
    'sma120': 'SMA120',
    'williams_r': 'Williams%R',
    'status': '状态',
    'cci20': 'CCI20'
  };
  return labels[key] || key;
}
```

- [ ] **Step 7: 添加标签页点击事件监听器**

在`formatIndicatorLabel`函数之后添加：

```javascript
// Setup tab click event listeners
document.addEventListener('DOMContentLoaded', () => {
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabName = btn.getAttribute('data-tab');
      switchTab(tabName);
    });
  });
});
```

- [ ] **Step 8: 提交侧边栏状态管理和标签页功能**

```bash
git add dashboard/public/js/components.js
git commit -m "feat: add sidebar state management and tab switching

- Add openSidebar() unified function for sidebar opening
- Modify openAnalysisSidebar() to use openSidebar()
- Add switchTab() for tab switching logic
- Add renderStrategyIndicators() for rendering indicators
- Add renderIndicatorCard() for rendering single cards
- Add formatIndicatorLabel() for label formatting
- Add tab click event listeners
- Support both card and strategy triggers with different default tabs"
```

---

## Task 6: 前端 - 在app.js中初始化表格行点击

**Files:**
- Modify: `dashboard/public/js/app.js`

- [ ] **Step 1: 找到初始化代码**

找到`DOMContentLoaded`事件监听器或`init()`函数。

- [ ] **Step 2: 添加setupStrategyTableRowClick调用**

在现有初始化代码后添加：

```javascript
// Setup strategy table row clicks
if (typeof setupStrategyTableRowClick === 'function') {
  setupStrategyTableRowClick();
}
```

- [ ] **Step 3: 测试完整流程**

1. 重启Dashboard服务器
2. 硬刷新浏览器
3. 点击交易策略表格的某一行
4. 验证：
   - 侧边栏打开
   - 显示"技术指标"标签页
   - 显示6个指标卡片
   - 数据正确显示

- [ ] **Step 4: 提交app.js更改**

```bash
git add dashboard/public/js/app.js
git commit -m "feat: initialize strategy table row clicks on app load

- Call setupStrategyTableRowClick() on DOMContentLoaded
- Ensure table row click handlers are registered on page load"
```

---

## Task 7: 集成测试和文档更新

- [ ] **Step 1: 运行完整测试流程**

手动测试以下场景：

1. **卡片点击触发侧边栏**
   - 点击概览卡片
   - 验证显示"大模型分析"标签页
   - 验证标签页按钮隐藏

2. **表格行点击触发侧边栏**
   - 点击交易策略表格行
   - 验证显示"技术指标"标签页
   - 验证标签页按钮显示
   - 验证6个指标卡片正确显示

3. **标签页切换**
   - 在技术指标模式下点击"大模型分析"标签
   - 验证内容切换
   - 在大模型分析模式下点击"技术指标"标签
   - 验证内容切换（如果有数据）

4. **缓存机制**
   - 点击同一行两次
   - 第二次应该更快（使用缓存）

5. **错误处理**
   - 检查浏览器控制台无错误
   - 检查服务器日志无错误

- [ ] **Step 2: 更新API端点文档**

在`AGENTS.md`中找到Dashboard API端点列表，在文件上传端点之后添加：

```markdown
- `GET /api/v1/strategies/:pair/:horizon/indicators`
  - 描述：获取指定货币对和周期的关键技术指标
  - 参数：
    - pair（货币对代码）：EUR, JPY, AUD, GBP, CAD, NZD
    - horizon（预测周期）：1, 5, 20
  - 响应：{ pair, pair_name, horizon, horizon_name, current_price, key_indicators, overall_summary }
```

- [ ] **Step 3: 更新README.md**

在Dashboard功能章节中添加：

```markdown
### 交易策略交互
- 点击交易策略表格的某一行，侧边栏显示该周期策略的关键技术指标
- 技术指标包括：支撑/阻力、趋势强度、动量信号、波动性、关键均线、信号
- 支持在"大模型分析"和"技术指标"两个标签页之间切换
```

- [ ] **Step 4: 提交文档更新**

```bash
git add AGENTS.md README.md
git commit -m "docs: update documentation for strategy indicators feature

- Add new API endpoint documentation to AGENTS.md
- Update README.md with strategy indicators interaction description"
```

---

## Task 8: 最终验证和推送

- [ ] **Step 1: 运行Dashboard测试**

确保所有功能正常工作：

```bash
cd /data/fx_predict/dashboard
npm start
```

测试清单：
- [ ] 概览卡片点击正常
- [ ] 交易策略表格行点击正常
- [ ] 侧边栏标签页切换正常
- [ ] 技术指标正确显示
- [ ] 缓存机制正常工作
- [ ] 加载状态正常显示
- [ ] 响应式布局正常

- [ ] **Step 2: 检查Git状态**

```bash
cd /data/fx_predict
git status
git log --oneline -5
```

- [ ] **Step 3: 推送到远程仓库**

```bash
git push
```

- [ ] **Step 4: 验证远程仓库**

访问 GitHub 确认所有提交已推送。

---

## 测试检查清单

### 单元测试
- [ ] API端点参数验证（无效货币对、无效周期）
- [ ] API端点缓存机制（首次加载、缓存命中、缓存过期）
- [ ] `extractKeyIndicators()` 函数边界情况（null/undefined指标）
- [ ] `generateOverallSummary()` 函数不同场景

### 集成测试
- [ ] 完整流程：点击表格行 → API调用 → 侧边栏显示
- [ ] 标签页切换：大模型分析 ↔ 技术指标
- [ ] 多触发源：卡片点击和表格行点击
- [ ] 缓存一致性：文件上传后清除缓存

### 手动测试
- [ ] 所有6个货币对的表格行点击
- [ ] 所有3个周期的表格行点击
- [ ] 侧边栏打开/关闭动画
- [ ] 加载状态显示
- [ ] 错误提示（网络错误、数据加载失败）

### 浏览器兼容性
- [ ] Chrome/Edge（Chromium）
- [ ] Firefox
- [ ] Safari
- [ ] 移动端浏览器

---

## 完成标准

功能完成标准：
- ✅ 点击交易策略表格行打开侧边栏
- ✅ 侧边栏显示6个关键技术指标类别
- ✅ 支持标签页切换（大模型分析/技术指标）
- ✅ 缓存机制正常工作（5分钟TTL）
- ✅ 文件上传后清除缓存
- ✅ 加载状态正常显示
- ✅ 错误处理友好

质量标准：
- ✅ 代码通过ESLint检查（如果配置）
- ✅ 浏览器控制台无错误
- ✅ 响应式布局正常（桌面/移动端）
- ✅ 性能目标达成（首次<500ms，缓存<100ms）

文档标准：
- ✅ AGENTS.md包含新API端点文档
- ✅ README.md包含新功能说明
- ✅ Git提交信息清晰规范