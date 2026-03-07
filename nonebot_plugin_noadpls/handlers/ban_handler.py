"""Ban handler - detects violations and executes bans."""
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.typing import T_State

from ..config import local_config
from ..data import data, save_data
from ..detectors import check_text
from ..utils.log import log
from .utils import whether_is_admin


async def judge_and_ban(event: GroupMessageEvent, state: T_State, bot: Bot):
    """判断是否包含违禁词，若包含则禁言

    Args:
        event: 群消息事件
        state: 状态字典
        bot: Bot实例

    State keys used:
        state["full_text"]: 要检查的文本

    State keys set:
        state["ban_judge"]: 是否禁言
        state["ban_success"]: 禁言是否成功
        state["revoke_success"]: 撤回是否成功
        state["unban_reason"]: 未禁言原因列表
        state["check_list"]: 检测到的违禁词列表
    """
    # 初始化变量
    user_id = event.user_id
    group_id = event.group_id
    full_text = state["full_text"]
    state["ban_judge"] = False
    state["ban_success"] = False
    state["revoke_success"] = False
    state["unban_reason"] = []

    # 调用check_text函数检查文本
    check_list = check_text(full_text)
    state["check_list"] = check_list

    # 存在违禁词
    if check_list:
        # ban_judge状态为True
        state["ban_judge"] = True
        log.info(f"检测到违禁词: {check_list}")
        # 获取用户该群被禁次数
        ban_count = data.get_ban_count(group_id, user_id)
        # 获取定义的禁言时间列表
        config_ban_list = local_config.ban_time
        ban_time = 0
        # 赋予禁言时间
        if ban_count < len(config_ban_list):
            ban_time = config_ban_list[ban_count]
            log.debug(f"ban_time:{ban_time}")
        elif ban_count >= len(config_ban_list):
            ban_time = config_ban_list[-1]
            log.debug(f"ban_time:{ban_time}")
        else:
            log.error("获取禁言时间失败(不该出现)")
        # 判断bot是否为管理员
        bot_is_admin = await whether_is_admin(bot, group_id, event.self_id)
        user_is_admin = await whether_is_admin(bot, group_id, user_id)
        if not bot_is_admin:
            bot_is_admin = await whether_is_admin(
                bot, group_id, event.self_id, refresh=True
            )
        # bot有权限且用户不是管理员（管理员包括群管理员、群主和超级用户）
        if bot_is_admin and not user_is_admin:
            try:
                await bot.set_group_ban(
                    group_id=group_id, user_id=user_id, duration=ban_time
                )
                state["ban_success"] = True
            except Exception as e:
                log.error(f"禁言失败: {e}")
                state["ban_success"] = False
            data.increase_ban_count(group_id, user_id)
            try:
                await bot.delete_msg(message_id=event.message_id)
                state["revoke_success"] = True
            except ActionFailed as e:
                log.error(f"删除消息失败: {e}")
                state["revoke_success"] = False
            save_data()

            log.info(f"已禁言用户: {user_id}")
        else:
            log.error(f"bot没有权限，无法禁言用户: {user_id}")
            if not bot_is_admin:
                state["unban_reason"] += ["bot没有权限 "]
            if user_is_admin:
                state["unban_reason"] += ["用户是管理员 "]
            return
        return
