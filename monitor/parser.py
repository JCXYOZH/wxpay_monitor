# -*- coding: utf-8 -*-
"""OCR文本 → 收款通知结构化解析

优化：
- 块内时间戳: 通知块内部出现时间戳文本时, 也关联到 cur["msg_time"]
  (解决新收款到达时时间戳在块内但未被关联的问题)
"""
import re

AMOUNT_RE = re.compile(r'[¥￥]\s*([\d,，]+(?:\.\d{1,2})?)')
PURE_AMOUNT_RE = re.compile(r'^\d{1,6}\.\d{2}$')
SEQ_RE = re.compile(r'今[日曰]\s*第\s*(\d+)\s*笔')
TIME_STAMP_RE = re.compile(
    r'^(?:昨天\s*|星期[一二三四五六日天]\s*|\d{1,2}月\d{1,2}日\s*)?\d{1,2}:\d{2}$')
DIGIT_FIX = str.maketrans({'O': '0', 'o': '0', 'l': '1', 'I': '1',
                           '，': ',', '。': '.'})

START_KEYWORDS = ('收款入账', '收款到账通知', '微信支付收款')
PAYER_REMARK_LABELS = ('转账备注', '付款方备注')
SYSTEM_NOTE_STOP = (
    '收款账户', '汇总', '收款统计', '收款小账本', '进入记账本', '我的账单',
    '交易状态', '收款方', '支付服务', '微信支付凭证', '查看账单', '使用零钱支付',
)

_NONE, _WAIT_PAYER, _WAIT_ACCOUNT, _WAIT_SUMMARY, _IGNORE_SYS = range(5)


def _norm_amount(s):
    s = s.translate(DIGIT_FIX).replace(',', '').replace('，', '').replace(' ', '')
    if s.count('.') > 1:
        head, _, tail = s.rpartition('.')
        s = head.replace('.', '') + '.' + tail
    try:
        v = float(s)
        return round(v, 2) if 0 < v < 1000000 else None
    except ValueError:
        return None


def _is_stop(text):
    return any(k in text for k in SYSTEM_NOTE_STOP)


def _looks_like_summary(text):
    return bool(SEQ_RE.search(text) or ('笔' in text and '共计' in text))


def parse_notifications(ocr_items):
    """ocr_items: [{'cx','cy','text','score'},...] 已按阅读顺序排列
    返回: [{'amount','remark','remark_digits','seq','account','summary',
            'sender','msg_time','raw_lines','score'}]"""
    notes, cur, state, prev_line = [], None, _NONE, None
    last_time = None

    def close():
        nonlocal cur
        if cur is not None and cur.get("amount") is not None:
            r = cur.get("remark") or ""
            digits = re.sub(r'\D', '', r.translate(DIGIT_FIX))
            cur["remark_digits"] = digits if len(digits) >= 8 else None
            if cur["remark_digits"] or cur.get("seq") or cur.get("account"):
                notes.append(cur)
        cur = None

    for it in ocr_items:
        text = (it.get("text") or "").strip()
        if not text:
            continue

        # ---- 时间戳行 ----
        if TIME_STAMP_RE.match(text):
            last_time = text
            if cur is None:
                continue                    # 块外时间戳, 仅记录
            else:
                # 块内时间戳 → 关联到当前通知(如果还没关联过)
                if cur.get("msg_time") is None:
                    cur["msg_time"] = text
                continue                    # 时间戳不作为通知内容处理

        # ---- 新通知块开始 ----
        if any(k in text for k in START_KEYWORDS):
            close()
            cur = {"amount": None, "remark": None, "remark_digits": None,
                   "seq": None, "account": None, "summary": None,
                   "sender": prev_line, "msg_time": last_time,
                   "raw_lines": [text], "score": it.get("score", 0.0)}
            state = _NONE
            continue
        if cur is None:
            prev_line = text
            continue
        cur["raw_lines"].append(text)
        cur["score"] = max(cur.get("score", 0.0), it.get("score", 0.0))
        stop = _is_stop(text)

        if state == _WAIT_PAYER:
            state = _NONE
            if not stop:
                cur["remark"] = text
                continue
        elif state == _IGNORE_SYS:
            if stop:
                state = _NONE
            else:
                continue
        elif state == _WAIT_ACCOUNT:
            state = _NONE
            if not stop:
                cur["account"] = text
                continue
        elif state == _WAIT_SUMMARY:
            state = _NONE
            if _looks_like_summary(text):
                cur["summary"] = text
                m = SEQ_RE.search(text)
                if m:
                    cur["seq"] = m.group(1)
                continue

        if any(k in text for k in PAYER_REMARK_LABELS):
            rest = ""
            for lbl in PAYER_REMARK_LABELS:
                if lbl in text:
                    rest = text.split(lbl, 1)[1].lstrip(' :：')
                    break
            if rest:
                cur["remark"] = rest
            else:
                state = _WAIT_PAYER
            continue
        if text == '备注' or text.startswith('备注：') or text.startswith('备注:'):
            continue
        if '收款账户' in text:
            rest = text.split('收款账户', 1)[1].lstrip(' :：')
            if rest:
                cur["account"] = rest
            else:
                state = _WAIT_ACCOUNT
            continue
        if '汇总' in text:
            rest = text.split('汇总', 1)[1].lstrip(' :：')
            if rest and _looks_like_summary(rest):
                cur["summary"] = rest
                m = SEQ_RE.search(rest)
                if m:
                    cur["seq"] = m.group(1)
            elif not rest:
                state = _WAIT_SUMMARY
            continue

        if cur["amount"] is None:
            m = AMOUNT_RE.search(text)
            if m:
                cur["amount"] = _norm_amount(m.group(1))
                continue
            if PURE_AMOUNT_RE.match(text):
                cur["amount"] = _norm_amount(text)
                continue

        m = SEQ_RE.search(text)
        if m and cur["seq"] is None:
            cur["seq"] = m.group(1)
            if not cur["summary"]:
                cur["summary"] = text

    close()
    return notes