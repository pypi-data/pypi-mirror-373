# validator.py
from typing import Callable, Awaitable, List, Optional, TypeVar, Union
import asyncio
from contextlib import asynccontextmanager
from tqdm.asyncio import tqdm
from tqdm import tqdm as sync_tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import signal
from batch_executor.constants import PHYSICAL_CORES, VIRTUAL_CORES

T = TypeVar('T')
def _process_timeout_handler(signum, frame):
    """信号处理函数，用于多进程超时"""
    raise TimeoutError("Process validation timeout")

def _process_verify_wrapper(args):
    """多进程验证包装函数"""
    item, verify_func, timeout = args
    try:
        if timeout:
            # 设置信号处理器
            signal.signal(signal.SIGALRM, _process_timeout_handler)
            signal.alarm(int(timeout))
        
        result = verify_func(item)
        
        if timeout:
            signal.alarm(0)  # 取消超时
        
        return True if result else False
    except TimeoutError:
        return False
    except Exception:
        return False
    finally:
        if timeout:
            signal.alarm(0)  # 确保取消超时
class Validator:
    """
    Validator that checks multiple items in parallel with concurrency control.
    Supports both async and process-based validation.
    Validates items in groups where finding one valid item in a group is sufficient.
    """
    def __init__(
        self,
        verify_func: Union[Callable[[T], Awaitable[bool]], Callable[[T], bool]],
        nproc: Optional[int] = None,
        timeout: Optional[float] = None,
        group_timeout: Optional[float] = None,
        show_progress: bool = True
    ):
        """
        Initialize the validator.
        
        Args:
            verify_func: Function that validates a single item (async or sync)
            nproc: Maximum number of concurrent validations
            timeout: Timeout for individual item validation
            group_timeout: Overall timeout for group validation
            show_progress: Whether to show progress bar
        """
        self.verify_func = verify_func
        self.nproc = nproc or PHYSICAL_CORES
        self.timeout = timeout
        self.group_timeout = group_timeout
        self.show_progress = show_progress
        self.is_async = asyncio.iscoroutinefunction(verify_func)
        
        if self.is_async:
            self.semaphore = asyncio.Semaphore(self.nproc)
            # 包装异步验证函数
            async def verify_async(item: T) -> bool:
                try:
                    return await verify_func(item)
                except Exception:
                    return False
            self.verify_func_async = verify_async

    @asynccontextmanager
    async def _verify_with_sem(self):
        """Context manager to control concurrent validations using semaphore"""
        async with self.semaphore:
            yield

    async def any_valid_in_group_async(self, items: List[T], pbar=None) -> bool:
        """
        Asynchronously validate a group of items until finding first valid item.
        
        Args:
            items: List of items to validate
            pbar: Optional progress bar instance
            
        Returns:
            True if any item is valid, False otherwise
        """
        if not items:
            return False

        tasks = set()
        try:
            # Create concurrent validation tasks
            for item in items:
                async with self._verify_with_sem():
                    task = asyncio.create_task(self.verify_func_async(item))
                    tasks.add(task)

            start_time = asyncio.get_event_loop().time()
            items_processed = 0

            while tasks:
                # Check group timeout
                if self.group_timeout:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed > self.group_timeout:
                        return False

                # Wait for next completed task
                done, pending = await asyncio.wait(
                    tasks,
                    timeout=self.timeout,
                    return_when=asyncio.FIRST_COMPLETED
                )

                if not done:
                    return False

                # Process completed tasks
                for task in done:
                    items_processed += 1
                    if pbar:
                        pbar.update(1)
                    try:
                        result = task.result()
                        if result:
                            # Cancel remaining tasks if valid item found
                            for t in pending:
                                t.cancel()
                            return True
                    except Exception:
                        pass
                tasks = pending
            return False
        finally:
            # Cleanup remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()

    def any_valid_in_group_process(self, items: List[T], pbar=None) -> bool:
        """
        Validate a group of items using multiprocessing until finding first valid item.
        
        Args:
            items: List of items to validate
            pbar: Optional progress bar instance
            
        Returns:
            True if any item is valid, False otherwise
        """
        if not items:
            return False

        start_time = time.time()
        
        with ProcessPoolExecutor(max_workers=min(self.nproc, len(items))) as executor:
            # 提交所有验证任务
            future_to_item = {
                executor.submit(_process_verify_wrapper, (item, self.verify_func, self.timeout)): item
                for item in items
            }
            
            try:
                for future in as_completed(future_to_item):
                    # Check group timeout
                    if self.group_timeout:
                        elapsed = time.time() - start_time
                        if elapsed > self.group_timeout:
                            # Cancel remaining tasks
                            for f in future_to_item:
                                if not f.done():
                                    f.cancel()
                            return False
                    
                    if pbar:
                        pbar.update(1)
                    
                    try:
                        result = future.result()
                        if result:
                            # Found valid item, cancel remaining tasks
                            for f in future_to_item:
                                if not f.done():
                                    f.cancel()
                            return True
                    except Exception:
                        continue
                
                return False
            except Exception:
                return False

    def any_valid_in_group(self, items: List[T], mode: str = "auto") -> bool:
        """
        Validate a single group with automatic or specified mode selection.
        
        Args:
            items: List of items to validate
            mode: Validation mode ("auto", "async", "process")
            
        Returns:
            True if any item is valid, False otherwise
        """
        if mode == "auto":
            if self.is_async:
                return asyncio.run(self.any_valid_in_group_async(items))
            else:
                return self.any_valid_in_group_process(items)
        elif mode == "async":
            if not self.is_async:
                raise ValueError("Async mode requires an async verify function")
            return asyncio.run(self.any_valid_in_group_async(items))
        elif mode == "process":
            if self.is_async:
                raise ValueError("Process mode requires a sync verify function")
            return self.any_valid_in_group_process(items)
        else:
            raise ValueError(f"Unsupported mode: {mode}. Choose from 'auto', 'async', 'process'")

    async def validate_groups_async(self, groups: List[List[T]]) -> List[bool]:
        """
        Validate multiple groups concurrently using async mode.
        
        Args:
            groups: List of item groups to validate
            
        Returns:
            List of validation results (True/False) for each group
        """
        if not self.is_async:
            raise ValueError("Async validation requires an async verify function")
            
        total_items = sum(len(group) for group in groups)
        items_pbar = tqdm(total=total_items, desc="Items", disable=not self.show_progress)

        try:
            # Create tasks for all groups
            tasks = [
                self.any_valid_in_group_async(group, items_pbar) 
                for group in groups
            ]
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions in results
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    processed_results.append(False)
                else:
                    processed_results.append(result)
            return processed_results
        finally:
            items_pbar.close()

    def validate_groups_process(self, groups: List[List[T]]) -> List[bool]:
        """
        Validate multiple groups using multiprocessing.
        
        Args:
            groups: List of item groups to validate
            
        Returns:
            List of validation results (True/False) for each group
        """
        if self.is_async:
            raise ValueError("Process validation requires a sync verify function")
            
        total_items = sum(len(group) for group in groups)
        items_pbar = sync_tqdm(total=total_items, desc="Items", disable=not self.show_progress)

        try:
            results = []
            
            # Process each group
            for group in groups:
                result = self.any_valid_in_group_process(group, items_pbar)
                results.append(result)
            
            return results
        finally:
            items_pbar.close()

    def validate_groups(self, groups: List[List[T]], mode: str = "auto") -> List[bool]:
        """
        Validate multiple groups with automatic or specified mode selection.
        
        Args:
            groups: List of item groups to validate
            mode: Validation mode ("auto", "async", "process")
                  "auto" automatically selects based on function type
            
        Returns:
            List of validation results (True/False) for each group
        """
        if mode == "auto":
            if self.is_async:
                return asyncio.run(self.validate_groups_async(groups))
            else:
                return self.validate_groups_process(groups)
        elif mode == "async":
            if not self.is_async:
                raise ValueError("Async mode requires an async verify function")
            return asyncio.run(self.validate_groups_async(groups))
        elif mode == "process":
            if self.is_async:
                raise ValueError("Process mode requires a sync verify function")
            return self.validate_groups_process(groups)
        else:
            raise ValueError(f"Unsupported mode: {mode}. Choose from 'auto', 'async', 'process'")
    
# 便捷函数
def validate_any(
    items: List[T], 
    verify_func: Union[Callable[[T], Awaitable[bool]], Callable[[T], bool]],
    nproc: Optional[int] = None,
    timeout: Optional[float] = None,
    group_timeout: Optional[float] = None,
    show_progress: bool = True
) -> bool:
    """
    便捷函数：自动选择模式验证单个组，找到任意一个有效项即返回True
    
    Args:
        items: 要验证的项目列表
        verify_func: 验证函数（异步或同步）
        nproc: 最大并发/进程数
        timeout: 单个项目超时时间
        group_timeout: 整组超时时间
        show_progress: 是否显示进度条
        
    Returns:
        True if any item is valid, False otherwise
    """
    validator = Validator(verify_func, nproc, timeout, group_timeout, show_progress)
    return validator.any_valid_in_group(items)

def validate_groups(
    groups: List[List[T]], 
    verify_func: Union[Callable[[T], Awaitable[bool]], Callable[[T], bool]],
    nproc: Optional[int] = None,
    timeout: Optional[float] = None,
    group_timeout: Optional[float] = None,
    show_progress: bool = True,
    mode: str = "auto"
) -> List[bool]:
    """
    便捷函数：批量验证多个组
    
    Args:
        groups: 要验证的组列表
        verify_func: 验证函数（异步或同步）
        nproc: 最大并发/进程数
        timeout: 单个项目超时时间
        group_timeout: 整组超时时间
        show_progress: 是否显示进度条
        mode: 验证模式 ("auto", "async", "process")
        
    Returns:
        List of validation results for each group
    """
    validator = Validator(verify_func, nproc, timeout, group_timeout, show_progress)
    return validator.validate_groups(groups, mode)
