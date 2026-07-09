<template>
  <div class="knowledge-page">
    <header class="page-header">
      <div>
        <h2 class="page-title"><el-icon color="var(--accent-cyan)"><Document /></el-icon> 知识库</h2>
        <p class="page-sub">上传 PDF/TXT 文档，构建私有 RAG 向量知识库</p>
      </div>
      <el-button type="primary" @click="triggerUpload">
        <el-icon><Upload /></el-icon> 上传文档
      </el-button>
      <input ref="fileInput" type="file" accept=".pdf,.txt" style="display:none" @change="handleFileChange"/>
    </header>

    <!-- Stats -->
    <div class="stats-row">
      <div class="stat-card tech-card">
        <div class="stat-icon"><el-icon :size="24" color="var(--accent-blue)"><Document /></el-icon></div>
        <div class="stat-info">
          <span class="stat-num">{{ stats.total }}</span>
          <span class="stat-label">文档总数</span>
        </div>
      </div>
      <div class="stat-card tech-card">
        <div class="stat-icon"><el-icon :size="24" color="var(--accent-green)"><SuccessFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-num">{{ stats.completed }}</span>
          <span class="stat-label">已完成</span>
        </div>
      </div>
      <div class="stat-card tech-card">
        <div class="stat-icon"><el-icon :size="24" color="var(--accent-purple)"><Cpu /></el-icon></div>
        <div class="stat-info">
          <span class="stat-num">{{ stats.chunks }}</span>
          <span class="stat-label">向量切片</span>
        </div>
      </div>
      <div class="stat-card tech-card">
        <div class="stat-icon"><el-icon :size="24" color="var(--accent-orange)"><Warning /></el-icon></div>
        <div class="stat-info">
          <span class="stat-num">{{ stats.failed }}</span>
          <span class="stat-label">处理失败</span>
        </div>
      </div>
    </div>

    <!-- Document list -->
    <div class="doc-list" v-loading="loading">
      <div v-if="documents.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">
          <el-icon :size="64" color="var(--text-muted)"><FolderOpened /></el-icon>
        </div>
        <h3>知识库为空</h3>
        <p>上传 PDF 或 TXT 文档，构建您的私有知识库</p>
        <el-button type="primary" @click="triggerUpload">立即上传</el-button>
      </div>

      <div v-else class="doc-grid">
        <div v-for="doc in documents" :key="doc.id" class="doc-card tech-card">
          <div class="doc-header">
            <div class="doc-icon">
              <el-icon :size="24" color="var(--accent-cyan)"><Document /></el-icon>
            </div>
            <div class="doc-meta">
              <h4 class="doc-title">{{ doc.title }}</h4>
              <p class="doc-filename">{{ doc.file_name || '无文件名' }}</p>
            </div>
            <span class="tag" :class="statusTag(doc.status)">{{ doc.status === 'completed' ? '已完成' : doc.status === 'pending' ? '处理中' : '失败' }}</span>
          </div>
          <div class="doc-stats">
            <span><el-icon><Size /></el-icon> {{ formatSize(doc.file_size) }}</span>
            <span><el-icon><Cpu /></el-icon> {{ doc.chunk_count }} 个切片</span>
            <span><el-icon><Clock /></el-icon> {{ formatDate(doc.created_at) }}</span>
          </div>
          <div class="doc-actions">
            <el-button text type="primary" size="small" @click="askAbout(doc)">
              <el-icon><ChatDotRound /></el-icon> 基于此提问
            </el-button>
            <el-button text type="danger" size="small" @click="deleteDoc(doc.id)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { knowledgeApi } from '../api/client'
import type { Document } from '../types'

const router = useRouter()
const documents = ref<Document[]>([])
const loading = ref(false)
const fileInput = ref<HTMLInputElement>()

const stats = computed(() => ({
  total: documents.value.length,
  completed: documents.value.filter(d => d.status === 'completed').length,
  pending: documents.value.filter(d => d.status === 'pending').length,
  failed: documents.value.filter(d => d.status === 'failed').length,
  chunks: documents.value.reduce((sum, d) => sum + d.chunk_count, 0),
}))

function statusTag(status: string) {
  if (status === 'completed') return 'tag-green'
  if (status === 'pending') return 'tag-blue'
  return 'tag-orange'
}

function formatSize(bytes: number) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

function formatDate(dt: string) {
  return new Date(dt).toLocaleDateString('zh-CN')
}

async function loadDocs() {
  loading.value = true
  try {
    const { data } = await knowledgeApi.listDocuments({ limit: 100 })
    documents.value = data.results
  } finally {
    loading.value = false
  }
}

function triggerUpload() { fileInput.value?.click() }

async function handleFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  loading.value = true
  try {
    await knowledgeApi.uploadDocument(file)
    ElMessage.success('文档上传成功，正在处理中...')
    await loadDocs()
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '上传失败')
  } finally {
    loading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

function askAbout(doc: Document) {
  ElMessage.info('正在跳转到对话页面...')
  router.push('/chat')
}

async function deleteDoc(id: number) {
  await ElMessageBox.confirm('确定删除该文档？删除后将无法用于 RAG 检索。', '提示', { type: 'warning' })
  await knowledgeApi.deleteDocument(id)
  ElMessage.success('已删除')
  await loadDocs()
}

onMounted(loadDocs)
</script>

<style scoped>
.knowledge-page { height: 100vh; display: flex; flex-direction: column; overflow: hidden; }

.page-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 24px; border-bottom: 1px solid var(--border-color); background: var(--bg-secondary);
}
.page-title { display: flex; align-items: center; gap: 8px; font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.page-sub { font-size: .75rem; color: var(--text-muted); }

.stats-row { display: flex; gap: 16px; padding: 20px 24px; }
.stat-card { flex: 1; display: flex; align-items: center; gap: 14px; padding: 16px; }
.stat-icon { width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; background: var(--bg-secondary); border-radius: var(--radius-sm); flex-shrink: 0; }
.stat-num { display: block; font-size: 1.4rem; font-weight: 800; color: var(--text-primary); }
.stat-label { font-size: .72rem; color: var(--text-muted); }

.doc-list { flex: 1; overflow-y: auto; padding: 0 24px 24px; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px; text-align: center; gap: 12px; }
.empty-icon { margin-bottom: 8px; }
.empty-state h3 { font-size: 1.1rem; color: var(--text-primary); }
.empty-state p { color: var(--text-muted); font-size: .82rem; }

.doc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.doc-card { padding: 20px; }
.doc-header { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 14px; }
.doc-icon { width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; background: rgba(57,208,216,.1); border-radius: var(--radius-sm); flex-shrink: 0; }
.doc-meta { flex: 1; min-width: 0; }
.doc-title { font-size: .88rem; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.doc-filename { font-size: .72rem; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.doc-stats { display: flex; gap: 14px; margin-bottom: 14px; font-size: .72rem; color: var(--text-muted); }
.doc-stats span { display: flex; align-items: center; gap: 4px; }
.doc-actions { display: flex; gap: 8px; border-top: 1px solid var(--border-color); padding-top: 12px; }
</style>
