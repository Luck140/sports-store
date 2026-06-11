<template>
  <div class="home">
    <section class="hero">
      <div class="hero-inner">
        <h1>体育用品一站式批发采购平台</h1>
        <p class="hero-desc">覆盖球类、服装、器材、鞋类、配件五大品类，源头厂家直供，支持批量采购</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" round @click="$router.push('/products')">立即选购</el-button>
          <el-button size="large" round @click="$router.push('/register')">免费注册</el-button>
        </div>
        <div class="hero-stats">
          <div class="hs-item"><span class="hs-num">5</span><span class="hs-label">商品品类</span></div>
          <div class="hs-item"><span class="hs-num">4</span><span class="hs-label">合作厂家</span></div>
          <div class="hs-item"><span class="hs-num">48h</span><span class="hs-label">平均发货</span></div>
        </div>
      </div>
    </section>

    <div class="container">
      <section class="section" v-if="banners.length">
        <el-carousel height="200px" :interval="4000" indicator-position="none" arrow="hover">
          <el-carousel-item v-for="b in banners" :key="b.banner_id">
            <div class="banner-card" :style="{background: ['linear-gradient(135deg,#e8652d,#f08050)','linear-gradient(135deg,#f08050,#e8652d)','linear-gradient(135deg,#f5a880,#e8652d)'][b.banner_id % 3]}" @click="bannerClick(b)">
              <div><h2>{{ b.title }}</h2><p v-if="b.subtitle">{{ b.subtitle }}</p></div>
            </div>
          </el-carousel-item>
        </el-carousel>
      </section>

      <section class="section">
        <div class="section-hd"><h2>商品分类</h2></div>
        <div class="category-grid">
          <div class="cat-card" v-for="(c,i) in categories" :key="c.name" @click="$router.push(`/products?category=${c.name}`)" :style="{animationDelay: i*0.1+'s'}">
            <span class="cat-icon">{{ c.icon }}</span>
            <span class="cat-name">{{ c.name }}</span>
            <span class="cat-desc">{{ c.desc }}</span>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="section-hd"><h2>热销商品</h2><el-button text @click="$router.push('/products?sort=sales')">更多</el-button></div>
        <el-row :gutter="16">
          <el-col :xs="12" :sm="8" :md="6" v-for="p in hotProducts" :key="p.product_id">
            <div class="product-card" @click="$router.push(`/products/${p.product_id}`)">
              <div class="pc-img">{{ getIcon(p.product_id) }}</div>
              <div class="pc-name" :title="p.product_name">{{ p.product_name }}</div>
              <div class="pc-price">¥{{ p.unit_price }}</div>
              <div class="pc-meta"><span>{{ p.category }}</span><span>已售 {{ p.sales_count || 0 }}</span></div>
            </div>
          </el-col>
        </el-row>
      </section>

      <section class="section cta-section">
        <div class="cta-box">
          <h2>开始您的批发采购</h2>
          <p>注册即可浏览全品类商品，享受批发价格和专属服务</p>
          <el-button type="primary" size="large" round @click="$router.push('/register')">免费注册</el-button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
const router = useRouter()
const banners = ref([])
const hotProducts = ref([])
const categories = [
  { name:'球类', icon:'🏀', desc:'篮球·足球·排球·乒乓球' },
  { name:'服装', icon:'👕', desc:'T恤·短裤·运动套装' },
  { name:'器材', icon:'🏸', desc:'球拍·护具·训练器材' },
  { name:'鞋类', icon:'👟', desc:'跑步鞋·训练鞋·户外鞋' },
  { name:'配件', icon:'🧢', desc:'袜子·帽子·运动背包' },
]
const icons = ['🏀','⚽','🏸','👕','⚾','🏐','🏓','🎽','🩳','🧢']
const getIcon = (id) => icons[(id - 1) % icons.length]
const bannerClick = (b) => {
  if (b.link_type === 'product' && b.link_value) router.push(`/products/${b.link_value}`)
  else if (b.link_type === 'category' && b.link_value) router.push(`/products?category=${b.link_value}`)
}
onMounted(async () => {
  try { const b = await axios.get('/api/banners/'); banners.value = b.data } catch {}
  try { const h = await axios.get('/api/products/hot', { params: { limit: 8 } }); hotProducts.value = h.data } catch {}
})
</script>

<style scoped>
.home { min-height:100%; }
.hero { background:var(--hero-gradient); padding:64px 20px; text-align:center; color:#fff; }
.hero-inner { max-width:720px; margin:0 auto; }
.hero h1 { font-size:clamp(22px,5vw,34px); font-weight:700; margin:0 0 12px 0; letter-spacing:1px; }
.hero-desc { font-size:15px; opacity:0.75; margin:0 0 28px 0; line-height:1.7; }
.hero-actions { display:flex; gap:14px; justify-content:center; margin-bottom:36px; }
.hero-stats { display:flex; justify-content:center; gap:40px; }
.hs-item { display:flex; flex-direction:column; align-items:center; }
.hs-num { font-size:26px; font-weight:700; }
.hs-label { font-size:12px; opacity:0.55; margin-top:2px; }
.container { max-width:1140px; margin:0 auto; padding:0 16px; }
.section { margin:32px 0; }
.section-hd { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.section-hd h2 { margin:0; font-size:19px; font-weight:600; }
.banner-card { height:100%; display:flex; align-items:center; justify-content:center; color:#fff; cursor:pointer; border-radius:8px; text-align:center; }
.banner-card h2 { font-size:24px; margin:0 0 6px 0; }
.banner-card p { font-size:14px; opacity:0.8; margin:0; }

.category-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:12px; }
.cat-card { background:#fff; border:1px solid var(--color-border-light); border-radius:8px; padding:20px; text-align:center; cursor:pointer; transition:all 0.2s; }
.cat-card:hover { border-color:var(--color-accent); transform:translateY(-2px); box-shadow:var(--shadow-md); }
.cat-icon { font-size:36px; display:block; margin-bottom:8px; }
.cat-name { font-size:15px; font-weight:600; display:block; margin-bottom:4px; color:var(--color-text); }
.cat-desc { font-size:12px; color:var(--color-text-muted); }

.product-card { background:#fff; border:1px solid var(--color-border-light); border-radius:8px; padding:14px; cursor:pointer; transition:all 0.2s; margin-bottom:12px; text-align:center; }
.product-card:hover { transform:translateY(-2px); box-shadow:var(--shadow-md); }
.pc-img { font-size:44px; margin-bottom:8px; }
.pc-name { font-size:13px; font-weight:600; margin-bottom:6px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.pc-price { color:var(--color-accent); font-size:17px; font-weight:700; margin-bottom:6px; }
.pc-meta { display:flex; justify-content:space-between; font-size:11px; color:var(--color-text-muted); }

.cta-section { margin:40px 0; }
.cta-box { background:linear-gradient(135deg, #e8652d, #f08050); border-radius:12px; padding:44px; text-align:center; color:#fff; }
.cta-box h2 { margin:0 0 8px 0; font-size:22px; }
.cta-box p { opacity:0.7; margin:0 0 20px 0; font-size:14px; }

@media (max-width:480px) { .hero { padding:40px 12px; } .hero-stats { gap:20px; } }
</style>
