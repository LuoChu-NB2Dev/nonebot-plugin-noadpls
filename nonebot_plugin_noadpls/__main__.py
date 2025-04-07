from nonebot.adapters import Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP, PRIVATE
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.exception import MatcherException
from nonebot.typing import T_State
from nonebot.rule import command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText
from nonebot import on_message
import httpx
from .utils.constants import CacheConstants
from .utils.log import log
from .utils.cache import save_cache, load_cache, cache_exists
from .ocr import online_ocr, local_ocr
from .config import env_config, local_config, global_config
from .ban_judge import check_text
from .data import NoticeType, data, save_data
import time

su = global_config.superusers

# 群聊消息通用匹配
group_message_matcher = on_message(
    priority=env_config.priority,
    block=False,
    permission=GROUP
)


# 私聊消息接收通知
receive_notice_on_private = on_message(
    rule=command("接收通知"),
    priority=env_config.priority,
    block=True,
    permission=PRIVATE
)

# 私聊消息关闭通知
receive_notice_off_private = on_message(
    rule=command("关闭通知"),
    priority=env_config.priority,
    block=True,
    permission=PRIVATE
)




# # 私聊消息通用匹配
# any_other_private = on_message(
#     priority=env_config.priority + 1,
#     block=False,
#     permission= PRIVATE
# )

# @any_other_private.handle()
# async def handle_private_message(
#     bot: Bot,
# ):


@group_message_matcher.handle()
async def handle_message(
    event: GroupMessageEvent,
    state: T_State,
    # bot: Bot
):
    """处理群消息，提取文本和图片的文字
    
    Args:
        state["full_text"]: 提取出的所有文本
        state["ocr_or_text"]: "ocr" or "text" or "both"
    """
    # dict1 = await bot.get_group_info(group_id=event.group_id)
    # dict2 = await bot.get_group_member_info(group_id=event.group_id,user_id=event.user_id)
    # dict3 = await bot.get_group_member_list(group_id=event.group_id)
    # log.error(f"group_info: {dict1}")
    # log.error(f"group_member_info: {dict2}")
    # log.error(f"group_member_list: {dict3}")
    if event.post_type == "message":
        getmsg = event.message
        state["raw_message"] = getmsg
        ocr_result = ""
        raw_text = ""
        full_text = ""
        ocr_bool = False
        text_bool = False
        # log.debug(f"{getmsg}")
        for segment in getmsg:
            if segment.type == "image":

                # 获取图片标识信息
                image_name = segment.data.get("file", "")
                image_url = segment.data.get("url", "")
                if not image_name or not image_url:
                    log.error(f"无法获取图片信息: {segment}")
                    await group_message_matcher.finish()
                    return

                # 图片数据的缓存键
                image_data_cache_key = f"{CacheConstants.QQ_RAW_PICTURE}{image_name}"
                # OCR结果的缓存键
                ocr_result_cache_key = f"{CacheConstants.OCR_RESULT_TEXT}{image_name}"

                # 先检查缓存中是否有结果
                if cache_exists(ocr_result_cache_key):
                    cached_result = load_cache(ocr_result_cache_key)
                    if cached_result:
                        log.info(f"使用缓存的OCR结果: {image_name}")
                        log.debug(f"缓存的OCR结果: {cached_result}")
                        ocr_result = cached_result
                    else:
                        log.error("缓存存在但无法获取/不该出现")
                        await group_message_matcher.finish()
                        return

                # 没有缓存，进行识别
                else:
                    if cache_exists(image_data_cache_key):
                        image_data = load_cache(image_data_cache_key)
                    else:
                        async with httpx.AsyncClient() as client:
                            response = await client.get(image_url)
                            if response.status_code != 200:
                                log.error(
                                    f"获取图像失败，状态码: {response.status_code}")
                                await group_message_matcher.finish()
                                return
                            image_data = response.content
                            save_cache(image_data_cache_key, image_data)

                    try:
                        # 尝试使用在线OCR（更可靠）
                        try:
                            ocr_text = local_ocr(
                                image_data, ocr_result_cache_key)
                        except Exception as e:
                            log.warning(f"本地OCR失败: {e}，尝试在线OCR")
                            # 如果在线OCR失败，尝试本地OCR
                            ocr_text = online_ocr(
                                image_data, ocr_result_cache_key)
                    except Exception as e:
                        log.error(f"OCR识别失败: {e}")
                        await group_message_matcher.finish()
                        return
                    ocr_result = ocr_text
                if ocr_result:
                    full_text += ocr_result
                    ocr_bool = True
                    log.debug(f"OCR识别结果: {ocr_result}")

            elif segment.type == "text":
                raw_text = segment.data.get("text", "").strip()
                if raw_text:
                    full_text += raw_text
                    text_bool = True
                    log.debug(f"原始文本消息: {raw_text}")

            else:
                log.debug(f"未知消息类型: {segment}{segment.type}")
        state["full_text"] = full_text
        if ocr_bool and text_bool:
            state["ocr_or_text"] = "both"
        elif ocr_bool:
            state["ocr_or_text"] = "ocr"
        elif text_bool:
            state["ocr_or_text"] = "text"
        else:
            log.error("不存在文本或图像识别结果")
        return
    return

@group_message_matcher.handle()
async def judge_and_ban(
    event: GroupMessageEvent,
    state: T_State,
    bot: Bot
):
    """判断是否包含违禁词，若包含则禁言

    Args:
        state["ban_judge"]: 是否禁言
    """
    user_id = event.user_id
    group_id = event.group_id
    full_text = state["full_text"]
    check_list = check_text(full_text)
    state["check_list"] = check_list
    state["ban_judge"] = False
    state["ban_success"] = False
    state["revoke_success"] = False
    
    if check_list:
        state["ban_judge"] = True
        log.info(f"检测到违禁词: {check_list}")
        ban_count = data.get_ban_count(group_id, user_id)
        config_ban_list = local_config.ban_time
        ban_time = 0
        if ban_count < len(config_ban_list):
            ban_time = config_ban_list[ban_count]
            log.debug(f"ban_time:{ban_time}")
        elif ban_count >= len(config_ban_list):
            ban_time = config_ban_list[-1]
            log.debug(f"ban_time:{ban_time}")
        else:
            log.error("获取禁言时间失败(不该出现)")

        bot_is_admin = await whether_is_admin(bot, group_id, event.self_id, refresh= True)
        if bot_is_admin and str(user_id) not in su:
            try:
                await bot.set_group_ban(
                    group_id=group_id,
                    user_id=user_id,
                    duration=ban_time
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
            return
        return


@group_message_matcher.handle()
async def transmit_to_admin(
    event: GroupMessageEvent,
    state: T_State,
    bot: Bot
):
    """转发消息到管理员

    Args:
        state["ban_judge"]: 是否禁言
    """
    if state["ban_judge"]:
        group_id = event.group_id
        user_id = event.user_id
        full_text = state["full_text"]
        admin_list = data.get_notice_list(group_id,  NoticeType.BAN)
        for admin_id in admin_list:
            try:
                time_a = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event.time))
                message = f"群号: {group_id}\n用户: {user_id}\n时间: {time_a}\n原始消息：\n{state['raw_message']}\n识别整合文本: {full_text}\n触发违禁词: {state['check_list']}\n"+\
                (("\n禁言失败" if not state["ban_success"] else "")+\
                ("\n撤回失败" if not state["revoke_success"] else ""))
                await bot.send_private_msg(
                    user_id=admin_id,
                    message=message)
                log.debug(f"已转发消息到管理员: {admin_id}")
            except Exception as e:
                log.error(f"转发消息失败: {e}")
                return
    return


@receive_notice_on_private.handle()
@receive_notice_off_private.handle()
async def get_notice_group_id(
    matcher: Matcher,
    arg: Message = CommandArg()
):
    if arg.extract_plain_text():
        matcher.set_arg("groupid", arg)
    return


@receive_notice_on_private.got("groupid", prompt="请输入群号")
async def set_notice_on(
    bot: Bot,
    event: PrivateMessageEvent,
    groupid: str = ArgPlainText("groupid"),
):
    await notice_public(bot, event, groupid, True)
    return


@receive_notice_off_private.got("groupid", prompt="请输入群号")
async def set_notice_off(
    bot: Bot,
    event: PrivateMessageEvent,
    groupid: str = ArgPlainText("groupid"),
):
    await notice_public(bot, event, groupid, False)
    return


async def get_group_member_list(bot: Bot, group_id: int, refresh: bool = False) -> list:# -> Any | list[dict[str, Any]] | dict[Any, Any] | None:# -> Any | list[dict[str, Any]] | dict[Any, Any] | None:# -> Any | list[dict[str, Any]] | dict[Any, Any] | None:
    group_id_int = int(group_id)
    member_list_ttl = CacheConstants.GROUP_MEMBER_LIST_TTL

    if cache_exists(f"{CacheConstants.GROUP_MEMBER_LIST}{group_id_int}") and not refresh:
        try:
            member_list = load_cache(
                f"{CacheConstants.GROUP_MEMBER_LIST}{group_id_int}")
            if not member_list or member_list is None:
                raise ValueError("缓存数据为空")
            return member_list
        except Exception as e:
            log.warning(f"加载缓存失败: {e}")

    try:
        member_list = await bot.get_group_member_list(group_id=group_id_int)
        if not member_list or member_list is None:
            raise MatcherException("bot不在群中 get_group_member_list为空")
        save_cache(f"{CacheConstants.GROUP_MEMBER_LIST}{group_id_int}",
                    member_list, ttl=member_list_ttl)
        return member_list
    except Exception as e:
        log.error(f"获取群成员列表失败: {e}")
        return []

async def whether_is_admin(bot: Bot, group_id: int, user_id: int, refresh: bool = False) -> bool:
    """判断用户是否为群管理员

    Args:
        bot: Bot实例
        group_id: 群号
        user_id: 用户ID

    Returns:
        bool: 是否为管理员
    """
    member_list = await get_group_member_list(bot, group_id, refresh)
    for member in member_list:
        if member.get("user_id") == user_id:
            if member.get("role") == "owner" or member.get("role") == "admin":
                return True
    return False

async def notice_public(bot, event, groupid, status):
    if not groupid.isdigit():
        await receive_notice_on_private.finish("请输入有效的群号")
        return
    group_id_int = int(groupid)
    user_id = event.user_id
    
    is_admin = await whether_is_admin(bot, group_id_int, user_id)

    if not is_admin:
        await receive_notice_on_private.finish("您不是这个群的管理员哦~")
        return

    log.debug(f"用户 {user_id} 是群 {group_id_int} 的管理员")
    if status:
        data.set_notice_state(group_id_int, user_id, NoticeType.BAN, True)
        save_data()
        await receive_notice_on_private.finish(f"已开启接收群号为：\n {group_id_int} \n的禁言通知")
        log.info(f"用户 {user_id} 已开启接收 {group_id_int} 的禁言通知")
    else:
        data.set_notice_state(group_id_int, user_id, NoticeType.BAN, False)
        save_data()
        await receive_notice_on_private.finish(f"已关闭接收群号为：\n {group_id_int} \n的禁言通知")
        log.info(f"用户 {user_id} 已关闭接收 {group_id_int} 的禁言通知")
    return


# TODO: 二维码检测
