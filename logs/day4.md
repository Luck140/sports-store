# 日志 Day4：2026年6月9日 — 前端设计优化与交互体验改进

---

## 今日工作概述

Day3完成后端核心功能后，今天将重心转移到前端。主要完成了设计系统的建立、配色方案的全面更换、响应式布局修复、表单验证和交互反馈的增强，以及页面代码的清理。到当天结束时，整个前端界面的视觉风格统一了，配色从Vue默认的蓝色系和Element Plus默认主题全面更换为深松绿加琥珀金的组合方案，所有页面适配了手机、平板和桌面三种屏幕尺寸。

---

## 一、设计系统建立

在前期开发中，前端没有统一的设计规范，颜色、字体等样式散落在各个组件中。无论是按钮颜色、表格边框还是文字大小，每个页面都需要单独设置，维护起来非常麻烦。

今天首先建立了两个设计文档。PRODUCT.md从产品战略层面明确了用户画像——系统面向体育用品批发行业的管理人员和工作人员，品牌个性定位为专业、可靠、高效，设计原则明确拒绝花哨的电商风格。DESIGN.md从视觉层面记录了颜色的色值用途、字体层级、组件样式和具体使用规范。

同时引入了Impeccable设计工具对项目进行了自动化诊断扫描，结合人工评审制定了完整的改进计划。改进按照五个步骤推进：从建立设计系统文档开始，到替换配色方案、修复响应式布局、增强表单验证和交互反馈，最后完成代码清理和无障碍优化。

颜色方案最终确定为深松绿（#1e3a3a）搭配琥珀金（#c8913a），辅以暖白色背景。这个选择基于两个考虑：一是市面上大部分企业管理系统都在使用蓝色，松绿色能够形成独特的品牌记忆点；二是琥珀金在色环上与绿色形成互补关系，金色本身带有品质感的价值联想，适合在价格显示和选中状态中使用。

---

## 二、CSS变量体系建立

建立设计规范后，在base.css中定义了完整的CSS变量体系。这套变量涵盖了品牌色、中性色、文字色、暗角色、反馈色、阴影、字体大小、间距和圆角等多个维度：

```css
:root {
  /* 品牌色：深松绿 */
  --color-primary: #1e3a3a;
  --color-primary-dark: #152a2a;
  --color-primary-darker: #0e1e1e;
  --color-primary-light: #2a4a4a;
  --color-primary-lighter: #4a6a6a;
  --color-primary-bg: rgba(30, 58, 58, 0.08);

  /* 强调色：琥珀金 */
  --color-accent: #c8913a;
  --color-accent-dark: #a6752a;
  --color-accent-light: #dbb05c;

  /* 中性色 */
  --color-bg: #f5f3ef;
  --color-surface: #ffffff;
  --color-border: #e2ddd6;

  /* 文字色 */
  --color-text: #1a1a1a;
  --color-text-2: #4a4a4a;
  --color-text-muted: #7a7a7a;

  /* 反馈色 */
  --color-success: #5a8a5a;
  --color-warning: #c8913a;
  --color-danger: #8a3a3a;
}
```

为了让Element Plus的组件能够自动适配这套颜色，将组件变量与项目变量进行了映射：

```css
:root {
  --el-color-primary: var(--color-primary);
  --el-color-primary-dark-2: var(--color-primary-dark);
  --el-color-primary-light-3: #4a6a6a;
  --el-color-success: var(--color-success);
  --el-color-warning: var(--color-warning);
  --el-color-danger: var(--color-danger);
  --el-text-color-primary: var(--color-text);
  --el-text-color-regular: var(--color-text-2);
  --el-text-color-secondary: var(--color-text-muted);
  --el-bg-color: var(--color-bg);
  --el-border-color: var(--color-border);
  --el-border-radius-base: 4px;
}
```

这种方式的优势非常明显：后续如果要更换配色，只需要修改变量值即可，不需要到每个页面文件中去查找和替换颜色。颜色对比度方面也做了考虑，正文文字使用#1a1a1a而非纯黑，在暖白色背景上能达到4.5:1以上的对比度，满足WCAG AA标准。

> **📷 图片1：base.css变量体系代码截图**
> 说明：截取Day4版本中base.css的完整变量定义，保存至日志图片/day4/baseCSS变量代码.png

---

## 三、响应式布局修复

前端页面在手机上打开时存在较多布局问题。主要进行了以下修复：

登录页面和注册页面原本使用了固定的像素宽度，在手机上会出现水平滚动条。将固定宽度改为百分比宽度加最大宽度的组合方式，在不同屏幕尺寸下调整上下边距。

商品列表的栅格系统添加了响应式断点参数——手机上每行一列，平板上每行两列，桌面上每行四列：

```html
<el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="p in list" :key="p.product_id">
```

侧边栏在平板尺寸下宽度从220px缩小到180px，在手机尺寸下改为横向布局：

```css
@media (max-width: 768px) { .sidebar { width: 180px; } .content { padding: 14px; } }
@media (max-width: 480px) { .app-layout { flex-direction: column; } .sidebar { width: 100%; min-height: auto; } }
```

首页的统计卡片也做了自适应调整，使用flex-wrap让卡片在窄屏上自动换行排列。

> **📷 图片2：响应式布局效果截图（手机视图）**
> 说明：按F12打开开发者工具，切换到手机模式（375px宽度）截图，保存至日志图片/day4/响应式手机视图.png

---

## 四、表单验证增强

之前的前端页面几乎没有表单验证，用户可以提交空表单或者错误格式的数据。今天对所有表单页面添加了完整的验证规则。

注册页面使用了Element Plus的rules验证机制，自定义了手机号和邮箱的格式校验：

```javascript
const validatePhone = (rule, value, callback) => {
  if (!value) { callback(new Error('请输入手机号码')); return }
  if (!/^1\d{10}$/.test(value)) { callback(new Error('手机号格式不正确')); return }
  callback()
}
const validateEmail = (rule, value, callback) => {
  if (!value) { callback(); return }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) { callback(new Error('邮箱格式不正确')); return }
  callback()
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  customer_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, validator: validatePhone, trigger: 'blur' }],
  email: [{ validator: validateEmail, trigger: 'blur' }],
}
```

模板中对应添加了prop属性和placeholder提示文字：

```html
<el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
  <el-form-item label="密码" prop="password">
    <el-input v-model="form.password" type="password" placeholder="至少6位" show-password />
  </el-form-item>
  <el-form-item label="手机" prop="phone">
    <el-input v-model="form.phone" placeholder="请输入手机号码" />
  </el-form-item>
</el-form>
```

所有表单的提交按钮绑定了loading属性防止重复提交：

```html
<el-button type="primary" @click="register" :loading="loading">注册</el-button>
```

登录页面添加了用户名和密码的必填验证。购物车页面在提交订单前验证收件人、联系电话和收件地址是否填写完整。忘记密码页面验证用户名和邮箱是否匹配。

搜索功能添加了300毫秒的防抖处理：

```javascript
let timer = null
const doSearch = () => {
  page.value = 1;
  clearTimeout(timer);
  timer = setTimeout(() => load(1), 300);
}
```

> **📷 图片3：注册页表单验证代码截图**
> 说明：截取Register.vue中验证规则的完整代码，保存至日志图片/day4/表单验证代码.png

> **📷 图片4：改进后的登录页面截图**
> 说明：启动后浏览器打开登录页面，截取完整布局，保存至日志图片/day4/登录页面.png

---

## 五、代码清理与无障碍优化

删除了项目中未使用的计数器功能Store文件（counter.js）。修复了路由守卫中已经废弃的next函数调用，消除了控制台警告。侧边栏菜单的颜色通过CSS变量统一控制，替代了之前在组件属性中硬编码颜色的方式。

添加了对prefers-reduced-motion媒体查询的支持，在用户开启减少动效选项时禁用所有动画和过渡效果：

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 六、前后端联调修复

在前后端联调过程中，发现部分数据交互存在问题。商品列表的分页参数对齐问题尤为突出——前端分页组件需要的是总页数，而后端返回的total是总记录数。解决方法是在后端返回数据中同时包含total和total_pages两个字段，前端根据实际需求选择使用。

---

## 七、遇到的问题与解决

| 编号 | 问题 | 原因 | 解决方法 |
|------|------|------|----------|
| 1 | Element Plus组件样式覆盖困难 | 部分组件内部使用了固定色值，CSS变量无法覆盖 | 查看组件源码确认具体的CSS选择器，逐一定制覆盖 |
| 2 | 配色方案选择反复 | 蓝色系太大众化，无法形成品牌辨识度 | 完全放弃蓝色系，选择深松绿加琥珀金组合 |
| 3 | 响应式布局中表格溢出 | el-table在手机宽度下无法完整显示所有列 | 在手机上隐藏部分次要列，或启用横向滚动 |

---

## 八、文件改动清单

| 文件 | 操作 | 说明 |
|------|------|------|
| PRODUCT.md | 新增 | 产品战略文档（35行） |
| DESIGN.md | 新增 | 视觉设计规范文档（164行） |
| .impeccable/design.json | 新增 | 设计系统配置文件（105行） |
| frontend/src/assets/base.css | 重写 | 完整CSS变量体系重构（166行） |
| frontend/src/assets/main.css | 修改 | 全局样式调整 |
| frontend/src/stores/counter.js | 删除 | 移除未使用的计数器Store |
| frontend/src/views/Login.vue | 修改 | 添加表单验证、响应式布局 |
| frontend/src/views/Register.vue | 修改 | 添加完整rules验证规则（+74行） |
| frontend/src/views/Products.vue | 修改 | 响应式栅格调整、搜索防抖 |
| frontend/src/views/Cart.vue | 修改 | 表单验证增强 |
| frontend/src/views/Orders.vue | 修改 | 细节样式调整 |
| frontend/src/views/App.vue | 修改 | 侧边栏样式变量化 |
| 其他vue文件 | 修改 | 配色替换和样式微调 |
| logs/day4.md | 新增 | 本日志文件 |

---

## 九、下一步计划

配色方案和布局框架已经确定下来，后续可以在现有基础上逐步完善更多页面的细节。数据展示方面可以根据实际业务需要做针对性的优化，交互体验方面可以在现有基础上继续加固和完善。
