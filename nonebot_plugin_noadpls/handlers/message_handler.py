"""Message handler - extracts text from messages and performs OCR."""
import httpx
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.typing import T_State

from ..ocr import local_ocr, online_ocr
from ..utils.cache import cache_exists, load_cache, save_cache
from ..utils.constants import PrefixConstants
from ..utils.log import log


async def handle_message(
    event: GroupMessageEvent,
    state: T_State,
    matcher,
):
    """处理群消息，提取文本和图片的文字

    Args:
        event: 群消息事件
        state: 状态字典，用于存储处理结果
        matcher: 消息匹配器

    State keys set:
        state["full_text"]: 提取出的所有文本
        state["ocr_or_text"]: "ocr" or "text" or "both"
        state["raw_message"]: 原始消息
    """
    # 匹配message事件
    if event.post_type == "message":
        getmsg = event.message
        # 将原始消息存储到状态中
        state["raw_message"] = getmsg
        # 初始化变量
        ocr_result = ""
        raw_text = ""
        full_text = ""
        ocr_bool = False
        text_bool = False

        for segment in getmsg:
            # 图片处理
            if segment.type == "image":
                # 获取图片标识信息
                image_name = segment.data.get("file", "")
                image_url = segment.data.get("url", "")
                if not image_name or not image_url:
                    log.error(f"无法获取图片信息: {segment}")
                    await matcher.finish()
                    return

                # 图片数据的缓存键
                image_data_cache_key = f"{PrefixConstants.QQ_RAW_PICTURE}{image_name}"
                # OCR结果的缓存键
                ocr_result_cache_key = f"{PrefixConstants.OCR_RESULT_TEXT}{image_name}"

                # 先检查缓存中是否有结果
                if cache_exists(ocr_result_cache_key):
                    cached_result = load_cache(ocr_result_cache_key)
                    if cached_result:
                        log.info(f"使用缓存的OCR结果: {image_name}")
                        log.debug(f"缓存的OCR结果: {cached_result}")
                        # 直接使用缓存的结果
                        ocr_result = cached_result
                    else:
                        log.error("缓存存在但无法获取/不该出现")
                        await matcher.finish()
                        return

                # 没有缓存，进行识别
                else:
                    if cache_exists(image_data_cache_key):
                        image_data = load_cache(image_data_cache_key)
                    else:
                        async with httpx.AsyncClient(timeout=30.0) as client:
                            response = await client.get(image_url)
                            if response.status_code != 200:
                                log.error(
                                    f"获取图像失败，状态码: {response.status_code}"
                                )
                                await matcher.finish()
                                return
                            image_data = response.content
                            save_cache(image_data_cache_key, image_data)

                    try:
                        # 尝试使用本地OCR
                        try:
                            ocr_text = local_ocr(image_data, ocr_result_cache_key)
                        except Exception as e:
                            log.warning(f"本地OCR失败: {e}，尝试在线OCR")
                            # 如果本地OCR失败，尝试在线OCR
                            ocr_text = online_ocr(image_data, ocr_result_cache_key)
                    except Exception as e:
                        log.error(f"OCR识别失败: {e}")
                        await matcher.finish()
                        return
                    ocr_result = ocr_text
                if ocr_result:
                    # 如果识别结果不为空，添加到文本中
                    full_text += ocr_result
                    ocr_bool = True
                    log.debug(f"OCR识别结果: {ocr_result}")

            # 文本处理
            elif segment.type == "text":
                raw_text = segment.data.get("text", "").strip()
                # 如果文本不为空，添加到文本中
                if raw_text:
                    full_text += raw_text
                    text_bool = True
                    log.debug(f"原始文本消息: {raw_text}")

            else:
                log.debug(f"未知消息类型: {segment}{segment.type}")

        # 将提取的文本和图片识别结果存储到状态中
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
