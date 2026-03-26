from typing import Dict, Any

import logging

logger = logging.getLogger(__name__)


class MultiHorizonPromptBuilder:
    """多周期 Prompt 构建器"""

    def __init__(self):
        """初始化构建器"""
        self.logger = logger