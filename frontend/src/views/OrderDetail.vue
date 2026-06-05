<template>
  <el-card>
    <template #header><span style="font-weight:bold;font-size:16px">订单 #{{ $route.params.id }} 明细</span></template>
    <el-table :data="details">
      <el-table-column prop="product_name" label="商品" />
      <el-table-column prop="unit_price" label="单价" />
      <el-table-column prop="quantity" label="数量" />
      <el-table-column prop="total_amount" label="小计" />
    </el-table>
    <el-button style="margin-top:16px" @click="$router.back()">返回</el-button>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const details = ref([])

onMounted(async () => {
  const res = await axios.get(`/api/orders/${route.params.id}/details`)
  details.value = res.data
})
</script>