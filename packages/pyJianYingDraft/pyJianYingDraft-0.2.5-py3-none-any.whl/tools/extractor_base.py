"""
元数据提取器基类
定义统一的提取接口和通用功能
"""

import json
import pandas as pd
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Union


@dataclass
class ExtractorConfig:
    """提取器配置"""
    source_file: Union[str, Path]
    """源数据文件路径"""

    output_file: Optional[Union[str, Path]] = None
    """输出文件路径，如果为None则不自动保存"""

    sort_by: List[str] = field(default_factory=lambda: ["is_vip", "name"])
    """排序字段"""

    dedup_by: str = "resource_id"
    """去重字段"""

    name_field: str = "title"
    """名称字段"""


class MetadataExtractor(ABC):
    """元数据提取器基类"""

    def __init__(self, config: ExtractorConfig):
        self.config = config
        self.raw_data: List[Dict[str, Any]] = []
        self.processed_data: pd.DataFrame = pd.DataFrame()

    def extract(self) -> pd.DataFrame:
        """执行完整的提取流程"""
        self.load_source_data()
        self.raw_data = self.parse_json_data()
        self.processed_data = self.process_data()

        if self.config.output_file:
            self.save_output()

        return self.processed_data

    def load_source_data(self) -> None:
        """加载源数据文件"""
        with open(self.config.source_file, 'r', encoding='utf-8') as f:
            self.source_content = f.readlines()

    @abstractmethod
    def parse_json_data(self) -> List[Dict[str, Any]]:
        """解析JSON数据，提取所需字段"""
        pass

    @abstractmethod
    def extract_item_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """从单个item中提取数据"""
        pass

    def process_data(self) -> pd.DataFrame:
        """处理数据：排序、去重等"""
        df = pd.DataFrame(self.raw_data)

        if len(df) == 0:
            return df

        # 排序
        if self.config.sort_by:
            available_cols = [col for col in self.config.sort_by if col in df.columns]
            if available_cols:
                df = df.sort_values(by=available_cols, ascending=True)

        # 去重
        if self.config.dedup_by and self.config.dedup_by in df.columns:
            df = df.drop_duplicates(subset=[self.config.dedup_by])

        return df.reset_index(drop=True)

    @abstractmethod
    def save_output(self) -> None:
        """保存输出文件"""
        pass

    @staticmethod
    def pad_to_length(s: str, length: int, pad_char: str = " ") -> str:
        """字符串填充，考虑中文字符宽度"""
        non_ascii_count = sum(1 for c in s if ord(c) > 127)
        return s.ljust(length - non_ascii_count, pad_char)

    @staticmethod
    def safe_json_loads(json_str: str, default: Any = None) -> Any:
        """安全解析JSON字符串"""
        try:
            if not json_str:
                return default or {}
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return default or {}

    @staticmethod
    def clean_identifier(name: str) -> str:
        """清理标识符名称，用于Python变量名"""
        cleaned = name.replace(' ', '_').replace('-', '_').replace('.', '_')
        # 如果以数字开头，添加下划线前缀
        if cleaned and cleaned[0].isdigit():
            cleaned = "_" + cleaned
        return cleaned

    def extract_common_fields(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """提取通用字段"""
        common_attr = item.get("common_attr", {})
        business_info = self.safe_json_loads(
            common_attr.get("business_info", {}).get("json_str", "{}"), {}
        )

        return {
            "name": common_attr.get(self.config.name_field, ""),
            "title": common_attr.get("title", ""),
            "is_vip": business_info.get("is_vip", False),
            "resource_id": common_attr.get("id", ""),
            "effect_id": common_attr.get("effect_id", ""),
            "md5": common_attr.get("md5", ""),
            "common_attr": common_attr,
            "business_info": business_info
        }