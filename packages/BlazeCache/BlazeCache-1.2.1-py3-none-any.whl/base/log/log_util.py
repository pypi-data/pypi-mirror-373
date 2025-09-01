import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from typing import Optional, Union, Any

class BccacheLogger:
    """自定义日志封装类，统一项目日志接口"""
    
    def __init__(self, 
                 name: str = "app", 
                 level: Union[str, int] = logging.INFO,
                 use_console: bool = True,
                 log_file: Optional[str] = None,
                 max_file_size: int = 100 * 1024 * 1024,  # 100MB
                 backup_count: int = 5):
        """
        初始化日志类
        
        Args:
            name: 日志名称
            level: 日志级别, 设置最低日志级别, 低于该级别的日志会被忽略
            use_console: 是否输出到控制台
            log_file: 日志文件路径, None表示不输出到文件
            max_file_size: 单个日志文件最大大小
            backup_count: 日志文件备份数量
        """
        self.name = name
        self.level = level
        self.use_console = use_console
        self.log_file = log_file
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # 初始化日志器
        self._logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """
        配置并返回日志器, 后续如果要更换 logger, 从该函数更改即可
        """
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        logger.propagate = False  # 防止日志重复输出
        
        # 清除已有的处理器
        if logger.hasHandlers():
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
        
        # 添加处理器
        if self.use_console:
            logger.addHandler(self._get_console_handler())
        
        if self.log_file:
            logger.addHandler(self._get_file_handler())
        
        return logger
    
    def _get_console_handler(self) -> logging.Handler:
        """获取控制台处理器"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)
        console_handler.setFormatter(self._get_formatter())
        return console_handler
    
    def _get_file_handler(self) -> logging.Handler:
        """获取文件处理器（支持日志切割）"""
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.level)
        file_handler.setFormatter(self._get_formatter())
        return file_handler
    
    def _get_formatter(self) -> logging.Formatter:
        """获取日志格式化器"""
        # 日志格式：时间 | 级别 | 名称 | 消息
        return logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S.%f"[:-3]  # 显示到毫秒
        )
    
    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录DEBUG级别日志"""
        self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录INFO级别日志"""
        self._logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录WARNING级别日志"""
        self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args: Any, exc_info: bool = False, **kwargs: Any) -> None:
        """记录ERROR级别日志"""
        self._logger.error(message, *args, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录CRITICAL级别日志"""
        self._logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录异常日志（自动包含异常堆栈）"""
        self._logger.exception(message, *args, **kwargs)
    
    def set_level(self, level: Union[str, int]) -> None:
        """设置日志级别"""
        self.level = level
        self._logger.setLevel(level)
        for handler in self._logger.handlers:
            handler.setLevel(level)
    
    def add_file_handler(self, file_path: str) -> None:
        """添加文件处理器"""
        self.log_file = file_path
        self._logger.addHandler(self._get_file_handler())
