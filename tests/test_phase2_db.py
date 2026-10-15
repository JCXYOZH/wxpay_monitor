# -*- coding: utf-8 -*-
"""阶段2-数据层测试: python tests/test_phase2_db.py
!! 会清空 wxpay_monitor 库的 orders/payments, 生产环境勿跑 !!"""
import os
import sys
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import models

models.init_db()
print("[1] 尾数池初始化 OK")

conn = models._pool.connection()
with conn.cursor() as cur:
    cur.execute("DELETE FROM payments")
    cur.execute("DELETE FROM orders")
    cur.execute("UPDATE tail_pool SET status='available', order_no=NULL,"
                " occupied_at=NULL")
conn.commit(); conn.close()

now_str = datetime.now().strftime("%H:%M")
old_str = (datetime.now() - timedelta(minutes=30)).strftime("%H:%M")

o1 = models.create_order(10.0)
o2 = models.create_order(10.0)
o3 = models.create_order(10.0)
amts = {o1["expected_amount"], o2["expected_amount"], o3["expected_amount"]}
assert len(amts) == 3
print("[2] 3单金额互异 OK:", sorted(amts))

# [3] 备注匹配(带今日时间)
r = models.match_payment(amount=o1["expected_amount"], remark=o1["remark_token"],
                         seq="10", msg_time=now_str, raw_text="T",
                         content_hash="A1", core_hash="C1")
assert r["status"] == "matched" and r["by"] == "remark", r
print("[3] 备注匹配 OK:", r["order_no"])

# [4] 序号门: (今日,seq=10)已登记 → 重扫且不重复入库
r = models.match_payment(amount=o1["expected_amount"], remark=o1["remark_token"],
                         seq="10", msg_time=now_str, raw_text="T",
                         content_hash="A1b", core_hash="C1b")
assert r["status"] == "rescan", r
cnt = models._query("SELECT COUNT(*) AS c FROM payments"
                    " WHERE content_hash IN ('A1','A1b')")[0]["c"]
assert cnt == 1, cnt
print("[4] 序号门重扫(不重复入库) OK")

# [5] 渲染窗口: 无seq, 15秒内同content_hash → duplicate
r = models.match_payment(amount=5.00, msg_time=now_str, raw_text="T",
                         content_hash="A2", core_hash="C2")
assert r["status"] == "unmatched", r
r = models.match_payment(amount=5.00, msg_time=now_str, raw_text="T",
                         content_hash="A2", core_hash="C2")
assert r["status"] == "duplicate", r
print("[5] 渲染窗口duplicate OK")

# [6] 时间门: 通知时间早于订单创建30分钟 → 拒绝匹配(旧通知不配新订单)
r = models.match_payment(amount=o2["expected_amount"], msg_time=old_str,
                         raw_text="T", content_hash="A3", core_hash="C3")
assert r["status"] == "unmatched", r
row = models._query("SELECT order_no FROM payments"
                    " WHERE content_hash='A3'")[0]
assert row["order_no"] is None
print("[6] 时间门拦截 OK")

# [7] 时间缺失 → 不匹配
r = models.match_payment(amount=o2["expected_amount"], raw_text="T",
                         content_hash="A4", core_hash="C4")
assert r["status"] == "unmatched" and \
       r.get("reason") == "time_missing_or_not_today", r
print("[7] 无时间指纹→不匹配 OK")

# [8] 昨天时间 → 不匹配
r = models.match_payment(amount=o2["expected_amount"], msg_time="昨天 22:02",
                         raw_text="T", content_hash="A5", core_hash="C5")
assert r["status"] == "unmatched" and \
       r.get("reason") == "time_missing_or_not_today", r
print("[8] 昨天时间→不匹配 OK")

# [9] 尾数匹配(正常今日时间)
r = models.match_payment(amount=o2["expected_amount"], msg_time=now_str,
                         raw_text="T", content_hash="A6", core_hash="C6")
assert r["status"] == "matched" and r["by"] == "tail", r
print("[9] 尾数匹配 OK:", r["order_no"])

# [10] 前缀匹配 + 基础金额
r = models.match_payment(amount=o3["base_amount"],
                         remark=o3["remark_token"][:10], msg_time=now_str,
                         raw_text="T", content_hash="A7", core_hash="C7")
assert r["status"] == "matched" and r["by"] == "prefix", r
print("[10] 前缀匹配 OK:", r["order_no"])

# [11] 备注对但金额错 → 拒绝
o4 = models.create_order(20.0)
r = models.match_payment(amount=0.01, remark=o4["remark_token"],
                         msg_time=now_str, raw_text="T",
                         content_hash="A8", core_hash="C8")
assert r["status"] == "unmatched", r
print("[11] 备注对金额错→拒绝 OK")

# [12] 基线占用当日序号 → 后续重扫
r = models.match_payment(amount=9.99, seq="88", msg_time=now_str,
                         raw_text="T", content_hash="A9", core_hash="C9",
                         baseline_only=True)
assert r["status"] == "baseline", r
r = models.match_payment(amount=9.99, seq="88", msg_time=now_str,
                         raw_text="T", content_hash="A10", core_hash="C10")
assert r["status"] == "rescan", r
print("[12] 基线占序号→重扫 OK")

# [13] 非今日通知不占用序号(防昨日通知堵住今日真实同序号收款)
r = models.match_payment(amount=8.88, seq="99", msg_time=None,
                         raw_text="T", content_hash="A11", core_hash="C11",
                         baseline_only=True)
row = models._query("SELECT day_seq FROM payments"
                    " WHERE content_hash='A11'")[0]
assert row["day_seq"] is None
r = models.match_payment(amount=8.88, seq="99", msg_time=now_str,
                         raw_text="T", content_hash="A12", core_hash="C12")
assert r["status"] == "unmatched", r
print("[13] 非今日不占序号 OK")

# [14] 宽松匹配: 唯一base订单+整数支付+无备注
o5 = models.create_order(0.20)
r = models.match_payment(amount=0.20, msg_time=now_str, raw_text="T",
                         content_hash="A20", core_hash="C20")
assert r["status"] == "matched" and r["by"] == "loose", r
print("[14] 宽松匹配(唯一base+整数) OK:", r["order_no"])

# [15] 多笔同base并存时, 整数支付拒绝宽松匹配(防错配)
# 注: [14]的o5已paid, 不会进入pending结果集; 必须"同时创建两笔"
#     才是真正的并存场景 → 用force_tail固定尾数, 确保两笔expected≠0.20
o6 = models.create_order(0.20, force_tail=5)    # expected=0.25, pending
o6b = models.create_order(0.20, force_tail=6)  # expected=0.26, pending
r = models.match_payment(amount=0.20, msg_time=now_str, raw_text="T",
                         content_hash="A21", core_hash="C21")
assert r["status"] == "unmatched", r
print("[15] 多笔同base并存→拒绝宽松 OK (转人工)")

# [16] force_tail=0固定金额
# 注: [11]遗留的o4(base=20.0)仍pending占用尾数0, 先取消并释放
conn = models._pool.connection()
with conn.cursor() as c2:
    c2.execute("UPDATE orders SET status='cancelled'"
               " WHERE order_no=%s AND status='pending'", (o4["order_no"],))
conn.commit(); conn.close()
models.recycle_expired()                # cancelled → 尾数0释放
o7 = models.create_order(0.10, force_tail=0)
assert o7["expected_amount"] == 0.10, o7
print("[16] force_tail=0固定金额 OK:", o7["expected_amount"])

print("\n数据层测试: 全部通过 ✔")