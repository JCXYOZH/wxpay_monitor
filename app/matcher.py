# -*- coding: utf-8 -*-
"""收款匹配调度 + 业务回调通知"""
import hashlib
import logging
import threading
import time
from datetime import date, datetime

import requests

import config
from app import models

logger = logging.getLogger("wxpay")


def _hash_pair(note):
    """core_hash不含summary(OCR最不稳字段); seq/时间是最强指纹"""
    core = "%.2f|%s|%s|%s|%s|%s" % (
        note.get("amount") or 0,
        note.get("remark_digits") or "",
        note.get("seq") or "",
        note.get("account") or "",
        (note.get("sender") or "")[:20],
        note.get("msg_time") or "")
    core_hash = hashlib.md5(core.encode("utf-8")).hexdigest()
    content_hash = hashlib.md5(
        (core + "|" + date.today().isoformat()).encode("utf-8")).hexdigest()
    return content_hash, core_hash


def handle_notification(note):
    amount = note.get("amount")
    if amount is None:
        return {"status": "invalid"}
    ch, coh = _hash_pair(note)
    result = models.match_payment(
        amount=amount,
        remark=note.get("remark_digits"),
        seq=note.get("seq"),
        raw_text=" / ".join(note.get("raw_lines", [])),
        account=note.get("account") or "",
        content_hash=ch, core_hash=coh,
        confidence=note.get("score", 0.0),
        summary=note.get("summary"), msg_time=note.get("msg_time"))
    st = result["status"]
    if st == "matched":
        logger.info("收款匹配成功: 订单=%s 方式=%s 金额=%.2f",
                    result["order_no"], result["by"], result["amount"])
        _notify(result["order"], result["amount"])
    elif st == "unmatched":
        if result.get("reason") == "time_missing_or_not_today":
            logger.warning("收款缺少今日时间指纹(时间未识别/非今日), 仅登记不匹配: "
                           "%.2f 备注=%r seq=%s 时间=%r",
                           amount, note.get("remark_digits"),
                           note.get("seq"), note.get("msg_time"))
        else:
            logger.warning("收到未匹配收款(无对应待支付订单或被时间门拦截): "
                           "%.2f 备注=%r seq=%s 时间=%r",
                           amount, note.get("remark_digits"),
                           note.get("seq"), note.get("msg_time"))
    elif st == "duplicate":
        logger.info("渲染期重扫拦截(15秒内已登记, 旧记录id=%s): 金额=%.2f",
                    result.get("dup_of"), amount)
    elif st == "rescan":
        logger.info("历史通知重扫(已登记过, 不重复入库): 金额=%.2f", amount)
    return result


def _notify(order, amount):
    if not config.NOTIFY_URL:
        return

    def run():
        payload = {
            "order_no": order["order_no"],
            "remark": order["remark_token"],
            "amount": amount,
            "expected_amount": float(order["expected_amount"]),
            "matched_by": "paid",
            "paid_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        for i in range(3):
            try:
                r = requests.post(config.NOTIFY_URL, json=payload, timeout=5)
                if r.status_code == 200:
                    return
            except Exception:
                pass
            time.sleep(1 + i)
        logger.error("业务回调失败(3次): %s", config.NOTIFY_URL)

    threading.Thread(target=run, daemon=True).start()