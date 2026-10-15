# -*- coding: utf-8 -*-
"""Flask API: 业务方对接入口"""
from flask import Flask, jsonify, request

import config
from app import models

app = Flask(__name__)


def _order_json(o):
    return {"order_no": o["order_no"], "remark": o["remark_token"],
            "base_amount": float(o["base_amount"]),
            "expected_amount": float(o["expected_amount"]),
            "tail_number": o["tail_number"],
            "status": o["status"], "matched_by": o.get("matched_by"),
            "created_at": str(o["created_at"]),
            "expires_at": str(o["expires_at"]),
            "paid_at": str(o["paid_at"]) if o.get("paid_at") else None}


@app.route("/api/order", methods=["POST"])
def create_order():
    """业务方创建订单, 返回支付金额+备注码"""
    data = request.get_json(silent=True) or {}
    try:
        base = round(float(data.get("base_amount")), 2)
    except (TypeError, ValueError):
        return jsonify({"code": 1, "msg": "base_amount必须为数字"}), 400
    if base <= 0 or base > 100000:
        return jsonify({"code": 1, "msg": "base_amount取值非法"}), 400
    force_tail = data.get("force_tail")
    if force_tail is not None:
        try:
            force_tail = int(force_tail)
        except (TypeError, ValueError):
            return jsonify({"code": 1, "msg": "force_tail必须为整数"}), 400
    try:
        o = models.create_order(base, force_tail=force_tail)
    except ValueError as e:
        return jsonify({"code": 1, "msg": str(e)}), 400
    except models.NoTailAvailable as e:
        return jsonify({"code": 2, "msg": str(e) or "尾数池耗尽, 请稍后重试"}), 503
    return jsonify({"code": 0, "data": {
        "order_no": o["order_no"],
        "pay_amount": o["expected_amount"],
        "remark": o["remark_token"],
        "expires_at": str(o["expires_at"]),
        "tips": "引导用户支付 pay_amount, 并在转账时填写 remark; "
                "用户也可只按精确金额支付(不填备注)"}})


@app.route("/api/order/<order_no>", methods=["GET"])
def query_order(order_no):
    o = models.get_order(order_no)
    if not o:
        return jsonify({"code": 1, "msg": "订单不存在"}), 404
    return jsonify({"code": 0, "data": _order_json(o)})


@app.route("/api/stats", methods=["GET"])
def stats():
    return jsonify({"code": 0, "data": models.get_stats()})


@app.route("/api/test/simulate", methods=["POST"])
def simulate():
    """联调用: 不经微信/OCR直接模拟一笔收款"""
    data = request.get_json(silent=True) or {}
    try:
        amount = round(float(data.get("amount")), 2)
    except (TypeError, ValueError):
        return jsonify({"code": 1, "msg": "amount必须为数字"}), 400
    from app import matcher
    from datetime import datetime as _dt
    note = {"amount": amount, "remark": data.get("remark"),
            "remark_digits": data.get("remark"),
            "account": data.get("account") or "零钱",
            "summary": data.get("summary") or "SIM",
            "msg_time": data.get("msg_time") or _dt.now().strftime("%H:%M"),
            "seq": data.get("seq"),
            "raw_lines": ["SIM %.2f" % amount], "score": 1.0}
    return jsonify({"code": 0, "data": matcher.handle_notification(note)})


if __name__ == "__main__":
    models.init_db()
    app.run(host="127.0.0.1", port=5000)