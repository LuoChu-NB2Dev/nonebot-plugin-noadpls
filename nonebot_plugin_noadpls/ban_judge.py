from typing import Optional, List
from cleanse_speech import DLFA, SpamShelf
from .config import config, save_config
from .utils.log import log
import pathlib
import re
import unicodedata
from jieba import lcut_for_search
from fuzzywuzzy import fuzz, process
from opencc import OpenCC

pre_text_list = []

_cached_ban_words = None

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

dfa = DLFA(words_resource=[*pre_text_list, *config_ban_text_list])

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
                with open(resource, 'r', encoding='utf-8') as f:
                    # 尝试按行读取词库文件
                    words = [line.strip() for line in f.readlines() if line.strip()]
                    all_ban_words.extend(words)
                    log.debug(f"从预定义词库 {resource.name} 加载了 {len(words)} 个词")
            except UnicodeDecodeError:
                # 可能是二进制文件，尝试解析base64编码内容
                import base64
                try:
                    with open(resource, 'rb') as f:
                        content = f.read()
                        lines = content.split(b'\n')
                        for line in lines:
                            if line:
                                try:
                                    word = base64.b64decode(line).decode('utf-8').strip()
                                    if word:
                                        all_ban_words.append(word)
                                except:
                                    pass
                    log.debug(f"从二进制词库 {resource.name} 加载了词")
                except Exception as e:
                    log.error(f"无法读取词库文件 {resource}: {e}")
        elif hasattr(resource, 'words') and isinstance(resource.words, list):
            # 兼容可能存在的其他格式词库
            all_ban_words.extend(resource.words)

    # 添加自定义违禁词
    all_ban_words.extend(config_ban_text_list)
    
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

    return []


def preprocess_text(text: str) -> str:
    """增强的文本预处理，应对各种规避检测手段

    Args:
        text: 原始文本

    Returns:
        处理后的文本
    """
    # 步骤1: Unicode规范化 (NFKC模式将兼容字符转为标准形式)
    result = unicodedata.normalize('NFKC', text)

    # 步骤2: 移除所有非中文、非英文、非数字的字符
    # 保留中文(含日韩)、英文和数字，移除其他所有字符
    result = re.sub(
        r'[^\u4e00-\u9fff\u3040-\u30ff\u3130-\u318fa-zA-Z0-9]', '', result)

    # 步骤3: 处理常见替代字符
    replace_pairs = {
        '0': 'o', '○': 'o', '〇': 'o',
        '1': 'l', '壹': '一',
        '2': '二', '贰': '二',
        '5': 's', '五': '5',
        '6': 'b', '六': '6',
        '8': 'B', '八': '8',
        '9': 'g', '九': '9',
        'c': '口', 'd': '口',
        '@': 'a'
    }

    for old, new in replace_pairs.items():
        result = result.replace(old, new)

    result = OpenCC('t2s').convert(result)  # 繁体转简体

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
        normalized_word = unicodedata.normalize('NFKC', word).lower()
        # 使用process.extractOne获取最佳匹配结果
        match_result = process.extractOne(
            normalized_word, all_ban_words, scorer=fuzz.ratio)
        if match_result and match_result[1] >= min_score:
            ban_word = match_result[0]  # 匹配到的违禁词
            score = match_result[1]     # 匹配分数

            log.debug(f"模糊匹配: '{word}' -> '{ban_word}' (分数: {score})")
            if ban_word not in matches:
                matches.append(ban_word)

    return matches


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
    global dfa, config_ban_text_list, pre_text_list, _cached_ban_words

    _cached_ban_words = None
    
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
