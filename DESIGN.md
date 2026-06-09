---
name: Sports Store
description: 体育用品批发销售信息系统
colors:
  primary: "#1e3a3a"
  accent: "#c8913a"
  neutral-bg: "#f5f3ef"
  surface: "#ffffff"
  ink: "#1a1a1a"
  ink-muted: "#7a7a7a"
  dark-bg: "#162626"
  dark-text: "#bcc6c6"
  success: "#5a8a5a"
  danger: "#8a3a3a"
typography:
  display:
    fontFamily: "'Helvetica Neue', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif"
    fontSize: "36px"
    fontWeight: 700
    lineHeight: 1.2
  body:
    fontFamily: "'Helvetica Neue', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "'Helvetica Neue', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 500
    lineHeight: 1.4
rounded:
  sm: "4px"
  md: "8px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "20px"
  xl: "24px"
  xxl: "40px"
---

# Design System: Sports Store

## 1. Overview

**Creative North Star: "静谧林舍"**

一个不像"企业管理系统"的企业管理系统。以深松绿为骨、琥珀金为睛，在沉稳的自然基调中透出温暖的光泽。整体氛围像是高端精品店或独立品牌的工作后台——安静、自信、有质感。

设计上拒绝传统企业系统的灰色沉闷，也拒绝花哨的电商风格。每一处色彩都有存在的理由：松绿传递信任与深度，琥珀金增添温暖与价值感，暖白底色让界面呼吸。

**Key Characteristics:**
- 深松绿为主色，克制沉稳，不喧宾夺主
- 琥珀金点缀，传递价值感（尤其价格和关键状态）
- 暖白色/米灰色背景取代冷灰，有自然质感
- 深色侧边栏用松绿底 + 琥珀金高亮
- 一切从简，但细节处有温度

## 2. Colors

松绿+琥珀金+暖白，来自自然的配色，既有深度又有温度。

### Primary
- **深松绿** (#1e3a3a): 主按钮、品牌色、重要交互元素。不是普通的蓝，不是普通的绿，是森林深处的安静力量。
- **深松绿暗** (#152a2a): 悬停态、深色区域。
- **松绿亮** (#2a4a4a): 浅色变体。

### Accent
- **琥珀金** (#c8913a): 价格显示、侧边栏选中态、警告标签、重要强调。金色不一定要俗气——克制的琥珀金是高级感的关键。
- **琥珀金暗** (#a6752a): 悬停态。

### Neutral (暖白系)
- **米灰底** (#f5f3ef): 页面背景。微微的暖调让界面有温度，不像冷灰那样"医院感"。
- **柔白** (#edebe6): 卡片/区块的交替底色。
- **纯白** (#ffffff): 卡片、表单、弹窗。
- **边框** (#e2ddd6): 温暖的浅茶色边框，比纯灰更有质感。

### Ink
- **墨色** (#1a1a1a): 正文。不是纯黑，微微柔和。
- **灰褐** (#4a4a4a): 次要文字。
- **淡褐** (#7a7a7a): 辅助文字。
- **浅灰** (#b0b0b0): 占位符、分割线。

### Dark Background
- **深松绿底** (#162626): 侧边栏背景、暗色区块。
- **极深松绿** (#0f1a1a): Logo 区域。

### Feedback
- **苔绿** (#5a8a5a): 成功态（已发货、已确认）。
- **琥珀金** (#c8913a): 警告态（待确认、待付款）。与强调色统一。
- **砖红** (#8a3a3a): 危险态（缺货、错误、删除）。
- **灰绿** (#7a8a8a): 信息态。

### Named Rules

**The Accent-as-Signal Rule.** 琥珀金是信号色，不是装饰色。只用于价格、选中态、关键提醒。用得越少，信号越强。

**The Warm-Not-Cold Rule.** 所有中性色都带有微暖的底色，拒绝冷灰色。暖 = 自然 = 可信赖。

## 3. Typography

**Display Font:** Helvetica Neue, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Arial, sans-serif
**Body Font:** Helvetica Neue, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Arial, sans-serif

**Character:** 干净利落的无衬线体系。不引入装饰性字体，质感通过间距和层级来体现。

### Hierarchy
- **Display** (700, 36px, 1.2): Hero 主标题。
- **Headline** (600, 20px, 1.3): 卡片标题、弹窗标题。
- **Title** (600, 16px, 1.4): 区块小标题、商品名称。
- **Body** (400, 14px, 1.6): 正文。
- **Label** (500, 12px, 1.4): 辅助文字、标签。

## 4. Elevation

扁平为主，阴影为辅。层级通过背景色明度区分（白+米灰+柔白三层）。阴影仅作为交互反馈出现。

### Shadow Vocabulary
- **卡片悬停** (0 2px 12px rgba(0,0,0,0.08)): 交互反馈。
- **下拉浮层** (0 2px 12px rgba(0,0,0,0.12)): 弹窗、下拉菜单。

## 5. Components

### Buttons
- **Shape:** 小圆角 (4px)。
- **Primary:** 深松绿底 + 白色文字。悬停时稍微亮一点。
- **Default:** 纯白底 + 暖灰边框。

### Sidebar
- **Background:** 深松绿 (#162626)。
- **Text:** 灰白 (#bcc6c6)。
- **Active:** 琥珀金 (#c8913a) 高亮，配微光背景。

### Cards
- **Corner:** 小圆角 (4px)。
- **Background:** 纯白 (#ffffff)。
- **Border:** 暖茶色 (#eae7e0)。
- **Shadow:** 静止无阴影，悬停微升。

### Tags
- **Pending/警告:** 琥珀金
- **Shipped/成功:** 苔绿
- **Out of Stock/危险:** 砖红
- **Cancelled/信息:** 灰绿

### Price Display
- **Color:** 琥珀金 (#c8913a)。用金色而非红色表示价格，传递价值感而非紧迫感。

## 6. Do's and Don'ts

### Do:
- **Do** 使用深松绿 (#1e3a3a) 作为主色。它是品牌的基础色，但不应该铺满整个界面。
- **Do** 使用暖白色背景 (#f5f3ef)。它让界面有温度，不像传统企业系统那样冷冰冰。
- **Do** 将琥珀金 (#c8913a) 保留给价格、选中态和关键提醒。
- **Do** 保持卡片简洁：白底 + 暖灰边框 + 小圆角。

### Don't:
- **Don't** 使用冷灰色 (#f0f2f5, #e4e7ed) 作为背景色。暖白系才是品牌语言。
- **Don't** 用红色 (#f56c6c) 显示价格。危险色只用于真正的错误和危险操作。
- **Don't** 使用任何蓝色 (#409EFF) — 这是旧主题色，已经过时。
- **Don't** 使用花哨的电商风格。保持安静的高级感。
- **Don't** 嵌套卡片。
- **Don't** 在表单提交时不显示 loading 状态。
