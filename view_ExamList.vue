<template>
  <div class="exam-list-page">
    <div class="page-header">
      <h1 class="page-title">📚 考试列表</h1>
      <p class="page-desc">选择下方考试开始作答</p>
    </div>

    <!-- 加载状态 -->
    <div class="loading" v-if="isLoading">
      <div class="spinner"></div>
      <p>加载考试列表中...</p>
    </div>

    <!-- 考试卡片容器 -->
    <div class="exam-cards" v-else>
      <div
        class="exam-card"
        v-for="exam in exams"
        :key="exam.id"
        @mouseenter="cardHover(exam.id, true)"
        @mouseleave="cardHover(exam.id, false)"
        :class="{ hover: hoveredCards[exam.id] }"
      >
        <div class="exam-card-header">
          <h3 class="exam-title">{{ exam.title }}</h3>
          <span class="exam-tag">{{ exam.total_score }} 分</span>
        </div>
        <div class="exam-card-body">
          <p class="exam-desc">{{ exam.description || '无考试描述' }}</p>
          <div class="exam-meta">
            <span class="meta-item">⏱️ {{ exam.time_limit }} 分钟</span>
            <span class="meta-item">📝 {{ exam.questions?.length || 'N/A' }} 题</span>
          </div>
        </div>
        <button
          class="start-btn"
          @click="goToExam(exam.id)"
          :disabled="isSubmitting"
        >
          <span v-if="submittingExamId === exam.id">进入中...</span>
          <span v-else>开始考试</span>
        </button>
      </div>

      <!-- 空状态 -->
      <div class="empty-state" v-if="exams.length === 0">
        <div class="empty-icon">📭</div>
        <p>暂无可用考试</p>
        <p class="empty-desc">请联系管理员获取考试权限</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getExamList, startExam } from '../api/exam';

const exams = ref([]);
const router = useRouter();
const isLoading = ref(true);
const isSubmitting = ref(false);
const submittingExamId = ref(null);
const hoveredCards = ref({}); // 卡片hover状态

// 卡片hover处理
const cardHover = (examId, isHover) => {
  hoveredCards.value[examId] = isHover;
};

onMounted(() => {
  fetchExams();
});

const fetchExams = async () => {
  try {
    isLoading.value = true;
    const res = await getExamList();
    exams.value = res || [];
    console.log('考试列表数据:', exams.value);
  } catch (error) {
    console.error('获取考试列表失败:', error);
    exams.value = [];
  } finally {
    isLoading.value = false;
  }
};

const goToExam = async (examId) => {
  try {
    isSubmitting.value = true;
    submittingExamId.value = examId;
    const res = await startExam(examId);
    router.push(`/take/${res.id}`);
  } catch (error) {
    console.error('创建考试记录失败:', error);
    alert('进入考试失败，请重试');
  } finally {
    isSubmitting.value = false;
    submittingExamId.value = null;
  }
};
</script>

<style scoped>
/* 页面容器 */
.exam-list-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
  min-height: 100vh;
  background-color: #f8f9fa;
}

/* 页面头部 */
.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-title {
  font-size: 28px;
  color: #2d3748;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.page-desc {
  font-size: 16px;
  color: #718096;
}

/* 加载状态 */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  gap: 15px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 考试卡片容器 */
.exam-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
}

/* 考试卡片 */
.exam-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 25px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.exam-card.hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
}

/* 卡片头部 */
.exam-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.exam-title {
  font-size: 18px;
  color: #2d3748;
  font-weight: 600;
  line-height: 1.4;
}

.exam-tag {
  background: #e8f4f8;
  color: #4299e1;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

/* 卡片内容 */
.exam-card-body {
  margin-bottom: 20px;
}

.exam-desc {
  font-size: 14px;
  color: #4a5568;
  line-height: 1.6;
  margin-bottom: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.exam-meta {
  display: flex;
  gap: 15px;
  font-size: 13px;
  color: #718096;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

/* 开始按钮 */
.start-btn {
  width: 100%;
  padding: 12px;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  opacity: 0.95;
}

.start-btn:hover {
  background: #5a67d8;
  opacity: 1;
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2);
}

.start-btn:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
}

/* 空状态 */
.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: #f8f9fa;
  border-radius: 12px;
  gap: 12px;
}

.empty-icon {
  font-size: 48px;
  color: #cbd5e0;
}

.empty-state p {
  font-size: 16px;
  color: #4a5568;
  font-weight: 500;
}

.empty-desc {
  font-size: 14px;
  color: #718096;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .exam-cards {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }

  .page-title {
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .exam-cards {
    grid-template-columns: 1fr;
  }

  .exam-card {
    padding: 20px;
  }

  .page-header {
    margin-bottom: 30px;
  }
}
</style>
