<template>
  <div class="form-page">
    <h2>欢迎登录</h2>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" @keyup.enter="login">
      <el-form-item label="用户名" prop="username"><el-input v-model="form.username" placeholder="请输入用户名" /></el-form-item>
      <el-form-item label="密码" prop="password"><el-input v-model="form.password" type="password" placeholder="请输入密码" show-password /></el-form-item>
      <el-form-item>
        <el-button type="primary" @click="login" :loading="loading">登录</el-button>
        <router-link to="/register"><el-button :disabled="loading">去注册</el-button></router-link>
        <router-link to="/forgot-password"><el-button link :disabled="loading">忘记密码</el-button></router-link>
      </el-form-item>
    </el-form>
    <p v-if="msg" :class="['form-msg', msgType]">{{ msg }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const form = ref({ username: '', password: '' })
const msg = ref('')
const msgType = ref('error')
const loading = ref(false)

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const login = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  msg.value = ''
  loading.value = true
  try {
    const res = await axios.post('/api/customers/login', null, { params: form.value })
    userStore.login(res.data)
    if (res.data.role === 'admin') router.push('/admin')
    else router.push('/products')
  } catch (e) {
    msg.value = e.response?.data?.detail || '登录失败，请检查用户名和密码'
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