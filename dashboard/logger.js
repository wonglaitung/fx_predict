const fs = require('fs');
const path = require('path');

const LOG_DIR = path.join(__dirname, 'logs');
const ACCESS_LOG = path.join(LOG_DIR, 'access.log');
const ERROR_LOG = path.join(LOG_DIR, 'error.log');

// Ensure log directory exists
if (!fs.existsSync(LOG_DIR)) {
  fs.mkdirSync(LOG_DIR, { recursive: true });
}

// Log levels
const LOG_LEVELS = {
  INFO: 'INFO',
  ERROR: 'ERROR',
  WARN: 'WARN'
};

function formatMessage(level, message) {
  const timestamp = new Date().toISOString();
  return `[${timestamp}] [${level}] ${message}\n`;
}

function logToFile(filePath, message) {
  try {
    fs.appendFileSync(filePath, message);
  } catch (error) {
    console.error('Failed to write to log file:', error);
  }
}

function logInfo(message) {
  const formatted = formatMessage(LOG_LEVELS.INFO, message);
  console.log(formatted.trim());
  logToFile(ACCESS_LOG, formatted);
}

function logError(message) {
  const formatted = formatMessage(LOG_LEVELS.ERROR, message);
  console.error(formatted.trim());
  logToFile(ERROR_LOG, formatted);
}

function logWarn(message) {
  const formatted = formatMessage(LOG_LEVELS.WARN, message);
  console.warn(formatted.trim());
  logToFile(ACCESS_LOG, formatted);
}

// Request logging middleware
function requestLogger(req, res, next) {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    const message = `${req.method} ${req.url} ${res.statusCode} ${duration}ms`;
    logInfo(message);
  });
  
  next();
}

// Error logging middleware
function errorLogger(err, req, res, next) {
  logError(`${err.name}: ${err.message}\nStack: ${err.stack}`);
  
  // Send generic error to client
  res.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message: '服务器内部错误'
    }
  });
}

module.exports = {
  logInfo,
  logError,
  logWarn,
  requestLogger,
  errorLogger
};