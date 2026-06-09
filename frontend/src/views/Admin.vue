<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in cards" :key="card.label">
        <el-card class="stat-card">
          <div class="stat-num">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const cards = ref([
  { label: '总订单数', value: 0 },
  { label: '待确认', value: 0 },
  { label: '未发货', value: 0 },
  { label: '库存预警', value: 0 },
])

onMounted(async () => {
  const res = await axios.get('/api/admin/dashboard')
  cards.value[0].value = res.data.total_orders
  cards.value[1].value = res.data.pending_orders
  cards.value[2].value = res.data.unshipped_orders
  cards.value[3].value = res.data.low_stock_count
})
</script>

<style scoped>
.stat-card { text-align:center; }
.stat-num { font-size:36px; font-weight:bold; color:var(--color-primary); }
.stat-label { font-size:14px; color:var(--color-text-muted); margin-top:8px; }
</style>