<template>
  <div v-loading="loading">
    <div class="breadcrumb">
      <router-link to="/">首页</router-link><span>/</span><router-link to="/orders">我的订单</router-link><span>/</span><span>订单详情</span>
    </div>
    <div v-if="!order" class="not-found">订单不存在</div>
    <template v-else>
      <el-card class="info-card">
        <div class="info-head">
          <b class="info-title">订单 #{{ order.order_id }}</b>
          <div class="info-tags"><el-tag :type="tagType(order.status)">{{ statusMap[order.status] }}</el-tag><el-tag v-if="order.payment_status === 1" type="success">已付款</el-tag><el-tag v-else type="info">未付款</el-tag></div>
        </div>
        <el-descriptions :column="2" border style="margin-top:12px">
          <el-descriptions-item label="商品金额">¥{{ (order.total_amount - order.shipping_cost).toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="运费">¥{{ order.shipping_cost }}</el-descriptions-item>
          <el-descriptions-item label="实付金额"><b class="text-accent">¥{{ order.total_amount }}</b></el-descriptions-item>
          <el-descriptions-item label="货物重量">{{ order.total_weight }} kg</el-descriptions-item>
          <el-descriptions-item label="收件人">{{ order.recipient_name }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ order.recipient_phone }}</el-descriptions-item>
          <el-descriptions-item label="收件地址" :span="2">{{ order.recipient_address }}</el-descriptions-item>
          <el-descriptions-item label="运输要求">{{ order.shipping_req || '无' }}</el-descriptions-item>
          <el-descriptions-item label="发票类型">{{ {0:'不需要',1:'增值税普通发票',2:'增值税专用发票'}[order.invoice_required] || '不需要' }}</el-descriptions-item>
          <el-descriptions-item v-if="order.invoice_required" label="发票抬头">{{ order.invoice_title }}</el-descriptions-item>
          <el-descriptions-item v-if="order.invoice_tax_no" label="税号">{{ order.invoice_tax_no }}</el-descriptions-item>
          <el-descriptions-item v-if="order.invoice_address_phone" label="地址电话">{{ order.invoice_address_phone }}</el-descriptions-item>
          <el-descriptions-item v-if="order.invoice_bank" label="开户行及账号">{{ order.invoice_bank }}</el-descriptions-item>
        </el-descriptions>
      </el-card>
      <el-card class="timeline-card">
        <template #header><span class="section-title">订单进度</span></template>
        <el-timeline>
          <el-timeline-item v-for="t in timeline" :key="t.title" :timestamp="formatTime(t.time)" placement="top">
            <h4>{{ t.title }}</h4>
            <p style="color:var(--ss-text-muted);font-size:13px">{{ t.desc }}</p>
          </el-timeline-item>
        </el-timeline>
      </el-card>
      <el-card class="detail-card">
        <template #header><span class="section-title">商品明细</span></template>
        <el-table :data="details" style="width:100%">
          <el-table-column prop="product_name" label="商品名称" />
          <el-table-column label="单价" width="100"><template #default="{row}">¥{{ row.unit_price }}</template></el-table-column>
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column label="金额" width="120"><template #default="{row}">¥{{ row.total_amount }}</template></el-table-column>
        </el-table>
      </el-card>
      <el-card class="payments-card">
        <template #header><span class="section-title">付款记录</span></template>
        <el-table v-if="payments.length" :data="payments" style="width:100%">
          <el-table-column prop="payment_method" label="支付方式" />
          <el-table-column label="金额" width="120"><template #default="{row}">¥{{ row.amount }}</template></el-table-column>
          <el-table-column prop="status" label="状态" width="100"><template #default="{row}"><el-tag :type="row.status === 'SUCCESS' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag></template></el-table-column>
          <el-table-column prop="transaction_id" label="流水号" min-width="180" />
        </el-table>
        <div v-else class="none-text">暂无付款记录</div>
      </el-card>
    </template>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
const route = useRoute()
const order = ref(null); const details = ref([]); const timeline = ref([]); const payments = ref([]); const loading = ref(true)
const statusMap = { PENDING: '待确认', CONFIRMED: '已确认', SHIPPED: '已发货', COMPLETED: '已完成', OUT_OF_STOCK: '缺货', REFUNDING: '退款中', CANCELLED: '已取消' }
const tagType = (s) => ({ PENDING: 'warning', CONFIRMED: 'primary', SHIPPED: 'success', COMPLETED: '', OUT_OF_STOCK: 'danger', REFUNDING: 'warning', CANCELLED: 'info' }[s] || '')
const formatTime = (t) => t ? new Date(t).toLocaleString('zh-CN') : ''
onMounted(async () => {
  const id = route.params.id
  try {
    const [o, d, t, p] = await Promise.all([axios.get(`/api/orders/${id}`), axios.get(`/api/orders/${id}/details`), axios.get(`/api/orders/${id}/timeline`), axios.get(`/api/payments/order/${id}`)])
    order.value = o.data; details.value = d.data; timeline.value = t.data; payments.value = p.data
  } catch {} finally { loading.value = false }
})
</script>
<style scoped>
.breadcrumb { display: flex; gap: 6px; margin-bottom: 14px; font-size: 13px; color: var(--ss-text-muted); }
.breadcrumb a { color: var(--ss-text-muted); text-decoration: none; }
.not-found { padding: 60px; text-align: center; color: var(--ss-text-muted); }
.info-card { margin-bottom: 16px; }
.info-head { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.info-title { font-size: 16px; }
.info-tags { display: flex; gap: 6px; }
.section-title { font-weight: 600; font-size: 15px; }
.timeline-card, .detail-card { margin-bottom: 16px; }
.none-text { color: var(--ss-text-muted); text-align: center; padding: 20px; }
</style>
