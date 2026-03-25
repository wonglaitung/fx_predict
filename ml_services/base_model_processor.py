import os
import pickle
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BaseModelProcessor:
    """基础模型处理器"""

    def __init__(self, model_dir: str = 'data/models'):
        self.model_dir = Path(model_dir)
        self.logger = logger

        # 确保模型目录存在
        self.model_dir.mkdir(parents=True, exist_ok=True)

    def save_model(self, model: Any, pair: str, model_name: str = 'model'):
        """
        保存模型

        Args:
            model: 模型对象
            pair: 货币对代码
            model_name: 模型名称
        """
        file_path = self.model_dir / f"{pair}_{model_name}.pkl"

        try:
            with open(file_path, 'wb') as f:
                pickle.dump(model, f)
            self.logger.info(f"模型已保存: {file_path}")
        except Exception as e:
            self.logger.error(f"保存模型失败: {e}")
            raise

    def load_model(self, pair: str, model_name: str = 'model') -> Any:
        """
        加载模型

        Args:
            pair: 货币对代码
            model_name: 模型名称

        Returns:
            模型对象

        Raises:
            FileNotFoundError: 模型文件不存在
        """
        file_path = self.model_dir / f"{pair}_{model_name}.pkl"

        if not file_path.exists():
            raise FileNotFoundError(f"模型文件不存在: {file_path}")

        try:
            with open(file_path, 'rb') as f:
                model = pickle.load(f)
            self.logger.info(f"模型已加载: {file_path}")
            return model
        except Exception as e:
            self.logger.error(f"加载模型失败: {e}")
            raise

    def model_exists(self, pair: str, model_name: str = 'model') -> bool:
        """
        检查模型是否存在

        Args:
            pair: 货币对代码
            model_name: 模型名称

        Returns:
            是否存在
        """
        file_path = self.model_dir / f"{pair}_{model_name}.pkl"
        return file_path.exists()