from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress

from .logger import Logger

logger = Logger()


def submit_task(func, item):
    """根据item的类型决定如何调用函数"""
    if isinstance(item, dict):
        # 检查是否是混合格式 {'args': (...), 'kwargs': {...}}
        if "args" in item and "kwargs" in item:
            return func(*item["args"], **item["kwargs"])
        elif "args" in item:
            return func(*item["args"])
        elif "kwargs" in item:
            return func(**item["kwargs"])
        else:
            # 纯字典，作为关键字参数
            return func(**item)
    elif isinstance(item, (tuple, list)) and not isinstance(item, str):
        # 元组或列表，作为位置参数
        return func(*item)
    else:
        # 单个值
        return func(item)


def parallel_map(func, items, description="running", max_workers=5):
    """
    并行执行函数，保证输出顺序与输入顺序一致

    Args:
        func: 要执行的函数
        items: 输入数据列表，支持以下格式：
            - 单个值的列表: [1, 2, 3]
            - 元组列表（位置参数）: [(1, 2), (3, 4), (5, 6)]
            - 字典列表（关键字参数）: [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
            - 混合格式：[{'args': (...), 'kwargs': {...}}, ...]
        max_workers: 最大工作线程数，默认为 5

    Returns:
        按输入顺序排列的结果列表

    Examples:
        # 单个参数
        parallel_map(lambda x: x * 2, [1, 2, 3])

        # 多个位置参数
        parallel_map(lambda x, y: x + y, [(1, 2), (3, 4), (5, 6)])

        # 关键字参数
        parallel_map(lambda a, b: a + b, [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}])

        # 混合参数
        parallel_map(lambda x, y, z=0: x + y + z,
                    [{'args': (1, 2), 'kwargs': {'z': 3}},
                     {'args': (4, 5), 'kwargs': {'z': 6}}])
    """
    results = [None] * len(items)

    with Progress() as progress:
        total_task = progress.add_task(f"[cyan]{description}...", total=len(items))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务，并保存任务和索引的映射
            future_to_index = {
                executor.submit(submit_task, func, item): i
                for i, item in enumerate(items)
            }

            # 按完成顺序获取结果，但保存到正确的位置
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    logger.info(f"index: {index}, result: {future.result()}")
                    results[index] = future.result()
                except Exception as e:
                    logger.error(f"Error in parallel_map: {e}")
                    results[index] = e
                progress.update(total_task, advance=1)

    return results
