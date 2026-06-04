<template>
  <div id="app">
    <!-- 已登录 -->
    <div class="app-layout" v-if="userStore.user">
      <el-menu :default-active="currentRoute" router class="sidebar" background-color="#304156" text-color="#bfcbd9" active-text-color="#409EFF">
        <div class="logo">{{ userStore.isAdmin ? '管理后台' : '体育用品' }}</div>
        <template v-if="userStore.isAdmin">
          <el-menu-item index="/admin"><el-icon><DataAnalysis /></el-icon><span>仪表盘</span></el-menu-item>
          <el-menu-item index="/admin/orders"><el-icon><Document /></el-icon><span>订单管理</span></el-menu-item>
          <el-menu-item index="/admin/purchases"><el-icon><Box /></el-icon><span>进货管理</span></el-menu-item>
          <el-menu-item index="/admin/reports"><el-icon><TrendCharts /></el-icon><span>报表中心</span></el-menu-item>
          <el-menu-item index="/products"><el-icon><Goods /></el-icon><span>商品浏览</span></el-menu-item>
        </template>
        <template v-else>
          <el-menu-item index="/products"><el-icon><Goods /></el-icon><span>商品列表</span></el-menu-item>
          <el-menu-item index="/cart"><el-icon><ShoppingCart /></el-icon><span>购物车</span></el-menu-item>
          <el-menu-item index="/orders"><el-icon><Document /></el-icon><span>我的订单</span></el-menu-item>
          <el-menu-item index="/profile"><el-icon><User /></el-icon><span>个人信息</span></el-menu-item>
        </template>
      </el-menu>
      <div class="main-area">
        <div class="topbar">
          <span>欢迎，{{ userStore.user.customer_name }}（{{ userStore.isAdmin ? '管理员' : '顾客' }}）</span>
          <el-badge :value="3" :hidden="true"><el-icon :size="20"><Bell /></el-icon></el-badge>
          <el-button type="danger" size="small" @click="handleLogout">退出登录</el-button>
        </div>
        <div class="content"><router-view /></div>
      </div>
    </div>
    <!-- 未登录 -->
    <div class="guest-layout" v-else>
      <div class="guest-nav">
        <span class="logo-text">体育用品批发销售信息系统</span>
        <div>
          <el-button @click="$router.push('/login')">登录</el-button>
          <el-button type="primary" @click="$router.push('/register')">注册</el-button>
        </div>
      </div>
      <div class="guest-content"><router-view /></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const currentRoute = computed(() => route.path)

function handleLogout() { userStore.logout(); router.push('/') }
</script>

<style>
body,html { margin:0; height:100%; font-family:'Helvetica Neue',Arial,sans-serif; }
#app { height:100%; }
.app-layout { display:flex; height:100%; }
.sidebar { width:200px; min-height:100vh; overflow-y:auto; }
.sidebar .logo { height:60px; line-height:60px; text-align:center; color:#fff; font-size:18px; font-weight:bold; background:#1f2d3d; }
.main-area { flex:1; display:flex; flex-direction:column; }
.topbar { height:50px; background:#fff; border-bottom:1px solid #e6e6e6; display:flex; align-items:center; justify-content:flex-end; padding:0 20px; gap:16px; font-size:14px; }
.content { flex:1; padding:20px; background:#f0f2f5; overflow-y:auto; }
.guest-layout { height:100%; }
.guest-nav { display:flex; justify-content:space-between; align-items:center; padding:0 40px; height:60px; background:#fff; border-bottom:1px solid #eee; }
.guest-nav .logo-text { font-size:20px; font-weight:bold; color:#303133; }
.guest-content { height:calc(100% - 60px); background:#f0f2f5; }
</style>