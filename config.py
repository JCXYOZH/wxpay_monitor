# -*- coding: utf-8 -*-
"""全局配置"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- MySQL 8.0 ----------
MYSQL = {
    "host": "47.120.68.25",
    "port": 3306,
    "user": "root",
    "password": "Big0try92.",
    "database": "wxpay_monitor",
    "charset": "utf8mb4",
}

# ---------- 微信窗口 ----------
WECHAT_WINDOW_TITLE = "微信"          # 4.1.15 主窗口标题
WECHAT_CHAT_TARGET = "微信支付"        # 监听的会话名称
MONITOR_INTERVAL = 0.5               # 轮询间隔(秒)
DIFF_THRESHOLD = 2.0                 # 帧差异阈值(平均像素差)
FULL_OCR_INTERVAL = 60               # 兜底全量OCR间隔(秒)
TITLE_CHECK_INTERVAL = 60            # "微信支付"会话校验间隔(秒)

# 监控区域(占客户区比例; 阶段1校准后 roi.json 会覆盖这些值)
ROI = {
    "title_check":  (0.30, 0.02, 1.00, 0.10),   # 会话标题区
    "message_area": (0.30, 0.10, 0.998, 0.965), # 全部消息区
    "new_message":  (0.30, 0.50, 0.998, 0.965),  # 底部新消息区(主OCR目标)
}

# ---------- 业务 ----------
ORDER_EXPIRE = 1800         # 订单过期(秒)
REMARK_PREFIX_LEN = 8       # 备注码前缀匹配最小长度

# ---------- 回调 ----------
NOTIFY_URL = "http://127.0.0.1:8080/api/pay/notify?token=wX7eK9OnePqQV"  # 收款成功后POST通知业务方; 留空=仅更新数据库(业务方轮询)

# ---------- 路径 ----------
LOG_DIR = os.path.join(BASE_DIR, "logs")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshots")
SAVE_MATCH_SCREENSHOT = True    # 匹配成功时保存现场截图

# ---------- 匹配安全 ----------
TIME_GATE_TOLERANCE_MIN = 2   # 通知时间与订单创建时间容差(分钟)