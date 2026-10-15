# -*- coding: utf-8 -*-
"""阶段1校准工具:
  python -m tools.calibrate          单次: 截图+全图OCR+计算ROI→写roi.json
  python -m tools.calibrate --watch  持续监听测试: 只解析打印, 不碰数据库
"""
import json
import os
import sys
import time

import cv2

import config
from monitor import ocr_engine, parser, window


def single():
    window.enable_dpi_awareness()
    hwnd = window.find_wechat_window()
    if not hwnd:
        print("[X] 未找到微信窗口, 请确认微信已打开且未最小化")
        return
    if window.is_iconic(hwnd):
        print("[X] 微信窗口处于最小化状态, 请还原后重试")
        return
    img = window.capture_window(hwnd)
    if window.is_blank(img):
        print("[X] 截图失败或内容为空")
        return
    os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
    full_path = os.path.join(config.SCREENSHOT_DIR, "calib_full.png")
    cv2.imwrite(full_path, img)
    print("[1] 完整客户区截图已保存:", full_path,
          " 尺寸=%dx%d" % (img.shape[1], img.shape[0]))

    print("[2] 预加载OCR模型(首次约10-30秒)...")
    ocr_engine.warmup()
    items = ocr_engine.ocr_image(img)
    print("[3] 全图共识别 %d 条文本:" % len(items))
    for it in items:
        print("    cy=%4d cx=%4d conf=%.2f  %r"
              % (it["cy"], it["cx"], it["score"], it["text"]))

    # 用"微信支付"标题位置自动计算消息区ROI
    h, w = img.shape[:2]
    # 必须整词匹配: 子串匹配会把聊天记录中的"微信支付凭证"支出卡片
    # 误认成会话标题(它x坐标更大), 导致title_check算到屏幕下半部分(y0>y1无效)
    titles = [it for it in items if it["text"].strip() == "微信支付"]
    if not titles:
        print("\n[!] 未识别到'微信支付'标题, 使用config默认ROI, "
              "请人工核对 screenshots/calib_full.png 后手改 roi.json")
        return
    t = max(titles, key=lambda i: i["cx"])       # 取x最大的=消息区顶部标题
    tx, ty = t["cx"] / float(w), t["cy"] / float(h)
    x0 = max(0.20, min(0.35, tx - 0.06))
    y0 = max(0.03, min(0.12, ty + 0.02))
    roi = {
        "title_check":  [round(x0, 3), round(max(0.01, ty - 0.035), 3), 1.0,
                         round(min(0.99, ty + 0.035), 3)],
        "message_area": [round(x0, 3), round(y0, 3), 0.998, 0.965],
        "new_message":  [round(x0, 3), round(max(0.50, y0 + 0.10), 3), 0.998, 0.965],
    }
    with open("roi.json", "w", encoding="utf-8") as f:
        json.dump(roi, f, ensure_ascii=False, indent=2)
    print("\n[4] ROI已计算并写入 roi.json:")
    print(json.dumps(roi, ensure_ascii=False, indent=2))
    print("[OK] 阶段1校准完成, 接下来运行: python -m tools.calibrate --watch")


def watch():
    """持续监听测试(不写数据库): 手动收一笔款, 看能否正确解析"""
    window.enable_dpi_awareness()
    roi = window.load_roi()
    print("当前ROI:", json.dumps(roi, ensure_ascii=False))
    print("预加载OCR模型...")
    ocr_engine.warmup()
    print("开始监听(每0.5s截图, Ctrl+C退出). 请保持微信打开且'微信支付'会话选中,")
    print("然后用另一台手机/账号向本机收款码支付任意金额测试...\n")
    prev_gray = None
    while True:
        try:
            hwnd = window.find_wechat_window()
            if not hwnd or window.is_iconic(hwnd):
                print("[!] 微信窗口不可用"); time.sleep(2); prev_gray = None; continue
            img = window.capture_window(hwnd)
            if window.is_blank(img):
                print("[!] 截图为空"); time.sleep(2); prev_gray = None; continue
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if prev_gray is None or cv2.absdiff(gray, prev_gray).mean() > config.DIFF_THRESHOLD:
                time.sleep(0.6)                    # 等动画渲染稳定
                img2 = window.capture_window(hwnd)
                if not window.is_blank(img2):
                    prev_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
                    region = window.crop_ratio(img2, roi["new_message"])
                    notes = parser.parse_notifications(ocr_engine.ocr_image(region))
                    for n in notes:
                        print("=" * 50)
                        print("识别到收款: 金额=%.2f  备注=%r  账户=%s"
                              % (n["amount"], n.get("remark"), n.get("account")))
                        print("  原文:", " / ".join(n["raw_lines"]))
            else:
                prev_gray = gray
            time.sleep(config.MONITOR_INTERVAL)
        except KeyboardInterrupt:
            print("\n退出监听"); return
        except Exception as e:
            print("[!] 异常:", e); time.sleep(3)


if __name__ == "__main__":
    if "--watch" in sys.argv:
        watch()
    else:
        single()