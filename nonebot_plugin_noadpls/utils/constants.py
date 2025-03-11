from nonebot import require
require("nonebot_plugin_localstore")

import nonebot_plugin_localstore as store
from ..__init__ import __plugin_meta__

# 从__init__获取插件名称
PLUGIN_NAME = __plugin_meta__.name
"init获取的插件名称"

class StorePath:
    """LocalStore相关常量"""

    # Config相关路径
    CONFIG_FILENAME = "config.yml"
    "可变配置文件名"
    CONFIG_PATH = store.get_plugin_config_dir()
    "LocalStore提供插件配置保存路径"
    CONFIG_FILE = CONFIG_PATH / CONFIG_FILENAME
    "可变配置文件"

    # Data相关路径
    DATA_PATH = store.get_plugin_data_dir()
    "LocalStore提供插件数据保存路径"

    # Cache相关路径
    CACHE_PATH = store.get_plugin_cache_dir()
    "LocalStore提供插件缓存保存路径"