require('dotenv').config();
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

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

// Start server
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
}

module.exports = app;