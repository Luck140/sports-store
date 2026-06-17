<template>
  <div>
    <div class="profile-tabs">
      <el-button :type="tab === 'info' ? 'primary' : 'default'" @click="tab = 'info'">基本信息</el-button>
      <el-button :type="tab === 'password' ? 'primary' : 'default'" @click="tab = 'password'">修改密码</el-button>
      <el-button :type="tab === 'addresses' ? 'primary' : 'default'" @click="tab = 'addresses'">收货地址</el-button>
      <el-button :type="tab === 'favorites' ? 'primary' : 'default'" @click="tab = 'favorites'">我的收藏</el-button>
    </div>
    <el-card v-if="tab === 'info'">
      <template #header><span class="section-title">基本信息</span></template>
      <div class="avatar-section">
        <div class="avatar-ring"><img v-if="avatar" :src="avatar" class="avatar-img" /><span v-else class="avatar-txt">{{ (profile.customer_name || 'U')[0] }}</span></div>
        <el-button size="small" @click="uploadAvatar">更换头像</el-button>
        <input type="file" ref="fileInput" accept="image/*" style="display:none" @change="onFileChange" />
      </div>
      <el-form :model="profile" label-width="80px">
        <el-form-item label="用户名"><span>{{ profile.username }}</span></el-form-item>
        <el-form-item label="姓名"><el-input v-model="profile.customer_name" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="profile.phone" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="profile.email" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="profile.address" /></el-form-item>
        <el-form-item><el-button type="primary" @click="saveProfile" :loading="saving">保存修改</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card v-if="tab === 'password'">
      <template #header><span class="section-title">修改密码</span></template>
      <el-form :model="pwdForm" label-width="100px" style="max-width:400px">
        <el-form-item label="原密码"><el-input v-model="pwdForm.old_password" type="password" show-password /></el-form-item>
        <el-form-item label="新密码"><el-input v-model="pwdForm.new_password" type="password" show-password /></el-form-item>
        <el-form-item label="确认密码"><el-input v-model="pwdForm.confirm" type="password" show-password /></el-form-item>
        <el-form-item><el-button type="primary" @click="changePwd" :loading="pwdLoading">修改密码</el-button></el-form-item>
      </el-form>
      <div v-if="pwdMsg" :style="{ color: pwdMsg.includes('成功') ? 'var(--ss-success)' : 'var(--ss-danger)', marginTop: 8 }">{{ pwdMsg }}</div>
    </el-card>
    <el-card v-if="tab === 'addresses'">
      <template #header><span class="section-title" style="display:flex;justify-content:space-between;align-items:center">收货地址<el-button size="small" type="primary" @click="openAddr()">+ 添加地址</el-button></span></template>
      <el-table :data="addresses" style="width:100%">
        <el-table-column prop="recipient_name" label="收件人" width="100" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="address" label="地址" min-width="200" />
        <el-table-column prop="tag" label="标签" width="80" />
        <el-table-column label="默认" width="60"><template #default="{row}">{{ row.is_default ? '✅' : '' }}</template></el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{row}"><el-button size="small" text @click="openAddr(row)">编辑</el-button><el-button size="small" text type="danger" @click="delAddr(row)">删除</el-button></template>
        </el-table-column>
      </el-table>
    </el-card>
    <div v-if="tab === 'favorites'">
      <div v-if="favorites.length === 0" class="empty-state">
        <p class="empty-icon">❤️</p><p>还没有收藏商品</p>
        <el-button type="primary" @click="$router.push('/products')">去逛逛</el-button>
      </div>
      <el-row :gutter="14" v-else>
        <el-col :xs="12" :sm="8" :md="6" v-for="f in favorites" :key="f.favorite_id">
          <div class="fav-card" @click="$router.push(`/products/${f.product_id}`)">
            <div class="fav-icon">{{ getFavIcon(f) }}</div>
            <div class="fav-name">{{ f.product_name }}</div>
            <div class="fav-price">¥{{ f.unit_price }}</div>
          </div>
        </el-col>
      </el-row>
    </div>
    <el-dialog v-model="addrDlg" :title="editAddr ? '编辑地址' : '添加地址'" width="480px">
      <el-form :model="addrForm" label-width="80px">
        <el-form-item label="收件人"><el-input v-model="addrForm.recipient_name" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="addrForm.phone" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="addrForm.address" type="textarea" rows="2" /></el-form-item>
        <el-form-item label="标签"><el-select v-model="addrForm.tag" allow-create filterable clearable style="width:100%"><el-option label="家" value="家" /><el-option label="公司" value="公司" /><el-option label="学校" value="学校" /></el-select></el-form-item>
        <el-form-item label="默认地址"><el-switch v-model="addrForm.is_default" :active-value="1" :inactive-value="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="addrDlg = false">取消</el-button><el-button type="primary" @click="saveAddr" :loading="addrSaving">保存</el-button></template>
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
const tab = ref(route.query.tab || 'info')
const profile = ref({}); const avatar = ref(''); const saving = ref(false); const fileInput = ref(null)
const pwdForm = ref({ old_password: '', new_password: '', confirm: '' }); const pwdLoading = ref(false); const pwdMsg = ref('')
const addresses = ref([]); const favorites = ref([])
const addrDlg = ref(false); const editAddr = ref(null); const addrSaving = ref(false)
const addrForm = ref({ recipient_name: '', phone: '', address: '', tag: '', is_default: 0 })
const icons = ['🏀', '⚽', '🏸', '👕', '⚾', '🏐', '🏓', '🎽', '🩳', '🧢']
const getFavIcon = (f) => getProductIcon(f)

const loadProfile = async () => {
  try {
    const r = await axios.get(`/api/customers/${userStore.user.customer_id}`)
    profile.value = r.data
    if (r.data.avatar) avatar.value = r.data.avatar
  } catch (e) {
    console.error('loadProfile error:', e)
    ElMessage.error('加载个人信息失败')
  }
}
const loadAddresses = async () => {
  try { const r = await axios.get(`/api/customers/${userStore.user.customer_id}/addresses`); addresses.value = r.data } catch (e) { console.error('loadAddresses error:', e) }
}
const loadFavorites = async () => {
  try { const r = await axios.get(`/api/customers/${userStore.user.customer_id}/favorites`); favorites.value = r.data } catch (e) { console.error('loadFavorites error:', e) }
}

const saveProfile = async () => {
  saving.value = true
  try {
    // 第一步：保存文字信息（姓名、电话、邮箱、地址）
    // 所有字段都发出去，空字符串后端会处理成 None 并排除
    await axios.put(`/api/customers/${userStore.user.customer_id}`, {
      customer_name: profile.value.customer_name || '',
      phone: profile.value.phone || '',
      email: profile.value.email || '',
      address: profile.value.address || '',
      avatar: avatar.value || ''
    })
    ElMessage.success('保存成功')
    // 重新加载最新数据
    await loadProfile()
    // 通知侧边栏更新头像
    if (avatar.value) {
      window.dispatchEvent(new CustomEvent('avatar-updated', { detail: avatar.value }))
    }
  } catch (e) {
    const msg = e.response?.data?.detail || '保存失败，请重试'
    ElMessage.error(msg)
    console.error('saveProfile error:', e)
  } finally { saving.value = false }
}

const uploadAvatar = () => fileInput.value?.click()
const onFileChange = (e) => {
  const f = e.target.files[0]; if (!f) return
  // 限制图片大小 2MB
  if (f.size > 2 * 1024 * 1024) {
    ElMessage.warning('图片不能超过 2MB')
    return
  }
  const reader = new FileReader()
  reader.onload = (ev) => { avatar.value = ev.target.result }
  reader.readAsDataURL(f)
}

const changePwd = async () => {
  if (pwdForm.value.new_password.length < 6) { pwdMsg.value = '新密码至少6位'; return }
  if (pwdForm.value.new_password !== pwdForm.value.confirm) { pwdMsg.value = '两次密码不一致'; return }
  pwdLoading.value = true; pwdMsg.value = ''
  try {
    await axios.post(`/api/customers/${userStore.user.customer_id}/change-password`, {
      old_password: pwdForm.value.old_password, new_password: pwdForm.value.new_password
    })
    pwdMsg.value = '密码修改成功！'
    pwdForm.value = { old_password: '', new_password: '', confirm: '' }
  } catch (e) { pwdMsg.value = e.response?.data?.detail || '修改失败' }
  finally { pwdLoading.value = false }
}

const openAddr = (addr) => {
  editAddr.value = addr || null
  addrForm.value = addr ? {
    recipient_name: addr.recipient_name, phone: addr.phone,
    address: addr.address, tag: addr.tag || '', is_default: addr.is_default
  } : { recipient_name: '', phone: '', address: '', tag: '', is_default: 0 }
  addrDlg.value = true
}

const saveAddr = async () => {
  if (!addrForm.value.recipient_name || !addrForm.value.phone || !addrForm.value.address) {
    ElMessage.warning('请填写完整的地址信息')
    addrSaving.value = false
    return
  }
  addrSaving.value = true
  try {
    if (editAddr.value) {
      await axios.put(`/api/customers/${userStore.user.customer_id}/addresses/${editAddr.value.address_id}`, addrForm.value)
    } else {
      await axios.post(`/api/customers/${userStore.user.customer_id}/addresses`, addrForm.value)
    }
    ElMessage.success('保存成功')
    addrDlg.value = false
    loadAddresses()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally { addrSaving.value = false }
}

const delAddr = async (addr) => {
  try {
    await ElMessageBox.confirm('确定删除此地址？')
    await axios.delete(`/api/customers/${userStore.user.customer_id}/addresses/${addr.address_id}`)
    ElMessage.success('已删除')
    loadAddresses()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => { loadProfile(); loadAddresses(); loadFavorites() })

watch(() => route.query.tab, (newTab) => {
  if (newTab && newTab !== tab.value) tab.value = newTab
})
</script>
<style scoped>
.profile-tabs { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.section-title { font-weight: 600; font-size: 15px; }
.avatar-section { text-align: center; margin-bottom: 16px; }
.avatar-ring { width: 64px; height: 64px; border-radius: 50%; background: var(--ss-primary-light); display: inline-flex; align-items: center; justify-content: center; font-size: 28px; color: #fff; overflow: hidden; margin-bottom: 6px; }
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.avatar-txt { font-weight: 700; }
.empty-state { padding: 40px; text-align: center; color: var(--ss-text-muted); }
.empty-icon { font-size: 48px; margin: 0 0 12px; }
.fav-card { background: var(--ss-surface); border: 1px solid var(--ss-border-light); border-radius: var(--ss-radius-sm); padding: 14px; text-align: center; cursor: pointer; transition: all var(--ss-transition-base); margin-bottom: 12px; }
.fav-card:hover { border-color: var(--ss-primary); box-shadow: var(--ss-shadow-md); transform: translateY(-1px); }
.fav-icon { font-size: 40px; padding: 8px 0; }
.fav-name { font-weight: 600; font-size: 13px; }
.fav-price { color: var(--ss-accent); font-weight: 700; font-size: 16px; margin-top: 4px; }
</style>
