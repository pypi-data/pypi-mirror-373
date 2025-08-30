"""
剪映元数据提取器
实现剪映特定的数据提取逻辑
"""

import json
from typing import Dict, List, Any
from .extractor_base import MetadataExtractor, ExtractorConfig


class JianYingExtractor(MetadataExtractor):
    """剪映通用提取器"""

    def __init__(self, config: ExtractorConfig, data_type: str = "general"):
        super().__init__(config)
        self.data_type = data_type

    def parse_json_data(self) -> List[Dict[str, Any]]:
        """解析剪映JSON数据格式"""
        rows = []

        for line in self.source_content:
            line = line.strip()
            if not line:
                continue

            try:
                # 解析JSON数据
                data = json.loads(line)

                # 提取effect_item_list
                effect_items = data.get("data", {}).get("effect_item_list", [])

                # 遍历effect_items并提取所需属性
                for item in effect_items:
                    item_data = self.extract_item_data(item)
                    if item_data:
                        rows.append(item_data)

            except json.JSONDecodeError:
                print(f"Warning: Failed to parse line: {line[:100]}...")
                continue

        return rows

    def extract_item_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """提取item数据，子类可重写以处理特定格式"""
        return self.extract_common_fields(item)

    def save_output(self) -> None:
        """保存为JSON格式"""
        output_data = self.processed_data.to_dict('records')

        with open(self.config.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(output_data)} items to {self.config.output_file}")


class FontExtractor(JianYingExtractor):
    """字体提取器"""

    def __init__(self, source_file: str, output_file: str = None):
        config = ExtractorConfig(
            source_file=source_file,
            output_file=output_file,
            sort_by=["is_vip", "title"],
            name_field="title"
        )
        super().__init__(config, "fonts")


class TextAnimationExtractor(JianYingExtractor):
    """文本动画提取器"""

    def __init__(self, source_file: str, output_file: str = None):
        config = ExtractorConfig(
            source_file=source_file,
            output_file=output_file,
            sort_by=["is_vip", "name"],
            name_field="title"
        )
        super().__init__(config, "text_animations")

    def extract_item_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """提取文本动画特定数据"""
        base_data = super().extract_item_data(item)

        # 文本动画使用name字段而不是title
        base_data["name"] = base_data["title"]

        return base_data


class MaskExtractor(JianYingExtractor):
    """蒙版提取器"""

    def __init__(self, source_file: str, output_file: str = None):
        config = ExtractorConfig(
            source_file=source_file,
            output_file=output_file,
            sort_by=["is_vip", "name"],
            name_field="title"
        )
        super().__init__(config, "masks")

    def extract_item_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """提取蒙版特定数据"""
        base_data = super().extract_item_data(item)
        base_data["name"] = base_data["title"]
        return base_data


class FilterExtractor(JianYingExtractor):
    """滤镜提取器"""

    def __init__(self, source_file: str, output_file: str = None):
        config = ExtractorConfig(
            source_file=source_file,
            output_file=output_file,
            sort_by=["is_vip", "title"],
            name_field="title"
        )
        super().__init__(config, "filters")

    def extract_item_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """提取滤镜特定数据"""
        base_data = super().extract_item_data(item)

        # 提取参数信息
        sdk_extra = self.safe_json_loads(
            base_data["common_attr"].get("sdk_extra", "{}"), {}
        )
        param_list = sdk_extra.get("setting", {}).get("effect_adjust_params", [])

        base_data["params"] = [
            [param["effect_key"], param["default"], param["min"], param["max"]]
            for param in param_list
        ]

        return base_data


class TransitionExtractor(JianYingExtractor):
    """转场提取器"""

    def __init__(self, source_file: str, output_file: str = None):
        config = ExtractorConfig(
            source_file=source_file,
            output_file=output_file,
            sort_by=["is_vip", "name"],
            name_field="title"
        )
        super().__init__(config, "transitions")

    def extract_item_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """提取转场特定数据"""
        base_data = super().extract_item_data(item)

        # 提取转场特定信息
        sdk_extra = self.safe_json_loads(
            base_data["common_attr"].get("sdk_extra", "{}"), {}
        )
        transition_info = sdk_extra.get("transition", {})

        base_data.update({
            "name": base_data["title"],
            "default_duration": transition_info.get("defaultDura", 1.0),
            "is_overlap": transition_info.get("isOverlap", False)
        })

        return base_data


class VideoEffectExtractor(JianYingExtractor):
    """视频特效提取器"""

    def __init__(self, source_file: str, output_file: str = None):
        config = ExtractorConfig(
            source_file=source_file,
            output_file=output_file,
            sort_by=["is_vip", "title"],
            name_field="title"
        )
        super().__init__(config, "video_effects")

    def extract_item_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """提取视频特效特定数据"""
        base_data = super().extract_item_data(item)

        # 提取参数信息
        sdk_extra = self.safe_json_loads(
            base_data["common_attr"].get("sdk_extra", "{}"), {}
        )
        param_list = sdk_extra.get("setting", {}).get("effect_adjust_params", [])

        base_data["params"] = [
            [param["effect_key"], param["default"], param["min"], param["max"]]
            for param in param_list
        ]

        return base_data


class AudioEffectExtractor(JianYingExtractor):
    """音频特效提取器"""

    def __init__(self, source_file: str, output_file: str = None):
        config = ExtractorConfig(
            source_file=source_file,
            output_file=output_file,
            sort_by=["is_vip", "effect_name"],
            name_field="name"
        )
        super().__init__(config, "audio_effects")

    def parse_json_data(self) -> List[Dict[str, Any]]:
        """解析音频特效的特殊JSON格式"""
        rows = []

        try:
            # 音频特效是单个JSON文件，不是按行的JSON
            content = "".join(self.source_content)
            data = json.loads(content)

            # 提取effects列表
            effect_items = data.get("data", {}).get("effects", [])

            for item in effect_items:
                item_data = self.extract_item_data(item)
                if item_data:
                    rows.append(item_data)

        except json.JSONDecodeError as e:
            print(f"Error parsing audio effects JSON: {e}")

        return rows

    def extract_item_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """提取音频特效特定数据"""
        extra = self.safe_json_loads(item.get("extra", "{}"), {})

        # 只提取"音色"类型的特效
        if "is_voice_conversion" not in extra:
            return None

        # 提取参数信息
        sdk_extra = self.safe_json_loads(item.get("sdk_extra", "{}"), {})
        param_list = sdk_extra.get("setting", {}).get("audio_effect_parameters_change", [])

        return {
            "effect_name": item.get("name", ""),
            "name": item.get("name", ""),
            "is_vip": extra.get("is_vip", False),
            "resource_id": item.get("resource_id", ""),
            "effect_id": item.get("effect_id", ""),
            "md5": item.get("id", ""),
            "params": [
                [param["sliderName"], param["defaultValue"], param["minValue"], param["maxValue"]]
                for param in param_list
            ]
        }