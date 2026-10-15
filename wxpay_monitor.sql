/*
 Navicat Premium Dump SQL

 Source Server         : MySQL80
 Source Server Type    : MySQL
 Source Server Version : 80033 (8.0.33)
 Source Host           : 47.120.68.25:3306
 Source Schema         : wxpay_monitor

 Target Server Type    : MySQL
 Target Server Version : 80033 (8.0.33)
 File Encoding         : 65001

 Date: 15/10/2026 15:15:40
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for orders
-- ----------------------------
DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `order_no` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '订单号',
  `remark_token` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '支付备注码(用户填写)',
  `base_amount` decimal(10, 2) NOT NULL COMMENT '基础金额',
  `tail_number` tinyint UNSIGNED NULL DEFAULT NULL,
  `expected_amount` decimal(10, 2) NOT NULL COMMENT '预期支付金额=基础+尾数',
  `status` enum('pending','paid','expired','cancelled') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `matched_by` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT 'remark/prefix/tail',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `expires_at` datetime NOT NULL,
  `paid_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `order_no`(`order_no` ASC) USING BTREE,
  UNIQUE INDEX `remark_token`(`remark_token` ASC) USING BTREE,
  INDEX `idx_status_created`(`status` ASC, `created_at` ASC) USING BTREE,
  INDEX `idx_expect`(`expected_amount` ASC, `status` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 50 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '收款订单' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of orders
-- ----------------------------
INSERT INTO `orders` VALUES (29, 'ORD20261012233047964', '101223304249', 10.00, 0, 10.00, 'paid', 'remark', '2026-10-12 23:30:48', '2026-10-13 00:00:48', '2026-10-12 23:30:58');
INSERT INTO `orders` VALUES (30, 'ORD20261012233051946', '101223304335', 10.00, 1, 10.01, 'paid', 'tail', '2026-10-12 23:30:51', '2026-10-13 00:00:51', '2026-10-12 23:31:16');
INSERT INTO `orders` VALUES (31, 'ORD20261012233053944', '101223300044', 10.00, 2, 10.02, 'paid', 'prefix', '2026-10-12 23:30:54', '2026-10-13 00:00:54', '2026-10-12 23:31:19');
INSERT INTO `orders` VALUES (32, 'ORD20261012233120651', '101223313367', 20.00, 0, 20.00, 'cancelled', NULL, '2026-10-12 23:31:21', '2026-10-13 00:01:21', NULL);
INSERT INTO `orders` VALUES (33, 'ORD20261012233136305', '101223313640', 0.20, 1, 0.21, 'paid', 'loose', '2026-10-12 23:31:37', '2026-10-13 00:01:37', '2026-10-12 23:31:42');
INSERT INTO `orders` VALUES (34, 'ORD20261012233143926', '101223318595', 0.20, 5, 0.25, 'expired', NULL, '2026-10-12 23:31:44', '2026-10-13 00:01:44', NULL);
INSERT INTO `orders` VALUES (35, 'ORD20261012233146860', '101223313540', 0.20, 6, 0.26, 'expired', NULL, '2026-10-12 23:31:47', '2026-10-13 00:01:47', NULL);
INSERT INTO `orders` VALUES (36, 'ORD20261012233155785', '101223317307', 0.10, 0, 0.10, 'expired', NULL, '2026-10-12 23:31:55', '2026-10-13 00:01:55', NULL);
INSERT INTO `orders` VALUES (37, 'ORD20261013105233760', '101310529134', 0.10, 0, 0.10, 'cancelled', NULL, '2026-10-13 10:52:34', '2026-10-13 11:22:34', NULL);
INSERT INTO `orders` VALUES (38, 'ORD20261013111447096', '101311145299', 0.10, 0, 0.10, 'expired', NULL, '2026-10-13 11:14:48', '2026-10-13 11:44:48', NULL);
INSERT INTO `orders` VALUES (39, 'ORD20261013111459794', '101311146369', 0.50, 1, 0.51, 'expired', NULL, '2026-10-13 11:14:59', '2026-10-13 11:44:59', NULL);
INSERT INTO `orders` VALUES (40, 'ORD20261013111511864', '101311157233', 0.10, 2, 0.12, 'expired', NULL, '2026-10-13 11:15:12', '2026-10-13 11:45:12', NULL);
INSERT INTO `orders` VALUES (41, 'ORD20261013130107473', '101313019652', 0.01, 0, 0.01, 'expired', NULL, '2026-10-13 13:01:08', '2026-10-13 13:31:08', NULL);
INSERT INTO `orders` VALUES (42, 'ORD20261013130109762', '101313014927', 0.01, 1, 0.02, 'expired', NULL, '2026-10-13 13:01:10', '2026-10-13 13:31:10', NULL);
INSERT INTO `orders` VALUES (43, 'ORD20261013130111576', '101313013467', 0.01, 2, 0.03, 'expired', NULL, '2026-10-13 13:01:12', '2026-10-13 13:31:12', NULL);
INSERT INTO `orders` VALUES (44, 'ORD20261013183437019', '101318344907', 0.01, 0, 0.01, 'paid', 'remark', '2026-10-13 18:34:38', '2026-10-13 19:04:38', '2026-10-13 18:37:37');
INSERT INTO `orders` VALUES (45, 'ORD20261013183440693', '101318349014', 0.01, 1, 0.02, 'paid', 'tail', '2026-10-13 18:34:40', '2026-10-13 19:04:40', '2026-10-13 18:37:52');
INSERT INTO `orders` VALUES (46, 'ORD20261013183443628', '101318349824', 0.01, 2, 0.03, 'expired', NULL, '2026-10-13 18:34:43', '2026-10-13 19:04:43', NULL);
INSERT INTO `orders` VALUES (47, 'ORD20261014170301653', '101417036848', 120.00, 0, 120.00, 'expired', NULL, '2026-10-14 17:03:01', '2026-10-14 17:33:01', NULL);
INSERT INTO `orders` VALUES (48, 'ORD20261014170508323', '101417053171', 0.10, 1, 0.11, 'paid', 'tail', '2026-10-14 17:05:09', '2026-10-14 17:35:09', '2026-10-14 17:11:29');
INSERT INTO `orders` VALUES (49, 'ORD20261014220856871', '101422083235', 0.15, 0, 0.15, 'paid', 'tail', '2026-10-14 22:08:57', '2026-10-14 22:38:57', '2026-10-14 22:10:57');

-- ----------------------------
-- Table structure for payments
-- ----------------------------
DROP TABLE IF EXISTS `payments`;
CREATE TABLE `payments`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `order_no` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '匹配到的订单',
  `amount` decimal(10, 2) NOT NULL,
  `remark_text` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `day_seq` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '今日第N笔',
  `account` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `summary_text` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `msg_time` varchar(24) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `raw_text` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `content_hash` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '去重哈希',
  `core_hash` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `ocr_confidence` decimal(5, 4) NULL DEFAULT NULL,
  `match_status` enum('matched','unmatched','baseline','rescan') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'unmatched',
  `detected_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_amount`(`amount` ASC) USING BTREE,
  INDEX `idx_order`(`order_no` ASC) USING BTREE,
  INDEX `idx_content_hash`(`content_hash` ASC) USING BTREE,
  INDEX `idx_core_hash`(`core_hash` ASC) USING BTREE,
  INDEX `idx_day_seq`(`day_seq` ASC, `detected_at` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 132 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = 'OCR识别的收款流水' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of payments
-- ----------------------------
INSERT INTO `payments` VALUES (80, 'ORD20261012233047964', 10.00, '101223304249', '10', '', '', '23:30', 'T', 'A1', 'C1', 0.0000, 'matched', '2026-10-12 23:30:56');
INSERT INTO `payments` VALUES (81, NULL, 5.00, NULL, NULL, '', '', '23:30', 'T', 'A2', 'C2', 0.0000, 'unmatched', '2026-10-12 23:31:01');
INSERT INTO `payments` VALUES (82, NULL, 10.01, NULL, NULL, '', '', '23:00', 'T', 'A3', 'C3', 0.0000, 'unmatched', '2026-10-12 23:31:05');
INSERT INTO `payments` VALUES (83, NULL, 10.01, NULL, NULL, '', '', NULL, 'T', 'A4', 'C4', 0.0000, 'unmatched', '2026-10-12 23:31:09');
INSERT INTO `payments` VALUES (84, NULL, 10.01, NULL, NULL, '', '', '昨天 22:02', 'T', 'A5', 'C5', 0.0000, 'unmatched', '2026-10-12 23:31:11');
INSERT INTO `payments` VALUES (85, 'ORD20261012233051946', 10.01, NULL, NULL, '', '', '23:30', 'T', 'A6', 'C6', 0.0000, 'matched', '2026-10-12 23:31:13');
INSERT INTO `payments` VALUES (86, 'ORD20261012233053944', 10.00, '1012233000', NULL, '', '', '23:30', 'T', 'A7', 'C7', 0.0000, 'matched', '2026-10-12 23:31:17');
INSERT INTO `payments` VALUES (87, NULL, 0.01, '101223313367', NULL, '', '', '23:30', 'T', 'A8', 'C8', 0.0000, 'unmatched', '2026-10-12 23:31:23');
INSERT INTO `payments` VALUES (88, NULL, 9.99, NULL, '88', '', '', '23:30', 'T', 'A9', 'C9', 0.0000, 'baseline', '2026-10-12 23:31:26');
INSERT INTO `payments` VALUES (89, NULL, 8.88, NULL, NULL, '', '', NULL, 'T', 'A11', 'C11', 0.0000, 'baseline', '2026-10-12 23:31:29');
INSERT INTO `payments` VALUES (90, NULL, 8.88, NULL, '99', '', '', '23:30', 'T', 'A12', 'C12', 0.0000, 'unmatched', '2026-10-12 23:31:33');
INSERT INTO `payments` VALUES (91, 'ORD20261012233136305', 0.20, NULL, NULL, '', '', '23:30', 'T', 'A20', 'C20', 0.0000, 'matched', '2026-10-12 23:31:39');
INSERT INTO `payments` VALUES (92, NULL, 0.20, NULL, NULL, '', '', '23:30', 'T', 'A21', 'C21', 0.0000, 'unmatched', '2026-10-12 23:31:49');
INSERT INTO `payments` VALUES (93, NULL, 100.00, '20261011114153', NULL, '', '', NULL, '收款到账通知 / 收款金额 / ￥100.00 / 付款方备注 / 20261011114153 / 汇总 / 今日第3笔收款，共计￥101.01 / 备注 / 收款成功，已存入零钱。点击可查看 / 详情 / 收款小账本', '1e8307f49f421b494eb5da6713109394', '2c0167d70c0e50705b50873d05f4092a', 1.0000, 'baseline', '2026-10-12 23:38:53');
INSERT INTO `payments` VALUES (94, NULL, 0.98, NULL, NULL, '', '', NULL, '收款到账通知 / 收款金额 / ￥0.98 / 汇总 / 今日第4笔收款，共计￥101.99 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本 / 支付服务 / 摇优事', 'c31563ef460ddbc259dc0aaf3fb7b080', '824844e39bbc2b54b4008b93a9db34b7', 0.9999, 'baseline', '2026-10-12 23:38:54');
INSERT INTO `payments` VALUES (95, NULL, 0.98, NULL, NULL, '', '今日第4笔收款，共计￥101.99', '昨天12:10', '收款到账通知 / 收款金额 / ¥0.98 / 汇总 / 今日第4笔收款，共计￥101.99 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本 / 古付服条 / 授优事', '7e96395919601df6d5cffa4b7fd7f010', '0e6e1fed237bb03594b10ac0dfca575c', 1.0000, 'unmatched', '2026-10-12 23:39:00');
INSERT INTO `payments` VALUES (96, NULL, 0.10, NULL, NULL, '零钱', '', NULL, '你有一笔收款入账 / 收款金额 / ￥0.10 / 收款账户 / 零钱 / 收款统计 / 进入记账本> / 快手科技 / 摇优惠 / 付服条', '0a51c5e3dcd273951acfdb58dc6d01f4', 'c687c58cd7ee7d7b868b5117080df415', 0.9999, 'unmatched', '2026-10-12 23:39:29');
INSERT INTO `payments` VALUES (97, NULL, 0.01, NULL, '1', '', '今日第1笔收款，共计￥0.01', NULL, '收款到账通知 / 收款金额 / ￥0.01 / 汇总 / 今日第1笔收款，共计￥0.01 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本', 'c437f96b5efecbc853430c9bcad2588b', 'dfb8037ba869e16f5c4a51e8be701790', 0.9999, 'unmatched', '2026-10-12 23:39:36');
INSERT INTO `payments` VALUES (98, NULL, 0.50, NULL, NULL, '零钱', '', NULL, '你有一笔收款入账 / 收款金额 / ￥0.50 / 收款账户 / 零钱 / 转账备注 / 提现成功，参与活动最高领68元 / 进入记账本> / 收款统计 / 支付服务 / 摇优惠', '4c72d34c0f4fa8b75f3b677f810674e1', '59d6f63655dd3db13a962afb6209ce14', 0.9999, 'unmatched', '2026-10-12 23:39:40');
INSERT INTO `payments` VALUES (99, NULL, 100.00, '20261011114153', NULL, '', '', NULL, '收款到账通知 / 收款金额 / ￥100.00 / 付款方备注 / 20261011114153 / 今日第3笔收款，共计￥101.01 / 汇总 / 收款成功，已存入零钱。点击可查看 / 备注 / 详情 / 收款小账本', '2bd171e1e00682e10d3dc3cb4e7db4cd', '188429cb0ff1d423929bc2086d25a7a5', 0.9999, 'baseline', '2026-10-12 23:48:12');
INSERT INTO `payments` VALUES (100, NULL, 0.98, NULL, NULL, '', '', NULL, '收款到账通知 / 收款金额 / ¥0.98 / 汇总 / 今日第4笔收款，共计￥101.99 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本 / 古付明条 / 摇优事', '7e96395919601df6d5cffa4b7fd7f010', '0e6e1fed237bb03594b10ac0dfca575c', 0.9999, 'baseline', '2026-10-12 23:48:14');
INSERT INTO `payments` VALUES (101, NULL, 0.98, NULL, '4', '', '今日第4笔收款，共计￥101.99', '20:41', '收款到账通知 / 收款金额 / ¥0.98 / 汇总 / 今日第4笔收款，共计￥101.99 / 收款成功，已存入零钱。点击可查看详情 / 备注 / 收款小账本 / 拼多多 / 古付服条 / 授优事', '98f5aed2a5a0611d73b4b39cda8b4c51', '466d90f7126edff6fa083e0849b621d6', 0.9999, 'unmatched', '2026-10-12 23:48:51');
INSERT INTO `payments` VALUES (102, NULL, 100.00, '20261011114153', NULL, '', '', NULL, '收款到账通知 / 收款金额 / ￥100.00 / 付款方备注 / 20261011114153 / 汇总 / 今日第3笔收款，共计￥101.01 / 收款成功，已存入零钱。点击可查看 / 备注 / 详情 / 收款小账本', 'b0fc02abc7aed20488ff11290286d2a6', '82da3f617c39898caffe203f7ff2abc1', 1.0000, 'baseline', '2026-10-13 10:38:28');
INSERT INTO `payments` VALUES (103, NULL, 0.98, NULL, NULL, '', '', NULL, '收款到账通知 / 收款金额 / ¥0.98 / 汇总 / 今日第4笔收款，共计￥101.99 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本 / 支付服务 / 摇优事', '5455a4a49ee1fd730777596ca3f2154c', '1aafd66c874b000c1b7008a8c396746d', 1.0000, 'baseline', '2026-10-13 10:38:29');
INSERT INTO `payments` VALUES (104, NULL, 0.98, NULL, '4', '', '今日第4笔收款，共计￥101.99', '星期日12:10', '收款到账通知 / 收款金额 / ¥0.98 / 汇总 / 今日第4笔收款，共计￥101.99 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本 / 古付服条 / 授优事', '727645e4ebfb2de0bd0f53aca97f7ece', 'f682f7d17e4bb7041f712daec477e10b', 0.9999, 'unmatched', '2026-10-13 10:38:35');
INSERT INTO `payments` VALUES (105, NULL, 100.00, '20261011114153', NULL, '', '', NULL, '收款到账通知 / 收款金额 / ￥100.00 / 付款方备注 / 20261011114153 / 汇总 / 今日第3笔收款，共计￥101.01 / 收款成功，已存入零钱。点击可查看 / 备注 / 详情 / 收款小账本', 'b0fc02abc7aed20488ff11290286d2a6', '82da3f617c39898caffe203f7ff2abc1', 1.0000, 'baseline', '2026-10-13 10:50:50');
INSERT INTO `payments` VALUES (106, NULL, 0.98, NULL, NULL, '', '', NULL, '收款到账通知 / 收款金额 / ¥0.98 / 汇总 / 今日第4笔收款，共计￥101.99 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本 / 支付服务 / 摇优事', '5455a4a49ee1fd730777596ca3f2154c', '1aafd66c874b000c1b7008a8c396746d', 1.0000, 'baseline', '2026-10-13 10:50:51');
INSERT INTO `payments` VALUES (107, NULL, 0.98, NULL, NULL, '', '今日第4笔收款，共计￥101.99', '昨天20:41', '收款到账通知 / 收款金额 / ¥0.98 / 汇总 / 今日第4笔收款，共计￥101.99 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本 / 拼多多 / 古付明条 / 授优事', 'b7be24d13f6641b27a3c99370f163d89', 'aafa9e3b4e17b00b5080594cf7827c53', 1.0000, 'unmatched', '2026-10-13 10:51:10');
INSERT INTO `payments` VALUES (108, NULL, 100.00, '20261011114153', NULL, '', '', NULL, '收款到账通知 / 收款金额 / ¥100.00 / 付款方备注 / 20261011114153 / 今日第3笔收款，共计￥101.01 / 汇总 / 收款成功，已存入零钱。点击可查看 / 备注 / 详情 / 收款小账本', 'b0fc02abc7aed20488ff11290286d2a6', '82da3f617c39898caffe203f7ff2abc1', 0.9999, 'baseline', '2026-10-13 10:52:18');
INSERT INTO `payments` VALUES (109, NULL, 0.98, NULL, NULL, '', '', NULL, '收款到账通知 / 收款金额 / ¥0.98 / 汇总 / 今日第4笔收款，共计￥101.99 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本 / 支付服务 / 摇优事', '5455a4a49ee1fd730777596ca3f2154c', '1aafd66c874b000c1b7008a8c396746d', 0.9999, 'baseline', '2026-10-13 10:52:19');
INSERT INTO `payments` VALUES (110, NULL, 100.00, '20261011114153', NULL, '', '', NULL, '收款到账通知 / 收款金额 / ￥100.00 / 付款方备注 / 20261011114153 / 汇总 / 今日第3笔收款，共计￥101.01 / 备注 / 收款成功，已存入零钱。点击可查看 / 详情 / 收款小账本', 'b0fc02abc7aed20488ff11290286d2a6', '82da3f617c39898caffe203f7ff2abc1', 0.9999, 'baseline', '2026-10-13 11:14:36');
INSERT INTO `payments` VALUES (111, NULL, 0.98, NULL, NULL, '', '', NULL, '收款到账通知 / 收款金额 / ¥0.98 / 汇总 / 今日第4笔收款，共计￥101.99 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本 / 支付服务 / 摇优事', '5455a4a49ee1fd730777596ca3f2154c', '1aafd66c874b000c1b7008a8c396746d', 1.0000, 'baseline', '2026-10-13 11:14:37');
INSERT INTO `payments` VALUES (112, NULL, 0.10, NULL, NULL, '零钱', '', '昨天20:41', '你有一笔收款入账 / 收款金额 / ￥0.10 / 收款账户 / 零钱 / 进入记账本> / 收款统计 / 摇优惠 / 支付服务', 'a71c1a7f65b082976a547b54f39b25b6', '78fcecaeb1eb32342b62f05c8996a98f', 0.9999, 'unmatched', '2026-10-13 11:14:57');
INSERT INTO `payments` VALUES (113, NULL, 0.11, NULL, NULL, '零钱', '', '11:15', '你有一笔收款入账 / 收款金额 / ¥0.11 / 收款账户 / 零钱 / 收款统计 / 进入记账本> / 支付服务 / 摇优惠', 'ab7b5f2b61d788aa31691aab6ea54b83', '43a83b60f32fe21999b1af0f12f21977', 0.9999, 'unmatched', '2026-10-13 11:15:41');
INSERT INTO `payments` VALUES (114, NULL, 0.11, NULL, NULL, '零钱', '', NULL, '你有一笔收款入账 / 收款金额 / ¥0.11 / 收款账户 / 零钱 / 收款统计 / 进入记账本> / 快手科技 / 你右 / 摇优惠 / 支付服务', 'a46d92cc0cdb7b890d54d2096c78408f', '5546fc949958a3e51ee7a0855918fe36', 0.9999, 'unmatched', '2026-10-13 11:19:22');
INSERT INTO `payments` VALUES (115, NULL, 0.11, NULL, NULL, '零钱', '', NULL, '你有一笔收款入账 / 收款金额 / ￥0.11 / 收款账户 / 零钱 / 收款统计 / 进入记账本 > / 8 / 快手科技', 'ab7b5f2b61d788aa31691aab6ea54b83', '43a83b60f32fe21999b1af0f12f21977', 0.9999, 'baseline', '2026-10-13 18:18:38');
INSERT INTO `payments` VALUES (116, NULL, 0.50, NULL, NULL, '零钱', '', NULL, '你有一笔收款入账 / 收款金额 / ￥0.50 / 收款账户 / 零钱 / 转账备注 / 提现成功，参与活动最高领68元 / 收款统计 / 进入记账本 > / 支付服条 / 摇优惠', '61b5d23d20428ded5cda1b67fc0c0763', '1e8f5ef9af2a9f7555a53c84fbce6eee', 0.9999, 'baseline', '2026-10-13 18:18:40');
INSERT INTO `payments` VALUES (117, 'ORD20261013183437019', 0.01, '101318344907', '1', '', '今日第1笔收款，共计￥0.01', '18:37', '收款到账通知 / 收款金额 / ¥0.01 / 付款方备注 / 101318344907 / 汇总 / 今日第1笔收款，共计￥0.01 / 收款成功，已存入零钱。点击可查看 / 备注 / 详情 / 收款小账本 / 支付服务 / 摇优惠', 'fd1c0c10e50dc9d827e5ef6f5173c256', '624b22084ab81c75677b0d188718a429', 0.9998, 'matched', '2026-10-13 18:37:36');
INSERT INTO `payments` VALUES (118, 'ORD20261013183440693', 0.02, NULL, '2', '', '今日第2笔收款，共计￥0.03', NULL, '收款到账通知 / 收款金额 / ￥0.02 / 汇总 / 今日第2笔收款，共计￥0.03 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本 / 支付服条 / 授优事', '5f71a5319c4c3a4a0f891030d3a10953', '9d88b0c95397bb0a5e896cc6ebb14062', 1.0000, 'matched', '2026-10-13 18:37:51');
INSERT INTO `payments` VALUES (119, NULL, 0.01, '101318344907', NULL, '', '', NULL, '收款到账通知 / 收款金额 / ¥0.01 / 付款方备注 / 101318344907 / 汇总 / 今日第1笔收款，共计￥0.01 / 备注 / 收款成功，已存入零钱。点击可查看 / 详情 / 收款小账本', 'c5efd5257ba44eead6cc5de47d31a364', '001668e98387456f935f3252f5df7454', 1.0000, 'baseline', '2026-10-14 16:41:11');
INSERT INTO `payments` VALUES (120, NULL, 0.02, NULL, NULL, '', '', NULL, '收款到账通知 / 收款金额 / ¥0.02 / 今日第2笔收款，共计￥0.03 / 汇总 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本 / 摇优事 / 古付昵条', '568435a5c72b99854699867884d021b2', '446789c293c7d2a2023d70fba82691ac', 1.0000, 'baseline', '2026-10-14 16:41:12');
INSERT INTO `payments` VALUES (121, NULL, 0.01, '101318344907', NULL, '', '', NULL, '收款到账通知 / 收款金额 / ¥0.01 / 付款方备注 / 101318344907 / 汇总 / 今日第1笔收款，共计￥0.01 / 备注 / 收款成功，已存入零钱。点击可查看 / 详情 / 收款小账本', 'c5efd5257ba44eead6cc5de47d31a364', '001668e98387456f935f3252f5df7454', 1.0000, 'baseline', '2026-10-14 16:57:15');
INSERT INTO `payments` VALUES (122, NULL, 0.02, NULL, NULL, '', '', NULL, '收款到账通知 / 收款金额 / ¥0.02 / 今日第2笔收款，共计￥0.03 / 汇总 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本 / 摇优事 / 古付昵条', '568435a5c72b99854699867884d021b2', '446789c293c7d2a2023d70fba82691ac', 1.0000, 'baseline', '2026-10-14 16:57:15');
INSERT INTO `payments` VALUES (123, NULL, 0.01, '101318344907', NULL, '', '', NULL, '收款到账通知 / 收款金额 / ¥0.01 / 付款方备注 / 101318344907 / 汇总 / 今日第1笔收款，共计￥0.01 / 备注 / 收款成功，已存入零钱。点击可查看 / 详情 / 收款小账本', 'c5efd5257ba44eead6cc5de47d31a364', '001668e98387456f935f3252f5df7454', 1.0000, 'baseline', '2026-10-14 17:02:28');
INSERT INTO `payments` VALUES (124, NULL, 0.02, NULL, NULL, '', '', NULL, '收款到账通知 / 收款金额 / ¥0.02 / 今日第2笔收款，共计￥0.03 / 汇总 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本 / 摇优事 / 古付昵条', '568435a5c72b99854699867884d021b2', '446789c293c7d2a2023d70fba82691ac', 1.0000, 'baseline', '2026-10-14 17:02:29');
INSERT INTO `payments` VALUES (125, 'ORD20261014170508323', 0.11, NULL, NULL, '零钱', '', '17:11', '你有一笔收款入账 / 收款金额 / ￥0.11 / 收款账户 / 零钱 / 收款统计 / 进入记账本> / 支付服务 / 摇优惠', '031885138dd7f6e665c6a0d0e22e8331', 'f3655a79b3a217aa955bea261bfc8703', 0.9999, 'matched', '2026-10-14 17:11:27');
INSERT INTO `payments` VALUES (126, NULL, 0.02, NULL, NULL, '', '', NULL, '收款到账通知 / 收款金额 / ¥0.02 / 汇总 / 今日第2笔收款，共计￥0.03 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本 / 微拼', '751b0eb36347b8c97e22482854fdc864', '04633b321a5dfcd7f1fc2afb1ecff902', 1.0000, 'baseline', '2026-10-14 17:51:00');
INSERT INTO `payments` VALUES (127, NULL, 0.11, NULL, NULL, '零钱', '', NULL, '你有一笔收款入账 / 收款金额 / ￥0.11 / 收款账户 / 零钱 / 收款统计 / 进入记账本> / 支付服条 / 摇优惠', '3b90c0af623440db9e591592904ca9d8', 'ddd902b68b6ede32f1a1e94324022d51', 0.9999, 'baseline', '2026-10-14 17:51:01');
INSERT INTO `payments` VALUES (128, NULL, 0.02, NULL, NULL, '', '', NULL, '收款到账通知 / 收款金额 / ¥0.02 / 汇总 / 今日第2笔收款，共计￥0.03 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本 / 微拼', '751b0eb36347b8c97e22482854fdc864', '04633b321a5dfcd7f1fc2afb1ecff902', 1.0000, 'baseline', '2026-10-14 22:08:19');
INSERT INTO `payments` VALUES (129, NULL, 0.11, NULL, NULL, '零钱', '', NULL, '你有一笔收款入账 / 收款金额 / ￥0.11 / 收款账户 / 零钱 / 收款统计 / 进入记账本> / 支付服条 / 摇优惠', '3b90c0af623440db9e591592904ca9d8', 'ddd902b68b6ede32f1a1e94324022d51', 0.9999, 'baseline', '2026-10-14 22:08:21');
INSERT INTO `payments` VALUES (130, 'ORD20261014220856871', 0.15, NULL, '1', '', '今日第1笔收款，共计￥0.15', '22:10', '收款到账通知 / 收款金额 / ¥0.15 / 汇总 / 今日第1笔收款，共计￥0.15 / 备注 / 收款成功，已存入零钱。点击可查看详情 / 收款小账本 / 支付服条 / 授优惠', '254f39e241dee4e3c5e7b848b4910457', 'b46ab0f21132d9914b156251470194df', 0.9999, 'matched', '2026-10-14 22:10:56');
INSERT INTO `payments` VALUES (131, NULL, 0.15, '101422083235', '2', '', '今日第2笔收款，共计￥0.30', NULL, '收款到账通知 / 收款金额 / ¥0.15 / 付款方备注 / 101422083235 / 汇总 / 今日第2笔收款，共计￥0.30 / 收款成功，已存入零钱。点击可查看 / 备注 / 详情 / 收款小账本 / 支付服务 / 摇优惠', '69816432681b17a6ec88371eca17a21f', 'eec5927120ebd0cc1ed08b53bf91d2cc', 1.0000, 'unmatched', '2026-10-14 22:12:01');

-- ----------------------------
-- Table structure for tail_pool
-- ----------------------------
DROP TABLE IF EXISTS `tail_pool`;
CREATE TABLE `tail_pool`  (
  `tail_number` tinyint UNSIGNED NOT NULL COMMENT '尾数0-99',
  `order_no` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '当前占用订单',
  `status` enum('available','occupied') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'available',
  `occupied_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`tail_number`) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '金额尾数池' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of tail_pool
-- ----------------------------
INSERT INTO `tail_pool` VALUES (0, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (1, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (2, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (3, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (4, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (5, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (6, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (7, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (8, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (9, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (10, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (11, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (12, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (13, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (14, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (15, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (16, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (17, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (18, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (19, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (20, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (21, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (22, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (23, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (24, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (25, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (26, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (27, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (28, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (29, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (30, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (31, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (32, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (33, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (34, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (35, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (36, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (37, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (38, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (39, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (40, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (41, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (42, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (43, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (44, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (45, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (46, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (47, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (48, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (49, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (50, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (51, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (52, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (53, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (54, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (55, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (56, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (57, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (58, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (59, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (60, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (61, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (62, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (63, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (64, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (65, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (66, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (67, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (68, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (69, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (70, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (71, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (72, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (73, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (74, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (75, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (76, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (77, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (78, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (79, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (80, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (81, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (82, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (83, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (84, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (85, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (86, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (87, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (88, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (89, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (90, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (91, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (92, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (93, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (94, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (95, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (96, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (97, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (98, NULL, 'available', NULL);
INSERT INTO `tail_pool` VALUES (99, NULL, 'available', NULL);

SET FOREIGN_KEY_CHECKS = 1;
