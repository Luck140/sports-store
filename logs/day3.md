# 日志 Day3：2026年6月5日 — 购物车、订单与支付模块开发

---

## 今日工作概述

Day2完成了顾客和商品模块的基础功能，今天工作量较大，主要完成了购物车、订单、支付和管理后台四个核心模块的开发。后端新增了4个路由文件，前端新增了11个页面组件。到当天结束时，系统已经可以完成从浏览商品、加入购物车、提交订单到支付确认的完整交易流程，管理员也能够在后台进行订单处理和商品管理。

---

## 一、购物车模块（Redis实现）

购物车是系统中读写频率最高的功能，因此选择使用Redis存储。以用户编号为键，购物车数据以JSON格式存储在Redis中，利用Redis的持久化机制保证数据不丢失。

```python
import redis, json
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def _cart_key(customer_id: int) -> str:
    return f"cart:{customer_id}"
```

购物车API共提供6个接口：

| 接口 | 方法 | 功能 |
|------|------|------|
| /api/cart/{id} | GET | 查看购物车，查询数据库获取商品名称和单价 |
| /api/cart/{id}/add | POST | 添加商品，已存在则增加数量 |
| /api/cart/{id}/update/{pid} | PUT | 修改数量，校验库存上限 |
| /api/cart/{id}/remove/{pid} | DELETE | 删除指定商品 |
| /api/cart/{id}/clear | DELETE | 清空购物车 |
| /api/cart/{id}/count | GET | 查询购物车商品数量（侧边栏角标用） |

购物车添加商品的实现：

```python
@router.post("/{customer_id}/add")
def add_to_cart(customer_id: int, product_id: int, quantity: int = 1, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    cart_data = redis_client.get(_cart_key(customer_id))
    cart = json.loads(cart_data) if cart_data else {"items": []}
    for item in cart["items"]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            break
    else:
        cart["items"].append({"product_id": product_id, "quantity": quantity})
    redis_client.set(_cart_key(customer_id), json.dumps(cart))
    return cart
```

购物车数据与数据库商品信息实时关联——每次查看购物车时，根据商品ID查询数据库获取最新的商品名称、单价和库存量，保证数据的准确性。

> **📷 图片1：购物车API代码截图**
> 说明：截取cart.py中购物车CRUD的完整代码，保存至日志图片/day3/购物车代码.png

---

## 二、订单模块开发

订单是系统的核心业务实体，今天完成了订单的创建、查询和状态管理功能。创建订单时，需要遍历购物车中的商品，计算总金额和运费，同时将商品名称和价格保存为快照：

```python
@router.post("/")
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    total = 0.0
    detail_records = []
    for item in data.items:
        product = db.query(Product).filter(Product.product_id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"商品 {item.product_id} 不存在")
        amount = float(product.unit_price) * item.quantity
        total += amount
        detail_records.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": float(product.unit_price),
            "total_amount": amount,
            "product_name_snapshot": product.product_name,
        })
    # 计算运费，首重1kg内包邮，超出每kg加收8元
    shipping_cost = 0
    if data.total_weight and data.total_weight > 0:
        shipping_cost = round(float(data.total_weight) * 10, 2)
        total += shipping_cost
    # 创建订单并写入数据库
    order = Order(customer_id=data.customer_id, total_amount=total, ...)
    db.add(order); db.flush()
    for d in detail_records:
        db.add(OrderDetail(order_id=order.order_id, **d))
    db.commit()
    rc.delete(f"cart:{data.customer_id}")  # 清空购物车
    return order
```

订单模块主要接口：

| 接口 | 方法 | 路径 | 功能 |
|------|------|------|------|
| 创建订单 | POST | /api/orders/ | 接收商品明细和收件信息，生成订单 |
| 查询订单 | GET | /api/orders/{id} | 查询订单基本信息 |
| 订单明细 | GET | /api/orders/{id}/details | 查询订单中的商品清单 |
| 订单时间轴 | GET | /api/orders/{id}/timeline | 按时间顺序展示订单流转 |
| 我的订单 | GET | /api/orders/customer/{id} | 按顾客查询订单列表 |
| 取消订单 | POST | /api/orders/{id}/customer-cancel | 待确认状态可取消 |
| 确认收货 | POST | /api/orders/{id}/confirm-receipt | 已发货状态可确认 |
| 催单 | POST | /api/orders/{id}/urge | 待确认或已确认可催单 |

> **📷 图片2：订单创建接口代码截图**
> 说明：截取orders.py中创建订单的完整代码，保存至日志图片/day3/订单创建代码.png

---

## 三、支付模块（策略模式）

支付模块采用策略模式设计，支持三种支付方式的灵活切换：

```python
class CreditCardPayment:
    def process(self, order_id, amount):
        return {"transaction_id": f"CC-{uuid.uuid4().hex[:12].upper()}", "status": "SUCCESS"}

class AlipayPayment:
    def process(self, order_id, amount):
        return {"transaction_id": f"ALI-{uuid.uuid4().hex[:12].upper()}", "status": "SUCCESS"}

class WechatPayment:
    def process(self, order_id, amount):
        return {"transaction_id": f"WX-{uuid.uuid4().hex[:12].upper()}", "status": "SUCCESS"}

_strategies = {
    "credit_card": CreditCardPayment(),
    "alipay": AlipayPayment(),
    "wechat": WechatPayment(),
}
```

支付接口根据传入的支付方式，从策略字典中查找对应的处理类，调用其process方法完成支付。如果新增支付方式，只需新增一个策略类并注册到_strategies字典中，无需修改原有代码。

```python
@router.post("/")
def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    strategy = _strategies.get(data.payment_method)
    if not strategy:
        raise HTTPException(status_code=400, detail=f"不支持的支付方式")
    result = strategy.process(data.order_id, data.amount)
    payment = Payment(
        order_id=data.order_id,
        payment_method=data.payment_method,
        amount=data.amount,
        transaction_id=result["transaction_id"],
        status=result["status"],
    )
    db.add(payment)
    order.payment_status = 1
    db.commit()
    return payment
```

> **📷 图片3：支付策略模式代码截图**
> 说明：截取payments.py中策略模式的完整实现，保存至日志图片/day3/支付策略代码.png

---

## 四、管理后台开发

管理后台今天完成了4个页面和对应的后端API：

| 功能 | 后端API | 前端页面 | 说明 |
|------|---------|---------|------|
| 仪表盘 | /api/admin/dashboard | Admin.vue | 统计卡片、热销排行、销售趋势 |
| 订单管理 | /api/admin/orders/* | AdminOrders.vue | 确认、发货、取消、批量操作 |
| 进货管理 | /api/admin/purchases/* | AdminPurchases.vue | 创建进货单、确认入库 |
| 报表中心 | /api/admin/reports/* | AdminReports.vue | 5类报表切换查看 |

仪表盘接口返回统计数据：

```python
@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    return {
        "total_orders": db.query(Order).count(),
        "pending_orders": pending_count,
        "low_stock_count": low_stock_count,
        "pending_todos": [
            {"label": "待确认订单", "count": pending_count},
            {"label": "库存预警商品", "count": low_stock_count},
        ],
    }
```

订单管理包含了分布式锁防止并发：

```python
@router.post("/orders/{order_id}/confirm")
def confirm_order(order_id: int, db: Session = Depends(get_db)):
    # 获取Redis分布式锁
    lock = redis_client.lock(f"lock:order:{order_id}", timeout=10)
    if not lock.acquire(blocking=True, blocking_timeout=5):
        raise HTTPException(status_code=409, detail="订单处理中")
    try:
        # 检查库存并扣减
        ...
    finally:
        lock.release()
```

> **📷 图片4：管理后台仪表盘页面截图**
> 说明：启动后浏览器打开管理后台，截取仪表盘页面，保存至日志图片/day3/管理后台仪表盘.png

---

## 五、前端新增页面

今天新增了11个前端页面组件：

| 页面 | 功能说明 |
|------|---------|
| Cart.vue | 购物车列表、结算信息、地址选择、运费计算、发票 |
| Orders.vue | 订单列表、状态筛选、支付、评价、退款申请 |
| OrderDetail.vue | 订单信息、时间轴、商品明细、付款记录 |
| ProductDetail.vue | 商品详情、收藏、评价列表 |
| Profile.vue | 基本信息、修改密码、地址管理、收藏管理 |
| Admin.vue | 仪表盘统计卡片、热销排行、销售趋势 |
| AdminOrders.vue | 订单管理表格、批量确认、批量发货 |
| AdminPurchases.vue | 进货单管理、库存预警、一键进货 |
| AdminReports.vue | 5类报表切换查看 |
| ForgotPassword.vue | 找回密码页面 |

> **📷 图片5：购物车页面截图**
> 说明：启动后浏览器打开购物车页面，截取完整布局，保存至日志图片/day3/购物车页面.png

> **📷 图片6：订单列表页面截图**
> 说明：浏览器打开订单列表页面截图，保存至日志图片/day3/订单列表页.png

---

## 六、全局样式系统

建立了base.css和main.css全局样式文件，统一了页面的设计风格。CSS变量体系中定义了品牌色、中性色、文字色、状态色和间距体系。Element Plus的组件样式也通过变量映射进行了覆盖适配。

---

## 七、遇到的问题与解决

| 编号 | 问题 | 原因 | 解决方法 |
|------|------|------|----------|
| 1 | 购物车修改数量时库存校验不一致 | 前端允许超出库存的数量输入 | 后端增加库存上限校验，前端同步绑定max值 |
| 2 | 订单创建时并发扣库存可能超卖 | 多个管理员同时确认同一订单 | 引入Redis分布式锁，确认订单前先获取锁 |
| 3 | 支付方式扩展需要修改路由代码 | 策略模式实现不完整 | 重构为策略模式，新增支付方式只需添加策略类 |

---

## 八、文件改动清单

| 文件 | 操作 | 说明 |
|------|------|------|
| backend/routers/cart.py | 新增 | 购物车CRUD（54行） |
| backend/routers/orders.py | 新增 | 订单创建/查询/状态管理（73行） |
| backend/routers/payments.py | 新增 | 策略模式三种支付（82行） |
| backend/routers/admin.py | 新增 | 管理后台所有功能（276行） |
| frontend/src/views/Cart.vue | 新增 | 购物车页面（70行） |
| frontend/src/views/Orders.vue | 新增 | 订单列表（81行） |
| frontend/src/views/OrderDetail.vue | 新增 | 订单详情（26行） |
| frontend/src/views/ProductDetail.vue | 新增 | 商品详情（34行） |
| frontend/src/views/Profile.vue | 新增 | 个人中心（51行） |
| frontend/src/views/Admin*.vue | 新增 | 4个管理后台页面（279行） |
| frontend/src/assets/base.css | 新增 | 全局设计系统变量（86行） |
| frontend/src/assets/main.css | 新增 | 全局样式（35行） |

---

## 九、下一步计划

明天将进行前端界面的全面美化和交互优化，重点改进配色方案、响应式布局和表单验证体验。
