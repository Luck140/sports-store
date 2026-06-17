<template>
  <div>
    <h2 class="page-title">报表中心</h2>
    <el-card class="filter-card" shadow="never">
      <el-radio-group v-model="reportType" @change="switchReport">
        <el-radio value="success">成功订单报表</el-radio>
        <el-radio value="unpaid">未付款报表</el-radio>
        <el-radio value="unshipped">未发货报表</el-radio>
        <el-radio value="lowstock">库存预警报表</el-radio>
        <el-radio value="stockrecords">库存变动记录</el-radio>
      </el-radio-group>
    </el-card>
    <el-card shadow="never" v-loading="loading">
      <el-table v-if="reportType === 'success' && data.length" :data="data" style="width:100%">
        <el-table-column label="订单号" width="100"><template #default="{row}">#{{ row.order_id }}</template></el-table-column>
        <el-table-column prop="customer_name" label="客户" width="100" />
        <el-table-column label="金额" width="100"><template #default="{row}">¥{{ row.total_amount }}</template></el-table-column>
        <el-table-column label="重量" width="80"><template #default="{row}">{{ row.total_weight }}kg</template></el-table-column>
        <el-table-column label="运费" width="80"><template #default="{row}">¥{{ row.shipping_cost }}</template></el-table-column>
        <el-table-column prop="recipient_name" label="收件人" width="90" />
        <el-table-column prop="recipient_address" label="地址" min-width="200" />
      </el-table>
      <el-table v-if="reportType === 'unpaid' && data.length" :data="data" style="width:100%">
        <el-table-column label="订单号" width="100"><template #default="{row}">#{{ row.order_id }}</template></el-table-column>
        <el-table-column prop="customer_name" label="客户" width="100" />
        <el-table-column label="金额" width="100"><template #default="{row}">¥{{ row.total_amount }}</template></el-table-column>
        <el-table-column prop="status" label="状态" width="100"><template #default="{row}"><el-tag :type="tagType(row.status)" size="small">{{ statusMap[row.status] }}</el-tag></template></el-table-column>
        <el-table-column label="下单时间" min-width="160"><template #default="{row}">{{ formatTime(row.order_date) }}</template></el-table-column>
      </el-table>
      <el-table v-if="reportType === 'unshipped' && data.length" :data="data" style="width:100%">
        <el-table-column label="订单号" width="100"><template #default="{row}">#{{ row.order_id }}</template></el-table-column>
        <el-table-column prop="customer_name" label="客户" width="100" />
        <el-table-column label="金额" width="100"><template #default="{row}">¥{{ row.total_amount }}</template></el-table-column>
        <el-table-column prop="status" label="状态" width="100"><template #default="{row}"><el-tag :type="tagType(row.status)" size="small">{{ statusMap[row.status] }}</el-tag></template></el-table-column>
        <el-table-column label="重量" width="80"><template #default="{row}">{{ row.total_weight }}kg</template></el-table-column>
      </el-table>
      <el-table v-if="reportType === 'lowstock' && data.length" :data="data" style="width:100%">
        <el-table-column label="编号" width="80"><template #default="{row}">{{ row.product_id }}</template></el-table-column>
        <el-table-column prop="product_name" label="商品名" min-width="140" />
        <el-table-column prop="manufacturer_name" label="厂家" width="140" />
        <el-table-column label="库存" width="80"><template #default="{row}"><span style="color:var(--ss-danger);font-weight:700">{{ row.stock_quantity }}</span></template></el-table-column>
        <el-table-column label="预警值" width="80"><template #default="{row}">{{ row.min_stock_threshold }}</template></el-table-column>
      </el-table>
      <el-table v-if="reportType === 'stockrecords' && data.length" :data="data" style="width:100%">
        <el-table-column label="记录ID" width="80"><template #default="{row}">{{ row.record_id }}</template></el-table-column>
        <el-table-column label="商品" width="80"><template #default="{row}">{{ row.product_id }}</template></el-table-column>
        <el-table-column label="变动量" width="80"><template #default="{row}"><span :style="{ color: row.quantity_change > 0 ? 'var(--ss-success)' : 'var(--ss-danger)' }">{{ row.quantity_change > 0 ? '+' : '' }}{{ row.quantity_change }}</span></template></el-table-column>
        <el-table-column prop="reason" label="原因" width="120" />
        <el-table-column label="时间" min-width="160"><template #default="{row}">{{ formatTime(row.operated_at) }}</template></el-table-column>
      </el-table>
      <el-empty v-if="data.length === 0" description="暂无数据" />
    </el-card>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const reportType = ref('success'); const data = ref([]); const loading = ref(false)
const statusMap = { PENDING: '待确认', CONFIRMED: '已确认', SHIPPED: '已发货', COMPLETED: '已完成', OUT_OF_STOCK: '缺货', REFUNDING: '退款中', CANCELLED: '已取消' }
const tagType = (s) => ({ PENDING: 'warning', CONFIRMED: 'primary', SHIPPED: 'success', COMPLETED: '', OUT_OF_STOCK: 'danger', REFUNDING: 'warning', CANCELLED: 'info' }[s] || '')
const formatTime = (t) => t ? new Date(t).toLocaleString('zh-CN') : ''
const endpoints = { success: '/api/admin/reports/success-orders', unpaid: '/api/admin/reports/unpaid-orders', unshipped: '/api/admin/reports/unshipped-orders', lowstock: '/api/admin/reports/low-stock', stockrecords: '/api/admin/reports/stock-records' }
const switchReport = async () => {
  loading.value = true
  try { const r = await axios.get(endpoints[reportType.value]); data.value = Array.isArray(r.data) ? r.data : r.data.items || [] } catch { data.value = [] }
  finally { loading.value = false }
}
onMounted(switchReport)
</script>
<style scoped>
.page-title { margin: 0 0 16px; font-size: 20px; }
.filter-card { margin-bottom: 16px; }
</style>
