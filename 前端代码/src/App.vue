<template>
  <div id="app" ref="appRef" :style="bgStyle">
    <!-- ====== 登录后布局 ====== -->
    <div class="app-layout" v-if="userStore.user">
      <aside class="sidebar">
        <div class="sb-head" @click="$router.push('/')">
          <span class="sb-head-icon">🏪</span> SportsStore
        </div>
        <div class="sb-user">
          <div class="sb-av">
            <img v-if="userAvatar" :src="userAvatar" class="sb-av-img" />
            <span v-else class="sb-av-txt">{{ (userStore.user.username || 'U')[0] }}</span>
          </div>
          <div class="sb-u-info">
            <div class="sb-u-name">{{ userStore.user.customer_name || userStore.user.username }}</div>
            <span class="sb-u-badge">{{ userStore.isAdmin ? '管理员' : '顾客' }}</span>
          </div>
        </div>
        <nav class="sb-nav">
          <template v-if="userStore.isAdmin">
            <router-link to="/admin" class="sb-item" active-class="sb-active" @click="setBg('admin')">📊 仪表盘</router-link>
            <router-link to="/admin/orders" class="sb-item" active-class="sb-active" @click="setBg('admin')">📦 订单管理</router-link>
            <router-link to="/admin/purchases" class="sb-item" active-class="sb-active" @click="setBg('admin')">📥 进货管理</router-link>
            <router-link to="/admin/reports" class="sb-item" active-class="sb-active" @click="setBg('admin')">📋 报表中心</router-link>
            <div class="sb-divider"></div>
            <router-link to="/products" class="sb-item" active-class="sb-active">🛍️ 商品浏览</router-link>
          </template>
          <template v-else>
            <router-link to="/products" class="sb-item" active-class="sb-active">🛍️ 商品列表</router-link>
            <router-link to="/cart" class="sb-item cart-item" active-class="sb-active">
              🛒 购物车
              <span v-if="cartCount" class="sb-dot">{{ cartCount }}</span>
            </router-link>
            <div class="sb-group">
              <div class="sb-item sb-parent" @click="toggleMenu('orders')" :class="{ 'sb-expanded': openMenus.orders }">
                📋 我的订单 <span class="sb-arrow">{{ openMenus.orders ? '▾' : '▸' }}</span>
              </div>
              <div v-if="openMenus.orders" class="sb-sub">
                <router-link to="/orders" class="sb-sub-item" active-class="sb-sub-active">全部订单</router-link>
                <router-link to="/orders?status=PENDING" class="sb-sub-item" active-class="sb-sub-active">待付款</router-link>
                <router-link to="/orders?status=CONFIRMED" class="sb-sub-item" active-class="sb-sub-active">待发货</router-link>
                <router-link to="/orders?status=SHIPPED" class="sb-sub-item" active-class="sb-sub-active">待收货</router-link>
              </div>
            </div>
            <div class="sb-group">
              <div class="sb-item sb-parent" @click="toggleMenu('profile')" :class="{ 'sb-expanded': openMenus.profile }">
                👤 个人中心 <span class="sb-arrow">{{ openMenus.profile ? '▾' : '▸' }}</span>
              </div>
              <div v-if="openMenus.profile" class="sb-sub">
                <router-link to="/profile" class="sb-sub-item" active-class="sb-sub-active">基本信息</router-link>
                <router-link to="/profile?tab=password" class="sb-sub-item" active-class="sb-sub-active">修改密码</router-link>
                <router-link to="/profile?tab=addresses" class="sb-sub-item" active-class="sb-sub-active">收货地址</router-link>
                <router-link to="/profile?tab=favorites" class="sb-sub-item" active-class="sb-sub-active">我的收藏</router-link>
              </div>
            </div>
          </template>
        </nav>
        <div class="sb-footer">
          <div class="sb-out" @click="handleLogout">退出登录</div>
        </div>
      </aside>
      <main class="main-area">
        <div class="content bg-layer"><router-view :key="$route.fullPath" /></div>
      </main>
    </div>

    <!-- ====== 未登录布局 ====== -->
    <div class="guest-layout" v-else>
      <header class="guest-nav">
        <router-link to="/" class="guest-brand">SportsStore</router-link>
        <div class="guest-links">
          <router-link to="/products" class="guest-link">浏览商品</router-link>
          <el-button size="small" @click="$router.push('/login')">登录</el-button>
          <el-button type="primary" size="small" @click="$router.push('/register')">免费注册</el-button>
        </div>
      </header>
      <div class="guest-body bg-layer"><router-view :key="$route.fullPath" /></div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const cartCount = ref(0)
const userAvatar = ref('')
const openMenus = reactive({ orders: false, profile: false })
const currentBg = ref('home')

const bgMap = {
  home: 'var(--ss-bg-home)',
  '球类': 'var(--ss-bg-ball)',
  '服装': 'var(--ss-bg-clothing)',
  '器材': 'var(--ss-bg-equipment)',
  '鞋类': 'var(--ss-bg-shoes)',
  '配件': 'var(--ss-bg-accessories)',
  admin: 'var(--ss-bg-admin)',
  cart: 'var(--ss-bg-cart)',
  order: 'var(--ss-bg-order)',
  auth: 'var(--ss-bg-auth)',
  default: 'var(--ss-bg-default)',
}

const bgStyle = computed(() => ({
  '--ss-current-bg': bgMap[currentBg.value] || bgMap.default
}))

function setBg(name) {
  currentBg.value = name
  // Also set on documentElement for any direct CSS var access
  document.documentElement.style.setProperty('--ss-current-bg', bgMap[name] || bgMap.default)
}

const toggleMenu = (key) => { openMenus[key] = !openMenus[key] }

async function fetchCartCount() {
  if (!userStore.user || userStore.isAdmin) return
  try {
    const r = await axios.get(`/api/cart/${userStore.user.customer_id}/count`)
    cartCount.value = r.data.count || 0
  } catch {}
}

async function fetchAvatar() {
  if (!userStore.user || userStore.isAdmin) return
  try {
    const r = await axios.get(`/api/customers/${userStore.user.customer_id}`)
    if (r.data.avatar) userAvatar.value = r.data.avatar
  } catch (e) {
    console.error('fetchAvatar error:', e)
  }
}

function handleLogout() {
  userStore.logout()
  router.push('/')
}

watch(route, () => {
  const p = route.path
  if (p.startsWith('/orders')) openMenus.orders = true
  if (p.startsWith('/profile')) openMenus.profile = true
  if (p === '/' || p === '/login' || p === '/register' || p === '/forgot-password') {
    setBg('home')
  } else if (p.startsWith('/admin')) {
    setBg('admin')
  } else if (p.startsWith('/cart')) {
    setBg('cart')
  } else if (p.startsWith('/orders')) {
    setBg('order')
  } else if (p === '/login' || p === '/register' || p === '/forgot-password') {
    setBg('auth')
  } else if (p.startsWith('/products')) {
    const cat = route.query.category
    if (cat && bgMap[cat]) setBg(cat)
    else setBg('default')
  } else if (p.startsWith('/profile')) {
    setBg('default')
  } else {
    setBg('default')
  }
  fetchCartCount()
}, { immediate: true })

watch(() => route.query.category, (cat) => {
  if (route.path.startsWith('/products')) {
    setBg(cat && bgMap[cat] ? cat : 'default')
  }
})

onMounted(() => {
  fetchAvatar()
  fetchCartCount()
  window.addEventListener('avatar-updated', (e) => {
    if (e.detail) userAvatar.value = e.detail
    else fetchAvatar()
  })
})
</script>

<style>
body, html { margin: 0; height: 100%; }
#app { height: 100%; }

/* ── App Shell ── */
.app-layout { display: flex; height: 100%; }

/* ── Sidebar ── */
.sidebar {
  width: 220px; min-height: 100vh;
  background: var(--ss-primary);
  display: flex; flex-direction: column; flex-shrink: 0;
  color: rgba(255,255,255,0.9);
}
.sb-head {
  height: 52px; display: flex; align-items: center; justify-content: center; gap: 6px;
  font-size: 17px; font-weight: 700; letter-spacing: 1px;
  background: rgba(0,0,0,0.10); cursor: pointer; user-select: none; color: #fff;
}
.sb-head-icon { font-size: 20px; }
.sb-user {
  padding: 16px; display: flex; align-items: center; gap: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.10);
}
.sb-av {
  width: 40px; height: 40px; border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.35);
  display: flex; align-items: center; justify-content: center;
  overflow: hidden; flex-shrink: 0;
  background: rgba(255,255,255,0.12);
}
.sb-av-img { width: 100%; height: 100%; object-fit: cover; }
.sb-av-txt { color: #fff; font-size: 16px; font-weight: 700; }
.sb-u-info { min-width: 0; }
.sb-u-name { font-size: 14px; color: #fff; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sb-u-badge {
  display: inline-block; font-size: 10px; font-weight: 700;
  color: var(--ss-primary); background: #fff;
  padding: 1px 8px; border-radius: 10px; margin-top: 2px;
}

/* ── Navigation ── */
.sb-nav { flex: 1; padding: 4px 0; overflow-y: auto; }
.sb-item {
  display: flex; align-items: center; padding: 0 20px; height: 40px;
  color: rgba(255,255,255,0.85); font-size: 13px; text-decoration: none;
  cursor: pointer; transition: background var(--ss-transition-fast); user-select: none;
}
.sb-item:hover { background: rgba(255,255,255,0.08); color: #fff; }
.sb-active { background: rgba(255,255,255,0.14); color: #fff; font-weight: 600; }
.cart-item { justify-content: space-between; }
.sb-dot {
  background: var(--ss-accent); color: #fff; font-size: 10px;
  min-width: 18px; height: 18px; line-height: 18px; text-align: center;
  border-radius: 9px; font-weight: 700;
}
.sb-parent { justify-content: space-between; }
.sb-arrow { font-size: 10px; opacity: 0.5; }
.sb-expanded { background: rgba(0,0,0,0.12); }
.sb-divider { height: 1px; background: rgba(255,255,255,0.08); margin: 4px 16px; }
.sb-sub { background: rgba(0,0,0,0.15); }
.sb-sub-item {
  display: flex; align-items: center; padding: 0 20px 0 48px; height: 36px;
  color: rgba(255,255,255,0.70); font-size: 12px; text-decoration: none;
  transition: background var(--ss-transition-fast);
}
.sb-sub-item:hover { background: rgba(255,255,255,0.06); color: #fff; }
.sb-sub-active { color: #fff; font-weight: 600; background: rgba(255,255,255,0.10); }

/* ── Sidebar Footer ── */
.sb-footer { border-top: 1px solid rgba(255,255,255,0.08); padding: 8px 16px; }
.sb-out {
  text-align: center; color: rgba(255,255,255,0.45); font-size: 12px;
  cursor: pointer; padding: 6px; border-radius: var(--ss-radius-sm);
  transition: background var(--ss-transition-fast);
}
.sb-out:hover { background: rgba(255,255,255,0.06); color: #fff; }

/* ── Main Area ── */
.main-area { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.content { flex: 1; padding: 20px 24px; overflow-y: auto; }

/* ── Guest Layout ── */
.guest-layout { height: 100%; display: flex; flex-direction: column; }
.guest-nav {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 32px; height: 56px;
  background: var(--ss-surface); border-bottom: 1px solid var(--ss-border);
}
.guest-brand { font-size: 18px; font-weight: 700; color: var(--ss-primary); text-decoration: none; letter-spacing: 1px; }
.guest-links { display: flex; align-items: center; gap: 12px; }
.guest-link { color: var(--ss-text-2); text-decoration: none; font-size: 14px; }
.guest-link:hover { color: var(--ss-primary); }
.guest-body { flex: 1; overflow-y: auto; }

/* ── Responsive ── */
@media (max-width: 768px) {
  .sidebar { width: 180px; }
  .content { padding: 14px; }
  .guest-nav { padding: 0 14px; }
}
@media (max-width: 480px) {
  .app-layout { flex-direction: column; }
  .sidebar { width: 100%; min-height: auto; }
}
</style>
