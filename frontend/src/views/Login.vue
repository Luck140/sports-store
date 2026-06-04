<template>
  <div class="form-page">
    <h2>顾客登录</h2>
    <el-form :model="form" label-width="80px">
      <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
      <el-form-item label="密码"><el-input v-model="form.password" type="password" /></el-form-item>
      <el-form-item>
        <el-button type="primary" @click="login">登录</el-button>
        <router-link to="/register"><el-button>去注册</el-button></router-link>
        <router-link to="/forgot-password"><el-button type="text">忘记密码</el-button></router-link>
      </el-form-item>
    </el-form>
    <p v-if="msg" style="color:red;">{{ msg }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const form = ref({ username: '', password: '' })
const msg = ref('')

const login = async () => {
  try {
    const res = await axios.post('/api/customers/login', null, { params: form.value })
    userStore.login(res.data)
    if (res.data.role === 'admin') router.push('/admin')
    else router.push('/products')
  } catch (e) { msg.value = e.response?.data?.detail || '登录失败' }
}
</script>

<style scoped>
.form-page { width:400px; margin:80px auto; }
</style>