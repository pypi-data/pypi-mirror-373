"""
高效批量数据写入工具
支持多种格式和异步写入，专为 executor 并发数据写入设计
"""
import json
import csv
import threading
import time
from pathlib import Path
from typing import Any, List, Dict, Optional, Union
from queue import Queue, Empty
from enum import Enum

class WriteFormat(Enum):
    """支持的写入格式"""
    JSON = "json"
    JSONL = "jsonl"
    CSV = "csv"
    TXT = "txt"

class BatchWriter:
    """批量数据写入器"""
    
    def __init__(
        self,
        file_path: Union[str, Path],
        format_type: WriteFormat = WriteFormat.JSONL,
        batch_size: int = 1000,
        max_queue_size: int = 10000,
        flush_interval: float = 2.0,
        auto_create_dir: bool = True
    ):
        """
        初始化批量写入器
        
        Args:
            file_path: 输出文件路径
            format_type: 写入格式
            batch_size: 批量写入大小
            max_queue_size: 最大队列大小
            flush_interval: 强制刷新间隔(秒)
            auto_create_dir: 自动创建目录
        """
        self.file_path = Path(file_path)
        self.format_type = format_type
        self.batch_size = batch_size
        self.max_queue_size = max_queue_size
        self.flush_interval = flush_interval
        self.auto_create_dir = auto_create_dir
        
        # 内部状态
        self._queue = Queue(maxsize=max_queue_size)
        self._writer_thread = None
        self._stop_event = threading.Event()
        self._buffer = []
        self._last_flush = time.time()
        self._is_running = False
        self._stats = {
            'total_written': 0,
            'total_batches': 0,
            'errors': 0,
            'start_time': None
        }
        
        # 初始化文件
        self._init_file()
    
    def _init_file(self):
        """初始化文件和目录"""
        if self.auto_create_dir:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _write_batch(self, items: List[Any]) -> bool:
        """写入一批数据"""
        if not items:
            return True
        
        try:
            if self.format_type == WriteFormat.JSON:
                return self._write_json_batch(items)
            elif self.format_type == WriteFormat.JSONL:
                return self._write_jsonl_batch(items)
            elif self.format_type == WriteFormat.CSV:
                return self._write_csv_batch(items)
            elif self.format_type == WriteFormat.TXT:
                return self._write_txt_batch(items)
            else:
                return False
        except Exception:
            return False
    
    def _write_json_batch(self, items: List[Any]) -> bool:
        """写入JSON格式批次"""
        existing_data = []
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
            except:
                existing_data = []
        
        combined_data = existing_data + items
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
        return True
    
    def _write_jsonl_batch(self, items: List[Any]) -> bool:
        """写入JSONL格式批次"""
        mode = 'a' if self.file_path.exists() else 'w'
        with open(self.file_path, mode, encoding='utf-8') as f:
            for item in items:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
        return True
    
    def _write_csv_batch(self, items: List[Any]) -> bool:
        """写入CSV格式批次"""
        if not items:
            return True
        
        # 确定字段名
        if isinstance(items[0], dict):
            fieldnames = list(items[0].keys())
        else:
            items = [{'data': str(item)} for item in items]
            fieldnames = ['data']
        
        file_exists = self.file_path.exists()
        mode = 'a' if file_exists else 'w'
        
        with open(self.file_path, mode, encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            
            for item in items:
                if isinstance(item, dict):
                    writer.writerow(item)
                else:
                    writer.writerow({'data': str(item)})
        return True
    
    def _write_txt_batch(self, items: List[Any]) -> bool:
        """写入文本格式批次"""
        mode = 'a' if self.file_path.exists() else 'w'
        with open(self.file_path, mode, encoding='utf-8') as f:
            for item in items:
                f.write(str(item) + '\n')
        return True
    
    def _writer_worker(self):
        """写入工作线程"""
        self._stats['start_time'] = time.time()
        
        while not self._stop_event.is_set() or not self._queue.empty():
            try:
                # 尝试获取数据
                try:
                    item = self._queue.get(timeout=0.5)
                    self._buffer.append(item)
                    self._queue.task_done()
                except Empty:
                    pass
                
                # 检查是否需要写入
                should_flush = (
                    len(self._buffer) >= self.batch_size or
                    (time.time() - self._last_flush) > self.flush_interval or
                    (self._stop_event.is_set() and self._buffer)
                )
                
                if should_flush and self._buffer:
                    if self._write_batch(self._buffer.copy()):
                        self._stats['total_written'] += len(self._buffer)
                        self._stats['total_batches'] += 1
                    else:
                        self._stats['errors'] += 1
                    
                    self._buffer.clear()
                    self._last_flush = time.time()
                    
            except Exception:
                self._stats['errors'] += 1
    
    def start(self):
        """启动写入器"""
        if self._is_running:
            return
        
        self._is_running = True
        self._stop_event.clear()
        self._writer_thread = threading.Thread(target=self._writer_worker, daemon=True)
        self._writer_thread.start()
    
    def stop(self, timeout: float = 10.0) -> bool:
        """停止写入器"""
        if not self._is_running:
            return True
        
        self._stop_event.set()
        
        if self._writer_thread and self._writer_thread.is_alive():
            self._writer_thread.join(timeout=timeout)
        
        self._is_running = False
        return True
    
    def write(self, item: Any, block: bool = True, timeout: Optional[float] = None) -> bool:
        """写入单个数据项"""
        if not self._is_running:
            self.start()
        
        try:
            self._queue.put(item, block=block, timeout=timeout)
            return True
        except:
            return False
    
    def write_many(self, items: List[Any], block: bool = True, timeout: Optional[float] = None) -> int:
        """写入多个数据项"""
        if not self._is_running:
            self.start()
        
        success_count = 0
        for item in items:
            if self.write(item, block=block, timeout=timeout):
                success_count += 1
            else:
                break
        return success_count
    
    def flush(self, timeout: float = 5.0) -> bool:
        """强制刷新缓冲区"""
        if not self._is_running:
            return True
        
        # 设置停止事件触发最后一次写入
        original_stop_state = self._stop_event.is_set()
        self._stop_event.set()
        
        # 等待队列清空和缓冲区写入
        start_time = time.time()
        while (not self._queue.empty() or self._buffer) and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        # 恢复原始状态
        if not original_stop_state:
            self._stop_event.clear()
        
        return self._queue.empty() and not self._buffer
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self._stats.copy()
        stats['queue_size'] = self._queue.qsize()
        stats['buffer_size'] = len(self._buffer)
        stats['is_running'] = self._is_running
        
        if stats['start_time']:
            stats['runtime'] = time.time() - stats['start_time']
            if stats['runtime'] > 0:
                stats['items_per_second'] = stats['total_written'] / stats['runtime']
        
        return stats
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.flush()
        self.stop()


def create_writer(
    file_path: Union[str, Path],
    format_type: Union[str, WriteFormat] = "jsonl",
    **kwargs
) -> BatchWriter:
    """创建批量写入器的便捷函数"""
    if isinstance(format_type, str):
        format_type = WriteFormat(format_type.lower())
    
    return BatchWriter(file_path, format_type, **kwargs)


def write_data_sync(
    data: List[Any],
    file_path: Union[str, Path],
    format_type: Union[str, WriteFormat] = "jsonl",
    **kwargs
) -> bool:
    """同步写入数据的便捷函数"""
    try:
        with create_writer(file_path, format_type, **kwargs) as writer:
            writer.write_many(data)
            writer.flush()
        return True
    except:
        return False
