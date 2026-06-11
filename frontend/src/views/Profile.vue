<template>
  <div>
    <div style="display:flex;gap:6px;margin-bottom:16px">
      <el-button :type="tab==='info'?'primary':''" size="small" @click="switchTab('info')">基本信息</el-button>
      <el-button :type="tab==='password'?'primary':''" size="small" @click="switchTab('password')">修改密码</el-button>
      <el-button :type="tab==='addresses'?'primary':''" size="small" @click="switchTab('addresses')">收货地址</el-button>
      <el-button :type="tab==='favorites'?'primary':''" size="small" @click="switchTab('favorites')">我的收藏</el-button>
    </div>

    <el-card v-if="tab==='info'" v-loading="pLoading" style="margin-bottom:14px">
      <template #header><span style="font-weight:600;font-size:15px">基本信息</span><el-button v-if="!editing" type="primary" size="small" style="float:right" @click="startEdit">编辑</el-button><el-button v-else type="primary" size="small" style="float:right" @click="save" :loading="saving">保存</el-button><el-button v-if="editing" size="small" style="float:right;margin-right:8px" @click="cancelEdit" :disabled="saving">取消</el-button></template>
      <el-form :model="form" label-width="80px" :disabled="!editing">
        <el-form-item label="头像"><div style="display:flex;align-items:center;gap:12px"><el-avatar :size="56" :src="form.avatar" v-if="form.avatar" /><el-icon v-else :size="56" color="var(--color-text-dim)"><User /></el-icon><el-button v-if="editing" size="small" @click="$refs.fi.click()">更换</el-button></div></el-form-item>
        <el-form-item label="用户名"><el-input v-model="form.username" disabled /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.customer_name" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
      </el-form>
      <input type="file" ref="fi" accept="image/*" style="display:none" @change="handleFile" />
    </el-card>

    <el-card v-if="tab==='password'" style="margin-bottom:14px">
      <template #header><span style="font-weight:600;font-size:15px">修改密码</span></template>
      <el-form :model="pw" :rules="pwRules" ref="pwRef" label-width="100px" style="max-width:400px">
        <el-form-item label="原密码" prop="old_password"><el-input v-model="pw.old_password" type="password" show-password /></el-form-item>
        <el-form-item label="新密码" prop="new_password"><el-input v-model="pw.new_password" type="password" show-password /></el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password"><el-input v-model="pw.confirm_password" type="password" show-password /></el-form-item>
        <el-form-item><el-button type="primary" @click="changePw" :loading="pwLoading">确认修改</el-button></el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="tab==='addresses'" style="margin-bottom:14px">
      <template #header><div style="display:flex;justify-content:space-between;align-items:center"><span style="font-weight:600;font-size:15px">收货地址</span><el-button type="primary" size="small" @click="openAddr()">新增</el-button></div></template>
      <el-table :data="addresses" v-if="addresses.length">
        <el-table-column prop="recipient_name" label="收件人" width="80" /><el-table-column prop="phone" label="电话" width="120" /><el-table-column prop="address" label="地址" />
        <el-table-column width="100"><template #default="s"><el-tag v-if="s.row.is_default" type="success" size="small">默认</el-tag><span v-else style="font-size:12px;color:var(--color-text-muted)">{{ s.row.tag||'' }}</span></template></el-table-column>
        <el-table-column label="操作" width="140"><template #default="s"><el-button size="small" @click="openAddr(s.row)">编辑</el-button><el-popconfirm title="确认删除？" @confirm="delAddr(s.row.address_id)"><template #reference><el-button size="small" type="danger">删除</el-button></template></el-popconfirm></template></el-table-column>
      </el-table>
      <el-empty v-else description="暂无收货地址" :image-size="60" />
    </el-card>

    <el-card v-if="tab==='favorites'">
      <template #header><span style="font-weight:600;font-size:15px">我的收藏</span></template>
      <el-row :gutter="12" v-if="favorites.length">
        <el-col :xs="12" :sm="6" v-for="f in favorites" :key="f.favorite_id"><div style="padding:12px;border:1px solid var(--color-border-light);border-radius:6px;cursor:pointer;margin-bottom:12px" @click="$router.push(`/products/${f.product_id}`)"><div style="font-size:13px;font-weight:600;margin-bottom:4px">{{f.product_name}}</div><div style="color:var(--color-accent);font-weight:700">¥{{f.unit_price}}</div></div></el-col>
      </el-row>
      <el-empty v-else description="暂无收藏" :image-size="60"><el-button type="primary" size="small" @click="$router.push('/products')">去逛逛</el-button></el-empty>
    </el-card>

    <el-dialog v-model="addrVisible" :title="addrEdit?'编辑地址':'新增地址'" width="420px">
      <el-form :model="addrForm" label-width="80px">
        <el-form-item label="收件人"><el-input v-model="addrForm.recipient_name" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="addrForm.phone" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="addrForm.address" /></el-form-item>
        <el-form-item label="标签"><el-select v-model="addrForm.tag" placeholder="选择" clearable allow-create filterable><el-option v-for="t in ['家','公司','仓库','学校']" :key="t" :label="t" :value="t" /></el-select></el-form-item>
        <el-form-item label="默认"><el-switch v-model="addrForm.is_default" :active-value="1" :inactive-value="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="addrVisible=false">取消</el-button><el-button type="primary" @click="saveAddr" :loading="addrSaving">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const route = useRoute(); const router = useRouter(); const userStore = useUserStore()
const tab = ref('info')
const pLoading = ref(false); const saving = ref(false); const editing = ref(false)
const form = ref({username:'',customer_name:'',address:'',phone:'',email:'',role:'',avatar:''})
const pw = ref({old_password:'',new_password:'',confirm_password:''}); const pwLoading = ref(false); const pwRef = ref(null)
const pwRules = { old_password:[{required:true,message:'请输入原密码',trigger:'blur'}], new_password:[{required:true,min:6,message:'新密码至少6位',trigger:'blur'}], confirm_password:[{required:true,validator:(r,v,cb)=>v===pw.value.new_password?cb():cb(new Error('两次密码不一致')),trigger:'blur'}] }
const addresses = ref([]); const favorites = ref([]); let backup = {}
const addrVisible = ref(false); const addrEdit = ref(null); const addrSaving = ref(false)
const addrForm = ref({recipient_name:'',phone:'',address:'',tag:'',is_default:0})

const switchTab = (t) => { tab.value = t; router.replace({query:t==='info'?{}:{tab:t}}) }

const fetchProfile = async () => { pLoading.value = true; try { const r = await axios.get(`/api/customers/${userStore.user.customer_id}`); Object.assign(form.value, r.data) } catch {} finally { pLoading.value = false } }
const fetchAddresses = async () => { try { const r = await axios.get(`/api/customers/${userStore.user.customer_id}/addresses`); addresses.value = r.data } catch {} }
const fetchFavorites = async () => { try { const r = await axios.get(`/api/customers/${userStore.user.customer_id}/favorites`); favorites.value = r.data } catch {} }

const startEdit = () => { backup = {...form.value}; editing.value = true }
const cancelEdit = () => { Object.assign(form.value, backup); editing.value = false }
const save = async () => { saving.value = true; try { await axios.put(`/api/customers/${userStore.user.customer_id}`, {customer_name:form.value.customer_name,address:form.value.address,phone:form.value.phone,email:form.value.email,avatar:form.value.avatar}); userStore.user.customer_name = form.value.customer_name; localStorage.setItem('customer',JSON.stringify(userStore.user)); ElMessage.success('保存成功'); editing.value = false } catch { ElMessage.error('保存失败') } finally { saving.value = false } }

const changePw = async () => { if (!pwRef.value) return; try { await pwRef.value.validate() } catch { return }; pwLoading.value = true; try { await axios.post(`/api/customers/${userStore.user.customer_id}/change-password`, {old_password:pw.value.old_password,new_password:pw.value.new_password}); ElMessage.success('密码修改成功'); pw.value = {old_password:'',new_password:'',confirm_password:''} } catch(e) { ElMessage.error(e.response?.data?.detail||'修改失败') } finally { pwLoading.value = false } }

const handleFile = (e) => { const f = e.target.files[0]; if(!f)return; const r=new FileReader(); r.onload=ev=>{form.value.avatar=ev.target.result}; r.readAsDataURL(f) }

const openAddr = (addr) => { if(addr){addrEdit.value=addr;addrForm.value={...addr}} else {addrEdit.value=null;addrForm.value={recipient_name:'',phone:'',address:'',tag:'',is_default:0}}; addrVisible.value = true }
const saveAddr = async () => { addrSaving.value = true; try { if(addrEdit.value){await axios.put(`/api/customers/${userStore.user.customer_id}/addresses/${addrEdit.value.address_id}`,addrForm.value);ElMessage.success('更新成功')} else {await axios.post(`/api/customers/${userStore.user.customer_id}/addresses`,addrForm.value);ElMessage.success('新增成功')}; addrVisible.value = false; fetchAddresses() } catch { ElMessage.error('保存失败') } finally { addrSaving.value = false } }
const delAddr = async (id) => { try { await axios.delete(`/api/customers/${userStore.user.customer_id}/addresses/${id}`); ElMessage.success('已删除'); fetchAddresses() } catch {} }

onMounted(() => {
  if (route.query.tab) tab.value = route.query.tab
  fetchProfile(); fetchAddresses(); fetchFavorites()
})
</script>
