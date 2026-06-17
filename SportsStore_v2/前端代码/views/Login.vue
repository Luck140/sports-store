<template>
  <div class="auth-page">
    <el-card class="auth-card">
      <template #header><h2 class="auth-title">登录</h2></template>
      <div v-if="error" class="auth-error">{{ error }}</div>
      <el-form @submit.prevent="handleLogin">
        <el-form-item label="用户名">
          <el-input v-model="username" placeholder="请输入用户名" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" placeholder="请输入密码" show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" style="width:100%">登录</el-button>
        </el-form-item>
      </el-form>
      <div class="auth-links">
        <router-link to="/register">没有账号？立即注册</router-link>
        <span class="auth-sep">|</span>
        <router-link to="/forgot-password">忘记密码</router-link>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
const router = useRouter()
const userStore = useUserStore()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const handleLogin = async () => {
  if (!username.value || !password.value) { error.value = '请输入用户名和密码'; return }
  loading.value = true; error.value = ''
  try {
    const r = await axios.post('/api/customers/login', null, { params: { username: username.value, password: password.value } })
    userStore.login(r.data)
    router.push(userStore.isAdmin ? '/admin' : '/products')
  } catch (e) { error.value = e.response?.data?.detail || '登录失败' }
  finally { loading.value = false }
}
</script>
<style scoped>
.auth-page { min-height: 70vh; display: flex; align-items: center; justify-content: center; padding: 40px 16px; }
.auth-card { width: 100%; max-width: 400px; }
.auth-title { text-align: center; margin: 0; font-size: 20px; }
.auth-error { background: var(--ss-danger-bg); color: var(--ss-danger); padding: 10px 14px; border-radius: var(--ss-radius-sm); margin-bottom: 14px; font-size: 13px; }
.auth-links { text-align: center; font-size: 13px; }
.auth-links a { color: var(--ss-primary); text-decoration: none; }
.auth-sep { margin: 0 8px; color: var(--ss-text-dim); }
</style>
