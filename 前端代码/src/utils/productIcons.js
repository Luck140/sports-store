/**
 * 根据商品名称关键词匹配对应的 emoji 图标
 * 确保每个商品显示与其品类相符的图标
 * 匹配规则：先匹配名称关键词，再按分类兜底
 */
export function getProductIcon(product) {
  if (!product) return '📦'

  const name = product.product_name || ''
  const cat = product.category || ''

  // ===== 精确关键词匹配（按顺序，先匹配的优先） =====
  const keywordMap = [
    // 篮球类
    { keys: ['篮球'], icon: '🏀' },
    // 足球类
    { keys: ['足球', '排球'], icon: '⚽' },
    // 网球
    { keys: ['网球拍', '网球'], icon: '🎾' },
    // 羽毛球
    { keys: ['羽毛球拍', '羽毛球'], icon: '🏸' },
    // 乒乓球
    { keys: ['乒乓球'], icon: '🏓' },
    // 跑步鞋
    { keys: ['跑步鞋', '跑鞋'], icon: '👟' },
    // 训练鞋
    { keys: ['训练鞋'], icon: '👟' },
    // 户外鞋
    { keys: ['户外鞋'], icon: '🥾' },
    // T恤
    { keys: ['T恤', 't恤'], icon: '👕' },
    // 短裤
    { keys: ['短裤'], icon: '🩳' },
    // 运动套装
    { keys: ['套装'], icon: '🥋' },
    // 护腕
    { keys: ['护腕'], icon: '⌚' },
    // 护膝
    { keys: ['护膝'], icon: '🦵' },
    // 瑜伽垫
    { keys: ['瑜伽垫', '瑜伽'], icon: '🧘' },
    // 背包
    { keys: ['背包', '包'], icon: '🎒' },
    // 运动袜
    { keys: ['袜'], icon: '🧦' },
    // 水壶
    { keys: ['水壶', '水杯'], icon: '🧴' },
    // 毛巾
    { keys: ['毛巾'], icon: '🧣' },
    // 帽子
    { keys: ['帽子', '帽'], icon: '🧢' },
  ]

  for (const rule of keywordMap) {
    for (const key of rule.keys) {
      if (name.includes(key)) return rule.icon
    }
  }

  // ===== 分类兜底 =====
  const catFallback = {
    '球类': '⚽',
    '服装': '👕',
    '鞋类': '👟',
    '器材': '🏸',
    '配件': '🧢',
  }

  return catFallback[cat] || '📦'
}
