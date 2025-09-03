import os
import time

import random
from functools import wraps

import natsort

from .logger import Logger

logger = Logger()


def makedirs(path):
    """"""
    if not os.path.isdir(path):
        os.makedirs(path)


def walk(path, types=None, max_depth=float("inf")):
    """"""
    depth = 0
    for root, dirs, filenames in os.walk(path):
        if depth >= max_depth:
            break
        depth += 1
        for filename in filenames:
            if types:
                type = filename.split(".")[-1]
                if type in types:
                    yield os.path.join(root, filename)
                    continue
            else:
                yield os.path.join(root, filename)


def walk_dirs(path, max_depth=float("inf")):
    """"""
    depth = 0
    yield path  # 返回根目录
    for root, dirs, filenames in os.walk(path):
        if depth >= max_depth:
            break
        depth += 1
        for dir in dirs:
            yield os.path.join(root, dir)


def probability_trigger(prob=0.5):
    """
    Args:
        prob: float, probability of triggering
    """
    if random.random() < prob:
        logger.info(f"probability_trigger: True, prob: {prob}")
        return True
    logger.info(f"probability_trigger: False, prob: {prob}")
    return False


def retry(retries=3, delay=1, backoff=0.25):
    """
    description:
    param:
    return:
    """

    def decorator(func):
        """
        description:
        param:
        return:
        """

        def wrapper(*args, **kwargs):
            """
            description:
            param:
            return:
            """

            attempts = retries
            while attempts > 0:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts -= 1
                    if attempts == 0:
                        logger.error("retry failed")
                        raise Exception("retry failed")
                        # return None

                    # 给delay加上25%的随机数，避免多个请求同时重试
                    r_delay = delay + delay * backoff * (1 - 2 * random.random())
                    r_delay = max(0, r_delay)

                    logger.error(
                        f"{e}, retrying after {r_delay:.2f} seconds, {attempts} retries left"
                    )

                    time.sleep(r_delay)

        return wrapper

    return decorator


def return_on_error(default_value=None):
    """
    装饰器：当函数执行失败时返回指定的默认值

    Args:
        default_value: 发生异常时返回的默认值，默认为 None

    Example:
        @return_on_error(default_value=[])
        def process_data():
            # 如果发生异常，将返回 []
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Function {func.__name__} failed with error: {str(e)}")
                return default_value

        return wrapper

    return decorator


def sample_lines(lines, num, seed=None):
    if seed is not None:
        random.seed(seed)
    # 创建列表副本以避免修改原始列表
    lines_copy = lines.copy()
    # 对副本进行随机打乱
    random.shuffle(lines_copy)
    return lines_copy[:num]


def sample_files(files, num, seed=None):
    files = natsort.natsorted(files)
    files = sample_lines(files, num, seed)
    files = natsort.natsorted(files)
    return files
