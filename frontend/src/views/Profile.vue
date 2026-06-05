<template>
  <el-card>
    <template #header>
      <span style="font-weight:bold;font-size:16px">个人信息</span>
      <el-button v-if="!editing" type="primary" size="small" style="float:right" @click="startEdit">编辑</el-button>
      <el-button v-else type="success" size="small" style="float:right" @click="save">保存</el-button>
      <el-button v-if="editing" size="small" style="float:right;margin-right:8px" @click="cancelEdit">取消</el-button>
    </template>
    <el-form :model="form" label-width="100px" :disabled="!editing">
      <el-form-item label="用户名"><el-input v-model="form.username" disabled /></el-form-item>
      <el-form-item label="姓名"><el-input v-model="form.customer_name" /></el-form-item>
      <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
      <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
      <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
      <el-form-item label="角色"><el-tag>{{ form.role === 'admin' ? '管理员' : '顾客' }}</el-tag></el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const form = ref({ username: '', customer_name: '', address: '', phone: '', email: '', role: '' })
const editing = ref(false)
let backup = {}

const fetchProfile = async () => {
  const res = await axios.get(`/api/customers/${userStore.user.customer_id}`)
  Object.assign(form.value, res.data)
}

const startEdit = () => { backup = { ...form.value }; editing.value = true }
const cancelEdit = () => { Object.assign(form.value, backup); editing.value = false }

const save = async () => {
  await axios.put(`/api/customers/${userStore.user.customer_id}`, {
    customer_name: form.value.customer_name, address: form.value.address,
    phone: form.value.phone, email: form.value.email
  })
  userStore.user.customer_name = form.value.customer_name
  localStorage.setItem('customer', JSON.stringify(userStore.user))
  ElMessage.success('保存成功')
  editing.value = false
}

onMounted(fetchProfile)
</script>