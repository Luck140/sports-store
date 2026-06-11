<template>
  <div class="form-page">
    <h2>注册账号</h2>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px" @keyup.enter="register">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="请设置登录用户名" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" placeholder="至少6位" show-password />
      </el-form-item>
      <el-form-item label="姓名" prop="customer_name">
        <el-input v-model="form.customer_name" placeholder="请输入真实姓名" />
      </el-form-item>
      <el-form-item label="地址" prop="address">
        <el-input v-model="form.address" placeholder="请输入收货地址" />
      </el-form-item>
      <el-form-item label="电话" prop="phone">
        <el-input v-model="form.phone" placeholder="请输入手机号码" />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" placeholder="请输入邮箱（选填）" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="register" :loading="loading">注册</el-button>
      </el-form-item>
    </el-form>
    <p v-if="msg" :class="['form-msg', msgType]">{{ msg }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const formRef = ref(null)
const form = ref({ username: '', password: '', customer_name: '', address: '', phone: '', email: '' })
const msg = ref('')
const msgType = ref('success')
const loading = ref(false)

const validatePhone = (rule, value, callback) => {
  if (!value) { callback(new Error('请输入手机号码')); return }
  if (!/^1\d{10}$/.test(value)) { callback(new Error('手机号格式不正确')); return }
  callback()
}
const validateEmail = (rule, value, callback) => {
  if (!value) { callback(); return }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) { callback(new Error('邮箱格式不正确')); return }
  callback()
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  customer_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  address: [{ required: true, message: '请输入地址', trigger: 'blur' }],
  phone: [{ required: true, validator: validatePhone, trigger: 'blur' }],
  email: [{ validator: validateEmail, trigger: 'blur' }],
}

const register = async () => {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }
  msg.value = ''
  loading.value = true
  try {
    await axios.post('/api/customers/register', form.value)
    msg.value = '🎉 注册成功，请登录'
    msgType.value = 'success'
  } catch (e) {
    msg.value = e.response?.data?.detail || '注册失败，请稍后重试'
    msgType.value = 'error'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.form-page { width: 90%; max-width: 500px; margin: 50px auto; }
.form-msg { margin-top:12px; padding:8px 12px; border-radius:4px; font-size:13px; }
.form-msg.error { color:var(--color-danger); background:rgba(245,108,108,0.08); }
.form-msg.success { color:var(--color-success); background:rgba(103,194,58,0.08); }
@media (max-width:480px) { .form-page { margin: 30px auto; } }
</style>