<template>
  <el-card v-loading="loading">
    <template v-if="product" #header>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span style="font-weight:bold;font-size:18px">{{ product.product_name }}</span>
        <div>
          <el-button v-if="userStore.user && !userStore.isAdmin" @click="toggleFavorite" :type="isFavorited ? 'warning' : 'default'" size="small">{{ isFavorited ? '★ 已收藏' : '☆ 收藏' }}</el-button>
          <el-button @click="$router.back()">返回</el-button>
        </div>
      </div>
    </template>
    <el-skeleton :rows="5" animated v-if="!product" />
    <template v-if="product">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="厂家">{{ product.manufacturer_name }}</el-descriptions-item>
        <el-descriptions-item label="分类">{{ product.category }}</el-descriptions-item>
        <el-descriptions-item label="单价"><span style="color:var(--color-accent);font-size:20px;font-weight:bold">¥{{ product.unit_price }}</span></el-descriptions-item>
        <el-descriptions-item label="库存">{{ product.stock_quantity > 0 ? product.stock_quantity : '已售罄' }}</el-descriptions-item>
        <el-descriptions-item label="已售">{{ product.sales_count || 0 }} 件</el-descriptions-item>
        <el-descriptions-item label="评分">{{ product.avg_rating ? product.avg_rating + ' 分 (' + product.review_count + '条评价)' : '暂无评价' }}</el-descriptions-item>
        <el-descriptions-item label="预警值">{{ product.min_stock_threshold }}</el-descriptions-item>
        <el-descriptions-item label="描述">{{ product.description || '暂无描述' }}</el-descriptions-item>
      </el-descriptions>
      <div style="margin-top:16px">
        <el-button v-if="!userStore.isAdmin && product.stock_quantity > 0" type="primary" size="large" @click="addToCart" :loading="adding">加入购物车</el-button>
        <el-button v-if="!userStore.user && product.stock_quantity > 0" type="primary" size="large" @click="$router.push('/login')">登录后购买</el-button>
      </div>
    </template>
  </el-card>

  <el-card style="margin-top:16px" v-if="product">
    <template #header><span style="font-weight:bold;font-size:16px">商品评价 ({{ reviews.length }})</span></template>
    <div v-if="reviews.length">
      <div v-for="r in reviews" :key="r.review_id" style="border-bottom:1px solid var(--color-border-light);padding:12px 0">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px">
          <span><strong>{{ r.customer_name }}</strong> <span style="color:var(--color-accent)">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</span></span>
          <span style="color:var(--color-text-muted);font-size:12px">{{ r.created_at?.slice(0,10) }}</span>
        </div>
        <p style="margin:0;color:var(--color-text-2)">{{ r.content }}</p>
      </div>
    </div>
    <el-empty v-else description="暂无评价" />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const route = useRoute()
const userStore = useUserStore()
const product = ref(null)
const reviews = ref([])
const loading = ref(true)
const adding = ref(false)
const isFavorited = ref(false)

onMounted(async () => {
  const pid = route.params.id
  try { const r = await axios.get(`/api/products/${pid}`); product.value = r.data } catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
  try { const r = await axios.get(`/api/reviews/product/${pid}`); reviews.value = r.data.items || [] } catch {}
  if (userStore.user) { try { const r = await axios.get(`/api/customers/${userStore.user.customer_id}/favorites`); isFavorited.value = r.data.some(f => f.product_id === parseInt(pid)) } catch {} }
})

const addToCart = async () => {
  adding.value = true
  try { await axios.post(`/api/cart/${userStore.user.customer_id}/add`, null, { params: { product_id: product.value.product_id, quantity: 1 } }); ElMessage.success('已加入购物车') }
  catch { ElMessage.error('添加失败') }
  finally { adding.value = false }
}

const toggleFavorite = async () => {
  if (isFavorited.value) { await axios.delete(`/api/customers/${userStore.user.customer_id}/favorites/${product.value.product_id}`); isFavorited.value = false; ElMessage.success('已取消收藏') }
  else { await axios.post(`/api/customers/${userStore.user.customer_id}/favorites/${product.value.product_id}`); isFavorited.value = true; ElMessage.success('已收藏') }
}
</script>
