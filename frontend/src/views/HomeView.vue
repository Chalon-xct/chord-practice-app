<template>
  <div class="home-view">
    <nav class="navbar">
      <div class="logo">🎸 和弦练习</div>
      <div class="nav-links">
        <template v-if="authStore.isAuthenticated">
          <router-link to="/practice">开始练习</router-link>
          <router-link to="/stats">统计</router-link>
          <router-link to="/history">历史记录</router-link>
          <button @click="handleLogout" class="btn btn-secondary">退出</button>
        </template>
        <template v-else>
          <router-link to="/login">登录</router-link>
          <router-link to="/register">注册</router-link>
        </template>
      </div>
    </nav>

    <div class="hero">
      <h1>每日和弦练习</h1>
      <p class="subtitle">AI 驱动的个性化吉他训练，每天 1 分钟提升你的和弦与听音能力</p>
      
      <div class="features">
        <div class="feature-card">
          <div class="feature-icon">🎸</div>
          <h3>看构成音猜和弦</h3>
          <p>根据显示的音符推断和弦名称</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🎵</div>
          <h3>听单音辨音</h3>
          <p>聆听 442Hz 标准音高的单音并识别</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🎯</div>
          <h3>循序渐进</h3>
          <p>AI 根据你的表现调整难度</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h3>智能总结</h3>
          <p>每次练习后获得详细反馈</p>
        </div>
      </div>

      <router-link v-if="!authStore.isAuthenticated" to="/register" class="btn btn-primary cta-button">
        免费开始练习
      </router-link>
      <router-link v-else to="/practice" class="btn btn-primary cta-button">
        开始今日练习
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.home-view {
  min-height: 100vh;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-links {
  display: flex;
  gap: 24px;
  align-items: center;
}

.nav-links a {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.nav-links a:hover {
  color: white;
}

.hero {
  text-align: center;
  padding: 80px 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.hero h1 {
  font-size: 48px;
  margin-bottom: 16px;
  background: linear-gradient(135deg, #fff 0%, #a5b4fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 60px;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 24px;
  margin-bottom: 60px;
}

.feature-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  transition: transform 0.3s, border-color 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
  border-color: rgba(102, 126, 234, 0.5);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.feature-card h3 {
  font-size: 18px;
  margin-bottom: 8px;
  color: white;
}

.feature-card p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.cta-button {
  font-size: 18px;
  padding: 16px 48px;
}
</style>
