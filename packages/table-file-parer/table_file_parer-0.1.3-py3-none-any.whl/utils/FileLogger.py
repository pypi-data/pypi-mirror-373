from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
import os
import yaml
from typing import Optional
from datetime import datetime, timedelta
from functools import wraps

current_sep = os.sep


class Timer:
    """独立计时工具（不依赖日志系统）"""

    def __init__(self, message: str = "计时任务"):
        self.message = message  # 任务描述（可选）
        self.start_time = None  # 开始时间（datetime 对象）
        self.elapsed_time = None  # 总耗时（timedelta 对象）

    def __enter__(self):
        """开始计时（with 语句进入时触发）"""
        self.start_time = datetime.now()
        return self  # 可选：返回实例供 with 语句绑定

    def __exit__(self, exc_type, exc_val, exc_tb):
        """结束计时（with 语句退出时触发）"""
        if self.start_time is not None:
            self.elapsed_time = datetime.now() - self.start_time

    def __call__(self, func):
        """作为装饰器使用（包装函数并计时）"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:  # 触发 __enter__ 和 __exit__
                result = func(*args, **kwargs)
            return result  # 返回原函数的结果

        return wrapper

    def get_elapsed_time(self, format: bool = True) -> str | timedelta:
        """获取耗时（支持格式化输出）

        Args:
            format: 是否返回格式化的字符串（如 "0小时3分钟15.23秒"），默认 True

        Returns:
            格式化字符串 或 timedelta 对象
        """
        if self.elapsed_time is None:
            raise ValueError("计时未完成，请先执行计时逻辑（with 语句或装饰器）")

        if not format:
            return self.elapsed_time

        # 分解 timedelta 为 小时:分钟:秒
        total_seconds = self.elapsed_time.total_seconds()
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours)}小时{int(minutes)}分钟{seconds:.2f}秒"

class FileErrorLogger:
    """管理混合模式错误日志的工具类（文件级覆盖+日期级增量）"""

    def __init__(self, base_log_dir: str = None):
        config = self.load_config()
        config_base_log_dir = config.get('paths', {}).get('log_root', f'{current_sep}default{current_sep}logs')
        if base_log_dir:
            base_log_dir = base_log_dir
        elif config_base_log_dir:
            base_log_dir = config_base_log_dir
        else:
            base_log_dir = f"..{current_sep}logs"
        self.base_log_dir = base_log_dir
        self.daily_log_dir = os.path.join(base_log_dir, "daily")  # 日期级日志目录（增量）
        self.file_log_dir = os.path.join(base_log_dir, "file_specific")  # 文件级日志目录（覆盖）

        # 初始化目录
        os.makedirs(self.daily_log_dir, exist_ok=True)
        os.makedirs(self.file_log_dir, exist_ok=True)

        # 初始化日期级增量日志器（保持原有逻辑）
        self.daily_logger = self._setup_daily_logger()

    def _setup_daily_logger(self) -> logging.Logger:
        """配置日期级增量错误日志器（保持追加模式）"""
        logger = logging.getLogger("daily_error_logger")
        logger.setLevel(logging.ERROR)

        if not logger.handlers:
            current_date = datetime.now().strftime("%Y-%m-%d")
            base_filename = f"daily_error_{current_date}.log"
            log_path = os.path.join(self.daily_log_dir, base_filename)

            file_handler = TimedRotatingFileHandler(
                filename=log_path,
                when="midnight",
                interval=1,
                backupCount=30,
                encoding="utf-8",
                delay=True
            )
            file_handler.suffix = "%Y-%m-%d.log"

            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(module)s.%(funcName)s:%(lineno)d - %(message)s"
            )
            file_handler.setFormatter(formatter)

            logger.addHandler(file_handler)

        return logger

    def get_file_error_logger(self, filename: str) -> logging.Logger:
        try:
            # 获取文件级覆盖模式的错误日志器（每次写入清空文件）
            # 清理非法字符（防止目录穿越）
            safe_filename = "".join(c if c.isalnum() or c in ('.', '_', '-') else '_' for c in filename)
            log_filename = f"{safe_filename}_error.log"
            log_path = os.path.join(self.file_log_dir, log_filename)

            # 创建专用日志器（使用文件名作为唯一标识）
            logger_name = f"file_error_{safe_filename}"
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.ERROR)

            # 关键修改：每次获取日志器时，先移除旧处理器（避免重复写入）
            for handler in logger.handlers[:]:  # 遍历副本防止迭代时修改
                logger.removeHandler(handler)
                handler.close()  # 显式关闭旧处理器

            # 创建新的文件处理器（覆盖模式）
            file_handler = logging.FileHandler(
                filename=log_path,
                mode='w',  # 关键：覆盖模式（每次打开文件时清空内容）
                encoding="utf-8",
                delay=True  # 延迟创建文件（首次写入时创建）
            )

            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] 处理文件: %(filename)s - %(message)s"
            )
            file_handler.setFormatter(formatter)

            # 添加过滤器传递文件名信息
            file_handler.addFilter(lambda record: setattr(record, "filename", filename) or True)

            logger.addHandler(file_handler)
            return logger
        except Exception as e:
            print(f"获取文件级日志器失败: {e}")
            raise

    def output_log(self, message: str, file_path: Optional[str] = None):
        """输出日志到文件级或日期级日志器"""
        if file_path:
            # 使用文件级日志器
            file_logger = self.get_file_error_logger(file_path)
            file_logger.error(f"错误详情: {str(message)}", exc_info=True)  # 每次调用都会清空文件

        daily_logger = self.daily_logger
        daily_logger.error(
                f"处理文件 {file_path} 时发生错误: {str(message)}",
                exc_info=True
            )

    def get_file_log_dir(self) -> str:
        """获取文件级日志目录"""
        return self.file_log_dir

    def get_daily_log_dir(self) -> str:
        """获取日期级日志目录"""
        return self.daily_log_dir

    def load_config(self, config_path=f"configs{current_sep}config.yaml"):
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"配置文件 {config_path} 不存在！")
            return {}



def get_timer(self, file_path: str) -> Timer:
    """获取带文件路径信息的计时器（支持上下文/装饰器）"""
    return Timer(
        logger=self.time_logger,
        message=f"文件: {file_path}"
    )


if __name__ == "__main__":
    logger_manager = FileErrorLogger()


    def process_file(file_path: str):
        """模拟多次处理同一文件的场景"""
        try:
            # 模拟随机错误（100%触发）
            raise ValueError(f"处理失败（时间戳：{datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            # 1. 文件级日志（覆盖模式）
            file_logger = logger_manager.get_file_error_logger(file_path)
            file_logger.error(f"错误详情: {str(e)}", exc_info=True)  # 每次调用都会清空文件

            # 2. 日期级日志（增量模式）
            logger_manager.daily_logger.error(
                f"处理文件 {file_path} 时发生错误: {str(e)}",
                exc_info=True
            )


    with Timer() as timer:
        # 第一次处理文件（生成新日志）
        process_file("data/test_file.csv")
        # 第二次处理同一文件（覆盖上次文件级日志）
        process_file("data/test_file.csv")
        # 处理不同文件（生成独立覆盖日志）
        process_file("data/another_file.txt")
    elapsed = timer.get_elapsed_time(format=False)
    print(f"总秒数：{elapsed.total_seconds():.2f}s")  # 输出：总秒数：1.80s