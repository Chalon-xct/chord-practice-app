<template>
  <div class="result-overlay">
    <div class="result-card card">
      <div class="result-header">
        <h2>练习完成！</h2>
        <button @click="$emit('close')" class="close-btn">×</button>
      </div>

      <div class="score-display">
        <div class="score-circle" :class="scoreClass">
          <span class="score-number">{{ result.score }}</span>
          <span class="score-label">分</span>
        </div>
        <p class="score-text">{{ correct }} / {{ total }} 正确</p>
        
        <div class="exp-gain">
          <span class="exp-icon">✨</span>
          <span class="exp-text">获得 {{ result.exp_gained }} 经验值</span>
        </div>
        
        <div class="level-progress-mini">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: (isNaN(result.level_progress) ? 0 : result.level_progress * 100) + '%' }"></div>
          </div>
          <p class="progress-info">Lv.{{ result.level_updated }} 进度：{{ Math.floor((isNaN(result.level_progress) ? 0 : result.level_progress) * 100) }}%</p>
        </div>
      </div>

      <div class="summary-section">
        <h3>📊 DeepSeek 智能分析</h3>
        
        <div class="summary-content">
          <p class="overall-comment">{{ result.summary.overall_comment }}</p>
          
          <div class="summary-grid">
            <div class="summary-item strengths">
              <h4>✨ 优势</h4>
              <ul>
                <li v-for="(item, i) in result.summary.strengths" :key="i">{{ item }}</li>
              </ul>
            </div>
            
            <div class="summary-item weaknesses">
              <h4>🎯 需加强</h4>
              <ul>
                <li v-for="(item, i) in result.summary.weaknesses" :key="i">{{ item }}</li>
              </ul>
            </div>
          </div>
          
          <div class="suggestions">
            <h4>💡 建议</h4>
            <ul>
              <li v-for="(item, i) in result.summary.suggestions" :key="i">{{ item }}</li>
            </ul>
          </div>
          
          <p class="encouragement">{{ result.summary.encouragement }}</p>
        </div>
      </div>

      <div class="next-plan-section">
        <h3>📅 下次练习计划</h3>
        <div class="plan-content">
          <p><strong>建议级别：</strong>第{{ result.next_plan.suggested_level }}级</p>
          <p><strong>重点和弦：</strong>{{ result.next_plan.focus_chords.join('、') }}</p>
          <p><strong>练习目标：</strong></p>
          <ul>
            <li v-for="(goal, i) in result.next_plan.practice_goals" :key="i">{{ goal }}</li>
          </ul>
          <p class="plan-message">{{ result.next_plan.message }}</p>
        </div>
      </div>

      <div class="chords-reference-section">
        <h3>🎸 本次练习和弦按法</h3>
        <div class="chords-grid">
          <div v-for="chord in result.chords_reference" :key="chord.name" class="chord-card">
            <h4>{{ chord.name }}</h4>
            <p class="chord-notes">{{ chord.notes.join(' - ') }}</p>
            <div class="chord-positions">
              <div v-for="(pos, i) in chord.positions" :key="i" class="position-item">
                <span class="position-name">{{ pos.name }}</span>
                <div class="fretboard">
                  <div v-for="(fret, stringIndex) in pos.positions" :key="stringIndex" 
                       class="fret" 
                       :class="getFretClass(fret)">
                    {{ getFretDisplay(fret) }}
                  </div>
                </div>
                <span class="difficulty">难度：{{ '⭐'.repeat(pos.difficulty) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="result-actions">
        <router-link to="/practice" class="btn btn-primary">继续练习</router-link>
        <router-link to="/history" class="btn btn-secondary">查看历史</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  result: {
    type: Object,
    required: true
  }
})

defineEmits(['close'])

const { correct, total } = props.result

const scoreClass = computed(() => {
  if (props.result.score >= 80) return 'excellent'
  if (props.result.score >= 60) return 'good'
  return 'needs-work'
})

function getFretClass(fret) {
  if (fret === -1) return 'mute'
  if (fret === 0) return 'open'
  return 'fretted'
}

function getFretDisplay(fret) {
  if (fret === -1) return '×'
  if (fret === 0) return '○'
  return fret
}
</script>

<style scoped>
.result-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  overflow-y: auto;
}

.result-card {
  background: #1a1a2e;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.result-header h2 {
  font-size: 28px;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  font-size: 32px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: white;
}

.score-display {
  text-align: center;
  margin-bottom: 32px;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  border: 4px solid;
}

.score-circle.excellent {
  border-color: #22c55e;
  background: rgba(34, 197, 94, 0.1);
}

.score-circle.good {
  border-color: #eab308;
  background: rgba(234, 179, 8, 0.1);
}

.score-circle.needs-work {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.score-number {
  font-size: 48px;
  font-weight: 700;
}

.score-label {
  font-size: 14px;
  opacity: 0.7;
}

.score-text {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.7);
}

.exp-gain {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px 24px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.exp-icon {
  font-size: 20px;
}

.exp-text {
  font-size: 16px;
  font-weight: 600;
  color: #a5b4fc;
}

.level-progress-mini {
  margin-top: 16px;
}

.level-progress-mini .progress-bar {
  width: 100%;
  height: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  overflow: hidden;
}

.level-progress-mini .progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 5px;
  transition: width 0.5s ease;
}

.progress-info {
  text-align: center;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 8px;
}

.summary-section,
.next-plan-section,
.chords-reference-section {
  margin-bottom: 32px;
}

h3 {
  font-size: 20px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.summary-content {
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  padding: 20px;
}

.overall-comment {
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 20px;
  color: rgba(255, 255, 255, 0.9);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.summary-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 16px;
}

.summary-item h4 {
  font-size: 14px;
  margin-bottom: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.summary-item ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.summary-item li {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  padding: 4px 0;
}

.strengths {
  border-left: 3px solid #22c55e;
}

.weaknesses {
  border-left: 3px solid #f59e0b;
}

.suggestions {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.suggestions h4 {
  font-size: 14px;
  margin-bottom: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.suggestions ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestions li {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  padding: 6px 0;
  padding-left: 20px;
  position: relative;
}

.suggestions li::before {
  content: '→';
  position: absolute;
  left: 0;
  color: #667eea;
}

.encouragement {
  font-style: italic;
  color: #667eea;
  text-align: center;
  padding: 16px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
}

.plan-content {
  background: rgba(34, 197, 94, 0.1);
  border-radius: 12px;
  padding: 20px;
}

.plan-content p {
  margin-bottom: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.plan-content ul {
  list-style: none;
  padding: 0;
  margin: 12px 0;
}

.plan-content li {
  padding: 6px 0;
  padding-left: 20px;
  position: relative;
  color: rgba(255, 255, 255, 0.7);
}

.plan-content li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #22c55e;
}

.plan-message {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(34, 197, 94, 0.3);
  font-style: italic;
  color: #86efac;
}

.chords-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.chord-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
}

.chord-card h4 {
  font-size: 20px;
  margin-bottom: 8px;
  color: #667eea;
}

.chord-notes {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 16px;
}

.position-item {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.position-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.position-name {
  display: block;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 8px;
}

.fretboard {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}

.fret {
  flex: 1;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.fret.mute {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.fret.open {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.fret.fretted {
  background: rgba(102, 126, 234, 0.3);
  color: #667eea;
}

.difficulty {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.result-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 32px;
  padding-top: 32px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.result-actions .btn {
  padding: 14px 32px;
}
</style>
