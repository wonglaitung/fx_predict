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


# 技术指标配置
INDICATOR_CONFIG = {
    'SMA': {'periods': [5, 10, 20, 50]},
    'EMA': {'periods': [12, 26]},
    'RSI': {'period': 14},
    'MACD': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
    'ADX': {'period': 14},
    'ATR': {'period': 14},
    'Bollinger': {'period': 20, 'std_dev': 2},
    'OBV': {},
    'KDJ': {'period': 9, 'm1': 3, 'm2': 3},
    'CCI': {'period': 20},
    'WilliamsR': {'period': 14}
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