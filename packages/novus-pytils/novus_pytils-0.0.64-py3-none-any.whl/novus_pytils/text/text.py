"""Text file handler with format conversion capabilities.

This module provides comprehensive text file handling including reading, writing,
and conversion between various text formats.
"""
import os
import json
import csv
import yaml
from typing import Any, Dict, List, Union
from novus_pytils.models.models import BaseFileHandler, FileManagerMixin
from novus_pytils.exceptions import ConversionError
from novus_pytils.globals import SUPPORTED_TEXT_EXTENSIONS, TEXT_CONVERSION_MAP


class TextHandler(BaseFileHandler, FileManagerMixin):
    """Handler for text files with conversion capabilities."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = SUPPORTED_TEXT_EXTENSIONS
        self.conversion_map = TEXT_CONVERSION_MAP
    
    def read(self, file_path: str, encoding: str = 'utf-8') -> Union[str, Dict, List]:
        """Read text file and return appropriate data structure based on format."""
        if not self.validate_file(file_path):
            raise ConversionError(f"Unsupported file format: {file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                if ext == '.json':
                    return json.load(file)
                elif ext in ['.yaml', '.yml']:
                    return yaml.safe_load(file)
                elif ext == '.csv':
                    reader = csv.DictReader(file)
                    return list(reader)
                else:
                    return file.read()
        except Exception as e:
            raise ConversionError(f"Failed to read file {file_path}: {str(e)}")
    
    def write(self, file_path: str, content: Any, encoding: str = 'utf-8', **kwargs) -> bool:
        """Write content to text file in appropriate format."""
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as file:
                if ext == '.json':
                    json.dump(content, file, indent=kwargs.get('indent', 2), ensure_ascii=False)
                elif ext in ['.yaml', '.yml']:
                    yaml.dump(content, file, default_flow_style=False, allow_unicode=True)
                elif ext == '.csv' and isinstance(content, list) and content:
                    if isinstance(content[0], dict):
                        fieldnames = content[0].keys()
                        writer = csv.DictWriter(file, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(content)
                    else:
                        writer = csv.writer(file)
                        writer.writerows(content)
                else:
                    if isinstance(content, (dict, list)):
                        content = str(content)
                    file.write(content)
            return True
        except Exception as e:
            raise ConversionError(f"Failed to write file {file_path}: {str(e)}")
    
    def convert(self, input_path: str, output_path: str, target_format: str, **kwargs) -> bool:
        """Convert text file from one format to another."""
        if not self.validate_file(input_path):
            raise ConversionError(f"Unsupported input file format: {input_path}")
        
        input_ext = os.path.splitext(input_path)[1].lower()
        target_ext = target_format if target_format.startswith('.') else f'.{target_format}'
        
        if target_ext not in self.get_supported_conversions(input_ext):
            raise ConversionError(f"Cannot convert from {input_ext} to {target_ext}")
        
        try:
            content = self.read(input_path, kwargs.get('input_encoding', 'utf-8'))
            
            if input_ext == '.csv' and target_ext == '.json':
                converted_content = content
            elif input_ext == '.json' and target_ext == '.csv':
                if isinstance(content, list) and content and isinstance(content[0], dict):
                    converted_content = content
                else:
                    raise ConversionError("JSON must be a list of dictionaries to convert to CSV")
            elif input_ext in ['.json', '.yaml', '.yml'] and target_ext in ['.json', '.yaml', '.yml']:
                converted_content = content
            elif target_ext == '.txt':
                if isinstance(content, str):
                    converted_content = content
                elif isinstance(content, (dict, list)):
                    converted_content = json.dumps(content, indent=2, ensure_ascii=False)
                else:
                    converted_content = str(content)
            elif input_ext == '.txt' and target_ext in ['.json', '.yaml', '.yml']:
                try:
                    converted_content = json.loads(content)
                except json.JSONDecodeError:
                    converted_content = {"content": content}
            else:
                converted_content = content
            
            return self.write(output_path, converted_content, kwargs.get('output_encoding', 'utf-8'), **kwargs)
        
        except Exception as e:
            raise ConversionError(f"Conversion failed from {input_path} to {output_path}: {str(e)}")
    
    def convert_encoding(self, file_path: str, from_encoding: str, to_encoding: str) -> bool:
        """Convert file encoding."""
        try:
            with open(file_path, 'r', encoding=from_encoding) as file:
                content = file.read()
            
            with open(file_path, 'w', encoding=to_encoding) as file:
                file.write(content)
            
            return True
        except Exception as e:
            raise ConversionError(f"Encoding conversion failed: {str(e)}")
    
    def merge_files(self, file_paths: List[str], output_path: str, separator: str = '\n') -> bool:
        """Merge multiple text files into one."""
        try:
            merged_content = []
            for file_path in file_paths:
                content = self.read(file_path)
                if isinstance(content, str):
                    merged_content.append(content)
                else:
                    merged_content.append(str(content))
            
            final_content = separator.join(merged_content)
            return self.write(output_path, final_content)
        except Exception as e:
            raise ConversionError(f"Failed to merge files: {str(e)}")
    
    def split_file(self, file_path: str, output_dir: str, lines_per_file: int = 1000) -> List[str]:
        """Split a large text file into smaller files."""
        try:
            content = self.read(file_path)
            if not isinstance(content, str):
                content = str(content)
            
            lines = content.split('\n')
            output_files = []
            
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            ext = os.path.splitext(file_path)[1]
            
            for i in range(0, len(lines), lines_per_file):
                chunk = lines[i:i + lines_per_file]
                output_file = os.path.join(output_dir, f"{base_name}_part_{i//lines_per_file + 1}{ext}")
                self.write(output_file, '\n'.join(chunk))
                output_files.append(output_file)
            
            return output_files
        except Exception as e:
            raise ConversionError(f"Failed to split file: {str(e)}")