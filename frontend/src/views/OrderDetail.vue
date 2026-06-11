<template>
  <div v-loading="loading">
    <el-card style="margin-bottom:12px" v-if="order">
      <template #header><span style="font-weight:bold;font-size:16px">订单 #{{ $route.params.id }}</span></template>
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="订单状态"><el-tag :type="statusType(order.status)">{{ statusText(order.status) }}</el-tag></el-descriptions-item>
        <el-descriptions-item label="付款状态">{{ order.payment_status===1?'已付款':order.payment_status===2?'已退款':'未付款' }}</el-descriptions-item>
        <el-descriptions-item label="商品金额">¥{{ order.total_amount }}</el-descriptions-item>
        <el-descriptions-item label="运费">¥{{ order.shipping_cost || 0 }}</el-descriptions-item>
        <el-descriptions-item label="实付金额"><strong style="color:var(--color-accent)">¥{{ (parseFloat(order.total_amount||0)+parseFloat(order.shipping_cost||0)).toFixed(2) }}</strong></el-descriptions-item>
        <el-descriptions-item label="货物重量">{{ order.total_weight || 0 }} kg</el-descriptions-item>
        <el-descriptions-item label="收件人">{{ order.recipient_name }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ order.recipient_phone }}</el-descriptions-item>
        <el-descriptions-item label="收件地址">{{ order.recipient_address }}</el-descriptions-item>
        <el-descriptions-item label="运输要求">{{ order.shipping_req || '无' }}</el-descriptions-item>
        <el-descriptions-item label="发票抬头" v-if="order.invoice_required">{{ order.invoice_title }}</el-descriptions-item>
        <el-descriptions-item label="发票税号" v-if="order.invoice_required">{{ order.invoice_tax_no }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card style="margin-bottom:12px">
      <template #header><span style="font-weight:bold;font-size:15px">订单时间轴</span></template>
      <el-timeline v-if="timeline.length">
        <el-timeline-item v-for="t in timeline" :key="t.title" :timestamp="t.time?.slice(0,16) || ''" placement="top">
          <div><strong>{{ t.title }}</strong><p style="margin:4px 0 0 0;color:var(--color-text-muted);font-size:13px" v-if="t.desc">{{ t.desc }}</p></div>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无数据" />
    </el-card>

    <el-card style="margin-bottom:12px">
      <template #header><span style="font-weight:bold;font-size:15px">商品明细</span></template>
      <el-table :data="details">
        <el-table-column label="商品" min-width="150"><template #default="scope">{{ scope.row.product_name }}</template></el-table-column>
        <el-table-column label="单价" width="100"><template #default="scope">¥{{ scope.row.unit_price }}</template></el-table-column>
        <el-table-column label="数量" width="80"><template #default="scope">{{ scope.row.quantity }}</template></el-table-column>
        <el-table-column label="小计" width="100"><template #default="scope">¥{{ scope.row.total_amount }}</template></el-table-column>
      </el-table>
    </el-card>

    <el-card>
      <template #header><span style="font-weight:bold;font-size:15px">付款记录</span></template>
      <el-table :data="payments">
        <el-table-column prop="payment_method" label="方式" width="100" />
        <el-table-column prop="amount" label="金额" width="100" />
        <el-table-column prop="status" label="状态" width="90"><template #default="scope"><el-tag :type="scope.row.status==='SUCCESS'?'success':'info'" size="small">{{ scope.row.status }}</el-tag></template></el-table-column>
        <el-table-column prop="transaction_id" label="流水号" />
        <el-table-column prop="payment_time" label="时间"><template #default="scope">{{ scope.row.payment_time?.slice(0,16) }}</template></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const order = ref(null)
const details = ref([])
const timeline = ref([])
const payments = ref([])
const loading = ref(true)

const statusType = (s) => ({ 'PENDING':'warning','CONFIRMED':'primary','SHIPPED':'success','COMPLETED':'success','OUT_OF_STOCK':'danger','REFUNDING':'warning','CANCELLED':'info' }[s] || 'info')
const statusText = (s) => ({ 'PENDING':'待确认','CONFIRMED':'已确认','SHIPPED':'已发货','COMPLETED':'已完成','OUT_OF_STOCK':'缺货','REFUNDING':'退款中','CANCELLED':'已取消' }[s] || s)

onMounted(async () => {
  const oid = route.params.id
  try { const r = await axios.get(`/api/orders/${oid}`); order.value = r.data } catch {}
  try { const r = await axios.get(`/api/orders/${oid}/details`); details.value = r.data } catch {}
  try { const r = await axios.get(`/api/orders/${oid}/timeline`); timeline.value = r.data } catch {}
  try { const r = await axios.get(`/api/payments/order/${oid}`); payments.value = r.data } catch {}
  loading.value = false
})
</script>
