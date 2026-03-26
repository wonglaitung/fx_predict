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

// DataLoader class
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
            current_price: data.metadata?.current_price,
            last_update: data.metadata?.analysis_date || new Date().toISOString()
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
    const pairs = dataLoader.loadAllPairs();
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