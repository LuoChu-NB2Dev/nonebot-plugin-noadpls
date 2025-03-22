from typing import Optional, Union, Any
import inspect
from nonebot.log import logger


class Log:
    """日志记录器"""

    def __init__(self, name: Optional[str] = None) -> None:
        """
        初始化日志记录器
        
        Args:
            name: 记录器名称，默认为自动检测调用模块名
        """
        if name is None:
            # 自动检测调用模块名
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            if module:
                # 获取完整模块路径
                module_path = module.__name__
                self.name = module_path[(module_path.find(".")):]
            else:
                self.name = name
        else:
            self.name = name
            
        self.logger = logger.opt(colors=True)

    def trace(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 TRACE 级别日志"""
        self.logger.trace(f"<b><cyan>{self.name}</cyan></b> | {msg}", *args, **kwargs)

    def debug(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 DEBUG 级别日志"""
        self.logger.debug(f"<b><cyan>{self.name}</cyan></b> | {msg}", *args, **kwargs)

    def info(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 INFO 级别日志"""
        self.logger.info(f"<b><cyan>{self.name}</cyan></b> | {msg}", *args, **kwargs)

    def success(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 SUCCESS 级别日志"""
        self.logger.success(f"<b><cyan>{self.name}</cyan></b> | {msg}", *args, **kwargs)

    def warning(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 WARNING 级别日志"""
        self.logger.warning(f"<b><cyan>{self.name}</cyan></b> | {msg}", *args, **kwargs)

    def error(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 ERROR 级别日志"""
        self.logger.error(f"<b><cyan>{self.name}</cyan></b> | {msg}", *args, **kwargs)

    def critical(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 CRITICAL 级别日志"""
        self.logger.critical(f"<b><cyan>{self.name}</cyan></b> | {msg}", *args, **kwargs)


# 导出默认日志记录器实例
log = Log()