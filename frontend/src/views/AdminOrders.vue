<template>
  <el-card>
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
        <span style="font-weight:bold;font-size:16px">订单管理</span>
        <div style="display:flex;gap:8px">
          <el-input v-model="searchKeyword" placeholder="订单号或顾客名" size="small" style="width:180px" clearable @change="fetchOrders" />
          <el-select v-model="statusFilter" size="small" placeholder="全部状态" clearable style="width:120px" @change="fetchOrders">
            <el-option label="待确认" value="PENDING" /><el-option label="已确认" value="CONFIRMED" /><el-option label="已发货" value="SHIPPED" /><el-option label="已完成" value="COMPLETED" /><el-option label="缺货" value="OUT_OF_STOCK" /><el-option label="退款中" value="REFUNDING" /><el-option label="已取消" value="CANCELLED" />
          </el-select>
          <el-button type="warning" size="small" @click="batchConfirm" :disabled="!selected.length">批量确认</el-button>
          <el-button type="success" size="small" @click="batchShip" :disabled="!selected.length">批量发货</el-button>
        </div>
      </div>
    </template>
    <el-table :data="orders" v-loading="loading" @selection-change="handleSelection">
      <el-table-column type="selection" width="40" />
      <el-table-column prop="order_id" label="订单号" width="80" />
      <el-table-column prop="customer_name" label="顾客" width="100">
        <template #default="scope"><el-button link type="primary" @click="showCustomer(scope.row.customer_id)">{{ scope.row.customer_name }}</el-button></template>
      </el-table-column>
      <el-table-column prop="total_amount" label="金额" width="90" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.status==='PENDING'" type="warning">待确认</el-tag>
          <el-tag v-else-if="scope.row.status==='CONFIRMED'" type="primary">已确认</el-tag>
          <el-tag v-else-if="scope.row.status==='SHIPPED'" type="success">已发货</el-tag>
          <el-tag v-else-if="scope.row.status==='COMPLETED'" type="success">已完成</el-tag>
          <el-tag v-else-if="scope.row.status==='OUT_OF_STOCK'" type="danger">缺货</el-tag>
          <el-tag v-else-if="scope.row.status==='REFUNDING'" type="warning">退款中</el-tag>
          <el-tag v-else-if="scope.row.status==='CANCELLED'" type="info">已取消</el-tag>
          <el-tag v-else>{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="详情" width="150">
        <template #default="scope"><el-button size="small" @click="showInvoice(scope.row)">发票</el-button><el-button size="small" @click="showShipping(scope.row)">邮寄</el-button><el-button size="small" @click="showPayments(scope.row)">付款</el-button></template>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template #default="scope">
          <el-button v-if="scope.row.status==='PENDING'" type="primary" size="small" @click="doAction('confirm', scope.row.order_id)">确认</el-button>
          <el-button v-if="scope.row.status==='CONFIRMED'" type="success" size="small" @click="doAction('ship', scope.row.order_id)">发货</el-button>
          <el-button v-if="scope.row.status==='REFUNDING'" type="success" size="small" @click="approveRefund(scope.row.order_id)">同意退款</el-button>
          <el-button v-if="scope.row.status==='REFUNDING'" type="danger" size="small" @click="rejectRefund(scope.row.order_id)">拒绝退款</el-button>
          <el-button v-if="scope.row.status!=='SHIPPED'&&scope.row.status!=='CANCELLED'&&scope.row.status!=='COMPLETED'&&scope.row.status!=='REFUNDING'" type="danger" size="small" @click="doAction('cancel', scope.row.order_id)">取消</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div style="text-align:center;margin-top:16px" v-if="totalPages > 1">
      <el-pagination background layout="prev, pager, next" :total="total" :page-size="pageSize" v-model:current-page="currentPage" @current-change="handlePageChange" />
    </div>

    <el-dialog v-model="invoiceVisible" title="发票信息" width="400px"><p><strong>发票抬头：</strong>{{ currentOrder?.invoice_title || '无' }}</p><p><strong>税号：</strong>{{ currentOrder?.invoice_tax_no || '无' }}</p><p><strong>需要发票：</strong>{{ currentOrder?.invoice_required ? '是' : '否' }}</p></el-dialog>
    <el-dialog v-model="shippingVisible" title="邮寄信息" width="400px"><p><strong>收件人：</strong>{{ currentOrder?.recipient_name || '无' }}</p><p><strong>电话：</strong>{{ currentOrder?.recipient_phone || '无' }}</p><p><strong>地址：</strong>{{ currentOrder?.recipient_address || '无' }}</p><p><strong>重量：</strong>{{ currentOrder?.total_weight || 0 }} kg</p><p><strong>要求：</strong>{{ currentOrder?.shipping_req || '无' }}</p></el-dialog>
    <el-dialog v-model="paymentsVisible" title="付款清单" width="500px"><el-table :data="payments"><el-table-column prop="payment_method" label="方式" /><el-table-column prop="amount" label="金额" /><el-table-column prop="status" label="状态" /><el-table-column prop="transaction_id" label="流水号" /><el-table-column prop="payment_time" label="时间" /></el-table></el-dialog>
    <el-dialog v-model="customerVisible" title="顾客详情" width="400px"><el-descriptions v-if="custDetail" :column="1" border size="small"><el-descriptions-item label="姓名">{{ custDetail.customer_name }}</el-descriptions-item><el-descriptions-item label="电话">{{ custDetail.phone }}</el-descriptions-item><el-descriptions-item label="邮箱">{{ custDetail.email }}</el-descriptions-item><el-descriptions-item label="地址">{{ custDetail.address }}</el-descriptions-item><el-descriptions-item label="注册时间">{{ custDetail.created_at?.slice(0,10) }}</el-descriptions-item><el-descriptions-item label="订单数">{{ custDetail.total_orders }}</el-descriptions-item><el-descriptions-item label="消费总额">¥{{ custDetail.total_spent }}</el-descriptions-item></el-descriptions></el-dialog>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const orders = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const totalPages = ref(1)
const searchKeyword = ref('')
const statusFilter = ref('')
const selected = ref([])
const invoiceVisible = ref(false)
const shippingVisible = ref(false)
const paymentsVisible = ref(false)
const currentOrder = ref(null)
const payments = ref([])
const customerVisible = ref(false)
const custDetail = ref(null)

const fetchOrders = async (page) => {
  loading.value = true
  try {
    const params = { page: page || currentPage.value, page_size: pageSize.value }
    if (statusFilter.value) params.status = statusFilter.value
    if (searchKeyword.value) params.keyword = searchKeyword.value
    const r = await axios.get('/api/admin/orders', { params })
    orders.value = r.data.items; total.value = r.data.total; totalPages.value = r.data.total_pages
  } catch {} finally { loading.value = false }
}
const handlePageChange = (p) => { currentPage.value = p; fetchOrders(p) }
const handleSelection = (rows) => { selected.value = rows.map(r => r.order_id) }

const doAction = async (act, id) => {
  const actions = { confirm: ['/api/admin/orders/', '/confirm', '已确认'], ship: ['/api/admin/orders/', '/ship', '已发货'], cancel: ['/api/admin/orders/', '/cancel', '已取消'] }
  const [base, suffix, msg] = actions[act]
  try { await axios.post(base + id + suffix); ElMessage.success(msg); fetchOrders(currentPage.value) }
  catch (e) { ElMessage.error(e.response?.data?.detail || '操作失败') }
}

const batchConfirm = async () => { if (!selected.value.length) return; try { await axios.post('/api/admin/orders/batch-confirm', { order_ids: selected.value }); ElMessage.success('批量确认完成'); fetchOrders() } catch {} }
const batchShip = async () => { if (!selected.value.length) return; try { await axios.post('/api/admin/orders/batch-ship', { order_ids: selected.value }); ElMessage.success('批量发货完成'); fetchOrders() } catch {} }

const approveRefund = async (id) => { try { await axios.post(`/api/payments/refund-approve/${id}`); ElMessage.success('退款审核通过'); fetchOrders() } catch (e) { ElMessage.error(e.response?.data?.detail || '操作失败') } }
const rejectRefund = async (id) => { try { await axios.post(`/api/payments/refund-reject/${id}`); ElMessage.success('退款已拒绝'); fetchOrders() } catch (e) { ElMessage.error(e.response?.data?.detail || '操作失败') } }

const showInvoice = (o) => { currentOrder.value = o; invoiceVisible.value = true }
const showShipping = (o) => { currentOrder.value = o; shippingVisible.value = true }
const showPayments = async (o) => { currentOrder.value = o; const r = await axios.get(`/api/payments/order/${o.order_id}`); payments.value = r.data; paymentsVisible.value = true }
const showCustomer = async (cid) => { try { const r = await axios.get(`/api/admin/customers/${cid}`); custDetail.value = r.data; customerVisible.value = true } catch {} }

onMounted(() => fetchOrders())
</script>
