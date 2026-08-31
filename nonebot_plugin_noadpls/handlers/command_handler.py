"""Command handlers - handle all command-based interactions."""
from typing import Union

from nonebot.adapters import Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, PrivateMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText

from ..data import NoticeType, data, save_data
from ..utils.log import log
from .utils import whether_is_admin


async def get_notice_group_id(matcher: Matcher, arg: Message):
    """获取通知相关命令的群号参数

    Args:
        matcher: 消息匹配器
        arg: 命令参数
    """
    if arg.extract_plain_text():
        matcher.set_arg("groupid", arg)
    return


async def set_notice_on(
    bot: Bot,
    event: PrivateMessageEvent,
    groupid: str,
    matcher,
):
    """开启接收禁言通知

    Args:
        bot: Bot实例
        event: 私聊消息事件
        groupid: 群号（字符串）
        matcher: 消息匹配器
    """
    await notice_public(bot, event, groupid, True, matcher)
    return


async def set_notice_off(
    bot: Bot,
    event: PrivateMessageEvent,
    groupid: str,
    matcher,
):
    """关闭接收禁言通知

    Args:
        bot: Bot实例
        event: 私聊消息事件
        groupid: 群号（字符串）
        matcher: 消息匹配器
    """
    await notice_public(bot, event, groupid, False, matcher)
    return


async def notice_public(
    bot: Bot, event: PrivateMessageEvent, groupid: str, status: bool, matcher
) -> None:
    """群通知开关公共处理函数

    Args:
        bot: Bot实例
        event: 私聊消息事件
        groupid: 群号（字符串）
        status: 开启或关闭
        matcher: 消息匹配器
    """
    if not groupid.isdigit():
        await matcher.finish("请输入有效的群号")
        return
    group_id_int = int(groupid)
    user_id = event.user_id

    is_admin = await whether_is_admin(bot, group_id_int, user_id)

    if not is_admin:
        await matcher.finish()
        return

    log.debug(f"用户 {user_id} 是群 {group_id_int} 的管理员")
    if status:
        data.set_notice_state(group_id_int, user_id, NoticeType.BAN, True)
        save_data()
        await matcher.send(f"已开启接收群号为：\n {group_id_int} \n的禁言通知")
        log.info(f"用户 {user_id} 已开启接收 {group_id_int} 的禁言通知")
        await matcher.finish()
    else:
        data.set_notice_state(group_id_int, user_id, NoticeType.BAN, False)
        save_data()
        await matcher.send(f"已关闭接收群号为：\n {group_id_int} \n的禁言通知")
        log.info(f"用户 {user_id} 已关闭接收 {group_id_int} 的禁言通知")
        await matcher.finish()
    return


async def get_group_detect_group_id(
    bot: Bot,
    event: Union[PrivateMessageEvent, GroupMessageEvent],
    matcher: Matcher,
    arg: Message,
    turn_on_matcher,
):
    """获取群检测命令的群号参数

    Args:
        bot: Bot实例
        event: 消息事件
        matcher: 当前消息匹配器
        arg: 命令参数
        turn_on_matcher: 开启检测的匹配器（用于判断是开启还是关闭）
    """
    # 如果是群消息且没有提供参数，直接使用当前群
    if isinstance(event, GroupMessageEvent) and not arg.extract_plain_text():
        status = matcher == turn_on_matcher
        await group_detect_public(bot, event, str(event.group_id), status, matcher)
        return

    # 如果提供了参数，设置参数
    if arg.extract_plain_text():
        matcher.set_arg("groupid", arg)
    return


async def set_group_detect_on(
    bot: Bot,
    event: Union[PrivateMessageEvent, GroupMessageEvent],
    groupid: str,
    matcher,
):
    """开启群检测功能

    Args:
        bot: Bot实例
        event: 消息事件
        groupid: 群号（字符串）
        matcher: 消息匹配器
    """
    await group_detect_public(bot, event, groupid, True, matcher)
    return


async def set_group_detect_off(
    bot: Bot,
    event: Union[PrivateMessageEvent, GroupMessageEvent],
    groupid: str,
    matcher,
):
    """关闭群检测功能

    Args:
        bot: Bot实例
        event: 消息事件
        groupid: 群号（字符串）
        matcher: 消息匹配器
    """
    await group_detect_public(bot, event, groupid, False, matcher)
    return


async def group_detect_public(
    bot: Bot,
    event: Union[PrivateMessageEvent, GroupMessageEvent],
    groupid: str,
    status: bool,
    matcher,
) -> None:
    """群检测开关公共处理函数

    Args:
        bot: Bot实例
        event: 消息事件
        groupid: 群号（字符串）
        status: 开启或关闭
        matcher: 消息匹配器
    """
    # 如果是群消息且没有提供群号，使用当前群号
    if isinstance(event, GroupMessageEvent) and not groupid:
        group_id_int = event.group_id
        user_id = event.user_id
    else:
        # 私聊消息或提供了群号
        if not groupid.isdigit():
            await matcher.finish("请输入有效的群号")
            return
        group_id_int = int(groupid)
        user_id = event.user_id

    # 验证用户是否为该群管理员
    is_admin = await whether_is_admin(bot, group_id_int, user_id)

    if not is_admin:
        await matcher.finish()
        return

    log.debug(f"用户 {user_id} 是群 {group_id_int} 的管理员")

    # 设置群检测状态
    if status:
        data.set_group_enable_state(group_id_int, True)
        save_data()
        success_msg = f"已开启群号为：\n {group_id_int} \n的群检测功能"
        log.info(f"用户 {user_id} 已开启 {group_id_int} 的群检测功能")
    else:
        data.set_group_enable_state(group_id_int, False)
        save_data()
        success_msg = f"已关闭群号为：\n {group_id_int} \n的群检测功能"
        log.info(f"用户 {user_id} 已关闭 {group_id_int} 的群检测功能")

    await matcher.send(success_msg)
    await matcher.finish()
    return
