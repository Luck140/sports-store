# 日志 Day2：2026年6月4日 — 后端数据模型与核心API开发

---

## 今日工作概述

Day1完成项目骨架搭建后，今天开始正式的功能开发。主要完成了三部分工作：一是完善了SQLAlchemy ORM数据模型，将Day1设计的9张数据库表映射为Python模型类；二是开发了顾客模块和商品模块的后端API接口，实现了注册、登录、用户信息管理和商品查询功能；三是搭建了前端基础页面，包括首页、登录注册页和商品列表页，实现了前后端联调。到当天结束时，系统已经可以完成用户注册登录和商品浏览的完整流程。

---

## 一、后端ORM模型实现

在Day1数据库设计的基础上，使用SQLAlchemy 2.0完成了9张表的ORM模型映射。每个模型类对应一张数据库表，通过Column类型定义字段，ForeignKey定义外键关系。

以Product模型为例：

```python
class Product(Base):
    __tablename__ = "products"
    product_id = Column(BigInteger, primary_key=True, autoincrement=True)
    manufacturer_id = Column(BigInteger, ForeignKey("manufacturers.manufacturer_id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    min_stock_threshold = Column(Integer, nullable=False, default=10)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

Customer模型涉及密码安全，password字段存储SHA256哈希值，不保存明文。Order和OrderDetail模型间通过外键关联，order_details表中保存下单时的unit_price快照，保证历史订单数据的准确性。

同时完成了database.py数据库连接配置：

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://root:Mn2024082132@localhost:3306/sports_store?charset=utf8mb4"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

> **📷 图片1：models.py完整代码截图**
> 说明：截取models.py中9个ORM模型类的完整定义，保存至日志图片/day2/models代码.png

---

## 二、顾客模块API开发

顾客模块是整个系统的用户基础，今天完成了4个核心接口：

| 接口 | 方法 | 路径 | 功能说明 |
|------|------|------|----------|
| 用户注册 | POST | /api/customers/register | 接收用户信息，密码经SHA256哈希后存储 |
| 用户登录 | POST | /api/customers/login | 验证用户名和密码，返回身份信息 |
| 获取信息 | GET | /api/customers/{id} | 根据ID查询用户详细信息 |
| 修改信息 | PUT | /api/customers/{id} | 修改姓名、电话、邮箱等资料 |

注册接口实现了用户名唯一性校验，若用户名已存在则返回400错误。登录接口验证密码哈希值是否匹配。以下为注册和登录接口的实现代码：

```python
@router.post("/register", response_model=CustomerResponse)
def register(data: CustomerCreate, db: Session = Depends(get_db)):
    exist = db.query(Customer).filter(Customer.username == data.username).first()
    if exist:
        raise HTTPException(status_code=400, detail="用户名已存在")
    customer = Customer(
        username=data.username,
        password=hash_password(data.password),
        customer_name=data.customer_name,
        address=data.address,
        phone=data.phone,
        email=data.email,
        role="customer",
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.username == username).first()
    if not customer or customer.password != hash_password(password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return {
        "customer_id": customer.customer_id,
        "customer_name": customer.customer_name,
        "role": customer.role,
        "message": "登录成功",
    }
```

> **📷 图片2：customers.py代码截图**
> 说明：截取routers/customers.py中注册和登录接口代码，保存至日志图片/day2/customers代码.png

> **📷 图片3：登录API测试截图**
> 说明：启动后端后，在CMD中执行curl测试注册和登录接口，截取返回JSON结果，保存至日志图片/day2/登录测试.png

---

## 三、商品模块API开发

商品查询是系统的核心功能，今天完成了3个接口：

| 接口 | 方法 | 路径 | 功能说明 |
|------|------|------|----------|
| 商品列表 | GET | /api/products/ | 返回所有商品列表 |
| 商品详情 | GET | /api/products/{id} | 查询单个商品，包含厂家名称 |
| 关键词搜索 | GET | /api/products/search/ | 按商品名称模糊搜索 |

商品列表接口的实现：

```python
@router.get("/", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()
```

商品详情接口关联查询厂家信息：

```python
@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    mfr = db.query(Manufacturer).filter(
        Manufacturer.manufacturer_id == product.manufacturer_id
    ).first()
    return ProductDetailResponse(
        product_id=product.product_id,
        manufacturer_name=mfr.manufacturer_name if mfr else "",
        product_name=product.product_name,
        unit_price=float(product.unit_price),
        stock_quantity=product.stock_quantity,
        description=product.description,
    )
```

> **📷 图片4：商品列表API截图**
> 说明：启动后端后，在CMD中执行curl请求商品列表接口，截取返回JSON数据，保存至日志图片/day2/商品列表API.png

---

## 四、主程序与路由注册

main.py中集成了CORS中间件配置和所有路由模块的注册：

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Sports Store", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import customers, products, cart, orders, admin, payments
app.include_router(customers.router)
app.include_router(products.router)
```

---

## 五、前端基础页面搭建

后端API开发完成后，同步搭建了前端基础页面。使用Vue 3的Composition API开发，主要包含以下页面：

首页展示了系统名称和业务描述，包含"立即选购"和"免费注册"两个操作按钮及四个统计指标。页面向下展示热销商品区域，通过axios从后端API获取数据。登录页面包含用户名和密码输入框，支持回车提交，按钮显示加载状态防止重复提交，错误信息以红色背景框展示。注册页面包含五个字段的输入和验证。商品列表页以网格形式展示商品，每行四个，每个商品卡片展示图标、名称、品类标签、销量、价格和库存状态。

用户登录状态通过Pinia状态管理存储在localStorage中，页面刷新后自动恢复登录状态。

> **📷 图片5：前端登录页面截图**
> 说明：启动前后端后，浏览器打开登录页面截图，保存至日志图片/day2/登录页面.png

> **📷 图片6：前端商品列表页截图**
> 说明：浏览器打开商品列表页面截图，保存至日志图片/day2/商品列表页.png

---

## 六、遇到的问题与解决

| 编号 | 问题 | 原因 | 解决方法 |
|------|------|------|----------|
| 1 | 商品列表接口未分页 | 初始实现直接返回全部数据 | Day2阶段暂未处理，后续迭代完善分页功能 |
| 2 | 登录返回信息缺少username | CustomerResponse模型未包含username字段 | 在返回体中直接拼接username字段 |

---

## 七、文件改动清单

| 文件 | 操作 | 说明 |
|------|------|------|
| backend/models.py | 新增 | 9个ORM模型定义（117行） |
| backend/database.py | 新增 | 数据库连接配置（18行） |
| backend/routers/customers.py | 新增 | 顾客注册/登录/信息管理API（85行） |
| backend/routers/products.py | 新增 | 商品列表/详情/搜索API（35行） |
| backend/schemas.py | 新增 | Pydantic请求响应模型（165行） |
| backend/main.py | 修改 | 增加路由注册，+37行 |
| frontend/src/App.vue | 新增 | 主布局组件（70行） |
| frontend/src/views/Home.vue | 新增 | 首页（39行） |
| frontend/src/views/Login.vue | 新增 | 登录页（40行） |
| frontend/src/views/Register.vue | 新增 | 注册页（50行） |
| frontend/src/views/Products.vue | 新增 | 商品列表页（102行） |

---

## 八、下一步计划

明天将继续开发购物车模块和订单模块，实现商品的添加购物车、数量修改和订单提交流程。
