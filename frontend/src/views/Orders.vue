<template>
  <el-card>
    <template #header><span style="font-weight:bold;font-size:16px">我的订单</span></template>
    <el-table :data="orders" empty-text="暂无订单">
      <el-table-column prop="order_id" label="订单号">
        <template #default="scope"><router-link :to="`/orders/${scope.row.order_id}`">#{{ scope.row.order_id }}</router-link></template>
      </el-table-column>
      <el-table-column prop="total_amount" label="金额">
        <template #default="scope"><span style="color:#f56c6c;font-weight:bold">¥{{ scope.row.total_amount }}</span></template>
      </el-table-column>
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          <el-tag v-if="scope.row.status==='PENDING'" type="warning">待确认</el-tag>
          <el-tag v-else-if="scope.row.status==='CONFIRMED'" type="primary">已确认</el-tag>
          <el-tag v-else-if="scope.row.status==='SHIPPED'" type="success">已发货</el-tag>
          <el-tag v-else-if="scope.row.status==='OUT_OF_STOCK'" type="danger">缺货</el-tag>
          <el-tag v-else-if="scope.row.status==='CANCELLED'" type="info">已取消</el-tag>
          <el-tag v-else>{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="付款">
        <template #default="scope">{{ scope.row.payment_status===1?'已付':scope.row.payment_status===2?'已退款':'未付' }}</template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button v-if="scope.row.payment_status===0" type="success" size="small" @click="showPayDialog(scope.row)">支付</el-button>
          <el-button v-if="scope.row.status==='SHIPPED'&&scope.row.payment_status===1" type="warning" size="small" @click="refund(scope.row.order_id)">退款</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="payVisible" title="确认支付" width="400px">
      <p>订单号：{{ payOrder?.order_id }}</p>
      <p>金额：<strong style="color:#f56c6c">¥{{ payOrder?.total_amount }}</strong></p>
      <el-radio-group v-model="payMethod">
        <el-radio label="ALIPAY">支付宝</el-radio>
        <el-radio label="WECHAT">微信支付</el-radio>
        <el-radio label="CREDIT_CARD">信用卡</el-radio>
      </el-radio-group>
      <template #footer>
        <el-button @click="payVisible=false">取消</el-button>
        <el-button type="primary" @click="doPay">确认支付</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const orders = ref([])
const payVisible = ref(false)
const payOrder = ref(null)
const payMethod = ref('ALIPAY')

const fetchOrders = async () => {
  const res = await axios.get(`/api/orders/customer/${userStore.user.customer_id}`)
  orders.value = res.data
}

const showPayDialog = (order) => { payOrder.value = order; payVisible.value = true }
const doPay = async () => {
  await axios.post('/api/payments/', { order_id: payOrder.value.order_id, payment_method: payMethod.value, amount: payOrder.value.total_amount })
  ElMessage.success('支付成功')
  payVisible.value = false
  fetchOrders()
}

const refund = async (orderId) => {
  if (!confirm('确认退款？')) return
  await axios.post('/api/payments/refund', { order_id: orderId, reason: '顾客申请退款' })
  ElMessage.success('退款成功')
  fetchOrders()
}

onMounted(fetchOrders)
</script>