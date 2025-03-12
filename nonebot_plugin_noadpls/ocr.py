import io
import os
import tempfile
from typing import Union, Optional, List
from pathlib import Path

from paddleocr import PaddleOCR

# 创建全局 PaddleOCR 实例，只需初始化一次以节省资源
# 可根据需要调整参数
paddle_ocr = PaddleOCR(
    use_angle_cls=True,  # 使用方向分类器
    lang="ch",  # 中文识别
    use_gpu=False,  # 不使用 GPU
    show_log=False,  # 不显示日志
)

def ocr_image(
    image: Union[str, bytes, Path, io.BytesIO], 
    lang: str = "ch"
) -> str:
    """
    使用本地 PaddleOCR 识别图片中的文字并返回字符串
    
    Args:
        image: 图片路径、字节数据或文件对象
        lang: 识别语言，默认为中文
        
    Returns:
        识别到的文本字符串，多行文本用换行符连接
    """
    # 处理字节流或 BytesIO 对象
    if isinstance(image, (bytes, io.BytesIO)):
        # 创建临时文件以处理字节数据
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            if isinstance(image, bytes):
                tmp.write(image)
            else:
                tmp.write(image.getvalue())
            tmp_path = tmp.name
        
        try:
            result = paddle_ocr.ocr(tmp_path, cls=True)
            os.unlink(tmp_path)  # 删除临时文件
        except Exception as e:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)  # 确保临时文件被删除
            raise e
    else:
        # 处理字符串路径或 Path 对象
        result = paddle_ocr.ocr(str(image), cls=True)
    
    # 提取并拼接识别到的文本
    text_list = []
    
    # PaddleOCR 返回格式: [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], [文本, 置信度]]
    # 处理可能的多页结果
    if result and isinstance(result[0], list):
        for page in result:
            for line in page:
                if isinstance(line, list) and len(line) >= 2:
                    text_list.append(line[1][0])  # 添加识别的文本
    
    # 返回用换行符连接的文本
    return " ".join(text_list)

if __name__ == "__main__":
    # 测试图片路径
    test_image_path = r"D:\OneDrive - Luo Chu Network Company\图片\Snipaste_2022-02-21_09-01-29.png"
    
    # 识别图片中的文本
    text = ocr_image(test_image_path)
    print(text)