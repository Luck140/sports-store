# 日志 Day6：2026年6月12日 — 细节优化与Bug修复

---

## 今日工作概述

前五天完成了系统的核心功能开发和前端界面设计，今天对系统进行了深入的技术细节优化和前端体验打磨。主要集中在侧边栏交互改进、个人中心Tab页面加载体验优化、购物车数量修改的库存校验逻辑、订单时间轴节点的完善、管理后台批量操作的数据一致性处理以及部分后端接口的性能优化。这些改进虽然每个都不算大，但涉及面较广，从顾客端到管理端都有覆盖，整体上让系统体验更加流畅和完整。

---

## 一、侧边栏交互优化

**1. 个人中心子菜单展开逻辑**

之前侧边栏中个人中心使用了Element Plus的el-sub-menu组件来实现子菜单展开。但在测试中发现当用户点击个人中心后跳转到Profile页面时，如果页面刷新或者用户通过浏览器地址栏直接访问Profile页面，子菜单会默认收起，用户无法直观地看到当前处于个人中心的哪个子模块。

修改后在App.vue中通过路由判断动态展开对应的子菜单：

```javascript
watch(route, () => {
  const p = route.path
  if (p.startsWith('/orders')) openMenus.orders = true
  if (p.startsWith('/profile')) openMenus.profile = true
}, { immediate: true })
```

**2. 购物车角标动态刷新**

购物车菜单项旁边的数量角标之前只在页面首次加载时获取数据。但如果用户在商品详情页加入购物车后通过浏览器的返回按钮回到商品列表，或者在其他页面操作了购物车，角标不会自动更新。

修改后在路由变化时增加了购物车数量的重新获取逻辑：

```javascript
watch(route, () => {
  fetchCartCount()
}, { immediate: true })

async function fetchCartCount() {
  if (!userStore.user || userStore.isAdmin) return
  try {
    const r = await axios.get(`/api/cart/${userStore.user.customer_id}/count`)
    cartCount.value = r.data.count || 0
  } catch {}
}
```

> **📷 图片1：侧边栏子菜单展开效果截图**
> 说明：登录后展开"我的订单"子菜单，截取侧边栏完整效果，保存至日志图片/day6/侧边栏子菜单.png

---

## 二、个人中心页面改进

**1. Tab切换时数据的按需加载**

之前个人中心页面在加载时会一次性请求基本信息、收货地址和收藏列表三个接口的数据。如果用户只是想要修改密码，根本不需要加载地址和收藏数据，这样会造成不必要的网络请求和数据库查询。

修改后改为按需加载模式：

```javascript
onMounted(() => { loadProfile() })  // 默认只加载基本信息

const switchTab = (tab) => {
  currentTab.value = tab
  if (tab === 'addresses' && addresses.value.length === 0) loadAddresses()
  if (tab === 'favorites' && favorites.value.length === 0) loadFavorites()
}
```

这个改动减少了首屏加载时间，也减轻了后端数据库的查询压力。

**2. 头像上传的图片格式校验**

之前头像上传功能没有对文件类型进行限制，用户可能选择非图片格式的文件导致显示异常。修改后在文件选择回调中增加了对文件类型的校验：

```javascript
const onFileChange = (e) => {
  const file = e.target.files[0]
  if (!file) return
  const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!validTypes.includes(file.type)) {
    ElMessage.warning('请选择图片格式的文件')
    return
  }
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.warning('图片不能超过2MB')
    return
  }
  const reader = new FileReader()
  reader.onload = (ev) => { avatar.value = ev.target.result }
  reader.readAsDataURL(file)
}
```

**3. 修改密码后的状态重置**

用户修改密码成功后，之前只是显示成功提示，但表单中已经填写的密码字段没有被清空。修改后在密码修改成功后自动清空三个密码输入框：

```javascript
const changePwd = async () => {
  try {
    await axios.post(`/api/customers/.../change-password`, data)
    pwdMsg.value = '密码修改成功！'
    pwdForm.value = { old_password: '', new_password: '', confirm: '' }
  } catch (e) {
    pwdMsg.value = e.response?.data?.detail || '修改失败'
  }
}
```

---

## 三、购物车功能完善

**1. 数量修改时的库存校验**

购物车中修改商品数量时，之前没有对库存上限进行严格校验。修改后在数量修改的前端逻辑中增加了实时校验，数量输入框的最大值绑定到该商品当前库存量：

```html
<el-input-number v-model="row.quantity" :min="1"
  :max="row.stock_quantity" size="small"
  @change="(v) => updateQty(row.product_id, v)" />
```

**2. 地址选择后的字段锁定**

用户从已有地址列表中选择了地址后，收件人、联系电话和地址三个字段会自动填充。修改后当用户选择了已有地址时，这些字段变为只读状态并显示灰色背景，明确告知用户这些字段来自已保存的地址。如果用户需要修改，可以先清空地址选择再手动填写。

**3. 运费计算的前端实时预览**

运费计算规则为首重1kg内包邮、超出每kg加收8元。之前在结算区只显示了最终的运费金额。修改后在运费区域增加了明细展示，让费用构成更加透明：

```html
<el-form-item label="运费规则">
  <span>首重1kg内<strong>包邮</strong>，超出后每1kg加收 ¥8</span>
  <span>预计运费：<strong>¥{{ shippingCost }}</strong></span>
</el-form-item>
```

> **📷 图片2：购物车运费明细截图**
> 说明：购物车加入商品后，截取底部运费计算明细区域，保存至日志图片/day6/购物车运费明细.png

---

## 四、订单相关功能优化

**1. 订单时间轴节点的完善**

之前的订单时间轴在某些状态下缺少关键节点。修改后完善了时间轴的节点逻辑，根据订单状态和操作记录动态展示对应的流转节点：

```python
timeline = []
timeline.append({"time": o.order_date, "icon": "cart", "title": "订单创建", "desc": "订单已提交"})

if o.status in ("CONFIRMED", "SHIPPED", "COMPLETED"):
    timeline.append({"time": o.updated_at, "icon": "check", "title": "已确认"})

if o.status in ("SHIPPED", "COMPLETED"):
    timeline.append({"time": o.shipping_date, "icon": "truck", "title": "已发货"})

if o.status == "COMPLETED":
    timeline.append({"time": o.updated_at, "icon": "home", "title": "已收货"})

if o.status == "CANCELLED":
    timeline.append({"time": o.updated_at, "icon": "close", "title": "已取消"})
```

**2. 订单列表筛选条件的持久化**

用户在订单列表中选择了状态筛选后，如果点击进入某个订单的详情页再返回列表，之前设置的筛选条件会丢失。修改后在URL参数中保留了筛选条件：

```javascript
watch(() => route.query.status, (newStatus) => {
  statusFilter.value = newStatus || ''
  page.value = 1
  load()
})
```

> **📷 图片3：订单时间轴完善后截图**
> 说明：进入订单详情页，截取时间轴部分展示完整节点流转，保存至日志图片/day6/订单时间轴.png

---

## 五、后端接口优化

**1. 商品列表接口的查询性能优化**

商品列表接口支持分类筛选、价格区间过滤、排序和分页，SQL查询的条件组合比较复杂。修改后将统计查询和分页查询中的公共筛选条件提取为独立的查询构建函数，避免了重复的条件拼接逻辑。

**2. 订单创建接口的事务处理**

创建订单时需要同时写入订单主表和订单明细表，还需要清空购物车缓存。修改后将缓存删除操作放在数据库事务提交之后执行：

```python
db.commit()  # 先提交数据库事务
rc.delete(f"cart:{data.customer_id}")  # 再删除缓存，避免数据不一致
```

**3. 管理后台统计查询的日期范围优化**

仪表盘的销售趋势统计之前查询的是全部历史数据。修改后限制为只查询最近三十天的数据，通过日期范围过滤减少了扫描的数据量。

---

## 六、遇到的问题与解决

| 编号 | 问题 | 原因 | 解决方法 |
|------|------|------|----------|
| 1 | 侧边栏子菜单页面刷新后收起 | 路由初始化时未自动展开 | 使用watch监听路由变化自动展开 |
| 2 | 购物车角标不更新 | 仅在页面加载时获取一次 | 路由变化时重新获取购物车数量 |
| 3 | 订单创建成功后购物车未清空 | 缓存删除在事务提交前 | 将缓存删除放到事务提交之后 |

---

## 七、文件改动清单

| 文件 | 操作 | 说明 |
|------|------|------|
| frontend/src/App.vue | 修改 | 侧边栏交互逻辑、购物车角标动态刷新 |
| frontend/src/views/Profile.vue | 修改 | Tab按需加载、头像格式校验、密码重置 |
| frontend/src/views/Cart.vue | 修改 | 库存校验、地址锁定、运费明细 |
| frontend/src/views/Orders.vue | 修改 | 筛选条件持久化 |
| frontend/src/views/OrderDetail.vue | 修改 | 时间轴节点完善 |
| backend/routers/orders.py | 修改 | 订单创建缓存处理优化 |

---

## 八、下一步计划

系统的核心功能已经比较完整，后续将进行前端功能测试和收尾工作，以及撰写各类报告文档。
