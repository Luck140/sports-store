<template>
  <div>
    <h2 class="page-title">订单管理</h2>
    <el-card class="filter-card" shadow="never">
      <el-row :gutter="12" align="middle">
        <el-col :span="8"><el-input v-model="keyword" placeholder="搜索订单号或顾客名" clearable @keyup.enter="load" @clear="load" /></el-col>
        <el-col :span="5"><el-select v-model="statusFilter" placeholder="全部状态" clearable style="width:100%" @change="load"><el-option label="全部状态" value="" /><el-option label="待确认" value="PENDING" /><el-option label="已确认" value="CONFIRMED" /><el-option label="已发货" value="SHIPPED" /><el-option label="已完成" value="COMPLETED" /><el-option label="缺货" value="OUT_OF_STOCK" /><el-option label="退款中" value="REFUNDING" /><el-option label="已取消" value="CANCELLED" /></el-select></el-col>
        <el-col :span="4"><el-button type="primary" size="small" @click="batchConfirm">批量确认</el-button></el-col>
        <el-col :span="4"><el-button type="success" size="small" @click="batchShip">批量发货</el-button></el-col>
      </el-row>
    </el-card>
    <el-card shadow="never" v-loading="loading">
      <el-table :data="orders" style="width:100%" @selection-change="sel => selectedIds = sel.map(s => s.order_id)">
        <el-table-column type="selection" width="40" />
        <el-table-column label="订单号" width="100"><template #default="{row}">#{{ row.order_id }}</template></el-table-column>
        <el-table-column label="顾客" width="120"><template #default="{row}"><el-button text size="small" @click="showCustomer(row)">{{ row.customer_name }}</el-button></template></el-table-column>
        <el-table-column label="金额" width="100"><template #default="{row}">¥{{ row.total_amount }}</template></el-table-column>
        <el-table-column label="状态" width="100"><template #default="{row}"><el-tag :type="tagType(row.status)" size="small">{{ statusMap[row.status] }}</el-tag></template></el-table-column>
        <el-table-column label="付款" width="80"><template #default="{row}"><el-tag :type="row.payment_status === 1 ? 'success' : 'info'" size="small">{{ row.payment_status === 1 ? '已付款' : '未付款' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" min-width="220">
          <template #default="{row}">
            <el-button size="small" @click="$router.push(`/orders/${row.order_id}`)">详情</el-button>
            <el-button v-if="row.status === 'PENDING'" size="small" type="primary" @click="confirmOrder(row)">确认</el-button>
            <el-button v-if="row.status === 'CONFIRMED'" size="small" type="success" @click="shipOrder(row)">发货</el-button>
            <el-button v-if="row.status === 'PENDING' || row.status === 'CONFIRMED'" size="small" @click="cancelOrder(row)">取消</el-button>
            <el-button v-if="row.status === 'REFUNDING'" size="small" type="success" @click="approveRefund(row)">同意退款</el-button>
            <el-button v-if="row.status === 'REFUNDING'" size="small" type="danger" @click="rejectRefund(row)">拒绝</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="text-align:center;margin-top:16px" v-if="totalPages > 1"><el-pagination background layout="prev,pager,next" :total="total" :page-size="pageSize" v-model:current-page="page" @current-change="load" /></div>
    </el-card>
    <el-dialog v-model="custDlg" title="顾客详情" width="400px">
      <div v-if="customer"><p><b>用户名：</b>{{ customer.username }}</p><p><b>姓名：</b>{{ customer.customer_name }}</p><p><b>电话：</b>{{ customer.phone }}</p><p><b>邮箱：</b>{{ customer.email }}</p><p><b>注册时间：</b>{{ formatTime(customer.created_at) }}</p><p><b>历史订单：</b>{{ customer.total_orders }} 单</p><p><b>消费总额：</b>¥{{ customer.total_spent }}</p></div>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
const orders = ref([]); const loading = ref(false); const keyword = ref(''); const statusFilter = ref('')
const page = ref(1); const total = ref(0); const pageSize = 20; const totalPages = ref(1); const selectedIds = ref([])
const custDlg = ref(false); const customer = ref(null)
const statusMap = { PENDING: '待确认', CONFIRMED: '已确认', SHIPPED: '已发货', COMPLETED: '已完成', OUT_OF_STOCK: '缺货', REFUNDING: '退款中', CANCELLED: '已取消' }
const tagType = (s) => ({ PENDING: 'warning', CONFIRMED: 'primary', SHIPPED: 'success', COMPLETED: '', OUT_OF_STOCK: 'danger', REFUNDING: 'warning', CANCELLED: 'info' }[s] || '')
const formatTime = (t) => t ? new Date(t).toLocaleString('zh-CN') : ''
const load = async () => {
  loading.value = true
  try { const p = { page: page.value, page_size: pageSize }; if (statusFilter.value) p.status = statusFilter.value; if (keyword.value) p.keyword = keyword.value; const r = await axios.get('/api/admin/orders', { params: p }); orders.value = r.data.items || []; total.value = r.data.total || 0; totalPages.value = r.data.total_pages || 1 } catch {} finally { loading.value = false }
}
const confirmOrder = async (o) => { try { await axios.post(`/api/admin/orders/${o.order_id}/confirm`); ElMessage.success('已确认'); load() } catch (e) { ElMessage.error(e.response?.data?.detail || '操作失败') } }
const shipOrder = async (o) => { try { await axios.post(`/api/admin/orders/${o.order_id}/ship`); ElMessage.success('已发货'); load() } catch (e) { ElMessage.error(e.response?.data?.detail) } }
const cancelOrder = async (o) => { try { await ElMessageBox.confirm('确定取消？'); await axios.post(`/api/admin/orders/${o.order_id}/cancel`); ElMessage.success('已取消'); load() } catch {} }
const batchConfirm = async () => { if (!selectedIds.value.length) { ElMessage.warning('请先选择订单'); return }; try { await axios.post('/api/admin/orders/batch-confirm', { order_ids: selectedIds.value }); ElMessage.success('批量确认完成'); load() } catch {} }
const batchShip = async () => { if (!selectedIds.value.length) { ElMessage.warning('请先选择订单'); return }; try { await axios.post('/api/admin/orders/batch-ship', { order_ids: selectedIds.value }); ElMessage.success('批量发货完成'); load() } catch {} }
const showCustomer = async (o) => { try { const r = await axios.get(`/api/admin/customers/${o.customer_id}`); customer.value = r.data; custDlg.value = true } catch {} }
const approveRefund = async (o) => { try { await ElMessageBox.confirm('确定同意退款？'); await axios.post('/api/payments/refund/approve', { order_id: o.order_id }); ElMessage.success('退款成功'); load() } catch {} }
const rejectRefund = async (o) => { try { await ElMessageBox.confirm('确定拒绝退款？'); await axios.post('/api/payments/refund/reject', { order_id: o.order_id }); ElMessage.success('已拒绝'); load() } catch {} }
onMounted(load)
</script>
<style scoped>
.page-title { margin: 0 0 16px; font-size: 20px; }
.filter-card { margin-bottom: 16px; }
</style>
