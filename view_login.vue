<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <h2 class="login-title">📝 考试系统</h2>
        <p class="login-subtitle">请登录后参与考试</p>
      </div>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username" class="form-label">用户名</label>
          <div class="input-wrapper">
            <i class="icon-user">👤</i>
            <input
              type="text"
              id="username"
              v-model="loginForm.username"
              required
              placeholder="请输入用户名"
              class="form-input"
              @focus="inputFocus('username')"
              @blur="inputBlur('username')"
            />
          </div>
        </div>
        <div class="form-group">
          <label for="password" class="form-label">密码</label>
          <div class="input-wrapper">
            <i class="icon-lock">🔒</i>
            <input
                type="password"
                id="password"
                v-model="loginForm.password"
                required
                placeholder="请输入密码"
                class="form-input"
                @focus="inputFocus('password')"
                @blur="inputBlur('password')"
            />
          </div>
        </div>
        <p class="error-message" v-if="errorMsg" :class="{ fadeIn: errorMsg }">{{ errorMsg }}</p>
        <button type="submit" class="login-btn" :disabled="isSubmitting">
          <span v-if="isSubmitting">登录中...</span>
          <span v-else>立即登录</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import {ref} from "vue";
import {useRouter} from "vue-router";
import {userLogin} from "../api/auth";
import {useCookies} from 'vue3-cookies';

const router = useRouter();
const {cookies} = useCookies();
const loginForm = ref({username: '', password: ''});
const errorMsg = ref('');
const isSubmitting = ref(false); // 提交状态
const focusField = ref(''); // 聚焦的输入框

// 输入框聚焦/失焦处理
const inputFocus = (field) => focusField.value = field;
const inputBlur = () => focusField.value = '';

const handleLogin = async () => {
  try {
    errorMsg.value = '';
    isSubmitting.value = true;
    const res = await userLogin(loginForm.value);
    console.log('后端返回的 Token:', res.token);

    // 存储 Token
    cookies.set('user_token', res.token, '1d');
    localStorage.setItem('user_info', JSON.stringify({
      userId: res.user_id,
      email: res.email
    }));

    // 处理回跳
    const redirectPath = router.currentRoute.value.query.redirect || '/exams';
    await router.push(redirectPath);
    setTimeout(() => alert('登录成功！'), 100);
  } catch (error) {
    errorMsg.value = '用户名或密码错误，请重试';
    console.error('登录失败:', error);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* 页面背景 */
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

/* 登录卡片 */
.login-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2);
  backdrop-filter: blur(4px);
  padding: 30px 40px;
  transition: transform 0.3s ease;
}

.login-card:hover {
  transform: translateY(-5px);
}

/* 头部标题 */
.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-title {
  font-size: 24px;
  color: #2d3748;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.login-subtitle {
  font-size: 14px;
  color: #718096;
}

/* 表单样式 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  color: #4a5568;
  font-weight: 500;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.icon-user, .icon-lock {
  position: absolute;
  left: 12px;
  color: #718096;
  font-size: 16px;
}

.form-input {
  width: 100%;
  padding: 14px 16px 14px 40px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  outline: none;
}

/* 输入框聚焦状态 */
.form-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input:focus-within {
  border-color: #667eea;
}

/* 错误提示 */
.error-message {
  color: #e53e3e;
  font-size: 13px;
  text-align: center;
  height: 16px;
  transition: opacity 0.3s ease;
}

.fadeIn {
  animation: fadeIn 0.3s ease forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 登录按钮 */
.login-btn {
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  opacity: 0.9;
}

.login-btn:hover {
  opacity: 1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.login-btn:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 响应式调整 */
@media (max-width: 480px) {
  .login-card {
    padding: 25px 20px;
  }

  .form-input {
    padding: 12px 14px 12px 36px;
    font-size: 15px;
  }

  .login-btn {
    padding: 12px;
    font-size: 15px;
  }
}
</style>
