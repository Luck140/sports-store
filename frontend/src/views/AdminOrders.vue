<template>
  <el-card>
    <template #header><span style="font-weight:bold;font-size:16px">订单管理</span></template>
    <el-table :data="orders" v-loading="loading">
      <el-table-column prop="order_id" label="订单号" width="80" />
      <el-table-column prop="customer_name" label="顾客" width="100" />
      <el-table-column prop="total_amount" label="金额" width="80" />
      <el-table-column prop="status" label="状态" width="90">
        <template #default="scope">
          <el-tag v-if="scope.row.status==='PENDING'" type="warning">待确认</el-tag>
          <el-tag v-else-if="scope.row.status==='CONFIRMED'" type="primary">已确认</el-tag>
          <el-tag v-else-if="scope.row.status==='SHIPPED'" type="success">已发货</el-tag>
          <el-tag v-else-if="scope.row.status==='OUT_OF_STOCK'" type="danger">缺货</el-tag>
          <el-tag v-else-if="scope.row.status==='CANCELLED'" type="info">已取消</el-tag>
          <el-tag v-else>{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="详情" width="180">
        <template #default="scope">
          <el-button size="small" @click="showInvoice(scope.row)">发票</el-button>
          <el-button size="small" @click="showShipping(scope.row)">邮寄</el-button>
          <el-button size="small" @click="showPayments(scope.row)">付款</el-button>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="scope">
          <el-button v-if="scope.row.status==='PENDING'" type="primary" size="small" @click="confirm(scope.row.order_id)" :loading="actingOrder === scope.row.order_id && action === 'confirm'">确认</el-button>
          <el-button v-if="scope.row.status==='CONFIRMED'" type="success" size="small" @click="ship(scope.row.order_id)" :loading="actingOrder === scope.row.order_id && action === 'ship'">发货</el-button>
          <el-button v-if="scope.row.status!=='SHIPPED'&&scope.row.status!=='CANCELLED'" type="danger" size="small" @click="cancel(scope.row.order_id)" :loading="actingOrder === scope.row.order_id && action === 'cancel'">取消</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 发票弹窗 -->
    <el-dialog v-model="invoiceVisible" title="发票信息" width="400px">
      <p><strong>发票抬头：</strong>{{ currentOrder?.invoice_title || '无' }}</p>
      <p><strong>税号：</strong>{{ currentOrder?.invoice_tax_no || '无' }}</p>
      <p><strong>是否需要发票：</strong>{{ currentOrder?.invoice_required ? '是' : '否' }}</p>
    </el-dialog>

    <!-- 邮寄信息弹窗 -->
    <el-dialog v-model="shippingVisible" title="邮寄信息" width="400px">
      <p><strong>收件人：</strong>{{ currentOrder?.recipient_name || '无' }}</p>
      <p><strong>电话：</strong>{{ currentOrder?.recipient_phone || '无' }}</p>
      <p><strong>地址：</strong>{{ currentOrder?.recipient_address || '无' }}</p>
      <p><strong>重量：</strong>{{ currentOrder?.total_weight || 0 }} kg</p>
      <p><strong>运输要求：</strong>{{ currentOrder?.shipping_req || '无' }}</p>
    </el-dialog>

    <!-- 付款清单弹窗 -->
    <el-dialog v-model="paymentsVisible" title="付款清单" width="500px">
      <el-table :data="payments">
        <el-table-column prop="payment_method" label="方式" />
        <el-table-column prop="amount" label="金额" />
        <el-table-column prop="status" label="状态" />
        <el-table-column prop="transaction_id" label="流水号" />
        <el-table-column prop="payment_time" label="时间" />
      </el-table>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const orders = ref([])
const loading = ref(false)
const invoiceVisible = ref(false)
const shippingVisible = ref(false)
const paymentsVisible = ref(false)
const currentOrder = ref(null)
const payments = ref([])
const actingOrder = ref(null)
const action = ref('')

const fetchOrders = async () => {
  loading.value = true
  try { const res = await axios.get('/api/admin/orders'); orders.value = res.data }
  catch { ElMessage.error('加载订单失败') }
  finally { loading.value = false }
}

const doAction = async (id, act, url, successMsg) => {
  actingOrder.value = id; action.value = act
  try { await axios.post(url); ElMessage.success(successMsg); fetchOrders() }
  catch { ElMessage.error('操作失败') }
  finally { actingOrder.value = null; action.value = '' }
}

const confirm = (id) => doAction(id, 'confirm', `/api/admin/orders/${id}/confirm`, '已确认')
const ship = (id) => doAction(id, 'ship', `/api/admin/orders/${id}/ship`, '已发货')
const cancel = (id) => doAction(id, 'cancel', `/api/admin/orders/${id}/cancel`, '已取消')

const showInvoice = (order) => { currentOrder.value = order; invoiceVisible.value = true }
const showShipping = (order) => { currentOrder.value = order; shippingVisible.value = true }
const showPayments = async (order) => {
  currentOrder.value = order
  const res = await axios.get(`/api/payments/order/${order.order_id}`)
  payments.value = res.data
  paymentsVisible.value = true
}

onMounted(fetchOrders)
</script>