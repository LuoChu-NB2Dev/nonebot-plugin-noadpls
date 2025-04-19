import inspect
from typing import Any, Optional, Union

from nonebot import get_driver
from nonebot.log import logger

global_config = get_driver().config


class Log:
    """日志记录器"""

    def __init__(self, name: Optional[str] = None) -> None:
        """
        初始化日志记录器

        Args:
            name: 记录器名称，如果提供则使用固定名称，否则动态检测
        """
        self.fixed_name = name
        self.configured_log_level_name = str(global_config.log_level).upper()
        self.logger = logger.opt(colors=True)

    def _get_caller_module(self) -> str:
        """获取调用者的模块名称"""
        if self.fixed_name:
            return self.fixed_name

        # 跳过 _get_caller_module, _log 和日志方法本身，获取实际调用者 (stack level 3)
        frame = inspect.stack()[3]
        module = inspect.getmodule(frame[0])
        if module:
            # 获取完整模块路径
            module_path = module.__name__
            # 尝试去除包前缀，如果存在的话
            try:
                return module_path[(module_path.index(".")) + 1 :]
            except ValueError:
                return module_path  # 如果没有点，返回完整路径
        return "unknown"

    def _get_caller_function(self) -> str:
        """获取调用者的函数名称"""
        # 注意：此方法不应在 fixed_name 设置时被调用
        # 跳过 _get_caller_function, _log 和日志方法本身，获取实际调用者 (stack level 3)
        frame = inspect.stack()[3]
        function = frame.function
        return function

    def _wheter_need_function(self) -> bool:
        """判断是否应在日志中显示函数名 (基于全局配置的日志级别)"""
        if self.fixed_name:  # 如果名称是固定的，则不显示动态函数名
            return False
        # 检查配置的日志级别是否为 TRACE 或 DEBUG
        # Loguru 级别: TRACE=5, DEBUG=10, INFO=20 ...
        try:
            level_no = logger.level(self.configured_log_level_name).no
            # 仅当全局配置级别 <= DEBUG 时显示函数名
            return level_no <= logger.level("DEBUG").no
        except ValueError:
            # 处理无效的日志级别名称
            return False  # 默认为不显示

    def _log(self, level: str, msg: Union[str, Any], *args, **kwargs) -> None:
        """内部日志记录方法，处理格式化和调用实际 logger"""
        module_name = self._get_caller_module()
        log_method = getattr(self.logger, level)

        if self._wheter_need_function():
            function_name = self._get_caller_function()
            # 如果函数名是 '<module>' (表示在模块级别调用)，则转义尖括号以防止 Loguru 解析错误
            if function_name == "<module>":
                function_part = r"<b><red>\<module></red></b>"  # 使用转义后的字符串
            else:
                function_part = f"<b><red>{function_name}</red></b>"  # 正常添加颜色标签
            final_msg = f"<b><cyan>{module_name}</cyan></b> | {function_part} | {msg}"
        else:
            final_msg = f"<b><cyan>{module_name}</cyan></b> | {msg}"

        log_method(final_msg, *args, **kwargs)

    def trace(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 TRACE 级别日志"""
        self._log("trace", msg, *args, **kwargs)

    def debug(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 DEBUG 级别日志"""
        self._log("debug", msg, *args, **kwargs)

    def info(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 INFO 级别日志"""
        self._log("info", msg, *args, **kwargs)

    def success(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 SUCCESS 级别日志"""
        self._log("success", msg, *args, **kwargs)

    def warning(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 WARNING 级别日志"""
        self._log("warning", msg, *args, **kwargs)

    def error(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 ERROR 级别日志"""
        self._log("error", msg, *args, **kwargs)

    def critical(self, msg: Union[str, Any], *args, **kwargs) -> None:
        """记录 CRITICAL 级别日志"""
        self._log("critical", msg, *args, **kwargs)


# 导出默认日志记录器实例
log = Log()
