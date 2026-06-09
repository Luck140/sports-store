<template>
  <div class="form-page">
    <h2>忘记密码</h2>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" @keyup.enter="resetPassword">
      <el-form-item label="用户名" prop="username"><el-input v-model="form.username" placeholder="请输入用户名" /></el-form-item>
      <el-form-item label="邮箱" prop="email"><el-input v-model="form.email" placeholder="请输入注册邮箱" /></el-form-item>
      <el-form-item>
        <el-button type="primary" @click="resetPassword" :loading="loading">重置密码</el-button>
        <router-link to="/login"><el-button :disabled="loading">返回登录</el-button></router-link>
      </el-form-item>
    </el-form>
    <p v-if="msg" :class="['form-msg', msgType]">{{ msg }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const formRef = ref(null)
const form = ref({ username: '', email: '' })
const msg = ref('')
const msgType = ref('success')
const loading = ref(false)

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
}

const resetPassword = async () => {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }
  msg.value = ''
  loading.value = true
  try {
    const res = await axios.post('/api/customers/forgot-password', null, { params: form.value })
    msg.value = res.data.message || '密码重置链接已发送到您的邮箱'
    msgType.value = 'success'
  } catch (e) {
    msg.value = e.response?.data?.detail || '重置失败，请检查信息是否正确'
    msgType.value = 'error'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.form-page { width:90%; max-width:400px; margin:80px auto; }
.form-msg { margin-top:12px; padding:8px 12px; border-radius:4px; font-size:13px; }
.form-msg.error { color:var(--color-danger); background:rgba(245,108,108,0.08); }
.form-msg.success { color:var(--color-success); background:rgba(103,194,58,0.08); }
@media (max-width:480px) { .form-page { margin:40px auto; } }
</style>