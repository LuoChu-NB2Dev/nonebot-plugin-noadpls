import hashlib
import io
from typing import Optional

import numpy as np
from PIL import Image

# 条件导入paddleocr，如果本地ocr不可用，不影响整体功能
try:
    from paddleocr import PaddleOCR

    # 创建全局 PaddleOCR 实例，只需初始化一次以节省资源
    paddle_ocr = PaddleOCR(
        use_angle_cls=True,  # 使用方向分类器
        lang="ch",  # 中文识别
        use_gpu=False,  # 不使用 GPU
        show_log=False,  # 不显示日志
    )
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False

from nonebot_plugin_noadpls.utils.cache import save_cache
from nonebot_plugin_noadpls.utils.constants import PrefixConstants
from nonebot_plugin_noadpls.utils.log import log


def recognize_image(image_data: bytes, cache_key: Optional[str] = None) -> str:
    """
    使用PaddleOCR识别图像数据中的文字

    Args:
        image_data: 图像的二进制数据
        cache_key: 缓存键名，如果为None则使用图像数据的哈希值

    Returns:
        识别的文本内容，没有换行符
    """
    if not PADDLE_AVAILABLE:
        raise ImportError("PaddleOCR未安装或不可用，无法进行本地OCR识别")

    # 如果没有提供缓存键，使用图像数据的哈希值作为缓存键
    if not cache_key:
        cache_key = (
            f"{PrefixConstants.OCR_RESULT_TEXT}{hashlib.md5(image_data).hexdigest()}"
        )

    # 将二进制数据转换为 PaddleOCR 可处理的格式
    image = io.BytesIO(image_data)
    pil_image = Image.open(image)
    np_array = np.array(pil_image)

    # 使用PaddleOCR识别图像
    result = paddle_ocr.ocr(np_array)

    # 提取识别的文本并拼接
    text = " "

    log.debug(f"OCR结果: {result}")

    # 检查结果是否为空
    if result is None or len(result) == 0:
        log.info("OCR未识别到任何文本")
        return text

    # 处理结果
    try:
        # 处理PaddleOCR返回的结构
        if isinstance(result, list):
            for page in result:  # 页面列表
                if isinstance(page, list):
                    for line in page:  # 文本行
                        if isinstance(line, list) and len(line) >= 2:
                            # 第二个元素是文本内容和置信度的元组
                            if isinstance(line[1], tuple) and len(line[1]) > 0:
                                text += line[1][0] + " "  # 添加文本并加空格
                            else:
                                raise AttributeError
    except Exception as e:
        log.error(f"本地处理OCR结果时出错: {e}")

    # 缓存结果
    save_cache(cache_key, text, PrefixConstants.OCR_CACHE_TTL)
    log.info(f"OCR结果已缓存: {cache_key}")

    return text
