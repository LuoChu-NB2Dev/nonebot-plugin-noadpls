# ruff: noqa: E402

from nonebot.plugin import PluginMetadata, inherit_supported_adapters

from . import __main__ as __main__
from .config import ConfigModel

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-noadpls",
    description="群广告检测",
    usage="检测群聊中广告的插件，撤回并禁言，转发管理员",
    type="application",
    homepage="https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls",
    config=ConfigModel,
    supported_adapters={"~onebot.v11"},
    extra={"License": "MIT", "Author": "gongfuture"},
)
