from .log import Log, log
from .constants import  GetStorePath, CacheConstants

# 导出所有公共接口
__all__ = ["Log", "log", 
           "GetStorePath","CacheConstants"
           ]


# Original by https://github.com/yzyyz1387/nonebot_plugin_admin/blob/main/nonebot_plugin_admin/utils.py


from nonebot.adapters.onebot.v11 import GroupMessageEvent, ActionFailed, Bot
from nonebot.matcher import Matcher
from typing import Union, Optional
from ..config import  global_config, config

su = global_config.superusers

async def mute_sb(bot: Bot, gid: int, lst: list, time: Optional[int] = None, scope: Optional[list] = None):
    """
    构造禁言
    :param gid: 群号
    :param time: 时间（s)
    :param lst: at列表
    :param scope: 用于被动检测禁言的时间范围
    :return:禁言操作
    """
    if 'all' in lst:
        yield bot.set_group_whole_ban(group_id=gid, enable=True)
    else:
        if time is None:
            if scope is None:
                time = random.randint(config.ban_rand_time_min, plugin_config.ban_rand_time_max)
            else:
                time = random.randint(scope[0], scope[1])
        for qq in lst:
            if int(qq) in su or str(qq) in su:
                log.info(f"SUPERUSER无法被禁言, {qq}")
            else:
                yield bot.set_group_ban(group_id=gid, user_id=qq, duration=time)