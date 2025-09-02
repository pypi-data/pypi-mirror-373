import threading
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, Future, wait as _wait
from functools import partial
from typing import Callable

from loguru import logger


class BasePool(ABC):
    """线程池基类"""

    def __init__(self, speed: int = 10, limit: int = 10):
        self.speed = speed
        self.pool = ThreadPoolExecutor(max_workers=self.speed)
        self.count = 0
        self.max_count = limit
        self.running_futures: list[Future] = []

    def __enter__(self) -> "BasePool":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close(wait=False)

    def close(self, wait: bool = True, cancel_futures: bool = False):
        """关闭线程池"""
        self.pool.shutdown(wait=wait, cancel_futures=cancel_futures)

    def done(self, func_name: str, future: Future):
        """统一的回调处理"""
        try:
            future.result()
        except Exception as e:
            logger.error(f"{func_name} => {e}")

    @abstractmethod
    def add(self, func: Callable, *args, **kwargs):
        pass

    def adds(self, func: Callable, *iterables):
        """批量添加任务"""
        for args in zip(*iterables):
            self.add(func, *args)

    def record(self, func: Callable, *args, **kwargs) -> Future:
        """提交任务并记录"""
        future = self.pool.submit(func, *args, **kwargs)
        self.count += 1
        self.running_futures.append(future)
        return future

    def block(self):
        """阻塞直到所有任务完成"""
        _wait(self.running_futures)

    def is_running(self) -> bool:
        """是否有任务正在运行"""
        return any(f.running() for f in self.running_futures)


class PoolWait(BasePool):
    """等待当前批次任务完成后再添加新任务"""

    def add(self, func: Callable, *args, **kwargs):
        if self.count >= self.max_count:
            self.block()
            self.count = 0
            self.running_futures.clear()
        future = self.record(func, *args, **kwargs)
        future.add_done_callback(partial(self.done, func.__name__))


class PoolMan(BasePool):
    """动态管理任务，有空位就添加新任务"""

    def __init__(self, speed: int = 10, limit: int = 10):
        super().__init__(speed, limit)
        self.lock = threading.Condition()

    def add(self, func: Callable, *args, **kwargs):
        with self.lock:
            while self.count >= self.max_count:
                self.lock.wait()
            future = self.record(func, *args, **kwargs)
            future.add_done_callback(partial(self._done_callback, func.__name__))

    def _done_callback(self, func_name: str, future: Future):
        """任务完成后的回调"""
        self.done(func_name, future)
        with self.lock:
            self.count -= 1
            if future in self.running_futures:
                self.running_futures.remove(future)
            self.lock.notify()


if __name__ == "__main__":
    import time, random
    from toolsman import printc

    def task(x):
        printc(f"task {x} running...", "yellow")
        time.sleep(random.randint(1, 3))
        printc(f"task {x} done", "green")

    # 使用 PoolWait
    with PoolWait() as pool:
        for i in range(30):
            pool.add(task, i + 1)

    print("=" * 50)

    # 使用 PoolMan
    with PoolMan() as pool:
        for i in range(30):
            pool.add(task, i)
