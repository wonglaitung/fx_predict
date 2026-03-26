import json
import logging

logger = logging.getLogger(__name__)


class LLMAnalysisParser:
    """LLM 输出解析器"""

    def __init__(self):
        """初始化解析器"""
        self.logger = logger