-- 体育用品批发销售信息系统 - 数据库初始化脚本
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
    `phone`             VARCHAR(255)    DEFAULT NULL            COMMENT '电话',
    `email`             VARCHAR(100)    DEFAULT NULL            COMMENT '邮箱',
    `role`              VARCHAR(20)     NOT NULL DEFAULT 'customer' COMMENT '角色: customer管理员',
    `avatar`            MEDIUMTEXT      DEFAULT NULL            COMMENT '头像base64',
    `created_at`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    PRIMARY KEY (`customer_id`),
    UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='顾客信息表';

-- 2. 生产厂家表
CREATE TABLE `manufacturers` (
    `manufacturer_id`   BIGINT          NOT NULL AUTO_INCREMENT COMMENT '厂家代码',
    `manufacturer_name` VARCHAR(100)    NOT NULL                COMMENT '厂家名称',
    `contact_person`    VARCHAR(50)     DEFAULT NULL            COMMENT '联系人',
    `contact_phone`     VARCHAR(255)    DEFAULT NULL            COMMENT '联系电话',
    `address`           VARCHAR(255)    DEFAULT NULL            COMMENT '厂家地址',
    PRIMARY KEY (`manufacturer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生产厂家信息表';

-- 3. 库存商品表
CREATE TABLE `products` (
    `product_id`        BIGINT          NOT NULL AUTO_INCREMENT COMMENT '商品分类编码',
    `manufacturer_id`   BIGINT          NOT NULL                COMMENT '生产厂家编码',
    `product_name`      VARCHAR(200)    NOT NULL                COMMENT '商品说明/名称',
    `category`          VARCHAR(50)     DEFAULT '未分类'        COMMENT '商品分类：球类/服装/器材/鞋类/配件',
    `unit_price`        DECIMAL(10, 2)  NOT NULL                COMMENT '单价',
    `stock_quantity`    INT             NOT NULL DEFAULT 0      COMMENT '当前库存数量',
    `min_stock_threshold` INT           NOT NULL DEFAULT 10     COMMENT '最低库存预警值',
    `sales_count`       INT             NOT NULL DEFAULT 0      COMMENT '已售数量',
    `description`       TEXT            DEFAULT NULL            COMMENT '详细描述',
    `created_at`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`product_id`),
    KEY `idx_manufacturer` (`manufacturer_id`),
    KEY `idx_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存商品信息表';

-- 4. 订单表（增加COMPLETED状态）
CREATE TABLE `orders` (
    `order_id`          BIGINT          NOT NULL AUTO_INCREMENT COMMENT '订单号',
    `customer_id`       BIGINT          NOT NULL                COMMENT '顾客代码',
    `order_date`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '下单日期',
    `total_amount`      DECIMAL(12, 2)  NOT NULL DEFAULT 0.00   COMMENT '订单总金额快照',
    `shipping_req`      VARCHAR(100)    DEFAULT NULL            COMMENT '运输要求',
    `shipping_date`     DATE            DEFAULT NULL            COMMENT '运输日期',
    `total_weight`      DECIMAL(8, 2)   DEFAULT NULL            COMMENT '货物总重量',
    `shipping_cost`     DECIMAL(8, 2)   DEFAULT 0.00           COMMENT '运费',
    `payment_status`    TINYINT(1)      NOT NULL DEFAULT 0      COMMENT '付款状态0未付1已付2已退款3部分退款',
    `status`            VARCHAR(20)     NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING/CONFIRMED/OUT_OF_STOCK/SHIPPED/COMPLETED/CANCELLED/REFUNDING',
    `recipient_name`    VARCHAR(50)     DEFAULT NULL            COMMENT '收件人姓名',
    `recipient_address` VARCHAR(255)    DEFAULT NULL            COMMENT '收件地址',
    `recipient_phone`   VARCHAR(255)    DEFAULT NULL            COMMENT '收件电话',
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

-- 5. 订单细则表（增加商品名称快照）
CREATE TABLE `order_details` (
    `detail_id`         BIGINT          NOT NULL AUTO_INCREMENT COMMENT '细则编号',
    `order_id`          BIGINT          NOT NULL                COMMENT '订单号',
    `product_id`        BIGINT          NOT NULL                COMMENT '产品分类编号',
    `product_name_snapshot` VARCHAR(200) DEFAULT NULL           COMMENT '下单时商品名称快照',
    `manufacturer_id`   BIGINT          NOT NULL                COMMENT '生产厂',
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
    `payment_method`    VARCHAR(30)     NOT NULL                COMMENT '支付方式',
    `amount`            DECIMAL(10, 2)  NOT NULL                COMMENT '本次支付金额',
    `payment_time`      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '支付时间',
    `transaction_id`    VARCHAR(100)    DEFAULT NULL            COMMENT '外部交易流水号',
    `status`            VARCHAR(20)     NOT NULL DEFAULT 'PENDING' COMMENT '支付状态',
    PRIMARY KEY (`payment_id`),
    KEY `idx_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='支付信息表';

-- 7. 库存变动记录表
CREATE TABLE `stock_records` (
    `record_id`         BIGINT          NOT NULL AUTO_INCREMENT COMMENT '记录ID',
    `product_id`        BIGINT          NOT NULL                COMMENT '商品ID',
    `quantity_change`   INT             NOT NULL                COMMENT '变动数量正数为入库负数为出库',
    `reason`            VARCHAR(50)     NOT NULL                COMMENT '变动原因',
    `related_id`        BIGINT          DEFAULT NULL            COMMENT '关联ID',
    `operated_by`       BIGINT          DEFAULT NULL            COMMENT '操作人ID',
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
    `status`            VARCHAR(20)     NOT NULL DEFAULT 'PENDING' COMMENT '状态',
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

-- 10. 收货地址表（新增）
CREATE TABLE `addresses` (
    `address_id`        BIGINT          NOT NULL AUTO_INCREMENT,
    `customer_id`       BIGINT          NOT NULL                COMMENT '顾客ID',
    `recipient_name`    VARCHAR(50)     NOT NULL                COMMENT '收件人姓名',
    `phone`             VARCHAR(255)    NOT NULL                COMMENT '联系电话',
    `address`           VARCHAR(255)    NOT NULL                COMMENT '详细地址',
    `is_default`        TINYINT(1)      NOT NULL DEFAULT 0      COMMENT '是否默认地址',
    `tag`               VARCHAR(20)     DEFAULT NULL            COMMENT '地址标签',
    `created_at`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`address_id`),
    KEY `idx_customer` (`customer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收货地址表';

-- 11. 商品评价表（新增）
CREATE TABLE `reviews` (
    `review_id`         BIGINT          NOT NULL AUTO_INCREMENT,
    `order_id`          BIGINT          NOT NULL                COMMENT '关联订单ID',
    `product_id`        BIGINT          NOT NULL                COMMENT '商品ID',
    `customer_id`       BIGINT          NOT NULL                COMMENT '评价人ID',
    `rating`            TINYINT         NOT NULL                COMMENT '评分1-5星',
    `content`           TEXT            DEFAULT NULL            COMMENT '评价内容',
    `created_at`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`review_id`),
    KEY `idx_product` (`product_id`),
    KEY `idx_customer` (`customer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品评价表';

-- 12. 商品收藏表（新增）
CREATE TABLE `favorites` (
    `favorite_id`       BIGINT          NOT NULL AUTO_INCREMENT,
    `customer_id`       BIGINT          NOT NULL                COMMENT '顾客ID',
    `product_id`        BIGINT          NOT NULL                COMMENT '商品ID',
    `created_at`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`favorite_id`),
    UNIQUE KEY `uk_customer_product` (`customer_id`, `product_id`),
    KEY `idx_customer` (`customer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品收藏表';

-- 13. 首页轮播横幅表（新增）
CREATE TABLE `banners` (
    `banner_id`         BIGINT          NOT NULL AUTO_INCREMENT,
    `title`             VARCHAR(100)    NOT NULL                COMMENT '横幅标题',
    `subtitle`          VARCHAR(200)    DEFAULT NULL            COMMENT '副标题',
    `image_url`         VARCHAR(500)    DEFAULT NULL            COMMENT '图片URL（可为空，用占位色块）',
    `link_type`         VARCHAR(20)     DEFAULT 'product'       COMMENT '链接类型：product/category/none',
    `link_value`        VARCHAR(100)    DEFAULT NULL            COMMENT '链接值（商品ID或分类名）',
    `sort_order`        INT             NOT NULL DEFAULT 0      COMMENT '排序序号',
    `is_active`         TINYINT(1)      NOT NULL DEFAULT 1      COMMENT '是否启用',
    PRIMARY KEY (`banner_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='首页轮播横幅表';

-- 14. 站内通知表（新增）
CREATE TABLE `notifications` (
    `notify_id`         BIGINT          NOT NULL AUTO_INCREMENT,
    `customer_id`       BIGINT          NOT NULL                COMMENT '接收用户ID',
    `title`             VARCHAR(200)    NOT NULL                COMMENT '通知标题',
    `content`           TEXT            DEFAULT NULL            COMMENT '通知内容',
    `notify_type`       VARCHAR(30)     NOT NULL                COMMENT 'order_status/stock_alert/system',
    `related_id`        BIGINT          DEFAULT NULL            COMMENT '关联ID',
    `is_read`           TINYINT(1)      NOT NULL DEFAULT 0      COMMENT '是否已读',
    `created_at`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`notify_id`),
    KEY `idx_customer` (`customer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='站内通知表';

-- 15. 操作日志表（新增）
CREATE TABLE `operation_logs` (
    `log_id`            BIGINT          NOT NULL AUTO_INCREMENT,
    `operator_id`       BIGINT          DEFAULT NULL            COMMENT '操作人ID',
    `operator_name`     VARCHAR(50)     DEFAULT NULL            COMMENT '操作人姓名',
    `operation_type`    VARCHAR(50)     NOT NULL                COMMENT '操作类型',
    `target_type`       VARCHAR(30)     NOT NULL                COMMENT '目标类型order/product/purchase',
    `target_id`         BIGINT          DEFAULT NULL            COMMENT '目标ID',
    `detail`            VARCHAR(500)    DEFAULT NULL            COMMENT '操作详情',
    `created_at`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`log_id`),
    KEY `idx_operator` (`operator_id`),
    KEY `idx_type` (`operation_type`),
    KEY `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';

-- 插入示例数据
INSERT INTO `manufacturers` VALUES (1,'星辉体育用品有限公司','张明','13912345601','广东省东莞市厚街镇体育路18号'),(2,'力健运动器材厂','李强','13912345602','浙江省义乌市北苑工业区'),(3,'飞跃体育服饰厂','王芳','13912345603','福建省晋江市陈埭镇'),(4,'安达健身设备有限公司','赵伟','13912345604','江苏省南通市如东县');

INSERT INTO `customers` VALUES (1,'admin','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','系统管理员',NULL,NULL,'13900000000','admin@sports.com','admin',NULL,'2024-01-01 00:00:00'),(2,'test','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','测试顾客','北京市朝阳区建国路100号','100020','13800138000','test@sports.com','customer',NULL,'2024-01-01 00:00:00');

INSERT INTO `products` VALUES (1,1,'专业篮球','球类',89.00,200,10,35,'标准7号篮球，室内外通用'),(2,1,'足球','球类',69.00,150,10,42,'5号足球，比赛级品质'),(3,2,'羽毛球拍','器材',159.00,80,5,18,'碳纤维材质，超轻设计'),(4,2,'乒乓球拍套装','器材',49.00,120,10,12,'双面反胶，含3个球'),(5,3,'速干运动T恤','服装',39.00,300,20,28,'吸湿排汗，多色可选'),(6,3,'运动短裤','服装',45.00,250,15,15,'透气面料，弹性腰带'),(7,4,'跑步鞋','鞋类',199.00,100,10,22,'缓震鞋底，透气网面'),(8,4,'运动袜三双装','配件',19.90,500,30,8,'纯棉材质，抗菌防臭');

INSERT INTO `banners` VALUES (1,'热销商品推荐','全场运动器材低至5折','','product','1',1,1),(2,'新品上架','2026夏季新品运动服饰上市','','category','服装',2,1),(3,'批发特惠','批量采购享更多优惠折扣','','none','',3,1);
