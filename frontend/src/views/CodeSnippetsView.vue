<template>
  <div class="snippets-container">
    <!-- 左侧：片段列表 -->
    <div class="snippets-sidebar">
      <div class="sidebar-header">
        <h3>📦 代码素材库</h3>
        <el-button type="primary" size="small" @click="showCreateDialog = true">
          + 新建
        </el-button>
      </div>

      <!-- 筛选 -->
      <div class="filters">
        <el-input
          v-model="keyword"
          placeholder="搜索片段..."
          prefix-icon="Search"
          clearable
          @input="debounceSearch"
        />

        <el-select v-model="filterCategory" placeholder="分类" clearable>
          <el-option
            v-for="cat in categories"
            :key="cat.name"
            :label="cat.name + ` (${cat.count})`"
            :value="cat.name"
          />
        </el-select>

        <el-select v-model="filterLanguage" placeholder="语言" clearable>
          <el-option label="Python" value="python" />
          <el-option label="JavaScript" value="javascript" />
          <el-option label="TypeScript" value="typescript" />
          <el-option label="Java" value="java" />
          <el-option label="Go" value="go" />
          <el-option label="SQL" value="sql" />
        </el-select>

        <el-checkbox v-model="filterFavorite">⭐ 收藏</el-checkbox>
      </div>

      <!-- 标签云 -->
      <div class="tags-cloud" v-if="tagsCloud.length">
        <span class="tags-title">标签：</span>
        <el-tag
          v-for="tag in tagsCloud.slice(0, 15)"
          :key="tag.name"
          :type="tag.count > 3 ? 'primary' : 'info'"
          size="small"
          class="tag-item"
          :class="{ active: selectedTags.includes(tag.name) }"
          @click="toggleTag(tag.name)"
        >
          {{ tag.name }} ({{ tag.count }})
        </el-tag>
      </div>

      <!-- 片段列表 -->
      <div class="snippets-list">
        <div
          v-for="snippet in snippets"
          :key="snippet.id"
          class="snippet-item"
          :class="{ active: selectedId === snippet.id }"
          @click="selectSnippet(snippet)"
        >
          <div class="snippet-header">
            <span class="snippet-title">{{ snippet.title }}</span>
            <span v-if="snippet.is_favorite" class="favorite-icon">⭐</span>
          </div>
          <div class="snippet-preview">{{ snippet.content?.substring(0, 80) }}...</div>
          <div class="snippet-meta">
            <el-tag size="small" type="info">{{ snippet.language || '未分类' }}</el-tag>
            <span class="use-count">使用 {{ snippet.use_count }} 次</span>
          </div>
          <div class="snippet-tags" v-if="snippet.tags?.length">
            <el-tag
              v-for="tag in snippet.tags.slice(0, 3)"
              :key="tag"
              size="small"
              effect="plain"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>

        <div v-if="snippets.length === 0" class="empty-state">
          <p>暂无片段</p>
          <el-button size="small" @click="showCreateDialog = true">
            创建第一个片段
          </el-button>
        </div>
      </div>
    </div>

    <!-- 右侧：片段详情 -->
    <div class="snippet-detail">
      <template v-if="currentSnippet">
        <div class="detail-header">
          <div class="detail-title">
            <h2>{{ currentSnippet.title }}</h2>
            <span v-if="currentSnippet.is_favorite">⭐</span>
          </div>
          <div class="detail-actions">
            <el-button @click="copySnippet" :disabled="!currentSnippet.content">
              📋 复制
            </el-button>
            <el-button @click="insertToChat" :disabled="!currentSnippet.content">
              💬 插入对话
            </el-button>
            <el-button @click="editSnippet">✏️ 编辑</el-button>
            <el-button @click="toggleFavorite">
              {{ currentSnippet.is_favorite ? '⭐' : '☆' }}
            </el-button>
            <el-button type="danger" @click="deleteSnippet">🗑️</el-button>
          </div>
        </div>

        <div class="detail-meta">
          <el-tag>{{ currentSnippet.category || '未分类' }}</el-tag>
          <el-tag type="info">{{ currentSnippet.language || '未指定' }}</el-tag>
          <span class="use-stat">使用 {{ currentSnippet.use_count }} 次</span>
        </div>

        <div class="detail-tags" v-if="currentSnippet.tags?.length">
          <el-tag
            v-for="tag in currentSnippet.tags"
            :key="tag"
            size="small"
            class="detail-tag"
          >
            {{ tag }}
          </el-tag>
        </div>

        <div class="detail-description" v-if="currentSnippet.description">
          {{ currentSnippet.description }}
        </div>

        <div class="detail-code">
          <div class="code-header">
            <span>💻 代码</span>
            <el-button size="small" @click="copySnippet">复制</el-button>
          </div>
          <pre class="code-block"><code>{{ currentSnippet.content }}</code></pre>
        </div>

        <div class="detail-footer">
          <span class="timestamp">
            创建于 {{ formatDate(currentSnippet.created_at) }}
          </span>
          <span class="timestamp" v-if="currentSnippet.updated_at !== currentSnippet.created_at">
            更新于 {{ formatDate(currentSnippet.updated_at) }}
          </span>
        </div>
      </template>

      <div v-else class="empty-state">
        <div class="empty-icon">📦</div>
        <p>选择一个片段查看详情</p>
      </div>
    </div>

    <!-- 创建/编辑弹窗 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingId ? '编辑片段' : '新建代码片段'"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form :model="snippetForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="snippetForm.title" placeholder="片段名称" />
        </el-form-item>

        <el-form-item label="分类">
          <el-select v-model="snippetForm.category" allow-create filterable placeholder="选择或输入分类">
            <el-option label="工具函数" value="utility" />
            <el-option label="业务模板" value="business" />
            <el-option label="SQL脚本" value="sql" />
            <el-option label="前端组件" value="frontend" />
            <el-option label="配置模板" value="config" />
            <el-option label="算法实现" value="algorithm" />
          </el-select>
        </el-form-item>

        <el-form-item label="语言">
          <el-select v-model="snippetForm.language" placeholder="选择语言">
            <el-option label="Python" value="python" />
            <el-option label="JavaScript" value="javascript" />
            <el-option label="TypeScript" value="typescript" />
            <el-option label="Java" value="java" />
            <el-option label="Go" value="go" />
            <el-option label="SQL" value="sql" />
            <el-option label="Shell" value="bash" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="标签">
          <el-select
            v-model="snippetForm.tags"
            multiple
            allow-create
            filterable
            placeholder="输入标签后按回车"
          >
          </el-select>
        </el-form-item>

        <el-form-item label="代码" required>
          <el-input
            v-model="snippetForm.content"
            type="textarea"
            :rows="12"
            placeholder="粘贴代码..."
            class="code-textarea"
          />
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="snippetForm.description"
            type="textarea"
            :rows="2"
            placeholder="片段说明或使用场景..."
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSnippet">
          {{ editingId ? '保存修改' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量操作工具栏 -->
    <div class="batch-toolbar" v-if="selectedIds.length > 0">
      <span>已选择 {{ selectedIds.length }} 个片段</span>
      <el-button size="small" @click="batchExport">导出</el-button>
      <el-button size="small" type="danger" @click="batchDelete">删除</el-button>
      <el-button size="small" @click="selectedIds = []">取消</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Snippet {
  id: number
  title: string
  content: string
  language?: string
  category?: string
  tags?: string[]
  description?: string
  is_favorite: boolean
  use_count: number
  created_at: string
  updated_at: string
}

const snippets = ref<Snippet[]>([])
const categories = ref<{name: string, count: number}[]>([])
const tagsCloud = ref<{name: string, count: number}[]>([])
const selectedId = ref<number | null>(null)
const currentSnippet = ref<Snippet | null>(null)
const showCreateDialog = ref(false)
const editingId = ref<number | null>(null)
const selectedIds = ref<number[]>([])

const keyword = ref('')
const filterCategory = ref('')
const filterLanguage = ref('')
const filterFavorite = ref(false)
const selectedTags = ref<string[]>([])

const snippetForm = ref({
  title: '',
  content: '',
  language: 'python',
  category: '',
  tags: [] as string[],
  description: ''
})

let searchTimer: ReturnType<typeof setTimeout>

const api = (window as any).api || {
  get: async (url: string) => {
    const res = await fetch(url, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })
    return { data: await res.json() }
  },
  post: async (url: string, body?: any) => {
    const res = await fetch(url, {
      method: body ? 'POST' : 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: body ? JSON.stringify(body) : undefined
    })
    return { data: await res.json() }
  },
  put: async (url: string, body: any) => {
    const res = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(body)
    })
    return { data: await res.json() }
  },
  delete: async (url: string) => {
    const res = await fetch(url, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    return { data: await res.json() }
  }
}

const loadSnippets = async () => {
  try {
    const params = new URLSearchParams()
    if (keyword.value) params.append('keyword', keyword.value)
    if (filterCategory.value) params.append('category', filterCategory.value)
    if (filterLanguage.value) params.append('language', filterLanguage.value)
    if (filterFavorite.value) params.append('is_favorite', 'true')

    const { data } = await api.get(`/api/v1/snippets/?${params}`)
    snippets.value = data.list || []
  } catch (e) {
    console.error('Failed to load snippets:', e)
  }
}

const loadCategories = async () => {
  try {
    const { data } = await api.get('/api/v1/snippets/categories/list')
    categories.value = data || []
  } catch (e) {
    console.error('Failed to load categories:', e)
  }
}

const loadTagsCloud = async () => {
  try {
    const { data } = await api.get('/api/v1/snippets/tags/cloud')
    tagsCloud.value = data || []
  } catch (e) {
    console.error('Failed to load tags:', e)
  }
}

const selectSnippet = async (snippet: Snippet) => {
  selectedId.value = snippet.id
  try {
    const { data } = await api.get(`/api/v1/snippets/${snippet.id}`)
    currentSnippet.value = data
  } catch (e) {
    currentSnippet.value = snippet
  }
}

const toggleTag = (tag: string) => {
  const idx = selectedTags.value.indexOf(tag)
  if (idx === -1) {
    selectedTags.value.push(tag)
  } else {
    selectedTags.value.splice(idx, 1)
  }
}

const debounceSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(loadSnippets, 300)
}

watch([filterCategory, filterLanguage, filterFavorite], loadSnippets)

const editSnippet = () => {
  if (!currentSnippet.value) return
  editingId.value = currentSnippet.value.id
  snippetForm.value = {
    title: currentSnippet.value.title,
    content: currentSnippet.value.content,
    language: currentSnippet.value.language || 'python',
    category: currentSnippet.value.category || '',
    tags: currentSnippet.value.tags || [],
    description: currentSnippet.value.description || ''
  }
  showCreateDialog.value = true
}

const saveSnippet = async () => {
  if (!snippetForm.value.title || !snippetForm.value.content) {
    ElMessage.warning('请填写标题和代码')
    return
  }

  try {
    if (editingId.value) {
      await api.put(`/api/v1/snippets/${editingId.value}`, snippetForm.value)
      ElMessage.success('更新成功')
    } else {
      await api.post('/api/v1/snippets/', snippetForm.value)
      ElMessage.success('创建成功')
    }

    showCreateDialog.value = false
    editingId.value = null
    resetForm()
    loadSnippets()
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e.message || ''))
  }
}

const deleteSnippet = async () => {
  if (!currentSnippet.value) return

  try {
    await ElMessageBox.confirm('确定要删除这个片段吗？', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await api.delete(`/api/v1/snippets/${currentSnippet.value.id}`)
    ElMessage.success('删除成功')
    currentSnippet.value = null
    selectedId.value = null
    loadSnippets()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const toggleFavorite = async () => {
  if (!currentSnippet.value) return
  try {
    await api.post(`/api/v1/snippets/${currentSnippet.value.id}/favorite`)
    currentSnippet.value.is_favorite = !currentSnippet.value.is_favorite
    loadSnippets()
  } catch (e) {
    console.error('Failed to toggle favorite:', e)
  }
}

const copySnippet = () => {
  if (currentSnippet.value?.content) {
    navigator.clipboard.writeText(currentSnippet.value.content)
    ElMessage.success('已复制到剪贴板')
  }
}

const insertToChat = () => {
  if (currentSnippet.value?.content) {
    window.dispatchEvent(new CustomEvent('insert-to-chat', {
      detail: currentSnippet.value
    }))
    ElMessage.success('已插入到对话')
  }
}

const batchExport = async () => {
  try {
    const { data } = await api.post('/api/v1/snippets/batch-export', {
      snippet_ids: selectedIds.value,
      format: 'markdown'
    })

    const blob = new Blob([data.content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = data.filename
    a.click()
    URL.revokeObjectURL(url)

    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除 ${selectedIds.value.length} 个片段吗？`, '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })

    for (const id of selectedIds.value) {
      await api.delete(`/api/v1/snippets/${id}`)
    }

    ElMessage.success('批量删除成功')
    selectedIds.value = []
    loadSnippets()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const resetForm = () => {
  snippetForm.value = {
    title: '',
    content: '',
    language: 'python',
    category: '',
    tags: [],
    description: ''
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const emit = defineEmits(['insert-to-chat'])

onMounted(() => {
  loadSnippets()
  loadCategories()
  loadTagsCloud()
})
</script>

<style scoped>
.snippets-container {
  height: 100%;
  display: flex;
  background: #0d1117;
  color: #e6edf3;
  overflow: hidden;
}

.snippets-sidebar {
  width: 400px;
  border-right: 1px solid #30363d;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #30363d;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
}

.filters {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-bottom: 1px solid #30363d;
}

.tags-cloud {
  padding: 8px 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
  border-bottom: 1px solid #30363d;
}

.tags-title {
  font-size: 12px;
  color: #8b949e;
}

.tag-item {
  cursor: pointer;
}

.tag-item.active {
  background: #58a6ff;
  color: #fff;
}

.snippets-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.snippet-item {
  background: #161b22;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  margin-bottom: 8px;
  transition: background 0.2s;
}

.snippet-item:hover {
  background: #21262d;
}

.snippet-item.active {
  background: rgba(88, 166, 255, 0.15);
  border-left: 2px solid #58a6ff;
}

.snippet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.snippet-title {
  font-weight: 600;
}

.favorite-icon {
  font-size: 14px;
}

.snippet-preview {
  font-size: 12px;
  color: #8b949e;
  font-family: 'Fira Code', monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 8px;
}

.snippet-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #6e7681;
}

.use-count {
  margin-left: auto;
}

.snippet-tags {
  display: flex;
  gap: 4px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.snippet-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 24px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.detail-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-title h2 {
  margin: 0;
  font-size: 20px;
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.detail-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.use-stat {
  font-size: 13px;
  color: #8b949e;
  margin-left: auto;
}

.detail-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.detail-tag {
  cursor: default;
}

.detail-description {
  color: #8b949e;
  margin-bottom: 16px;
  padding: 12px;
  background: #161b22;
  border-radius: 8px;
}

.detail-code {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-weight: 600;
}

.code-block {
  flex: 1;
  background: #0d1117;
  padding: 16px;
  border-radius: 8px;
  overflow: auto;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

.detail-footer {
  display: flex;
  gap: 16px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #30363d;
}

.timestamp {
  font-size: 12px;
  color: #6e7681;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #6e7681;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.code-textarea :deep(textarea) {
  font-family: 'Fira Code', 'Consolas', monospace !important;
}

.batch-toolbar {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: #21262d;
  padding: 12px 24px;
  border-radius: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  z-index: 100;
}
</style>
