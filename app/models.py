# -*- coding: utf-8 -*-
"""MySQL 8.0 数据访问层: 序号门 + 时间门 + 重扫不入库"""
import hashlib
import random
import re
from datetime import date, datetime, timedelta

import pymysql
from dbutils.pooled_db import PooledDB

import config

_TIME_YESTERDAY_RE = re.compile(r'^昨天')


class NoTailAvailable(Exception):
    """尾数池耗尽"""


DEDUP_WINDOW_SECONDS = 15   # 渲染期重扫窗口(无序号通知的短时去重)
_TIME_RE = re.compile(r'^(昨天)?\s*(\d{1,2}):(\d{2})$')

_pool = PooledDB(
    creator=pymysql, mincached=2, maxcached=8, maxconnections=16,
    blocking=True, ping=1,
    host=config.MYSQL["host"], port=config.MYSQL["port"],
    user=config.MYSQL["user"], password=config.MYSQL["password"],
    database=config.MYSQL["database"], charset=config.MYSQL["charset"],
    autocommit=False, cursorclass=pymysql.cursors.DictCursor,
)


def _parse_notif_time(msg_time):
    """'11:42'→今日datetime; '昨天 22:02'/星期/日期形式/缺失→None(不可匹配)"""
    if not msg_time:
        return None
    m = _TIME_RE.match(msg_time.strip())
    if not m:
        return None
    if m.group(1):                      # 昨天
        return None
    now = datetime.now()
    try:
        t = now.replace(hour=int(m.group(2)), minute=int(m.group(3)),
                        second=0, microsecond=0)
    except ValueError:
        return None
    if t > now:                         # 显示为"未来"(跨零点残影) → 视作非今日
        return None
    return t


def _query(sql, args=None):
    conn = _pool.connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchall()
    finally:
        conn.close()


def init_db():
    conn = _pool.connection()
    try:
        with conn.cursor() as cur:
            values = ",".join(["(%d)" % i for i in range(100)])
            cur.execute("INSERT IGNORE INTO tail_pool (tail_number) VALUES " + values)
        conn.commit()
    finally:
        conn.close()


def recycle_expired():
    now = datetime.now()
    conn = _pool.connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE orders SET status='expired' "
                        "WHERE status='pending' AND expires_at<%s", (now,))
            cur.execute(
                "UPDATE tail_pool t INNER JOIN orders o ON t.order_no=o.order_no "
                "SET t.status='available', t.order_no=NULL, t.occupied_at=NULL "
                "WHERE t.status='occupied' "
                "AND o.status IN ('expired','cancelled','paid')")
        conn.commit()
    finally:
        conn.close()


def _gen_ids(now):
    order_no = "ORD%s%03d" % (now.strftime("%Y%m%d%H%M%S"), random.randint(0, 999))
    remark = "%s%04d" % (now.strftime("%m%d%H%M"), random.randint(0, 9999))
    return order_no, remark


def create_order(base_amount, expire_seconds=None, force_tail=None):
    expire_seconds = expire_seconds or config.ORDER_EXPIRE
    now = datetime.now()
    base_amount = round(float(base_amount), 2)
    if base_amount <= 0:
        raise ValueError("base_amount必须大于0")
    conn = _pool.connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE orders SET status='expired' "
                        "WHERE status='pending' AND expires_at<%s", (now,))
            cur.execute(
                "UPDATE tail_pool t INNER JOIN orders o ON t.order_no=o.order_no "
                "SET t.status='available', t.order_no=NULL, t.occupied_at=NULL "
                "WHERE t.status='occupied' "
                "AND o.status IN ('expired','cancelled','paid')")
            cur.execute("SELECT tail_number FROM tail_pool "
                        "WHERE status='available' FOR UPDATE")
            avail = [r["tail_number"] for r in cur.fetchall()]
            if not avail:
                raise NoTailAvailable("尾数池已耗尽(100个尾数均被占用)")
            cur.execute("SELECT expected_amount FROM orders WHERE status='pending'")
            pending_amt = set(float(r["expected_amount"]) for r in cur.fetchall())
            if force_tail is not None:
                if not (isinstance(force_tail, int) and 0 <= force_tail <= 99):
                    raise ValueError("force_tail必须为0-99的整数")
                if force_tail not in avail:
                    raise NoTailAvailable("尾数%d当前被占用" % force_tail)
                if round(base_amount + force_tail / 100.0, 2) in pending_amt:
                    raise NoTailAvailable("金额%.2f已存在pending订单"
                                          % (base_amount + force_tail / 100.0))
                tail = force_tail
            else:
                cand = [t for t in avail
                        if round(base_amount + t / 100.0, 2) not in pending_amt]
                tail = cand[0] if cand else avail[0]
            order_no = remark = None
            for _ in range(3):
                _o, _r = _gen_ids(now)
                try:
                    cur.execute(
                        "INSERT INTO orders (order_no, remark_token, base_amount,"
                        " tail_number, expected_amount, status, created_at, expires_at)"
                        " VALUES (%s,%s,%s,%s,%s,'pending',%s,%s)",
                        (_o, _r, base_amount, tail,
                         round(base_amount + tail / 100.0, 2),
                         now, now + timedelta(seconds=expire_seconds)))
                    order_no, remark = _o, _r
                    break
                except pymysql.err.IntegrityError:
                    continue
            if not order_no:
                raise RuntimeError("单号生成冲突, 请重试")
            cur.execute("UPDATE tail_pool SET status='occupied', order_no=%s,"
                        " occupied_at=%s WHERE tail_number=%s",
                        (order_no, now, tail))
        conn.commit()
        return {"order_no": order_no, "remark_token": remark,
                "base_amount": base_amount, "tail_number": tail,
                "expected_amount": round(base_amount + tail / 100.0, 2),
                "status": "pending",
                "expires_at": now + timedelta(seconds=expire_seconds)}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _default_hashes(amount, remark, seq, account, msg_time):
    core = "%.2f|%s|%s|%s|%s" % (amount, remark or "", seq or "",
                                 account or "", msg_time or "")
    core_hash = hashlib.md5(core.encode("utf-8")).hexdigest()
    content_hash = hashlib.md5(
        (core + "|" + date.today().isoformat()).encode("utf-8")).hexdigest()
    return content_hash, core_hash


def match_payment(amount, remark=None, seq=None, raw_text="", account="",
                 content_hash=None, core_hash=None, confidence=0.0,
                 baseline_only=False, summary=None, msg_time=None):
    """识别到一笔收款:
    1) 序号门: (今日,seq)已登记 → rescan(不重复入库)
    2) 渲染窗口: 15秒内同content_hash → duplicate
    3) 历史重扫: core_hash已见(窗口外) → rescan(不重复入库)
    4) 无时间但有序号(新收款假设) → 用当前系统时间
    5) 首见入库 → baseline/unmatched
    6) 时间门: 仍无法确定今日时间 → 不匹配, 仅登记
    7) 匹配: 备注精确→备注前缀→金额尾数"""
    amount = round(float(amount), 2)
    notif_time = _parse_notif_time(msg_time)

    # 序号占用判断:
    # - 明确"昨天"标记 → 不占(防昨日通知堵塞今日真实同序号)
    # - 基线扫描+无今日时间 → 不占(旧通知大概率, 宁可不占)
    # - 基线扫描+有今日时间 → 占
    # - 运行中+无时间但有序号 → 占(新收款假设: 序号门已保证非重扫)
    # - 运行中+今日时间 → 占
    if not seq:
        store_seq = None
    elif baseline_only:
        store_seq = seq if notif_time is not None else None
    elif msg_time and _TIME_YESTERDAY_RE.match(msg_time.strip()):
        store_seq = None
    else:
        store_seq = seq

    if content_hash is None or core_hash is None:
        d_ch, d_coh = _default_hashes(amount, remark, seq, account, msg_time)
        content_hash = content_hash or d_ch
        core_hash = core_hash or d_coh
    conn = _pool.connection()
    try:
        with conn.cursor() as cur:
            now = datetime.now()
            # ---- 1) 序号门 ----
            if store_seq:
                cur.execute("SELECT id FROM payments WHERE day_seq=%s AND "
                            "detected_at>=CURDATE() LIMIT 1", (store_seq,))
                if cur.fetchone():
                    conn.rollback()
                    return {"status": "rescan", "amount": amount,
                            "seq": store_seq}
            # ---- 2) 渲染窗口 ----
            cur.execute("SELECT id FROM payments WHERE content_hash=%s AND "
                        "detected_at>=%s ORDER BY id DESC LIMIT 1",
                        (content_hash,
                         now - timedelta(seconds=DEDUP_WINDOW_SECONDS)))
            hit = cur.fetchone()
            if hit:
                conn.rollback()
                return {"status": "duplicate", "amount": amount,
                        "dup_of": hit["id"]}
            # ---- 3) 历史重扫(core_hash已见) → 不入库 ----
            if not baseline_only:
                cur.execute("SELECT id FROM payments WHERE core_hash=%s LIMIT 1",
                            (core_hash,))
                if cur.fetchone():
                    conn.rollback()
                    return {"status": "rescan", "amount": amount}

            # ---- 4) 运行中的新通知: 时间戳未识别 → 用当前时间 ----
            # OCR在通知刚到达(渲染未完成)时最容易漏读时间戳/汇总行,
            # 序号门+渲染窗口+core_hash 已保证同一笔真实收款只处理一次,
            # "到达即现在"是安全假设. 显式标记"昨天/日期"的除外(旧通知).
            if notif_time is None and store_seq:
                notif_time = now
            elif (notif_time is None and baseline_only is False
                  and not (msg_time and _TIME_YESTERDAY_RE.match(msg_time.strip()))
                  and not (msg_time and re.match(r'^(星期|\d{1,2}月)', msg_time.strip()))):
                # 无时间且无序号: 若msg_time本身为None(彻底没读到时间戳),
                # 视为刚到达的新通知 → 当前时间; 若读到的是"昨天/星期/日期"
                # 形式, 保持None(时间门拦截)
                if msg_time is None:
                    notif_time = now

            # ---- 5) 首见入库 ----
            status_val = "baseline" if baseline_only else "unmatched"
            cur.execute(
                "INSERT INTO payments (amount, remark_text, day_seq, account,"
                " summary_text, msg_time, raw_text, content_hash, core_hash,"
                " ocr_confidence, match_status)"
                " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (amount, remark, store_seq, account, (summary or "")[:128],
                 msg_time, (raw_text or "")[:500], content_hash, core_hash,
                 confidence, status_val))
            payment_id = cur.lastrowid
            if baseline_only:
                conn.commit()
                return {"status": "baseline", "amount": amount,
                        "payment_id": payment_id}
            # ---- 6) 时间门 ----
            if notif_time is None:
                conn.commit()
                return {"status": "unmatched", "amount": amount,
                        "payment_id": payment_id,
                        "reason": "time_missing_or_not_today"}
            deadline = notif_time + timedelta(
                minutes=config.TIME_GATE_TOLERANCE_MIN)

            # ---- 7) 匹配 ----
            def _amount_ok(o):
                return amount in (float(o["expected_amount"]),
                                 float(o["base_amount"]))

            order, by = None, None
            if remark:
                cur.execute("SELECT * FROM orders WHERE remark_token=%s AND"
                            " status='pending' AND expires_at>%s AND created_at<=%s"
                            " LIMIT 1 FOR UPDATE", (remark, now, deadline))
                o = cur.fetchone()
                if o and _amount_ok(o):
                    order, by = o, "remark"
            if order is None and remark and len(remark) >= config.REMARK_PREFIX_LEN:
                cur.execute("SELECT * FROM orders WHERE remark_token LIKE %s AND"
                            " status='pending' AND expires_at>%s AND created_at<=%s"
                            " LIMIT 2 FOR UPDATE", (remark + "%", now, deadline))
                rows = cur.fetchall()
                if len(rows) == 1 and _amount_ok(rows[0]):
                    order, by = rows[0], "prefix"
            if order is None:
                cur.execute("SELECT * FROM orders WHERE expected_amount=%s AND"
                            " status='pending' AND expires_at>%s AND created_at<=%s"
                            " ORDER BY created_at LIMIT 1 FOR UPDATE",
                            (amount, now, deadline))
                o = cur.fetchone()
                if o:
                    order, by = o, "tail"
            # ---- 宽松匹配: 用户付了base整数+无有效备注码 ----
            # 条件(全部满足才匹配, 防错配):
            #   1) 备注通道/尾数通道均未命中
            #   2) 金额恰好等于某订单的base_amount(整数支付)
            #   3) base=该金额的pending订单全局唯一(多笔并存时无法判断→人工)
            #   4) 该订单expected≠金额(尾数0的情况已被尾数通道处理)
            #   5) 时间门通过(查询条件已含)
            if order is None:
                cur.execute("SELECT * FROM orders WHERE base_amount=%s AND"
                            " status='pending' AND expires_at>%s AND created_at<=%s"
                            " FOR UPDATE", (amount, now, deadline))
                rows = cur.fetchall()
                if (len(rows) == 1
                        and float(rows[0]["expected_amount"]) != amount):
                    order, by = rows[0], "loose"

            if order:
                cur.execute("UPDATE orders SET status='paid', matched_by=%s,"
                            " paid_at=%s WHERE id=%s AND status='pending'",
                            (by, datetime.now(), order["id"]))
                cur.execute("UPDATE payments SET order_no=%s,"
                            " match_status='matched' WHERE id=%s",
                            (order["order_no"], payment_id))
                cur.execute("UPDATE tail_pool SET status='available',"
                            " order_no=NULL, occupied_at=NULL WHERE order_no=%s",
                            (order["order_no"],))
                conn.commit()
                return {"status": "matched", "by": by, "payment_id": payment_id,
                        "order_no": order["order_no"], "order": order,
                        "amount": amount}
            conn.commit()
            return {"status": "unmatched", "amount": amount,
                    "payment_id": payment_id}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_order(order_no):
    rows = _query("SELECT * FROM orders WHERE order_no=%s", (order_no,))
    return rows[0] if rows else None


def get_stats():
    orders = _query("SELECT status, COUNT(*) AS c FROM orders GROUP BY status")
    tails = _query("SELECT status, COUNT(*) AS c FROM tail_pool GROUP BY status")
    pays = _query("SELECT COUNT(*) AS c, IFNULL(SUM(amount),0) AS s"
                  " FROM payments WHERE detected_at>=CURDATE()"
                  " AND match_status IN ('matched','unmatched')")
    return {"orders": {r["status"]: r["c"] for r in orders},
            "tails": {r["status"]: r["c"] for r in tails},
            "today_payments": {"count": pays[0]["c"],
                               "total": float(pays[0]["s"])}}