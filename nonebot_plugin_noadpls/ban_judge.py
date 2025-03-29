from typing import Optional, List
from cleanse_speech import DLFA, SpamShelf
from .config import config, save_config
from .utils.log import log

pre_text_list = []

config_pre_text_list = config.env.ban_pre_text
config_ban_text_list = config.local.ban_text

SPAM_LIBRARIES = {
    "advertisement": SpamShelf.CN.ADVERTISEMENT,
    "pornographic": SpamShelf.CN.PORNOGRAPHIC,
    "politics": SpamShelf.CN.POLITICS,
    "general": SpamShelf.CN.GENERAL,
    "netease": SpamShelf.CN.NETEASE
}

for pre_text in config_pre_text_list:
    pre_text = pre_text.lower()  # 转小写，便于匹配
    if pre_text in SPAM_LIBRARIES:
        pre_text_list.append(SPAM_LIBRARIES[pre_text])
        log.info(f"已加载词库: {pre_text}")
    else:
        log.warning(f"未知词库: {pre_text}")

if not pre_text_list:
    pre_text_list = [SpamShelf.CN.ADVERTISEMENT]
    log.info("使用默认词库: advertisement")

dfa = DLFA(words_resource=[*pre_text_list])


def check_text(text: str) -> list:
    """检查文本是否包含违禁词

    Args:
        text: 需要检查的文本

    Returns:
        违禁词列表，如果没有则为空列表
    """
    return dfa.extract_illegal_words(text)


def update_words(
    new_words: Optional[List[str]] = None,
    add_words: Optional[List[str]] = None,
    remove_words: Optional[List[str]] = None,
    reload_library: bool = False) -> bool:
    """更新违禁词列表

    Args:
        new_words: 完全替换现有自定义违禁词
        add_words: 添加新的违禁词
        remove_words: 删除指定违禁词
        reload_library: 是否重新加载预定义词库

    Returns:
        是否成功更新
    """
    global dfa, config_ban_text_list, pre_text_list

    try:
        # 更新自定义违禁词列表
        if new_words:
            # 完全替换现有自定义违禁词
            config.local.ban_text = new_words
            config_ban_text_list = new_words
            log.info(f"已替换自定义违禁词列表，共 {len(new_words)} 个词")

        if add_words:
            # 添加新的违禁词（去重）
            current_words = set(config.local.ban_text)
            added = 0
            for word in add_words:
                if word and word not in current_words:
                    current_words.add(word)
                    added += 1

            config.local.ban_text = list(current_words)
            config_ban_text_list = config.local.ban_text
            log.info(f"已添加 {added} 个新违禁词，当前共 {len(current_words)} 个词")

        if remove_words:
            # 删除指定违禁词
            current_words = set(config.local.ban_text)
            removed = 0
            for word in remove_words:
                if word in current_words:
                    current_words.remove(word)
                    removed += 1

            config.local.ban_text = list(current_words)
            config_ban_text_list = config.local.ban_text
            log.info(f"已删除 {removed} 个违禁词，当前共 {len(current_words)} 个词")

        # 重新加载预定义词库
        if reload_library:
            pre_text_list = []
            for pretext in config.env.ban_pre_text:
                pretext = pretext.lower()
                if pretext in SPAM_LIBRARIES:
                    pre_text_list.append(SPAM_LIBRARIES[pretext])
                    log.info(f"已重新加载词库: {pretext}")
                else:
                    log.warning(f"未知词库: {pretext}")

            if not pre_text_list:
                pre_text_list = [SpamShelf.CN.ADVERTISEMENT]
                log.info("使用默认词库: advertisement")

        # 重建DFA检测器
        dfa = DLFA(words_resource=[
            *pre_text_list,  # 预定义词库
            config_ban_text_list  # 自定义违禁词
        ])

        # 保存配置到文件
        save_config()

        log.info("违禁词更新完成")
        return True

    except Exception as e:
        log.error(f"更新违禁词失败: {e}")
        return False
