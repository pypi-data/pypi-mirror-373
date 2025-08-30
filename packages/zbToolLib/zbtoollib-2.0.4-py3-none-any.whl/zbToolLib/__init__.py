from .info import *
from .data import *
from .file import *
from .web import *
from .system import *

def threadPoolDecorator(thread_pool:ThreadPoolExecutor):
    def warpFunction(func):
        def warpper(*args):
            thread_pool.submit(func, *args)
        return warpper
    return warpFunction

logging.info("程序api初始化成功！")
