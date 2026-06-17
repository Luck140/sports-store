<template>
  <div>
    <div class="page-head">
      <h2 class="page-title" style="margin:0">进货管理</h2>
      <div><el-button @click="showLowStock">库存预警</el-button><el-button type="primary" @click="openCreate" style="margin-left:8px">+ 创建进货单</el-button></div>
    </div>
    <el-card shadow="never" v-loading="loading">
      <el-table :data="purchases" style="width:100%">
        <el-table-column label="进货单号" width="120"><template #default="{row}">#{{ row.purchase_id }}</template></el-table-column>
        <el-table-column prop="manufacturer_name" label="厂家" width="160" />
        <el-table-column label="总金额" width="120"><template #default="{row}">¥{{ row.total_amount }}</template></el-table-column>
        <el-table-column label="状态" width="100"><template #default="{row}"><el-tag :type="row.status === 'COMPLETED' ? 'success' : 'warning'" size="small">{{ row.status === 'COMPLETED' ? '已完成' : '待入库' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="120"><template #default="{row}"><el-button v-if="row.status === 'PENDING'" size="small" type="primary" @click="confirmPurchase(row)">确认入库</el-button><span v-else style="color:var(--ss-text-muted)">已入库</span></template></el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="createDlg" title="创建进货单" width="600px">
      <el-form :model="purchaseForm" label-width="80px">
        <el-form-item label="厂家"><el-select v-model="purchaseForm.manufacturer_id" placeholder="选择厂家" style="width:100%"><el-option v-for="m in manufacturers" :key="m.manufacturer_id" :label="m.manufacturer_name" :value="m.manufacturer_id" /></el-select></el-form-item>
        <el-form-item label="商品明细">
          <div v-for="(item, i) in purchaseForm.items" :key="i" style="display:flex;gap:8px;margin-bottom:8px">
            <el-select v-model="item.product_id" placeholder="选择商品" filterable style="flex:2" @change="(v) => { const p = allProducts.find(x => x.product_id === v); if (p) item.unit_price = p.unit_price }"><el-option v-for="p in allProducts" :key="p.product_id" :label="p.product_name" :value="p.product_id" /></el-select>
            <el-input-number v-model="item.quantity" :min="1" style="width:100px" />
            <el-input-number v-model="item.unit_price" :precision="2" :min="0" style="width:120px" />
            <el-button text type="danger" @click="purchaseForm.items.splice(i, 1)">删除</el-button>
          </div>
          <el-button size="small" @click="purchaseForm.items.push({ product_id: null, quantity: 1, unit_price: 0 })">+ 添加商品</el-button>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="createDlg = false">取消</el-button><el-button type="primary" @click="savePurchase" :loading="saving">创建</el-button></template>
    </el-dialog>
    <el-dialog v-model="stockDlg" title="库存预警商品" width="600px">
      <el-table :data="lowStockProducts" style="width:100%">
        <el-table-column prop="product_name" label="商品名" min-width="140" />
        <el-table-column prop="manufacturer_name" label="厂家" width="120" />
        <el-table-column label="库存" width="80"><template #default="{row}"><span style="color:var(--ss-danger)">{{ row.stock_quantity }}</span></template></el-table-column>
        <el-table-column label="预警值" width="80"><template #default="{row}">{{ row.min_stock_threshold }}</template></el-table-column>
        <el-table-column label="操作" width="100"><template #default="{row}"><el-button size="small" type="primary" @click="quickPurchase(row)">一键进货</el-button></template></el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
const loading = ref(false); const purchases = ref([])
const createDlg = ref(false); const saving = ref(false); const manufacturers = ref([]); const allProducts = ref([])
const stockDlg = ref(false); const lowStockProducts = ref([])
const purchaseForm = ref({ manufacturer_id: null, items: [{ product_id: null, quantity: 1, unit_price: 0 }] })
const loadPurchases = async () => { loading.value = true; try { const r = await axios.get('/api/admin/purchases'); purchases.value = r.data } catch {} finally { loading.value = false } }
const openCreate = async () => { purchaseForm.value = { manufacturer_id: null, items: [{ product_id: null, quantity: 1, unit_price: 0 }] }; try { const r = await axios.get('/api/admin/manufacturers'); manufacturers.value = r.data } catch {}; try { const r = await axios.get('/api/admin/products'); allProducts.value = r.data } catch {}; createDlg.value = true }
const savePurchase = async () => {
  saving.value = true
  try { const items = purchaseForm.value.items.filter(i => i.product_id); if (!items.length) { ElMessage.warning('请添加商品'); return }; await axios.post('/api/admin/purchases', { manufacturer_id: purchaseForm.value.manufacturer_id, items }); ElMessage.success('创建成功'); createDlg.value = false; loadPurchases() } catch { ElMessage.error('创建失败') } finally { saving.value = false }
}
const confirmPurchase = async (po) => { try { await axios.post(`/api/admin/purchases/${po.purchase_id}/confirm`); ElMessage.success('入库成功'); loadPurchases() } catch { ElMessage.error('入库失败') } }
const showLowStock = async () => { try { const r = await axios.get('/api/admin/reports/low-stock'); lowStockProducts.value = r.data; stockDlg.value = true } catch {} }
const quickPurchase = async (p) => {
  try { const r = await axios.post('/api/admin/purchases/from-low-stock', { product_id: p.product_id }); purchaseForm.value = { manufacturer_id: r.data.manufacturer_id, items: [{ product_id: r.data.product_id, quantity: r.data.suggest_quantity, unit_price: r.data.suggest_unit_price }] }; try { const r2 = await axios.get('/api/admin/manufacturers'); manufacturers.value = r2.data } catch {}; try { const r3 = await axios.get('/api/admin/products'); allProducts.value = r3.data } catch {}; stockDlg.value = false; createDlg.value = true } catch {}
}
onMounted(loadPurchases)
</script>
<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
</style>
