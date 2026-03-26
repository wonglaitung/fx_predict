import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime, timedelta

from data_services.technical_analysis import TechnicalAnalyzer
from ml_services.fx_trading_model import FXTradingModel

import logging

logger = logging.getLogger(__name__)


class MultiHorizonContextBuilder:
    """多周期上下文构建器"""

    def __init__(self):
        """初始化构建器"""
        self.technical_analyzer = TechnicalAnalyzer()
        self.model = FXTradingModel()
        self.logger = logger