# 日志 Day5：2026年6月11日 — 前端全面重构与功能完善

---

## 今日工作概述

Day4完成了设计系统和配色方案的建立，今天在此基础上对前端进行了全面重构，同时对后端进行了功能完善。前端方面，所有页面组件的代码都进行了大幅度重写，涉及12个类别共计49项改进。后端方面，新增了横幅管理、评价系统和通知推送三个模块，并对现有模块进行了功能增强。数据库从9张表扩展为15张表，新增了地址、评价、收藏、横幅、通知和操作日志表。到当天结束时，系统的功能完整度和用户体验都有了显著提升。

---

## 一、购物车页面重构

购物车页面是此次重构的重点。原来的购物车只有简单的商品ID和数量显示，现在重构为两个清晰的区域：

上半部分为商品列表，每行展示商品名称、单价、数量调节器、小计金额和删除按钮。数量修改后实时刷新小计和总金额，数量上限绑定到商品当前库存。

```html
<el-card v-if="cart.items && cart.items.length">
  <el-table :data="cart.items">
    <el-table-column label="商品" min-width="160">
      <template #default="scope">{{ scope.row.product_name }}</template>
    </el-table-column>
    <el-table-column label="数量" width="150">
      <template #default="scope">
        <el-input-number v-model="scope.row.quantity" :min="1"
          :max="scope.row.stock_quantity || 999" size="small"
          @change="updateQty(scope.row)" controls-position="right" />
      </template>
    </el-table-column>
    <el-table-column label="小计" width="110">
      <template #default="scope">
        <span style="color:var(--color-accent);font-weight:600">¥{{ scope.row.subtotal }}</span>
      </template>
    </el-table-column>
    <el-table-column label="操作" width="80">
      <template #default="scope">
        <el-popconfirm title="确认删除该商品？" @confirm="remove(scope.row.product_id)">
          <template #reference><el-button type="danger" link size="small">删除</el-button></template>
        </el-popconfirm>
      </template>
    </el-table-column>
  </el-table>
</el-card>
```

下半部分为结算信息区域，包含收货地址选择、运费计算和发票信息。运费计算使用computed属性实现实时预览：

```javascript
const shippingCost = computed(() => {
  const w = parseFloat(info.value.total_weight) || 0
  if (w <= 1) return 0
  return Math.round((w - 1) * 8 * 100) / 100
})
const grandTotal = computed(() =>
  Math.round((cart.value.total_price + shippingCost.value) * 100) / 100
)
```

地址选择功能支持从已保存地址中选取，选择后自动填充收件人、电话和地址。发票支持不需要、普通发票和增值税专用发票三种选项，选择后动态显示发票抬头和税号输入框。

新增了货物重量自动估算功能：

```javascript
watch(() => cart.value.item_count, (n) => {
  if (n > 0 && !info.value.total_weight) {
    info.value.total_weight = Math.round(n * 0.5 * 10) / 10
  }
})
```

> **📷 图片1：购物车页面重构后截图**
> 说明：启动后浏览器打开购物车页面，截取完整布局，保存至日志图片/day5/购物车页面.png

---

## 二、侧边栏导航重构

侧边栏导航重构为手风琴展开模式。原来的实现使用了Element Plus的el-sub-menu组件，存在页面刷新后菜单收起的问题。改用自定义HTML元素配合Vue Router的router-link组件，通过reactive对象控制展开状态：

```html
<template v-if="!userStore.isAdmin">
  <router-link to="/products" class="sb-item">商品列表</router-link>
  <router-link to="/cart" class="sb-item">购物车</router-link>

  <div class="sb-group">
    <div class="sb-item sb-parent" @click="toggleMenu('orders')"
      :class="{ 'sb-expanded': openMenus.orders }">
      我的订单 <span class="sb-arrow">{{ openMenus.orders ? '▾' : '▸' }}</span>
    </div>
    <div v-show="openMenus.orders" class="sb-sub">
      <router-link to="/orders" class="sb-sub-item">全部订单</router-link>
      <router-link to="/orders?status=PENDING" class="sb-sub-item">待付款</router-link>
      <router-link to="/orders?status=SHIPPED" class="sb-sub-item">待收货</router-link>
    </div>
  </div>
</template>
```

子菜单展开状态通过reactive对象管理，路由变化时自动展开对应菜单：

```javascript
const openMenus = reactive({ orders: false, profile: false })
const toggleMenu = (key) => { openMenus[key] = !openMenus[key] }

watch(route, () => {
  if (route.path.startsWith('/orders')) openMenus.orders = true
  if (route.path.startsWith('/profile')) openMenus.profile = true
})
```

> **📷 图片2：侧边栏导航展开效果截图**
> 说明：登录后截取侧边栏展开子菜单效果，保存至日志图片/day5/侧边栏导航.png

---

## 三、订单详情页重构

订单详情页重构为四个清晰的信息区块：

```html
<!-- 区块1：订单基本信息 -->
<el-card>
  <el-descriptions :column="2" border>
    <el-descriptions-item label="订单号">#{{ order.order_id }}</el-descriptions-item>
    <el-descriptions-item label="订单状态">
      <el-tag :type="tagType(order.status)">{{ statusMap[order.status] }}</el-tag>
    </el-descriptions-item>
    <el-descriptions-item label="实付金额">
      <b style="color:var(--color-accent)">¥{{ order.total_amount }}</b>
    </el-descriptions-item>
    <el-descriptions-item label="收件人">{{ order.recipient_name }}</el-descriptions-item>
  </el-descriptions>
</el-card>

<!-- 区块2：订单时间轴 -->
<el-card>
  <el-timeline>
    <el-timeline-item v-for="t in timeline" :key="t.title"
      :timestamp="formatTime(t.time)" placement="top">
      <h4>{{ t.title }}</h4>
      <p>{{ t.desc }}</p>
    </el-timeline-item>
  </el-timeline>
</el-card>

<!-- 区块3：商品明细 -->
<el-card>
  <el-table :data="details">
    <el-table-column prop="product_name" label="商品名称" />
    <el-table-column label="单价"><template #default="{row}">¥{{ row.unit_price }}</template></el-table-column>
    <el-table-column prop="quantity" label="数量" />
    <el-table-column label="金额"><template #default="{row}">¥{{ row.total_amount }}</template></el-table-column>
  </el-table>
</el-card>

<!-- 区块4：付款记录 -->
<el-card v-if="payments.length">
  <el-table :data="payments">
    <el-table-column prop="payment_method" label="支付方式" />
    <el-table-column label="金额"><template #default="{row}">¥{{ row.amount }}</template></el-table-column>
    <el-table-column prop="status" label="状态" />
    <el-table-column prop="transaction_id" label="流水号" />
  </el-table>
</el-card>
```

> **📷 图片3：订单详情页四区块截图**
> 说明：点击某个订单进入详情页，截取完整页面，保存至日志图片/day5/订单详情页.png

---

## 四、个人中心页面重构

个人中心页面重构为四个标签页切换，数据按需加载：

```javascript
const loadProfile = async () => { ... }
const loadAddresses = async () => { ... }
const loadFavorites = async () => { ... }

const switchTab = (newTab) => {
  tab.value = newTab
  if (newTab === 'addresses' && !addresses.value.length) loadAddresses()
  if (newTab === 'favorites' && !favorites.value.length) loadFavorites()
}
```

基本信息标签支持头像上传，转为Base64存储并限制文件大小：

```javascript
const onFileChange = (e) => {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.warning('图片不能超过2MB')
    return
  }
  const reader = new FileReader()
  reader.onload = (ev) => { avatar.value = ev.target.result }
  reader.readAsDataURL(file)
}
```

> **📷 图片4：个人中心页面截图**
> 说明：登录后进入个人中心，截取基本信息标签页，保存至日志图片/day5/个人中心页面.png

---

## 五、后端新增模块

新增了三个后端模块：

横幅模块支持首页轮播图的灵活配置：

```python
@router.get("/", response_model=list[BannerResponse])
def get_active_banners(db: Session = Depends(get_db)):
    return db.query(Banner).filter(Banner.is_active == 1).order_by(Banner.sort_order).all()
```

评价模块实现了商品评价功能：

```python
@router.post("/")
def create_review(data: ReviewCreate, db: Session = Depends(get_db)):
    if data.rating < 1 or data.rating > 5:
        raise HTTPException(status_code=400, detail="评分范围为1-5")
    order = db.query(Order).filter(Order.order_id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    review = Review(order_id=data.order_id, product_id=data.product_id,
                    customer_id=data.customer_id, rating=data.rating, content=data.content)
    db.add(review)
    db.commit()
    return review
```

通知模块实现了站内通知功能，在订单状态变更时自动发送通知：

```python
@router.get("/{customer_id}")
def list_notifications(customer_id: int, page: int, page_size: int, db: Session = Depends(get_db)):
    q = db.query(Notification).filter(Notification.customer_id == customer_id)
    total = q.count()
    items = q.offset((page-1)*page_size).limit(page_size).all()
    return {"items": items, "total": total}
```

---

## 六、现有模块增强

顾客模块新增了地址管理和收藏管理功能：

```python
@router.get("/{customer_id}/addresses")
def list_addresses(customer_id: int, db: Session = Depends(get_db)):
    return db.query(Address).filter(Address.customer_id == customer_id).all()

@router.post("/{customer_id}/favorites/{product_id}")
def add_favorite(customer_id: int, product_id: int, db: Session = Depends(get_db)):
    exist = db.query(Favorite).filter(Favorite.customer_id == customer_id,
                                       Favorite.product_id == product_id).first()
    if exist:
        raise HTTPException(status_code=400, detail="已收藏过该商品")
    db.add(Favorite(customer_id=customer_id, product_id=product_id))
    db.commit()
    return {"message": "收藏成功"}
```

商品模块增加了分类查询和热销商品接口，列表查询新增了分类筛选、价格区间过滤和排序功能。支付模块增加了退款申请、退款审核和拒绝退款功能。管理后台增加了销售图表、热销商品排行、顾客详情和操作日志查询接口。

---

## 七、遇到的问题与解决

| 编号 | 问题 | 原因 | 解决方法 |
|------|------|------|----------|
| 1 | 侧边栏子菜单刷新后收起 | el-sub-menu组件状态不持久化 | 使用reactive+watch管理展开状态 |
| 2 | 购物车数量修改与库存不同步 | 前端未绑定库存上限 | input-number的max属性绑定当前库存量 |
| 3 | 个人中心Tab切换数据重复请求 | 页面加载时一次性请求所有接口 | 改为按需加载 |
| 4 | 评价接口未验证用户身份 | 未校验评价人是否与订单关联 | 创建评价时验证订单归属 |

---

## 八、文件改动清单

| 文件 | 操作 | 说明 |
|------|------|------|
| frontend/src/views/Cart.vue | 重写 | 购物车页面重构（+80行） |
| frontend/src/views/Orders.vue | 重写 | 订单列表重构（+159行） |
| frontend/src/views/OrderDetail.vue | 重写 | 订单详情四区块（+77行） |
| frontend/src/views/Profile.vue | 重写 | 个人中心四标签（+142行） |
| frontend/src/views/Products.vue | 重构 | 商品列表优化（+205行） |
| frontend/src/App.vue | 重写 | 侧边栏手风琴导航（+117行） |
| backend/routers/banners.py | 新增 | 横幅管理模块 |
| backend/routers/reviews.py | 新增 | 评价管理模块 |
| backend/routers/notifications.py | 新增 | 通知推送模块 |
| backend/routers/customers.py | 修改 | 新增地址和收藏接口（+136行） |
| backend/routers/payments.py | 修改 | 新增退款功能（+65行） |
| backend/models.py | 修改 | 新增6个模型（+76行） |
| backend/schemas.py | 修改 | 新增数据模型（+93行） |
| database/init.sql | 修改 | 15张表完整建表脚本 |

---

## 九、下一步计划

明天将进行系统的细节优化和Bug修复，重点改进侧边栏交互、个人中心加载体验、购物车校验逻辑和订单时间轴节点完善。
