# 日志 Day7：2026年6月15日 — 前端功能测试与收尾工作

---

## 今日工作概述

前六天完成了系统的全部功能开发，今天进入项目的收尾阶段。主要完成了三部分工作：一是对系统所有功能模块进行了完整的测试和问题修复；二是对前端设计系统进行了重构升级，更换了配色方案并增加了背景图功能；三是编写了课程设计相关的各类文档和报告。

---

## 一、系统功能测试

对系统的所有页面和功能进行了全面测试，涵盖顾客端和管理端全部流程。

**顾客端测试项：**

| 功能模块 | 测试项 | 测试结果 |
|---------|-------|---------|
| 首页 | 横幅轮播、分类跳转、热销商品展示 | 通过 |
| 商品列表 | 关键词搜索、分类筛选、价格过滤、排序、分页 | 通过 |
| 商品详情 | 信息展示、收藏、加入购物车、评价列表 | 通过 |
| 购物车 | 添加/修改/删除、库存校验、结算信息、提交订单 | 通过 |
| 订单 | 创建、支付、取消、确认收货、催单 | 通过 |
| 个人中心 | 信息修改、头像上传、密码修改、地址管理、收藏 | 通过 |

**管理端测试项：**

| 功能模块 | 测试项 | 测试结果 |
|---------|-------|---------|
| 仪表盘 | 统计卡片、热销排行、销售趋势 | 通过 |
| 订单管理 | 确认/发货/取消、批量操作、退款审核 | 通过 |
| 进货管理 | 进货单创建、入库、库存预警 | 通过 |
| 报表中心 | 五类报表切换和数据展示 | 通过 |

> **📷 图片1：系统测试过程截图**
> 说明：截取商品列表页或订单页，展示正常运行状态，保存至日志图片/day7/系统测试截图.png

---

## 二、Bug修复汇总

测试过程中发现并修复了多个问题。

**1. 基本信息保存时空字段覆盖数据库值**

修复前，前端发送了所有字段，包括空字符串，导致数据库原有值被覆盖：

```javascript
await axios.put(`/api/customers/${id}`, {
  phone: profile.value.phone,   // 可能为空字符串""
  email: profile.value.email,   // 可能为空字符串""
  avatar: avatar.value          // 可能为空字符串""
})
```

修复后，后端增加空字符串转None验证器，更新时排除None字段：

```python
@model_validator(mode="before")
@classmethod
def empty_str_to_none(cls, values: dict) -> dict:
    return {k: None if isinstance(v, str) and v == "" else v
            for k, v in values.items()}

for k, v in data.model_dump(exclude_none=True).items():
    setattr(c, k, v)
```

**2. 头像上传后侧边栏不更新**

修复前，fetchAvatar只在页面加载时执行一次。修复后通过自定义事件通知侧边栏刷新：

```javascript
// Profile.vue保存后触发事件
window.dispatchEvent(new CustomEvent('avatar-updated', { detail: avatar.value }))

// App.vue监听事件更新头像
window.addEventListener('avatar-updated', (e) => {
  if (e.detail) userAvatar.value = e.detail
  else fetchAvatar()
})
```

**3. 子菜单点击一次后失效**

v-show与router-link配合使用时，display:none状态下的组件事件出现脱钩。将v-show替换为v-if：

```html
<!-- ❌ 之前 -->
<div v-show="openMenus.orders" class="sb-sub">

<!-- ✅ 之后 -->
<div v-if="openMenus.orders" class="sb-sub">
```

同时为router-view添加key属性确保路由变化时组件重新渲染：

```html
<router-view :key="$route.fullPath" />
```

**4. 订单列表切换状态后数据不刷新**

添加路由参数监听，切换状态时重新加载数据：

```javascript
watch(() => route.query.status, (newStatus) => {
  statusFilter.value = newStatus || ''
  page.value = 1
  load()
})
```

**5. 添加收货地址失败**

前端缺少必填字段验证，空字段被发送到后端导致校验失败。修复后增加前端验证：

```javascript
if (!addrForm.value.recipient_name || !addrForm.value.phone || !addrForm.value.address) {
  ElMessage.warning('请填写完整的地址信息')
  return
}
```

> **📷 图片2：Bug修复前后对比截图**
> 说明：截取个人中心基本信息页，展示修复后数据正常显示的效果，保存至日志图片/day7/Bug修复对比.png

---

## 三、设计系统重构

将配色方案从橙色系全面更换为粉绿配色方案：

| 用途 | 旧色值（橙色系） | 新色值（粉绿系） |
|------|----------------|----------------|
| 品牌主色 | #e8652d | #006973 |
| 强调色 | #e8652d | #E68CBE |
| 辅助色 | #f5a880 | #A5C3A0 |
| 正文色 | #1a1a1a | #1a1a1a |
| 背景色 | #f5f6f8 | #f4f5f7 |

```css
:root {
  --ss-primary: #006973;
  --ss-primary-dark: #004d54;
  --ss-accent: #e68cbe;
  --ss-green: #a5c3a0;
  --ss-text: #1a1a1a;
  --ss-text-2: #555555;
  --ss-bg: #f4f5f7;
  --ss-surface: #ffffff;
}
```

**背景图系统实现：**

每种商品分类对应不同的背景图片，通过CSS变量动态切换：

```css
:root {
  --ss-bg-home: url('/images/hero-bg.jpg');
  --ss-bg-ball: url('/images/ball-bg.jpg');
  --ss-bg-clothing: url('/images/clothing-bg.jpg');
  --ss-bg-equipment: url('/images/equipment-bg.jpg');
  --ss-bg-shoes: url('/images/shoes-bg.jpg');
  --ss-bg-accessories: url('/images/accessories-bg.jpg');
}
```

页面路由变化时自动切换对应背景图：

```javascript
watch(route, () => {
  if (route.path.startsWith('/admin')) setBg('admin')
  else if (route.path.startsWith('/products')) {
    const cat = route.query.category
    if (cat && bgMap[cat]) setBg(cat)
    else setBg('default')
  }
})
```

背景图透明度通过遮罩层的rgba值控制，调整为0.15使背景图清晰可见：

```css
.bg-layer::before {
  background: rgba(255, 255, 255, 0.15);
}
```

> **📷 图片3：最终版首页截图（粉绿配色+背景图）**
> 说明：打开首页，截取英雄区域+背景图显示效果，保存至日志图片/day7/首页最终效果.png

---

## 四、订单页面卡片式布局改造

将订单列表页面从简单的表格布局改造为电商风格的卡片式布局。每个订单卡片包含五个区块：

| 区块 | 展示内容 | 样式特点 |
|------|---------|---------|
| 顶部店铺栏 | 店铺logo + SportsStore + 旗舰店标签 + 订单状态 | 状态用颜色区分 |
| 商品主体区 | 商品图标 + 名称 + 规格x数量 + 服务保障标签 | 服务标签绿底白字 |
| 价格支付区 | 实付金额（标红）+ 运费 + 优惠信息 | 重点金额标红突出 |
| 操作按钮区 | 根据状态动态显示按钮 | 横向排列 |
| 底部物流栏 | 物流图标 + 进度文案 + 预计时间 | 灰色底色区分 |

同时，订单列表的API接口增加了商品明细数据的返回：

```python
items.append({
    "order_id": o.order_id,
    "status": o.status,
    "total_amount": float(o.total_amount),
    "items": [
        {"product_name": d.product_name_snapshot, "quantity": d.quantity, ...}
        for d in db.query(OrderDetail).filter(OrderDetail.order_id == o.order_id).all()
    ]
})
```

> **📷 图片4：订单卡片式布局截图**
> 说明：进入订单列表页，截取订单卡片的完整五区块布局，保存至日志图片/day7/订单卡片布局.png

---

## 五、商品图标分类映射

之前商品使用按ID循环的emoji图标，导致跑步鞋显示衣服图标、羽毛球显示足球图标等问题。改为按商品名称关键词匹配图标：

```javascript
const keywordMap = [
  { keys: ['篮球'], icon: '🏀' },
  { keys: ['足球', '排球'], icon: '⚽' },
  { keys: ['乒乓球'], icon: '🏓' },
  { keys: ['羽毛球'], icon: '🏸' },
  { keys: ['网球'], icon: '🎾' },
  { keys: ['跑步鞋', '跑鞋'], icon: '👟' },
  { keys: ['训练鞋'], icon: '👟' },
  { keys: ['户外鞋'], icon: '🥾' },
  { keys: ['T恤', 't恤'], icon: '👕' },
  { keys: ['短裤'], icon: '🩳' },
  { keys: ['套装'], icon: '🥋' },
  { keys: ['护腕'], icon: '⌚' },
  { keys: ['护膝'], icon: '🦵' },
  { keys: ['瑜伽', '瑜伽垫'], icon: '🧘' },
  { keys: ['背包'], icon: '🎒' },
  { keys: ['袜'], icon: '🧦' },
  { keys: ['水壶'], icon: '🧴' },
  { keys: ['毛巾'], icon: '🧣' },
]
```

> **📷 图片5：商品列表图标匹配效果截图**
> 说明：打开商品列表页，截取各商品图标与品类正确对应的效果，保存至日志图片/day7/商品图标映射.png

---

## 六、发票系统改进

根据国家税务总局2017年第16号公告的要求，对发票系统进行了完善：

| 发票类型 | 必填字段 |
|---------|---------|
| 增值税普通发票 | 单位名称、纳税人识别号 |
| 增值税专用发票 | 单位名称、纳税人识别号、地址电话、开户行及账号 |

在订单详情页增加了发票信息的完整展示：

```html
<el-descriptions-item label="发票类型">
  {{ {0:'不需要',1:'增值税普通发票',2:'增值税专用发票'}[order.invoice_required] }}
</el-descriptions-item>
<el-descriptions-item v-if="order.invoice_tax_no" label="税号">
  {{ order.invoice_tax_no }}
</el-descriptions-item>
<el-descriptions-item v-if="order.invoice_address_phone" label="地址电话">
  {{ order.invoice_address_phone }}
</el-descriptions-item>
```

---

## 七、文件改动清单

| 文件 | 操作 | 说明 |
|------|------|------|
| 前端代码/src/assets/base.css | 重写 | 粉绿配色方案变量体系 |
| 前端代码/src/assets/main.css | 修改 | 背景图遮罩层、透明度控制 |
| 前端代码/src/App.vue | 修改 | 背景图切换系统、头像事件监听 |
| 前端代码/src/views/Orders.vue | 重写 | 电商风格卡片式布局 |
| 前端代码/src/utils/productIcons.js | 新增 | 商品图标分类映射工具 |
| 前端代码/src/views/Profile.vue | 修改 | 保存逻辑修复、错误提示增强 |
| 前端代码/src/views/Products.vue | 修改 | 图标映射切换 |
| 后端服务代码/schemas.py | 修改 | 空字符串转None验证器 |
| 后端服务代码/routers/orders.py | 修改 | 订单接口增加商品明细 |
| README.md | 重写 | 完整项目说明和部署文档 |

---

## 八、总结

经过七天的开发，SportsStore体育用品批发销售系统从零开始完成了需求分析、数据库设计、后端API开发、前端页面开发和界面设计优化的全过程。系统实现了商品管理、购物车、订单流转、支付集成、管理后台等完整的业务流程，采用了Vue 3 + FastAPI的前后端分离架构，数据库使用MySQL，缓存使用Redis。

通过本次课程设计，完整实践了从需求分析到系统交付的软件开发全流程，深入掌握了前后端分离架构的开发模式，对数据库设计、API设计、前端框架和版本控制等方面都有了更加深入的理解。
