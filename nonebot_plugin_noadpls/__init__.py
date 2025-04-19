# ruff: noqa: E402

from nonebot.plugin import PluginMetadata

from . import __main__ as __main__
from .config import PrefixModel

__plugin_meta__ = PluginMetadata(
    name="群聊广告哒咩",
    description="检测群聊中广告的插件，撤回并禁言，转发管理员",
    usage="",
    type="application",
    homepage="https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls",
    config=PrefixModel,
    supported_adapters={"~onebot.v11"},
    extra={"License": "MIT", "Author": "gongfuture"},
)
