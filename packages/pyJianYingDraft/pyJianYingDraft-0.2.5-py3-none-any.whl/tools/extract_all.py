 
"""
统一元数据提取脚本

用于从剪映原始数据中提取各种类型的元数据
替换原来分散在 ignored/meta 中的各个提取脚本

使用方法:
    python extract_all.py --type fonts --source ignored/meta/fonts.json
    python extract_all.py --type all  # 提取所有类型
    python extract_all.py --config config.yaml  # 使用配置文件
"""

import argparse
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from .jianying_extractor import (
    FontExtractor, TextAnimationExtractor, MaskExtractor,
    FilterExtractor, TransitionExtractor, VideoEffectExtractor, AudioEffectExtractor
)
from .code_generator import CodeGenerator, LegacyCodeGenerator


class MetadataExtractorManager:
    """元数据提取管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.extractors = self._init_extractors()
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "data_sources": {
                "fonts": "ignored/meta/fonts.json",
                "text_intro": "ignored/meta/text_intro.json", 
                "text_outro": "ignored/meta/text_outro.json",
                "text_repeat": "ignored/meta/text_repeat.json",
                "masks": "ignored/meta/masks.json",
                "filters": "ignored/meta/视频特效/filters.json",
                "transitions": "ignored/meta/视频特效/transitions.json",
                "video_character": "ignored/meta/视频特效/video_character_effect.json",
                "video_scene": "ignored/meta/视频特效/video_scene_effect.json", 
                "audio_effects": "ignored/meta/audio_effect.json"
            },
            "output_dir": "pyJianYingDraft/metadata",
            "data_dir": "pyJianYingDraft/data",
            "legacy_output": "tools/legacy_output"
        }
        
        if config_file and Path(config_file).exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    user_config = yaml.safe_load(f)
                else:
                    user_config = json.load(f)
            
            # 合并配置
            default_config.update(user_config)
        
        return default_config
    
    def _init_extractors(self) -> Dict[str, Any]:
        """初始化提取器"""
        sources = self.config["data_sources"]
        return {
            "fonts": FontExtractor,
            "text_intro": TextAnimationExtractor,
            "text_outro": TextAnimationExtractor, 
            "text_repeat": TextAnimationExtractor,
            "masks": MaskExtractor,
            "filters": FilterExtractor,
            "transitions": TransitionExtractor,
            "video_character": VideoEffectExtractor,
            "video_scene": VideoEffectExtractor,
            "audio_effects": AudioEffectExtractor
        }
    
    def extract_single_type(self, data_type: str, source_file: Optional[str] = None, 
                          output_file: Optional[str] = None, legacy_format: bool = False) -> None:
        """提取单一类型的元数据"""
        if data_type not in self.extractors:
            print(f"Error: Unknown data type '{data_type}'")
            print(f"Available types: {list(self.extractors.keys())}")
            return
        
        # 确定源文件
        if source_file is None:
            source_file = self.config["data_sources"].get(data_type)
            if not source_file:
                print(f"Error: No source file configured for type '{data_type}'")
                return
        
        source_path = Path(source_file)
        if not source_path.exists():
            print(f"Error: Source file not found: {source_path}")
            return
        
        # 确定输出文件
        if output_file is None:
            if legacy_format:
                output_file = f"{self.config['legacy_output']}/{data_type}_meta.py"
            else:
                output_file = f"{self.config['data_dir']}/{data_type}.json"
        
        # 创建提取器
        extractor_class = self.extractors[data_type]
        extractor = extractor_class(source_file, output_file)
        
        try:
            print(f"Extracting {data_type} from {source_file}...")
            
            if legacy_format:
                # 使用旧版格式生成器
                template_type = self._get_template_type(data_type)
                LegacyCodeGenerator.generate_from_extractor(extractor, output_file, template_type)
            else:
                # 使用新版JSON格式
                data = extractor.extract()
                print(f"Successfully extracted {len(data)} items")
                
        except Exception as e:
            print(f"Error extracting {data_type}: {e}")
    
    def extract_all(self, legacy_format: bool = False) -> None:
        """提取所有类型的元数据"""
        print("Starting extraction of all metadata types...")
        
        for data_type in self.extractors.keys():
            print(f"\n--- Extracting {data_type} ---")
            try:
                self.extract_single_type(data_type, legacy_format=legacy_format)
            except Exception as e:
                print(f"Failed to extract {data_type}: {e}")
                continue
        
        print("\nExtraction completed!")
    
    def generate_code(self, data_type: str, input_file: Optional[str] = None) -> None:
        """生成Python代码文件"""
        if input_file is None:
            input_file = f"{self.config['data_dir']}/{data_type}.json"
        
        input_path = Path(input_file)
        if not input_path.exists():
            print(f"Error: Input file not found: {input_path}")
            return
        
        # 加载数据
        with open(input_path, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
        
        import pandas as pd
        data = pd.DataFrame(data_list)
        
        # 生成代码
        generator = CodeGenerator(data, data_type)
        
        # 确定类名和输出文件
        class_mapping = {
            "fonts": ("FontType", "font_meta.py", "EffectEnum", "EffectMeta"),
            "text_intro": ("IntroType", "animation_meta.py", "EffectEnum", "Animation_meta"),
            "text_outro": ("OutroType", "animation_meta.py", "EffectEnum", "Animation_meta"), 
            "text_repeat": ("GroupAnimationType", "animation_meta.py", "EffectEnum", "Animation_meta"),
            "masks": ("MaskType", "mask_meta.py", "EffectEnum", "EffectMeta"),
            "filters": ("FilterType", "filter_meta.py", "EffectEnum", "EffectMeta"),
            "transitions": ("TransitionType", "transition_meta.py", "EffectEnum", "Transition_meta"),
            "video_character": ("VideoCharacterEffectType", "video_effect_meta.py", "EffectEnum", "EffectMeta"),
            "video_scene": ("VideoSceneEffectType", "video_effect_meta.py", "EffectEnum", "EffectMeta"),
            "audio_effects": ("ToneEffectType", "audio_effect_meta.py", "EffectEnum", "Audio_effect_meta")
        }
        
        if data_type in class_mapping:
            class_name, filename, base_class, meta_class = class_mapping[data_type]
            output_file = f"{self.config['output_dir']}/{filename}"
            generator.save_to_file(output_file, class_name, base_class, meta_class)
        else:
            print(f"Error: No code generation mapping for type '{data_type}'")
    
    def _get_template_type(self, data_type: str) -> str:
        """获取模板类型"""
        mapping = {
            "fonts": "font",
            "text_intro": "animation",
            "text_outro": "animation",
            "text_repeat": "animation", 
            "masks": "effect",
            "filters": "effect",
            "transitions": "transition",
            "video_character": "effect",
            "video_scene": "effect",
            "audio_effects": "audio_effect"
        }
        return mapping.get(data_type, "effect")
    
    def cleanup_legacy_files(self) -> None:
        """清理旧版提取脚本生成的文件"""
        legacy_patterns = [
            "ignored/meta/extract_*.py",
            "ignored/meta/video_effect_meta.py",
            "ignored/meta/metadata.py"
        ]
        
        print("Cleaning up legacy files...")
        cleaned_count = 0
        
        for pattern in legacy_patterns:
            for file_path in Path(".").glob(pattern):
                if file_path.is_file():
                    file_path.unlink()
                    print(f"Removed: {file_path}")
                    cleaned_count += 1
        
        print(f"Cleaned up {cleaned_count} legacy files")


def main():
    parser = argparse.ArgumentParser(description="剪映元数据提取工具")
    parser.add_argument("--type", choices=["fonts", "text_intro", "text_outro", "text_repeat", 
                                          "masks", "filters", "transitions", "video_character", 
                                          "video_scene", "audio_effects", "all"],
                       help="要提取的数据类型")
    parser.add_argument("--source", help="源数据文件路径")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--legacy", action="store_true", help="使用旧版格式输出")
    parser.add_argument("--generate-code", help="从JSON数据生成Python代码")
    parser.add_argument("--cleanup", action="store_true", help="清理旧版文件")
    
    args = parser.parse_args()
    
    if not any([args.type, args.generate_code, args.cleanup]):
        parser.print_help()
        return
    
    manager = MetadataExtractorManager(args.config)
    
    if args.cleanup:
        manager.cleanup_legacy_files()
        return
    
    if args.generate_code:
        manager.generate_code(args.generate_code)
        return
    
    if args.type == "all":
        manager.extract_all(legacy_format=args.legacy)
    else:
        manager.extract_single_type(args.type, args.source, args.output, legacy_format=args.legacy)


if __name__ == "__main__":
    main()