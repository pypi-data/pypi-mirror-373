import ctypes
import inspect
import random
import time
from concurrent.futures import as_completed, Future
from datetime import datetime, timedelta
from threading import Thread
from pathlib import Path

from loguru import logger


now = lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_file(file_path: str):
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


class Timer:
    """记录耗时（上下文模式）"""

    def __init__(self, name: str = None):
        self.name = name or "Timer"
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.perf_counter()
        elapsed = end_time - self.start_time
        printc(f"{repr(self.name)} Cons {elapsed:.2f}S", "red")
        return False


def printv(*args, newline=True, sep="    ", rstrip=True):
    """打印变量的名称、值"""
    frame = inspect.currentframe().f_back
    vars = frame.f_locals
    s = ""
    for name, value in vars.items():
        if value in args:
            tail = "\n" if newline else sep
            part = f"{name}: {value!r}{tail}"
            s += part
    print(s.rstrip() if rstrip else s)


def ts2time(ts: float) -> str:
    """时间戳转时间"""
    date_fmt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
    return date_fmt


def time2ts(date_fmt: str) -> int:
    """时间转时间戳"""
    ts = time.mktime(time.strptime(date_fmt, "%Y-%m-%d %H:%M:%S"))
    return int(ts)


def today_anytime_ts(hour: int, minute: int, second=0) -> float:
    """获取今天任意时刻的时间戳"""
    now = datetime.now()
    today_0 = now - timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
    today_anytime = today_0 + timedelta(hours=hour, minutes=minute, seconds=second)
    ts = today_anytime.timestamp()
    return ts


def timef(ts: int | float) -> str:
    """时间戳（秒）转时间"""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def nget(src: dict, args: str, failed=None):
    """字典多层取值，键不存在则返回 `failed` 的值"""
    temp = src
    for i, a in enumerate(args.split(".")):
        if a not in temp:
            printc(f"KEY {a!r} miss", "red")
            return failed
        temp = temp.get(a)
        if i == len(args) - 1:
            return temp
        if not isinstance(temp, dict):
            printc(f"KEY {a!r} VALUE {temp!r} not is dict", "red")
            return failed
    return temp


def kill_thread(thread: Thread):
    """强制杀死线程"""
    tid = thread.ident
    exctype = SystemExit
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))


def wait_fs_results(fs: list[Future], timeout: float = None):
    """等待多个线程的结果。有序获取（先返回的靠前）所有线程的返回值（不包括异常的线程、None值）"""
    results = []
    try:
        for v in as_completed(fs, timeout=timeout):
            try:
                result = v.result()
                if result is not None:
                    results.append(result)
            except Exception as e:
                logger.error(e)
    except Exception as e:
        logger.error(e)
    return results


COLOR_CODES = {
    "black": "30",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "magenta": "35",
    "cyan": "36",
    "white": "37",
    "gray": "90",
    "light_red": "91",
    "light_green": "92",
    "light_yellow": "93",
    "light_blue": "94",
    "light_magenta": "95",
    "light_cyan": "96",
    "light_white": "97",
}


def printc(content, color: str):
    """输出（可指定颜色）"""
    color_code = COLOR_CODES.get(color)
    if color_code:
        print(f"\033[{color_code}m{content}\033[0m")
    else:
        print(content)


def make_ua():
    """制作一个随机User-Agent"""
    a = random.randint(55, 62)
    c = random.randint(0, 3200)
    d = random.randint(0, 150)
    os_type = [
        "(Windows NT 6.1; WOW64)",
        "(Windows NT 10.0; WOW64)",
        "(X11; Linux x86_64)",
        "(Macintosh; Intel Mac OS X 10_12_6)",
    ]
    chrome_version = f"Chrome/{a}.0.{c}.{d}"
    os_choice = random.choice(os_type)
    ua = f"Mozilla/5.0 {os_choice} AppleWebKit/537.36 (KHTML, like Gecko) {chrome_version} Safari/537.36"
    return ua


if __name__ == "__main__":
    printc("py3", "red")
    printc("py3", "yellow")
    printc("py3", "blue")
    printc("py3", "green")

    maps = {"data": {"all": {"core": {"name": "CLOS", "age": 22}}}}
    r = nget(maps, "data.all.core")
    print(r)

    name, age = "CLOS", 22
    printv(name, age)

    from concurrent.futures import ThreadPoolExecutor

    pool = ThreadPoolExecutor(max_workers=5)

    def work(tid):
        while 1:
            print(f"{tid} is running")
            n = random.randint(1, 100)
            if n % 2 == 0 and n > 20:
                print(f"{tid} is OK")
                return n
            time.sleep(1)

    fs = [pool.submit(work, i) for i in range(5)]

    with Timer("Pool"):
        rs = wait_fs_results(fs)
        print(rs)
