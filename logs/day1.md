# 日志 Day1：2026年6月1日 — 项目初始化与数据库设计

---

## 今日工作概述

今天正式启动体育用品批发销售系统 SportsStore 的开发。主要完成了项目的环境搭建、技术选型、数据库设计和项目骨架搭建三项工作。到当天结束时，已经确定了前后端分离的技术架构，完成了 9 张数据库表的设计和建表脚本编写，并成功配置了前后端开发环境，后端 FastAPI 服务可以正常启动，前端 Vue 3 项目能够正常编译运行。

---

## 一、技术选型

系统采用前后端分离架构，前端运行在 5173 端口，后端运行在 8000 端口，通过 CORS 中间件实现跨域通信。

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 前端框架 | Vue 3 | 3.5+ | 用户界面构建 |
| 构建工具 | Vite | 6.x | 前端项目构建与热更新 |
| UI 组件库 | Element Plus | 2.9+ | 企业级 UI 组件 |
| 状态管理 | Pinia | 3.x | 前端状态管理 |
| 后端框架 | FastAPI | 0.136+ | RESTful API 开发 |
| ORM | SQLAlchemy | 2.0+ | 数据库对象关系映射 |
| 数据库 | MySQL | 8.0+ | 关系型数据存储 |
| 缓存 | Redis | 7.x | 购物车数据存储 |
| HTTP 客户端 | Axios | 1.7+ | 前后端数据通信 |

---

## 二、项目结构

项目按功能模块划分为四个目录：

```
📁 sports-store/
├── 📁 database/              # 数据库初始化脚本
│   └── 📄 init.sql          # 建表脚本（9张表）
├── 📁 backend/               # FastAPI 后端
│   ├── 📄 main.py           # 应用入口
│   ├── 📄 database.py       # 数据库连接
│   ├── 📄 models.py         # ORM 模型
│   └── 📄 requirements.txt  # Python 依赖
├── 📁 frontend/              # Vue 3 前端
│   ├── 📄 index.html
│   ├── 📄 package.json
│   └── 📁 src/
└── 📁 logs/                  # 开发日志
```

> **📷 图片1：项目目录结构截图**
> 说明：使用 `tree` 命令或 VS Code 截取项目目录结构图，保存至 `日志图片/day1/项目目录结构.png`

---

## 三、数据库设计

数据模型设计是今天的核心工作。通过对系统业务需求的分析，共识别出 9 个核心实体，设计了 9 张数据库表。

### 3.1 实体关系设计

系统中各实体的关系如下：

- **顾客** 与 **订单**：一对多关系，一个顾客可以创建多个订单
- **订单** 与 **订单明细**：一对多关系，一个订单包含多条商品记录
- **商品** 与 **厂家**：多对一关系，多个商品可属于同一厂家
- **订单** 与 **支付记录**：一对多关系，一个订单可以有多次支付
- **商品** 与 **库存变动记录**：一对多关系，每次库存变化都有记录

### 3.2 核心表结构

以顾客表和订单表为例展示数据库表结构：

**customers（顾客表）：**

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| customer_id | BIGINT | PK, AUTO_INCREMENT | 顾客编号 |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| password | VARCHAR(255) | NOT NULL | 密码（SHA256 哈希） |
| customer_name | VARCHAR(50) | NOT NULL | 真实姓名 |
| phone | VARCHAR(255) | | 联系电话 |
| email | VARCHAR(100) | | 电子邮箱 |
| role | VARCHAR(20) | DEFAULT 'customer' | 角色 |
| avatar | TEXT | | 头像（Base64） |
| created_at | DATETIME | DEFAULT NOW() | 注册时间 |

```sql
CREATE TABLE customers (
  customer_id   BIGINT NOT NULL AUTO_INCREMENT,
  username      VARCHAR(50) NOT NULL UNIQUE,
  password      VARCHAR(255) NOT NULL,
  customer_name VARCHAR(50) NOT NULL,
  phone         VARCHAR(255),
  email         VARCHAR(100),
  role          VARCHAR(20) NOT NULL DEFAULT 'customer',
  avatar        TEXT,
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

> **📷 图片2：数据库建表SQL代码截图**
> 说明：截取 init.sql 中 customers 表的建表语句，保存至 `日志图片/day1/建表SQL截图.png`

**orders（订单表）：**

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| order_id | BIGINT | PK, AUTO_INCREMENT | 订单号 |
| customer_id | BIGINT | FK → customers | 所属顾客 |
| total_amount | DECIMAL(12,2) | NOT NULL | 订单总金额 |
| status | VARCHAR(20) | DEFAULT 'PENDING' | 订单状态 |
| payment_status | SMALLINT | DEFAULT 0 | 付款状态 |
| recipient_name | VARCHAR(50) | | 收件人 |
| recipient_address | VARCHAR(255) | | 收件地址 |
| shipping_cost | DECIMAL(8,2) | DEFAULT 0.00 | 运费 |

> **📷 图片3：MySQL 中执行 SHOW TABLES 的结果截图**
> 说明：在 MySQL 命令行执行 `USE sports_store; SHOW TABLES;` 后截图，保存至 `日志图片/day1/数据库表清单.png`

### 3.3 完整数据表清单

| 编号 | 表名 | 用途 | 核心字段数 |
|------|------|------|-----------|
| 1 | customers | 顾客信息 | 9 |
| 2 | manufacturers | 生产厂家 | 4 |
| 3 | products | 商品库存 | 8 |
| 4 | orders | 订单主表 | 12 |
| 5 | order_details | 订单明细 | 7 |
| 6 | payments | 支付记录 | 6 |
| 7 | stock_records | 库存变动 | 5 |
| 8 | purchase_orders | 进货单 | 4 |
| 9 | purchase_details | 进货明细 | 5 |

### 3.4 关键设计决策

**订单金额快照：** 订单明细表中单独保存 `product_name_snapshot` 和 `unit_price` 字段，作为下单时的商品信息副本。即使后续商品价格修改，历史订单的数据也不会受到影响。

**订单状态机：** 订单状态采用字符串字段存储，定义如下状态流转路径：

```
PENDING(待确认) → CONFIRMED(已确认) → SHIPPED(已发货) → COMPLETED(已完成)
                     ↕                      ↕
            CANCELLED(已取消)      OUT_OF_STOCK(缺货)
```

**库存扣减时机：** 选择在管理员确认订单时扣减库存，而非用户下单时。这样可以避免未付款订单占用库存的问题。取消已确认订单时自动回补库存，每次变动都记录到 stock_records 表。

---

## 四、ORM 模型代码

后端使用 SQLAlchemy 2.0 作为 ORM 框架，以下以 Product 模型为例：

```python
class Product(Base):
    __tablename__ = "products"
    product_id = Column(BigInteger, primary_key=True, autoincrement=True)
    manufacturer_id = Column(BigInteger, ForeignKey("manufacturers.manufacturer_id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    category = Column(String(50), default="未分类")
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    min_stock_threshold = Column(Integer, nullable=False, default=10)
    sales_count = Column(Integer, nullable=False, default=0)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

> **📷 图片4：models.py 中核心模型代码截图**
> 说明：截取 models.py 中 Product 或 Order 模型的完整定义，保存至 `日志图片/day1/ORM模型代码.png`

---

## 五、后端 API 路由结构

后端采用 FastAPI 的 APIRouter 机制按功能模块组织路由，方便后续扩展：

```python
from routers import customers, products, cart, orders, admin, payments, reviews, banners, notifications
app.include_router(customers.router)    # 顾客模块
app.include_router(products.router)     # 商品模块
app.include_router(cart.router)         # 购物车模块
app.include_router(orders.router)       # 订单模块
app.include_router(admin.router)        # 管理后台
app.include_router(payments.router)     # 支付模块
app.include_router(reviews.router)      # 评价模块
app.include_router(banners.router)      # 横幅模块
app.include_router(notifications.router) # 通知模块
```

---

## 六、开发环境搭建

1. 安装 Python 3.13.0 并创建虚拟环境：`python -m venv venv`
2. 安装后端依赖：`pip install fastapi uvicorn sqlalchemy pymysql redis`
3. 安装 MySQL 8.0，创建数据库 `sports_store`，执行 `init.sql` 建表
4. 安装 Redis 7.0 并启动服务
5. 安装 Node.js，初始化 Vue 3 项目：`npm create vite@latest`
6. 安装前端依赖：`npm install vue-router pinia element-plus axios`

> **📷 图片5：后端服务启动成功的控制台截图**
> 说明：执行 `python main.py` 后，终端显示 `Uvicorn running on http://0.0.0.0:8000`，保存至 `日志图片/day1/后端启动成功.png`
>
> **📷 图片6：数据库初始化成功截图**
> 说明：执行 `init.sql` 后，在 MySQL 中查询数据确认插入成功，保存至 `日志图片/day1/数据库初始化成功.png`

---

## 七、遇到的问题与解决

| # | 问题 | 原因 | 解决方法 |
|---|------|------|----------|
| 1 | MySQL 中文乱码 | 数据库默认编码 latin1 不支持中文 | 建库时指定 `CHARACTER SET utf8mb4`，连接 URL 添加 `charset=utf8mb4` |
| 2 | 前端请求后端报 CORS 错误 | 前后端端口不同，浏览器同源策略阻止 | 后端添加 `CORSMiddleware`，配置 `allow_origins` |

---

## 八、文件改动清单

| 文件 | 操作 | 说明 |
|------|------|------|
| database/init.sql | 新增 | 9 张表建表脚本 + 初始数据（约 134 行） |
| backend/main.py | 新增 | 应用入口、CORS 配置、路由注册 |
| backend/database.py | 新增 | 数据库连接配置（SQLAlchemy 引擎） |
| backend/models.py | 新增 | 9 个 ORM 模型定义 |
| backend/requirements.txt | 新增 | Python 项目依赖列表 |
| frontend/ | 初始化 | Vite 创建的 Vue 3 项目骨架 |

---

## 九、下一步计划

项目骨架搭建完成后，后续按顾客管理 → 商品管理 → 购物车 → 订单 → 支付的顺序，逐步完成后端 API 开发，并同步实现前端页面功能。
