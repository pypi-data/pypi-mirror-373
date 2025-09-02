import asyncio
import time
from batch_executor import Validator, validate_any, validate_groups

# 同步验证函数
def sync_verify(item):
    time.sleep(0.1)  # 模拟验证过程
    return item > 5

# 异步验证函数
async def async_verify(item):
    await asyncio.sleep(0.1)  # 模拟异步验证过程
    return item > 5

# 使用类接口
def test_validate_any():
    validator = Validator(sync_verify, nproc=4, timeout=1.0)
    # 验证单个组
    items = [1, 2, 3, 6, 7, 8]
    result = validator.any_valid_in_group(items)  # 自动选择进程模式
    print(f"Any valid in group: {result}")  # True (因为6, 7, 8 > 5)

    # 验证多个组
    groups = [[1, 2, 3], [6, 7, 8], [4, 5]]
    results = validator.validate_groups(groups, mode="process")
    print(f"Group results: {results}")  # [False, True, False]

    # 使用便捷函数
    # 验证单个组 - 自动模式
    result = validate_any([1, 2, 3, 6], sync_verify, nproc=4)
    print(f"Any valid: {result}")  # True

    # 验证单个组 - 异步模式
    result = validate_any([1, 2, 3, 6], async_verify, nproc=4)
    print(f"Any valid (async): {result}")  # True

    # 验证单个组 - 进程模式
    result = validate_any([1, 2, 3, 6], sync_verify, nproc=4)
    print(f"Any valid (process): {result}")  # True

def test_validate_groups():
    # 批量验证多个组
    groups = [[1, 2], [6, 7], [3, 4]]
    results = validate_groups(groups, sync_verify, nproc=4, mode="process")
    print(f"Batch results: {results}")  # [False, True, False]
