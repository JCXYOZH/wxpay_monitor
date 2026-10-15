# -*- coding: utf-8 -*-
"""监控主进程: 截图→差异检测→OCR→解析→匹配"""
import logging
import logging.handlers
import os
import time

import cv2

import config
from app import matcher, models
from monitor import ocr_engine, parser, window

logger = logging.getLogger("wxpay")


def setup_logger():
    os.makedirs(config.LOG_DIR, exist_ok=True)
    os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    fh = logging.handlers.TimedRotatingFileHandler(
        os.path.join(config.LOG_DIR, "monitor.log"), when="midnight",
        backupCount=7, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(sh)
    logger.addHandler(fh)


def save_debug(img, tag):
    if config.SAVE_MATCH_SCREENSHOT:
        name = time.strftime("%Y%m%d_%H%M%S_") + tag + ".png"
        try:
            cv2.imwrite(os.path.join(config.SCREENSHOT_DIR, name), img)
        except Exception:
            pass


def check_active_chat(img, roi):
    """校验微信当前打开的是'微信支付'会话"""
    region = window.crop_ratio(img, roi["title_check"])
    items = ocr_engine.ocr_image(region)
    if not any("微信支付" in it["text"] for it in items):
        logger.error("!! 当前微信未选中'微信支付'会话, 收款监听已失效! "
                     "请点击微信左侧列表中的'微信支付'!")
        save_debug(img, "wrong_chat")


def process_frame(img, roi):
    region = window.crop_ratio(img, roi["new_message"])
    notes = parser.parse_notifications(ocr_engine.ocr_image(region))
    if not notes:
        # 渲染补偿: 通知可能正在渐入动画中, 1.5秒后重扫一次
        time.sleep(1.5)
        hwnd = window.find_wechat_window()
        if hwnd and not window.is_iconic(hwnd):
            img2 = window.capture_window(hwnd)
            if not window.is_blank(img2):
                img = img2
                region = window.crop_ratio(img2, roi["new_message"])
                notes = parser.parse_notifications(ocr_engine.ocr_image(region))
    if not notes:
        return
    logger.info("OCR识别到 %d 条收款通知", len(notes))
    save_debug(img, "detected")
    for n in notes:
        try:
            r = matcher.handle_notification(n)
            logger.info("  -> %s 金额=%.2f %s", r["status"], n["amount"],
                        r.get("order_no") or "")
        except Exception:
            logger.exception("处理通知异常: %s", n)


def startup_baseline(roi):
    """启动基线: 扫描整个消息区, 把屏幕上所有历史通知全部登记(不参与匹配)"""
    hwnd = window.find_wechat_window()
    if not hwnd or window.is_iconic(hwnd):
        logger.warning("基线扫描跳过: 微信窗口不可用")
        return
    img = window.capture_window(hwnd)
    if window.is_blank(img):
        logger.warning("基线扫描跳过: 截图为空")
        return
    region = window.crop_ratio(img, roi["message_area"])
    notes = parser.parse_notifications(ocr_engine.ocr_image(region))
    logger.info("基线登记 %d 条当前可见通知(不参与匹配)", len(notes))
    for n in notes:
        try:
            from app import matcher as _m
            ch, coh = _m._hash_pair(n)
            r = models.match_payment(
                amount=n["amount"], remark=n.get("remark_digits"),
                seq=n.get("seq"),
                raw_text=" / ".join(n.get("raw_lines", [])),
                account=n.get("account") or "",
                content_hash=ch, core_hash=coh,
                confidence=n.get("score", 0.0), baseline_only=True)
            logger.info("  基线: 金额=%.2f seq=%s 时间=%r → %s",
                        n["amount"], n.get("seq"), n.get("msg_time"),
                        r["status"])
        except Exception:
            logger.exception("基线登记异常: %s", n)


def main():
    setup_logger()
    window.enable_dpi_awareness()
    models.init_db()
    roi = window.load_roi()
    logger.info("启动监控: 轮询%.1fs | ROI=%s", config.MONITOR_INTERVAL, roi)
    logger.info("预加载OCR模型(首次约10-30秒)...")
    ocr_engine.warmup()
    startup_baseline(roi)
    logger.info("OCR就绪, 开始监听 (要求: 微信保持打开且'微信支付'会话选中)")

    prev_gray, last_full, last_title = None, 0.0, 0.0
    while True:
        try:
            hwnd = window.find_wechat_window()
            if not hwnd:
                logger.warning("未找到微信窗口, 2秒后重试")
                time.sleep(2); prev_gray = None; continue
            if window.is_iconic(hwnd):
                logger.warning("微信窗口已最小化! 监听失效, 请还原窗口")
                time.sleep(2); prev_gray = None; continue
            img = window.capture_window(hwnd)
            if window.is_blank(img):
                logger.warning("截图为空(窗口可能被遮挡或渲染异常)")
                time.sleep(2); prev_gray = None; continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if prev_gray is None:
                prev_gray = gray                # 首帧仅作差异基线, 不触发OCR
            else:
                changed = cv2.absdiff(gray, prev_gray).mean() > config.DIFF_THRESHOLD
                force = (time.time() - last_full) > config.FULL_OCR_INTERVAL
                if changed or force:
                    time.sleep(0.6)             # 等动画/渲染稳定
                    img2 = window.capture_window(hwnd)
                    if not window.is_blank(img2):
                        process_frame(img2, roi)
                        prev_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
                        last_full = time.time()
                    else:
                        prev_gray = None
                else:
                    prev_gray = gray

            if time.time() - last_title > config.TITLE_CHECK_INTERVAL:
                check_active_chat(img, roi)
                models.recycle_expired()
                last_title = time.time()

            time.sleep(config.MONITOR_INTERVAL)
        except KeyboardInterrupt:
            logger.info("手动停止监控"); break
        except Exception:
            logger.exception("监控循环异常, 3秒后恢复")
            time.sleep(3); prev_gray = None


if __name__ == "__main__":
    main()