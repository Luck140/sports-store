<template>
  <div class="home">
    <!-- Hero 区域 -->
    <section class="hero" :style="{ backgroundImage: 'var(--ss-bg-home)' }">
      <div class="hero-overlay"></div>
      <div class="hero-inner">
        <h1 class="hero-title">SportsStore</h1>
        <p class="hero-desc">体育用品一站式批发采购平台 · 源头厂家直供 · 支持批量采购</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" round @click="$router.push('/products')">立即选购</el-button>
          <el-button size="large" round @click="$router.push('/register')">免费注册</el-button>
          <el-button size="large" round plain @click="$router.push('/login')">立即登录</el-button>
        </div>
        <div class="hero-stats">
          <div class="hs-item">
            <span class="hs-num">5</span>
            <span class="hs-label">商品品类</span>
          </div>
          <div class="hs-item">
            <span class="hs-num">4</span>
            <span class="hs-label">合作厂家</span>
          </div>
          <div class="hs-item">
            <span class="hs-num">48h</span>
            <span class="hs-label">平均发货</span>
          </div>
          <div class="hs-item">
            <span class="hs-num">20</span>
            <span class="hs-label">精选商品</span>
          </div>
        </div>
      </div>
    </section>

    <div class="container">
      <!-- 轮播横幅 -->
      <section class="section" v-if="banners.length">
        <el-carousel height="200px" :interval="4000" indicator-position="none" arrow="hover">
          <el-carousel-item v-for="b in banners" :key="b.banner_id">
            <div class="banner-card" :style="{ background: getBannerBg(b.banner_id) }" @click="bannerClick(b)">
              <div class="banner-text">
                <h2>{{ b.title }}</h2>
                <p v-if="b.subtitle">{{ b.subtitle }}</p>
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>
      </section>

      <!-- 商品分类 -->
      <section class="section">
        <div class="section-hd"><h2>商品分类</h2></div>
        <div class="category-grid">
          <div
            v-for="(c, i) in categories" :key="c.name"
            class="cat-card"
            @click="goCategory(c.name)"
            :style="{ animationDelay: i * 0.08 + 's' }"
          >
            <div class="cat-icon-wrap" :style="{ background: c.color + '18' }">
              <span class="cat-icon">{{ c.icon }}</span>
            </div>
            <span class="cat-name">{{ c.name }}</span>
            <span class="cat-desc">{{ c.desc }}</span>
          </div>
        </div>
      </section>

      <!-- 热销商品 -->
      <section class="section">
        <div class="section-hd">
          <h2>热销商品</h2>
          <el-button text @click="$router.push('/products?sort=sales')">查看全部 →</el-button>
        </div>
        <el-row :gutter="16">
          <el-col :xs="12" :sm="8" :md="6" v-for="p in hotProducts" :key="p.product_id">
            <div class="product-card" @click="$router.push(`/products/${p.product_id}`)">
              <div class="pc-icon">{{ getIcon(p) }}</div>
              <div class="pc-name" :title="p.product_name">{{ p.product_name }}</div>
              <div class="pc-meta">
                <span class="pc-cat">{{ p.category }}</span>
                <span class="pc-sales">已售 {{ p.sales_count || 0 }}</span>
              </div>
              <div class="pc-price">¥{{ p.unit_price }}</div>
            </div>
          </el-col>
        </el-row>
      </section>

      <!-- CTA -->
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
import { getProductIcon } from '@/utils/productIcons'

const router = useRouter()
const banners = ref([])
const hotProducts = ref([])

const categories = [
  { name: '球类', icon: '🏀', desc: '篮球·足球·排球·乒乓球', color: '#e8652d' },
  { name: '服装', icon: '👕', desc: 'T恤·短裤·运动套装', color: '#e68cbe' },
  { name: '器材', icon: '🏸', desc: '球拍·护具·训练器材', color: '#006973' },
  { name: '鞋类', icon: '👟', desc: '跑步鞋·训练鞋·户外鞋', color: '#a5c3a0' },
  { name: '配件', icon: '🧢', desc: '袜子·帽子·运动背包', color: '#e8a040' },
]

const icons = ['🏀', '⚽', '🏸', '👕', '⚾', '🏐', '🏓', '🎽', '🩳', '🧢']
const getIcon = (p) => getProductIcon(p)

const bannerColors = [
  'linear-gradient(135deg, #006973, #a5c3a0)',
  'linear-gradient(135deg, #a5c3a0, #006973)',
  'linear-gradient(135deg, #e68cbe, #006973)',
]
const getBannerBg = (id) => bannerColors[id % bannerColors.length]

const bannerClick = (b) => {
  if (b.link_type === 'product' && b.link_value) router.push(`/products/${b.link_value}`)
  else if (b.link_type === 'category' && b.link_value) router.push(`/products?category=${b.link_value}`)
}

const goCategory = (name) => { router.push(`/products?category=${name}`) }

onMounted(async () => {
  try { const b = await axios.get('/api/banners/'); banners.value = b.data } catch {}
  try { const h = await axios.get('/api/products/hot', { params: { limit: 8 } }); hotProducts.value = h.data } catch {}
})
</script>

<style scoped>
.home { min-height: 100%; }

/* Hero */
.hero {
  position: relative;
  padding: 80px 20px;
  text-align: center;
  background-size: cover;
  background-position: center;
  color: #fff;
  overflow: hidden;
}
.hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(0,105,115,0.85), rgba(0,105,115,0.70));
  z-index: 0;
}
.hero-inner { position: relative; z-index: 1; max-width: 720px; margin: 0 auto; }
.hero-title {
  font-size: clamp(28px, 5vw, 42px);
  font-weight: 700;
  margin: 0 0 10px 0;
  letter-spacing: 2px;
}
.hero-desc { font-size: 15px; opacity: 0.85; margin: 0 0 28px; line-height: 1.7; }
.hero-actions { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-bottom: 36px; }
.hero-stats {
  display: flex;
  justify-content: center;
  gap: 24px;
  flex-wrap: wrap;
}
.hs-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 130px;
  padding: 12px 4px;
  background: rgba(255,255,255,0.10);
  border-radius: var(--ss-radius-sm);
  backdrop-filter: blur(4px);
}
.hs-num { font-size: 30px; font-weight: 700; }
.hs-label { font-size: 12px; opacity: 0.6; margin-top: 2px; }

/* Container */
.container { max-width: 1140px; margin: 0 auto; padding: 0 16px; }
.section { margin: 32px 0; }
.section-hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.section-hd h2 { margin: 0; font-size: 19px; font-weight: 600; color: var(--ss-text); }

/* Banner */
.banner-card {
  height: 100%; display: flex; align-items: center; justify-content: center;
  color: #fff; cursor: pointer; border-radius: var(--ss-radius-md); text-align: center;
}
.banner-text h2 { font-size: 24px; margin: 0 0 4px; }
.banner-text p { font-size: 14px; opacity: 0.8; margin: 0; }

/* Category Grid */
.category-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; }
.cat-card {
  background: var(--ss-surface); border: 1px solid var(--ss-border-light);
  border-radius: var(--ss-radius-md); padding: 24px 16px;
  text-align: center; cursor: pointer;
  transition: all var(--ss-transition-base);
}
.cat-card:hover {
  border-color: var(--ss-primary); transform: translateY(-3px);
  box-shadow: var(--ss-shadow-lg);
}
.cat-icon-wrap {
  width: 52px; height: 52px; border-radius: var(--ss-radius-lg);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 10px;
}
.cat-icon { font-size: 28px; line-height: 1; }
.cat-name { font-size: 15px; font-weight: 600; display: block; margin-bottom: 4px; color: var(--ss-text); }
.cat-desc { font-size: 12px; color: var(--ss-text-muted); }

/* Product Card */
.product-card {
  background: var(--ss-surface); border: 1px solid var(--ss-border-light);
  border-radius: var(--ss-radius-sm); padding: 16px;
  cursor: pointer; transition: all var(--ss-transition-base);
  margin-bottom: 16px; text-align: center;
}
.product-card:hover {
  transform: translateY(-2px); box-shadow: var(--ss-shadow-md);
}
.pc-icon { font-size: 40px; margin-bottom: 8px; }
.pc-name { font-size: 13px; font-weight: 600; margin-bottom: 6px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pc-meta { display: flex; justify-content: space-between; font-size: 11px; color: var(--ss-text-muted); margin-bottom: 8px; }
.pc-cat { background: var(--ss-primary-bg); color: var(--ss-primary); padding: 1px 6px; border-radius: 3px; }
.pc-price { color: var(--ss-accent); font-size: 18px; font-weight: 700; }

/* CTA */
.cta-section { margin: 48px 0; }
.cta-box {
  background: linear-gradient(135deg, var(--ss-primary), var(--ss-green));
  border-radius: var(--ss-radius-md);
  padding: 48px; text-align: center; color: #fff;
}
.cta-box h2 { margin: 0 0 8px; font-size: 22px; }
.cta-box p { opacity: 0.7; margin: 0 0 20px; font-size: 14px; }

@media (max-width: 480px) {
  .hero { padding: 48px 12px; }
  .hero-stats { gap: 20px; }
}
</style>
