<template>
  <div v-loading="loading">
    <h2 class="page-title">我的购物车</h2>
    <div v-if="!cart.items || cart.items.length === 0" class="empty-state">
      <p class="empty-icon">🛒</p>
      <p class="empty-text">购物车是空的</p>
      <el-button type="primary" @click="$router.push('/products')">去选购</el-button>
    </div>
    <template v-else>
      <el-card>
        <el-table :data="cart.items" style="width:100%">
          <el-table-column label="商品" min-width="200">
            <template #default="{row}">
              <router-link :to="`/products/${row.product_id}`" style="color:var(--ss-primary);font-weight:500">{{ row.product_name }}</router-link>
            </template>
          </el-table-column>
          <el-table-column label="单价" width="100"><template #default="{row}">¥{{ row.unit_price }}</template></el-table-column>
          <el-table-column label="数量" width="160">
            <template #default="{row}">
              <el-input-number v-model="row.quantity" :min="1" :max="row.stock_quantity" size="small" controls-position="right" @change="(v) => updateQty(row.product_id, v)" />
            </template>
          </el-table-column>
          <el-table-column label="小计" width="120"><template #default="{row}">¥{{ (row.unit_price * row.quantity).toFixed(2) }}</template></el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{row}"><el-button text type="danger" size="small" @click="confirmRemove(row)">删除</el-button></template>
          </el-table-column>
        </el-table>
        <div class="cart-summary">共 <b>{{ cart.item_count }}</b> 件，商品金额：<b class="text-accent">¥{{ cart.total_price }}</b></div>
      </el-card>
      <el-card class="checkout-card">
        <template #header><span class="checkout-hd">结算信息</span></template>
        <el-form label-width="120px">
          <el-form-item label="收货地址">
            <el-select v-model="selectedAddress" placeholder="选择已保存地址" style="width:100%" @change="fillAddress" clearable>
              <el-option v-for="a in addresses" :key="a.address_id" :label="`${a.recipient_name} · ${a.address}${a.tag ? ' [' + a.tag + ']' : ''}`" :value="a.address_id" />
            </el-select>
          </el-form-item>
          <el-form-item label="收件人"><el-input v-model="checkout.recipient_name" placeholder="收件人" /></el-form-item>
          <el-form-item label="联系电话"><el-input v-model="checkout.recipient_phone" placeholder="联系电话" /></el-form-item>
          <el-form-item label="详细地址"><el-input v-model="checkout.recipient_address" placeholder="详细地址" /></el-form-item>
          <el-form-item label="货物重量(kg)">
            <el-input v-model.number="checkout.total_weight" type="number" :min="0" :step="0.5" placeholder="请输入货物重量" />
            <div style="font-size:12px;color:var(--ss-text-muted);margin-top:4px">首重1kg内包邮，超出每kg加收¥8</div>
          </el-form-item>
          <el-form-item label="运输要求"><el-input v-model="checkout.shipping_req" placeholder="如有特殊要求请注明" /></el-form-item>

          <!-- 发票区域（符合国家标准） -->
          <el-divider content-position="left">发票信息</el-divider>
          <el-form-item label="发票类型">
            <el-radio-group v-model="checkout.invoice_required">
              <el-radio :value="0">不需要发票</el-radio>
              <el-radio :value="1">增值税普通发票</el-radio>
              <el-radio :value="2">增值税专用发票</el-radio>
            </el-radio-group>
          </el-form-item>
          <template v-if="checkout.invoice_required">
            <el-form-item label="单位名称" required>
              <el-input v-model="checkout.invoice_title" placeholder="购买方单位全称（必填）" />
            </el-form-item>
            <el-form-item label="纳税人识别号" :required="checkout.invoice_required === 2">
              <el-input v-model="checkout.invoice_tax_no" :placeholder="checkout.invoice_required === 2 ? '购买方纳税人识别号（必填）' : '企业购买请填写纳税人识别号'" />
              <div style="font-size:12px;color:var(--ss-text-muted);margin-top:4px">根据国家税务总局公告2017年第16号，企业购买方应提供纳税人识别号</div>
            </el-form-item>
            <template v-if="checkout.invoice_required === 2">
              <el-form-item label="地址、电话" required>
                <el-input v-model="checkout.invoice_address_phone" placeholder="购买方地址及电话（专票必填）" />
              </el-form-item>
              <el-form-item label="开户行及账号" required>
                <el-input v-model="checkout.invoice_bank" placeholder="购买方开户行名称及账号（专票必填）" />
              </el-form-item>
            </template>
          </template>
        </el-form>
        <div class="checkout-total">
          <div>商品金额：¥{{ cart.total_price }}</div>
          <div>运费：¥{{ shippingCost }}</div>
          <div class="pay-amount">实付金额：¥{{ (parseFloat(cart.total_price) + shippingCost).toFixed(2) }}</div>
          <el-button type="primary" size="large" @click="submitOrder" :loading="ordering" style="margin-top:12px">确认下单</el-button>
        </div>
      </el-card>
    </template>
    <el-dialog v-model="removeDialog" title="确认删除" width="320px">
      <p>确定要从购物车中移除「{{ removing?.product_name }}」吗？</p>
      <template #footer><el-button @click="removeDialog = false">取消</el-button><el-button type="danger" @click="doRemove">确认删除</el-button></template>
    </el-dialog>
    <el-dialog v-model="payDialog" title="支付确认" width="400px">
      <p>订单已创建，订单号：<b>#{{ newOrderId }}</b></p>
      <p class="pay-amount">金额：¥{{ payAmount }}</p>
      <el-radio-group v-model="payMethod" class="pay-methods">
        <el-radio value="credit_card" class="pay-method-item">💳 信用卡支付</el-radio>
        <el-radio value="alipay" class="pay-method-item">📱 支付宝</el-radio>
        <el-radio value="wechat" class="pay-method-item">💚 微信支付</el-radio>
      </el-radio-group>
      <template #footer><el-button @click="payDialog = false">稍后支付</el-button><el-button type="primary" @click="doPay" :loading="paying">确认支付</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
import { ElMessage } from 'element-plus'
const router = useRouter(); const userStore = useUserStore()
const customerId = computed(() => userStore.user?.customer_id)
const cart = ref({ items: [], total_price: 0, item_count: 0 })
const addresses = ref([]); const selectedAddress = ref(null); const loading = ref(false); const ordering = ref(false)
const removeDialog = ref(false); const removing = ref(null)
const payDialog = ref(false); const payMethod = ref('alipay'); const paying = ref(false); const newOrderId = ref(null); const payAmount = ref(0)
const checkout = ref({ recipient_name: '', recipient_phone: '', recipient_address: '', total_weight: 1, shipping_req: '', invoice_required: 0, invoice_title: '', invoice_tax_no: '', invoice_address_phone: '', invoice_bank: '' })
const shippingCost = computed(() => { const w = parseFloat(checkout.value.total_weight) || 0; return w <= 1 ? 0 : Math.ceil((w - 1)) * 8 })
const loadCart = async () => { loading.value = true; try { const r = await axios.get(`/api/cart/${customerId.value}`); cart.value = r.data } catch { cart.value = { items: [], total_price: 0, item_count: 0 } } finally { loading.value = false } }
const loadAddresses = async () => { try { const r = await axios.get(`/api/customers/${customerId.value}/addresses`); addresses.value = r.data; const d = r.data.find(a => a.is_default); if (d) { selectedAddress.value = d.address_id; fillAddress(d.address_id) } } catch {} }
const fillAddress = (id) => { const a = addresses.value.find(x => x.address_id === id); if (a) { checkout.value.recipient_name = a.recipient_name; checkout.value.recipient_phone = a.phone; checkout.value.recipient_address = a.address } }
const updateQty = async (pid, qty) => { try { await axios.put(`/api/cart/${customerId.value}/update/${pid}`, null, { params: { quantity: qty } }) } catch {}; loadCart() }
const confirmRemove = (item) => { removing.value = item; removeDialog.value = true }
const doRemove = async () => { try { await axios.delete(`/api/cart/${customerId.value}/remove/${removing.value.product_id}`); ElMessage.success('已移除') } catch { ElMessage.error('操作失败') }; removeDialog.value = false; loadCart() }
const submitOrder = async () => {
  if (!checkout.value.recipient_name || !checkout.value.recipient_phone || !checkout.value.recipient_address) { ElMessage.warning('请填写完整的收货信息'); return }
  ordering.value = true
  try {
    const items = cart.value.items.map(i => ({ product_id: i.product_id, manufacturer_id: 1, quantity: i.quantity, unit_price: i.unit_price }))
    const r = await axios.post('/api/orders/', { customer_id: customerId.value, ...checkout.value, items })
    newOrderId.value = r.data.order_id; payAmount.value = r.data.total_amount; payDialog.value = true
  } catch (e) { ElMessage.error(e.response?.data?.detail || '下单失败') } finally { ordering.value = false }
}
const doPay = async () => {
  paying.value = true
  try { await axios.post('/api/payments/', { order_id: newOrderId.value, payment_method: payMethod.value, amount: payAmount.value }); ElMessage.success('支付成功！'); payDialog.value = false; router.push(`/orders/${newOrderId.value}`) } catch { ElMessage.error('支付失败') } finally { paying.value = false }
}
onMounted(() => { loadCart(); loadAddresses() })
</script>
<style scoped>
.page-title { margin: 0 0 16px; font-size: 20px; }
.empty-state { padding: 60px 0; text-align: center; color: var(--ss-text-muted); }
.empty-icon { font-size: 48px; margin: 0 0 12px; }
.cart-summary { padding: 12px 0; text-align: right; font-size: 14px; }
.checkout-card { margin-top: 16px; }
.checkout-hd { font-weight: 600; font-size: 15px; }
.checkout-total { padding: 14px 0; border-top: 1px solid var(--ss-border-light); text-align: right; font-size: 13px; color: var(--ss-text-muted); }
.pay-amount { font-size: 18px; font-weight: 700; color: var(--ss-accent); }
.pay-methods { display: flex; flex-direction: column; gap: 10px; }
.pay-method-item { margin: 0 !important; }
</style>
