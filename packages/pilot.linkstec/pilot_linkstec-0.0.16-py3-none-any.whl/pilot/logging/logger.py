import logging
import sys
import threading

# コンソールカラーのコード定義
RESET = "\x1b[0m"
COLOR_MAP = {
    logging.DEBUG: "\x1b[37m",  # 白色
    logging.INFO: "\x1b[32m",  # 緑色
    logging.WARNING: "\x1b[33m",  # 黄色
    logging.ERROR: "\x1b[31m",  # 赤色
    logging.CRITICAL: "\x1b[41m",  # 赤背景白文字
}


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        color = COLOR_MAP.get(record.levelno, RESET)
        # スレッド名を取得
        thread_name = threading.current_thread().name
        thread_name = thread_name.split('_', 1)[1] if '_' in thread_name else thread_name
        # クラス名、メソッド名、行番号
        prefix = f"{self.formatTime(record, '%Y-%m-%d %H:%M:%S')} " \
                 f"[{record.levelname}] " \
                 f"[{thread_name}] " \
                 f"[{record.module}.{record.funcName}:{record.lineno}]"
        message = super().format(record)
        return f"{color}{prefix} {message}{RESET}"


_global_logger_configured = False


def setup_global_logger(log_level: int = logging.INFO):
    global _global_logger_configured

    if not _global_logger_configured:
        logging.basicConfig(
            level=log_level,
            format='%(message)s'
        )

        root_logger = logging.getLogger()
        if root_logger.handlers:
            root_logger.handlers.clear()

        handler = logging.StreamHandler(sys.stdout)
        formatter = ColoredFormatter('%(message)s')
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        root_logger.setLevel(log_level)

        _global_logger_configured = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
