require('dotenv').config();
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const multer = require('multer');
const { logInfo, logError, requestLogger, errorLogger } = require('./logger');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  methods: process.env.ALLOWED_METHODS?.split(',') || ['GET', 'POST'],
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
          
          // Get all three horizon predictions for overview
          const predictions1d = data.ml_predictions?.['1_day'] || {};
          const predictions5d = data.ml_predictions?.['5_day'] || {};
          const predictions20d = data.ml_predictions?.['20_day'] || {};
          
          // Extract LLM analysis
          const llmAnalysis = data.llm_analysis || {};
          
          pairs.push({
            pair: data.metadata?.pair || pairCode,
            pair_name: data.metadata?.pair_name || `${pairCode}/USD`,
            current_price: data.metadata?.current_price,
            last_update: data.metadata?.data_date || new Date().toISOString(),
            // Use 1-day as main prediction for backward compatibility
            prediction: predictions1d.prediction_text || 'hold',
            probability: predictions1d.probability || 0.5,
            confidence: predictions1d.confidence || 'unknown',
            // Add multi-horizon predictions
            predictions: {
              '1d': {
                prediction: predictions1d.prediction_text || 'hold',
                probability: predictions1d.probability || 0.5,
                confidence: predictions1d.confidence || 'unknown'
              },
              '5d': {
                prediction: predictions5d.prediction_text || 'hold',
                probability: predictions5d.probability || 0.5,
                confidence: predictions5d.confidence || 'unknown'
              },
              '20d': {
                prediction: predictions20d.prediction_text || 'hold',
                probability: predictions20d.probability || 0.5,
                confidence: predictions20d.confidence || 'unknown'
              }
            },
            llm_analysis: {
              summary: llmAnalysis.summary || '',
              overall_assessment: llmAnalysis.overall_assessment || 'unknown',
              key_factors: llmAnalysis.key_factors || [],
              horizon_analysis: llmAnalysis.horizon_analysis || {}
            }
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
      const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      
      // Standardize the format to match loadAllPairs
      const predictions1d = data.ml_predictions?.['1_day'] || {};
      const predictions5d = data.ml_predictions?.['5_day'] || {};
      const predictions20d = data.ml_predictions?.['20_day'] || {};
      const llmAnalysis = data.llm_analysis || {};
      const tradingStrategies = data.trading_strategies || {};
      
      return {
        pair: data.metadata?.pair || pair,
        pair_name: data.metadata?.pair_name || `${pair}/USD`,
        current_price: data.metadata?.current_price || 0,
        last_update: data.metadata?.data_date || new Date().toISOString(),
        // Use 1-day as main prediction for backward compatibility
        prediction: predictions1d.prediction_text || 'hold',
        probability: predictions1d.probability || 0.5,
        confidence: predictions1d.confidence || 'unknown',
        // Add multi-horizon predictions
        predictions: {
          '1d': {
            prediction: predictions1d.prediction_text || 'hold',
            probability: predictions1d.probability || 0.5,
            confidence: predictions1d.confidence || 'unknown'
          },
          '5d': {
            prediction: predictions5d.prediction_text || 'hold',
            probability: predictions5d.probability || 0.5,
            confidence: predictions5d.confidence || 'unknown'
          },
          '20d': {
            prediction: predictions20d.prediction_text || 'hold',
            probability: predictions20d.probability || 0.5,
            confidence: predictions20d.confidence || 'unknown'
          }
        },
        llm_analysis: {
          summary: llmAnalysis.summary || '',
          overall_assessment: llmAnalysis.overall_assessment || 'unknown',
          key_factors: llmAnalysis.key_factors || [],
          horizon_analysis: llmAnalysis.horizon_analysis || {}
        },
        trading_strategies: tradingStrategies,
        // Add technical indicators and risk analysis
        technical_indicators: data.technical_indicators || {},
        risk_analysis: data.risk_analysis || {}
      };
    } catch (error) {
      console.error(`Error loading data for ${pair}:`, error);
      throw error;
    }
  }

  loadPairRaw(pair) {
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
      console.error(`Error loading raw data for ${pair}:`, error);
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
    
    // Return technical indicators directly from the data
    const indicators = data.technical_indicators || {};
    
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

// Configure multer for file uploads
const upload = multer({
  storage: multer.diskStorage({
    destination: function (req, file, cb) {
      // Save to data/raw directory
      const uploadDir = path.resolve(process.env.UPLOAD_DIR || '../data/raw');
      cb(null, uploadDir);
    },
    filename: function (req, file, cb) {
      // Keep original filename
      cb(null, file.originalname);
    }
  }),
  fileFilter: function (req, file, cb) {
    // Only accept .xlsx files
    if (file.mimetype === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
        file.originalname.endsWith('.xlsx')) {
      cb(null, true);
    } else {
      cb(new Error('只接受 .xlsx 格式的文件'), false);
    }
  },
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  }
});

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

// Get Chinese name for horizon
function getHorizonName(horizon) {
  const names = {
    '1': '短线（1天）',
    '5': '中线（5天）',
    '20': '长线（20天）'
  };
  return names[horizon] || `${horizon}天`;
}

// Upload data file endpoint
app.post('/api/v1/upload', upload.single('file'), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        error: {
          code: 'INVALID_REQUEST',
          message: '未上传文件'
        }
      });
    }

    const { filename, path: filePath, size } = req.file;
    logInfo(`File uploaded: ${filename}, size: ${size} bytes, path: ${filePath}`);

    // Clear cache to force reload with new data
    dataCache.clear();
    dataCache.clearByPattern('strategy_indicators:');
    logInfo('Cache cleared after file upload');

    res.json({
      success: true,
      message: '文件上传成功',
      file: {
        filename: filename,
        size: size,
        uploaded_at: new Date().toISOString()
      }
    });
  } catch (error) {
    logError(`Upload failed: ${error.message}`);
    res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: '文件上传失败'
      }
    });
  }
});

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
    
    // Load data - load raw data to access metadata and technical_indicators
    const rawData = dataLoader.loadPairRaw(pair);
    
    // Get technical indicators and trading strategies
    const indicators = rawData.technical_indicators || {};
    const metadata = rawData.metadata || {};
    const strategies = rawData.trading_strategies || {};
    
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

// Error handling middleware (must be last)
app.use(errorLogger);

// Start server
if (require.main === module) {
  app.listen(PORT, () => {
    logInfo(`Server started on port ${PORT}`);
    console.log(`Server running on port ${PORT}`);
    
    // 打印所有 API 端点信息
    console.log('\n================================================================================');
    console.log('可用的 API 端点');
    console.log('================================================================================\n');
    
    const apiEndpoints = [
      {
        method: 'GET',
        path: '/health',
        description: '健康检查',
        params: [],
        response: '{ status: "ok", uptime, timestamp }'
      },
      {
        method: 'GET',
        path: '/api/v1/pairs',
        description: '获取所有货币对信息',
        params: [],
        response: '{ pairs: [{ pair, pair_name, current_price, prediction, probability, confidence, llm_analysis }] }'
      },
      {
        method: 'GET',
        path: '/api/v1/pairs/:pair',
        description: '获取单个货币对详细信息',
        params: [
          { name: 'pair', type: 'string', description: '货币对代码 (EUR, JPY, AUD, GBP, CAD, NZD)' }
        ],
        response: '{ metadata, ml_predictions, consistency_analysis, llm_analysis, trading_strategies, technical_indicators, risk_analysis }'
      },
      {
        method: 'GET',
        path: '/api/v1/strategies',
        description: '获取所有交易策略',
        params: [],
        response: '{ strategies: { pair: [{ horizon, horizon_name, direction, entry_price, stop_loss, take_profit, recommendation, confidence, risk_reward_ratio, position_size }] } }'
      },
      {
        method: 'GET',
        path: '/api/v1/consistency',
        description: '获取一致性分析',
        params: [],
        response: '{ consistency: { pair: { score, interpretation, all_same, majority_trend, scores_by_horizon, technical_support, technical_indicators_summary } } }'
      },
      {
        method: 'GET',
        path: '/api/v1/indicators/:pair',
        description: '获取指定货币对的技术指标',
        params: [
          { name: 'pair', type: 'string', description: '货币对代码 (EUR, JPY, AUD, GBP, CAD, NZD)' }
        ],
        response: '{ pair, indicators: { trend, momentum, volatility, volume, price_pattern, market_environment } }'
      },
      {
        method: 'GET',
        path: '/api/v1/risk',
        description: '获取风险分析',
        params: [],
        response: '{ risks: { pair: { warnings, risk_level } } }'
      },
      {
        method: 'POST',
        path: '/api/v1/upload',
        description: '上传数据文件',
        params: [
          { name: 'file', type: 'file', description: 'Excel 文件 (.xlsx), 最大 10MB' }
        ],
        response: '{ success: true, message: "文件上传成功", file: { filename, size, uploaded_at } }'
      },
      {
        method: 'GET',
        path: '/api/v1/strategies/:pair/:horizon/indicators',
        description: '获取指定货币对和周期的关键技术指标',
        params: [
          { name: 'pair', type: 'string', description: '货币对代码 (EUR, JPY, AUD, GBP, CAD, NZD)' },
          { name: 'horizon', type: 'string', description: '预测周期 (1, 5, 20)' }
        ],
        response: '{ pair, pair_name, horizon, horizon_name, current_price, key_indicators, overall_summary }'
      }
    ];
    
    apiEndpoints.forEach((endpoint, index) => {
      console.log(`${index + 1}. ${endpoint.method} ${endpoint.path}`);
      console.log(`   描述: ${endpoint.description}`);
      
      if (endpoint.params.length > 0) {
        console.log('   参数:');
        endpoint.params.forEach(param => {
          console.log(`     - ${param.name} (${param.type}): ${param.description}`);
        });
      } else {
        console.log('   参数: 无');
      }
      
      console.log(`   响应: ${endpoint.response}`);
      console.log('');
    });
    
    console.log('================================================================================');
    console.log(`总计: ${apiEndpoints.length} 个 API 端点`);
    console.log('================================================================================\n');
  });
}

module.exports = app;