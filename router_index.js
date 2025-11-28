import { createRouter, createWebHistory } from "vue-router";
import Login from '../views/Login.vue';
import ExamList from "../views/ExamList.vue";
import ExamTaking from "../views/ExamTaking.vue";
import ExamResult from "../views/ExamResult.vue";
// 引入 vue3-cookies（与登录页保持一致）
import { useCookies } from 'vue3-cookies';

// 初始化 cookies（注意：在路由创建前初始化）
const { cookies } = useCookies();

/**
 * 辅助函数：获取有效的用户 Token（只读取 Cookie，因为登录时只存了 Cookie）
 */
const getValidToken = () => {
  // 直接用 vue3-cookies 读取，与登录时的存储方式完全匹配
  return cookies.get('user_token');
};

// 路由规则不变（保持你原来的配置）
const routes = [
  { path: '/', redirect: '/exams', meta: { requiresAuth: true } },
  { path: '/login', component: Login, meta: { requiresAuth: false, title: '登录' } },
  { path: '/exams', component: ExamList, meta: { requiresAuth: true, title: '考试列表' } },
  { path: '/take/:id', component: ExamTaking, meta: { requiresAuth: true, title: '参加考试' } },
  { path: '/result/:id', component: ExamResult, meta: { requiresAuth: true, title: '考试结果' } },
  { path: '/:pathMatch(.*)*', redirect: '/login', meta: { requiresAuth: false } }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// 路由守卫修改（简化 Token 读取逻辑）
router.beforeEach((to, from, next) => {
  // 设置页面标题（不变）
  document.title = to.meta.title ? `${to.meta.title} - 考试系统` : '考试系统';

  if (to.meta.requiresAuth) {
    const token = getValidToken();

    // 开发环境日志
    if (import.meta.env.DEV) {
      console.log('[路由守卫] 目标页面:', to.path);
      console.log('[路由守卫] Cookie 中的 user_token:', token);
    }

    if (token) {
      next();
    } else {
      // 未登录，跳登录页并记录回跳地址
      next({ path: '/login', query: { redirect: to.fullPath } });
    }
  } else {
    next();
  }
});

export default router;
