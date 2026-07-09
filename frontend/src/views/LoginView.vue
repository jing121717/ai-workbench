<template>
  <div class="login-page">
    <div class="bg-grid"></div>
    <div class="bg-glow"></div>
    <div class="bg-particles">
      <div v-for="i in 30" :key="i" class="particle" :style="particleStyle(i)"></div>
    </div>

    <div class="login-container">
      <div class="brand-section">
        <div class="brand-content">
          <div class="brand-logo glow-border">
            <svg width="72" height="72" viewBox="0 0 72 72" fill="none">
              <rect width="72" height="72" rx="20" fill="url(#lg2)"/>
              <path d="M18 36l12 12 24-24" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
              <defs>
                <linearGradient id="lg2" x1="0" y1="0" x2="72" y2="72">
                  <stop stop-color="#4d8ef8"/><stop offset="1" stop-color="#22d3ee"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 class="brand-title">AI Workbench</h1>
          <p class="brand-subtitle">全栈 AI 智能代码工作台</p>
          <div class="brand-divider"></div>
          <div class="brand-features">
            <div class="feature-item" v-for="f in features" :key="f.label">
              <el-icon :color="f.color"><component :is="f.icon" /></el-icon>
              <span>{{ f.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="form-section">
        <div class="form-card tech-card">
          <div class="form-header">
            <div class="form-icon">
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                <rect width="40" height="40" rx="12" fill="url(#fi)"/>
                <path d="M12 20l6 6 10-10" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                <defs>
                  <linearGradient id="fi" x1="0" y1="0" x2="40" y2="40">
                    <stop stop-color="#4d8ef8"/><stop offset="1" stop-color="#22d3ee"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <div>
              <h2>欢迎回来</h2>
              <p>登录您的 AI 代码工作台</p>
            </div>
          </div>

          <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="login-form">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="form.username" placeholder="请输入用户名" size="large" prefix-icon="User"/>
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large"
                prefix-icon="Lock" show-password @keyup.enter="handleLogin"/>
            </el-form-item>
          </el-form>

          <button class="login-btn" :class="{ loading: logging }" @click="handleLogin" :disabled="logging">
            <span v-if="!logging">
              <el-icon style="margin-right:6px"><Promotion /></el-icon>
              登 录
            </span>
            <span v-else class="loading-dots">登录中<span>.</span><span>.</span><span>.</span></span>
          </button>

          <div class="form-divider">
            <span>默认账号</span>
          </div>
          <div class="default-account">
            <span>admin</span><span class="sep">/</span><span>Admin@123456</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const logging = ref(false)
const formRef = ref()
const form = reactive({ username: 'admin', password: 'Admin@123456' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const features = [
  { icon: 'Cpu', color: '#4d8ef8', label: 'LangChain + Qwen 大模型 RAG' },
  { icon: 'Document', color: '#22d3ee', label: 'Chroma 向量知识库检索' },
  { icon: 'ChatDotRound', color: '#a78bfa', label: 'Web 网页 + 桌面双端互通' },
  { icon: 'Box', color: '#10b981', label: 'Docker 容器化一键部署' },
  { icon: 'Monitor', color: '#fb923c', label: 'Vue3 + PySide6 全栈开发' },
  { icon: 'Connection', color: '#f87171', label: 'Redis 会话缓存与限流' },
]

function particleStyle(i: number) {
  return {
    left: `${(i * 17 + 7) % 100}%`,
    top: `${(i * 23 + 11) % 100}%`,
    animationDelay: `${i * 0.4}s`,
    animationDuration: `${10 + (i % 6)}s`,
    width: `${3 + (i % 4) * 2}px`,
    height: `${3 + (i % 4) * 2}px`,
  }
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  logging.value = true
  try {
    await auth.login(form.username, form.password)
    ElMessage.success('登录成功，欢迎使用 AI 工作台')
    router.push('/chat')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '登录失败，请检查账号密码')
  } finally {
    logging.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: var(--bg-primary); position: relative; overflow: hidden;
}
.bg-grid { position: absolute; inset: 0; z-index: 0; }
.bg-glow {
  position: absolute; top: -200px; left: 50%; transform: translateX(-50%);
  width: 600px; height: 600px;
  background: radial-gradient(ellipse, rgba(77,142,248,.12) 0%, transparent 70%);
  pointer-events: none;
}
.bg-particles { position: absolute; inset: 0; pointer-events: none; z-index: 1; }
.particle {
  position: absolute; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
  opacity: .2; animation: float linear infinite;
}

.login-container {
  display: flex; width: 940px; max-width: 95vw;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl); overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,.7), 0 0 80px rgba(77,142,248,.08);
  position: relative; z-index: 2;
}

.brand-section {
  width: 400px; flex-shrink: 0;
  background: linear-gradient(160deg, rgba(77,142,248,.08) 0%, rgba(34,211,238,.04) 100%);
  border-right: 1px solid var(--border-color);
  display: flex; align-items: center; justify-content: center; padding: 48px 40px;
}
.brand-content { text-align: center; }
.brand-logo { margin-bottom: 20px; display: inline-block; border-radius: 20px; padding: 4px; }
.brand-title { font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; }
.brand-subtitle { color: var(--text-secondary); font-size: .88rem; margin-bottom: 24px; }
.brand-divider { width: 60px; height: 2px; background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan)); margin: 0 auto 24px; border-radius: 2px; }
.brand-features { display: flex; flex-direction: column; gap: 12px; text-align: left; }
.feature-item { display: flex; align-items: center; gap: 10px; color: var(--text-secondary); font-size: .82rem; }

.form-section { flex: 1; padding: 48px 40px; display: flex; align-items: center; justify-content: center; }
.form-card { width: 100%; max-width: 360px; padding: 8px; }
.form-header { display: flex; align-items: center; gap: 14px; margin-bottom: 32px; }
.form-icon { flex-shrink: 0; }
.form-header h2 { font-size: 1.4rem; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.form-header p { color: var(--text-muted); font-size: .82rem; }

.login-form :deep(.el-form-item__label) { color: var(--text-secondary) !important; font-size: .78rem !important; padding-bottom: 6px !important; }
.login-form :deep(.el-input__prefix) { color: var(--text-muted) !important; }

.login-btn {
  width: 100%; height: 48px; margin-top: 8px;
  background: linear-gradient(135deg, var(--accent-blue), #3b82f6);
  border: none; border-radius: var(--radius-sm);
  color: #fff; font-size: 1rem; font-weight: 600; letter-spacing: 2px;
  cursor: pointer; transition: all .3s;
  box-shadow: 0 4px 20px rgba(77,142,248,.4);
  display: flex; align-items: center; justify-content: center;
}
.login-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 6px 28px rgba(77,142,248,.55); }
.login-btn:disabled { opacity: .7; cursor: not-allowed; }

.loading-dots span { animation: blink 1.4s infinite; }
.loading-dots span:nth-child(2) { animation-delay: .2s; }
.loading-dots span:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 0%,80%,100% { opacity: 0; } 40% { opacity: 1; } }

.form-divider { display: flex; align-items: center; margin: 20px 0 12px; gap: 12px; }
.form-divider::before, .form-divider::after { content: ''; flex: 1; height: 1px; background: var(--border-color); }
.form-divider span { font-size: .72rem; color: var(--text-muted); white-space: nowrap; }
.default-account { display: flex; align-items: center; justify-content: center; gap: 6px; background: var(--bg-tertiary); border-radius: var(--radius-sm); padding: 8px 16px; font-size: .78rem; color: var(--text-secondary); }
.default-account .sep { color: var(--text-muted); }
</style>
