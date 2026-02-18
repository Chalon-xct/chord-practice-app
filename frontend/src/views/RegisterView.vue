<template>
  <div class="auth-view">
    <div class="auth-card card">
      <h2>注册</h2>
      
      <div v-if="error" class="error-message">{{ error }}</div>
      <div v-if="success" class="success-message">{{ success }}</div>
      
      <form @submit.prevent="handleRegister">
        <div class="input-group">
          <label>用户名</label>
          <input 
            type="text" 
            v-model="username" 
            placeholder="请输入用户名"
            required
          />
        </div>
        
        <div class="input-group">
          <label>邮箱</label>
          <input 
            type="email" 
            v-model="email" 
            placeholder="请输入邮箱"
            required
          />
        </div>
        
        <div class="input-group">
          <label>密码</label>
          <input 
            type="password" 
            v-model="password" 
            placeholder="请输入密码"
            required
            minlength="6"
          />
        </div>
        
        <button type="submit" class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="loading"></span>
          <span v-else>注册</span>
        </button>
      </form>
      
      <p class="auth-link">
        已有账号？<router-link to="/login">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

async function handleRegister() {
  loading.value = true
  error.value = ''
  success.value = ''
  
  try {
    const response = await axios.post('/api/auth/register', {
      username: username.value,
      email: email.value,
      password: password.value
    })
    
    authStore.setAuth(response.data.token, response.data.user)
    router.push('/practice')
  } catch (err) {
    error.value = err.response?.data?.error || '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  padding: 40px;
}

.auth-card h2 {
  text-align: center;
  margin-bottom: 32px;
  font-size: 28px;
}

.auth-link {
  text-align: center;
  margin-top: 24px;
  color: rgba(255, 255, 255, 0.6);
}

.auth-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.auth-link a:hover {
  text-decoration: underline;
}

form {
  display: flex;
  flex-direction: column;
}

.btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
</style>
