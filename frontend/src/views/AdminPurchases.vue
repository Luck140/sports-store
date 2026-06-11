<template>
  <el-card>
    <template #header><span style="font-weight:bold;font-size:16px">进货管理</span></template>
    <el-button type="primary" @click="openDialog">创建进货单</el-button>
    <el-button style="margin-left:8px" @click="showLowStock" type="warning" plain>库存预警商品</el-button>

    <el-table :data="purchases" style="margin-top:16px" empty-text="暂无进货单">
      <el-table-column prop="purchase_id" label="进货单号" />
      <el-table-column prop="manufacturer_name" label="厂家" />
      <el-table-column prop="total_amount" label="总金额" />
      <el-table-column prop="status" label="状态" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button v-if="scope.row.status==='PENDING'" type="primary" size="small" @click="confirmPurchase(scope.row.purchase_id)" :loading="confirmingId === scope.row.purchase_id">确认入库</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dialogVisible" title="创建进货单" width="550px">
    <el-form :model="form" label-width="80px">
      <el-form-item label="厂家">
        <el-select v-model="form.manufacturer_id" placeholder="请选择厂家">
          <el-option v-for="m in manufacturers" :key="m.manufacturer_id" :label="m.manufacturer_name" :value="m.manufacturer_id" />
        </el-select>
      </el-form-item>
      <el-divider>商品明细</el-divider>
      <div v-for="(item, index) in form.items" :key="index" style="margin-bottom:12px">
        <el-row :gutter="8">
          <el-col :span="6"><span style="line-height:32px">商品ID</span><el-input-number v-model="item.product_id" :min="1" style="width:100%" /></el-col>
          <el-col :span="6"><span style="line-height:32px">数量</span><el-input-number v-model="item.quantity" :min="1" style="width:100%" /></el-col>
          <el-col :span="6"><span style="line-height:32px">单价</span><el-input-number v-model="item.unit_price" :min="0" :precision="2" style="width:100%" /></el-col>
          <el-col :span="6"><el-button type="danger" @click="form.items.splice(index,1)" style="margin-top:20px">删除</el-button></el-col>
        </el-row>
      </div>
      <el-button @click="form.items.push({product_id:1,quantity:1,unit_price:0})">+ 添加商品</el-button>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible=false">取消</el-button>
      <el-button type="primary" @click="createPurchase">提交</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="lsVisible" title="库存预警商品" width="600px">
    <el-table :data="lowStockProducts" empty-text="暂无库存预警">
      <el-table-column prop="product_name" label="商品名" />
      <el-table-column prop="manufacturer_name" label="厂家" />
      <el-table-column prop="stock_quantity" label="当前库存" />
      <el-table-column prop="min_stock_threshold" label="预警值" />
      <el-table-column label="操作">
        <template #default="scope"><el-button type="primary" size="small" @click="autoGeneratePurchase(scope.row)">一键进货</el-button></template>
      </el-table-column>
    </el-table>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const purchases = ref([])
const manufacturers = ref([])
const dialogVisible = ref(false)
const confirmingId = ref(null)
const form = ref({ manufacturer_id: null, items: [{ product_id: 1, quantity: 1, unit_price: 0 }] })

const fetchPurchases = async () => { try { const res = await axios.get('/api/admin/purchases'); purchases.value = res.data } catch { ElMessage.error('加载进货单失败') } }
const fetchManufacturers = async () => { try { const res = await axios.get('/api/admin/manufacturers'); manufacturers.value = res.data } catch {} }

const openDialog = () => { dialogVisible.value = true; form.value = { manufacturer_id: null, items: [{ product_id: 1, quantity: 1, unit_price: 0 }] } }

const createPurchase = async () => {
  if (!form.value.manufacturer_id) { ElMessage.warning('请选择厂家'); return }
  try {
    await axios.post('/api/admin/purchases', form.value)
    ElMessage.success('进货单创建成功')
    dialogVisible.value = false
    fetchPurchases()
  } catch { ElMessage.error('创建失败') }
}

const lowStockProducts = ref([])
const lsVisible = ref(false)

const showLowStock = async () => {
  try { const r = await axios.get('/api/admin/reports/low-stock'); lowStockProducts.value = r.data; lsVisible.value = true } catch {}
}

const autoGeneratePurchase = async (product) => {
  try {
    const r = await axios.post('/api/admin/purchases/from-low-stock', { product_id: product.product_id })
    form.value = { manufacturer_id: r.data.manufacturer_id, items: [{ product_id: r.data.product_id, quantity: r.data.suggest_quantity, unit_price: r.data.suggest_unit_price }] }
    lsVisible.value = false; dialogVisible.value = true
  } catch { ElMessage.error('操作失败') }
}

const confirmPurchase = async (id) => {
  confirmingId.value = id
  try {
    await axios.post(`/api/admin/purchases/${id}/confirm`)
    ElMessage.success('入库成功')
    fetchPurchases()
  } catch { ElMessage.error('入库失败') }
  finally { confirmingId.value = null }
}

onMounted(() => { fetchPurchases(); fetchManufacturers() })
</script>