<template>
  <div class="form-page">
    <h2>顾客注册</h2>
    <el-form :model="form" label-width="100px">
      <el-form-item label="用户名">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" />
      </el-form-item>
      <el-form-item label="姓名">
        <el-input v-model="form.customer_name" />
      </el-form-item>
      <el-form-item label="地址">
        <el-input v-model="form.address" />
      </el-form-item>
      <el-form-item label="电话">
        <el-input v-model="form.phone" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="form.email" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="register">注册</el-button>
      </el-form-item>
    </el-form>
    <p v-if="msg">{{ msg }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const form = ref({ username: '', password: '', customer_name: '', address: '', phone: '', email: '' })
const msg = ref('')

const register = async () => {
  try {
    await axios.post('/api/customers/register', form.value)
    msg.value = '注册成功，请登录'
  } catch (e) {
    msg.value = e.response?.data?.detail || '注册失败'
  }
}
</script>

<style scoped>
.form-page { width: 500px; margin: 50px auto; }
</style>