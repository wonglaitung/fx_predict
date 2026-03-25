import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FXDataLoader:
    """外汇数据加载器"""

    def __init__(self):
        """初始化加载器"""
        self.logger = logger

    def load_pair(self, pair: str, file_path: str) -> pd.DataFrame:
        """
        加载单个货币对数据

        Args:
            pair: 货币对代码，对应 Excel 工作表名称（如 'EUR', 'JPY', 'AUD' 等）
            file_path: Excel 文件路径

        Returns:
            DataFrame，包含 Date、Close、SMA5、SMA10、SMA20 等列

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 数据格式错误或工作表不存在

        Notes:
            - pair 参数对应 Excel 的工作表名称
            - 返回的数据已按日期升序排序（旧数据在前）
            - 缺失值已使用前向填充处理
        """
        # 检查文件是否存在
        if not Path(file_path).exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            # 读取 Excel 文件
            df = pd.read_excel(file_path, sheet_name=pair)

            # 预处理数据
            df = self._preprocess(df)

            # 验证数据格式
            if not self._validate_data_format(df):
                raise ValueError("数据格式验证失败")

            self.logger.info(f"成功加载货币对 {pair}，共 {len(df)} 条记录")
            return df

        except ValueError as e:
            if "Worksheet named" in str(e):
                raise ValueError(f"工作表不存在: {pair}") from e
            raise ValueError(f"数据格式错误: {e}") from e
        except Exception as e:
            raise ValueError(f"加载数据失败: {e}") from e

    def load_all_pairs(self, file_path: str) -> dict:
        """
        加载所有货币对数据

        Args:
            file_path: Excel 文件路径

        Returns:
            字典 {pair_code: DataFrame}
        """
        # 获取所有工作表名称
        xls = pd.ExcelFile(file_path)
        all_pairs = {}

        for sheet_name in xls.sheet_names:
            try:
                df = self.load_pair(sheet_name, file_path)
                all_pairs[sheet_name] = df
                self.logger.info(f"已加载货币对: {sheet_name}")
            except Exception as e:
                self.logger.warning(f"加载货币对 {sheet_name} 失败: {e}")

        self.logger.info(f"成功加载 {len(all_pairs)} 个货币对")
        return all_pairs

    def _preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        预处理数据

        - 日期格式化（MM/DD/YYYY → datetime）
        - 数据排序（升序：旧数据在前）
        - 缺失值处理（前向填充）
        - 数据类型转换

        Args:
            df: 原始数据

        Returns:
            预处理后的数据
        """
        # 移除不需要的列（如 Unnamed: 0）
        df = df.drop(columns=['Unnamed: 0'], errors='ignore')

        # 转换日期格式
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')

        # 转换数值列
        numeric_columns = ['Close', 'SMA5', 'SMA10', 'SMA20']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 按日期升序排序（旧数据在前）
        if 'Date' in df.columns:
            df = df.sort_values('Date', ascending=True).reset_index(drop=True)

        # 前向填充缺失值
        df = df.ffill()

        return df

    def _validate_data_format(self, df: pd.DataFrame) -> bool:
        """
        验证数据格式

        Args:
            df: 待验证的数据

        Returns:
            True 如果数据格式有效，False 否则
        """
        # 检查必需的列
        required_columns = ['Date', 'Close']
        for col in required_columns:
            if col not in df.columns:
                self.logger.error(f"缺少必需列: {col}")
                return False

        # 检查日期格式
        if df['Date'].dtype != 'datetime64[ns]':
            self.logger.error("Date 列不是 datetime 类型")
            return False

        # 检查 Close 是否为数值类型
        if not pd.api.types.is_numeric_dtype(df['Close']):
            self.logger.error("Close 列不是数值类型")
            return False

        return True