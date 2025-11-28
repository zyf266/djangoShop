<template>
  <div class="exam-taking-page">
    <!-- 顶部导航栏 -->
    <div class="exam-header">
      <div class="header-left">
        <h1 class="exam-title">{{ exam.title }}</h1>
      </div>
      <div class="header-right">
        <div class="timer" :class="{ warning: timeRemaining <= 10, danger: timeRemaining <= 5 }">
          ⏰ 剩余时间：{{ timeRemaining }} 分钟
        </div>
      </div>
    </div>

    <!-- 考试容器 -->
    <div class="exam-container">
      <!-- 题目区域 -->
      <div class="questions-wrapper">
        <form @submit.prevent="submitAnswers" class="questions-form">
          <div
            class="question-card"
            v-for="(answer, index) in answerRecords"
            :key="answer.question.id"
            :class="{ active: currentQuestion === index }"
          >
            <div class="question-header">
              <span class="question-number">第 {{ index + 1 }} 题</span>
              <span class="question-score">{{ answer.question.score }} 分</span>
            </div>
            <h3 class="question-content">{{ answer.question.content }}</h3>

            <!-- 单选题 -->
            <div class="options" v-if="answer.question.question_type === 'single'">
              <div
                class="option-item"
                v-for="(option, key) in answer.question.options"
                :key="key"
              >
                <input
                  type="radio"
                  :id="`q${answer.question.id}_${key}`"
                  :name="`question_${answer.question.id}`"
                  :value="key"
                  v-model="answer.user_answer"
                  class="option-input"
                >
                <label :for="`q${answer.question.id}_${key}`" class="option-label">
                  <span class="option-letter">{{ key }}</span>. {{ option }}
                </label>
              </div>
            </div>

            <!-- 多选题 -->
            <div class="options" v-if="answer.question.question_type === 'multiple'">
              <div
                class="option-item"
                v-for="(option, key) in answer.question.options"
                :key="key"
              >
                <input
                  type="checkbox"
                  :id="`q${answer.question.id}_${key}`"
                  :name="`question_${answer.question.id}`"
                  :value="key"
                  @change="handleMultipleChoice(answer, key)"
                  class="option-input"
                  :checked="answer.user_answer?.split(',').includes(String(key))"
                >
                <label :for="`q${answer.question.id}_${key}`" class="option-label">
                  <span class="option-letter">{{ key }}</span>. {{ option }}
                </label>
              </div>
            </div>

            <!-- 判断题 -->
            <div class="options" v-if="answer.question.question_type === 'judge'">
              <div class="option-item judge-option">
                <input
                  type="radio"
                  id="judge_true"
                  :name="`question_${answer.question.id}`"
                  value="True"
                  v-model="answer.user_answer"
                  class="option-input"
                >
                <label for="judge_true" class="option-label">对</label>
              </div>
              <div class="option-item judge-option">
                <input
                  type="radio"
                  id="judge_false"
                  :name="`question_${answer.question.id}`"
                  value="False"
                  v-model="answer.user_answer"
                  class="option-input"
                >
                <label for="judge_false" class="option-label">错</label>
              </div>
            </div>
          </div>

          <!-- 底部按钮区 -->
          <div class="form-actions">
            <button
              type="button"
              class="btn save-btn"
              @click="saveAnswers"
              :disabled="isSaving"
            >
              <span v-if="isSaving">保存中...</span>
              <span v-else>💾 保存答案</span>
            </button>
            <button
              type="submit"
              class="btn submit-btn"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting">提交中...</span>
              <span v-else>🚀 提交试卷</span>
            </button>
          </div>
        </form>
      </div>

      <!-- 右侧题目导航 -->
      <div class="question-nav">
        <h3 class="nav-title">题目导航</h3>
        <div class="nav-items">
          <button
            class="nav-item"
            v-for="(answer, index) in answerRecords"
            :key="answer.question.id"
            @click="currentQuestion = index"
            :class="{
              answered: answer.user_answer,
              active: currentQuestion === index,
              current: currentQuestion === index
            }"
          >
            {{ index + 1 }}
          </button>
        </div>
        <div class="nav-legend">
          <div class="legend-item">
            <span class="legend-dot unanswered"></span> 未作答
          </div>
          <div class="legend-item">
            <span class="legend-dot answered"></span> 已作答
          </div>
          <div class="legend-item">
            <span class="legend-dot active"></span> 当前题
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getExamRecord, saveAnswers, finishExam } from '../api/exam';

export default {
  name: 'ExamTaking',
  data() {
    return {
      recordId: null,
      exam: {},
      answerRecords: [],
      timeRemaining: 0,
      timer: null,
      record: null,
      currentQuestion: 0, // 当前选中的题目索引
      isSaving: false, // 保存答案状态
      isSubmitting: false // 提交试卷状态
    };
  },
  created() {
    this.recordId = this.parseRecordId();
    if (this.recordId) {
      this.fetchRecord();
    } else {
      console.error('无法解析recordId');
      alert('获取考试信息失败，无法识别考试ID');
    }
  },
  destroyed() {
    clearInterval(this.timer);
  },
  methods: {
    parseRecordId() {
      let id = this.$route.params.id;
      if (typeof id === 'object' && id !== null) {
        id = id.id || id.recordId || JSON.stringify(id);
      }
      if (typeof id === 'string' && (id.startsWith('{') || id.includes('[object Object]'))) {
        try {
          const parsed = JSON.parse(id);
          return parsed.id || parsed.recordId || id;
        } catch (e) {
          console.warn('无法解析recordId字符串:', id);
          return id;
        }
      }
      return id;
    },

    async fetchRecord() {
      try {
        const res = await getExamRecord(this.recordId);
        if (!res || !res.exam || !res.exam.questions) {
          throw new Error('考试数据格式不正确');
        }
        this.record = res;
        this.exam = res.exam;
        this.answerRecords = res.answer_records || []; // 直接使用后端返回的答题记录
        console.log("后端返回的答题记录：", this.answerRecords); // 确认结构
        this.calculateTimeRemaining();
        this.startTimer();
      } catch (error) {
        console.error('获取考试记录失败:', error);
        alert('获取考试信息失败，请刷新页面重试');
      }
    },

    calculateTimeRemaining() {
      if (!this.record || !this.record.start_time || !this.exam.time_limit) {
        this.timeRemaining = 60;
        return;
      }
      try {
        const now = new Date();
        const startTime = new Date(this.record.start_time);
        if (isNaN(startTime.getTime())) {
          throw new Error('无效的开始时间格式');
        }
        const timeUsed = Math.floor((now - startTime) / 60000);
        this.timeRemaining = Math.max(0, this.exam.time_limit - timeUsed);
      } catch (error) {
        console.error('计算剩余时间失败:', error);
        this.timeRemaining = this.exam.time_limit || 60;
      }
    },

    startTimer() {
      if (this.timer) clearInterval(this.timer);
      this.timer = setInterval(() => {
        this.timeRemaining--;
        if (this.timeRemaining <= 0) {
          clearInterval(this.timer);
          this.submitAnswers(); // 时间到自动提交
        }
      }, 60000);
    },

    handleMultipleChoice(answer, key) {
      const stringKey = String(key);
      let answers = answer.user_answer ? answer.user_answer.split(',') : [];
      if (answers.includes(stringKey)) {
        answers = answers.filter(item => item !== stringKey);
      } else {
        answers.push(stringKey);
      }
      answer.user_answer = answers.join(',');
    },

async saveAnswers() {
  try {
    this.isSaving = true;
    console.log('原始 answerRecords:', this.answerRecords); // 看初始值
    const answers = this.answerRecords.map(ans => ({
      question_id: ans.question.id,
      user_answer: ans.user_answer || ''
    }));
    console.log('最终提交的 answers:', answers); // 重点看 user_answer 是 null/"" 还是其他
    await saveAnswers(String(this.recordId), {answers});
    alert('答案已成功保存！');
  } catch (error) {
    console.error('保存答案失败:', error);
    // 打印完整的错误响应（含服务器具体提示）
    console.log('服务器响应详情:', error.response?.data);
    console.log('响应状态码:', error.response?.status);
    alert(`保存答案失败: ${error.response?.data?.detail || error.message}`);
  } finally {
    this.isSaving = false;
  }
},

    async submitAnswers() {
      if (window.confirm('确定要提交试卷吗？提交后无法修改答案！')) {
        try {
          this.isSubmitting = true;
          await this.saveAnswers();
          await this.finishExam();
          this.$router.push(`/result/${this.recordId}/`);
        } catch (error) {
          console.error('提交过程失败:', error);
          alert('提交试卷失败，请重试');
        } finally {
          this.isSubmitting = false;
        }
      }
    },

    async finishExam() {
      try {
        await finishExam(String(this.recordId));
        console.log('考试提交成功');
      } catch (error) {
        console.error('提交考试失败:', error.response || error);
        throw new Error('提交考试失败: ' + (error.response?.data?.message || error.message));
      }
    }
  }
};
</script>

<style scoped>
/* 页面容器 */
.exam-taking-page {
  background-color: #f8f9fa;
  min-height: 100vh;
  padding: 20px;
}

/* 顶部导航 */
.exam-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 15px 30px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 25px;
}

.exam-title {
  font-size: 22px;
  color: #2d3748;
  font-weight: 600;
}

.timer {
  font-size: 16px;
  font-weight: 600;
  color: #4a5568;
  padding: 8px 16px;
  border-radius: 8px;
  background: #f5f5f5;
}

.timer.warning {
  color: #ed8936;
  background: #fef7fb;
}

.timer.danger {
  color: #e53e3e;
  background: #fef2f2;
}

/* 考试容器 */
.exam-container {
  display: flex;
  gap: 25px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 题目区域 */
.questions-wrapper {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 30px;
  max-height: calc(100vh - 180px);
  overflow-y: auto;
}

.questions-form {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* 题目卡片 */
.question-card {
  padding: 25px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.question-card.active {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.question-number {
  font-size: 14px;
  color: #718096;
  font-weight: 500;
}

.question-score {
  font-size: 13px;
  color: #4299e1;
  background: #e8f4f8;
  padding: 3px 8px;
  border-radius: 4px;
}

.question-content {
  font-size: 16px;
  color: #2d3748;
  margin-bottom: 20px;
  line-height: 1.6;
}

/* 选项样式 */
.options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  border-radius: 8px;
  transition: background 0.2s ease;
}

.option-item:hover {
  background: #f8f9fa;
}

.option-input {
  width: 18px;
  height: 18px;
  accent-color: #667eea;
  cursor: pointer;
}

.option-label {
  font-size: 15px;
  color: #4a5568;
  cursor: pointer;
  flex: 1;
  line-height: 1.5;
}

.option-letter {
  display: inline-block;
  width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  background: #f5f5f5;
  border-radius: 50%;
  margin-right: 8px;
  color: #718096;
  font-size: 12px;
}

/* 判断题样式 */
.judge-option {
  display: inline-flex;
  margin-right: 30px;
}

/* 按钮区 */
.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 20px;
  justify-content: center;
}

.btn {
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
}

.save-btn {
  background: #e8f4f8;
  color: #4299e1;
}

.save-btn:hover {
  background: #d1e7dd;
  color: #2b6cb0;
}

.submit-btn {
  background: #667eea;
  color: #fff;
}

.submit-btn:hover {
  background: #5a67d8;
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2);
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 右侧题目导航 */
.question-nav {
  width: 280px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 20px;
  height: fit-content;
}

.nav-title {
  font-size: 16px;
  color: #2d3748;
  font-weight: 600;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.nav-items {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.nav-item {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  background: #fff;
  color: #4a5568;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-item:hover {
  border-color: #667eea;
  color: #667eea;
}

.nav-item.answered {
  background: #e8f4f8;
  border-color: #4299e1;
  color: #2b6cb0;
}

.nav-item.active {
  background: #667eea;
  border-color: #667eea;
  color: #fff;
}

.nav-item.current {
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3);
}

/* 导航图例 */
.nav-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 12px;
  color: #718096;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.legend-dot.unanswered {
  background: #e2e8f0;
}

.legend-dot.answered {
  background: #4299e1;
}

.legend-dot.active {
  background: #667eea;
}

/* 响应式调整 */
@media (max-width: 1024px) {
  .exam-container {
    flex-direction: column;
  }

  .question-nav {
    width: 100%;
  }

  .questions-wrapper {
    max-height: none;
  }
}

@media (max-width: 768px) {
  .exam-header {
    padding: 12px 20px;
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }

  .question-card {
    padding: 20px;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
