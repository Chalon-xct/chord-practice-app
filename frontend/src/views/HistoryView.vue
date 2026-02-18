<template>
  <div class="history-view">
    <nav class="navbar">
      <div class="logo">🎸 和弦练习</div>
      <div class="nav-links">
        <router-link to="/practice">开始练习</router-link>
        <router-link to="/stats">统计</router-link>
        <button @click="handleLogout" class="btn btn-secondary">退出</button>
      </div>
    </nav>

    <div class="history-container container">
      <h1>练习历史</h1>

      <div v-if="loading" class="loading-container">
        <span class="loading"></span>
      </div>

      <template v-else>
        <div v-if="practices.length === 0" class="no-data card">
          <p>还没有练习记录</p>
          <router-link to="/practice" class="btn btn-primary">开始第一次练习</router-link>
        </div>

        <div v-else class="history-list">
          <div v-for="practice in practices" :key="practice.id" class="history-card card">
            <div class="history-header">
              <div class="history-date">
                {{ formatDateTime(practice.practice_date) }}
              </div>
              <div class="history-score" :class="getScoreClass(practice.score)">
                {{ practice.score }}分
              </div>
            </div>

            <div class="history-details">
              <div class="detail-row">
                <span class="detail-label">级别</span>
                <span class="detail-value">Lv.{{ practice.level }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">正确率</span>
                <span class="detail-value">{{ practice.correct_answers }}/{{ practice.total_questions }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">时长</span>
                <span class="detail-value">{{ formatDuration(practice.duration_seconds) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">和弦</span>
                <span class="detail-value chords">{{ practice.chords_practiced }}</span>
              </div>
            </div>

            <div v-if="practice.deepseek_summary" class="history-summary">
              <h4>AI 总结</h4>
              <p>{{ getSummaryPreview(practice.deepseek_summary) }}</p>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const practices = ref([])

onMounted(async () => {
  try {
    const response = await axios.get('/api/practice/history')
    practices.value = response.data.practices
  } catch (err) {
    console.error('加载历史记录失败:', err)
  } finally {
    loading.value = false
  }
})

function formatDateTime(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatDuration(seconds) {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}分${secs}秒`
}

function getScoreClass(score) {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  return 'needs-work'
}

function getSummaryPreview(summaryStr) {
  try {
    const summary = typeof summaryStr === 'string' ? JSON.parse(summaryStr) : summaryStr
    return summary.overall_comment || '暂无总结'
  } catch {
    return '暂无总结'
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.history-view {
  min-height: 100vh;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-links {
  display: flex;
  gap: 20px;
  align-items: center;
}

.nav-links a {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
}

.nav-links a:hover {
  color: white;
}

.history-container {
  padding: 40px 20px;
}

.history-container h1 {
  font-size: 32px;
  margin-bottom: 32px;
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: 60px;
}

.no-data {
  text-align: center;
  padding: 60px 40px;
}

.no-data p {
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 24px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.history-card {
  padding: 24px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.history-date {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
}

.history-score {
  font-size: 24px;
  font-weight: 700;
  padding: 8px 20px;
  border-radius: 20px;
}

.history-score.excellent {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.history-score.good {
  background: rgba(234, 179, 8, 0.2);
  color: #eab308;
}

.history-score.needs-work {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.history-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.detail-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
}

.detail-value {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
}

.detail-value.chords {
  font-size: 14px;
  color: #667eea;
}

.history-summary {
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
  padding: 16px;
}

.history-summary h4 {
  font-size: 14px;
  color: #667eea;
  margin-bottom: 8px;
}

.history-summary p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
}
</style>
