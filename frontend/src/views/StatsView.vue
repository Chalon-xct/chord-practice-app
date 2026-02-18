<template>
  <div class="stats-view">
    <nav class="navbar">
      <div class="logo">🎸 和弦练习</div>
      <div class="nav-links">
        <router-link to="/practice">开始练习</router-link>
        <router-link to="/history">历史记录</router-link>
        <button @click="handleLogout" class="btn btn-secondary">退出</button>
      </div>
    </nav>

    <div class="stats-container container">
      <h1>学习统计</h1>

      <div v-if="loading" class="loading-container">
        <span class="loading"></span>
      </div>

      <template v-else>
        <div class="stats-grid">
          <div class="stat-card card">
            <div class="stat-icon">📚</div>
            <div class="stat-value">{{ stats.total_practices }}</div>
            <div class="stat-label">总练习次数</div>
          </div>

          <div class="stat-card card">
            <div class="stat-icon">🔥</div>
            <div class="stat-value">{{ stats.current_streak }}</div>
            <div class="stat-label">连续打卡天数</div>
          </div>

          <div class="stat-card card">
            <div class="stat-icon">📊</div>
            <div class="stat-value">{{ stats.average_score }}</div>
            <div class="stat-label">平均得分</div>
          </div>

          <div class="stat-card card">
            <div class="stat-icon">🏆</div>
            <div class="stat-value">{{ stats.best_score }}</div>
            <div class="stat-label">最高得分</div>
          </div>

          <div class="stat-card card">
            <div class="stat-icon">⭐</div>
            <div class="stat-value">Lv.{{ stats.current_level }}</div>
            <div class="stat-label">当前级别</div>
          </div>
          
          <div class="stat-card card level-progress-card">
            <div class="stat-icon">📈</div>
            <div class="stat-value">{{ stats.total_experience }}</div>
            <div class="stat-label">总经验值</div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: (isNaN(stats.level_progress) ? 0 : stats.level_progress * 100) + '%' }"></div>
            </div>
            <div class="progress-text">
              {{ Math.floor(stats.exp_in_level || 0) }} / {{ Math.floor(stats.exp_needed || 100) }} XP
            </div>
          </div>
        </div>

        <div class="level-info card">
          <h2>级别说明</h2>
          <div class="level-descriptions">
            <div class="level-item" :class="{ active: stats.current_level <= 2 }">
              <span class="level-num">1-2 级</span>
              <span class="level-desc">基础三和弦：C, D, E, G, A, Am, Em, Dm</span>
            </div>
            <div class="level-item" :class="{ active: stats.current_level >= 3 && stats.current_level <= 4 }">
              <span class="level-num">3-4 级</span>
              <span class="level-desc">更多调式和弦：F, Bm 等</span>
            </div>
            <div class="level-item" :class="{ active: stats.current_level >= 5 && stats.current_level <= 6 }">
              <span class="level-num">5-6 级</span>
              <span class="level-desc">七和弦：Cmaj7, Dm7, G7 等</span>
            </div>
            <div class="level-item" :class="{ active: stats.current_level >= 7 && stats.current_level <= 8 }">
              <span class="level-num">7-8 级</span>
              <span class="level-desc">延伸和弦、变化和弦</span>
            </div>
            <div class="level-item" :class="{ active: stats.current_level >= 9 }">
              <span class="level-num">9-10 级</span>
              <span class="level-desc">复杂爵士和弦</span>
            </div>
          </div>
        </div>

        <div class="recent-practices card">
          <h2>最近练习</h2>
          <div v-if="recentPractices.length === 0" class="no-data">
            还没有练习记录，开始第一次练习吧！
          </div>
          <div v-else class="practice-list">
            <div v-for="practice in recentPractices" :key="practice.id" class="practice-item">
              <div class="practice-date">{{ formatDate(practice.practice_date) }}</div>
              <div class="practice-info">
                <span class="practice-level">Lv.{{ practice.level }}</span>
                <span class="practice-score" :class="getScoreClass(practice.score)">
                  {{ practice.score }}分
                </span>
                <span class="practice-accuracy">
                  {{ practice.correct_answers }}/{{ practice.total_questions }}
                </span>
              </div>
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
const stats = ref({
  total_practices: 0,
  current_streak: 0,
  average_score: 0,
  best_score: 0,
  current_level: 1,
  total_experience: 0,
  exp_in_level: 0,
  exp_needed: 100,
  level_progress: 0
})
const recentPractices = ref([])

onMounted(async () => {
  await loadStats()
})

async function loadStats() {
  try {
    const [statsRes, historyRes] = await Promise.all([
      axios.get('/api/user/stats'),
      axios.get('/api/practice/history')
    ])
    
    stats.value = statsRes.data
    recentPractices.value = historyRes.data.practices.slice(0, 5)
  } catch (err) {
    console.error('加载统计失败:', err)
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 86400000 && date.getDate() === now.getDate()) {
    return '今天'
  } else if (diff < 172800000) {
    return '昨天'
  } else {
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  }
}

function getScoreClass(score) {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  return 'needs-work'
}

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.stats-view {
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

.stats-container {
  padding: 40px 20px;
}

.stats-container h1 {
  font-size: 32px;
  margin-bottom: 32px;
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: 60px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  text-align: center;
  padding: 32px 24px;
}

.stat-icon {
  font-size: 40px;
  margin-bottom: 16px;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}

.stat-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

.level-progress-card {
  position: relative;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  margin: 12px 0 8px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.progress-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.level-info {
  margin-bottom: 32px;
}

.level-info h2 {
  font-size: 20px;
  margin-bottom: 20px;
}

.level-descriptions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.level-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  opacity: 0.5;
  transition: all 0.3s;
}

.level-item.active {
  opacity: 1;
  background: rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.level-num {
  font-weight: 600;
  color: #667eea;
  min-width: 60px;
}

.level-desc {
  color: rgba(255, 255, 255, 0.8);
}

.recent-practices h2 {
  font-size: 20px;
  margin-bottom: 20px;
}

.no-data {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  padding: 40px;
}

.practice-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.practice-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.practice-date {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.practice-info {
  display: flex;
  gap: 16px;
  align-items: center;
}

.practice-level {
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
}

.practice-score {
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 12px;
}

.practice-score.excellent {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.practice-score.good {
  background: rgba(234, 179, 8, 0.2);
  color: #eab308;
}

.practice-score.needs-work {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.practice-accuracy {
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}
</style>
