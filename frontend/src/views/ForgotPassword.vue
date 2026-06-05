<template>
  <div class="form-page">
    <h2>忘记密码</h2>
    <el-form :model="form" label-width="80px">
      <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
      <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
      <el-form-item>
        <el-button type="primary" @click="resetPassword">重置密码</el-button>
        <router-link to="/login"><el-button>返回登录</el-button></router-link>
      </el-form-item>
    </el-form>
    <p v-if="msg" style="color:green;">{{ msg }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
const form = ref({ username: '', email: '' })
const msg = ref('')

const resetPassword = async () => {
  try {
    const res = await axios.post('/api/customers/forgot-password', null, { params: form.value })
    msg.value = res.data.message
  } catch (e) { msg.value = e.response?.data?.detail || '重置失败' }
}
</script>

<style scoped>
.form-page { width:400px; margin:80px auto; }
</style>