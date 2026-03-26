require('dotenv').config();
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { logInfo, logError, requestLogger, errorLogger } = require('./logger');

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
app.use(requestLogger);

// DataCache class
class DataCache {
  constructor(ttl = 300000) { // Default 5 minutes
    this.cache = new Map();
    this.ttl = ttl;
  }

  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key);
      logInfo(`Cache expired for key: ${key}`);
      return null;
    }

    logInfo(`Cache hit for key: ${key}`);
    return item.data;
  }

  set(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
    logInfo(`Cache set for key: ${key}`);
  }

  clear() {
    this.cache.clear();
    logInfo('Cache cleared');
  }

  clearByPattern(pattern) {
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
        logInfo(`Cache cleared for pattern: ${pattern}`);
      }
    }
  }
}

// DataLoader class
class DataLoader {
  constructor(dataDir, cache) {
    this.dataDir = dataDir;
    this.cache = cache;
  }

  loadAllPairs() {
    const validPairs = ['EUR', 'JPY', 'AUD', 'GBP', 'CAD', 'NZD'];
    const pairs = [];
    const seenPairs = new Set();

    try {
      const files = fs.readdirSync(this.dataDir)
        .filter(f => f.endsWith('.json'));

      // Sort files to get the latest one for each pair
      files.sort().reverse();

      files.forEach(file => {
        const pairCode = file.split('_')[0];
        if (validPairs.includes(pairCode) && !seenPairs.has(pairCode)) {
          const filePath = path.join(this.dataDir, file);
          const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
          
          // Get the 5-day prediction as the main prediction for overview
          const mainPrediction = data.ml_predictions?.['5_day'] || data.ml_predictions?.['1_day'] || {};
          
          pairs.push({
            pair: data.metadata?.pair || pairCode,
            pair_name: data.metadata?.pair_name || `${pairCode}/USD`,
            current_price: data.metadata?.current_price,
            last_update: data.metadata?.data_date || new Date().toISOString(),
            prediction: mainPrediction.prediction_text || 'hold',
            probability: mainPrediction.probability || 0.5,
            confidence: mainPrediction.confidence || 'unknown'
          });
          seenPairs.add(pairCode);
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

const dataCache = new DataCache(parseInt(process.env.CACHE_TTL) || 300000);
const dataLoader = new DataLoader(process.env.DATA_DIR || '../data/predictions', dataCache);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

// Get all pairs
app.get('/api/v1/pairs', (req, res) => {
  try {
    const cached = dataCache.get('pairs');
    if (cached) {
      return res.json({ pairs: cached });
    }

    const pairs = dataLoader.loadAllPairs();
    dataCache.set('pairs', pairs);
    logInfo(`Loaded ${pairs.length} pairs`);
    res.json({ pairs });
  } catch (error) {
    logError(`Failed to load pairs: ${error.message}`);
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
    const cacheKey = `pair:${pair}`;
    
    const cached = dataCache.get(cacheKey);
    if (cached) {
      return res.json(cached);
    }

    const data = dataLoader.loadPair(pair);
    dataCache.set(cacheKey, data);
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

// Get all trading strategies
app.get('/api/v1/strategies', (req, res) => {
  try {
    const pairs = dataLoader.loadAllPairs();
    const strategies = {};

    pairs.forEach(pair => {
      try {
        const data = dataLoader.loadPair(pair.pair);
        // Convert strategy object to array format
        const strategyObj = data.trading_strategies || {};
        const strategyArray = [
          { 
            ...strategyObj.short_term, 
            horizon: 1, 
            horizon_name: 'short_term',
            direction: strategyObj.short_term?.recommendation || 'hold'
          },
          { 
            ...strategyObj.medium_term, 
            horizon: 5, 
            horizon_name: 'medium_term',
            direction: strategyObj.medium_term?.recommendation || 'hold'
          },
          { 
            ...strategyObj.long_term, 
            horizon: 20, 
            horizon_name: 'long_term',
            direction: strategyObj.long_term?.recommendation || 'hold'
          }
        ].filter(s => s.name); // Filter out empty strategies
        strategies[pair.pair] = strategyArray;
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

// Get technical indicators for a specific pair
app.get('/api/v1/indicators/:pair', (req, res) => {
  try {
    const { pair } = req.params;
    const data = dataLoader.loadPair(pair);
    
    // Map indicator names from Chinese to English if needed
    const indicators = {};
    if (data.llm_analysis && data.llm_analysis.horizon_analysis) {
      data.llm_analysis.horizon_analysis.forEach(ha => {
        indicators[ha.horizon] = ha.technical_indicators || {};
      });
    }
    
    res.json({ pair, indicators });
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
          message: 'Failed to load indicators'
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
        risks[pair.pair] = {
          warnings: data.risk_analysis?.warnings || [],
          risk_level: data.risk_analysis?.risk_level || 'unknown'
        };
      } catch (error) {
        risks[pair.pair] = { warnings: [], risk_level: 'unknown' };
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

// Error handling middleware (must be last)
app.use(errorLogger);

// Start server
if (require.main === module) {
  app.listen(PORT, () => {
    logInfo(`Server started on port ${PORT}`);
    console.log(`Server running on port ${PORT}`);
  });
}

module.exports = app;