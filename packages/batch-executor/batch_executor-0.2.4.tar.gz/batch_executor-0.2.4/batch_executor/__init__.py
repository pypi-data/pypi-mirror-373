"""Top-level package for batch_executor."""

__author__ = """Rex Wang"""
__email__ = '1073853456@qq.com'
__version__ = '0.2.4'

from .custom_logger import setup_logger
from .main import (
    BatchExecutor, batch_executor,
    batch_async_executor, batch_hybrid_executor,
    batch_process_executor, batch_thread_executor
)
from .validator import Validator, validate_any, validate_groups
from .custom_logger import setup_logger
from .utils import rotate_file, get_files_with_ext, read_jsonl_files
