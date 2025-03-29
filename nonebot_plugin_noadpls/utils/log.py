from typing import Optional, Union, Any
import inspect
from nonebot.log import logger


class Log:
    """日志记录器"""

    def __init__(self, name: Optional[str] = None) -> None:
        """
        初始化日志记录器
        
        Args:
            name: 记录器名称，如果提供则使用固定名称，否则动态检测
        """
        self.fixed_name = name
        self.logger = logger.opt(colors=True)

    def _get_caller_module(self) -> str:
        """获取调用者的模块名称"""
        if self.fixed_name:
            return self.fixed_name

        # 跳过_get_caller_module和日志方法本身，获取实际调用者
        frame = inspect.stack()[2]
        module = inspect.getmodule(frame[0])
        if module:
            # 获取完整模块路径
            module_path = module.__name__
            return module_path[(module_path.find(".")) + 1:]
        return "unknown"

    def trace(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 TRACE 级别日志"""
        module_name = self._get_caller_module()
        self.logger.trace(
            f"<b><cyan>{module_name}</cyan></b> | {msg}", *args, **kwargs)

    def debug(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 DEBUG 级别日志"""
        module_name = self._get_caller_module()
        self.logger.debug(
            f"<b><cyan>{module_name}</cyan></b> | {msg}", *args, **kwargs)

    def info(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 INFO 级别日志"""
        module_name = self._get_caller_module()
        self.logger.info(
            f"<b><cyan>{module_name}</cyan></b> | {msg}", *args, **kwargs)

    def success(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 SUCCESS 级别日志"""
        module_name = self._get_caller_module()
        self.logger.success(
            f"<b><cyan>{module_name}</cyan></b> | {msg}", *args, **kwargs)

    def warning(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 WARNING 级别日志"""
        module_name = self._get_caller_module()
        self.logger.warning(
            f"<b><cyan>{module_name}</cyan></b> | {msg}", *args, **kwargs)

    def error(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 ERROR 级别日志"""
        module_name = self._get_caller_module()
        self.logger.error(
            f"<b><cyan>{module_name}</cyan></b> | {msg}", *args, **kwargs)

    def critical(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 CRITICAL 级别日志"""
        module_name = self._get_caller_module()
        self.logger.critical(
            f"<b><cyan>{module_name}</cyan></b> | {msg}", *args, **kwargs)


# 导出默认日志记录器实例
log = Log()