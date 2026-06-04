<template>
  <div>
    <el-card class="search-card">
      <el-input v-model="keyword" placeholder="搜索商品名称..." prefix-icon="Search" style="width:300px" @keyup.enter="search" clearable />
      <el-button type="primary" style="margin-left:10px" @click="search">搜索</el-button>
      <el-button v-if="userStore.isAdmin" type="success" style="margin-left:10px" @click="openAddDialog">添加商品</el-button>
    </el-card>
    <el-card style="margin-top:16px">
      <template #header><span style="font-weight:bold;font-size:16px">商品列表</span></template>
      <el-row :gutter="20">
        <el-col :span="6" v-for="p in products" :key="p.product_id">
          <el-card class="product-card" shadow="hover" @click="$router.push(`/products/${p.product_id}`)" style="cursor:pointer">
            <div class="p-img">{{ getIcon(p.product_id) }}</div>
            <div class="p-name">{{ p.product_name }}</div>
            <div class="p-price">¥{{ p.unit_price }}</div>
            <div class="p-stock">库存：{{ p.stock_quantity }}</div>
            <el-button v-if="!userStore.isAdmin" type="primary" size="small" @click.stop="addToCart(p.product_id)" style="margin-top:8px;width:100%">加入购物车</el-button>
            <el-button v-else type="warning" size="small" @click.stop="openEditDialog(p)" style="margin-top:8px;width:100%">编辑</el-button>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 添加/编辑商品弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editingProduct ? '编辑商品' : '添加商品'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="商品名称"><el-input v-model="form.product_name" /></el-form-item>
        <el-form-item label="厂家"><el-select v-model="form.manufacturer_id"><el-option v-for="m in manufacturers" :key="m.manufacturer_id" :label="m.manufacturer_name" :value="m.manufacturer_id" /></el-select></el-form-item>
        <el-form-item label="单价"><el-input-number v-model="form.unit_price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="库存"><el-input-number v-model="form.stock_quantity" :min="0" /></el-form-item>
        <el-form-item label="预警值"><el-input-number v-model="form.min_stock_threshold" :min="0" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="saveProduct">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const products = ref([])
const keyword = ref('')
const manufacturers = ref([])
const dialogVisible = ref(false)
const editingProduct = ref(null)
const form = ref({ product_name: '', manufacturer_id: 1, unit_price: 0, stock_quantity: 0, min_stock_threshold: 10, description: '' })

const icons = ['🏀','⚽','🏸','👕','⚾','🏐','🏓','🎽','🩳','🧢']
const getIcon = (id) => icons[(id - 1) % icons.length]

const fetchProducts = async () => { const res = await axios.get('/api/products/'); products.value = res.data }
const fetchManufacturers = async () => { const res = await axios.get('/api/admin/manufacturers'); manufacturers.value = res.data }
const search = async () => {
  if (keyword.value) { const res = await axios.get('/api/products/search/', { params: { keyword: keyword.value } }); products.value = res.data }
  else fetchProducts()
}
const addToCart = async (pid) => {
  await axios.post(`/api/cart/${userStore.user.customer_id}/add`, null, { params: { product_id: pid, quantity: 1 } })
  ElMessage.success('已加入购物车')
}

const openAddDialog = () => {
  editingProduct.value = null
  form.value = { product_name: '', manufacturer_id: 1, unit_price: 0, stock_quantity: 0, min_stock_threshold: 10, description: '' }
  dialogVisible.value = true
}
const openEditDialog = (p) => {
  editingProduct.value = p
  form.value = { ...p }
  dialogVisible.value = true
}
const saveProduct = async () => {
  if (editingProduct.value) {
    await axios.put(`/api/admin/products/${editingProduct.value.product_id}`, form.value)
    ElMessage.success('商品更新成功')
  } else {
    await axios.post('/api/admin/products', form.value)
    ElMessage.success('商品添加成功')
  }
  dialogVisible.value = false
  fetchProducts()
}

onMounted(() => { fetchProducts(); if (userStore.isAdmin) fetchManufacturers() })
</script>

<style scoped>
.search-card { margin-bottom:16px; }
.product-card { text-align:center; margin-bottom:16px; }
.p-img { font-size:60px; margin-bottom:8px; }
.p-name { font-size:14px; font-weight:bold; margin-bottom:4px; }
.p-price { color:#f56c6c; font-size:18px; font-weight:bold; }
.p-stock { font-size:12px; color:#909399; margin-bottom:4px; }
</style>