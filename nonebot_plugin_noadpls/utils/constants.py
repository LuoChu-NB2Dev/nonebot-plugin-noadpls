from nonebot import require
require("nonebot_plugin_localstore")

import nonebot_plugin_localstore as store


class GetStorePath:
    """
    LocalStore相关常量
    
    Args:
        CONFIG_FILENAME: 可变配置文件名
        CONFIG_PATH: LocalStore提供插件配置保存路径
        CONFIG_FILE: 可变配置文件
        DATA_FILENAME: 可变数据文件名
        DATA_PATH: LocalStore提供插件数据保存路径
        DATA_FILE: 可变数据文件
        CACHE_PATH: LocalStore提供插件缓存保存路径
    """

    # Config相关路径
    CONFIG_FILENAME = "config.yml"
    "可变配置文件名"
    CONFIG_PATH = store.get_plugin_config_dir()
    "LocalStore提供插件配置保存路径"
    CONFIG_FILE = CONFIG_PATH / CONFIG_FILENAME
    "可变配置文件"

    # Data相关路径
    DATA_FILENAME = "data.yml"
    "可变数据文件名"
    DATA_PATH = store.get_plugin_data_dir()
    "LocalStore提供插件数据保存路径"
    DATA_FILE = DATA_PATH / DATA_FILENAME
    "可变数据文件"

    # Cache相关路径
    CACHE_PATH = store.get_plugin_cache_dir()
    "LocalStore提供插件缓存保存路径"

class CacheConstants:
    """
    缓存前缀
    
    
    Args:
        QQ_RAW_MESSAGE: QQ原始消息缓存前缀
        QQ_RAW_PICTURE: QQ原始图片缓存前缀
        
    """

    # 接收消息相关
    QQ_RAW_MESSAGE = "qq_raw_message_"
    "QQ原始消息缓存前缀"
    QQ_RAW_PICTURE = "qq_raw_picture_"
    "QQ原始图片缓存前缀"
    GROUP_MEMBER_LIST = "group_member_list_"
    "群成员列表缓存前缀"
    GROUP_MEMBER_LIST_TTL = 3600
    
    # OCR相关
    OCR_RESULT_TEXT = "ocr_result_text_"
    "OCR结果文字缓存前缀"
    OCR_RESULT_IMAGE = "ocr_result_image_"
    "OCR结果图片缓存前缀"
    OCR_CACHE_TTL = 86400
    "定义缓存有效期（1天）"
    
    