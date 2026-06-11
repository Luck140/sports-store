<template>
  <div>
    <el-row :gutter="12" style="margin-bottom:16px">
      <el-col :span="6" v-for="(card, i) in cards" :key="i">
        <el-card :class="['stat-card', card.urgent ? 'urgent' : '']">
          <div class="stat-num" :style="{color:card.color}">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
          <div v-if="card.urgent && card.value > 0" class="stat-tip">{{ card.tip }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-alert v-if="todos.length" title="待办提醒" type="warning" show-icon :closable="false" style="margin-bottom:16px">
      <div v-for="t in todos" :key="t.label" style="margin-top:4px">
        <router-link :to="t.link" style="font-size:14px">{{ t.label }}：{{ t.count }} 条待处理</router-link>
      </div>
    </el-alert>

    <el-row :gutter="16">
      <el-col :xs="24" :md="12" style="margin-bottom:16px">
        <el-card><template #header><span style="font-weight:bold;font-size:15px">热销商品 TOP5</span></template>
          <div v-for="(p,i) in hotProducts" :key="p.product_id" style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--color-border-light)">
            <span>{{ i+1 }}. {{ p.product_name }}</span><span style="color:var(--color-text-muted)">已售 {{ p.sales_count }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12" style="margin-bottom:16px">
        <el-card><template #header><span style="font-weight:bold;font-size:15px">近30天销售额</span></template>
          <div v-if="salesData.length">
            <div v-for="d in salesData.slice(0,10)" :key="d.date" style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--color-border-light);font-size:13px">
              <span>{{ d.date }}</span><span>{{ d.count }}单</span><span style="color:var(--color-accent)">¥{{ d.amount }}</span>
            </div>
          </div>
          <el-empty v-else description="暂无数据" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const cards = ref([{ label:'总订单数', value:0, color:'var(--color-primary)', urgent:false, tip:'' }, { label:'待确认', value:0, color:'var(--color-warning)', urgent:true, tip:'请尽快处理' }, { label:'未发货', value:0, color:'var(--color-info)', urgent:false, tip:'' }, { label:'库存预警', value:0, color:'var(--color-danger)', urgent:true, tip:'需要进货' }])
const todos = ref([])
const hotProducts = ref([])
const salesData = ref([])

onMounted(async () => {
  try {
    const r = await axios.get('/api/admin/dashboard')
    cards.value[0].value = r.data.total_orders
    cards.value[1].value = r.data.pending_orders
    cards.value[2].value = r.data.unshipped_orders
    cards.value[3].value = r.data.low_stock_count
    todos.value = (r.data.pending_todos || []).filter(t => t.count > 0)
  } catch {}
  try { const r = await axios.get('/api/admin/dashboard/hot-products'); hotProducts.value = r.data } catch {}
  try { const r = await axios.get('/api/admin/dashboard/sales-chart'); salesData.value = r.data } catch {}
})
</script>

<style scoped>
.stat-card { text-align:center; }
.stat-num { font-size:36px; font-weight:bold; }
.stat-label { font-size:14px; color:var(--color-text-muted); margin-top:8px; }
.stat-tip { font-size:12px; color:var(--color-danger); margin-top:4px; font-weight:500; }
.stat-card.urgent { border:1px solid var(--color-danger); background:rgba(138,58,58,0.03); }
</style>
