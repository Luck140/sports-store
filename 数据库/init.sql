-- SportsStore Database Init
USE sports_store;

-- Drop in reverse dependency order
DROP TABLE IF EXISTS operation_logs, notifications, stock_records, reviews,
  favorites, addresses, payments, order_details, orders, purchase_details,
  purchase_orders, products, manufacturers, banners, customers;

-- 1. customers
CREATE TABLE customers (
  customer_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  customer_name VARCHAR(100) NOT NULL,
  address VARCHAR(255),
  postal_code VARCHAR(20),
  phone VARCHAR(255),
  email VARCHAR(100),
  role VARCHAR(20) NOT NULL DEFAULT 'customer',
  avatar TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. manufacturers
CREATE TABLE manufacturers (
  manufacturer_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  manufacturer_name VARCHAR(100) NOT NULL,
  contact_person VARCHAR(50),
  contact_phone VARCHAR(255),
  address VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. products
CREATE TABLE products (
  product_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  manufacturer_id BIGINT NOT NULL,
  product_name VARCHAR(200) NOT NULL,
  category VARCHAR(50) DEFAULT '',
  unit_price DECIMAL(10,2) NOT NULL,
  stock_quantity INT NOT NULL DEFAULT 0,
  min_stock_threshold INT NOT NULL DEFAULT 10,
  sales_count INT NOT NULL DEFAULT 0,
  description TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. orders
CREATE TABLE orders (
  order_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  shipping_req VARCHAR(100),
  shipping_date DATE,
  total_weight DECIMAL(8,2),
  shipping_cost DECIMAL(8,2) DEFAULT 0.00,
  payment_status SMALLINT NOT NULL DEFAULT 0,
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  recipient_name VARCHAR(50),
  recipient_address VARCHAR(255),
  recipient_phone VARCHAR(255),
  invoice_required SMALLINT NOT NULL DEFAULT 0,
  invoice_title VARCHAR(200),
  invoice_tax_no VARCHAR(50),
  invoice_address_phone VARCHAR(255),
  invoice_bank VARCHAR(255),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. order_details
CREATE TABLE order_details (
  detail_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  order_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  product_name_snapshot VARCHAR(200),
  manufacturer_id BIGINT NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  total_amount DECIMAL(12,2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. payments
CREATE TABLE payments (
  payment_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  order_id BIGINT NOT NULL,
  payment_method VARCHAR(30) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  payment_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  transaction_id VARCHAR(100),
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. stock_records
CREATE TABLE stock_records (
  record_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  product_id BIGINT NOT NULL,
  quantity_change INT NOT NULL,
  reason VARCHAR(50) NOT NULL,
  related_id BIGINT,
  operated_by BIGINT,
  operated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES products(product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. purchase_orders
CREATE TABLE purchase_orders (
  purchase_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  manufacturer_id BIGINT NOT NULL,
  purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. purchase_details
CREATE TABLE purchase_details (
  detail_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  purchase_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  total_amount DECIMAL(12,2) NOT NULL,
  FOREIGN KEY (purchase_id) REFERENCES purchase_orders(purchase_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. addresses
CREATE TABLE addresses (
  address_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  recipient_name VARCHAR(50) NOT NULL,
  phone VARCHAR(255) NOT NULL,
  address VARCHAR(255) NOT NULL,
  is_default SMALLINT NOT NULL DEFAULT 0,
  tag VARCHAR(20),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. reviews
CREATE TABLE reviews (
  review_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  order_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  customer_id BIGINT NOT NULL,
  rating SMALLINT NOT NULL,
  content TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. favorites
CREATE TABLE favorites (
  favorite_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  UNIQUE KEY uk_cp (customer_id, product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 13. banners
CREATE TABLE banners (
  banner_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(100) NOT NULL,
  subtitle VARCHAR(200),
  image_url VARCHAR(500),
  link_type VARCHAR(20) DEFAULT 'product',
  link_value VARCHAR(100),
  sort_order INT NOT NULL DEFAULT 0,
  is_active SMALLINT NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 14. notifications
CREATE TABLE notifications (
  notify_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  title VARCHAR(200) NOT NULL,
  content TEXT,
  notify_type VARCHAR(30) NOT NULL,
  related_id BIGINT,
  is_read SMALLINT NOT NULL DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 15. operation_logs
CREATE TABLE operation_logs (
  log_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  operator_id BIGINT,
  operator_name VARCHAR(50),
  operation_type VARCHAR(50) NOT NULL,
  target_type VARCHAR(30) NOT NULL,
  target_id BIGINT,
  detail VARCHAR(500),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========== SEED DATA ==========

-- Admin (pw: admin123)
INSERT INTO customers (username, password, customer_name, role, phone, email) VALUES
('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', '系统管理员', 'admin', '13800000000', 'admin@sportsstore.com');

-- Test user (pw: test123)
INSERT INTO customers (username, password, customer_name, role, phone, email) VALUES
('testuser', 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae', '测试用户', 'customer', '13900000001', 'test@test.com');

-- Manufacturers
INSERT INTO manufacturers (manufacturer_name, contact_person, contact_phone, address) VALUES
('红双喜体育', '张经理', '021-12345678', '上海浦东'),
('李宁体育', '李总', '010-87654321', '北京朝阳'),
('安踏体育', '王经理', '0592-1234567', '厦门思明'),
('尤尼克斯上海', '陈总监', '021-99887766', '上海静安');

-- Products (20)
INSERT INTO products (manufacturer_id, product_name, category, unit_price, stock_quantity, min_stock_threshold, sales_count, description) VALUES
(1, '红双喜标准篮球', '球类', 89.00, 200, 20, 156, '优质PU材质，标准七号篮球'),
(1, '红双喜足球', '球类', 79.00, 180, 20, 98, '高级PVC材质，五号标准足球'),
(1, '红双喜乒乓球拍套装', '球类', 45.00, 300, 30, 245, '含两拍三球'),
(1, '红双喜羽毛球拍', '球类', 65.00, 150, 15, 87, '铝合金拍框，轻量设计'),
(2, '李宁运动T恤', '服装', 99.00, 500, 50, 312, '速干面料，透气舒适'),
(2, '李宁运动短裤', '服装', 79.00, 400, 40, 201, '弹性面料，运动自由伸展'),
(2, '李宁运动套装', '服装', 259.00, 200, 20, 56, '上衣+长裤，春秋运动训练服'),
(3, '安踏跑步鞋', '鞋类', 299.00, 150, 15, 178, '缓震科技，舒适跑步体验'),
(3, '安踏训练鞋', '鞋类', 249.00, 120, 12, 89, '多功能训练鞋，耐磨防滑'),
(3, '安踏户外鞋', '鞋类', 329.00, 80, 10, 45, '防泼水设计，户外徒步首选'),
(4, '尤尼克斯网球拍', '器材', 399.00, 60, 10, 34, '碳素拍框，专业级网球拍'),
(4, '尤尼克斯羽毛球', '器材', 39.00, 600, 50, 267, '耐打训练羽毛球，12只装'),
(4, '尤尼克斯护腕', '配件', 25.00, 800, 60, 456, '吸汗护腕，运动必备配件'),
(4, '尤尼克斯运动背包', '配件', 149.00, 250, 25, 123, '大容量运动背包'),
(2, '李宁运动袜', '配件', 15.00, 1000, 100, 678, '棉质运动袜，透气吸汗，3双装'),
(2, '李宁运动水壶', '配件', 35.00, 500, 40, 234, '500ml运动水壶，食品级材质'),
(3, '安踏运动护膝', '器材', 69.00, 300, 30, 145, '加压护膝，运动防护'),
(1, '红双喜排球', '球类', 75.00, 120, 15, 67, '软式排球，适合中小学使用'),
(3, '安踏瑜伽垫', '器材', 89.00, 200, 20, 89, '防滑瑜伽垫，6mm厚度'),
(4, '尤尼克斯运动毛巾', '配件', 29.00, 600, 50, 345, '速干运动毛巾，柔软亲肤');

-- Banners
INSERT INTO banners (title, subtitle, link_type, link_value, sort_order, is_active) VALUES
('新品上市', '李宁2026春季运动系列全新发布', 'category', '服装', 1, 1),
('全场促销', '全场体育用品批发价低至8折', 'category', '配件', 2, 1),
('限时特惠', '红双喜球类商品买三送一', 'category', '球类', 3, 1);

-- Test user addresses
INSERT INTO addresses (customer_id, recipient_name, phone, address, is_default, tag) VALUES
(2, '张三', '13900000001', '北京市海淀区学院路15号', 1, '公司'),
(2, '张三', '13900000001', '北京市朝阳区幸福小区3号楼', 0, '家');

-- 为已存在的数据库添加新发票字段
SET @s1 = IF((SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='orders' AND COLUMN_NAME='invoice_address_phone')=0,
  'ALTER TABLE orders ADD COLUMN invoice_address_phone VARCHAR(255) AFTER invoice_tax_no', 'SELECT 1');
PREPARE stmt1 FROM @s1; EXECUTE stmt1; DEALLOCATE PREPARE stmt1;

SET @s2 = IF((SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='orders' AND COLUMN_NAME='invoice_bank')=0,
  'ALTER TABLE orders ADD COLUMN invoice_bank VARCHAR(255) AFTER invoice_address_phone', 'SELECT 1');
PREPARE stmt2 FROM @s2; EXECUTE stmt2; DEALLOCATE PREPARE stmt2;

-- 更新商品描述为更丰富的内容
UPDATE products SET description = CONCAT(description, '。适用场景：室内外通用。材质：优质PU皮革，柔软耐磨。尺寸：标准7号球(周长75-78cm)。保养：使用后用干布擦拭，避免长时间暴晒。') WHERE product_id = 1 AND description LIKE '优质PU材质%';
UPDATE products SET description = CONCAT(description, '。适用场景：室外草地、人造草坪。材质：高级PVC+丁基内胆。尺寸：5号标准球。保养：充气适中，存放于阴凉干燥处。') WHERE product_id = 2 AND description LIKE '高级PVC材质%';
UPDATE products SET description = CONCAT(description, '。适用场景：家庭娱乐、业余训练。包含：2支球拍、3只乒乓球。拍面材质：杨木+橡胶胶皮。保养：避免受潮，胶皮面避免接触油污。') WHERE product_id = 3 AND description LIKE '含两拍三球%';
UPDATE products SET description = CONCAT(description, '。适用场景：业余休闲、学校体育课。拍框材质：6013铝合金。重量：约100g。保养：避免撞击硬物，更换羽线可延长寿命。') WHERE product_id = 4 AND description LIKE '铝合金拍框%';
UPDATE products SET description = CONCAT(description, '。适用场景：跑步、健身、日常穿着。面料：100%聚酯纤维速干面料。特点：吸湿排汗、轻盈透气、抗皱易打理。尺码：S-3XL。颜色：黑/白/蓝/灰多色可选。') WHERE product_id = 5 AND description LIKE '速干面料%';
UPDATE products SET description = CONCAT(description, '。适用场景：运动训练、日常休闲。面料：90%棉+10%氨纶弹力面料。特点：四向弹力、宽松剪裁、腰部抽绳设计。尺码：M-3XL。') WHERE product_id = 6 AND description LIKE '弹性面料%';
