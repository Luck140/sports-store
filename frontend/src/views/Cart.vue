<template>
  <div v-loading="cartLoading">
    <el-card v-if="cart.items && cart.items.length" style="margin-bottom:16px">
      <template #header><span style="font-weight:600;font-size:16px">购物车（{{ cart.item_count }} 件商品）</span></template>
      <el-table :data="cart.items" size="default">
        <el-table-column label="商品" min-width="160">
          <template #default="scope">{{ scope.row.product_name || '商品' }}</template>
        </el-table-column>
        <el-table-column label="单价" width="100"><template #default="scope">¥{{ scope.row.unit_price }}</template></el-table-column>
        <el-table-column label="数量" width="150">
          <template #default="scope">
            <el-input-number v-model="scope.row.quantity" :min="1" :max="scope.row.stock_quantity || 999" size="small" @change="updateQty(scope.row)" controls-position="right" />
          </template>
        </el-table-column>
        <el-table-column label="小计" width="110"><template #default="scope"><span style="color:var(--color-accent);font-weight:600">¥{{ scope.row.subtotal }}</span></template></el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="scope"><el-popconfirm title="确认删除该商品？" @confirm="remove(scope.row.product_id)"><template #reference><el-button type="danger" link size="small">删除</el-button></template></el-popconfirm></template>
        </el-table-column>
      </el-table>
      <div style="text-align:right;margin-top:16px;font-size:15px">商品合计：<strong style="color:var(--color-accent);font-size:22px">¥{{ cart.total_price }}</strong></div>
    </el-card>

    <el-empty v-if="!cart.items || !cart.items.length" description="购物车是空的">
      <el-button type="primary" @click="$router.push('/products')">去选购商品</el-button>
    </el-empty>

    <el-card v-if="cart.items && cart.items.length">
      <template #header><span style="font-weight:600;font-size:16px">结算信息</span></template>
      <el-form :model="info" :rules="rules" ref="infoFormRef" label-width="90px">
        <el-divider content-position="left">收货地址</el-divider>
        <el-form-item v-if="addresses.length" label="选择地址">
          <el-select v-model="selectedAddressId" @change="selectAddress" clearable placeholder="选择已有收货地址" style="width:100%">
            <el-option v-for="a in addresses" :key="a.address_id" :label="`${a.recipient_name} — ${a.phone} — ${a.address}`" :value="a.address_id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="8"><el-form-item label="收件人" prop="recipient_name"><el-input v-model="info.recipient_name" placeholder="请输入收件人" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="联系电话" prop="recipient_phone"><el-input v-model="info.recipient_phone" placeholder="请输入手机号" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="运输要求"><el-input v-model="info.shipping_req" placeholder="如：工作日送货" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="收货地址" prop="recipient_address"><el-input v-model="info.recipient_address" placeholder="省/市/区/详细地址" /></el-form-item>

        <el-divider content-position="left">运费</el-divider>
        <el-form-item label="货物总重">
          <el-input-number v-model="info.total_weight" :min="0" :precision="1" style="width:180px" /><span style="margin-left:8px;color:var(--color-text-muted);font-size:12px">千克（根据商品数量估算，可手动调整）</span>
        </el-form-item>
        <el-form-item label="运费规则"><span style="font-size:13px;color:var(--color-text-2)">首重1kg内<strong>包邮</strong>，超出后每1kg加收 ¥8 &nbsp; 预计运费：<strong style="color:var(--color-accent)">¥{{ shippingCost }}</strong></span></el-form-item>

        <el-divider content-position="left">发票信息</el-divider>
        <el-form-item label="发票类型">
          <el-radio-group v-model="invoiceType">
            <el-radio value="">不需要</el-radio>
            <el-radio value="normal">普通发票</el-radio>
            <el-radio value="vat">增值税专用发票</el-radio>
          </el-radio-group>
        </el-form-item>
        <template v-if="invoiceType">
          <el-row :gutter="12">
            <el-col :span="12"><el-form-item :label="invoiceType === 'vat' ? '单位名称' : '发票抬头'"><el-input v-model="info.invoice_title" :placeholder="invoiceType === 'vat' ? '请输入单位全称' : '个人或单位名称'" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="纳税人识别号"><el-input v-model="info.invoice_tax_no" placeholder="请输入税号" /></el-form-item></el-col>
          </el-row>
        </template>

        <el-divider />
        <div style="text-align:right;padding:12px 0;font-size:14px;line-height:2">
          <div>商品金额：<strong>¥{{ cart.total_price }}</strong></div>
          <div>运费：<strong>¥{{ shippingCost }}</strong></div>
          <div style="font-size:18px;margin-top:4px">实付金额：<strong style="color:var(--color-accent)">¥{{ grandTotal }}</strong></div>
          <el-button type="primary" size="large" @click="checkout" :loading="submitting" style="margin-top:12px;min-width:160px">确认下单</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const cart = ref({ items: [], total_price: 0, item_count: 0 })
const cartLoading = ref(false)
const addresses = ref([])
const selectedAddressId = ref(null)
const infoFormRef = ref(null)
const info = ref({ recipient_name: '', recipient_phone: '', recipient_address: '', total_weight: 0, shipping_req: '', invoice_required: 0, invoice_title: '', invoice_tax_no: '' })
const invoiceType = ref('')
const submitting = ref(false)

const shippingCost = computed(() => { const w = parseFloat(info.value.total_weight) || 0; if (w <= 1) return 0; return Math.round((w - 1) * 8 * 100) / 100 })
const grandTotal = computed(() => Math.round((cart.value.total_price + shippingCost.value) * 100) / 100)

const rules = {
  recipient_name: [{ required: true, message: '请输入收件人姓名', trigger: 'blur' }],
  recipient_phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }, { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' }],
  recipient_address: [{ required: true, message: '请输入收货地址', trigger: 'blur' }],
}

// Auto-estimate weight from item count
watch(() => cart.value.item_count, (n) => { if (n > 0 && !info.value.total_weight) { info.value.total_weight = Math.round(n * 0.5 * 10) / 10 } })

const fetchCart = async () => { cartLoading.value = true; try { const r = await axios.get(`/api/cart/${userStore.user.customer_id}`); cart.value = r.data } catch {} finally { cartLoading.value = false } }
const fetchAddresses = async () => { try { const r = await axios.get(`/api/customers/${userStore.user.customer_id}/addresses`); addresses.value = r.data } catch {} }

const updateQty = async (item) => { try { await axios.put(`/api/cart/${userStore.user.customer_id}/update/${item.product_id}`, null, { params: { quantity: item.quantity } }); fetchCart() } catch (e) { ElMessage.error(e.response?.data?.detail || '修改失败'); fetchCart() } }
const remove = async (pid) => { try { await axios.delete(`/api/cart/${userStore.user.customer_id}/remove/${pid}`); fetchCart(); ElMessage.success('已删除') } catch {} }
const selectAddress = (id) => { const a = addresses.value.find(x => x.address_id === id); if (a) { info.value.recipient_name = a.recipient_name; info.value.recipient_phone = a.phone; info.value.recipient_address = a.address } }

const checkout = async () => {
  if (!infoFormRef.value) return
  try { await infoFormRef.value.validate() } catch { return }
  submitting.value = true
  try {
    const payload = { customer_id: userStore.user.customer_id, items: cart.value.items.map(i => ({ product_id: i.product_id, manufacturer_id: 1, quantity: i.quantity, unit_price: 0 })), ...info.value, invoice_required: invoiceType.value ? 1 : 0 }
    const res = await axios.post('/api/orders/', payload)
    ElMessage.success(`下单成功！订单号 ${res.data.order_id}`)
    router.push(`/orders/${res.data.order_id}`)
  } catch (e) { ElMessage.error(e.response?.data?.detail || '下单失败，请稍后重试') }
  finally { submitting.value = false }
}

onMounted(() => { fetchCart(); fetchAddresses() })
</script>
