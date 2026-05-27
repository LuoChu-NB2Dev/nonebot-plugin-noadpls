"""Word list manager - handles updates to ban word lists."""
from typing import Optional

from cleanse_speech import DLFA, SpamShelf

from ..config import config, save_config
from ..utils.constants import PrefixConstants
from ..utils.log import log
from . import text_detector

# 定义正则表达式的前缀标识
REGEX_PREFIX = PrefixConstants.BAN_PRE_TEXT_REGEX

SPAM_LIBRARIES = {
    "advertisement": SpamShelf.CN.ADVERTISEMENT,
    "pornographic": SpamShelf.CN.PORNOGRAPHIC,
    "politics": SpamShelf.CN.POLITICS,
    "general": SpamShelf.CN.GENERAL,
    "netease": SpamShelf.CN.NETEASE,
}


def update_words(
    new_words: Optional[list[str]] = None,
    add_words: Optional[list[str]] = None,
    remove_words: Optional[list[str]] = None,
    reload_library: bool = False,
) -> bool:
    """更新违禁词列表

    Args:
        new_words: 完全替换现有自定义违禁词
        add_words: 添加新的违禁词
        remove_words: 删除指定违禁词
        reload_library: 是否重新加载预定义词库

    Returns:
        是否成功更新
    """
    try:
        # Get current module state
        state = text_detector.get_module_state()
        config_ban_text_list = state["config_ban_text_list"]
        pre_text_list = state["pre_text_list"]
        
        # Clear cached ban words
        state["_cached_ban_words"] = None

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

        # 分离并更新普通文本和正则表达式
        normal_words = [
            w for w in config_ban_text_list if not w.startswith(REGEX_PREFIX)
        ]
        regex_patterns = [
            w[len(REGEX_PREFIX) :]
            for w in config_ban_text_list
            if w.startswith(REGEX_PREFIX)
        ]

        # 重新编译正则表达式
        _compiled_regex = text_detector._compile_regex_patterns(regex_patterns)

        # 重建DFA检测器 (仅使用普通文本)
        dfa = DLFA(
            words_resource=[
                *pre_text_list,  # 预定义词库
                normal_words,  # 自定义普通违禁词
            ]
        )

        # Update state back to text_detector
        state["dfa"] = dfa
        state["pre_text_list"] = pre_text_list
        state["normal_words"] = normal_words
        state["regex_patterns"] = regex_patterns
        state["_compiled_regex"] = _compiled_regex
        state["config_ban_text_list"] = config_ban_text_list
        text_detector.set_module_state(state)

        # 保存配置到文件
        save_config()

        log.info("违禁词更新完成")
        return True

    except Exception as e:
        log.error(f"更新违禁词失败: {e}")
        return False
