import logging
import sys
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo
from colorama import Fore, Style, init
import os
import traceback

init(autoreset=True)

# ====================================================================================================
# ** 添加ok的日志级别 **
# 给默认的logging模块，添加一个用于表达成功的级别
# ====================================================================================================
OK_LEVEL = 25
logging.addLevelName(OK_LEVEL, "OK")

def ok(self, message, *args, **kwargs):
    if self.isEnabledFor(OK_LEVEL):
        self._log(OK_LEVEL, message, args, **kwargs)

logging.Logger.ok = ok

# ====================================================================================================
# ** 辅助函数 **
# - get_display_width(): 获取文本的显示宽度，中文字符算作1.685个宽度单位，以尽量保持显示居中
# ====================================================================================================
def get_display_width(text: str) -> int:
    width = 0
    for char in text:
        if unicodedata.east_asian_width(char) in ('F', 'W', 'A'):
            width += 1.685
        else:
            width += 1
    return int(width)

# ====================================================================================================
# ** 自定义Logger类封装所有功能 **
# ====================================================================================================
class Logger:
    OK_LEVEL = 25
    FORMATS = {
        logging.DEBUG: ('', ''),
        logging.INFO: (Fore.BLUE, "🔵 "),
        logging.WARNING: (Fore.YELLOW, "🔔 "),
        logging.ERROR: (Fore.RED, "❌ "),
        logging.CRITICAL: (Fore.RED + Style.BRIGHT, "⭕ "),
        OK_LEVEL: (Fore.GREEN, "✅ "),
    }

    def __init__(self, name='Log', show_time=False, use_color=True, timezone="Asia/Shanghai"):
        # 设置日志级别
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.show_time = show_time
        self.timezone = timezone  # 新增时区配置

        # 如果已存在 handlers，先清理
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # 控制台输出 handler
        console_handler = MinConsoleHandler(sys.stdout)
        console_handler.setFormatter(MinFormatter(use_color=use_color, show_time=show_time, timezone=timezone))
        self.logger.addHandler(console_handler)

        # 禁用传播到根日志记录器
        self.logger.propagate = False

    def divider(self, name='', sep='=', display_time=True):
        """打印带时间戳的分割线"""
        seperator_len = 72
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        middle = f' {name} {now} ' if display_time else f' {name} '
        middle_width = get_display_width(middle)
        decoration_count = max(4, (seperator_len - middle_width) // 2)
        line = sep * decoration_count + middle + sep * decoration_count

        if get_display_width(line) < seperator_len:
            line += sep

        self.logger.debug(line)

    def get_logger(self):
        """返回 logger 实例"""
        return self.logger

    # 为各个日志级别创建方法，便于编辑器提示
    def ok(self, message, *args, **kwargs):
        return self.logger.ok(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        return self.logger.info(message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        return self.logger.debug(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        return self.logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        return self.logger.error(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        return self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message, *args, **kwargs):
        return self.logger.exception(message, *args, **kwargs)

class MinFormatter(logging.Formatter):
    def __init__(self, use_color=True, show_time=False, timezone="Asia/Shanghai"):
        super().__init__("%(message)s")
        self.use_color = use_color
        self.show_time = show_time
        self.timezone = timezone  # 新增时区配置

    def format(self, record):
        original_message = record.getMessage()

        # 使用配置的时区
        local_tz = ZoneInfo(self.timezone)
        timestamp = f"[{datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S')}] " if self.show_time else ""

        if self.use_color:
            color, prefix = Logger.FORMATS.get(record.levelno, ('', ''))
            formatted_message = f"{timestamp}{color}{prefix}{original_message}{Style.RESET_ALL}"
        else:
            _, prefix = Logger.FORMATS.get(record.levelno, ('', ''))
            formatted_message = f"{timestamp}{prefix}{original_message}"

        # 添加异常信息
        if record.exc_info:
            exc_text = ''.join(traceback.format_exception(*record.exc_info))
            formatted_message += f"\n{Fore.RED}{exc_text}{Style.RESET_ALL}" if self.use_color else f"\n{exc_text}"

        return formatted_message

class MinConsoleHandler(logging.StreamHandler):
    def emit(self, record):
        if record.levelno == logging.DEBUG:
            print(self.format(record), flush=True)
        elif record.levelno == Logger.OK_LEVEL:
            super().emit(record)
            print()
        else:
            super().emit(record)

# ====================================================================================================
# ** 功能函数 **
# ====================================================================================================
def get_logger(name=None, file_path=None, show_time=False, use_color=True, timezone="Asia/Shanghai") -> Logger:
    if name is None:
        name = '_'
    logger_instance = Logger(name, show_time, use_color, timezone)  # 传递时区参数
    if file_path:
        # 如果目录不存在，创建目录
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        add_file_handler(logger_instance.get_logger(), file_path, show_time, timezone)
    return logger_instance

def add_file_handler(logger: logging.Logger, path: str, show_time=False, timezone="Asia/Shanghai"):
    # 添加文件日志输出，启用时间戳
    file_handler = logging.FileHandler(path)
    file_handler.setFormatter(MinFormatter(use_color=False, show_time=show_time, timezone=timezone))  # 传递时区参数
    logger.addHandler(file_handler)

# ====================================================================================================
# ** 示例使用 **
# ====================================================================================================
if __name__ == '__main__':
    # 获取日志对象
    logger = get_logger('xx', 'logs/application.log', show_time=True, use_color=True)  # This will use Logger

    # 输出日志信息
    logger.debug("调试信息，没有标记和颜色，等同于print")
    logger.info("提示信息，蓝色的，可以记录一些中间结果")
    logger.ok("完成提示，绿色的，通常表示成功和完成")
    logger.warning("警告信息，黄色的，通常表示警告")
    logger.error("错误信息，红色的，通常是报错的相关提示")
    logger.critical("重要提示，深红色。通常是非常关键的信息")

    # 使用 divider 方法
    logger.divider("这是一个分割线", sep='*', display_time=True)

    # 触发一个异常
    try:
        1 / 0
    except Exception:
        logger.exception("捕获到一个异常，程序将继续运行。")
