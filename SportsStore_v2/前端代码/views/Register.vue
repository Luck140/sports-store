<template>
  <div class="auth-page">
    <el-card class="auth-card">
      <template #header><h2 class="auth-title">注册账号</h2></template>
      <div v-if="error" class="auth-error">{{ error }}</div>
      <div v-if="success" class="auth-success">{{ success }}</div>
      <el-form @submit.prevent="handleRegister">
        <el-form-item label="用户名"><el-input v-model="form.username" placeholder="4-20位字母或数字" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" type="password" placeholder="至少6位" show-password /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.customer_name" placeholder="收货人姓名" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="form.phone" placeholder="11位手机号" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" placeholder="example@email.com" /></el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" style="width:100%">注册</el-button>
        </el-form-item>
      </el-form>
      <div class="auth-links">
        <router-link to="/login">已有账号？立即登录</router-link>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
const router = useRouter()
const form = reactive({ username: '', password: '', customer_name: '', phone: '', email: '' })
const loading = ref(false); const error = ref(''); const success = ref('')
const handleRegister = async () => {
  if (form.username.length < 4) { error.value = '用户名至少4位'; return }
  if (form.password.length < 6) { error.value = '密码至少6位'; return }
  if (!form.customer_name) { error.value = '请输入姓名'; return }
  if (!/^1\d{10}$/.test(form.phone)) { error.value = '请输入正确的11位手机号'; return }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) { error.value = '请输入正确的邮箱格式'; return }
  loading.value = true; error.value = ''
  try {
    await axios.post('/api/customers/register', form)
    success.value = '注册成功！即将跳转登录...'
    setTimeout(() => router.push('/login'), 1500)
  } catch (e) { error.value = e.response?.data?.detail || '注册失败' }
  finally { loading.value = false }
}
</script>
<style scoped>
.auth-page { min-height: 70vh; display: flex; align-items: center; justify-content: center; padding: 40px 16px; }
.auth-card { width: 100%; max-width: 480px; }
.auth-title { text-align: center; margin: 0; font-size: 20px; }
.auth-error { background: var(--ss-danger-bg); color: var(--ss-danger); padding: 10px 14px; border-radius: var(--ss-radius-sm); margin-bottom: 14px; font-size: 13px; }
.auth-success { background: var(--ss-success-bg); color: var(--ss-success); padding: 10px 14px; border-radius: var(--ss-radius-sm); margin-bottom: 14px; font-size: 13px; }
.auth-links { text-align: center; font-size: 13px; }
.auth-links a { color: var(--ss-primary); text-decoration: none; }
</style>
