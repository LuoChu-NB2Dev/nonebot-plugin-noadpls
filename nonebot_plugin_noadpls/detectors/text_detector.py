"""Text detection module - handles text preprocessing and multi-layer detection."""
import pathlib
import re
import unicodedata
from re import Pattern

from cleanse_speech import DLFA, SpamShelf
from fuzzywuzzy import fuzz, process
from jieba import lcut_for_search
from opencc import OpenCC

from ..config import config
from ..utils.constants import PrefixConstants
from ..utils.log import log

# Module-level state
_cached_ban_words = None
_compiled_regex = {}  # 存储编译后的正则表达式

config_pre_text_list = config.env.ban_pre_text
config_ban_text_list = config.local.ban_text

# 定义正则表达式的前缀标识
REGEX_PREFIX = PrefixConstants.BAN_PRE_TEXT_REGEX

SPAM_LIBRARIES = {
    "advertisement": SpamShelf.CN.ADVERTISEMENT,
    "pornographic": SpamShelf.CN.PORNOGRAPHIC,
    "politics": SpamShelf.CN.POLITICS,
    "general": SpamShelf.CN.GENERAL,
    "netease": SpamShelf.CN.NETEASE,
}

# Initialize pre_text_list based on configuration
pre_text_list = []

if not config_pre_text_list:
    pre_text_list = [SpamShelf.CN.ADVERTISEMENT]
    log.info("使用默认词库: advertisement")
else:
    for pre_text in config_pre_text_list:
        pre_text = pre_text.lower()  # 转小写，便于匹配
        if pre_text == "none":
            pre_text_list = []
            log.info("不使用预定义词库")
            break
        if pre_text in SPAM_LIBRARIES:
            pre_text_list.append(SPAM_LIBRARIES[pre_text])
            log.info(f"已加载词库: {pre_text}")
        else:
            log.warning(f"未知词库: {pre_text}")

# 分离普通文本和正则表达式
normal_words = [w for w in config_ban_text_list if not w.startswith(REGEX_PREFIX)]
regex_patterns = [
    w[len(REGEX_PREFIX) :] for w in config_ban_text_list if w.startswith(REGEX_PREFIX)
]

# Initialize DFA detector
dfa = DLFA(words_resource=[*pre_text_list, normal_words])


def _compile_regex_patterns(patterns: list[str]) -> dict[str, Pattern]:
    """编译正则表达式模式

    Args:
        patterns: 正则表达式字符串列表

    Returns:
        编译后的正则表达式字典 {模式字符串: 编译后的模式}
    """
    compiled = {}
    for pattern in patterns:
        try:
            compiled[pattern] = re.compile(pattern, re.IGNORECASE)
            log.debug(f"成功编译正则表达式: {pattern}")
        except Exception as e:
            log.error(f"正则表达式编译失败: {pattern}, 错误: {e}")
    return compiled


# Compile regex patterns on module load
_compiled_regex = _compile_regex_patterns(regex_patterns)


def _load_ban_words_from_resources():
    """从资源文件加载所有违禁词，仅执行一次"""
    global _cached_ban_words
    if _cached_ban_words is not None:
        return _cached_ban_words

    # 获取所有违禁词
    all_ban_words = []

    # 从预定义词库中提取
    for resource in pre_text_list:
        # 预定义词库是文件路径，需要读取内容
        if isinstance(resource, pathlib.Path) and resource.exists():
            try:
                with open(resource, encoding="utf-8") as f:
                    # 尝试按行读取词库文件
                    words = [line.strip() for line in f.readlines() if line.strip()]
                    all_ban_words.extend(words)
                    log.debug(f"从预定义词库 {resource.name} 加载了 {len(words)} 个词")
            except UnicodeDecodeError:
                # 可能是二进制文件，尝试解析base64编码内容
                import base64

                try:
                    with open(resource, "rb") as f:
                        content = f.read()
                        lines = content.split(b"\n")
                        for line in lines:
                            if line:
                                try:
                                    word = (
                                        base64.b64decode(line).decode("utf-8").strip()
                                    )
                                    if word:
                                        all_ban_words.append(word)
                                except Exception:
                                    pass
                    log.debug(f"从二进制词库 {resource.name} 加载了词")
                except Exception as e:
                    log.error(f"无法读取词库文件 {resource}: {e}")
        else:
            log.error(f"预定义词库 {resource} 不存在或不可读")
            continue

    # 添加自定义违禁词（仅普通文本，不包含正则表达式）
    all_ban_words.extend(normal_words)

    _cached_ban_words = all_ban_words
    log.info(f"成功预加载 {len(all_ban_words)} 个违禁词")
    return all_ban_words


def check_text(text: str) -> list:
    """多层次检查文本是否包含违禁词

    Args:
        text: 需要检查的文本

    Returns:
        违禁词列表
    """
    # 第一层：原始DFA检测
    result = dfa.extract_illegal_words(text)
    if result:
        return result

    # 第二层：基础预处理后检测
    processed_text = preprocess_text(text)
    if processed_text != text:
        result = dfa.extract_illegal_words(processed_text)
        if result:
            return result

    # 第三层：模糊匹配检测
    fuzzy_matches = fuzzy_match_check(processed_text)
    if fuzzy_matches:
        return fuzzy_matches

    # 第四层：正则表达式检测
    regex_matches = regex_match_check(text)
    if regex_matches:
        return regex_matches

    return []


def regex_match_check(text: str) -> list:
    """使用正则表达式检查文本

    Args:
        text: 要检查的文本

    Returns:
        匹配到的正则表达式列表
    """
    matches = []

    # 对每个正则表达式进行匹配
    for pattern, compiled_pattern in _compiled_regex.items():
        log.debug(f"检查正则表达式: {pattern}")
        if compiled_pattern.search(text):
            matches.append(f"{REGEX_PREFIX}{pattern}: {compiled_pattern.findall(text)}")
            log.debug(
                f"正则表达式匹配成功: {pattern}: {compiled_pattern.findall(text)}"
            )

    return matches


def preprocess_text(text: str) -> str:
    """增强的文本预处理，应对各种规避检测手段

    Args:
        text: 原始文本

    Returns:
        处理后的文本
    """
    # 步骤1: Unicode规范化 (NFKC模式将兼容字符转为标准形式)
    result = unicodedata.normalize("NFKC", text)

    # 步骤2: 移除所有非中文、非英文、非数字的字符
    # 保留中文(含日韩)、英文和数字，移除其他所有字符
    result = re.sub(r"[^\u4e00-\u9fff\u3040-\u30ff\u3130-\u318fa-zA-Z0-9]", "", result)

    # 步骤3: 处理常见替代字符
    replace_pairs = {
        "0": "o",
        "○": "o",
        "〇": "o",
        "1": "l",
        "壹": "一",
        "2": "二",
        "贰": "二",
        "5": "s",
        "五": "5",
        "6": "b",
        "六": "6",
        "8": "B",
        "八": "8",
        "9": "g",
        "九": "9",
        "c": "口",
        "d": "口",
        "@": "a",
    }

    for old, new in replace_pairs.items():
        result = result.replace(old, new)

    result = OpenCC("t2s").convert(result)  # 繁体转简体

    log.debug(f"文本预处理: '{text}' -> '{result}'")
    return result


def fuzzy_match_check(text: str, min_score: int = 85) -> list:
    """使用jieba分词和模糊匹配进行检测

    Args:
        text: 要检查的文本
        min_score: 最低匹配分数阈值(0-100)，越高要求越严格

    Returns:
        匹配到的违禁词列表
    """
    all_ban_words = _load_ban_words_from_resources()

    # 如果违禁词库为空，直接返回
    if not all_ban_words:
        return []

    # 对文本进行分词
    words = lcut_for_search(text)

    # 存储匹配结果
    matches = []

    # 获取长度>=2的词进行匹配检查，避免单字误判
    check_words = [w for w in words if len(w) >= 2]

    # 对每个分词结果进行模糊匹配
    for word in check_words:
        normalized_word = unicodedata.normalize("NFKC", word).lower()
        # 使用process.extractOne获取最佳匹配结果
        match_result = process.extractOne(
            normalized_word, all_ban_words, scorer=fuzz.ratio
        )
        if match_result and match_result[1] >= min_score:
            ban_word = match_result[0]  # 匹配到的违禁词
            score = match_result[1]  # 匹配分数

            log.debug(f"模糊匹配: '{word}' -> '{ban_word}' (分数: {score})")
            if ban_word not in matches:
                matches.append(ban_word)

    return matches


# Export module-level variables for use by word_manager
def get_module_state():
    """Get current module state for word manager updates."""
    return {
        "dfa": dfa,
        "pre_text_list": pre_text_list,
        "normal_words": normal_words,
        "regex_patterns": regex_patterns,
        "_compiled_regex": _compiled_regex,
        "_cached_ban_words": _cached_ban_words,
        "config_ban_text_list": config_ban_text_list,
    }


def set_module_state(state):
    """Set module state after word manager updates."""
    global dfa, pre_text_list, normal_words, regex_patterns, _compiled_regex, _cached_ban_words, config_ban_text_list
    dfa = state["dfa"]
    pre_text_list = state["pre_text_list"]
    normal_words = state["normal_words"]
    regex_patterns = state["regex_patterns"]
    _compiled_regex = state["_compiled_regex"]
    _cached_ban_words = state["_cached_ban_words"]
    config_ban_text_list = state["config_ban_text_list"]
