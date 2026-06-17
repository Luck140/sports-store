<template>
  <div class="orders-page">
    <h2 class="page-title">我的订单</h2>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input v-model="keyword" placeholder="搜索订单号" clearable prefix-icon="Search" @keyup.enter="load" @clear="load" />
      <el-select v-model="statusFilter" placeholder="全部状态" clearable @change="load">
        <el-option label="全部状态" value="" />
        <el-option label="待确认" value="PENDING" />
        <el-option label="已确认" value="CONFIRMED" />
        <el-option label="已发货" value="SHIPPED" />
        <el-option label="已完成" value="COMPLETED" />
        <el-option label="缺货" value="OUT_OF_STOCK" />
        <el-option label="退款中" value="REFUNDING" />
        <el-option label="已取消" value="CANCELLED" />
      </el-select>
    </div>

    <!-- 加载中 -->
    <div v-loading="loading">
      <!-- 空状态 -->
      <div v-if="!loading && orders.length === 0" class="empty-state">
        <p class="empty-icon">📋</p>
        <p class="empty-text">暂无订单</p>
        <el-button type="primary" @click="$router.push('/products')">去选购</el-button>
      </div>

      <!-- 订单列表 -->
      <div v-else class="order-list">
        <div v-for="o in orders" :key="o.order_id" class="order-card" @click="$router.push(`/orders/${o.order_id}`)">

          <!-- 1. 顶部店铺栏 -->
          <div class="card-header">
            <div class="store-info">
              <span class="store-logo">🏪</span>
              <span class="store-name">SportsStore</span>
              <span class="store-tag">旗舰店</span>
            </div>
            <div class="order-status" :class="statusClass(o)">
              {{ statusMap[o.status] }}
              <span v-if="o.status === 'PENDING' && o.payment_status === 0" class="status-sub">待付款</span>
            </div>
          </div>

          <!-- 2. 商品主体区 -->
          <div class="product-section" v-for="(item, idx) in (o.items || [])" :key="idx">
            <div class="product-img">
              {{ getIcon(item) }}
            </div>
            <div class="product-info">
              <div class="product-title">{{ item.product_name }}</div>
              <div class="product-spec">
                <span>×{{ item.quantity }}</span>
                <span class="spec-sep">|</span>
                <span>¥{{ item.unit_price }}/件</span>
              </div>
              <div class="service-tags">
                <span class="service-tag">坏了包赔</span>
                <span class="service-tag">7天无理由退货</span>
              </div>
            </div>
            <div class="product-amount">
              <span class="amount-label">小计</span>
              <span class="amount-value">¥{{ item.total_amount }}</span>
            </div>
          </div>

          <!-- 3. 价格支付区 -->
          <div class="price-section">
            <div class="group-avatars">
              <span class="group-avatar">👤</span>
              <span class="group-avatar">👤</span>
              <span class="group-avatar">👤</span>
              <span class="group-count">{{ (o.order_id % 3) + 2 }}人拼单</span>
            </div>
            <div class="price-info">
              <div class="price-row" v-if="o.shipping_cost > 0">
                <span class="price-label">运费</span>
                <span class="price-val">¥{{ o.shipping_cost }}</span>
              </div>
              <div class="price-row main-price">
                <span class="price-label">实付</span>
                <span class="price-num">¥{{ o.total_amount }}</span>
              </div>
              <div class="price-row discount" v-if="o.payment_status === 0">
                <span class="price-label">优惠</span>
                <span class="price-discount">支持先用后付</span>
              </div>
            </div>
          </div>

          <!-- 4. 操作按钮区 -->
          <div class="action-section">
            <div class="action-left">
              <!-- 拼单头像数量显示 -->
            </div>
            <div class="action-buttons">
              <el-button size="small" plain @click.stop="$router.push(`/orders/${o.order_id}`)">查看详情</el-button>

              <!-- 待确认/未付款 -->
              <el-button v-if="o.status === 'PENDING' && o.payment_status === 0" size="small" type="danger" plain @click.stop="cancelOrder(o)">取消订单</el-button>
              <el-button v-if="o.status === 'PENDING' && o.payment_status === 0" size="small" type="primary" @click.stop="doPay(o)">去支付</el-button>

              <!-- 待确认/已付款 -->
              <el-button v-if="o.status === 'PENDING' && o.payment_status === 1" size="small" @click.stop="urgeOrder(o)">催发货</el-button>

              <!-- 已确认 -->
              <el-button v-if="o.status === 'CONFIRMED'" size="small" @click.stop="urgeOrder(o)">催发货</el-button>

              <!-- 已发货 -->
              <el-button v-if="o.status === 'SHIPPED'" size="small" @click.stop="requestRefund(o)">申请退款</el-button>
              <el-button v-if="o.status === 'SHIPPED'" size="small" @click.stop="confirmReceipt(o)" type="primary">确认收货</el-button>

              <!-- 已完成 -->
              <el-button v-if="o.status === 'COMPLETED'" size="small" @click.stop="writeReview(o)">评价</el-button>

              <!-- 退款中 -->
              <el-button v-if="o.status === 'REFUNDING'" size="small" disabled>退款处理中</el-button>
            </div>
          </div>

          <!-- 5. 底部物流时效栏 -->
          <div class="logistics-bar">
            <span class="logistics-icon">🚚</span>
            <span class="logistics-text">{{ logisticsText(o) }}</span>
            <span class="logistics-time">{{ logisticsTime(o) }}</span>
          </div>

        </div>

        <!-- 分页 -->
        <div style="text-align:center;margin-top:20px" v-if="totalPages > 1">
          <el-pagination background layout="prev,pager,next" :total="total" :page-size="pageSize" v-model:current-page="page" @current-change="load" />
        </div>
      </div>
    </div>

    <!-- 支付弹窗 -->
    <el-dialog v-model="payDialog" title="支付" width="380px" @click.stop>
      <p>订单：<b>#{{ payingOrder?.order_id }}</b></p>
      <p class="pay-amount">金额：¥{{ payingOrder?.total_amount }}</p>
      <el-radio-group v-model="payMethod" class="pay-methods">
        <el-radio value="credit_card" class="pay-method-item">💳 信用卡支付</el-radio>
        <el-radio value="alipay" class="pay-method-item">📱 支付宝</el-radio>
        <el-radio value="wechat" class="pay-method-item">💚 微信支付</el-radio>
      </el-radio-group>
      <template #footer>
        <el-button @click="payDialog = false">取消</el-button>
        <el-button type="primary" @click="doPayConfirm" :loading="paying">确认支付</el-button>
      </template>
    </el-dialog>

    <!-- 评价弹窗 -->
    <el-dialog v-model="reviewDialog" title="评价商品" width="400px" @click.stop>
      <div style="margin-bottom:12px">评分：<el-rate v-model="reviewForm.rating" /></div>
      <el-input v-model="reviewForm.content" type="textarea" rows="3" placeholder="写下您的评价..." />
      <template #footer>
        <el-button @click="reviewDialog = false">取消</el-button>
        <el-button type="primary" @click="submitReview" :loading="submitting">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProductIcon } from '@/utils/productIcons'

const route = useRoute(); const router = useRouter(); const userStore = useUserStore()
const orders = ref([]); const loading = ref(false); const keyword = ref('')
const statusFilter = ref(route.query.status || '')
const page = ref(1); const total = ref(0); const pageSize = 10; const totalPages = ref(1)
const payDialog = ref(false); const payingOrder = ref(null); const payMethod = ref('alipay'); const paying = ref(false)
const reviewDialog = ref(false); const reviewForm = ref({ order_id: null, product_id: null, rating: 5, content: '' }); const submitting = ref(false)
const icons = ['🏀', '⚽', '🏸', '👕', '⚾', '🏐', '🏓', '🎽', '🩳', '🧢']
const getIcon = (item) => getProductIcon(item)

const statusMap = { PENDING: '待确认', CONFIRMED: '已确认', SHIPPED: '已发货', COMPLETED: '已完成', OUT_OF_STOCK: '缺货', REFUNDING: '退款中', CANCELLED: '已取消' }

const statusClass = (o) => {
  if (o.status === 'PENDING' || o.status === 'REFUNDING') return 'status-orange'
  if (o.status === 'CONFIRMED') return 'status-blue'
  if (o.status === 'SHIPPED') return 'status-green'
  if (o.status === 'OUT_OF_STOCK') return 'status-red'
  if (o.status === 'CANCELLED') return 'status-gray'
  return ''
}

const logisticsText = (o) => {
  if (o.status === 'PENDING' || o.status === 'CONFIRMED') return '等待卖家确认订单'
  if (o.status === 'SHIPPED') return '包裹正在运送中'
  if (o.status === 'COMPLETED') return '已签收'
  if (o.status === 'CANCELLED') return '订单已取消'
  if (o.status === 'OUT_OF_STOCK') return '商品缺货，请联系客服'
  if (o.status === 'REFUNDING') return '退款处理中'
  return '订单处理中'
}

const logisticsTime = (o) => {
  if (o.status === 'PENDING') return '预计 24h 内确认'
  if (o.status === 'CONFIRMED') return '预计 2-3 天发货'
  if (o.status === 'SHIPPED') return '预计 3-5 天送达'
  if (o.status === 'COMPLETED') return '感谢您的购买'
  return ''
}

const formatTime = (t) => t ? new Date(t).toLocaleString('zh-CN') : ''

const load = async () => {
  loading.value = true
  try {
    const p = { customer_id: userStore.user.customer_id, page: page.value, page_size: pageSize }
    if (statusFilter.value) p.status = statusFilter.value
    if (keyword.value) p.keyword = keyword.value
    const r = await axios.get(`/api/orders/customer/${userStore.user.customer_id}`, { params: p })
    orders.value = r.data.items || []
    total.value = r.data.total || 0
    totalPages.value = r.data.total_pages || 1
  } catch { orders.value = [] }
  finally { loading.value = false }
}

const doPay = (o) => { payingOrder.value = o; payMethod.value = 'alipay'; payDialog.value = true }
const doPayConfirm = async () => {
  paying.value = true
  try {
    await axios.post('/api/payments/', { order_id: payingOrder.value.order_id, payment_method: payMethod.value, amount: payingOrder.value.total_amount })
    ElMessage.success('支付成功')
    payDialog.value = false
    load()
  } catch { ElMessage.error('支付失败') }
  finally { paying.value = false }
}

const cancelOrder = async (o) => {
  try {
    await ElMessageBox.confirm('确定要取消此订单吗？')
    await axios.post(`/api/orders/${o.order_id}/customer-cancel`)
    ElMessage.success('已取消')
    load()
  } catch {}
}

const confirmReceipt = async (o) => {
  try {
    await ElMessageBox.confirm('确认已收到货物吗？')
    await axios.post(`/api/orders/${o.order_id}/confirm-receipt`)
    ElMessage.success('收货成功')
    load()
  } catch {}
}

const requestRefund = async (o) => {
  try {
    await ElMessageBox.confirm('确定要申请退款吗？')
    await axios.post('/api/payments/refund/request', { order_id: o.order_id })
    ElMessage.success('退款申请已提交')
    load()
  } catch {}
}

const urgeOrder = async (o) => {
  try { await axios.post(`/api/orders/${o.order_id}/urge`); ElMessage.success('已催单') } catch {}
}

const writeReview = async (o) => {
  reviewForm.value = { order_id: o.order_id, product_id: null, rating: 5, content: '' }
  try {
    const r = await axios.get(`/api/orders/${o.order_id}/details`)
    if (r.data.length) reviewForm.value.product_id = r.data[0].product_id
    reviewDialog.value = true
  } catch {}
}

const submitReview = async () => {
  submitting.value = true
  try {
    await axios.post('/api/reviews/', { ...reviewForm.value, customer_id: userStore.user.customer_id })
    ElMessage.success('评价成功')
    reviewDialog.value = false
    load()
  } catch { ElMessage.error('提交失败') }
  finally { submitting.value = false }
}

onMounted(load)
watch(() => route.query.status, (newStatus) => {
  statusFilter.value = newStatus || ''
  page.value = 1
  load()
})
</script>

<style scoped>
.orders-page { max-width: 820px; margin: 0 auto; }
.page-title { margin: 0 0 16px; font-size: 20px; font-weight: 600; }

/* 筛选栏 */
.filter-bar { display: flex; gap: 12px; margin-bottom: 16px; background: var(--ss-surface); padding: 14px 18px; border-radius: var(--ss-radius-sm); border: 1px solid var(--ss-border-light); }
.filter-bar .el-input { flex: 1; }
.filter-bar .el-select { width: 160px; }

/* 空状态 */
.empty-state { padding: 80px 0; text-align: center; color: var(--ss-text-muted); }
.empty-icon { font-size: 56px; margin: 0 0 12px; }
.empty-text { margin-bottom: 16px; }

/* 订单卡片 */
.order-list { display: flex; flex-direction: column; gap: 14px; }
.order-card { background: var(--ss-surface); border-radius: var(--ss-radius-sm); border: 1px solid var(--ss-border-light); overflow: hidden; cursor: pointer; transition: box-shadow var(--ss-transition-base); }
.order-card:hover { box-shadow: var(--ss-shadow-md); }

/* 1. 顶部店铺栏 */
.card-header { display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; border-bottom: 1px solid var(--ss-border-lighter); }
.store-info { display: flex; align-items: center; gap: 8px; }
.store-logo { font-size: 20px; }
.store-name { font-size: 14px; font-weight: 600; color: var(--ss-text); }
.store-tag { font-size: 10px; background: var(--ss-primary); color: #fff; padding: 1px 6px; border-radius: 3px; font-weight: 500; }
.order-status { font-size: 13px; font-weight: 600; }
.status-orange { color: var(--ss-warning); }
.status-blue { color: var(--ss-primary); }
.status-green { color: var(--ss-success); }
.status-red { color: var(--ss-danger); }
.status-gray { color: var(--ss-text-muted); }
.status-sub { font-size: 11px; font-weight: 400; margin-left: 4px; opacity: 0.7; }

/* 2. 商品主体区 */
.product-section { display: flex; align-items: center; padding: 14px 18px; border-bottom: 1px solid var(--ss-border-lighter); gap: 12px; }
.product-img { width: 64px; height: 64px; border-radius: var(--ss-radius-sm); background: var(--ss-bg-warm); display: flex; align-items: center; justify-content: center; font-size: 32px; flex-shrink: 0; }
.product-info { flex: 1; min-width: 0; }
.product-title { font-size: 14px; font-weight: 500; color: var(--ss-text); margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.product-spec { font-size: 12px; color: var(--ss-text-muted); margin-bottom: 6px; display: flex; align-items: center; gap: 4px; }
.spec-sep { color: var(--ss-text-dim); }
.service-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.service-tag { font-size: 10px; background: var(--ss-green); color: #fff; padding: 1px 8px; border-radius: 10px; font-weight: 500; }
.product-amount { text-align: right; flex-shrink: 0; }
.amount-label { display: block; font-size: 11px; color: var(--ss-text-muted); }
.amount-value { font-size: 14px; font-weight: 600; color: var(--ss-text); }

/* 3. 价格支付区 */
.price-section { display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; border-bottom: 1px solid var(--ss-border-lighter); }
.group-avatars { display: flex; align-items: center; gap: 2px; }
.group-avatar { width: 24px; height: 24px; border-radius: 50%; background: var(--ss-bg-warm); border: 1px solid var(--ss-border-light); display: flex; align-items: center; justify-content: center; font-size: 12px; margin-left: -6px; }
.group-avatar:first-child { margin-left: 0; }
.group-count { font-size: 11px; color: var(--ss-text-muted); margin-left: 6px; }
.price-info { text-align: right; }
.price-row { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--ss-text-muted); margin-bottom: 2px; justify-content: flex-end; }
.price-row.main-price { margin-bottom: 0; }
.price-label { font-size: 12px; }
.price-val { font-size: 12px; }
.price-num { font-size: 18px; font-weight: 700; color: var(--ss-danger); }
.price-discount { font-size: 11px; color: var(--ss-success); background: var(--ss-success-bg); padding: 1px 6px; border-radius: 3px; }

/* 4. 操作按钮区 */
.action-section { display: flex; justify-content: flex-end; align-items: center; padding: 12px 18px; border-bottom: 1px solid var(--ss-border-lighter); }
.action-buttons { display: flex; gap: 8px; flex-wrap: wrap; }

/* 5. 底部物流时效栏 */
.logistics-bar { display: flex; align-items: center; gap: 6px; padding: 10px 18px; background: var(--ss-bg-warm); font-size: 12px; }
.logistics-icon { font-size: 14px; }
.logistics-text { color: var(--ss-success); font-weight: 500; flex: 1; }
.logistics-time { color: var(--ss-text-muted); font-size: 11px; }

/* 弹窗 */
.pay-amount { font-size: 20px; font-weight: 700; color: var(--ss-accent); }
.pay-methods { display: flex; flex-direction: column; gap: 10px; margin: 12px 0; }
.pay-method-item { margin: 0 !important; }
</style>
