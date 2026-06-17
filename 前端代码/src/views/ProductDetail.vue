<template>
  <div>
    <div class="breadcrumb">
      <router-link to="/">首页</router-link><span>/</span>
      <router-link to="/products">商品列表</router-link><span>/</span>
      <span>{{ product?.product_name || '商品详情' }}</span>
    </div>
    <div v-loading="loading">
      <div v-if="!product" class="not-found">商品未找到</div>
      <el-row :gutter="24" v-else>
        <el-col :xs="24" :md="10">
          <div class="detail-img-wrap">
            <span class="detail-img">{{ getIcon(product) }}</span>
          </div>
        </el-col>
        <el-col :xs="24" :md="14">
          <h1 class="detail-title">{{ product.product_name }}</h1>
          <div class="detail-tags">
            <el-tag size="small">{{ product.category }}</el-tag>
            <el-tag size="small" type="info">{{ product.manufacturer_name }}</el-tag>
          </div>
          <div class="detail-price">¥{{ product.unit_price }}</div>
          <div class="detail-meta">
            <span>库存：<b :style="{ color: product.stock_quantity > 10 ? 'var(--ss-success)' : 'var(--ss-warning)' }">{{ product.stock_quantity }}</b></span>
            <span>已售：<b>{{ product.sales_count || 0 }}</b></span>
            <span>评分：<b>{{ product.avg_rating || '暂无' }}</b> <span v-if="product.review_count">({{ product.review_count }}条)</span></span>
          </div>
          <div class="detail-threshold" v-if="product.min_stock_threshold">库存预警值：{{ product.min_stock_threshold }}</div>
          <div class="detail-desc">{{ product.description || '暂无描述' }}</div>
          <div class="detail-actions">
            <el-button v-if="userStore.user && !userStore.isAdmin" type="primary" @click="addCart">加入购物车</el-button>
            <el-button v-if="!userStore.user" type="primary" @click="$router.push('/login')">登录后购买</el-button>
            <el-button v-if="userStore.user && !userStore.isAdmin" :type="isFav ? 'primary' : 'default'" @click="toggleFav">
              {{ isFav ? '❤️ 已收藏' : '🤍 收藏' }}
            </el-button>
          </div>
        </el-col>
      </el-row>
      <!-- 评价 -->
      <el-card class="review-section" v-if="product">
        <template #header><span class="review-hd">商品评价</span></template>
        <div v-if="reviews.length === 0" class="review-empty">暂无评价</div>
        <div v-for="r in reviews" :key="r.review_id" class="review-item">
          <div class="review-head">
            <span><b>{{ r.customer_name }}</b> <span class="stars">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</span></span>
            <span class="review-time">{{ formatTime(r.created_at) }}</span>
          </div>
          <div class="review-body">{{ r.content }}</div>
        </div>
        <div style="text-align:center;margin-top:14px" v-if="reviewTotal > reviewPageSize">
          <el-pagination background small layout="prev,pager,next" :total="reviewTotal" :page-size="reviewPageSize" v-model:current-page="reviewPage" @current-change="loadReviews" />
        </div>
      </el-card>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { getProductIcon } from '@/utils/productIcons'
const route = useRoute(); const router = useRouter(); const userStore = useUserStore()
const product = ref(null); const loading = ref(true)
const reviews = ref([]); const reviewPage = ref(1); const reviewTotal = ref(0); const reviewPageSize = 5
const isFav = ref(false)
const icons = ['🏀', '⚽', '🏸', '👕', '⚾', '🏐', '🏓', '🎽', '🩳', '🧢']
const getIcon = (p) => getProductIcon(p)
const formatTime = (t) => t ? new Date(t).toLocaleString('zh-CN') : ''
const addCart = async () => {
  try { await axios.post(`/api/cart/${userStore.user.customer_id}/add`, null, { params: { product_id: product.value.product_id, quantity: 1 } }); ElMessage.success('已加入购物车') } catch (e) { ElMessage.error(e.response?.data?.detail || '添加失败') }
}
const toggleFav = async () => {
  if (!userStore.user) { ElMessage.warning('请先登录'); return }
  try {
    if (isFav.value) {
      await axios.delete(`/api/customers/${userStore.user.customer_id}/favorites/${product.value.product_id}`)
      isFav.value = false
      ElMessage.success('已取消收藏')
    } else {
      await axios.post(`/api/customers/${userStore.user.customer_id}/favorites/${product.value.product_id}`)
      isFav.value = true
      ElMessage.success('收藏成功')
    }
  } catch (e) {
    const msg = e.response?.data?.detail || e.message || '操作失败'
    ElMessage.error(msg)
  }
}
const loadReviews = async () => {
  try { const r = await axios.get(`/api/reviews/product/${route.params.id}`, { params: { page: reviewPage.value, page_size: reviewPageSize } }); reviews.value = r.data.items || []; reviewTotal.value = r.data.total || 0 } catch {}
}
onMounted(async () => {
  try {
    const id = route.params.id; const r = await axios.get(`/api/products/${id}`); product.value = r.data
    if (userStore.user && !userStore.isAdmin) { try { const f = await axios.get(`/api/customers/${userStore.user.customer_id}/favorites`); isFav.value = f.data.some(x => x.product_id == id) } catch {} }
    loadReviews()
  } catch { ElMessage.error('加载失败') } finally { loading.value = false }
})
</script>
<style scoped>
.breadcrumb { display: flex; gap: 6px; margin-bottom: 14px; font-size: 13px; color: var(--ss-text-muted); }
.breadcrumb a { color: var(--ss-text-muted); text-decoration: none; }
.not-found { padding: 60px; text-align: center; color: var(--ss-text-muted); }
.detail-img-wrap { font-size: 120px; text-align: center; background: var(--ss-surface); border-radius: var(--ss-radius-sm); border: 1px solid var(--ss-border-light); padding: 40px; }
.detail-title { font-size: 22px; font-weight: 600; margin: 0 0 8px; }
.detail-tags { display: flex; gap: 8px; margin-bottom: 12px; }
.detail-price { font-size: 28px; font-weight: 700; color: var(--ss-accent); margin-bottom: 14px; }
.detail-meta { display: flex; gap: 20px; font-size: 13px; margin-bottom: 10px; color: var(--ss-text-2); }
.detail-threshold { font-size: 12px; color: var(--ss-text-muted); margin-bottom: 14px; }
.detail-desc { font-size: 14px; color: var(--ss-text-2); margin-bottom: 20px; line-height: 1.8; }
.detail-actions { display: flex; gap: 12px; }
.review-section { margin-top: 28px; }
.review-hd { font-weight: 600; font-size: 15px; }
.review-empty { color: var(--ss-text-muted); padding: 20px 0; text-align: center; }
.review-item { padding: 12px 0; border-bottom: 1px solid var(--ss-border-light); }
.review-head { display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 13px; }
.review-time { color: var(--ss-text-muted); }
.stars { color: #f0ad4e; }
.review-body { font-size: 13px; color: var(--ss-text-2); }
</style>
