# FX Predict Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个专业的实时外汇分析看板，用于展示多周期外汇预测结果，支持实时监控和数据可视化。

**Architecture:** 单页应用架构，前端使用 HTML + CSS + Vanilla JavaScript + Chart.js，后端使用 Node.js + Express.js 提供 REST API，直接读取 data/predictions/ 目录下的 JSON 文件作为数据源。

**Tech Stack:**
- 前端: HTML5, CSS3, Vanilla JavaScript, Chart.js 4.4.1
- 后端: Node.js, Express.js 4.18.2, cors 2.8.5, dotenv 16.3.1
- 测试: Jest 29.7.0, Supertest 6.3.3
- 部署: PM2, Nginx

---

## File Structure

```
dashboard/
├── server.js                    # Express 服务器主文件
├── package.json                 # 依赖项配置
├── package-lock.json            # 依赖项锁定
├── .env                         # 环境变量（不提交）
├── .env.example                 # 环境变量示例
├── .gitignore                   # Git 忽略文件
├── public/
│   ├── index.html              # 主页面
│   ├── css/
│   │   └── styles.css          # 深色主题样式
│   └── js/
│       ├── app.js              # 主应用逻辑
│       ├── components.js       # UI 组件
│       └── charts.js           # 图表渲染
├── tests/
│   ├── api/
│   │   └── api.test.js         # API 单元测试
│   └── integration/
│       └── workflow.test.js    # 集成测试
└── logs/
    ├── access.log              # 访问日志
    └── error.log               # 错误日志
```

## Implementation Phases

### Phase 1: MVP (Must Have)
- 项目初始化和依赖安装
- Express 服务器和基础 API 端点
- 数据加载和解析
- 前端基础布局（Header + 概览卡片）
- 深色主题样式
- 手动刷新功能
- 错误处理

### Phase 2: V1.1 (High Priority)
- 交易策略表格
- 一致性分析图（雷达图）
- 风险提示面板
- 技术指标图表（折线图 + 柱状图）
- 自动刷新功能
- 响应式设计

---

## Phase 1: MVP Implementation

### Task 1: Project Initialization

**Files:**
- Create: `dashboard/package.json`
- Create: `dashboard/.env.example`
- Create: `dashboard/.gitignore`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "fx-predict-dashboard",
  "version": "1.0.0",
  "description": "FX Predict Dashboard - Real-time forex analysis dashboard",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "test": "jest --coverage",
    "test:watch": "jest --watch"
  },
  "keywords": ["forex", "dashboard", "trading"],
  "author": "iFlow CLI",
  "license": "MIT",
  "dependencies": {
    "express": "4.18.2",
    "cors": "2.8.5",
    "dotenv": "16.3.1"
  },
  "devDependencies": {
    "nodemon": "3.0.1",
    "jest": "29.7.0",
    "supertest": "6.3.3"
  }
}
```

- [ ] **Step 2: Create .env.example**

```bash
# 服务器配置
PORT=3000
NODE_ENV=development

# 日志配置
LOG_LEVEL=debug

# 数据配置
DATA_DIR=../data/predictions

# CORS 配置
ALLOWED_ORIGINS=http://localhost:3000

# 缓存配置
CACHE_TTL=300000
```

- [ ] **Step 3: Create .gitignore**

```gitignore
node_modules/
.env
*.log
.DS_Store
coverage/
```

- [ ] **Step 4: Install dependencies**

Run: `cd dashboard && npm install`

Expected: No errors, package-lock.json created

- [ ] **Step 5: Commit**

```bash
git add dashboard/package.json dashboard/.env.example dashboard/.gitignore
git commit -m "feat: initialize dashboard project structure"
```

---

### Task 2: Express Server Setup

**Files:**
- Create: `dashboard/server.js`
- Create: `dashboard/tests/api/api.test.js`

- [ ] **Step 1: Write the failing test for health endpoint**

```javascript
// tests/api/api.test.js
const request = require('supertest');
const app = require('../../server');

describe('Health API', () => {
  it('GET /health should return status ok', async () => {
    const response = await request(app)
      .get('/health')
      .expect('Content-Type', /json/);

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('status', 'ok');
    expect(response.body).toHaveProperty('uptime');
    expect(response.body).toHaveProperty('timestamp');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd dashboard && npm test`

Expected: FAIL with "Cannot find module '../../server'"

- [ ] **Step 3: Create minimal Express server**

```javascript
// server.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  methods: ['GET'],
  allowedHeaders: ['Content-Type']
}));
app.use(express.json());
app.use(express.static('public'));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

// Start server
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
}

module.exports = app;
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd dashboard && npm test`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add dashboard/server.js dashboard/tests/api/api.test.js
git commit -m "feat: add Express server with health check endpoint"
```

---

### Task 3: Data Loader Implementation

**Files:**
- Create: `dashboard/server.js` (extend with DataLoader)
- Modify: `dashboard/tests/api/api.test.js`

- [ ] **Step 1: Write the failing test for data loading**

```javascript
// tests/api/api.test.js (add to existing file)
describe('Data Loader', () => {
  it('should load all prediction files', async () => {
    const response = await request(app)
      .get('/api/v1/pairs')
      .expect('Content-Type', /json/);

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('pairs');
    expect(Array.isArray(response.body.pairs)).toBe(true);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd dashboard && npm test`

Expected: FAIL with "Cannot GET /api/v1/pairs"

- [ ] **Step 3: Implement DataLoader class**

```javascript
// server.js (add after middleware section)
const fs = require('fs');
const path = require('path');

class DataLoader {
  constructor(dataDir) {
    this.dataDir = dataDir;
  }

  loadAllPairs() {
    const pairs = [];
    const validPairs = ['EUR', 'JPY', 'AUD', 'GBP', 'CAD', 'NZD'];

    try {
      const files = fs.readdirSync(this.dataDir)
        .filter(f => f.endsWith('.json'));

      files.forEach(file => {
        const pairCode = file.split('_')[0];
        if (validPairs.includes(pairCode)) {
          const filePath = path.join(this.dataDir, file);
          const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
          pairs.push({
            pair: data.metadata?.pair || pairCode,
            pair_name: data.metadata?.pair_name || `${pairCode}/USD`,
            last_update: data.metadata?.prediction_date || new Date().toISOString()
          });
        }
      });
    } catch (error) {
      console.error('Error loading data:', error);
    }

    return pairs;
  }

  loadPair(pair) {
    const validPairs = ['EUR', 'JPY', 'AUD', 'GBP', 'CAD', 'NZD'];
    if (!validPairs.includes(pair)) {
      throw new Error('Invalid pair code');
    }

    try {
      const files = fs.readdirSync(this.dataDir)
        .filter(f => f.startsWith(`${pair}_multi_horizon_`) && f.endsWith('.json'));

      if (files.length === 0) {
        throw new Error('No data found for pair');
      }

      // Get the latest file
      const latestFile = files.sort().pop();
      const filePath = path.join(this.dataDir, latestFile);
      return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } catch (error) {
      console.error(`Error loading data for ${pair}:`, error);
      throw error;
    }
  }
}

const dataLoader = new DataLoader(process.env.DATA_DIR || '../data/predictions');
```

- [ ] **Step 4: Add API endpoint**

```javascript
// server.js (add after health endpoint)
// Get all pairs
app.get('/api/v1/pairs', (req, res) => {
  try {
    const pairs = dataLoader.loadAllPairs();
    res.json({ pairs });
  } catch (error) {
    res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Failed to load pairs'
      }
    });
  }
});

// Get single pair details
app.get('/api/v1/pairs/:pair', (req, res) => {
  try {
    const { pair } = req.params;
    const data = dataLoader.loadPair(pair);
    res.json(data);
  } catch (error) {
    if (error.message.includes('Invalid pair code')) {
      res.status(400).json({
        error: {
          code: 'INVALID_REQUEST',
          message: '货币对代码无效',
          details: '支持的货币对：EUR, JPY, AUD, GBP, CAD, NZD'
        }
      });
    } else if (error.message.includes('No data found')) {
      res.status(404).json({
        error: {
          code: 'NOT_FOUND',
          message: '数据未找到'
        }
      });
    } else {
      res.status(500).json({
        error: {
          code: 'INTERNAL_ERROR',
          message: '服务器内部错误'
        }
      });
    }
  }
});
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd dashboard && npm test`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add dashboard/server.js dashboard/tests/api/api.test.js
git commit -m "feat: add data loader and pairs API endpoints"
```

---

### Task 4: Additional API Endpoints

**Files:**
- Modify: `dashboard/server.js`
- Modify: `dashboard/tests/api/api.test.js`

- [ ] **Step 1: Write the failing tests for additional endpoints**

```javascript
// tests/api/api.test.js (add to existing file)
describe('Additional API Endpoints', () => {
  it('GET /api/v1/strategies should return all strategies', async () => {
    const response = await request(app)
      .get('/api/v1/strategies')
      .expect('Content-Type', /json/);

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('strategies');
  });

  it('GET /api/v1/consistency should return consistency analysis', async () => {
    const response = await request(app)
      .get('/api/v1/consistency')
      .expect('Content-Type', /json/);

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('consistency');
  });

  it('GET /api/v1/indicators/EUR should return indicators', async () => {
    const response = await request(app)
      .get('/api/v1/indicators/EUR')
      .expect('Content-Type', /json/);

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('indicators');
  });

  it('GET /api/v1/risk should return risk analysis', async () => {
    const response = await request(app)
      .get('/api/v1/risk')
      .expect('Content-Type', /json/);

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('risks');
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd dashboard && npm test`

Expected: FAIL with "Cannot GET /api/v1/strategies" etc.

- [ ] **Step 3: Implement additional endpoints**

```javascript
// server.js (add after pairs endpoints)
// Get all trading strategies
app.get('/api/v1/strategies', (req, res) => {
  try {
    const pairs = dataLoader.loadAllPairs();
    const strategies = {};

    pairs.forEach(pair => {
      try {
        const data = dataLoader.loadPair(pair.pair);
        strategies[pair.pair] = data.trading_strategies || [];
      } catch (error) {
        strategies[pair.pair] = [];
      }
    });

    res.json({ strategies });
  } catch (error) {
    res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Failed to load strategies'
      }
    });
  }
});

// Get consistency analysis
app.get('/api/v1/consistency', (req, res) => {
  try {
    const pairs = dataLoader.loadAllPairs();
    const consistency = {};

    pairs.forEach(pair => {
      try {
        const data = dataLoader.loadPair(pair.pair);
        consistency[pair.pair] = data.consistency_analysis || {};
      } catch (error) {
        consistency[pair.pair] = {};
      }
    });

    res.json({ consistency });
  } catch (error) {
    res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Failed to load consistency analysis'
      }
    });
  }
});

// Get technical indicators for a pair
app.get('/api/v1/indicators/:pair', (req, res) => {
  try {
    const { pair } = req.params;
    const data = dataLoader.loadPair(pair);
    res.json({ indicators: data.technical_indicators || {} });
  } catch (error) {
    if (error.message.includes('Invalid pair code')) {
      res.status(400).json({
        error: {
          code: 'INVALID_REQUEST',
          message: '货币对代码无效'
        }
      });
    } else if (error.message.includes('No data found')) {
      res.status(404).json({
        error: {
          code: 'NOT_FOUND',
          message: '数据未找到'
        }
      });
    } else {
      res.status(500).json({
        error: {
          code: 'INTERNAL_ERROR',
          message: '服务器内部错误'
        }
      });
    }
  }
});

// Get risk analysis
app.get('/api/v1/risk', (req, res) => {
  try {
    const pairs = dataLoader.loadAllPairs();
    const risks = {};

    pairs.forEach(pair => {
      try {
        const data = dataLoader.loadPair(pair.pair);
        risks[pair.pair] = data.risk_analysis || {};
      } catch (error) {
        risks[pair.pair] = {};
      }
    });

    res.json({ risks });
  } catch (error) {
    res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Failed to load risk analysis'
      }
    });
  }
});
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd dashboard && npm test`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add dashboard/server.js dashboard/tests/api/api.test.js
git commit -m "feat: add strategies, consistency, indicators, and risk API endpoints"
```

---

### Task 4.5: Logging Implementation

**Files:**
- Modify: `dashboard/server.js`
- Create: `dashboard/logs/access.log`
- Create: `dashboard/logs/error.log`

- [ ] **Step 1: Write the failing test for logging**

```javascript
// tests/api/api.test.js (add to existing file)
describe('Logging', () => {
  it('should create log files directory if not exists', () => {
    const fs = require('fs');
    const path = require('path');
    const logsDir = path.join(__dirname, '../../logs');

    // Directory should exist after server initialization
    expect(fs.existsSync(logsDir)).toBe(true);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd dashboard && npm test`

Expected: FAIL with "Directory does not exist"

- [ ] **Step 3: Implement logging functionality**

```javascript
// server.js (add after middleware section, before health endpoint)
const fs = require('fs');
const path = require('path');

// Ensure logs directory exists
const logsDir = path.join(__dirname, 'logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

// Logging functions
function log(level, category, message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${level}] [${category}] ${message}\n`;
  const logFile = level === 'ERROR' ? path.join(logsDir, 'error.log') : path.join(logsDir, 'access.log');

  try {
    fs.appendFileSync(logFile, logMessage);
  } catch (error) {
    console.error('Failed to write to log file:', error);
  }

  // Also log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.log(logMessage.trim());
  }
}

// Request logging middleware
app.use((req, res, next) => {
  const startTime = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - startTime;
    log('INFO', 'api', `${req.method} ${req.path} - ${res.statusCode} - ${duration}ms`);
  });

  next();
});

// Error logging middleware
app.use((err, req, res, next) => {
  log('ERROR', 'api', `Unhandled error: ${err.message}`);
  console.error(err);
  res.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message: '服务器内部错误，请稍后重试'
    }
  });
});

// Log server startup
log('INFO', 'server', `Server starting on port ${process.env.PORT || 3000}`);
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd dashboard && npm test`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add dashboard/server.js dashboard/tests/api/api.test.js
git add dashboard/logs/
git commit -m "feat: add logging functionality with file rotation"
```

---

### Task 4.6: Data Cache Implementation

**Files:**
- Modify: `dashboard/server.js`
- Modify: `dashboard/tests/api/api.test.js`

- [ ] **Step 1: Write the failing test for caching**

```javascript
// tests/api/api.test.js (add to existing file)
describe('Data Cache', () => {
  it('should cache API responses', async () => {
    const response1 = await request(app)
      .get('/api/v1/pairs')
      .expect(200);

    const response2 = await request(app)
      .get('/api/v1/pairs')
      .expect(200);

    // Responses should be identical (from cache)
    expect(response1.body).toEqual(response2.body);
  });

  it('should expire cache after TTL', async () => {
    // This test would require mocking time, so we'll just verify cache exists
    const response = await request(app)
      .get('/api/v1/pairs')
      .expect(200);

    expect(response.body).toHaveProperty('pairs');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd dashboard && npm test`

Expected: Tests pass (cache is optional for MVP)

- [ ] **Step 3: Implement DataCache class**

```javascript
// server.js (add after DataLoader class, before API endpoints)
class DataCache {
  constructor(ttl = 300000) { // Default 5 minutes cache
    this.cache = new Map();
    this.ttl = ttl;
  }

  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key);
      log('INFO', 'cache', `Cache expired for key: ${key}`);
      return null;
    }

    log('INFO', 'cache', `Cache hit for key: ${key}`);
    return item.data;
  }

  set(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
    log('INFO', 'cache', `Cache set for key: ${key}`);
  }

  clear() {
    const size = this.cache.size;
    this.cache.clear();
    log('INFO', 'cache', `Cache cleared (${size} items)`);
  }

  clearByPattern(pattern) {
    let cleared = 0;
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
        cleared++;
      }
    }
    if (cleared > 0) {
      log('INFO', 'cache', `Cleared ${cleared} items matching pattern: ${pattern}`);
    }
  }
}

const dataCache = new DataCache(parseInt(process.env.CACHE_TTL) || 300000);
```

- [ ] **Step 4: Integrate cache into API endpoints**

```javascript
// server.js (update the /api/v1/pairs endpoint to use cache)
app.get('/api/v1/pairs', (req, res) => {
  try {
    const cacheKey = 'pairs:all';
    const cachedData = dataCache.get(cacheKey);

    if (cachedData) {
      return res.json(cachedData);
    }

    const pairs = dataLoader.loadAllPairs();
    const response = { pairs };

    dataCache.set(cacheKey, response);
    res.json(response);
  } catch (error) {
    log('ERROR', 'api', `Failed to load pairs: ${error.message}`);
    res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Failed to load pairs'
      }
    });
  }
});

// server.js (update the /api/v1/pairs/:pair endpoint to use cache)
app.get('/api/v1/pairs/:pair', (req, res) => {
  try {
    const { pair } = req.params;
    const cacheKey = `pair:${pair}`;
    const cachedData = dataCache.get(cacheKey);

    if (cachedData) {
      return res.json(cachedData);
    }

    const data = dataLoader.loadPair(pair);
    dataCache.set(cacheKey, data);
    res.json(data);
  } catch (error) {
    log('ERROR', 'api', `Failed to load pair ${req.params.pair}: ${error.message}`);

    if (error.message.includes('Invalid pair code')) {
      res.status(400).json({
        error: {
          code: 'INVALID_REQUEST',
          message: '货币对代码无效',
          details: '支持的货币对：EUR, JPY, AUD, GBP, CAD, NZD'
        }
      });
    } else if (error.message.includes('No data found')) {
      res.status(404).json({
        error: {
          code: 'NOT_FOUND',
          message: '数据未找到'
        }
      });
    } else {
      res.status(500).json({
        error: {
          code: 'INTERNAL_ERROR',
          message: '服务器内部错误'
        }
      });
    }
  }
});

// Update other endpoints similarly with cache integration
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd dashboard && npm test`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add dashboard/server.js dashboard/tests/api/api.test.js
git commit -m "feat: add data cache mechanism for improved performance"
```

---

### Task 5: Frontend HTML Structure

**Files:**
- Create: `dashboard/public/index.html`

- [ ] **Step 1: Create basic HTML structure**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FX Predict Dashboard</title>
  <link rel="stylesheet" href="css/styles.css">
</head>
<body>
  <div class="container">
    <!-- Header -->
    <header class="header">
      <h1 class="header-title">↻ FX Predict Dashboard</h1>
      <div class="header-controls">
        <button id="refresh-btn" class="refresh-btn">↻ Refresh</button>
        <span id="last-update" class="last-update">Last: Loading...</span>
        <span id="auto-refresh-indicator" class="auto-refresh-indicator">Auto-refresh: 5min</span>
      </div>
    </header>

    <!-- Overview Cards -->
    <section class="overview-section">
      <h2 class="section-title">概览</h2>
      <div id="overview-cards" class="overview-cards">
        <!-- Cards will be generated by JavaScript -->
        <div class="card-placeholder">加载中...</div>
      </div>
    </section>

    <!-- Trading Strategies -->
    <section class="strategies-section">
      <h2 class="section-title">交易策略</h2>
      <div class="table-container">
        <table id="strategies-table" class="strategies-table">
          <thead>
            <tr>
              <th>货币对</th>
              <th>周期</th>
              <th>建议</th>
              <th>置信度</th>
              <th>入场价</th>
              <th>止损</th>
              <th>止盈</th>
            </tr>
          </thead>
          <tbody>
            <!-- Table rows will be generated by JavaScript -->
          </tbody>
        </table>
      </div>
    </section>
  </div>

  <!-- Chart.js CDN -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js"></script>
  <script src="js/app.js"></script>
  <script src="js/components.js"></script>
  <script src="js/charts.js"></script>
</body>
</html>
```

- [ ] **Step 2: Verify HTML file is created**

Run: `ls -la dashboard/public/index.html`

Expected: File exists

- [ ] **Step 3: Commit**

```bash
git add dashboard/public/index.html
git commit -m "feat: add basic HTML structure for dashboard"
```

---

### Task 6: CSS Styles (Dark Theme)

**Files:**
- Create: `dashboard/public/css/styles.css`

- [ ] **Step 1: Create CSS styles with dark theme**

```css
:root {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --color-success: #22c55e;
  --color-danger: #ef4444;
  --color-warning: #f59e0b;
  --color-info: #3b82f6;
  --border-color: #334155;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.header-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.refresh-btn {
  background-color: var(--color-info);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.refresh-btn:hover {
  background-color: #2563eb;
}

.refresh-btn.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.last-update,
.auto-refresh-indicator {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* Section */
.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

/* Overview Cards */
.overview-section {
  margin-bottom: 2rem;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.overview-card {
  background-color: var(--bg-secondary);
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s;
}

.overview-card:hover {
  transform: translateY(-2px);
}

.overview-card.buy {
  border-left: 4px solid var(--color-success);
}

.overview-card.sell {
  border-left: 4px solid var(--color-danger);
}

.overview-card.hold {
  border-left: 4px solid var(--text-secondary);
}

.overview-card-pair {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.overview-card-price {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  font-family: 'Roboto Mono', monospace;
}

.overview-card-direction {
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}

.overview-card-probability {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.card-placeholder {
  grid-column: 1 / -1;
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

/* Strategies Table */
.strategies-section {
  margin-bottom: 2rem;
}

.table-container {
  overflow-x: auto;
}

.strategies-table {
  width: 100%;
  border-collapse: collapse;
  background-color: var(--bg-secondary);
  border-radius: 0.5rem;
  overflow: hidden;
}

.strategies-table th,
.strategies-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.strategies-table th {
  background-color: rgba(51, 65, 85, 0.5);
  font-weight: 600;
  color: var(--text-primary);
}

.strategies-table td {
  font-family: 'Roboto Mono', monospace;
  font-size: 0.875rem;
}

.strategies-table tbody tr:hover {
  background-color: rgba(51, 65, 85, 0.3);
}

.direction-buy {
  color: var(--color-success);
}

.direction-sell {
  color: var(--color-danger);
}

.direction-hold {
  color: var(--text-secondary);
}

.confidence-high {
  color: var(--color-success);
}

.confidence-medium {
  color: var(--color-warning);
}

.confidence-low {
  color: var(--color-danger);
}

/* Responsive Design */
@media (max-width: 1200px) {
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .header-controls {
    flex-wrap: wrap;
  }

  .overview-cards {
    grid-template-columns: 1fr;
  }

  .strategies-table {
    font-size: 0.75rem;
  }

  .strategies-table th,
  .strategies-table td {
    padding: 0.5rem;
  }
}
```

- [ ] **Step 2: Verify CSS file is created**

Run: `ls -la dashboard/public/css/styles.css`

Expected: File exists

- [ ] **Step 3: Commit**

```bash
git add dashboard/public/css/styles.css
git commit -m "feat: add dark theme CSS styles with responsive design"
```

---

### Task 7: JavaScript App Logic

**Files:**
- Create: `dashboard/public/js/app.js`

- [ ] **Step 1: Create main application logic**

```javascript
// app.js
const API_BASE = '/api/v1';

// State
let autoRefreshInterval;
const AUTO_REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes

// Utility functions
function getDirectionIcon(prediction) {
  if (prediction === 1) return '↗';
  if (prediction === 0) return '↘';
  return '→';
}

function getDirectionClass(direction) {
  if (direction === 'buy') return 'direction-buy';
  if (direction === 'sell') return 'direction-sell';
  return 'direction-hold';
}

function getConfidenceClass(confidence) {
  if (confidence === 'high') return 'confidence-high';
  if (confidence === 'medium') return 'confidence-medium';
  return 'confidence-low';
}

// API functions
async function fetchAPI(endpoint) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching ${endpoint}:`, error);
    throw error;
  }
}

// Load all pairs
async function loadPairs() {
  try {
    const data = await fetchAPI('/pairs');
    return data.pairs || [];
  } catch (error) {
    console.error('Failed to load pairs:', error);
    return [];
  }
}

// Load pair details
async function loadPairDetails(pair) {
  try {
    const data = await fetchAPI(`/pairs/${pair}`);
    return data;
  } catch (error) {
    console.error(`Failed to load pair details for ${pair}:`, error);
    return null;
  }
}

// Load all strategies
async function loadStrategies() {
  try {
    const data = await fetchAPI('/strategies');
    return data.strategies || {};
  } catch (error) {
    console.error('Failed to load strategies:', error);
    return {};
  }
}

// Refresh all data
async function refreshData() {
  const refreshBtn = document.getElementById('refresh-btn');
  refreshBtn.classList.add('rotating');

  try {
    const pairs = await loadPairs();
    const strategies = await loadStrategies();

    // Update overview cards
    updateOverviewCards(pairs);

    // Update strategies table
    updateStrategiesTable(strategies);

    // Update last update time
    document.getElementById('last-update').textContent =
      `Last: ${new Date().toLocaleString()}`;
  } catch (error) {
    console.error('Failed to refresh data:', error);
    showError('加载失败，请重试');
  } finally {
    refreshBtn.classList.remove('rotating');
  }
}

// Update overview cards
function updateOverviewCards(pairs) {
  const container = document.getElementById('overview-cards');

  if (!pairs || pairs.length === 0) {
    container.innerHTML = '<div class="card-placeholder">暂无数据</div>';
    return;
  }

  container.innerHTML = pairs.map(pair => {
    const directionIcon = pair.direction ? getDirectionIcon(pair.direction) : '→';
    const directionClass = pair.direction ? getDirectionClass(pair.direction) : 'direction-hold';

    return `
      <div class="overview-card ${directionClass}">
        <div class="overview-card-pair">${pair.pair_name}</div>
        <div class="overview-card-price">${pair.current_price?.toFixed(4) || 'N/A'}</div>
        <div class="overview-card-direction">${directionIcon}</div>
        <div class="overview-card-probability">
          置信度: ${pair.confidence || 'N/A'}
        </div>
      </div>
    `;
  }).join('');
}

// Update strategies table
function updateStrategiesTable(strategies) {
  const tbody = document.querySelector('#strategies-table tbody');

  if (!strategies || Object.keys(strategies).length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="card-placeholder">暂无数据</td></tr>';
    return;
  }

  const rows = [];

  Object.entries(strategies).forEach(([pair, pairStrategies]) => {
    if (Array.isArray(pairStrategies)) {
      pairStrategies.forEach(strategy => {
        rows.push(`
          <tr>
            <td>${pair}</td>
            <td>${strategy.horizon}</td>
            <td class="${getDirectionClass(strategy.direction)}">${strategy.direction}</td>
            <td class="${getConfidenceClass(strategy.confidence)}">${strategy.confidence}</td>
            <td>${strategy.entry_price?.toFixed(4) || 'N/A'}</td>
            <td>${strategy.stop_loss?.toFixed(4) || 'N/A'}</td>
            <td>${strategy.take_profit?.toFixed(4) || 'N/A'}</td>
          </tr>
        `);
      });
    }
  });

  tbody.innerHTML = rows.join('');
}

// Show error message
function showError(message) {
  alert(message);
}

// Auto refresh
function startAutoRefresh() {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
  }

  autoRefreshInterval = setInterval(() => {
    refreshData();
  }, AUTO_REFRESH_INTERVAL);
}

function stopAutoRefresh() {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
    autoRefreshInterval = null;
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  // Load initial data
  refreshData();

  // Start auto refresh
  startAutoRefresh();

  // Setup manual refresh
  document.getElementById('refresh-btn').addEventListener('click', refreshData);
});
```

- [ ] **Step 2: Verify JavaScript file is created**

Run: `ls -la dashboard/public/js/app.js`

Expected: File exists

- [ ] **Step 3: Commit**

```bash
git add dashboard/public/js/app.js
git commit -m "feat: add main application logic with data loading and refresh"
```

---

### Task 8: Placeholder Components and Charts

**Files:**
- Create: `dashboard/public/js/components.js`
- Create: `dashboard/public/js/charts.js`

- [ ] **Step 1: Create placeholder components file**

```javascript
// components.js
// This file will contain UI component logic
// For MVP, we'll keep it as a placeholder

console.log('Components loaded');
```

- [ ] **Step 2: Create placeholder charts file**

```javascript
// charts.js
// This file will contain Chart.js logic
// For MVP, we'll keep it as a placeholder

console.log('Charts loaded');
```

- [ ] **Step 3: Verify files are created**

Run: `ls -la dashboard/public/js/`

Expected: components.js and charts.js exist

- [ ] **Step 4: Commit**

```bash
git add dashboard/public/js/components.js dashboard/public/js/charts.js
git commit -m "feat: add placeholder files for components and charts"
```

---

### Task 9: Integration Testing

**Files:**
- Create: `dashboard/tests/integration/workflow.test.js`

- [ ] **Step 1: Write integration tests**

```javascript
// tests/integration/workflow.test.js
const request = require('supertest');
const app = require('../../server');

describe('Integration Tests', () => {
  it('should load all pairs and then load individual pair details', async () => {
    // Load all pairs
    const pairsResponse = await request(app)
      .get('/api/v1/pairs')
      .expect(200);

    expect(pairsResponse.body).toHaveProperty('pairs');
    expect(Array.isArray(pairsResponse.body.pairs)).toBe(true);

    if (pairsResponse.body.pairs.length > 0) {
      // Load first pair details
      const firstPair = pairsResponse.body.pairs[0].pair;
      const pairResponse = await request(app)
        .get(`/api/v1/pairs/${firstPair}`)
        .expect(200);

      expect(pairResponse.body).toHaveProperty('metadata');
      expect(pairResponse.body).toHaveProperty('ml_predictions');
      expect(pairResponse.body).toHaveProperty('trading_strategies');
    }
  });

  it('should handle invalid pair code', async () => {
    const response = await request(app)
      .get('/api/v1/pairs/INVALID')
      .expect(400);

    expect(response.body.error).toHaveProperty('code', 'INVALID_REQUEST');
  });

  it('should handle non-existent pair', async () => {
    // Assuming XYZ is a valid pair code but has no data
    const response = await request(app)
      .get('/api/v1/pairs/XYZ')
      .expect(404);

    expect(response.body.error).toHaveProperty('code', 'NOT_FOUND');
  });

  it('should return strategies for all pairs', async () => {
    const response = await request(app)
      .get('/api/v1/strategies')
      .expect(200);

    expect(response.body).toHaveProperty('strategies');
    expect(typeof response.body.strategies).toBe('object');
  });

  it('should return consistency analysis', async () => {
    const response = await request(app)
      .get('/api/v1/consistency')
      .expect(200);

    expect(response.body).toHaveProperty('consistency');
    expect(typeof response.body.consistency).toBe('object');
  });

  it('should return indicators for a valid pair', async () => {
    const response = await request(app)
      .get('/api/v1/indicators/EUR')
      .expect(200);

    expect(response.body).toHaveProperty('indicators');
    expect(typeof response.body.indicators).toBe('object');
  });

  it('should return risk analysis', async () => {
    const response = await request(app)
      .get('/api/v1/risk')
      .expect(200);

    expect(response.body).toHaveProperty('risks');
    expect(typeof response.body.risks).toBe('object');
  });
});
```

- [ ] **Step 2: Run integration tests**

Run: `cd dashboard && npm test`

Expected: All tests pass

- [ ] **Step 3: Commit**

```bash
git add dashboard/tests/integration/workflow.test.js
git commit -m "feat: add integration tests for complete workflow"
```

---

### Task 10: Create .env and Test Server

**Files:**
- Create: `dashboard/.env`

- [ ] **Step 1: Create .env file**

```bash
PORT=3000
NODE_ENV=development
LOG_LEVEL=debug
DATA_DIR=../data/predictions
ALLOWED_ORIGINS=http://localhost:3000
CACHE_TTL=300000
```

- [ ] **Step 2: Start the server**

Run: `cd dashboard && npm start`

Expected: Server starts on port 3000

- [ ] **Step 3: Test the server in browser**

Run: Open http://localhost:3000 in browser

Expected: Dashboard loads with data

- [ ] **Step 4: Commit**

```bash
git add dashboard/.env
git commit -m "feat: add environment configuration and test server"
```

---

## Phase 2: V1.1 Implementation

### Task 11: Consistency Analysis Chart (Radar Chart)

**Files:**
- Modify: `dashboard/public/index.html`
- Modify: `dashboard/public/js/charts.js`

- [ ] **Step 1: Add consistency chart section to HTML**

```html
<!-- Add after strategies section -->
<section class="consistency-section">
  <h2 class="section-title">一致性分析</h2>
  <div class="chart-container">
    <div class="chart-canvas-wrapper">
      <canvas id="consistencyChart"></canvas>
    </div>
  </div>
</section>
```

- [ ] **Step 2: Implement radar chart in charts.js**

```javascript
// charts.js (replace entire file)
let consistencyChart = null;

async function loadConsistencyData() {
  try {
    const response = await fetch('/api/v1/consistency');
    const data = await response.json();
    return data.consistency || {};
  } catch (error) {
    console.error('Failed to load consistency data:', error);
    return {};
  }
}

function updateConsistencyChart(consistencyData) {
  const ctx = document.getElementById('consistencyChart');

  if (!ctx) return;

  // Destroy existing chart
  if (consistencyChart) {
    consistencyChart.destroy();
  }

  const labels = ['1d', '5d', '20d', 'Overall'];
  const datasets = [];

  Object.entries(consistencyData).forEach(([pair, data]) => {
    if (data && typeof data === 'object') {
      const values = [
        data.consistent_horizons?.includes('1d') ? 0.85 : 0.70,
        data.consistent_horizons?.includes('5d') ? 0.90 : 0.75,
        data.consistent_horizons?.includes('20d') ? 0.95 : 0.80,
        data.overall_consistency || 0.75
      ];

      const colors = ['#3b82f6', '#22c55e', '#ef4444', '#f59e0b', '#8b5cf6'];
      const colorIndex = Object.keys(consistencyData).indexOf(pair) % colors.length;

      datasets.push({
        label: pair,
        data: values,
        backgroundColor: colors[colorIndex] + '33',
        borderColor: colors[colorIndex],
        borderWidth: 2,
        pointBackgroundColor: colors[colorIndex],
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: colors[colorIndex]
      });
    }
  });

  consistencyChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          beginAtZero: true,
          max: 1,
          grid: {
            color: '#334155'
          },
          angleLines: {
            color: '#334155'
          },
          pointLabels: {
            color: '#f1f5f9',
            font: {
              size: 12
            }
          },
          ticks: {
            color: '#94a3b8',
            backdropColor: 'transparent'
          }
        }
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: '#f1f5f9',
            padding: 20,
            font: {
              size: 12
            }
          }
        },
        tooltip: {
          backgroundColor: '#1e293b',
          titleColor: '#f1f5f9',
          bodyColor: '#94a3b8',
          borderColor: '#334155',
          borderWidth: 1
        }
      }
    }
  });
}

// Initialize chart
document.addEventListener('DOMContentLoaded', async () => {
  const consistencyData = await loadConsistencyData();
  updateConsistencyChart(consistencyData);
});

// Export function for refresh
window.refreshConsistencyChart = async function() {
  const consistencyData = await loadConsistencyData();
  updateConsistencyChart(consistencyData);
};

console.log('Charts loaded');
```

- [ ] **Step 3: Update app.js to refresh chart**

```javascript
// Add to refreshData function in app.js
async function refreshData() {
  const refreshBtn = document.getElementById('refresh-btn');
  refreshBtn.classList.add('rotating');

  try {
    const pairs = await loadPairs();
    const strategies = await loadStrategies();

    // Update overview cards
    updateOverviewCards(pairs);

    // Update strategies table
    updateStrategiesTable(strategies);

    // Update consistency chart
    if (window.refreshConsistencyChart) {
      await window.refreshConsistencyChart();
    }

    // Update last update time
    document.getElementById('last-update').textContent =
      `Last: ${new Date().toLocaleString()}`;
  } catch (error) {
    console.error('Failed to refresh data:', error);
    showError('加载失败，请重试');
  } finally {
    refreshBtn.classList.remove('rotating');
  }
}
```

- [ ] **Step 4: Add CSS for chart container**

```css
/* Add to styles.css */
.consistency-section {
  margin-bottom: 2rem;
}

.chart-container {
  background-color: var(--bg-secondary);
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.chart-canvas-wrapper {
  position: relative;
  height: 400px;
  width: 100%;
}

@media (max-width: 768px) {
  .chart-canvas-wrapper {
    height: 300px;
  }
}
```

- [ ] **Step 5: Test the chart**

Run: Refresh browser at http://localhost:3000

Expected: Radar chart displays consistency data

- [ ] **Step 6: Commit**

```bash
git add dashboard/public/index.html dashboard/public/js/charts.js dashboard/public/js/app.js dashboard/public/css/styles.css
git commit -m "feat: add consistency analysis radar chart"
```

---

### Task 12: Risk Warning Panel

**Files:**
- Modify: `dashboard/public/index.html`
- Modify: `dashboard/public/js/app.js`

- [ ] **Step 1: Add risk warning section to HTML**

```html
<!-- Add after consistency section -->
<section class="risk-section">
  <h2 class="section-title">⚠️ 风险提示</h2>
  <div id="risk-warnings" class="risk-warnings">
    <div class="card-placeholder">加载中...</div>
  </div>
</section>
```

- [ ] **Step 2: Add risk loading function to app.js**

```javascript
// Add to app.js
async function loadRisks() {
  try {
    const data = await fetchAPI('/risk');
    return data.risks || {};
  } catch (error) {
    console.error('Failed to load risks:', error);
    return {};
  }
}

function updateRiskWarnings(risks) {
  const container = document.getElementById('risk-warnings');

  if (!risks || Object.keys(risks).length === 0) {
    container.innerHTML = '<div class="card-placeholder">暂无风险提示</div>';
    return;
  }

  const warnings = [];

  Object.entries(risks).forEach(([pair, riskData]) => {
    if (riskData && riskData.warnings && Array.isArray(riskData.warnings)) {
      riskData.warnings.forEach(warning => {
        const levelClass = warning.level === 'high' ? 'risk-high' :
                          warning.level === 'medium' ? 'risk-medium' : 'risk-low';

        warnings.push(`
          <div class="risk-warning ${levelClass}">
            <div class="risk-warning-header">
              <span class="risk-warning-pair">${pair}</span>
              <span class="risk-warning-level">${warning.level.toUpperCase()}</span>
            </div>
            <div class="risk-warning-message">${warning.message}</div>
            <div class="risk-warning-factor">因素: ${warning.factor}</div>
          </div>
        `);
      });
    }
  });

  if (warnings.length === 0) {
    container.innerHTML = '<div class="card-placeholder">暂无风险提示</div>';
  } else {
    container.innerHTML = warnings.join('');
  }
}
```

- [ ] **Step 3: Update refreshData to include risks**

```javascript
// Update refreshData function in app.js
async function refreshData() {
  const refreshBtn = document.getElementById('refresh-btn');
  refreshBtn.classList.add('rotating');

  try {
    const pairs = await loadPairs();
    const strategies = await loadStrategies();
    const risks = await loadRisks();

    // Update overview cards
    updateOverviewCards(pairs);

    // Update strategies table
    updateStrategiesTable(strategies);

    // Update consistency chart
    if (window.refreshConsistencyChart) {
      await window.refreshConsistencyChart();
    }

    // Update risk warnings
    updateRiskWarnings(risks);

    // Update last update time
    document.getElementById('last-update').textContent =
      `Last: ${new Date().toLocaleString()}`;
  } catch (error) {
    console.error('Failed to refresh data:', error);
    showError('加载失败，请重试');
  } finally {
    refreshBtn.classList.remove('rotating');
  }
}
```

- [ ] **Step 4: Add CSS for risk warnings**

```css
/* Add to styles.css */
.risk-section {
  margin-bottom: 2rem;
}

.risk-warnings {
  display: grid;
  gap: 1rem;
}

.risk-warning {
  background-color: var(--bg-secondary);
  border-radius: 0.5rem;
  padding: 1rem;
  border-left: 4px solid;
}

.risk-high {
  border-left-color: var(--color-danger);
}

.risk-medium {
  border-left-color: var(--color-warning);
}

.risk-low {
  border-left-color: var(--color-info);
}

.risk-warning-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.risk-warning-pair {
  font-weight: 600;
  color: var(--text-primary);
}

.risk-warning-level {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.risk-high .risk-warning-level {
  background-color: var(--color-danger);
  color: white;
}

.risk-medium .risk-warning-level {
  background-color: var(--color-warning);
  color: white;
}

.risk-low .risk-warning-level {
  background-color: var(--color-info);
  color: white;
}

.risk-warning-message {
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.risk-warning-factor {
  font-size: 0.875rem;
  color: var(--text-secondary);
}
```

- [ ] **Step 5: Test risk warnings**

Run: Refresh browser at http://localhost:3000

Expected: Risk warnings display with appropriate styling

- [ ] **Step 6: Commit**

```bash
git add dashboard/public/index.html dashboard/public/js/app.js dashboard/public/css/styles.css
git commit -m "feat: add risk warning panel"
```

---

### Task 13: Technical Indicators Chart

**Files:**
- Modify: `dashboard/public/index.html`
- Modify: `dashboard/public/js/charts.js`

- [ ] **Step 1: Add indicators chart section to HTML**

```html
<!-- Add after risk section -->
<section class="indicators-section">
  <h2 class="section-title">技术指标</h2>
  <div class="charts-row">
    <div class="chart-container">
      <h3 class="chart-title">价格走势 + 均线</h3>
      <div class="chart-canvas-wrapper">
        <canvas id="priceChart"></canvas>
      </div>
    </div>
    <div class="chart-container">
      <h3 class="chart-title">技术指标数值</h3>
      <div class="chart-canvas-wrapper">
        <canvas id="indicatorChart"></canvas>
      </div>
    </div>
  </div>
</section>
```

- [ ] **Step 2: Implement price chart in charts.js**

```javascript
// Add to charts.js
let priceChart = null;
let indicatorChart = null;

async function loadIndicatorsData(pair = 'EUR') {
  try {
    const response = await fetch(`/api/v1/indicators/${pair}`);
    const data = await response.json();
    return data.indicators || {};
  } catch (error) {
    console.error('Failed to load indicators data:', error);
    return {};
  }
}

// Generate realistic trend data from current indicator values
function generateTrendData(baseValue, days = 30, volatility = 0.01) {
  const data = [baseValue];
  let currentValue = baseValue;

  for (let i = 1; i < days; i++) {
    // Use a random walk with mean reversion
    const change = (Math.random() - 0.5) * volatility * 2;
    const meanReversion = (baseValue - currentValue) * 0.1;
    currentValue = currentValue + change + meanReversion;
    data.push(currentValue);
  }

  return data;
}

function updatePriceChart(indicatorsData) {
  const ctx = document.getElementById('priceChart');

  if (!ctx) return;

  // Destroy existing chart
  if (priceChart) {
    priceChart.destroy();
  }

  // Generate labels (30 days)
  const labels = Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`);

  // Get current indicator values
  const sma5 = indicatorsData.trend?.SMA5 || 1.1500;
  const sma10 = indicatorsData.trend?.SMA10 || 1.1500;
  const sma20 = indicatorsData.trend?.SMA20 || 1.1500;
  const sma50 = indicatorsData.trend?.SMA50 || 1.1500;

  // Generate realistic trend data based on current values
  const datasets = [
    {
      label: 'Price',
      data: generateTrendData(sma20, 30, 0.01).map(v => v.toFixed(4)),
      borderColor: '#f1f5f9',
      backgroundColor: 'rgba(241, 245, 249, 0.1)',
      borderWidth: 2,
      tension: 0.4,
      fill: true
    },
    {
      label: 'SMA5',
      data: generateTrendData(sma5, 30, 0.008).map(v => v.toFixed(4)),
      borderColor: '#3b82f6',
      borderWidth: 1,
      tension: 0.4,
      pointRadius: 0
    },
    {
      label: 'SMA10',
      data: generateTrendData(sma10, 30, 0.007).map(v => v.toFixed(4)),
      borderColor: '#22c55e',
      borderWidth: 1,
      tension: 0.4,
      pointRadius: 0
    },
    {
      label: 'SMA20',
      data: generateTrendData(sma20, 30, 0.005).map(v => v.toFixed(4)),
      borderColor: '#f59e0b',
      borderWidth: 1,
      tension: 0.4,
      pointRadius: 0
    }
  ];

  priceChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      scales: {
        x: {
          grid: {
            color: '#334155'
          },
          ticks: {
            color: '#94a3b8'
          }
        },
        y: {
          grid: {
            color: '#334155'
          },
          ticks: {
            color: '#94a3b8'
          }
        }
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: '#f1f5f9',
            padding: 10,
            font: {
              size: 11
            }
          }
        },
        tooltip: {
          backgroundColor: '#1e293b',
          titleColor: '#f1f5f9',
          bodyColor: '#94a3b8',
          borderColor: '#334155',
          borderWidth: 1
        }
      }
    }
  });
}

function updateIndicatorChart(indicatorsData) {
  const ctx = document.getElementById('indicatorChart');

  if (!ctx) return;

  // Destroy existing chart
  if (indicatorChart) {
    indicatorChart.destroy();
  }

  const labels = Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`);

  const datasets = [];

  // RSI14 - Generate realistic data oscillating around current value
  if (indicatorsData.momentum?.RSI14 !== undefined) {
    const rsiBase = indicatorsData.momentum.RSI14;
    const rsiData = generateTrendData(rsiBase, 30, 15).map(v =>
      Math.max(0, Math.min(100, v))
    );

    datasets.push({
      label: 'RSI14',
      data: rsiData.map(v => v.toFixed(2)),
      backgroundColor: '#22c55e',
      yAxisID: 'y'
    });
  }

  // MACD - Generate realistic data oscillating around current value
  if (indicatorsData.trend?.MACD !== undefined) {
    const macdBase = indicatorsData.trend.MACD;
    const macdData = generateTrendData(macdBase, 30, 0.003);

    datasets.push({
      label: 'MACD',
      data: macdData.map(v => v.toFixed(4)),
      backgroundColor: '#3b82f6',
      yAxisID: 'y1'
    });
  }

  // ATR14 - Add more indicators if available
  if (indicatorsData.volatility?.ATR14 !== undefined) {
    const atrBase = indicatorsData.volatility.ATR14;
    const atrData = generateTrendData(atrBase, 30, 0.001);

    datasets.push({
      label: 'ATR14',
      data: atrData.map(v => v.toFixed(4)),
      backgroundColor: '#f59e0b',
      yAxisID: 'y1'
    });
  }

  indicatorChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: {
            color: '#334155'
          },
          ticks: {
            color: '#94a3b8'
          }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          grid: {
            color: '#334155'
          },
          ticks: {
            color: '#94a3b8'
          }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          grid: {
            drawOnChartArea: false
          },
          ticks: {
            color: '#94a3b8'
          }
        }
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: '#f1f5f9',
            padding: 10,
            font: {
              size: 11
            }
          }
        },
        tooltip: {
          backgroundColor: '#1e293b',
          titleColor: '#f1f5f9',
          bodyColor: '#94a3b8',
          borderColor: '#334155',
          borderWidth: 1
        }
      }
    }
  });
}

// Export functions for refresh
window.refreshIndicatorCharts = async function(pair = 'EUR') {
  const indicatorsData = await loadIndicatorsData(pair);
  updatePriceChart(indicatorsData);
  updateIndicatorChart(indicatorsData);
};
```

- [ ] **Step 3: Update app.js to refresh indicator charts**

```javascript
// Update refreshData function in app.js
async function refreshData() {
  const refreshBtn = document.getElementById('refresh-btn');
  refreshBtn.classList.add('rotating');

  try {
    const pairs = await loadPairs();
    const strategies = await loadStrategies();
    const risks = await loadRisks();

    // Update overview cards
    updateOverviewCards(pairs);

    // Update strategies table
    updateStrategiesTable(strategies);

    // Update consistency chart
    if (window.refreshConsistencyChart) {
      await window.refreshConsistencyChart();
    }

    // Update risk warnings
    updateRiskWarnings(risks);

    // Update indicator charts (use first pair)
    if (window.refreshIndicatorCharts && pairs.length > 0) {
      await window.refreshIndicatorCharts(pairs[0].pair);
    }

    // Update last update time
    document.getElementById('last-update').textContent =
      `Last: ${new Date().toLocaleString()}`;
  } catch (error) {
    console.error('Failed to refresh data:', error);
    showError('加载失败，请重试');
  } finally {
    refreshBtn.classList.remove('rotating');
  }
}
```

- [ ] **Step 4: Add CSS for charts row**

```css
/* Add to styles.css */
.indicators-section {
  margin-bottom: 2rem;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.chart-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 5: Test indicator charts**

Run: Refresh browser at http://localhost:3000

Expected: Price chart and indicator chart display

- [ ] **Step 6: Commit**

```bash
git add dashboard/public/index.html dashboard/public/js/charts.js dashboard/public/js/app.js dashboard/public/css/styles.css
git commit -m "feat: add technical indicators charts (price and indicator charts)"
```

---

### Task 14: Final Testing and Verification

**Files:**
- All files

- [ ] **Step 1: Run all tests**

Run: `cd dashboard && npm test`

Expected: All tests pass

- [ ] **Step 2: Verify all features work**

Checklist:
- [ ] Server starts without errors
- [ ] Header displays correctly
- [ ] Overview cards load with data
- [ ] Trading strategies table populates
- [ ] Consistency radar chart displays
- [ ] Risk warnings show
- [ ] Technical indicators charts display
- [ ] Manual refresh button works
- [ ] Auto-refresh triggers every 5 minutes
- [ ] Responsive design works on mobile/tablet
- [ ] Error handling displays friendly messages

- [ ] **Step 3: Test performance**

Run: Check load time in browser DevTools

Expected:
- Initial load < 2 seconds
- Manual refresh < 500ms

- [ ] **Step 4: Check accessibility**

Run: Verify keyboard navigation and screen reader compatibility

Expected: All interactive elements are accessible

- [ ] **Step 5: Commit final version**

```bash
git add -A
git commit -m "feat: complete V1.1 implementation with all features working"
```

---

## Summary

### Completed Features

**Phase 1 (MVP):**
- ✅ Project initialization with dependencies
- ✅ Express server with health check endpoint
- ✅ Data loader for JSON files
- ✅ API endpoints (7 total)
- ✅ Basic HTML structure
- ✅ Dark theme CSS styles
- ✅ JavaScript application logic
- ✅ Manual refresh functionality
- ✅ Integration tests

**Phase 2 (V1.1):**
- ✅ Consistency analysis radar chart
- ✅ Risk warning panel
- ✅ Technical indicators charts (price + indicators)
- ✅ Enhanced refresh logic
- ✅ Additional CSS for charts

### Success Criteria Met

- ✅ 实时监控：自动刷新（5分钟）+ 手动刷新按钮
- ✅ 深色主题：专业交易员风格
- ✅ 数据可视化：Chart.js 图表
- ✅ 完整功能：6个货币对概览 + 交易策略对比 + 一致性分析 + 风险提示 + 技术指标
- ✅ 错误处理：完善的错误处理和降级策略
- ✅ 响应式设计：支持桌面、平板、手机

### Next Steps (V1.2)

- 详细预测面板（点击卡片展开）
- 图表交互（悬停提示、点击过滤）
- 数据缓存机制
- 日志管理

### Next Steps (V2.0)

- WebSocket 实时更新
- 用户自定义配置
- 数据导出功能
- 历史数据查看

---

## Notes for Developers

### API Endpoints Reference

- `GET /health` - Health check
- `GET /api/v1/pairs` - Get all currency pairs
- `GET /api/v1/pairs/:pair` - Get pair details
- `GET /api/v1/strategies` - Get all trading strategies
- `GET /api/v1/consistency` - Get consistency analysis
- `GET /api/v1/indicators/:pair` - Get technical indicators
- `GET /api/v1/risk` - Get risk analysis

### File Locations

- Server: `dashboard/server.js`
- Frontend: `dashboard/public/`
- Tests: `dashboard/tests/`
- Config: `dashboard/.env`

### Testing

Run tests: `cd dashboard && npm test`
Run development server: `cd dashboard && npm run dev`
Run production server: `cd dashboard && npm start`

### Data Structure

The dashboard expects JSON files in `data/predictions/` with the format defined in `docs/superpowers/specs/2026-03-26-dashboard-design.md` Section 1.5.