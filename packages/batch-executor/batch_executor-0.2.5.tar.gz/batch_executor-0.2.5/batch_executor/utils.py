import os
from pathlib import Path
from typing import List, Optional, Union
from batch_executor.constants import logger
import json

def rotate_file(file:Union[Path, str], max_size:int=500):
    """rename existing file"""
    file = Path(str(file))
    if file.exists():
        for i in range(max_size):
            new_file = file.parent / f'{file.stem}_{i}{file.suffix}'
            if not new_file.exists():
                file.rename(new_file)
                return new_file
        logger.warning(f"Failed to rename file {file}")

def get_files_with_ext(directory, ext: str = '.jsonl', exclude_patterns=None) -> List[Path]:
    """获取目录下的所有指定扩展名的文件"""
    if exclude_patterns is None:
        exclude_patterns = []
    elif isinstance(exclude_patterns, str):
        exclude_patterns = [exclude_patterns]
    target_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(ext):
                if not any(pattern in file for pattern in exclude_patterns):
                    full_path = Path(root, file).resolve()
                    target_files.append(full_path)
    return target_files

def read_jsonl_files(file_paths: List[Path]) -> List[dict]:
    """读取多个JSONL文件并合并结果"""
    all_data = []
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            all_data.append(data)
                        except json.JSONDecodeError:
                            continue
        except (FileNotFoundError, PermissionError):
            continue
    return all_data
