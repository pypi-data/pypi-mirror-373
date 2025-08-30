"""
代码生成器
用于将提取的元数据生成Python代码
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from .extractor_base import MetadataExtractor


class CodeGenerator:
    """Python代码生成器"""
    
    def __init__(self, data: pd.DataFrame, data_type: str):
        self.data = data
        self.data_type = data_type
    
    def generate_enum_code(self, 
                          class_name: str, 
                          base_class: str = "EffectEnum",
                          meta_class: str = "EffectMeta") -> str:
        """生成枚举类代码"""
        
        # 生成头部
        header = f'''"""记录剪映{self.data_type}元数据, 此文件的内容主要由程序生成"""

from .effect_meta import {base_class}
from .effect_meta import {meta_class}

class {class_name}({base_class}):
'''
        
        # 生成枚举项
        items = []
        for _, row in self.data.iterrows():
            item_code = self._generate_item_code(row, meta_class)
            if item_code:
                items.append(item_code)
        
        return header + "\n".join(items)
    
    def _generate_item_code(self, row: pd.Series, meta_class: str) -> str:
        """生成单个枚举项代码"""
        name = self._clean_identifier(row.get('name', row.get('title', '')))
        title = row.get('title', row.get('name', ''))
        is_vip = row.get('is_vip', False)
        resource_id = row.get('resource_id', '')
        effect_id = row.get('effect_id', '')
        md5 = row.get('md5', '')
        
        # 根据数据类型生成不同的代码
        if self.data_type == "fonts":
            return self._generate_font_item(name, title, is_vip, resource_id, effect_id, md5, meta_class)
        elif self.data_type == "text_animations":
            duration = row.get('animation_duration', 0.0)
            return self._generate_animation_item(name, title, is_vip, duration, resource_id, effect_id, md5)
        elif self.data_type == "transitions":
            duration = row.get('default_duration', 1.0)
            is_overlap = row.get('is_overlap', False)
            return self._generate_transition_item(name, title, is_vip, resource_id, effect_id, md5, duration, is_overlap)
        elif self.data_type in ["filters", "video_effects"]:
            params = row.get('params', [])
            return self._generate_effect_with_params(name, title, is_vip, resource_id, effect_id, md5, params, meta_class)
        elif self.data_type == "audio_effects":
            params = row.get('params', [])
            return self._generate_audio_effect(name, title, is_vip, resource_id, effect_id, md5, params)
        else:
            # 默认简单特效
            return self._generate_simple_effect(name, title, is_vip, resource_id, effect_id, md5, meta_class)
    
    def _generate_font_item(self, name: str, title: str, is_vip: bool, 
                           resource_id: str, effect_id: str, md5: str, meta_class: str) -> str:
        """生成字体项"""
        padded_name = self._pad_to_length(name, 20)
        return f'    {padded_name}= {meta_class}("{title}", {is_vip}, "{resource_id}", "{effect_id}", "{md5}")'
    
    def _generate_animation_item(self, name: str, title: str, is_vip: bool, duration: float,
                               resource_id: str, effect_id: str, md5: str) -> str:
        """生成动画项"""
        padded_name = self._pad_to_length(name, 12)
        return f'    {padded_name}= Animation_meta("{title}", {is_vip}, {duration:.3f}, "{resource_id}", "{effect_id}", "{md5}")'
    
    def _generate_transition_item(self, name: str, title: str, is_vip: bool,
                                resource_id: str, effect_id: str, md5: str, 
                                duration: float, is_overlap: bool) -> str:
        """生成转场项"""
        padded_name = self._pad_to_length(name, 12)
        code = f'    {padded_name}= Transition_meta("{title}", {is_vip}, "{resource_id}", "{effect_id}", "{md5}", {duration:.6f}, {is_overlap})\n'
        code += f'    """默认时长: {duration:.2f}s"""\n'
        return code
    
    def _generate_effect_with_params(self, name: str, title: str, is_vip: bool,
                                   resource_id: str, effect_id: str, md5: str, 
                                   params: List, meta_class: str) -> str:
        """生成带参数的特效项"""
        padded_name = self._pad_to_length(name, 12)
        
        # 生成参数字符串
        param_str = ""
        annotation_str = '    """参数:\n'
        
        if params:
            param_lines = []
            for param in params:
                if len(param) >= 4:
                    param_lines.append(f'                            Effect_param("{param[0]}", {param[1]:.3f}, {param[2]:.3f}, {param[3]:.3f})')
                    annotation_str += f'        - {param[0]}: 默认{param[1]:.2f}, {param[2]:.2f} ~ {param[3]:.2f}\n'
            
            if param_lines:
                param_str = "[\n" + ",\n".join(param_lines) + "\n                        ]"
                annotation_str += '    """\n'
            else:
                param_str = "[]"
                annotation_str = ""
        else:
            param_str = "[]"
            annotation_str = ""
        
        code = f'    {padded_name}= {meta_class}("{title}", {is_vip}, "{resource_id}", "{effect_id}", "{md5}", {param_str})\n'
        if annotation_str and annotation_str != '    """参数:\n    """\n':
            code += annotation_str
        
        return code
    
    def _generate_audio_effect(self, name: str, title: str, is_vip: bool,
                             resource_id: str, effect_id: str, md5: str, params: List) -> str:
        """生成音频特效项"""
        padded_name = self._pad_to_length(name, 12)
        
        # 生成参数字符串
        param_str = ""
        annotation_str = '    """参数:\n'
        
        if params:
            param_lines = []
            for param in params:
                if len(param) >= 4:
                    param_lines.append(f'                            Audio_effect_param("{param[0]}", {param[1]:.3f}, {param[2]:.3f}, {param[3]:.3f})')
                    annotation_str += f'        - {param[0]}: 默认{param[1]:.2f}, {param[2]:.2f} ~ {param[3]:.2f}\n'
            
            if param_lines:
                param_str = "[\n" + ",\n".join(param_lines) + "\n                        ]"
                annotation_str += '    """\n'
            else:
                param_str = "[]"
                annotation_str = ""
        else:
            param_str = "[]"
            annotation_str = ""
        
        code = f'    {padded_name}= Audio_effect_meta("{title}", {is_vip}, "{resource_id}", "{effect_id}", "{md5}", {param_str})\n'
        if annotation_str and annotation_str != '    """参数:\n    """\n':
            code += annotation_str
        
        return code
    
    def _generate_simple_effect(self, name: str, title: str, is_vip: bool,
                              resource_id: str, effect_id: str, md5: str, meta_class: str) -> str:
        """生成简单特效项"""
        padded_name = self._pad_to_length(name, 12)
        return f'    {padded_name}= {meta_class}("{title}", {is_vip}, "{resource_id}", "{effect_id}", "{md5}", [])'
    
    @staticmethod
    def _pad_to_length(s: str, length: int, pad_char: str = " ") -> str:
        """字符串填充，考虑中文字符宽度"""
        non_ascii_count = sum(1 for c in s if ord(c) > 127)
        return s.ljust(length - non_ascii_count, pad_char)
    
    @staticmethod
    def _clean_identifier(name: str) -> str:
        """清理标识符名称，用于Python变量名"""
        cleaned = name.replace(' ', '_').replace('-', '_').replace('.', '_')
        # 如果以数字开头，添加下划线前缀
        if cleaned and cleaned[0].isdigit():
            cleaned = "_" + cleaned
        return cleaned
    
    def save_to_file(self, output_file: str, class_name: str, 
                    base_class: str = "EffectEnum", meta_class: str = "EffectMeta") -> None:
        """保存代码到文件"""
        code = self.generate_enum_code(class_name, base_class, meta_class)
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"Generated {len(self.data)} items to {output_file}")


class LegacyCodeGenerator:
    """兼容旧版代码生成格式的生成器"""
    
    @staticmethod
    def generate_from_extractor(extractor: MetadataExtractor, output_file: str, 
                              template_type: str = "effect") -> None:
        """从提取器生成代码（兼容旧版格式）"""
        data = extractor.extract()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for _, row in data.iterrows():
                if template_type == "font":
                    LegacyCodeGenerator._write_font_line(f, row)
                elif template_type == "animation":
                    LegacyCodeGenerator._write_animation_line(f, row)
                elif template_type == "transition":
                    LegacyCodeGenerator._write_transition_line(f, row)
                elif template_type == "effect":
                    LegacyCodeGenerator._write_effect_line(f, row)
                elif template_type == "audio_effect":
                    LegacyCodeGenerator._write_audio_effect_line(f, row)
        
        print(f"Generated {len(data)} items to {output_file}")
    
    @staticmethod
    def _write_font_line(f, row):
        name = MetadataExtractor.clean_identifier(row['title'])
        padded_name = MetadataExtractor.pad_to_length(name, 20)
        f.write(f'    {padded_name}= Effect_meta("{row["title"]}", {row["is_vip"]}, "{row["resource_id"]}", "{row["effect_id"]}", "{row["md5"]}")\n')
    
    @staticmethod
    def _write_animation_line(f, row):
        name = MetadataExtractor.clean_identifier(row['name'])
        padded_name = MetadataExtractor.pad_to_length(name, 12)
        duration = row.get('animation_duration', 0.0)
        f.write(f'    {padded_name}= Animation_meta("{row["name"]}", {row["is_vip"]}, {duration:.3f}, "{row["resource_id"]}", "{row["effect_id"]}", "{row["md5"]}")\n')
    
    @staticmethod
    def _write_transition_line(f, row):
        name = MetadataExtractor.clean_identifier(row['name'])
        padded_name = MetadataExtractor.pad_to_length(name, 12)
        f.write(f'    {padded_name}= Transition_meta("{row["name"]}", {row["is_vip"]}, "{row["resource_id"]}", "{row["effect_id"]}", "{row["md5"]}", {row["default_duration"]:.6f}, {row["is_overlap"]})\n')
        f.write(f'    """默认时长: {row["default_duration"]:.2f}s"""\n')
    
    @staticmethod
    def _write_effect_line(f, row):
        name = MetadataExtractor.clean_identifier(row.get('title', row.get('name', '')))
        padded_name = MetadataExtractor.pad_to_length(name, 12)
        f.write(f'    {padded_name}= Effect_meta("{row.get("title", row.get("name", ""))}", {row["is_vip"]}, "{row["resource_id"]}", "{row["effect_id"]}", "{row["md5"]}", [])\n')
    
    @staticmethod
    def _write_audio_effect_line(f, row):
        name = MetadataExtractor.clean_identifier(row['effect_name'])
        padded_name = MetadataExtractor.pad_to_length(name, 12)
        f.write(f'    {padded_name}= Audio_effect_meta("{row["effect_name"]}", {row["is_vip"]}, "{row["resource_id"]}", "{row["effect_id"]}", "{row["md5"]}", [])\n')
