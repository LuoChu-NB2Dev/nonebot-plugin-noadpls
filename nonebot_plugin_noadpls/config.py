import yaml
from nonebot import get_driver, get_plugin_config
from pydantic import BaseModel

from .utils import GetStorePath, log


class LocalConfigModel(BaseModel):
    """localstore插件 可变动配置项"""

    # some_setting: str = "默认值"
    # enable_feature: bool = True
    ban_time: list[int] = [60, 300, 1800, 3600, 86400]
    ban_text: list[str] = []
    # ban_text_path: List[str] = []


class EnvConfigModel(BaseModel):
    """env读取 不可变动配置项"""

    enable: bool = True
    priority: int = 10
    # block: bool = False

    ban_pre_text: list[str] = ["advertisement"]


class PrefixModel(BaseModel):
    """前缀配置"""

    noadpls: EnvConfigModel


class ConfigModel(BaseModel):
    env: EnvConfigModel
    local: LocalConfigModel


def load_config() -> LocalConfigModel:
    """加载配置，分别加载环境变量配置和本地文件配置"""
    local_config_dict = {}
    default_local = LocalConfigModel()

    # 加载本地配置文件
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            try:
                local_config_dict = yaml.safe_load(f) or {}
                local_config_dict = {**default_local.model_dump(), **local_config_dict}
            except Exception as e:
                log.error(f"读取配置文件失败: {e}")
        log.debug("本地配置文件加载成功")
    else:
        # 配置文件不存在，创建默认配置
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        local_config_dict = default_local.model_dump()
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(local_config_dict, f, allow_unicode=True)
        log.info("配置文件不存在，已创建默认配置文件")

    return LocalConfigModel(**local_config_dict)


# 配置文件路径
CONFIG_PATH = GetStorePath.CONFIG_FILE

global_config = get_driver().config

env_config = get_plugin_config(PrefixModel).noadpls

local_config = load_config()


# 导出配置实例
config = ConfigModel(env=env_config, local=local_config)

# print(config.model_dump())


def save_config() -> None:
    """仅保存本地可修改的配置到本地文件"""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # # 创建一个只包含LocalConfigModel字段的字典
    # local_fields = set(LocalConfigModel().model_dump().keys())
    config_dict = config.model_dump()
    # local_config_dict = {k: v for k,
    #                      v in config_dict.items() if k in local_fields}

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config_dict, f, allow_unicode=True)


save_config()
