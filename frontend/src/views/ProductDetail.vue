<template>
  <el-card v-if="product">
    <template #header><span style="font-weight:bold;font-size:18px">{{ product.product_name }}</span></template>
    <p><strong>厂家：</strong>{{ product.manufacturer_name }}</p>
    <p><strong>单价：</strong><span style="color:#f56c6c;font-size:20px">¥{{ product.unit_price }}</span></p>
    <p><strong>库存：</strong>{{ product.stock_quantity }}</p>
    <p><strong>最低预警：</strong>{{ product.min_stock_threshold }}</p>
    <p><strong>描述：</strong>{{ product.description || '暂无描述' }}</p>
    <el-button type="primary" size="large" @click="addToCart">加入购物车</el-button>
    <el-button @click="$router.back()">返回</el-button>
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

onMounted(async () => {
  const res = await axios.get(`/api/products/${route.params.id}`)
  product.value = res.data
})

const addToCart = async () => {
  await axios.post(`/api/cart/${userStore.user.customer_id}/add`, null, { params: { product_id: product.value.product_id, quantity: 1 } })
  ElMessage.success('已加入购物车')
}
</script>