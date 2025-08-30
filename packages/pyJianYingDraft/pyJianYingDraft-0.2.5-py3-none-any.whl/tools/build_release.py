 
"""
发布构建脚本

用于构建用于公开发布的清洁版本数据
- 提取所有元数据
- 生成Python代码文件
- 创建公开数据文件
- 清理敏感信息
"""

import json
import shutil
import yaml
from pathlib import Path
from typing import Dict, List, Any

from .extract_all import MetadataExtractorManager
from .code_generator import CodeGenerator


class ReleaseBuilder:
    """发布版本构建器"""
    
    def __init__(self, config_file: str = "tools/config.yaml"):
        self.config_file = config_file
        self.manager = MetadataExtractorManager(config_file)
        self.config = self.manager.config
    
    def build_full_release(self) -> None:
        """构建完整的发布版本"""
        print("=== Starting Release Build ===")
        
        # 1. 提取所有元数据到JSON
        print("\n1. Extracting metadata to JSON...")
        self.manager.extract_all(legacy_format=False)
        
        # 2. 生成Python代码文件
        print("\n2. Generating Python code files...")
        self._generate_all_code_files()
        
        # 3. 创建公开数据文件
        print("\n3. Creating public data file...")
        self._create_public_data()
        
        # 4. 验证生成的文件
        print("\n4. Validating generated files...")
        self._validate_output()
        
        print("\n=== Release Build Completed ===")
    
    def _generate_all_code_files(self) -> None:
        """生成所有Python代码文件"""
        class_mapping = self.config["code_generation"]["class_mapping"]
        
        for data_type, mapping in class_mapping.items():
            input_file = f"{self.config['data_dir']}/{data_type}.json"
            
            if not Path(input_file).exists():
                print(f"Warning: {input_file} not found, skipping...")
                continue
            
            try:
                # 加载数据
                with open(input_file, 'r', encoding='utf-8') as f:
                    data_list = json.load(f)
                
                if not data_list:
                    print(f"Warning: {data_type} has no data, skipping...")
                    continue
                
                import pandas as pd
                data = pd.DataFrame(data_list)
                
                # 生成代码
                generator = CodeGenerator(data, data_type)
                output_file = f"{self.config['output_dir']}/{mapping['file_name']}"
                
                generator.save_to_file(
                    output_file,
                    mapping['class_name'],
                    mapping['base_class'],
                    mapping['meta_class']
                )
                
                print(f"Generated {mapping['class_name']} -> {output_file}")
                
            except Exception as e:
                print(f"Error generating code for {data_type}: {e}")
    
    def _create_public_data(self) -> None:
        """创建公开数据文件"""
        public_config = self.config["release"]["public_data"]
        include_fields = public_config["include_fields"]
        
        public_data = {}
        data_dir = Path(self.config['data_dir'])
        
        for data_type, fields in include_fields.items():
            input_file = data_dir / f"{data_type}.json"
            
            if not input_file.exists():
                print(f"Warning: {input_file} not found for public data")
                continue
            
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    full_data = json.load(f)
                
                # 清理数据，只保留指定字段
                cleaned_data = []
                for item in full_data:
                    cleaned_item = {}
                    for field in fields:
                        if field in item:
                            cleaned_item[field] = item[field]
                        elif field == "has_params":
                            # 特殊处理：检查是否有参数但不暴露具体参数
                            cleaned_item[field] = bool(item.get("params", []))
                    
                    if cleaned_item:
                        cleaned_data.append(cleaned_item)
                
                public_data[data_type] = cleaned_data
                print(f"Cleaned {data_type}: {len(cleaned_data)} items")
                
            except Exception as e:
                print(f"Error processing {data_type} for public data: {e}")
        
        # 保存公开数据文件
        output_path = data_dir / public_config["filename"]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(public_data, f, ensure_ascii=False, indent=2)
        
        print(f"Public data saved to: {output_path}")
    
    def _validate_output(self) -> None:
        """验证输出文件"""
        issues = []
        
        # 检查Python代码文件
        metadata_dir = Path(self.config['output_dir'])
        expected_files = [
            "font_meta.py",
            "animation_meta.py", 
            "mask_meta.py",
            "filter_meta.py",
            "transition_meta.py",
            "video_effect_meta.py",
            "audio_effect_meta.py"
        ]
        
        for filename in expected_files:
            filepath = metadata_dir / filename
            if not filepath.exists():
                issues.append(f"Missing metadata file: {filepath}")
            elif filepath.stat().st_size == 0:
                issues.append(f"Empty metadata file: {filepath}")
        
        # 检查数据文件
        data_dir = Path(self.config['data_dir'])
        if not (data_dir / "public_metadata.json").exists():
            issues.append("Missing public_metadata.json")
        
        # 检查语法错误
        for py_file in metadata_dir.glob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, str(py_file), 'exec')
            except SyntaxError as e:
                issues.append(f"Syntax error in {py_file}: {e}")
        
        if issues:
            print("\nValidation Issues Found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ All output files validated successfully")
    
    def clean_for_public_release(self) -> None:
        """清理项目以准备公开发布"""
        print("=== Cleaning for Public Release ===")
        
        exclude_patterns = self.config["release"]["exclude_from_public"]
        cleaned_count = 0
        
        for pattern in exclude_patterns:
            for path in Path(".").glob(pattern):
                if path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    print(f"Removed: {path}")
                    cleaned_count += 1
        
        print(f"Cleaned {cleaned_count} items for public release")
    
    def create_gitignore_update(self) -> None:
        """更新.gitignore文件"""
        gitignore_path = Path(".gitignore")
        
        # 需要忽略的工具目录内容
        tool_ignores = [
            "",
            "# Internal metadata extraction tools (not for public release)",
            "tools/",
            "ignored/",
            "*.db",
            "rp.db*",
            "**/raw_data/",
            "**/*_cache/",
            ""
        ]
        
        # 读取现有.gitignore
        existing_lines = []
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                existing_lines = [line.strip() for line in f.readlines()]
        
        # 检查是否需要添加新规则
        needs_update = False
        for ignore_rule in tool_ignores:
            if ignore_rule.strip() and ignore_rule not in existing_lines:
                needs_update = True
                break
        
        if needs_update:
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                f.write('\n'.join(tool_ignores))
            print("Updated .gitignore with tool exclusions")
        else:
            print(".gitignore already up to date")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="构建发布版本")
    parser.add_argument("--full", action="store_true", help="执行完整构建")
    parser.add_argument("--code-only", action="store_true", help="只生成代码文件")
    parser.add_argument("--public-data", action="store_true", help="只生成公开数据")
    parser.add_argument("--clean", action="store_true", help="清理敏感文件")
    parser.add_argument("--update-gitignore", action="store_true", help="更新.gitignore")
    parser.add_argument("--config", default="tools/config.yaml", help="配置文件路径")
    
    args = parser.parse_args()
    
    if not any([args.full, args.code_only, args.public_data, args.clean, args.update_gitignore]):
        parser.print_help()
        return
    
    builder = ReleaseBuilder(args.config)
    
    if args.full:
        builder.build_full_release()
    elif args.code_only:
        builder._generate_all_code_files()
    elif args.public_data:
        builder._create_public_data()
    elif args.clean:
        builder.clean_for_public_release()
    elif args.update_gitignore:
        builder.create_gitignore_update()


if __name__ == "__main__":
    main()