<template>
  <div>
    <el-card style="margin-bottom:12px">
      <el-row :gutter="12" align="middle">
        <el-col :xs="24" :sm="7"><el-input v-model="searchKeyword" placeholder="输入订单号" clearable @change="fetchOrders" size="default" /></el-col>
        <el-col :xs="12" :sm="4"><el-select v-model="statusFilter" placeholder="全部状态" clearable @change="fetchOrders" style="width:100%">
          <el-option label="待确认" value="PENDING" /><el-option label="已确认" value="CONFIRMED" /><el-option label="已发货" value="SHIPPED" /><el-option label="已完成" value="COMPLETED" /><el-option label="已取消" value="CANCELLED" /><el-option label="退款中" value="REFUNDING" />
        </el-select></el-col>
      </el-row>
    </el-card>

    <div v-if="!loading && orders.length === 0" style="padding:80px 0;text-align:center">
      <el-empty :description="statusFilter ? '该状态下暂无订单' : '还没有订单'">
        <el-button type="primary" @click="$router.push('/products')">去选购商品</el-button>
      </el-empty>
    </div>

    <el-card v-else v-loading="loading">
      <el-table :data="orders" style="width:100%">
        <el-table-column label="订单号" width="90"><template #default="s"><router-link :to="`/orders/${s.row.order_id}`">#{{ s.row.order_id }}</router-link></template></el-table-column>
        <el-table-column label="金额" width="110"><template #default="s"><span style="color:var(--color-accent);font-weight:700">¥{{ s.row.total_amount }}</span></template></el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="s">
            <el-tag v-if="s.row.status==='PENDING'" type="warning" size="small">待确认</el-tag>
            <el-tag v-else-if="s.row.status==='CONFIRMED'" type="primary" size="small">已确认</el-tag>
            <el-tag v-else-if="s.row.status==='SHIPPED'" type="success" size="small">已发货</el-tag>
            <el-tag v-else-if="s.row.status==='COMPLETED'" size="small">已完成</el-tag>
            <el-tag v-else-if="s.row.status==='OUT_OF_STOCK'" type="danger" size="small">缺货</el-tag>
            <el-tag v-else-if="s.row.status==='REFUNDING'" type="warning" size="small">退款中</el-tag>
            <el-tag v-else-if="s.row.status==='CANCELLED'" type="info" size="small">已取消</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="付款" width="70"><template #default="s">{{ s.row.payment_status===1?'已付':s.row.payment_status===2?'已退':'未付' }}</template></el-table-column>
        <el-table-column label="时间" width="110"><template #default="s">{{ s.row.order_date?.slice(0,10) }}</template></el-table-column>
        <el-table-column label="操作" min-width="200">
          <template #default="s">
            <el-button v-if="s.row.payment_status===0" type="success" size="small" @click="showPay(s.row)">支付</el-button>
            <el-button v-if="s.row.status==='PENDING'" type="danger" size="small" plain @click="cancelOrder(s.row.order_id)">取消</el-button>
            <el-button v-if="s.row.status==='SHIPPED'" type="primary" size="small" @click="confirmReceipt(s.row.order_id)">确认收货</el-button>
            <el-button v-if="s.row.status==='COMPLETED'" type="warning" size="small" @click="showReview(s.row)">评价</el-button>
            <el-button v-if="(s.row.status==='PENDING'||s.row.status==='CONFIRMED') && s.row.payment_status===1" size="small" @click="urgeOrder(s.row.order_id)">催单</el-button>
            <el-button v-if="s.row.status==='SHIPPED' && s.row.payment_status===1" type="warning" size="small" plain @click="requestRefund(s.row.order_id)">申请退款</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="text-align:center;margin-top:20px" v-if="totalPages > 1">
        <el-pagination background layout="prev, pager, next" :total="total" :page-size="pageSize" v-model:current-page="currentPage" @current-change="(p) => fetchOrders(p)" />
      </div>
    </el-card>

    <el-dialog v-model="payVisible" title="确认支付" width="420px">
      <template v-if="payOrder">
        <el-descriptions :column="1" border size="small"><el-descriptions-item label="订单号">#{{ payOrder.order_id }}</el-descriptions-item><el-descriptions-item label="商品金额">¥{{ payOrder.total_amount }}</el-descriptions-item><el-descriptions-item label="运费">¥{{ payOrder.shipping_cost || 0 }}</el-descriptions-item><el-descriptions-item label="实付"><strong style="color:var(--color-accent)">¥{{ (parseFloat(payOrder.total_amount||0)+parseFloat(payOrder.shipping_cost||0)).toFixed(2) }}</strong></el-descriptions-item></el-descriptions>
        <el-radio-group v-model="payMethod" style="margin-top:12px;display:flex;flex-direction:column;gap:8px"><el-radio label="ALIPAY">支付宝</el-radio><el-radio label="WECHAT">微信支付</el-radio><el-radio label="CREDIT_CARD">信用卡</el-radio></el-radio-group>
      </template>
      <template #footer><el-button @click="payVisible=false">取消</el-button><el-button type="primary" @click="doPay" :loading="paying">确认支付</el-button></template>
    </el-dialog>

    <el-dialog v-model="reviewVisible" title="商品评价" width="420px">
      <div v-for="item in reviewItems" :key="item.product_id" style="margin-bottom:16px">
        <p style="margin:0 0 6px 0;font-weight:600">{{ item.product_name }}</p>
        <el-rate v-model="item.rating" /><el-input v-model="item.content" placeholder="分享您的使用体验（选填）" type="textarea" rows="2" style="margin-top:6px" />
      </div>
      <template #footer><el-button @click="reviewVisible=false">取消</el-button><el-button type="primary" @click="submitReviews" :loading="reviewing">提交评价</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()
const orders = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const totalPages = ref(1)
const searchKeyword = ref('')
const statusFilter = ref('')
const payVisible = ref(false)
const payOrder = ref(null)
const payMethod = ref('ALIPAY')
const paying = ref(false)
const reviewVisible = ref(false)
const reviewItems = ref([])
const reviewing = ref(false)

const fetchOrders = async (page) => {
  loading.value = true
  try {
    const p = { page: page || currentPage.value, page_size: pageSize.value }
    if (statusFilter.value) p.status = statusFilter.value
    if (searchKeyword.value) p.keyword = searchKeyword.value
    const r = await axios.get(`/api/orders/customer/${userStore.user.customer_id}`, { params: p })
    orders.value = r.data.items; total.value = r.data.total; totalPages.value = r.data.total_pages
  } catch {} finally { loading.value = false }
}

const showPay = (o) => { payOrder.value = o; payVisible.value = true }
const doPay = async () => {
  paying.value = true
  try { await axios.post('/api/payments/', { order_id: payOrder.value.order_id, payment_method: payMethod.value, amount: parseFloat(payOrder.value.total_amount) + parseFloat(payOrder.value.shipping_cost || 0) }); ElMessage.success('支付成功'); payVisible.value = false; fetchOrders(currentPage.value) }
  catch { ElMessage.error('支付失败') } finally { paying.value = false }
}

const cancelOrder = (id) => { ElMessageBox.confirm('确认取消该订单？','提示',{confirmButtonText:'确认取消',cancelButtonText:'再想想',type:'warning'}).then(async () => { try { await axios.post(`/api/orders/${id}/customer-cancel`); ElMessage.success('已取消'); fetchOrders(currentPage.value) } catch(e) { ElMessage.error(e.response?.data?.detail||'取消失败') } }).catch(() => {}) }
const confirmReceipt = (id) => { ElMessageBox.confirm('确认已收到货物？','确认收货',{confirmButtonText:'确认收货',type:'success'}).then(async () => { try { await axios.post(`/api/orders/${id}/confirm-receipt`); ElMessage.success('已确认收货'); fetchOrders(currentPage.value) } catch(e) { ElMessage.error(e.response?.data?.detail||'操作失败') } }).catch(() => {}) }
const urgeOrder = async (id) => { try { await axios.post(`/api/orders/${id}/urge`); ElMessage.success('已发送催单提醒') } catch {} }
const requestRefund = (id) => { ElMessageBox.confirm('确认申请退款？退款需管理员审核。','申请退款',{confirmButtonText:'确认申请',type:'warning'}).then(async () => { try { await axios.post('/api/payments/refund-request', { order_id: id, reason: '顾客申请退款' }); ElMessage.success('退款申请已提交，请等待审核'); fetchOrders(currentPage.value) } catch(e) { ElMessage.error(e.response?.data?.detail||'申请失败') } }).catch(() => {}) }

const showReview = async (order) => { payOrder.value = order; const r = await axios.get(`/api/orders/${order.order_id}/details`); reviewItems.value = r.data.map(d => ({ product_id: d.product_id, product_name: d.product_name, rating: 5, content: '' })); reviewVisible.value = true }
const submitReviews = async () => { reviewing.value = true; try { for (const item of reviewItems.value) { await axios.post('/api/reviews/', { order_id: payOrder.value.order_id, product_id: item.product_id, rating: item.rating, content: item.content || '好评' }) }; ElMessage.success('评价成功'); reviewVisible.value = false } catch { ElMessage.error('评价失败') } finally { reviewing.value = false } }

onMounted(() => fetchOrders())
</script>
