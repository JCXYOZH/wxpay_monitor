# -*- coding: utf-8 -*-
"""阶段4端到端测试(需先启动run_api.bat和run_monitor.bat):
python tests/test_phase4_e2e.py
流程: 创建3个订单→提示你真实付款→轮询直到paid"""
import os
import sys
import time

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = "http://127.0.0.1:5000"

orders = []
for _ in range(3):
    r = requests.post(BASE + "/api/order", json={"base_amount": 0.01}).json()
    d = r["data"]
    orders.append(d["order_no"])
    print("订单%s: 请支付 ¥%.2f, 转账备注填: %s (或直接按金额支付)"
          % (d["order_no"], d["pay_amount"], d["remark"]))

print("\n等待支付(最长5分钟), 依次按上面金额付款...")
deadline = time.time() + 300
while time.time() < deadline:
    time.sleep(5)
    states = []
    for no in orders:
        s = requests.get(BASE + "/api/order/" + no).json()["data"]
        states.append(s["status"])
    print("状态:", dict(zip(orders, states)))
    if all(s == "paid" for s in states):
        print("\n3笔全部匹配成功 ✔"); sys.exit(0)
print("\n超时, 部分未支付"); sys.exit(1)