<template>
  <div class="hero">
    <div class="hero-box">
      <h1>体育用品批发销售信息系统</h1>
      <p class="subtitle">一站式管理体育用品批发业务，高效、便捷、专业</p>
      <div class="features">
        <el-card v-for="f in features" :key="f.title" class="f-card">
          <el-icon :size="36"><component :is="f.icon" /></el-icon>
          <h3>{{ f.title }}</h3>
          <p>{{ f.desc }}</p>
        </el-card>
      </div>
      <div class="actions">
        <el-button type="primary" size="large" @click="$router.push('/register')">立即注册</el-button>
        <el-button size="large" @click="$router.push('/login')">已有账号？登录</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
const features = [
  { icon:'Goods', title:'商品管理', desc:'浏览与管理体育用品库存' },
  { icon:'ShoppingCart', title:'在线下单', desc:'轻松选购并提交订单' },
  { icon:'Document', title:'订单追踪', desc:'实时查看订单状态与支付' },
]
</script>

<style scoped>
.hero { height:100%; display:flex; align-items:center; justify-content:center; background:var(--hero-gradient); }
.hero-box { text-align:center; color:#fff; padding:40px; max-width:800px; width:90%; }
.hero-box h1 { font-size:var(--font-size-2xl); margin-bottom:10px; font-weight:700; }
.subtitle { font-size:var(--font-size-md); opacity:0.9; margin-bottom:40px; }
.features { display:flex; gap:24px; justify-content:center; margin-bottom:40px; flex-wrap:wrap; }
.f-card { width:clamp(140px, 30vw, 180px); background:rgba(255,255,255,0.15); border:none; color:#fff; }
.f-card h3 { margin:8px 0; }
.f-card p { font-size:var(--font-size-xs); opacity:0.8; }
.actions { display:flex; gap:16px; justify-content:center; flex-wrap:wrap; }
@media (max-width:480px) { .hero-box { padding:20px; } .features { gap:16px; } }
</style>
