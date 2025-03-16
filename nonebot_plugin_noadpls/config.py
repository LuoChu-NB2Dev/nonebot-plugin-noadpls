import yaml
from typing import Optional, List
from nonebot import get_plugin_config, get_driver
from pydantic import BaseModel

from .utils import log, GetStorePath

class LocalConfigModel(BaseModel):
    """localstore插件 可变动配置项"""
    # some_setting: str = "默认值"
    # enable_feature: bool = True
    ban_time: List[int] = [60, 300, 1800, 3600, 86400]


class EnvConfigModel(BaseModel):
    """env读取 不可变动配置项"""


class PrefixModel(BaseModel):
    """前缀配置"""
    noadpls: Optional[EnvConfigModel] = None


class ConfigModel(BaseModel):
    """配置合并"""


# 获取.env插件配置
env_config = get_plugin_config(PrefixModel)

global_config = get_driver().config

# 配置文件路径
CONFIG_PATH = GetStorePath.CONFIG_FILE


def load_config() -> ConfigModel:
    """加载配置，分别加载环境变量配置和本地文件配置"""
    local_config_dict = {}

    # 加载本地配置文件
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            try:
                local_config_dict = yaml.safe_load(f) or {}
            except Exception as e:
                log.error(f"读取配置文件失败: {e}")
        log.debug("本地配置文件加载成功")
    else:
        # 配置文件不存在，创建默认配置
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        default_local = LocalConfigModel()
        local_config_dict = default_local.model_dump()
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(local_config_dict, f, allow_unicode=True)
        log.info("配置文件不存在，已创建默认配置文件")

    # 合并两种配置
    merged_config = {
        **env_config.model_dump(),  # 环境变量配置
        **local_config_dict         # 本地文件配置
    }

    return ConfigModel(**merged_config)


# 导出配置实例
config = load_config()


def save_config() -> None:
    """仅保存本地可修改的配置到本地文件"""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 创建一个只包含LocalConfigModel字段的字典
    local_fields = set(LocalConfigModel().model_dump().keys())
    config_dict = config.model_dump()
    local_config_dict = {k: v for k,
                         v in config_dict.items() if k in local_fields}

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(local_config_dict, f, allow_unicode=True)
