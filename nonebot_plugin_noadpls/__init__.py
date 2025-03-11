# ruff: noqa: E402

from nonebot.plugin import PluginMetadata, inherit_supported_adapters, require

require("nonebot_plugin_alconna")

from . import __main__ as __main__
from .config import ConfigModel
from ._version import __version__ as __version__

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-noadpls",
    description="插件模板",
    usage="这是一个一个一个插件模板",
    type="application",
    homepage="https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls",
    config=ConfigModel,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={"License": "MIT", "Author": "gongfuture"},
)
