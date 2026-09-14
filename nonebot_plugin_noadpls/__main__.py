"""Main entry point - registers matchers and connects handlers."""
from nonebot import on_message
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP, PRIVATE
from nonebot.params import ArgPlainText, CommandArg
from nonebot.rule import Rule, command

from .config import env_config
from .data import data
from .handlers import (
    get_group_detect_group_id,
    get_notice_group_id,
    judge_and_ban,
    notice_to_member,
    set_group_detect_off,
    set_group_detect_on,
    set_notice_off,
    set_notice_on,
    transmit_to_admin,
)
from .handlers.message_handler import handle_message


def group_detection_enabled() -> Rule:
    """
    自定义规则：检查群组是否启用了检测功能
    只有启用检测的群组消息才会被处理
    """

    async def _group_detection_enabled(event: Event) -> bool:
        if isinstance(event, GroupMessageEvent):
            return data.get_group_enable_state(event.group_id)
        return True  # 非群组消息默认通过

    return Rule(_group_detection_enabled)


# 群聊消息通用匹配 - 使用自定义规则检查群组检测状态
group_message_matcher = on_message(
    rule=group_detection_enabled(),
    priority=env_config.priority,
    block=False,
    permission=GROUP,
)

# 私聊消息接收通知
receive_notice_on_private = on_message(
    rule=command("接收通知"),
    priority=env_config.priority,
    block=True,
    permission=PRIVATE,
)

# 私聊消息关闭通知
receive_notice_off_private = on_message(
    rule=command("关闭通知"),
    priority=env_config.priority,
    block=True,
    permission=PRIVATE,
)

group_detect_turn_on = on_message(
    rule=command("nap_on"),
    priority=env_config.priority,
    block=True,
    permission=GROUP | PRIVATE,
)

group_detect_turn_off = on_message(
    rule=command("nap_off"),
    priority=env_config.priority,
    block=True,
    permission=GROUP | PRIVATE,
)


# Register handlers for group message matcher
@group_message_matcher.handle()
async def _handle_message(event: GroupMessageEvent, state):
    """处理群消息，提取文本和图片的文字"""
    await handle_message(event, state, group_message_matcher)


@group_message_matcher.handle()
async def _judge_and_ban(event: GroupMessageEvent, state, bot):
    """判断是否包含违禁词，若包含则禁言"""
    await judge_and_ban(event, state, bot)


@group_message_matcher.handle()
async def _transmit_to_admin(event: GroupMessageEvent, state, bot):
    """转发消息到管理员"""
    await transmit_to_admin(event, state, bot)


@group_message_matcher.handle()
async def _notice_to_member(event: GroupMessageEvent, state, bot):
    """通知被禁言的成员"""
    await notice_to_member(event, state, bot, group_message_matcher)


# Register handlers for notice commands
@receive_notice_on_private.handle()
@receive_notice_off_private.handle()
async def _get_notice_group_id(matcher, arg=CommandArg()):
    """获取通知命令的群号"""
    await get_notice_group_id(matcher, arg)


@receive_notice_on_private.got("groupid", prompt="请输入群号")
async def _set_notice_on(bot, event, groupid: str = ArgPlainText("groupid")):
    """开启接收禁言通知"""
    await set_notice_on(bot, event, groupid, receive_notice_on_private)


@receive_notice_off_private.got("groupid", prompt="请输入群号")
async def _set_notice_off(bot, event, groupid: str = ArgPlainText("groupid")):
    """关闭接收禁言通知"""
    await set_notice_off(bot, event, groupid, receive_notice_off_private)


# Register handlers for group detect commands
@group_detect_turn_on.handle()
@group_detect_turn_off.handle()
async def _get_group_detect_group_id(bot, event, matcher, arg=CommandArg()):
    """获取群检测命令的群号"""
    await get_group_detect_group_id(bot, event, matcher, arg, group_detect_turn_on)


@group_detect_turn_on.got("groupid", prompt="请输入群号")
async def _set_group_detect_on(bot, event, groupid: str = ArgPlainText("groupid")):
    """开启群检测"""
    await set_group_detect_on(bot, event, groupid, group_detect_turn_on)


@group_detect_turn_off.got("groupid", prompt="请输入群号")
async def _set_group_detect_off(bot, event, groupid: str = ArgPlainText("groupid")):
    """关闭群检测"""
    await set_group_detect_off(bot, event, groupid, group_detect_turn_off)


# TODO: 二维码检测
