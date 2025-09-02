"""
批量任务执行器，支持异步、多线程和多进程三种模式
- async_run: 异步并发执行（适用于IO密集型）
- thread_run: 多线程并发（适用于IO密集型）
- process_run: 多进程并发（适用于CPU密集型）
- hybrid_run: 多进程+异步混合执行（适用于大规模IO密集型）
- run: 自动选择执行模式
"""
import logging
import asyncio
import math
import signal
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from typing import List, Callable, Any, Coroutine, Optional
from tqdm.asyncio import tqdm
from tqdm import tqdm as sync_tqdm
from typing import TypeVar, List, Callable, Any, Optional, Awaitable, Union
from func_timeout import func_timeout, FunctionTimedOut
from multiprocessing import Manager
from pathlib import Path
from dataclasses import dataclass
from batch_executor.writer import BatchWriter, WriteFormat
from batch_executor.utils import read_jsonl_files
from batch_executor.custom_logger import setup_logger
from batch_executor.constants import PHYSICAL_CORES, VIRTUAL_CORES

# 默认日志记录器
_thread_logger = setup_logger('multi_thread', log_level="INFO")
_process_logger = setup_logger('multi_process', log_level="INFO")
_async_logger = setup_logger('multi_async', log_level="INFO")
_hybrid_logger = setup_logger('multi_hybrid', log_level="INFO")

@dataclass
class ExecutorConfig:
    """执行器配置类"""
    # 基础执行配置
    nproc: int = None
    ncoroutine: Optional[int] = None
    timeout: Optional[Union[int, float]] = None
    keep_order: bool = True
    task_desc: str = ""
    
    # 日志配置
    logger: Optional[logging.Logger] = None
    disable_logger: bool = False
    
    # 缓存配置
    cache_file: Optional[Union[str, Path]] = None
    cache_dir: Optional[Union[str, Path]] = None
    split_num: int = 1  # 分割文件数量
    index_field: str = "index"
    error_field: str = "error"
    result_field: str = "result"
    overwrite: bool = False
    
    def __post_init__(self):
        """后处理初始化"""
        if self.nproc is None:
            # 默认使用物理核心数
            self.nproc = PHYSICAL_CORES
        if self.ncoroutine is None:
            self.ncoroutine = self.nproc
    
    def get_cache_path(self, index: Optional[int] = None) -> Optional[Path]:
        """获取完整的缓存文件路径"""
        if not self.cache_file:
            return None
        
        cache_file_path = Path(self.cache_file)
        
        # 处理分割文件
        if self.split_num > 1 and index is not None:
            # 获取文件名和扩展名
            stem = cache_file_path.stem
            suffix = cache_file_path.suffix
            cache_file_path = cache_file_path.with_name(f"{stem}_{index % self.split_num}{suffix}")
        
        if self.cache_dir:
            cache_dir_path = Path(self.cache_dir)
            return cache_dir_path / cache_file_path
        else:
            return cache_file_path
    
    def get_all_cache_paths(self) -> List[Path]:
        """获取所有缓存文件路径"""
        if not self.cache_file:
            return []
        
        if self.split_num <= 1:
            cache_path = self.get_cache_path()
            return [cache_path] if cache_path else []
        
        cache_paths = []
        for i in range(self.split_num):
            cache_path = self.get_cache_path(i)
            if cache_path:
                cache_paths.append(cache_path)
        return cache_paths


def _timeout_handler(signum, frame):
    """信号处理函数，用于多进程超时"""
    raise TimeoutError("Process execution timeout")

def _process_wrapper(args):
    """外部包装函数，用于多进程执行"""
    item, idx, func, timeout = args
    try:
        if timeout:
            # 设置信号处理器
            signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(int(timeout))
        
        result = func(item)
        
        if timeout:
            signal.alarm(0)  # 取消超时
        
        return idx, result, None
    except TimeoutError as e:
        return idx, None, f"Timeout after {timeout}s: {str(e)}"
    except Exception as e:
        if timeout:
            signal.alarm(0)  # 确保取消超时
        return idx, None, e

def _hybrid_worker_with_progress(args):
    """混合执行器的进程工作函数，支持实时进度更新和缓存"""
    items_chunk, func_async, ncoroutine, timeout, start_idx, progress_queue, cache_config = args
    
    async def async_worker_in_process():
        """在进程内部运行异步任务"""
        sem = asyncio.Semaphore(ncoroutine)
        
        # 创建进程内的缓存写入器
        process_cache_writer = None
        if cache_config:
            cache_path = cache_config['cache_path']
            if cache_path:
                process_cache_writer = BatchWriter(
                    cache_path,
                    WriteFormat.JSONL,
                    batch_size=50,
                    flush_interval=0.5
                )
                process_cache_writer.start()
        
        async def wrapped_func(item, idx):
            async with sem:
                try:
                    if timeout:
                        result = await asyncio.wait_for(func_async(item), timeout=timeout)
                    else:
                        result = await func_async(item)
                    
                    # 保存到缓存
                    if process_cache_writer and cache_config:
                        cache_data = {cache_config['index_field']: idx}
                        if isinstance(result, dict):
                            cache_data.update(result)
                        else:
                            cache_data[cache_config['result_field']] = result
                        process_cache_writer.write(cache_data)
                    
                    # 发送进度更新信号
                    progress_queue.put(1)
                    return idx, result, None
                except asyncio.TimeoutError:
                    error_msg = f"Timeout after {timeout}s"
                    
                    # 保存错误到缓存
                    if process_cache_writer and cache_config:
                        cache_data = {
                            cache_config['index_field']: idx,
                            cache_config['error_field']: error_msg
                        }
                        process_cache_writer.write(cache_data)
                    
                    progress_queue.put(1)
                    return idx, None, error_msg
                except Exception as e:
                    error_msg = str(e)
                    
                    # 保存错误到缓存
                    if process_cache_writer and cache_config:
                        cache_data = {
                            cache_config['index_field']: idx,
                            cache_config['error_field']: error_msg
                        }
                        process_cache_writer.write(cache_data)
                    
                    progress_queue.put(1)
                    return idx, None, error_msg
        
        try:
            tasks = [wrapped_func(item, start_idx + i) for i, item in enumerate(items_chunk)]
            results = []
            
            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
            
            return results
        finally:
            # 停止缓存写入器
            if process_cache_writer:
                process_cache_writer.flush()
                process_cache_writer.stop()
    
    try:
        # 在子进程中运行异步事件循环
        return asyncio.run(async_worker_in_process())
    except Exception as e:
        # 如果整个chunk失败，返回所有项目的错误，并更新进度
        for _ in range(len(items_chunk)):
            progress_queue.put(1)
        return [(start_idx + i, None, str(e)) for i in range(len(items_chunk))]

class Executor:
    """批量任务执行器类"""
    
    def __init__(self, func: Callable[[Any], Any], config: Optional[ExecutorConfig] = None, **kwargs):
        """
        初始化执行器
        
        Args:
            func: 执行函数
            config: 执行器配置对象
            **kwargs: 额外的配置参数（会覆盖config中的同名参数）
        """
        self.func = func
        
        # 如果没有提供config，创建默认配置
        if config is None:
            config = ExecutorConfig()
        
        # 使用kwargs更新配置
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        self.config = config
        self._cached_indices = set()
        self._cache_writers = {}  # 分割文件的写入器字典
        
        self._init_cache()
    
    def _init_cache(self):
        """初始化缓存"""
        if not self.config.cache_file:
            return
        
        if self.config.overwrite:
            # 覆盖模式：直接清空缓存，删除所有相关文件
            self._cached_indices.clear()
            cache_paths = self.config.get_all_cache_paths()
            for cache_path in cache_paths:
                if cache_path.exists():
                    cache_path.unlink()
            return
        
        # 非覆盖模式：读取已缓存的数据
        cache_paths = self.config.get_all_cache_paths()
        existing_files = [path for path in cache_paths if path.exists()]
        
        if existing_files:
            try:
                all_cache_data = read_jsonl_files(existing_files)
                for data in all_cache_data:
                    if isinstance(data, dict) and self.config.index_field in data:
                        # 只保留非错误的索引
                        if self.config.error_field not in data:
                            self._cached_indices.add(data[self.config.index_field])
            except:
                pass
    
    def _get_cache_writer(self, index: int) -> Optional[BatchWriter]:
        """获取指定索引对应的缓存写入器"""
        if not self.config.cache_file:
            return None
        
        cache_path = self.config.get_cache_path(index)
        if not cache_path:
            return None
        
        # 使用缓存路径作为key
        cache_key = str(cache_path)
        
        if cache_key not in self._cache_writers:
            self._cache_writers[cache_key] = BatchWriter(
                cache_path,
                WriteFormat.JSONL,
                batch_size=100,
                flush_interval=1.0
            )
            self._cache_writers[cache_key].start()
        
        return self._cache_writers[cache_key]
    
    def _start_cache_writers(self):
        """启动所有缓存写入器（在非分割模式下使用）"""
        if not self.config.cache_file or self.config.split_num > 1:
            return
        
        cache_path = self.config.get_cache_path()
        if cache_path:
            cache_key = str(cache_path)
            if cache_key not in self._cache_writers:
                self._cache_writers[cache_key] = BatchWriter(
                    cache_path,
                    WriteFormat.JSONL,
                    batch_size=100,
                    flush_interval=1.0
                )
                self._cache_writers[cache_key].start()
    
    def _stop_cache_writers(self):
        """停止所有缓存写入器"""
        for writer in self._cache_writers.values():
            if writer:
                writer.flush()
                writer.stop()
        self._cache_writers.clear()
    
    def _save_result_to_cache(self, idx: int, result: Any, error: Optional[str] = None):
        """保存结果到缓存"""
        if not self.config.cache_file:
            return
        
        if self.config.split_num > 1:
            # 分割模式：根据索引获取对应的写入器
            writer = self._get_cache_writer(idx)
        else:
            # 单文件模式：使用通用写入器
            cache_path = self.config.get_cache_path()
            writer = self._cache_writers.get(str(cache_path)) if cache_path else None
        
        if not writer:
            return
        
        cache_data = {self.config.index_field: idx}
        
        if error:
            cache_data[self.config.error_field] = error
        else:
            if isinstance(result, dict):
                cache_data.update(result)
            else:
                cache_data[self.config.result_field] = result
        
        writer.write(cache_data)
    
    def _filter_cached_items(self, items: List[Any]) -> tuple[List[tuple], List[Any]]:
        """过滤已缓存的项目"""
        if not self.config.cache_file:
            return [(i, item) for i, item in enumerate(items)], []
        
        filtered_items = []
        cached_results = [None] * len(items)
        
        # 获取所有缓存数据
        cache_paths = self.config.get_all_cache_paths()
        existing_files = [path for path in cache_paths if path.exists()]
        
        if existing_files:
            try:
                all_cache_data = read_jsonl_files(existing_files)
                # 构建索引到结果的映射
                cache_map = {}
                for data in all_cache_data:
                    if (isinstance(data, dict) and 
                        self.config.index_field in data and 
                        self.config.error_field not in data):
                        idx = data[self.config.index_field]
                        result_data = data.copy()
                        result_data.pop(self.config.index_field, None)
                        if (self.config.result_field in result_data and 
                            len(result_data) == 1):
                            cache_map[idx] = result_data[self.config.result_field]
                        else:
                            cache_map[idx] = result_data
                
                # 根据缓存映射过滤项目
                for i, item in enumerate(items):
                    if i in cache_map:
                        cached_results[i] = cache_map[i]
                    else:
                        filtered_items.append((i, item))
            except:
                # 读取失败，处理所有项目
                filtered_items = [(i, item) for i, item in enumerate(items)]
        else:
            filtered_items = [(i, item) for i, item in enumerate(items)]
        
        return filtered_items, cached_results
    
    def _get_default_logger(self, mode: str) -> logging.Logger:
        """获取默认日志记录器"""
        if self.config.disable_logger:
            return None
        if mode == "async":
            return _async_logger
        elif mode == "thread":
            return _thread_logger
        elif mode == "process":
            return _process_logger
        elif mode == "hybrid":
            return _hybrid_logger
        else:
            return _thread_logger
    
    def _process_results(self, results_with_idx: List[tuple], failures: List[tuple], logger: logging.Logger, cached_results: List[Any] = None) -> List[Any]:
        """处理结果，包括排序和日志记录"""
        if failures and logger:
            logger.warning(f"Total failures: {len(failures)}")
        
        # 如果有缓存结果，需要合并
        if cached_results:
            final_results = cached_results.copy()
            for idx, result in results_with_idx:
                if idx < len(final_results):
                    final_results[idx] = result
        else:
            if self.config.keep_order:
                results_with_idx.sort(key=lambda x: x[0])
            final_results = [r for _, r in results_with_idx]
            
        return final_results
    
    def _chunk_items(self, items: List[Any], nproc: int) -> List[List[Any]]:
        """将项目列表分块"""
        chunk_size = math.ceil(len(items) / nproc)
        chunks = []
        for i in range(0, len(items), chunk_size):
            chunks.append(items[i:i + chunk_size])
        return chunks
    
    async def async_run(self, items: List[Any]) -> List[Any]:
        """异步并发执行任务"""
        if not len(items):
            return []
        
        # 过滤已缓存的项目
        filtered_items, cached_results = self._filter_cached_items(items)
        if not filtered_items:
            return cached_results
        
        # 启动缓存写入器
        self._start_cache_writers()
        
        try:
            if self.config.disable_logger:
                logger = None
            else:
                logger = self.config.logger or self._get_default_logger("async")
            sem = asyncio.Semaphore(self.config.nproc)
            
            # 定义任务函数 -> idx, result, error
            async def wrapped_func(item_with_idx):
                idx, item = item_with_idx
                async with sem:
                    try:
                        if self.config.timeout:
                            result = await asyncio.wait_for(self.func(item), timeout=self.config.timeout)
                        else:
                            result = await self.func(item)
                        
                        # 保存到缓存
                        self._save_result_to_cache(idx, result)
                        
                        if logger:
                            logger.debug(f"Successfully processed item {idx}")
                        return idx, result, None
                    except asyncio.TimeoutError:
                        error_msg = f"Timeout after {self.config.timeout}s"
                        self._save_result_to_cache(idx, None, error_msg)
                        if logger:
                            logger.error(f"Item {idx} timeout: {error_msg}")
                        return idx, None, error_msg
                    except Exception as e:
                        error_msg = str(e)
                        self._save_result_to_cache(idx, None, error_msg)
                        if logger:
                            logger.error(f"Error processing item {idx}: {error_msg}")
                        return idx, None, error_msg
            
            tasks = [wrapped_func(item_with_idx) for item_with_idx in filtered_items]
            results_with_idx = []
            
            desc = f"{self.config.task_desc} " if self.config.task_desc else ""
            total_items = len(items)
            completed_items = len(items) - len(filtered_items)  # 已缓存的数量
            
            pbar = tqdm(total=total_items, desc=desc, ncols=80, dynamic_ncols=True)
            pbar.update(completed_items)  # 更新已缓存的进度
            
            failures = []
            
            for coro in asyncio.as_completed(tasks):
                idx, result, error = await coro
                if error:
                    failures.append((idx, error))
                    if logger:
                        logger.error(f"Task {idx} failed: {error}")
                results_with_idx.append((idx, result))
                pbar.update(1)
            
            pbar.close()
            return self._process_results(results_with_idx, failures, logger, cached_results)
        
        finally:
            self._stop_cache_writers()
    
    def thread_run(self, items: List[Any]) -> List[Any]:
        """多线程并发执行任务"""
        if not len(items):
            return []
        
        # 过滤已缓存的项目
        filtered_items, cached_results = self._filter_cached_items(items)
        if not filtered_items:
            return cached_results
        
        # 启动缓存写入器
        self._start_cache_writers()
        
        try:
            if self.config.disable_logger:
                logger = None
            else:
                logger = self.config.logger or self._get_default_logger("thread")
            
            # 定义任务函数 -> idx, result, error
            def wrapped_func(item_with_idx):
                idx, item = item_with_idx
                try:
                    if self.config.timeout:
                        # 使用 func_timeout 进行真正的超时控制
                        result = func_timeout(self.config.timeout, self.func, args=(item,))
                    else:
                        result = self.func(item)
                    
                    # 保存到缓存
                    self._save_result_to_cache(idx, result)
                    
                    if logger:
                        logger.debug(f"Successfully processed item {idx}")
                    return idx, result, None
                except FunctionTimedOut:
                    error_msg = f"Timeout after {self.config.timeout}s"
                    self._save_result_to_cache(idx, None, error_msg)
                    if logger:
                        logger.error(f"Item {idx} timeout: {error_msg}")
                    return idx, None, error_msg
                except Exception as e:
                    error_msg = str(e)
                    self._save_result_to_cache(idx, None, error_msg)
                    if logger:
                        logger.error(f"Error processing item {idx}: {error_msg}")
                    return idx, None, error_msg
            
            results_with_idx = []
            failures = []
            
            desc = f"{self.config.task_desc} " if self.config.task_desc else ""
            total_items = len(items)
            completed_items = len(items) - len(filtered_items)  # 已缓存的数量
            
            pbar = sync_tqdm(total=total_items, desc=desc, ncols=80, dynamic_ncols=True)
            pbar.update(completed_items)  # 更新已缓存的进度
            
            with ThreadPoolExecutor(max_workers=self.config.nproc) as executor:
                # 提交所有任务
                future_to_idx = {
                    executor.submit(wrapped_func, item_with_idx): item_with_idx[0]
                    for item_with_idx in filtered_items
                }
                
                # 处理完成的任务
                for future in as_completed(future_to_idx):
                    try:
                        idx, result, error = future.result()
                        
                        if error:
                            failures.append((idx, error))
                            if logger:
                                logger.error(f"Task {idx} failed: {error}")
                        results_with_idx.append((idx, result))
                        
                    except Exception as e:
                        # 这里处理其他可能的异常
                        idx = future_to_idx[future]
                        error_msg = str(e)
                        self._save_result_to_cache(idx, None, error_msg)
                        failures.append((idx, error_msg))
                        if logger:
                            logger.error(f"Task {idx} unexpected error: {error_msg}")
                        results_with_idx.append((idx, None))
                    
                    pbar.update(1)
            
            pbar.close()
            return self._process_results(results_with_idx, failures, logger, cached_results)
        
        finally:
            self._stop_cache_writers()
    
    def process_run(self, items: List[Any]) -> List[Any]:
        """多进程并发执行任务"""
        if not len(items):
            return []
        
        # 过滤已缓存的项目
        filtered_items, cached_results = self._filter_cached_items(items)
        if not filtered_items:
            return cached_results
        
        # 启动缓存写入器
        self._start_cache_writers()
        
        try:
            if self.config.disable_logger:
                logger = None
            else:
                logger = self.config.logger or self._get_default_logger("process")
            results_with_idx = []
            failures = []
            
            desc = f"{self.config.task_desc} " if self.config.task_desc else ""
            total_items = len(items)
            completed_items = len(items) - len(filtered_items)  # 已缓存的数量
            
            pbar = sync_tqdm(total=total_items, desc=desc, ncols=80, dynamic_ncols=True)
            pbar.update(completed_items)  # 更新已缓存的进度
            
            with ProcessPoolExecutor(max_workers=self.config.nproc) as executor:
                # 准备参数，包含超时时间
                process_args = [(item, idx, self.func, self.config.timeout) for idx, item in filtered_items]
                
                # 提交所有任务
                future_to_idx = {
                    executor.submit(_process_wrapper, args): args[1] 
                    for args in process_args
                }
                
                # 处理完成的任务
                for future in as_completed(future_to_idx, timeout=None):
                    try:
                        # 对于多进程，超时控制在子进程内部实现
                        # 这里可以设置一个稍长的超时作为安全网
                        future_timeout = (self.config.timeout + 5) if self.config.timeout else None
                        idx, result, error = future.result(timeout=future_timeout)
                        
                        if error:
                            self._save_result_to_cache(idx, None, error)
                            failures.append((idx, error))
                            if logger:
                                logger.error(f"Task {idx} failed: {error}")
                        else:
                            self._save_result_to_cache(idx, result)
                        
                        results_with_idx.append((idx, result))
                        
                    except concurrent.futures.TimeoutError:
                        idx = future_to_idx[future]
                        error_msg = f"Process timeout after {self.config.timeout}s"
                        self._save_result_to_cache(idx, None, error_msg)
                        failures.append((idx, error_msg))
                        if logger:
                            logger.error(f"Task {idx} process timeout: {error_msg}")
                        results_with_idx.append((idx, None))
                    
                    pbar.update(1)
            
            pbar.close()
            return self._process_results(results_with_idx, failures, logger, cached_results)
        
        finally:
            self._stop_cache_writers()
    
    def hybrid_run(self, items: List[Any]) -> List[Any]:
        """
        混合执行器：多进程 + 异步（支持缓存功能）
        将任务分配到多个进程，每个进程内部使用异步处理
        """
        if not len(items):
            return []
        
        if not asyncio.iscoroutinefunction(self.func):
            raise ValueError("hybrid_run requires an async function")
        
        # 过滤已缓存的项目
        filtered_items, cached_results = self._filter_cached_items(items)
        if not filtered_items:
            return cached_results
        
        if self.config.disable_logger:
            logger = None
        else:
            logger = self.config.logger or self._get_default_logger("hybrid")
        
        # 创建进度队列
        manager = Manager()
        progress_queue = manager.Queue()
        
        # 将任务分块分配给不同进程
        chunks = self._chunk_items([item for _, item in filtered_items], self.config.nproc)
        
        results_with_idx = []
        failures = []
        
        desc = f"{self.config.task_desc} " if self.config.task_desc else ""
        total_items = len(items)
        completed_items = len(items) - len(filtered_items)  # 已缓存的数量
        
        pbar = sync_tqdm(total=total_items, desc=desc, ncols=80, dynamic_ncols=True)
        pbar.update(completed_items)  # 更新已缓存的进度
        
        # 启动进度监控线程
        import threading
        progress_stop_event = threading.Event()
        
        def progress_monitor():
            """监控进度队列并更新进度条"""
            while not progress_stop_event.is_set():
                try:
                    # 非阻塞获取进度更新
                    while not progress_queue.empty():
                        progress_queue.get_nowait()
                        pbar.update(1)
                    progress_stop_event.wait(0.1)  # 每100ms检查一次
                except:
                    pass
        
        progress_thread = threading.Thread(target=progress_monitor)
        progress_thread.start()
        
        try:
            with ProcessPoolExecutor(max_workers=self.config.nproc) as executor:
                # 准备每个进程的参数
                process_args = []
                start_idx = 0
                filtered_idx_map = {i: original_idx for i, (original_idx, _) in enumerate(filtered_items)}
                
                for chunk_idx, chunk in enumerate(chunks):
                    if len(chunk):  # 确保chunk不为空
                        # 计算该chunk对应的原始索引起始位置
                        chunk_start_idx = start_idx
                        
                        # 准备缓存配置
                        cache_config = None
                        if self.config.cache_file:
                            # 为该chunk的第一个项目确定缓存文件路径
                            first_original_idx = filtered_idx_map.get(chunk_start_idx, 0)
                            cache_path = self.config.get_cache_path(first_original_idx)
                            cache_config = {
                                'cache_path': cache_path,
                                'index_field': self.config.index_field,
                                'error_field': self.config.error_field,
                                'result_field': self.config.result_field
                            }
                        
                        process_args.append((
                            chunk, 
                            self.func, 
                            self.config.ncoroutine, 
                            self.config.timeout, 
                            chunk_start_idx,  # 在filtered_items中的起始索引
                            progress_queue,
                            cache_config
                        ))
                        start_idx += len(chunk)
                
                # 提交所有进程任务
                future_to_info = {
                    executor.submit(_hybrid_worker_with_progress, args): {
                        'chunk': args[0],
                        'start_idx': args[4]
                    }
                    for args in process_args
                }
                
                # 处理完成的任务
                for future in as_completed(future_to_info):
                    try:
                        # 获取该进程处理的结果列表
                        chunk_results = future.result()
                        
                        info = future_to_info[future]
                        chunk_start_idx = info['start_idx']
                        
                        for relative_idx, result, error in chunk_results:
                            # 转换回原始索引
                            filtered_idx = chunk_start_idx + (relative_idx - chunk_start_idx)
                            original_idx = filtered_idx_map.get(filtered_idx, filtered_idx)
                            
                            if error:
                                failures.append((original_idx, error))
                                if logger:
                                    logger.error(f"Task {original_idx} failed: {error}")
                            results_with_idx.append((original_idx, result))
                            
                    except Exception as e:
                        # 如果整个进程失败，处理该chunk的所有任务
                        info = future_to_info[future]
                        chunk = info['chunk']
                        chunk_start_idx = info['start_idx']
                        
                        for i, item in enumerate(chunk):
                            filtered_idx = chunk_start_idx + i
                            original_idx = filtered_idx_map.get(filtered_idx, filtered_idx)
                            failures.append((original_idx, str(e)))
                            if logger:
                                logger.error(f"Process failed for task {original_idx}: {str(e)}")
                            results_with_idx.append((original_idx, None))
        finally:
            # 停止进度监控
            progress_stop_event.set()
            progress_thread.join()
            
            # 处理队列中剩余的进度更新
            while not progress_queue.empty():
                try:
                    progress_queue.get_nowait()
                    pbar.update(1)
                except:
                    break
        
        pbar.close()
        return self._process_results(results_with_idx, failures, logger, cached_results)
    
    def run(self, items: List[Any], mode: str = "auto") -> List[Any]:
        """
        自动选择执行模式或指定执行模式
        
        Args:
            items: 要处理的项目列表
            mode: 执行模式，可选 "auto", "async", "thread", "process", "hybrid"
                  "auto" 模式会根据函数类型自动选择
            
        Returns:
            处理结果列表
        """
        if not len(items):
            return []
        
        if mode == "auto":
            if asyncio.iscoroutinefunction(self.func):
                return asyncio.run(self.async_run(items))
            else:
                return self.thread_run(items)
        elif mode == "async":
            return asyncio.run(self.async_run(items))
        elif mode == "thread":
            return self.thread_run(items)
        elif mode == "process":
            return self.process_run(items)
        elif mode == "hybrid":
            return self.hybrid_run(items)
        else:
            raise ValueError(f"Unsupported mode: {mode}. Choose from 'auto', 'async', 'thread', 'process', 'hybrid'")


# 保持向后兼容的函数接口
def batch_async_executor(
    items: List[Any],
    func_async: Callable[[Any], Coroutine],
    nproc: Optional[int] = None,
    task_desc: str = "",
    logger: Optional[logging.Logger] = _async_logger,
    keep_order: bool = True,
    timeout: Optional[Union[int, float]] = None,
    cache_file: Optional[Union[str, Path]] = None,
    cache_dir: Optional[Union[str, Path]] = None,
    split_num: int = 1,
    index_field: str = "index",
    error_field: str = "error",
    result_field: str = "result",
    overwrite: bool = False
) -> List[Any]:
    """向后兼容的异步执行函数"""
    config = ExecutorConfig(
        nproc=nproc,
        task_desc=task_desc,
        logger=logger,
        disable_logger=logger is None,
        keep_order=keep_order,
        timeout=timeout,
        cache_file=cache_file,
        cache_dir=cache_dir,
        split_num=split_num,
        index_field=index_field,
        error_field=error_field,
        result_field=result_field,
        overwrite=overwrite
    )
    executor = Executor(func_async, config)
    return asyncio.run(executor.async_run(items))


def batch_thread_executor(
    items: List[Any],
    func: Callable[[Any], Any],
    nproc: Optional[int] = None,
    task_desc: str = "",
    logger: Optional[logging.Logger] = _thread_logger,
    keep_order: bool = True,
    timeout: Optional[Union[int, float]] = None,
    cache_file: Optional[Union[str, Path]] = None,
    cache_dir: Optional[Union[str, Path]] = None,
    split_num: int = 1,
    index_field: str = "index",
    error_field: str = "error",
    result_field: str = "result",
    overwrite: bool = False
) -> List[Any]:
    """向后兼容的线程执行函数"""
    config = ExecutorConfig(
        nproc=nproc,
        task_desc=task_desc,
        logger=logger,
        disable_logger=logger is None,
        keep_order=keep_order,
        timeout=timeout,
        cache_file=cache_file,
        cache_dir=cache_dir,
        split_num=split_num,
        index_field=index_field,
        error_field=error_field,
        result_field=result_field,
        overwrite=overwrite
    )
    executor = Executor(func, config)
    return executor.thread_run(items)


def batch_process_executor(
    items: List[Any],
    func: Callable[[Any], Any],
    nproc: Optional[int] = None,
    task_desc: str = "",
    logger: Optional[logging.Logger] = _process_logger,
    keep_order: bool = True,
    timeout: Optional[Union[int, float]] = None,
    cache_file: Optional[Union[str, Path]] = None,
    cache_dir: Optional[Union[str, Path]] = None,
    split_num: int = 1,
    index_field: str = "index",
    error_field: str = "error",
    result_field: str = "result",
    overwrite: bool = False
) -> List[Any]:
    """向后兼容的进程执行函数"""
    config = ExecutorConfig(
        nproc=nproc,
        task_desc=task_desc,
        logger=logger,
        disable_logger=logger is None,
        keep_order=keep_order,
        timeout=timeout,
        cache_file=cache_file,
        cache_dir=cache_dir,
        split_num=split_num,
        index_field=index_field,
        error_field=error_field,
        result_field=result_field,
        overwrite=overwrite
    )
    executor = Executor(func, config)
    return executor.process_run(items)


def batch_hybrid_executor(
    items: List[Any],
    func_async: Callable[[Any], Coroutine],
    nproc: int = 4,
    ncoroutine: Optional[int] = VIRTUAL_CORES,
    task_desc: str = "",
    logger: Optional[logging.Logger] = _hybrid_logger,
    keep_order: bool = True,
    timeout: Optional[Union[int, float]] = None,
    cache_file: Optional[Union[str, Path]] = None,
    cache_dir: Optional[Union[str, Path]] = None,
    split_num: int = 1,
    index_field: str = "index",
    error_field: str = "error",
    result_field: str = "result",
    overwrite: bool = False
) -> List[Any]:
    """混合执行器函数接口：多进程 + 异步"""
    config = ExecutorConfig(
        nproc=nproc,
        ncoroutine=ncoroutine,
        task_desc=task_desc,
        logger=logger,
        disable_logger=logger is None,
        keep_order=keep_order,
        timeout=timeout,
        cache_file=cache_file,
        cache_dir=cache_dir,
        split_num=split_num,
        index_field=index_field,
        error_field=error_field,
        result_field=result_field,
        overwrite=overwrite
    )
    executor = Executor(func_async, config)
    return executor.hybrid_run(items)


def batch_executor(
    items: List[Any],
    func: Callable[[Any], Any],
    nproc: Optional[int] = None,
    ncoroutine: Optional[int] = VIRTUAL_CORES,
    task_desc: str = "",
    logger: Optional[logging.Logger] = _thread_logger,
    keep_order: bool = True,
    timeout: Optional[Union[int, float]] = None,
    cache_file: Optional[Union[str, Path]] = None,
    cache_dir: Optional[Union[str, Path]] = None,
    split_num: int = 1,
    index_field: str = "index",
    error_field: str = "error",
    result_field: str = "result",
    overwrite: bool = False,
    mode: str = "auto"
):
    """向后兼容的自动执行函数"""
    config = ExecutorConfig(
        nproc=nproc,
        ncoroutine=ncoroutine,
        task_desc=task_desc,
        logger=logger,
        disable_logger=logger is None,
        keep_order=keep_order,
        timeout=timeout,
        cache_file=cache_file,
        cache_dir=cache_dir,
        split_num=split_num,
        index_field=index_field,
        error_field=error_field,
        result_field=result_field,
        overwrite=overwrite
    )
    executor = Executor(func, config)
    return executor.run(items, mode=mode)
