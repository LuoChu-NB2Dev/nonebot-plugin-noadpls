"""Utility functions for handlers."""
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.exception import MatcherException

from ..config import global_config
from ..utils.cache import cache_exists, load_cache, save_cache
from ..utils.constants import PrefixConstants
from ..utils.log import log

su = global_config.superusers


async def get_group_member_list(bot: Bot, group_id: int, refresh: bool = False) -> list:
    """获取群成员列表，支持缓存

    Args:
        bot: Bot实例
        group_id: 群ID
        refresh: 是否刷新缓存

    Returns:
        群成员列表
    """
    group_id_int = int(group_id)
    member_list_ttl = PrefixConstants.GROUP_MEMBER_LIST_TTL

    if (
        cache_exists(f"{PrefixConstants.GROUP_MEMBER_LIST}{group_id_int}")
        and not refresh
    ):
        try:
            member_list = load_cache(
                f"{PrefixConstants.GROUP_MEMBER_LIST}{group_id_int}"
            )
            if not member_list or member_list is None:
                raise ValueError("缓存数据为空")
            return member_list
        except Exception as e:
            log.warning(f"加载缓存失败: {e}")

    try:
        member_list = await bot.get_group_member_list(group_id=group_id_int)
        if not member_list or member_list is None:
            raise MatcherException("bot不在群中 get_group_member_list为空")
        save_cache(
            f"{PrefixConstants.GROUP_MEMBER_LIST}{group_id_int}",
            member_list,
            ttl=member_list_ttl,
        )
        return member_list
    except Exception as e:
        log.error(f"获取群成员列表失败: {e}")
        return []


async def whether_is_admin(
    bot: Bot, group_id: int, user_id: int, refresh: bool = False
) -> bool:
    """判断用户是否为群管理员

    Args:
        bot: Bot实例
        group_id: 群号
        user_id: 用户ID
        refresh: 是否刷新缓存

    Returns:
        bool: 是否为管理员
    """
    # 超级用户拥有所有权限
    if str(user_id) in su:
        return True
    member_list = await get_group_member_list(bot, group_id, refresh)
    for member in member_list:
        if member.get("user_id") == user_id:
            if member.get("role") == "owner" or member.get("role") == "admin":
                return True
    return False
