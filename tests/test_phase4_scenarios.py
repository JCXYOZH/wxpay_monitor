# -*- coding: utf-8 -*-
"""阶段4-场景测试: python tests/test_phase4_scenarios.py [--loose]
前置: run_api.bat 和 python -m monitor.worker 都在运行中

默认两笔(固定金额 force_tail=0):
  订单A: ¥0.10, 用户支付时不填备注 → 尾数匹配
  订单B: ¥0.5x, 用户支付时填无关文字'提现成功，参与活动最高领68元'
         (无有效数字码) → 备注通道放弃进行匹配

--loose 追加第三笔(宽松匹配演示):
  订单C: base=0.10, 尾数随机(如0.11), 用户只付整数¥0.10+不填备注
         → base全局唯一 → loose匹配
"""
import os
import sys
import time

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = "http://127.0.0.1:5000"
RUN_LOOSE = "--loose" in sys.argv
PAY_INTERVAL = 10


def cleanup_pending():
    """清理测试遗留的pending订单, 释放全部尾数
    (用文件自身路径定位项目根目录, 不依赖运行时工作目录)"""
    import os
    import pymysql

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root)

    import config

    conn = pymysql.connect(host=config.MYSQL["host"],
                           port=config.MYSQL["port"],
                           user=config.MYSQL["user"],
                           password=config.MYSQL["password"],
                           database=config.MYSQL["database"],
                           autocommit=True)
    with conn.cursor() as cur:
        cur.execute("UPDATE orders SET status='cancelled'"
                    " WHERE status='pending'")
        cur.execute("UPDATE tail_pool SET status='available',"
                    " order_no=NULL, occupied_at=NULL")
    conn.close()
    print("[清理] 已取消全部pending订单, 尾数池已重置")

def create(base, force_tail=None):
    payload = {"base_amount": base}
    if force_tail is not None:
        payload["force_tail"] = force_tail
    r = requests.post(BASE + "/api/order", json=payload).json()
    if r["code"] != 0:
        print("创建失败:", r); sys.exit(1)
    return r["data"]


def wait_paid(orders, timeout=300):
    deadline = time.time() + timeout
    result = {o: "pending" for o in orders}
    while time.time() < deadline:
        time.sleep(5)
        line = []
        for o in orders:
            s = requests.get(BASE + "/api/order/" + o).json()["data"]
            result[o] = s
            line.append("%s:%s%s" % (o[-6:], "✔" if s["status"] == "paid" else "…",
                                     s["status"]))
        print("[%s] %s" % (time.strftime("%H:%M:%S"), " | ".join(line)))
        if all(result[o]["status"] == "paid" for o in orders):
            return result
    return result


cleanup_pending()
print("=" * 62)
print("场景测试: 固定金额支付 (force_tail=0)")
print("=" * 62)

print("\n[%s] 创建订单A (¥0.10, 尾数0)..." % time.strftime("%H:%M:%S"))
dA = create(0.10, force_tail=0)
print("  订单A: %s  支付金额=¥%.2f" % (dA["order_no"], dA["pay_amount"]))

print("  等待%d秒..." % PAY_INTERVAL)
time.sleep(PAY_INTERVAL)

print("[%s] 创建订单B (base=0.50, 尾数随机)..." % time.strftime("%H:%M:%S"))
dB = create(0.50)                     # 不指定尾数, 避免与A争抢尾数0
print("  订单B: %s  支付金额=¥%.2f" % (dB["order_no"], dB["pay_amount"]))

dC = None
if RUN_LOOSE:
    print("  等待%d秒..." % PAY_INTERVAL)
    time.sleep(PAY_INTERVAL)
    print("[%s] 创建订单C (base=0.10, 尾数随机→宽松匹配)..." %
          time.strftime("%H:%M:%S"))
    dC = create(0.10)
    print("  订单C: %s  提示金额=¥%.2f (请故意只付整数¥0.10)" %
          (dC["order_no"], dC["pay_amount"]))

print("\n" + "=" * 62)
print("请用另一个微信依次支付:")
print("  1) ¥%.2f (订单A) — 不填备注" % dA["pay_amount"])
print("  2) ¥%.2f (订单B) — 备注填: 提现成功，参与活动最高领68元" % dB["pay_amount"])
if RUN_LOOSE:
    print("  3) ¥0.10 (订单C, 注意是整数不是¥%.2f) — 不填备注" % dC["pay_amount"])
print("=" * 62)

orders = [dA["order_no"], dB["order_no"]] + \
         ([dC["order_no"]] if RUN_LOOSE else [])
result = wait_paid(orders)

print("\n" + "=" * 62)
all_paid = True
for o in orders:
    s = result[o]
    print("  %s → %-8s matched_by=%s" % (o, s["status"], s.get("matched_by")))
    all_paid = all_paid and s["status"] == "paid"
print("=" * 62)
print("全部匹配成功 ✔" if all_paid else "存在未完成订单 ✘ (查监控日志/payments表)")
sys.exit(0 if all_paid else 1)