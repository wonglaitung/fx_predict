import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ml_services.multi_horizon_context import MultiHorizonContextBuilder
from data_services.technical_analysis import TechnicalAnalyzer
from ml_services.fx_trading_model import FXTradingModel


def test_context_builder_initialization():
    """测试 MultiHorizonContextBuilder 初始化"""
    builder = MultiHorizonContextBuilder()
    assert builder is not None
    assert builder.technical_analyzer is not None
    assert builder.model is not None