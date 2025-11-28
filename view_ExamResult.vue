<template>
  <div class="result-page">
    <!-- 顶部结果概览 -->
    <div class="result-header">
      <div class="result-banner">
        <h1 class="exam-title">{{ exam.title }} - 考试结果</h1>
        <div class="score-card" :class="{ pass: record.score >= exam.pass_score, fail: record.score < exam.pass_score }">
          <div class="score-label">最终得分</div>
          <div class="score-value">{{ record.score }}/{{ exam.total_score }}</div>
          <div class="pass-status">
            {{ record.score >= exam.pass_score ? '🎉 考试通过' : '⚠️ 考试未通过' }}
          </div>
        </div>
      </div>

      <!-- 考试信息 -->
      <div class="exam-info">
        <div class="info-item">
          <span class="info-label">开始时间</span>
          <span class="info-value">{{ formatTime(record.start_time) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">结束时间</span>
          <span class="info-value">{{ formatTime(record.end_time) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">考试时长</span>
          <span class="info-value">{{ calculateDuration(record.start_time, record.end_time) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">及格分数</span>
          <span class="info-value">{{ exam.total_score*0.6 }} 分</span>
        </div>
        <div class="info-item">
          <span class="info-label">答题数</span>
          <span class="info-value">{{ answerRecords.length }} 题</span>
        </div>
        <div class="info-item">
          <span class="info-label">正确率</span>
          <span class="info-value">{{ calculateAccuracy() }}%</span>
        </div>
      </div>
    </div>

    <!-- 题目详情 -->
    <div class="questions-result">
      <h2 class="section-title">答题详情</h2>
      <div
        class="question-result-card"
        v-for="answer in answerRecords"
        :key="answer.id"
        :class="{ correct: answer.is_correct, incorrect: !answer.is_correct }"
      >
        <div class="question-header">
          <h3 class="question-content">{{ answer.question.content }}</h3>
          <span class="question-score">{{ answer.question.score }} 分</span>
        </div>
        <div class="answer-details">
          <div class="answer-item">
            <span class="answer-label">你的答案：</span>
            <span class="answer-value">{{ formatAnswer(answer.user_answer, answer.question.question_type) }}</span>
          </div>
          <div class="answer-item">
            <span class="answer-label">正确答案：</span>
            <span class="answer-value">{{ formatAnswer(answer.question.answer, answer.question.question_type) }}</span>
          </div>
          <div class="answer-item">
            <span class="answer-label">作答结果：</span>
            <span class="answer-result">{{ answer.is_correct ? '正确' : '错误' }}</span>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div class="empty-state" v-if="answerRecords.length === 0">
        <div class="empty-icon">📭</div>
        <p>暂无答题记录</p>
      </div>
    </div>

    <!-- 返回按钮 -->
    <div class="back-btn-container">
      <button class="back-btn" @click="goBack">返回考试列表</button>
    </div>
  </div>
</template>

<script>
import { getExamResult } from "../api/exam";
import { format } from 'date-fns'; // 需安装：npm install date-fns

export default {
  name: 'ExamResult',
  data() {
    return {
      recordId: this.$route.params.id,
      record: {},
      exam: {},
      answerRecords: []
    };
  },
  created() {
    this.fetchResult();
  },
  methods: {
    async fetchResult() {
      try {
        const res = await getExamResult(this.recordId);
        this.record = res;
        this.exam = res.exam;
        this.answerRecords = res.answer_records || []; // 直接使用后端返回的答题记录
        console.log("后端返回的答题记录：", this.answerRecords); // 确认结构
        console.log("record",this.record)
        console.log("exam",this.exam)
        console.log("answerRecords",this.answerRecords)
      } catch (error) {
        console.error('获取考试结果失败:', error);
        alert('获取考试结果失败，请刷新页面重试');
      }
    },

    // 格式化时间
    formatTime(timeStr) {
      if (!timeStr) return '无';
      try {
        return format(new Date(timeStr), 'yyyy-MM-dd HH:mm:ss');
      } catch (e) {
        return timeStr;
      }
    },

    // 计算考试时长
    calculateDuration(startTime, endTime) {
      if (!startTime || !endTime) return '无';
      try {
        const start = new Date(startTime);
        const end = new Date(endTime);
        const diffMinutes = Math.floor((end - start) / 60000);
        const hours = Math.floor(diffMinutes / 60);
        const minutes = diffMinutes % 60;
        return hours > 0 ? `${hours}小时${minutes}分钟` : `${minutes}分钟`;
      } catch (e) {
        return '无';
      }
    },

    // 计算正确率
    calculateAccuracy() {
      if (this.answerRecords.length === 0) return 0;
      const correctCount = this.answerRecords.filter(ans => ans.is_correct).length;
      return Math.round((correctCount / this.answerRecords.length) * 100);
    },

    // 格式化答案（处理多选题逗号分隔）
    formatAnswer(answer, questionType) {
      if (!answer) return '未作答';
      if (questionType === 'multiple' && answer.includes(',')) {
        return answer.split(',').join('、');
      }
      if (questionType === 'judge') {
        return answer === 'True' ? '对' : '错';
      }
      return answer;
    },

    // 返回考试列表
    goBack() {
      this.$router.push('/exams');
    }
  }
};
</script>

<style scoped>
/* 页面容器 */
.result-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
  min-height: 100vh;
  background-color: #f8f9fa;
}

/* 结果头部 */
.result-header {
  margin-bottom: 40px;
}

.result-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  margin-bottom: 25px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
}

.exam-title {
  font-size: 26px;
  margin-bottom: 25px;
  font-weight: 600;
}

/* 分数卡片 */
.score-card {
  display: inline-block;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  padding: 25px 40px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.score-label {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.score-value {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 10px;
}

.pass-status {
  font-size: 18px;
  font-weight: 500;
}

.score-card.pass .pass-status {
  color: #c3e6cb;
}

.score-card.fail .pass-status {
  color: #f8d7da;
}

/* 考试信息 */
.exam-info {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  background: #fff;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 13px;
  color: #718096;
  font-weight: 500;
}

.info-value {
  font-size: 15px;
  color: #2d3748;
  font-weight: 600;
}

/* 答题详情 */
.questions-result {
  background: #fff;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
}

.section-title {
  font-size: 20px;
  color: #2d3748;
  margin-bottom: 25px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
  font-weight: 600;
}

/* 题目结果卡片 */
.question-result-card {
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 15px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.question-result-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.03);
}

.question-result-card.correct {
  border-color: #c3e6cb;
  background: #f8f9fa;
}

.question-result-card.incorrect {
  border-color: #f8d7da;
  background: #faf0f5;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.question-content {
  font-size: 16px;
  color: #2d3748;
  line-height: 1.6;
  font-weight: 500;
}

.question-score {
  font-size: 13px;
  padding: 4px 10px;
  border-radius: 20px;
  font-weight: 500;
}

.question-result-card.correct .question-score {
  background: #e8f4f8;
  color: #28a745;
}

.question-result-card.incorrect .question-score {
  background: #fef7fb;
  color: #dc3545;
}

/* 答案详情 */
.answer-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 14px;
}

.answer-item {
  display: flex;
  gap: 8px;
}

.answer-label {
  color: #718096;
  font-weight: 500;
  min-width: 80px;
}

.answer-value {
  color: #4a5568;
  flex: 1;
}

.answer-result {
  font-weight: 600;
}

.question-result-card.correct .answer-result {
  color: #28a745;
}

.question-result-card.incorrect .answer-result {
  color: #dc3545;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 12px;
  color: #718096;
}

.empty-icon {
  font-size: 48px;
}

/* 返回按钮 */
.back-btn-container {
  text-align: center;
  margin-top: 20px;
}

.back-btn {
  padding: 12px 30px;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: #5a67d8;
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .result-banner {
    padding: 30px 20px;
  }

  .exam-title {
    font-size: 22px;
  }

  .score-value {
    font-size: 36px;
  }

  .exam-info {
    grid-template-columns: 1fr 1fr;
    padding: 20px;
  }

  .questions-result {
    padding: 20px;
  }

  .question-content {
    font-size: 15px;
  }
}

@media (max-width: 480px) {
  .exam-info {
    grid-template-columns: 1fr;
  }

  .score-card {
    padding: 20px 30px;
  }

  .answer-item {
    flex-direction: column;
    gap: 4px;
  }

  .answer-label {
    min-width: auto;
  }
}
</style>
