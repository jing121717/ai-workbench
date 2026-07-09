<template>
  <div class="settings-page">
    <header class="page-header">
      <h2 class="page-title"><el-icon color="var(--accent-cyan)"><Setting /></el-icon> 系统设置</h2>
    </header>

    <div class="settings-body">
      <!-- Profile -->
      <section class="settings-section">
        <h3 class="section-title">账号信息</h3>
        <div class="settings-card tech-card">
          <div class="profile-row">
            <el-avatar :size="64" style="background: linear-gradient(135deg,#58a6ff,#39d0d8); font-size: 1.5rem; font-weight: 700;">
              {{ auth.userInfo?.username?.[0]?.toUpperCase() || 'A' }}
            </el-avatar>
            <div class="profile-info">
              <h4>{{ auth.userInfo?.nickname || auth.userInfo?.username }}</h4>
              <p>{{ auth.userInfo?.username }}@aiworkbench.local</p>
              <span class="tag tag-cyan">开发者</span>
            </div>
          </div>
        </div>
      </section>

      <!-- API Config -->
      <section class="settings-section">
        <h3 class="section-title">服务配置</h3>
        <div class="settings-card tech-card">
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">后端 API 地址</span>
              <span class="setting-hint">前端用于连接 FastAPI 后端服务</span>
            </div>
            <el-input v-model="apiBase" style="width: 280px" placeholder="http://localhost:8000"/>
          </div>
          <div class="divider"></div>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">Qwen 模型名称</span>
              <span class="setting-hint">HuggingFace 模型名称，如 Qwen/Qwen2.5-1.5B-Instruct</span>
            </div>
            <el-input v-model="qwenModel" style="width: 280px" placeholder="Qwen/Qwen2.5-1.5B-Instruct"/>
          </div>
          <div class="divider"></div>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">向量模型</span>
              <span class="setting-hint">用于文本嵌入与向量检索</span>
            </div>
            <el-input v-model="embeddingModel" style="width: 280px" placeholder="BAAI/bge-small-zh-v1.5"/>
          </div>
          <div class="divider"></div>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">运行设备</span>
              <span class="setting-hint">CPU 或 CUDA（需 GPU 支持）</span>
            </div>
            <el-select v-model="modelDevice" style="width: 280px">
              <el-option label="CPU" value="cpu"/>
              <el-option label="CUDA (GPU)" value="cuda"/>
            </el-select>
          </div>
          <div class="divider"></div>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">限流配置</span>
              <span class="setting-hint">每分钟最大请求数（0 = 不限流）</span>
            </div>
            <el-input-number v-model="rateLimit" :min="0" :max="1000"/>
          </div>
        </div>
      </section>

      <!-- Knowledge base info -->
      <section class="settings-section">
        <h3 class="section-title">知识库信息</h3>
        <div class="settings-card tech-card">
          <div class="kb-stats">
            <div class="kb-stat">
              <span class="kb-num">{{ KNOWLEDGE_COUNT }}</span>
              <span class="kb-label">预置知识条目</span>
            </div>
            <div class="kb-stat">
              <span class="kb-num">{{ CATEGORIES.join(', ') }}</span>
              <span class="kb-label">覆盖领域</span>
            </div>
          </div>
          <p class="kb-desc">系统预置了 Git、Docker、SQL、Python、系统设计、前端等常见编程问答知识库，开机即可用。更多知识可通过上传 PDF/TXT 文档补充。</p>
        </div>
      </section>

      <!-- Actions -->
      <section class="settings-section">
        <h3 class="section-title">操作</h3>
        <div class="settings-card tech-card action-card">
          <el-button @click="saveSettings" type="primary">
            <el-icon><Check /></el-icon> 保存配置
          </el-button>
          <el-button @click="resetSettings">
            <el-icon><RefreshRight /></el-icon> 重置
          </el-button>
          <el-button @click="checkHealth">
            <el-icon><Connection /></el-icon> 检测服务状态
          </el-button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const auth = useAuthStore()

const apiBase = ref(localStorage.getItem('api_base') || 'http://localhost:8000')
const qwenModel = ref(localStorage.getItem('qwen_model') || 'Qwen/Qwen2.5-1.5B-Instruct')
const embeddingModel = ref(localStorage.getItem('embedding_model') || 'BAAI/bge-small-zh-v1.5')
const modelDevice = ref(localStorage.getItem('model_device') || 'cpu')
const rateLimit = ref(Number(localStorage.getItem('rate_limit') || 60))

const KNOWLEDGE_COUNT = 23
const CATEGORIES = ['Git', 'Docker', 'SQL', 'Python', '系统设计', '前端', '网络', 'Redis', 'FastAPI', 'OS']

function saveSettings() {
  localStorage.setItem('api_base', apiBase.value)
  localStorage.setItem('qwen_model', qwenModel.value)
  localStorage.setItem('embedding_model', embeddingModel.value)
  localStorage.setItem('model_device', modelDevice.value)
  localStorage.setItem('rate_limit', String(rateLimit.value))
  ElMessage.success('配置已保存，部分配置需重启后端服务后生效')
}

function resetSettings() {
  apiBase.value = 'http://localhost:8000'
  qwenModel.value = 'Qwen/Qwen2.5-1.5B-Instruct'
  embeddingModel.value = 'BAAI/bge-small-zh-v1.5'
  modelDevice.value = 'cpu'
  rateLimit.value = 60
  ElMessage.info('配置已重置为默认值')
}

async function checkHealth() {
  try {
    const { data } = await axios.get(`${apiBase.value}/api/health`)
    ElMessage.success(`服务状态：${data.status} | 版本：${data.version}`)
  } catch {
    ElMessage.error('无法连接到后端服务，请检查服务是否启动')
  }
}
</script>

<style scoped>
.settings-page { height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
.page-header { padding: 16px 24px; border-bottom: 1px solid var(--border-color); background: var(--bg-secondary); }
.page-title { display: flex; align-items: center; gap: 8px; font-size: 1.1rem; font-weight: 700; color: var(--text-primary); }
.settings-body { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 24px; max-width: 760px; }
.settings-section { display: flex; flex-direction: column; gap: 12px; }
.section-title { font-size: .75rem; letter-spacing: 1px; color: var(--text-muted); text-transform: uppercase; }
.settings-card { padding: 20px; display: flex; flex-direction: column; gap: 0; }
.profile-row { display: flex; align-items: center; gap: 16px; }
.profile-info h4 { font-size: 1rem; color: var(--text-primary); margin-bottom: 2px; }
.profile-info p { font-size: .8rem; color: var(--text-muted); margin-bottom: 8px; }
.setting-item { display: flex; align-items: center; justify-content: space-between; padding: 12px 0; }
.setting-label { font-size: .88rem; color: var(--text-primary); margin-bottom: 2px; }
.setting-hint { font-size: .72rem; color: var(--text-muted); }
.divider { height: 1px; background: var(--border-color); }
.kb-stats { display: flex; gap: 24px; margin-bottom: 12px; }
.kb-stat { display: flex; flex-direction: column; }
.kb-num { font-size: 1.2rem; font-weight: 700; color: var(--accent-cyan); }
.kb-label { font-size: .72rem; color: var(--text-muted); }
.kb-desc { font-size: .8rem; color: var(--text-secondary); line-height: 1.7; }
.action-card { flex-direction: row; gap: 12px; }
</style>
