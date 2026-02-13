"""Admin handler - sends notifications and messages to admins and members."""
import time

from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.typing import T_State

from ..data import NoticeType, data
from ..utils.log import log


async def transmit_to_admin(event: GroupMessageEvent, state: T_State, bot: Bot):
    """转发消息到管理员

    Args:
        event: 群消息事件
        state: 状态字典
        bot: Bot实例

    State keys used:
        state["ban_judge"]: 是否触发了禁言
        state["full_text"]: 检测的文本
        state["raw_message"]: 原始消息
        state["ocr_or_text"]: 消息类型
        state["check_list"]: 触发的违禁词列表
        state["ban_success"]: 禁言是否成功
        state["revoke_success"]: 撤回是否成功
        state["unban_reason"]: 未禁言原因
    """
    if state["ban_judge"]:
        group_id = event.group_id
        user_id = event.user_id
        full_text = state["full_text"]
        admin_list = data.get_notice_list(group_id, NoticeType.BAN)
        for admin_id in admin_list:
            try:
                time_a = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(event.time))
                message = (
                    f"群号:  {group_id}\n"
                    f"用户:  {user_id}\n"
                    f"时间:  {time_a}\n"
                    f"消息类型:  {'文本' if state['ocr_or_text'] == 'text' else '图片' if state['ocr_or_text'] == 'ocr' else '文本+图片'}\n"
                    f"原始消息：\n{state['raw_message']}\n"
                    f"识别整合文本:  {full_text}\n"
                    f"触发违禁词:  {state['check_list']}\n"
                )
                # 添加失败信息(如果有)
                if not state["ban_success"] or not state["revoke_success"]:
                    if not state["ban_success"]:
                        message += "\n禁言失败"
                    if not state["revoke_success"]:
                        message += "\n撤回失败"
                    if state["unban_reason"]:
                        message += f"\n失败原因:  {state['unban_reason']}"

                await bot.send_private_msg(user_id=admin_id, message=message)
                log.debug(f"已转发消息到管理员: {admin_id}")
            except Exception as e:
                log.error(f"转发消息失败: {e}")
                return
    return


async def notice_to_member(event: GroupMessageEvent, state: T_State, bot: Bot, matcher):
    """通知被禁言的成员

    Args:
        event: 群消息事件
        state: 状态字典
        bot: Bot实例
        matcher: 消息匹配器

    State keys used:
        state["ban_judge"]: 是否触发了禁言
        state["ban_success"]: 禁言是否成功
        state["revoke_success"]: 撤回是否成功
    """
    if state["ban_judge"]:
        message = "\n你发送的消息中包含管理员不允许发送的违禁词哦~"
        if state["ban_success"] and state["revoke_success"]:
            message += "\n你已被禁言并且撤回该消息\n申诉或对线请与接收通知的管理联系~"
        await bot.send(event=event, at_sender=True, message=message)
    await matcher.finish()
    return
