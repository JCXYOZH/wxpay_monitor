# -*- coding: utf-8 -*-
"""OCR封装: rapidocr-onnxruntime (PP-OCRv4 mobile, 纯CPU, Py3.8兼容)"""
import threading

_engine = None
_lock = threading.Lock()


def get_engine():
    global _engine
    if _engine is None:
        with _lock:
            if _engine is None:
                from rapidocr_onnxruntime import RapidOCR
                _engine = RapidOCR()
    return _engine


def warmup():
    """预加载模型, 避免首次识别延迟"""
    import numpy as np
    get_engine()(np.zeros((64, 64, 3), dtype=np.uint8))


def ocr_image(img_bgr):
    """OCR一张图, 返回按阅读顺序(先y后x)排列的条目列表:
    [{'cx':中心x, 'cy':中心y, 'text':文本, 'score':置信度}, ...]"""
    if img_bgr is None or img_bgr.size == 0:
        return []
    result, _ = get_engine()(img_bgr)
    if not result:
        return []
    items = []
    for box, text, score in result:
        xs = [p[0] for p in box]
        ys = [p[1] for p in box]
        items.append({"cx": sum(xs) / 4.0, "cy": sum(ys) / 4.0,
                      "text": text, "score": float(score)})
    items.sort(key=lambda i: (i["cy"], i["cx"]))
    return items