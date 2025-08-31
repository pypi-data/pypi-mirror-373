import time
from functools import wraps

import structlog

logger = structlog.get_logger(__name__)


def timer_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 获取函数开始运行时间
        result = func(*args, **kwargs)  # 执行函数
        end_time = time.time()  # 获取函数结束运行时间
        elapsed_time = (end_time - start_time) * 1000  # 计算函数运行时间（单位：毫秒）

        cost = f"{elapsed_time:.3f}"

        msg = f"[{func.__name__}] 函数运行时间为 {cost} 毫秒"
        if elapsed_time < 3000:
            logger.info(msg)
        else:
            logger.warning(msg)
        return result

    return wrapper
