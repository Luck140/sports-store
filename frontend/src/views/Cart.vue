<template>
  <el-card>
    <template #header><span style="font-weight:bold;font-size:16px">我的购物车</span></template>
    <el-table :data="cart.items" v-if="cart.items?.length" empty-text="购物车为空">
      <el-table-column label="商品ID" prop="product_id" />
      <el-table-column label="数量" prop="quantity" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button type="danger" size="small" @click="remove(scope.row.product_id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-else description="购物车为空" />

    <div v-if="cart.items?.length" style="margin-top:20px">
      <el-divider>邮寄信息</el-divider>
      <el-form :model="info" :rules="rules" ref="infoFormRef" label-width="100px" inline>
        <el-form-item label="收件人" prop="recipient_name"><el-input v-model="info.recipient_name" placeholder="请输入收件人姓名" /></el-form-item>
        <el-form-item label="联系电话" prop="recipient_phone"><el-input v-model="info.recipient_phone" placeholder="请输入手机号码" /></el-form-item>
        <el-form-item label="收件地址" prop="recipient_address"><el-input v-model="info.recipient_address" style="width:300px" placeholder="请输入详细地址" /></el-form-item>
        <el-form-item label="货物重量(kg)"><el-input-number v-model="info.total_weight" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="运输要求"><el-input v-model="info.shipping_req" placeholder="选填" /></el-form-item>
      </el-form>

      <el-divider>发票信息</el-divider>
      <el-form :model="info" label-width="100px" inline>
        <el-form-item label="需要发票"><el-switch v-model="info.invoice_required" :active-value="1" :inactive-value="0" /></el-form-item>
        <el-form-item label="发票抬头" v-if="info.invoice_required"><el-input v-model="info.invoice_title" /></el-form-item>
        <el-form-item label="税号" v-if="info.invoice_required"><el-input v-model="info.invoice_tax_no" /></el-form-item>
      </el-form>

      <div style="text-align:right;margin-top:16px">
        <el-button type="primary" size="large" @click="checkout" :loading="submitting">提交订单</el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const cart = ref({ items: [] })
const infoFormRef = ref(null)
const info = ref({
  recipient_name: '', recipient_phone: '', recipient_address: '',
  total_weight: 0, shipping_req: '',
  invoice_required: 0, invoice_title: '', invoice_tax_no: ''
})
const submitting = ref(false)

const rules = {
  recipient_name: [{ required: true, message: '请输入收件人姓名', trigger: 'blur' }],
  recipient_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
  recipient_address: [{ required: true, message: '请输入收件地址', trigger: 'blur' }],
}

const fetchCart = async () => { const res = await axios.get(`/api/cart/${userStore.user.customer_id}`); cart.value = res.data }
const remove = async (pid) => { await axios.delete(`/api/cart/${userStore.user.customer_id}/remove/${pid}`); fetchCart(); ElMessage.success('已删除') }

const checkout = async () => {
  if (!infoFormRef.value) return
  try { await infoFormRef.value.validate() } catch { return }
  submitting.value = true
  const items = cart.value.items.map(i => ({ product_id: i.product_id, manufacturer_id: 1, quantity: i.quantity, unit_price: 0 }))
  try {
    const res = await axios.post('/api/orders/', {
      customer_id: userStore.user.customer_id, items,
      ...info.value
    })
    ElMessage.success(`订单创建成功，订单号: ${res.data.order_id}`)
    router.push('/orders')
  } catch (e) { ElMessage.error('下单失败，请稍后重试') }
  finally { submitting.value = false }
}
onMounted(fetchCart)
</script>