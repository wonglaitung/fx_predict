import os
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# 货币对配置
CURRENCY_PAIRS = {
    'EUR': {'symbol': 'EURUSD', 'name': '欧元/美元'},
    'JPY': {'symbol': 'USDJPY', 'name': '美元/日元'},
    'AUD': {'symbol': 'AUDUSD', 'name': '澳元/美元'},
    'GBP': {'symbol': 'GBPUSD', 'name': '英镑/美元'},
    'CAD': {'symbol': 'USDCAD', 'name': '美元/加元'},
    'NZD': {'symbol': 'NZDUSD', 'name': '新西兰元/美元'}
}


# 信号配置
SIGNAL_CONFIG = {
    'buy_threshold': 60,
    'sell_threshold': 40,
    'ml_probability_threshold': 0.60
}


# 路径配置
PATHS = {
    'data_dir': 'data',
    'model_dir': 'data/models',
    'prediction_dir': 'data/predictions',
    'log_file': 'fx_predict.log'
}


# 模型配置
MODEL_CONFIG = {
    'horizon': 20,  # 预测周期（天）
    'high_confidence_threshold': 0.60,  # 高置信度阈值
    'catboost_params': {
        'iterations': 1000,
        'depth': 6,
        'learning_rate': 0.05,
        'l2_leaf_reg': 3,
        'random_seed': 42,
        'verbose': False,
        'loss_function': 'Logloss',
        'eval_metric': 'Accuracy'
    }
}


# 技术指标配置（30-40个指标）
INDICATOR_CONFIG = {
    # 趋势类指标
    'SMA': {'periods': [5, 10, 20, 50, 120]},
    'EMA': {'periods': [5, 10, 12, 20, 26]},
    'MACD': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
    'ADX': {'period': 14},
    
    # 动量类指标
    'RSI': {'period': 14},
    'KDJ': {'period': 9, 'm1': 3, 'm2': 3},
    'WilliamsR': {'period': 14},
    'CCI': {'period': 20},
    
    # 波动类指标
    'ATR': {'period': 14},
    'Bollinger': {'period': 20, 'std_dev': 2},
    'Std_20d': {'period': 20},
    'Volatility_20d': {'period': 20},
    
    # 成交量类指标
    'OBV': {},
    
    # 价格形态指标
    'Price_Percentile': {'period': 120},
    'Bias_Rates': {'periods': [5, 10, 20]},
    
    # 市场环境指标
    'Trend_Slope': {'period': 20},
    'MA_Alignment': {}
}


# 数据配置
DATA_CONFIG = {
    'supported_pairs': ['EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'NZD'],
    'pair_symbols': {
        'EUR': 'EURUSD',
        'JPY': 'USDJPY',
        'GBP': 'GBPUSD',
        'AUD': 'AUDUSD',
        'CAD': 'USDCAD',
        'CHF': 'USDCHF',
        'NZD': 'NZDUSD'
    },
    'min_data_points': 100,
    'train_test_split': 0.8
}


# 大模型配置
LLM_CONFIG = {
    'api_key': os.getenv('QWEN_API_KEY', ''),
    'chat_url': os.getenv('QWEN_CHAT_URL',
                         'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'),
    'chat_model': os.getenv('QWEN_CHAT_MODEL', 'qwen-plus-2025-12-01'),
    'max_tokens': int(os.getenv('MAX_TOKENS', 32768)),
    'enable_thinking': True
}


def validate_config():
    """
    验证配置有效性

    Returns:
        bool: 配置是否有效
    """
    # 验证模型配置
    if MODEL_CONFIG['horizon'] <= 0:
        logger.error("预测周期必须大于0")
        return False

    if not (0 < MODEL_CONFIG['high_confidence_threshold'] <= 1):
        logger.error("高置信度阈值必须在(0, 1]范围内")
        return False

    # 验证数据配置
    if DATA_CONFIG['min_data_points'] < 50:
        logger.error("最小数据点数不能少于50")
        return False

    # 验证技术指标配置
    if not INDICATOR_CONFIG:
        logger.error("技术指标配置不能为空")
        return False

    # 验证货币对配置
    if not CURRENCY_PAIRS:
        logger.error("货币对配置不能为空")
        return False

    # 验证信号配置
    if not (0 <= SIGNAL_CONFIG['buy_threshold'] <= 100):
        logger.error("买入阈值必须在0-100范围内")
        return False

    if not (0 <= SIGNAL_CONFIG['sell_threshold'] <= 100):
        logger.error("卖出阈值必须在0-100范围内")
        return False

    if not (0 < SIGNAL_CONFIG['ml_probability_threshold'] <= 1):
        logger.error("ML概率阈值必须在(0, 1]范围内")
        return False

    # 验证路径配置
    required_paths = ['data_dir', 'model_dir', 'prediction_dir']
    for path_key in required_paths:
        if path_key not in PATHS or not PATHS[path_key]:
            logger.error(f"路径配置缺少必需项: {path_key}")
            return False

    # 验证大模型配置
    if not LLM_CONFIG['api_key']:
        logger.warning("未设置 QWEN_API_KEY，大模型功能将不可用")

    logger.info("配置验证通过")
    return True


if __name__ == '__main__':
    if validate_config():
        print("配置验证通过")
    else:
        print("配置验证失败")