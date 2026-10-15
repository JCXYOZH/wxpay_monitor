# -*- coding: utf-8 -*-
"""微信4.1.15窗口定位与截图 (Win11 25H2 + 150% DPI)"""
import ctypes
import json
import os

import numpy as np
import win32gui
import win32ui

import config


def enable_dpi_awareness():
    """150%缩放下保证坐标为物理像素, 否则截图区域会偏移1.5倍"""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)   # PER_MONITOR_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def _enum_callback(hwnd, result):
    if not win32gui.IsWindowVisible(hwnd):
        return
    if win32gui.GetWindowText(hwnd) != config.WECHAT_WINDOW_TITLE:
        return
    l, t, r, b = win32gui.GetWindowRect(hwnd)
    if r - l > 400 and b - t > 400:          # 过滤小窗/悬浮窗
        result.append((hwnd, r - l, b - t))


def find_wechat_window():
    """返回微信主窗口句柄(取可见窗口中面积最大者), 找不到返回None"""
    wins = []
    try:
        win32gui.EnumWindows(_enum_callback, wins)
    except Exception:
        return None
    if not wins:
        return None
    wins.sort(key=lambda x: x[1] * x[2], reverse=True)
    return wins[0][0]


def is_iconic(hwnd):
    """窗口是否最小化"""
    return bool(win32gui.IsIconic(hwnd))


def capture_window(hwnd):
    """PrintWindow(PW_RENDERFULLCONTENT)截取客户区, 返回BGR ndarray
    特性: 可捕获GPU自绘内容; 窗口被遮挡仍有效; 窗口最小化则失败"""
    wr = win32gui.GetWindowRect(hwnd)
    w, h = wr[2] - wr[0], wr[3] - wr[1]
    if w <= 0 or h <= 0:
        return None
    hwnd_dc = mfc_dc = save_dc = bmp = None
    try:
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(mfc_dc, w, h)
        save_dc.SelectObject(bmp)
        # 2 = PW_RENDERFULLCONTENT: 捕获DWM/DX渲染内容(微信4.x必须)
        ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)
        bmp_str = bmp.GetBitmapBits(True)
        if len(bmp_str) != w * h * 4:
            return None
        img = np.frombuffer(bmp_str, dtype=np.uint8).reshape(h, w, 4)
        # 裁掉标题栏/边框 → 客户区
        pt = win32gui.ClientToScreen(hwnd, (0, 0))
        cl = win32gui.GetClientRect(hwnd)
        off_x, off_y = pt[0] - wr[0], pt[1] - wr[1]
        img = img[off_y:off_y + cl[3], off_x:off_x + cl[2]]
        if img.size == 0:
            return None
        return np.ascontiguousarray(img[:, :, :3])       # BGRA→BGR
    except Exception:
        return None
    finally:
        try:
            if bmp is not None:
                win32gui.DeleteObject(bmp.GetHandle())
            if save_dc is not None:
                save_dc.DeleteDC()
            if mfc_dc is not None:
                mfc_dc.DeleteDC()
            if hwnd_dc is not None:
                win32gui.ReleaseDC(hwnd, hwnd_dc)
        except Exception:
            pass


def capture_window_mss(hwnd):
    """备用方案: 屏幕坐标直截(要求窗口不被遮挡)"""
    import mss
    pt = win32gui.ClientToScreen(hwnd, (0, 0))
    cl = win32gui.GetClientRect(hwnd)
    with mss.mss() as sct:
        shot = sct.grab({"left": pt[0], "top": pt[1],
                         "width": cl[2], "height": cl[3]})
    return np.array(shot)[:, :, :3]


def is_blank(img):
    """空白帧检测(最小化时PrintWindow输出纯色)"""
    return img is None or float(img.std()) < 1.5


def load_roi():
    """roi.json(阶段1校准产物)优先, 否则用config默认值"""
    path = os.path.join(config.BASE_DIR, "roi.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return dict(config.ROI)


def crop_ratio(img, rect):
    """按比例矩形裁剪 (x0,y0,x1,y1 均为0~1)"""
    h, w = img.shape[:2]
    return img[int(h * rect[1]):int(h * rect[3]), int(w * rect[0]):int(w * rect[2])]