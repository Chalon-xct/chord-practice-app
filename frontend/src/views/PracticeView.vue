<template>
  <div class="practice-view">
    <nav class="navbar">
      <div class="navbar-left">
        <div class="logo">🎸 和弦练习</div>
        <div class="level-display">
          <span class="level-badge">Lv.{{ userLevel }}</span>
          <div class="mini-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: (levelProgress * 100) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
      <div class="nav-links">
        <router-link to="/stats">统计</router-link>
        <router-link to="/history">历史记录</router-link>
        <button @click="handleLogout" class="btn btn-secondary">退出</button>
      </div>
    </nav>

    <div class="practice-container">
      <template v-if="loadingPractice">
        <div class="loading-screen card">
          <div class="loading-icon">🎵</div>
          <h2>正在生成练习...</h2>
          <p>AI 正在为你定制今日的和弦练习内容</p>
          <div class="loading-spinner"></div>
        </div>
      </template>
      
      <template v-else-if="!practiceStarted">
        <div class="start-screen card">
          <h2>今日练习</h2>
          
          <div v-if="practiceInfo" class="practice-info">
            <div class="info-item">
              <span class="label">练习重点</span>
              <span class="value">{{ practiceInfo.focus_area }}</span>
            </div>
            <div class="info-item">
              <span class="label">建议</span>
              <span class="value">{{ practiceInfo.tips }}</span>
            </div>
          </div>
          
          <p class="practice-desc">
            每次练习约 1 分钟，包含看构成音猜和弦和听单音辨音两种题型
          </p>
          
          <button @click="startPractice" class="btn btn-primary btn-large" :disabled="loading">
            <span v-if="loading" class="loading"></span>
            <span v-else>开始练习</span>
          </button>
        </div>
      </template>

      <template v-else-if="submittingPractice">
        <div class="loading-screen card">
          <div class="loading-icon">📊</div>
          <h2>正在分析结果...</h2>
          <p>AI 正在生成你的练习报告和下次练习计划</p>
          <div class="loading-spinner"></div>
        </div>
      </template>
      
      <template v-else-if="!practiceFinished">
        <div class="question-card card">
          <div class="question-header">
            <span class="question-type">
              {{ currentQuestion.type === 'chord' ? '🎸 看构成音猜和弦' : '🎵 听单音辨音' }}
            </span>
            <span class="question-progress">{{ currentQuestionIndex + 1 }} / {{ questions.length }}</span>
          </div>

          <div v-if="currentQuestion.type === 'chord'" class="chord-question">
            <p class="question-text">以下音符构成什么和弦？</p>
            
            <div class="notes-display">
              <div v-for="note in currentQuestion.notes" :key="note" class="note-chip">
                {{ note }}
              </div>
            </div>
            
            <div class="chord-options">
              <button 
                v-for="option in currentQuestion.options" 
                :key="option"
                @click="selectAnswer(option)"
                class="option-button"
                :class="{ selected: selectedAnswer === option }"
                :disabled="submittingPractice"
              >
                {{ option }}
              </button>
            </div>
          </div>

          <div v-else class="note-question">
            <p class="question-text">听音频，这是什么音？（标准音 A=442Hz）</p>
            
            <button @click="playCurrentNote" class="play-button" :disabled="submittingPractice">
              <span class="play-icon">▶</span>
              播放音频
            </button>
            
            <div class="note-selection">
              <button
                v-for="note in allNotes"
                :key="note"
                @click="selectAnswer(note)"
                class="note-button"
                :class="{ selected: selectedAnswer === note }"
                :disabled="submittingPractice"
              >
                {{ note }}
              </button>
            </div>
          </div>

          <div class="question-actions">
            <button 
              v-if="!showAnswer" 
              @click="submitAnswer" 
              class="btn btn-primary"
              :disabled="!canSubmit || submittingPractice"
            >
              提交答案
            </button>
            
            <button 
              v-else 
              @click="nextQuestion" 
              class="btn btn-primary"
              :disabled="submittingPractice"
            >
              {{ currentQuestionIndex < questions.length - 1 ? '下一题' : '查看结果' }}
            </button>
          </div>

          <div v-if="showAnswer" class="answer-feedback" :class="isCorrect ? 'correct' : 'wrong'">
            <span class="feedback-icon">{{ isCorrect ? '✓' : '✗' }}</span>
            <span class="feedback-text">
              {{ isCorrect ? '回答正确！' : `正确答案：${currentQuestion.answer}` }}
            </span>
          </div>
        </div>
      </template>

      <template v-else>
        <ResultView 
          :result="practiceResult" 
          @close="finishPractice"
        />
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import ResultView from '../components/ResultView.vue'

const router = useRouter()
const authStore = useAuthStore()

const userLevel = ref(1)
const levelProgress = ref(0)
const practiceStarted = ref(false)
const practiceFinished = ref(false)
const loading = ref(false)
const loadingPractice = ref(false)
const submittingPractice = ref(false)
const practiceInfo = ref(null)
const chords = ref([])
const questions = ref([])
const currentQuestionIndex = ref(0)
const selectedAnswer = ref(null)
const showAnswer = ref(false)
const answers = ref([])
const practiceStartTime = ref(null)
const practiceResult = ref(null)

const allNotes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

const NOTE_FREQUENCIES_442 = {
  'C': 263.07, 'C#': 278.74, 'D': 295.21, 'D#': 312.70,
  'E': 331.17, 'F': 350.62, 'F#': 371.25, 'G': 393.08,
  'G#': 416.00, 'A': 442.00, 'A#': 469.85, 'B': 498.79
}

const currentQuestion = computed(() => questions.value[currentQuestionIndex.value])

const canSubmit = computed(() => {
  return selectedAnswer.value !== null
})

const isCorrect = computed(() => {
  return selectedAnswer.value === currentQuestion.value.answer
})

onMounted(async () => {
  if (authStore.user) {
    userLevel.value = authStore.user.current_level
    levelProgress.value = authStore.user.level_progress || 0
  }
  
  try {
    const statsRes = await axios.get('/api/user/stats')
    userLevel.value = statsRes.data.current_level
    levelProgress.value = statsRes.data.level_progress || 0
  } catch (err) {
    console.error('加载等级失败:', err)
  }
})

async function startPractice() {
  loadingPractice.value = true
  
  try {
    const response = await axios.post('/api/practice/start')
    chords.value = response.data.chords
    practiceInfo.value = {
      focus_area: response.data.focus_area,
      tips: response.data.tips
    }
    
    generateQuestions(response.data.chords)
    practiceStarted.value = true
    practiceStartTime.value = Date.now()
  } catch (err) {
    alert('加载练习失败：' + (err.response?.data?.error || err.message))
    loadingPractice.value = false
  }
}

function generateQuestions(chordList) {
  questions.value = []
  
  chordList.forEach((chord) => {
    questions.value.push({
      type: 'chord',
      chordName: chord.name,
      notes: chord.notes,
      options: generateOptions(chord.name, chordList.map(c => c.name)),
      answer: chord.name
    })
  })
  
  const singleNotes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
  singleNotes.forEach((note) => {
    questions.value.push({
      type: 'note',
      noteName: note,
      midi: generateSingleNoteMidi(note),
      answer: note
    })
  })
  
  questions.value.sort(() => Math.random() - 0.5)
}

function generateOptions(correct, allChords) {
  const options = [correct]
  const others = allChords.filter(c => c !== correct)
  
  while (options.length < 4 && others.length > 0) {
    const randomIndex = Math.floor(Math.random() * others.length)
    options.push(others[randomIndex])
    others.splice(randomIndex, 1)
  }
  
  return options.sort(() => Math.random() - 0.5)
}

function generateSingleNoteMidi(noteName) {
  const audioContext = new (window.AudioContext || window.webkitAudioContext)()
  const frequency = NOTE_FREQUENCIES_442[noteName] || 442
  
  const oscillator = audioContext.createOscillator()
  const gainNode = audioContext.createGain()
  
  oscillator.type = 'sine'
  oscillator.frequency.value = frequency
  
  gainNode.gain.setValueAtTime(0.5, audioContext.currentTime)
  gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 1.5)
  
  oscillator.connect(gainNode)
  gainNode.connect(audioContext.destination)
  
  oscillator.start(audioContext.currentTime)
  oscillator.stop(audioContext.currentTime + 1.5)
  
  return { frequency, context: audioContext }
}

function playCurrentNote() {
  if (currentQuestion.value.midi) {
    const { frequency } = currentQuestion.value.midi
    playTone(frequency)
  }
}

function playTone(frequency) {
  const audioContext = new (window.AudioContext || window.webkitAudioContext)()
  const oscillator = audioContext.createOscillator()
  const gainNode = audioContext.createGain()
  
  oscillator.type = 'sine'
  oscillator.frequency.value = frequency
  
  gainNode.gain.setValueAtTime(0.5, audioContext.currentTime)
  gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 1.5)
  
  oscillator.connect(gainNode)
  gainNode.connect(audioContext.destination)
  
  oscillator.start(audioContext.currentTime)
  oscillator.stop(audioContext.currentTime + 1.5)
}

function selectAnswer(option) {
  selectedAnswer.value = option
}

function submitAnswer() {
  showAnswer.value = true
  
  answers.value.push({
    chord: currentQuestion.value.type === 'chord' ? currentQuestion.value.chordName : currentQuestion.value.noteName,
    questionType: currentQuestion.value.type,
    answer: selectedAnswer.value,
    correct: isCorrect.value
  })
}

function nextQuestion() {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++
    selectedAnswer.value = null
    showAnswer.value = false
  } else {
    finishPracticeSession()
  }
}

async function finishPracticeSession() {
  const duration = Math.floor((Date.now() - practiceStartTime.value) / 1000)
  submittingPractice.value = true
  
  try {
    const response = await axios.post('/api/practice/submit', {
      answers: answers.value,
      duration: duration,
      chords: chords.value.map(c => c.name)
    })
    
    practiceResult.value = response.data
    levelProgress.value = response.data.level_progress || 0
    userLevel.value = response.data.level_updated
    
    if (authStore.user) {
      authStore.user.current_level = response.data.level_updated
      authStore.user.level_progress = response.data.level_progress || 0
      localStorage.setItem('user', JSON.stringify(authStore.user))
    }
    
    practiceFinished.value = true
  } catch (err) {
    alert('提交练习失败：' + (err.response?.data?.error || err.message))
    submittingPractice.value = false
  }
}

function finishPractice() {
  router.push('/stats')
}

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.practice-view {
  min-height: 100vh;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.level-display {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mini-progress .progress-bar {
  width: 100px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.mini-progress .progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
  transition: width 0.5s ease;
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

.level-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.practice-container {
  max-width: 700px;
  margin: 0 auto;
  padding: 40px 20px;
}

.loading-screen {
  text-align: center;
  padding: 80px 40px;
}

.loading-icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.loading-screen h2 {
  font-size: 28px;
  margin-bottom: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.loading-screen p {
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 32px;
  font-size: 16px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  margin: 0 auto;
  border: 4px solid rgba(102, 126, 234, 0.2);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.start-screen {
  text-align: center;
  padding: 60px 40px;
}

.start-screen h2 {
  font-size: 32px;
  margin-bottom: 32px;
}

.practice-info {
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
  text-align: left;
}

.info-item {
  margin-bottom: 16px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item .label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  display: block;
  margin-bottom: 4px;
}

.info-item .value {
  color: white;
  font-size: 16px;
}

.practice-desc {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 32px;
  line-height: 1.6;
}

.btn-large {
  padding: 16px 64px;
  font-size: 18px;
}

.question-card {
  padding: 32px;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.question-type {
  font-size: 18px;
  font-weight: 600;
}

.question-progress {
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}

.question-text {
  font-size: 20px;
  text-align: center;
  margin-bottom: 32px;
  color: rgba(255, 255, 255, 0.9);
}

.notes-display {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 32px;
}

.note-chip {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  font-size: 20px;
  font-weight: 600;
}

.chord-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.option-button {
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: white;
  font-size: 24px;
  font-weight: 600;
  transition: all 0.2s;
}

.option-button:hover {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.option-button.selected {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.2);
}

.option-button:disabled,
.note-button:disabled,
.play-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.play-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  width: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 32px;
  transition: transform 0.2s;
}

.play-button:hover {
  transform: scale(1.02);
}

.play-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.note-selection {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
}

.note-button {
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.2s;
}

.note-button:hover {
  border-color: #667eea;
}

.note-button.selected {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.2);
}

.question-actions {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

.question-actions .btn {
  padding: 14px 48px;
}

.question-actions .btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.answer-feedback {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  margin-top: 24px;
  font-weight: 600;
}

.answer-feedback.correct {
  background: rgba(34, 197, 94, 0.2);
  border: 1px solid rgba(34, 197, 94, 0.5);
  color: #86efac;
}

.answer-feedback.wrong {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.5);
  color: #fca5a5;
}

.feedback-icon {
  font-size: 24px;
}
</style>
