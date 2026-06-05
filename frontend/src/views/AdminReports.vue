<template>
  <el-card>
    <template #header><span style="font-weight:bold;font-size:16px">报表中心</span></template>
    <el-radio-group v-model="reportType" style="margin-bottom:16px">
      <el-radio-button value="success">成功订单</el-radio-button>
      <el-radio-button value="unpaid">未付款</el-radio-button>
      <el-radio-button value="unshipped">未发货</el-radio-button>
      <el-radio-button value="lowstock">库存预警</el-radio-button>
      <el-radio-button value="stockrecords">库存变动记录</el-radio-button>
    </el-radio-group>
    <el-table :data="data" empty-text="暂无数据">
      <!-- 成功订单 -->
      <template v-if="reportType==='success'">
        <el-table-column prop="order_id" label="订单号" />
        <el-table-column prop="customer_name" label="客户" />
        <el-table-column prop="total_amount" label="金额" />
        <el-table-column prop="total_weight" label="重量(kg)" />
        <el-table-column prop="shipping_cost" label="运费" />
        <el-table-column prop="recipient_name" label="收件人" />
        <el-table-column prop="recipient_address" label="地址" />
      </template>
      <!-- 未付款 -->
      <template v-if="reportType==='unpaid'">
        <el-table-column prop="order_id" label="订单号" />
        <el-table-column prop="customer_name" label="客户" />
        <el-table-column prop="total_amount" label="金额" />
        <el-table-column prop="status" label="状态" />
        <el-table-column prop="order_date" label="下单时间" />
      </template>
      <!-- 未发货 -->
      <template v-if="reportType==='unshipped'">
        <el-table-column prop="order_id" label="订单号" />
        <el-table-column prop="customer_name" label="客户" />
        <el-table-column prop="total_amount" label="金额" />
        <el-table-column prop="status" label="状态" />
        <el-table-column prop="total_weight" label="重量(kg)" />
      </template>
      <!-- 库存预警 -->
      <template v-if="reportType==='lowstock'">
        <el-table-column prop="product_id" label="商品ID" />
        <el-table-column prop="product_name" label="商品名" />
        <el-table-column prop="manufacturer_name" label="厂家" />
        <el-table-column prop="stock_quantity" label="库存" />
        <el-table-column prop="min_stock_threshold" label="预警值" />
      </template>
      <!-- 库存变动记录 -->
      <template v-if="reportType==='stockrecords'">
        <el-table-column prop="product_id" label="商品ID" />
        <el-table-column prop="quantity_change" label="变动量" />
        <el-table-column prop="reason" label="原因" />
        <el-table-column prop="operated_at" label="时间" />
      </template>
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'

const reportType = ref('success')
const data = ref([])

const load = async () => {
  const urls = {
    success: '/api/admin/reports/success-orders',
    unpaid: '/api/admin/reports/unpaid-orders',
    unshipped: '/api/admin/reports/unshipped-orders',
    lowstock: '/api/admin/reports/low-stock',
    stockrecords: '/api/admin/reports/stock-records',
  }
  const res = await axios.get(urls[reportType.value])
  data.value = res.data
}

watch(reportType, load, { immediate: true })
</script>