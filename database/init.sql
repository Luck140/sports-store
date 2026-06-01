-- 体育用品批发销售信息系统 - 数据库初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS sports_store DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sports_store;

-- 1. 顾客表
CREATE TABLE `customers` (
    `customer_id`       BIGINT          NOT NULL AUTO_INCREMENT COMMENT '顾客代码',
    `username`          VARCHAR(50)     NOT NULL                COMMENT '登录用户名',
    `password`          VARCHAR(255)    NOT NULL                COMMENT '加密后的密码',
    `customer_name`     VARCHAR(50)     NOT NULL                COMMENT '顾客姓名',
    `address`           VARCHAR(255)    DEFAULT NULL            COMMENT '地址',
    `postal_code`       VARCHAR(20)     DEFAULT NULL            COMMENT '邮编',
    `phone`             VARCHAR(255)    DEFAULT NULL            COMMENT '电话，需加密存储',
    `email`             VARCHAR(100)    DEFAULT NULL            COMMENT '邮箱',
    `created_at`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    PRIMARY KEY (`customer_id`),
    UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='顾客信息表';

-- 2. 生产厂家表
CREATE TABLE `manufacturers` (
    `manufacturer_id`   BIGINT          NOT NULL AUTO_INCREMENT COMMENT '厂家代码',
    `manufacturer_name` VARCHAR(100)    NOT NULL                COMMENT '厂家名称',
    `contact_person`    VARCHAR(50)     DEFAULT NULL            COMMENT '联系人',
    `contact_phone`     VARCHAR(255)    DEFAULT NULL            COMMENT '联系电话，需加密',
    `address`           VARCHAR(255)    DEFAULT NULL            COMMENT '厂家地址',
    PRIMARY KEY (`manufacturer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生产厂家信息表';

-- 3. 库存商品表
CREATE TABLE `products` (
    `product_id`        BIGINT          NOT NULL AUTO_INCREMENT COMMENT '商品分类编码',
    `manufacturer_id`   BIGINT          NOT NULL                COMMENT '生产厂家编码',
    `product_name`      VARCHAR(200)    NOT NULL                COMMENT '商品说明/名称',
    `unit_price`        DECIMAL(10, 2)  NOT NULL                COMMENT '单价',
    `stock_quantity`    INT             NOT NULL DEFAULT 0      COMMENT '当前库存数量',
    `min_stock_threshold` INT           NOT NULL DEFAULT 10     COMMENT '最低库存预警值',
    `description`       TEXT            DEFAULT NULL            COMMENT '详细描述',
    `created_at`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`product_id`),
    KEY `idx_manufacturer` (`manufacturer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存商品信息表';

-- 4. 订单表
CREATE TABLE `orders` (
    `order_id`          BIGINT          NOT NULL AUTO_INCREMENT COMMENT '订单号',
    `customer_id`       BIGINT          NOT NULL                COMMENT '顾客代码',
    `order_date`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '下单日期',
    `total_amount`      DECIMAL(12, 2)  NOT NULL DEFAULT 0.00   COMMENT '订单总金额快照',
    `shipping_req`      VARCHAR(100)    DEFAULT NULL            COMMENT '运输要求',
    `shipping_date`     DATE            DEFAULT NULL            COMMENT '运输日期（实际发货日）',
    `total_weight`      DECIMAL(8, 2)   DEFAULT NULL            COMMENT '货物总重量',
    `shipping_cost`     DECIMAL(8, 2)   DEFAULT 0.00           COMMENT '运费',
    `payment_status`    TINYINT(1)      NOT NULL DEFAULT 0      COMMENT '付款状态 (0=未付款, 1=已付款)',
    `status`            VARCHAR(20)     NOT NULL DEFAULT 'PENDING' COMMENT '订单状态: PENDING, CONFIRMED, OUT_OF_STOCK, SHIPPED, CANCELLED',
    `recipient_name`    VARCHAR(50)     DEFAULT NULL            COMMENT '收件人姓名',
    `recipient_address` VARCHAR(255)    DEFAULT NULL            COMMENT '收件地址',
    `recipient_phone`   VARCHAR(255)    DEFAULT NULL            COMMENT '收件电话，需加密',
    `invoice_required`  TINYINT(1)      NOT NULL DEFAULT 0      COMMENT '是否需要发票',
    `invoice_title`     VARCHAR(200)    DEFAULT NULL            COMMENT '发票抬头',
    `invoice_tax_no`    VARCHAR(50)     DEFAULT NULL            COMMENT '发票税号',
    `created_at`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`order_id`),
    KEY `idx_customer` (`customer_id`),
    KEY `idx_status` (`status`),
    KEY `idx_payment_status` (`payment_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单信息表';

-- 5. 订单细则表
CREATE TABLE `order_details` (
    `detail_id`         BIGINT          NOT NULL AUTO_INCREMENT COMMENT '细则编号',
    `order_id`          BIGINT          NOT NULL                COMMENT '订单号',
    `product_id`        BIGINT          NOT NULL                COMMENT '产品分类编号',
    `manufacturer_id`   BIGINT          NOT NULL                COMMENT '生产厂（下单时快照）',
    `quantity`          INT             NOT NULL                COMMENT '数量',
    `unit_price`        DECIMAL(10, 2)  NOT NULL                COMMENT '下单时单价快照',
    `total_amount`      DECIMAL(12, 2)  NOT NULL                COMMENT '该条目总金额',
    PRIMARY KEY (`detail_id`),
    KEY `idx_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单细则表';

-- 6. 支付信息表
CREATE TABLE `payments` (
    `payment_id`        BIGINT          NOT NULL AUTO_INCREMENT,
    `order_id`          BIGINT          NOT NULL                COMMENT '关联的订单号',
    `payment_method`    VARCHAR(30)     NOT NULL                COMMENT '支付方式: CREDIT_CARD, ALIPAY, WECHAT',
    `amount`            DECIMAL(10, 2)  NOT NULL                COMMENT '本次支付金额',
    `payment_time`      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '支付时间',
    `transaction_id`    VARCHAR(100)    DEFAULT NULL            COMMENT '外部交易流水号',
    `status`            VARCHAR(20)     NOT NULL DEFAULT 'PENDING' COMMENT '支付状态: PENDING, PROCESSING, SUCCESS, FAILED',
    PRIMARY KEY (`payment_id`),
    KEY `idx_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='支付信息表';

-- 7. 库存变动记录表
CREATE TABLE `stock_records` (
    `record_id`         BIGINT          NOT NULL AUTO_INCREMENT COMMENT '记录ID',
    `product_id`        BIGINT          NOT NULL                COMMENT '商品ID',
    `quantity_change`   INT             NOT NULL                COMMENT '变动数量（正数为入库，负数为出库）',
    `reason`            VARCHAR(50)     NOT NULL                COMMENT '变动原因: ORDER_CONFIRM, PURCHASE, ORDER_CANCEL, ADJUST',
    `related_id`        BIGINT          DEFAULT NULL            COMMENT '关联ID（如订单ID、进货单ID）',
    `operated_by`       BIGINT          DEFAULT NULL            COMMENT '操作人ID（管理员ID）',
    `operated_at`       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`record_id`),
    KEY `idx_product` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存变动记录表';

-- 8. 进货单表
CREATE TABLE `purchase_orders` (
    `purchase_id`       BIGINT          NOT NULL AUTO_INCREMENT COMMENT '进货单ID',
    `manufacturer_id`   BIGINT          NOT NULL                COMMENT '厂家代码',
    `purchase_date`     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '进货日期',
    `total_amount`      DECIMAL(12, 2)  NOT NULL DEFAULT 0.00   COMMENT '进货总金额',
    `status`            VARCHAR(20)     NOT NULL DEFAULT 'PENDING' COMMENT '状态: PENDING, COMPLETED',
    `created_at`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`purchase_id`),
    KEY `idx_manufacturer` (`manufacturer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='进货单表';

-- 9. 进货单细则表
CREATE TABLE `purchase_details` (
    `detail_id`         BIGINT          NOT NULL AUTO_INCREMENT COMMENT '细则编号',
    `purchase_id`       BIGINT          NOT NULL                COMMENT '进货单ID',
    `product_id`        BIGINT          NOT NULL                COMMENT '商品ID',
    `quantity`          INT             NOT NULL                COMMENT '进货数量',
    `unit_price`        DECIMAL(10, 2)  NOT NULL                COMMENT '进货单价',
    `total_amount`      DECIMAL(12, 2)  NOT NULL                COMMENT '该条目总金额',
    PRIMARY KEY (`detail_id`),
    KEY `idx_purchase_id` (`purchase_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='进货单细则表';