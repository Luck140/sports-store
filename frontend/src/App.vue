<template>
  <div id="app">
    <div class="app-layout" v-if="userStore.user">
      <aside class="sidebar">
        <div class="sb-head" @click="$router.push('/')">SportsStore</div>
        <div class="sb-userbox">
          <div class="sb-av">{{ (userStore.user.customer_name || 'U')[0] }}</div>
          <div><div class="sb-un">{{ userStore.user.customer_name || '用户' }}</div><div class="sb-ur">{{ userStore.isAdmin ? '管理员' : '顾客' }}</div></div>
        </div>
        <el-menu :default-active="currentRoute" router class="sb-menu" :default-openeds="menuOpen">
          <template v-if="userStore.isAdmin">
            <el-menu-item index="/admin"><el-icon><DataAnalysis /></el-icon>仪表盘</el-menu-item>
            <el-menu-item index="/admin/orders"><el-icon><Document /></el-icon>订单管理</el-menu-item>
            <el-menu-item index="/admin/purchases"><el-icon><Box /></el-icon>进货管理</el-menu-item>
            <el-menu-item index="/admin/reports"><el-icon><TrendCharts /></el-icon>报表中心</el-menu-item>
            <el-menu-item index="/products"><el-icon><Goods /></el-icon>商品浏览</el-menu-item>
          </template>
          <template v-else>
            <el-menu-item index="/products"><el-icon><Goods /></el-icon>商品列表</el-menu-item>
            <el-menu-item index="/cart"><el-icon><ShoppingCart /></el-icon>购物车<span v-if="cartCount" class="sb-dot">{{ cartCount }}</span></el-menu-item>
            <el-menu-item index="/orders"><el-icon><Document /></el-icon>我的订单</el-menu-item>
            <el-sub-menu index="profile-group">
              <template #title><el-icon><User /></el-icon>个人中心</template>
              <el-menu-item index="/profile">基本信息</el-menu-item>
              <el-menu-item index="/profile?tab=password">修改密码</el-menu-item>
              <el-menu-item index="/profile?tab=addresses">收货地址</el-menu-item>
              <el-menu-item index="/profile?tab=favorites">我的收藏</el-menu-item>
            </el-sub-menu>
          </template>
        </el-menu>
        <div class="sb-out" @click="handleLogout">退出登录</div>
      </aside>
      <div class="main-area">
        <div class="content"><router-view /></div>
      </div>
    </div>

    <div class="guest-layout" v-else>
      <nav class="guest-nav">
        <router-link to="/" style="font-size:18px;font-weight:700;color:var(--color-primary);text-decoration:none;letter-spacing:1px">SportsStore</router-link>
        <div style="display:flex;align-items:center;gap:14px">
          <el-button text @click="$router.push('/products')" style="color:var(--color-text-2)">浏览商品</el-button>
          <el-button size="small" @click="$router.push('/login')">登录</el-button>
          <el-button type="primary" size="small" @click="$router.push('/register')">免费注册</el-button>
        </div>
      </nav>
      <div class="guest-content"><router-view /></div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
const router = useRouter(); const route = useRoute(); const userStore = useUserStore()
const currentRoute = computed(() => route.path)
const cartCount = ref(0)
const menuOpen = computed(() => {
  if (['/profile'].includes(route.path) || route.path.startsWith('/profile')) return ['profile-group']
  return []
})
const fetchCC = async () => { if (userStore.user && !userStore.isAdmin) { try { const r = await axios.get(`/api/cart/${userStore.user.customer_id}/count`); cartCount.value = r.data.count || 0 } catch {} } }
fetchCC(); watch(currentRoute, () => { if (route.name === 'cart' || route.name === 'products') fetchCC() })
function handleLogout() { userStore.logout(); router.push('/') }
</script>

<style>
body,html { margin:0; height:100%; font-family:var(--font-family); }
#app { height:100%; }
.app-layout { display:flex; height:100%; }
.sidebar { width:220px; min-height:100vh; background:var(--color-primary); display:flex; flex-direction:column; flex-shrink:0; overflow-y:auto; }
.sb-head { height:52px; line-height:52px; text-align:center; color:#fff; font-size:17px; font-weight:700; letter-spacing:1px; background:rgba(0,0,0,0.1); cursor:pointer; }
.sb-userbox { padding:18px 16px; display:flex; align-items:center; gap:10px; border-bottom:1px solid rgba(255,255,255,0.15); }
.sb-av { width:38px; height:38px; border-radius:50%; background:rgba(255,255,255,0.25); color:#fff; display:flex; align-items:center; justify-content:center; font-size:15px; font-weight:700; flex-shrink:0; }
.sb-un { font-size:14px; color:#fff; font-weight:500; }
.sb-ur { font-size:11px; color:rgba(255,255,255,0.65); }
.sb-menu { border:none !important; background:transparent !important; flex:1; padding-top:4px; }
.sb-menu .el-menu-item,
.sb-menu .el-sub-menu .el-sub-menu__title { color:rgba(255,255,255,0.9) !important; height:44px; line-height:44px; font-size:13px; }
.sb-menu .el-menu-item:hover,
.sb-menu .el-sub-menu .el-sub-menu__title:hover { background:rgba(255,255,255,0.1) !important; color:#fff !important; }
.sb-menu .el-menu-item.is-active { background:rgba(255,255,255,0.18) !important; color:#fff !important; font-weight:600; }
.sb-menu .el-sub-menu .el-menu { background:rgba(0,0,0,0.1) !important; }
.sb-menu .el-sub-menu .el-menu .el-menu-item { padding-left:56px !important; font-size:12px; height:40px; line-height:40px; }
.sb-dot { display:inline-block; background:#fff; color:var(--color-primary); font-size:10px; min-width:18px; height:18px; line-height:18px; text-align:center; border-radius:9px; font-weight:700; margin-left:auto; }
.sb-out { padding:14px; text-align:center; color:rgba(255,255,255,0.6); font-size:12px; cursor:pointer; border-top:1px solid rgba(255,255,255,0.1); }
.sb-out:hover { color:#fff; }
.main-area { flex:1; display:flex; flex-direction:column; min-width:0; }
.content { flex:1; padding:20px 24px; overflow-y:auto; }
.guest-layout { height:100%; display:flex; flex-direction:column; }
.guest-nav { display:flex; justify-content:space-between; align-items:center; padding:0 36px; height:56px; background:#fff; border-bottom:1px solid var(--color-border); flex-shrink:0; }
.guest-content { flex:1; overflow-y:auto; }
@media (max-width:768px) { .sidebar { width:180px; } .content { padding:14px; } .guest-nav { padding:0 14px; } }
@media (max-width:480px) { .app-layout { flex-direction:column; } .sidebar { width:100%; min-height:auto; } }
</style>
