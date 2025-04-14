import yaml
from nonebot import get_driver, get_plugin_config
from pydantic import BaseModel

from .utils import StoragePathConstants, log


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

    noadpls: EnvConfigModel = EnvConfigModel()


class ConfigModel(BaseModel):
    env: EnvConfigModel
    local: LocalConfigModel


def load_config() -> LocalConfigModel:
    """加载本地文件配置"""
    local_config_dict = {}
    default_local = LocalConfigModel()

    # 加载本地配置文件
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            try:
                loaded_data = yaml.safe_load(f) or {}
                # 仅加载 LocalConfigModel 中定义的字段
                local_config_dict = {
                    k: loaded_data[k]
                    for k in default_local.model_dump().keys()
                    if k in loaded_data
                }
                # 对于缺失的字段，使用默认值填充
                local_config_dict = {**default_local.model_dump(), **local_config_dict}
                log.debug("本地配置文件加载成功")
            except Exception as e:
                log.error(f"读取配置文件失败: {e}, 将使用默认本地配置")
                local_config_dict = default_local.model_dump()
        # print(local_config_dict) # 用于调试，可以注释掉
    else:
        # 配置文件不存在，创建默认配置
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        local_config_dict = default_local.model_dump()
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(local_config_dict, f, allow_unicode=True)
        log.info("配置文件不存在，已创建默认配置文件")

    return LocalConfigModel(**local_config_dict)


# 配置文件路径
CONFIG_PATH = StoragePathConstants.CONFIG_FILE

global_config = get_driver().config

env_config = get_plugin_config(PrefixModel).noadpls

# 从 yml 文件加载 local 配置
local_config = load_config()


# 导出合并后的配置实例
config = ConfigModel(env=env_config, local=local_config)

# print(config.model_dump()) # 用于调试，可以注释掉


def save_config() -> None:
    """仅保存本地可修改的配置 (local 部分) 到本地文件"""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 获取 local 配置部分的字典
    local_config_to_save = config.local.model_dump()

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(local_config_to_save, f, allow_unicode=True)
    log.debug("本地配置已保存到文件")


# save_config() # 可以在需要时调用以保存当前 local 配置
