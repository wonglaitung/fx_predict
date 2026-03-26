import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class JSONFormatter:
    """JSON 格式化器"""

    def __init__(self):
        """初始化格式化器"""
        self.logger = logger