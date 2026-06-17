<template>
  <div class="auth-page">
    <el-card class="auth-card">
      <template #header><h2 class="auth-title">找回密码</h2></template>
      <div v-if="message" class="auth-success">{{ message }}</div>
      <div v-if="error" class="auth-error">{{ error }}</div>
      <p style="font-size:13px;color:var(--ss-text-muted);margin-bottom:16px">输入您的用户名和注册邮箱，密码将重置为默认值</p>
      <el-form @submit.prevent="handleReset">
        <el-form-item label="用户名"><el-input v-model="username" placeholder="请输入用户名" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="email" placeholder="请输入注册邮箱" /></el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" style="width:100%">重置密码</el-button>
        </el-form-item>
      </el-form>
      <div class="auth-links"><router-link to="/login">返回登录</router-link></div>
    </el-card>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import axios from 'axios'
const username = ref(''); const email = ref(''); const loading = ref(false)
const message = ref(''); const error = ref('')
const handleReset = async () => {
  if (!username.value || !email.value) { error.value = '请填写完整信息'; return }
  loading.value = true; error.value = ''
  try {
    const r = await axios.post('/api/customers/forgot-password', null, { params: { username: username.value, email: email.value } })
    message.value = r.data.message
  } catch (e) { error.value = e.response?.data?.detail || '重置失败' }
  finally { loading.value = false }
}
</script>
<style scoped>
.auth-page { min-height: 70vh; display: flex; align-items: center; justify-content: center; padding: 40px 16px; }
.auth-card { width: 100%; max-width: 400px; }
.auth-title { text-align: center; margin: 0; font-size: 20px; }
.auth-error { background: var(--ss-danger-bg); color: var(--ss-danger); padding: 10px 14px; border-radius: var(--ss-radius-sm); margin-bottom: 14px; font-size: 13px; }
.auth-success { background: var(--ss-success-bg); color: var(--ss-success); padding: 10px 14px; border-radius: var(--ss-radius-sm); margin-bottom: 14px; font-size: 13px; }
.auth-links { text-align: center; font-size: 13px; }
.auth-links a { color: var(--ss-primary); text-decoration: none; }
</style>
