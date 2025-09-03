import time
from functools import wraps
from typing import Optional, Callable, Any, Tuple
from contextlib import deque

from .logger import Logger

logger = Logger()


def format_time(seconds: float, unit: str = "auto") -> Tuple[float, str]:
    """
    自动格式化时间，返回格式化后的时间值和单位

    Args:
        seconds: 时间（秒）
        unit: 显示单位，"auto"为自动选择

    Returns:
        (格式化后的时间值, 单位字符串)
    """
    if unit == "auto":
        if seconds < 1:
            return seconds * 1000, "ms"
        elif seconds < 60:
            return seconds, "s"
        elif seconds < 3600:
            return seconds / 60, "min"
        else:
            return seconds / 3600, "h"
    elif unit == "ms":
        return seconds * 1000, "ms"
    elif unit == "min":
        return seconds / 60, "min"
    elif unit == "h":
        return seconds / 3600, "h"
    else:
        return seconds, "s"


class Timer:
    """
    计时装饰器类，用于测量函数执行时间

    Args:
        timer_unit: 时间单位，支持 "auto"(自动选择), "ms"(毫秒), "s"(秒), "min"(分钟), "h"(小时)
        message: 自定义消息，默认使用函数名
    """

    def __init__(self, timer_unit: str = "auto", message: str = "", history_length: int = 100):
        self.timer_unit = timer_unit
        self.message = message
        self.turn = 0
        self.history = deque(maxlen=history_length)

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            display_message = self.message if self.message else func.__name__
            self.turn += 1
            logger.info(f"{display_message}: 开始执行")
            start_time = time.time()

            try:
                result = func(*args, **kwargs)

                elapsed_time = time.time() - start_time
                formatted_time, unit = format_time(elapsed_time, self.timer_unit)
                self.history.append(elapsed_time)
                avg_time = sum(self.history) / len(self.history)
                avg_formatted_time, avg_unit = format_time(avg_time, self.timer_unit)
                logger.info(
                    f"{display_message} 执行完成，耗时: {formatted_time:.3f} {unit}, 平均耗时: {avg_formatted_time:.3f} {avg_unit}"
                )
                return result

            except Exception as e:
                elapsed_time = time.time() - start_time
                formatted_time, unit = format_time(elapsed_time, self.timer_unit)
                self.history.append(elapsed_time)
                avg_time = sum(self.history) / len(self.history)
                avg_formatted_time, avg_unit = format_time(avg_time, self.timer_unit)
                logger.error(
                    f"{display_message} 执行失败，耗时: {formatted_time:.3f} {unit}，平均耗时: {avg_formatted_time:.3f} {avg_unit}，错误: {e}"
                )
                raise
            

        return wrapper


# 为了保持向后兼容，可以保留原来的函数版本
def timer(timer_unit: str = "auto", message: str = "", history_length: int = 100) -> Callable:
    """
    计时装饰器，用于测量函数执行时间

    Args:
        timer_unit: 时间单位，支持 "auto"(自动选择), "ms"(毫秒), "s"(秒), "min"(分钟), "h"(小时)
        message: 自定义消息，默认使用函数名

    Returns:
        装饰器函数

    Example:
        @timer()  # 自动选择单位
        def process_data():
            # 处理数据
            pass

        @timer("ms", "数据处理")
        def process_data():
            # 处理数据
            pass
    """
    return Timer(timer_unit, message)


class ContextTimer:
    """
    上下文管理器形式的计时器

    Args:
        name: 计时器名称
        unit: 时间单位，支持 "auto"(自动选择), "ms"(毫秒), "s"(秒), "min"(分钟), "h"(小时)

    Example:
        with ContextTimer("数据处理"):  # 自动选择单位
            # 处理数据
            pass

        with ContextTimer("数据处理", "ms"):
            # 处理数据
            pass
    """

    def __init__(self, name: str = "timer", unit: str = "auto"):
        self.name = name
        self.unit = unit
        self.start_time: Optional[float] = None

    def __enter__(self) -> "ContextTimer":
        logger.info(f"{self.name}: 开始计时")
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.start_time is None:
            return

        elapsed_time = time.time() - self.start_time
        formatted_time, unit = format_time(elapsed_time, self.unit)

        if exc_type is None:
            logger.info(f"{self.name} 执行完成，耗时: {formatted_time:.3f} {unit}")
        else:
            logger.error(f"{self.name} 执行异常，耗时: {formatted_time:.3f} {unit}")


def measure_time(func: Callable, *args, **kwargs) -> Tuple[Any, float]:
    """
    测量函数执行时间

    Args:
        func: 要测量的函数
        *args: 函数参数
        **kwargs: 函数关键字参数

    Returns:
        (函数返回值, 执行时间)
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    elapsed_time = time.time() - start_time
    return result, elapsed_time


def sleep_with_log(seconds: float, message: str = "") -> None:
    """
    带日志的睡眠函数

    Args:
        seconds: 睡眠时间（秒）
        message: 日志消息
    """
    msg = message or f"暂停 {seconds} 秒"
    logger.info(f"{msg}: 开始")
    time.sleep(seconds)
    logger.info(f"{msg}: 结束")
