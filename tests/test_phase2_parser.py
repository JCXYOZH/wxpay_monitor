# -*- coding: utf-8 -*-
"""阶段2-解析器测试:
python tests/test_phase2_parser.py"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitor.parser import parse_notifications


def mk(texts):
    return [{"cx": 500, "cy": i * 40, "text": t, "score": 0.95}
            for i, t in enumerate(texts)]


CASES = [
    # 1. 收款码收款·无付款方备注 (watch实测: ¥0.98)
    (["收款到账通知", "收款金额", "￥0.98", "汇总", "今日第4笔收款，共计￥101.99",
      "备注", "收款成功，已存入零钱。点击可查看详情", "收款小账本", "支付服条", "授优事"],
     {"amount": 0.98, "digits": None, "seq": "4", "account": None}),
    # 2. 收款码收款·带付款方备注码 (watch实测: ¥1.00)
    #    系统"备注"(收款成功已存入零钱)绝不能覆盖"付款方备注"
    (["收款到账通知", "收款金额", "¥1.00", "付款方备注", "20261011113915", "汇总",
      "今日第2笔收款，共计￥1.01", "备注", "收款成功，已存入零钱。点击可查看",
      "详情", "收款小账本", "11:42", "瑶优惠", "支付服务"],
     {"amount": 1.00, "digits": "20261011113915", "seq": "2", "account": None}),
    # 3. 渲染残帧 (watch实测) → 质量门必须丢弃
    (["收款到账通知", "收款金额", "¥1.00", "古付明条", "授优惠"],
     None),
    # 4. 直接转账 (calib_full实测: ¥0.50, "转账备注"=付款方备注)
    (["快手科技", "你有一笔收款入账", "收款金额", "¥0.50", "收款账户", "零钱",
      "转账备注", "提现成功，参与活动最高领68元", "收款统计", "进入记账本>"],
     {"amount": 0.50, "digits": None, "seq": None, "account": "零钱"}),
    # 5. 支出消息(微信支付凭证) → 不产生任何通知
    (["微信支付凭证", "使用零钱支付", "¥1.83", "收款方", "青提香柠茶",
      "交易状态", "支付成功，对方已收款", "查看账单详情"],
     "EMPTY"),
    # 6. 同屏两条收款 (用户实测截图: ¥1.00与¥100.00, 标签值同行格式)
    (["你有一笔收款入账", "收款金额", "¥1.00", "付款方备注", "2026101113915",
      "收款账户：零钱", "汇总：今日第2笔收款，共计¥1.01",
      "你有一笔收款入账", "收款金额", "¥100.00", "付款方备注", "2026101114153",
      "收款账户：零钱", "汇总：今日第3笔收款，共计¥101.01"],
     "TWO"),
    # 7. 汇总行被OCR漏读, 系统备注紧随"汇总"标签(21:11实测):
    #    不得误当汇总; seq缺失但备注码在 → 保留该通知
    (["你有一笔收款入账", "收款金额", "¥100.00", "付款方备注", "20261011114153",
      "收款账户：零钱", "汇总", "备注：收款成功，已存入零钱。点击可查看", "收款小账本"],
     {"amount": 100.00, "digits": "20261011114153", "seq": None, "account": "零钱"}),
]

ok = True
for i, (texts, expect) in enumerate(CASES):
    notes = parse_notifications(mk(texts))
    if expect == "EMPTY" or expect is None:
        passed = (notes == [])
        got = "返回%d条(应为0)" % len(notes)
    elif expect == "TWO":
        got = [(n["amount"], n.get("remark_digits"), n.get("seq")) for n in notes]
        passed = (got == [(1.00, "2026101113915", "2"),
                          (100.00, "2026101114153", "3")])
    else:
        if len(notes) != 1:
            passed, got = False, "返回%d条(应为1)" % len(notes)
        else:
            n = notes[0]
            got = (n["amount"], n.get("remark_digits"), n.get("seq"),
                   n.get("account"))
            passed = (n["amount"] == expect["amount"] and
                      n.get("remark_digits") == expect["digits"] and
                      n.get("seq") == expect["seq"] and
                      n.get("account") == expect["account"])
    ok = ok and passed
    print("用例%d %s: %s" % (i + 1, "PASS" if passed else "FAIL", got))

print("\n解析器测试:", "全部通过 ✔" if ok else "存在失败 ✘")
sys.exit(0 if ok else 1)