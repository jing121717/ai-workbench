<template>
  <div class="code-repo-container">
    <div class="repo-header">
      <div class="header-left">
        <h2>📦 代码仓库管理</h2>
        <el-tag type="info" v-if="activeProject">{{ activeProject.name }}</el-tag>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showImportDialog = true">
          ➕ 导入代码仓库
        </el-button>
        <el-button @click="refreshProjects" :loading="loading">
          🔄 刷新
        </el-button>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧：项目列表 -->
      <div class="projects-sidebar">
        <div class="sidebar-header">
          <span>我的项目</span>
        </div>
        <div class="project-list">
          <div
            v-for="project in projects"
            :key="project.id"
            class="project-item"
            :class="{ active: activeProject?.id === project.id }"
            @click="selectProject(project)"
          >
            <div class="project-icon">📁</div>
            <div class="project-info">
              <div class="project-name">{{ project.name }}</div>
              <div class="project-meta">
                <span>{{ project.total_files }} 文件</span>
                <span>{{ project.total_units }} 单元</span>
              </div>
              <div class="project-tech">
                <el-tag
                  v-for="tech in (project.tech_stack || []).slice(0, 3)"
                  :key="tech"
                  size="small"
                  type="info"
                >
                  {{ tech }}
                </el-tag>
              </div>
            </div>
          </div>

          <div v-if="projects.length === 0" class="empty-state">
            <p>暂无项目</p>
            <el-button size="small" @click="showImportDialog = true">
              导入第一个项目
            </el-button>
          </div>
        </div>
      </div>

      <!-- 中间：项目结构 -->
      <div class="structure-panel">
        <template v-if="activeProject">
          <div class="panel-header">
            <span>📂 项目结构</span>
            <div class="panel-actions">
              <el-button size="small" @click="syncProject" :loading="syncing">
                🔄 同步
              </el-button>
              <el-button size="small" @click="showUnitList = true">
                📋 代码单元
              </el-button>
            </div>
          </div>

          <!-- 文件树 -->
          <div class="file-tree">
            <el-tree
              :data="treeData"
              :props="treeProps"
              node-key="path"
              default-expand-all
              @node-click="handleNodeClick"
            >
              <template #default="{ node, data }">
                <span class="tree-node">
                  <span class="node-icon">{{ data.type === 'dir' ? '📁' : getFileIcon(data.ext) }}</span>
                  <span class="node-label">{{ node.label }}</span>
                  <span v-if="data.type === 'file'" class="node-size">{{ getFileSize(data.path) }}</span>
                </span>
              </template>
            </el-tree>
          </div>

          <!-- 语言统计 -->
          <div class="lang-stats" v-if="activeProject.languages_stats">
            <div class="stats-title">📊 语言分布</div>
            <div class="lang-bars">
              <div
                v-for="(count, lang) in activeProject.languages_stats"
                :key="lang"
                class="lang-bar-item"
              >
                <span class="lang-name">{{ lang }}</span>
                <div class="bar-container">
                  <div
                    class="bar-fill"
                    :style="{ width: getLangPercent(count) + '%' }"
                  ></div>
                </div>
                <span class="lang-count">{{ count }}</span>
              </div>
            </div>
          </div>
        </template>

        <div v-else class="empty-state">
          <div class="empty-icon">📦</div>
          <p>选择一个项目查看详情</p>
        </div>
      </div>

      <!-- 右侧：代码单元详情 -->
      <div class="units-panel">
        <template v-if="selectedUnit">
          <div class="unit-header">
            <div class="unit-title">
              <el-tag size="small" :type="getUnitTypeColor(selectedUnit.type)">
                {{ selectedUnit.type }}
              </el-tag>
              <span>{{ selectedUnit.name }}</span>
            </div>
            <el-button size="small" @click="selectedUnit = null">关闭</el-button>
          </div>

          <div class="unit-meta">
            <div>📁 {{ selectedUnit.file_path }}</div>
            <div>📍 行 {{ selectedUnit.start_line }}-{{ selectedUnit.end_line }}</div>
            <div v-if="selectedUnit.signature">🔖 {{ selectedUnit.signature }}</div>
          </div>

          <div v-if="selectedUnit.doc_comment" class="unit-doc">
            <div class="doc-title">📝 文档注释</div>
            <pre class="doc-content">{{ selectedUnit.doc_comment }}</pre>
          </div>

          <div class="unit-code">
            <div class="code-header">
              <span>💻 代码</span>
              <el-button size="small" @click="copyCode">📋 复制</el-button>
            </div>
            <pre class="code-content"><code>{{ selectedUnit.content }}</code></pre>
          </div>
        </template>

        <div v-else class="empty-state">
          <p>选择一个代码单元查看</p>
        </div>
      </div>
    </div>

    <!-- 导入弹窗 -->
    <el-dialog v-model="showImportDialog" title="导入代码仓库" width="600px">
      <el-tabs v-model="importTab">
        <el-tab-pane label="📁 上传文件" name="upload">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :file-list="fileList"
            drag
            multiple
          >
            <el-icon><UploadFilled /></el-icon>
            <div>拖拽文件或点击上传</div>
            <template #tip>
              <div class="el-upload__tip">支持所有编程语言文件</div>
            </template>
          </el-upload>
        </el-tab-pane>

        <el-tab-pane label="🔗 Git 克隆" name="git">
          <el-form :model="gitForm" label-width="100px">
            <el-form-item label="仓库地址">
              <el-input
                v-model="gitForm.url"
                placeholder="https://github.com/user/repo.git"
              />
            </el-form-item>
            <el-form-item label="本地路径">
              <el-input v-model="gitForm.localPath" placeholder="可选，留空则使用默认路径" />
            </el-form-item>
            <el-form-item label="分支">
              <el-input v-model="gitForm.branch" placeholder="main" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button
          v-if="importTab === 'upload'"
          type="primary"
          @click="startUpload"
          :loading="importing"
        >
          开始导入
        </el-button>
        <el-button
          v-else
          type="primary"
          @click="startGitClone"
          :loading="importing"
        >
          克隆仓库
        </el-button>
      </template>
    </el-dialog>

    <!-- 代码单元列表弹窗 -->
    <el-dialog v-model="showUnitList" title="代码单元" width="800px">
      <div class="units-filter">
        <el-select v-model="filterType" placeholder="按类型筛选" clearable>
          <el-option label="函数" value="function" />
          <el-option label="类" value="class" />
          <el-option label="接口" value="interface" />
          <el-option label="方法" value="method" />
          <el-option label="常量" value="constant" />
        </el-select>
        <el-input
          v-model="filterKeyword"
          placeholder="搜索名称..."
          prefix-icon="Search"
          clearable
        />
      </div>

      <el-table :data="filteredUnits" style="width: 100%" height="400">
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="getUnitTypeColor(row.type)">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="file_path" label="文件" show-overflow-tooltip />
        <el-table-column prop="start_line" label="行号" width="80" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="viewUnit(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

interface Project {
  id: number
  name: string
  tech_stack: string[]
  total_files: number
  total_units: number
  languages_stats?: Record<string, number>
  project_tree?: any
}

interface CodeUnit {
  id: number
  type: string
  name: string
  file_path: string
  start_line: number
  end_line: number
  content: string
  signature?: string
  doc_comment?: string
}

const loading = ref(false)
const syncing = ref(false)
const importing = ref(false)
const projects = ref<Project[]>([])
const activeProject = ref<Project | null>(null)
const selectedUnit = ref<CodeUnit | null>(null)
const showImportDialog = ref(false)
const showUnitList = ref(false)
const importTab = ref('upload')
const fileList = ref<any[]>([])
const filterType = ref('')
const filterKeyword = ref('')
const units = ref<CodeUnit[]>([])

const gitForm = ref({
  url: '',
  localPath: '',
  branch: 'main'
})

const treeProps = {
  children: 'children',
  label: 'name'
}

const treeData = computed(() => {
  if (!activeProject.value?.project_tree) return []
  return [activeProject.value.project_tree]
})

const filteredUnits = computed(() => {
  let result = units.value
  if (filterType.value) {
    result = result.filter(u => u.type === filterType.value)
  }
  if (filterKeyword.value) {
    const kw = filterKeyword.value.toLowerCase()
    result = result.filter(u =>
      u.name.toLowerCase().includes(kw) ||
      u.file_path.toLowerCase().includes(kw)
    )
  }
  return result
})

const api = (window as any).api || {
  get: async (url: string) => {
    const res = await fetch(url, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })
    return { data: await res.json() }
  },
  post: async (url: string, body: any) => {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(body)
    })
    return { data: await res.json() }
  }
}

const loadProjects = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/api/v1/code-projects/')
    projects.value = data.owned || []
  } catch (e) {
    console.error('Failed to load projects:', e)
  } finally {
    loading.value = false
  }
}

const selectProject = async (project: Project) => {
  activeProject.value = project
  selectedUnit.value = null

  try {
    const { data } = await api.get(`/api/v1/code-projects/${project.id}`)
    activeProject.value = { ...activeProject.value, ...data }
  } catch (e) {
    console.error('Failed to load project details:', e)
  }
}

const refreshProjects = () => {
  loadProjects()
}

const syncProject = async () => {
  if (!activeProject.value) return
  syncing.value = true
  try {
    await api.post(`/api/v1/code-projects/${activeProject.value.id}/sync`)
    ElMessage.success('同步成功')
    selectProject(activeProject.value)
  } catch (e) {
    ElMessage.error('同步失败')
  } finally {
    syncing.value = false
  }
}

const handleFileChange = (file: any) => {
  fileList.value.push(file)
}

const startUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择文件')
    return
  }
  importing.value = true
  ElMessage.info('文件上传功能需要前端实现多文件表单提交')
  importing.value = false
}

const startGitClone = async () => {
  if (!gitForm.value.url) {
    ElMessage.warning('请输入仓库地址')
    return
  }
  importing.value = true
  try {
    const { data } = await api.post('/api/v1/code-projects/git-clone', gitForm.value)
    ElMessage.success('克隆成功')
    showImportDialog.value = false
    loadProjects()
  } catch (e: any) {
    ElMessage.error(e.message || '克隆失败')
  } finally {
    importing.value = false
  }
}

const handleNodeClick = async (data: any) => {
  if (data.type === 'file') {
    const { data: unitData } = await api.get(`/api/v1/code-projects/${activeProject.value?.id}/units?file_path=${data.path}`)
    if (unitData.units && unitData.units.length > 0) {
      selectedUnit.value = unitData.units[0]
    }
  }
}

const viewUnit = (unit: CodeUnit) => {
  selectedUnit.value = unit
  showUnitList.value = false
}

const getFileIcon = (ext: string) => {
  const icons: Record<string, string> = {
    '.py': '🐍', '.js': '🟨', '.ts': '🔷', '.vue': '💚',
    '.java': '☕', '.go': '🔵', '.rs': '🦀', '.sql': '🗃️',
    '.html': '🌐', '.css': '🎨', '.json': '📋', '.md': '📝'
  }
  return icons[ext] || '📄'
}

const getLangPercent = (count: number) => {
  if (!activeProject.value?.languages_stats) return 0
  const total = Object.values(activeProject.value.languages_stats).reduce((a, b) => a + b, 0)
  return total > 0 ? (count / total) * 100 : 0
}

const getUnitTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    function: 'success', class: 'warning', interface: 'info',
    method: 'success', constant: '', type: 'info'
  }
  return colors[type] || ''
}

const copyCode = () => {
  if (selectedUnit.value?.content) {
    navigator.clipboard.writeText(selectedUnit.value.content)
    ElMessage.success('已复制')
  }
}

onMounted(loadProjects)
</script>

<style scoped>
.code-repo-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #0d1117;
  color: #e6edf3;
}

.repo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #30363d;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.projects-sidebar {
  width: 300px;
  border-right: 1px solid #30363d;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 12px 16px;
  font-weight: 600;
  border-bottom: 1px solid #30363d;
}

.project-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.project-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 4px;
}

.project-item:hover {
  background: #161b22;
}

.project-item.active {
  background: rgba(88, 166, 255, 0.15);
  border-left: 2px solid #58a6ff;
}

.project-icon {
  font-size: 24px;
}

.project-info {
  flex: 1;
  min-width: 0;
}

.project-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.project-meta {
  font-size: 12px;
  color: #8b949e;
  display: flex;
  gap: 8px;
}

.project-tech {
  display: flex;
  gap: 4px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.structure-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #30363d;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #30363d;
}

.panel-actions {
  display: flex;
  gap: 8px;
}

.file-tree {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-icon {
  font-size: 14px;
}

.node-size {
  font-size: 11px;
  color: #6e7681;
  margin-left: auto;
}

.lang-stats {
  padding: 16px;
  border-top: 1px solid #30363d;
}

.stats-title {
  font-weight: 600;
  margin-bottom: 12px;
}

.lang-bar-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.lang-name {
  width: 80px;
  font-size: 12px;
}

.bar-container {
  flex: 1;
  height: 8px;
  background: #21262d;
  border-radius: 4px;
}

.bar-fill {
  height: 100%;
  background: #58a6ff;
  border-radius: 4px;
  transition: width 0.3s;
}

.lang-count {
  width: 40px;
  font-size: 12px;
  color: #8b949e;
  text-align: right;
}

.units-panel {
  width: 400px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.unit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #30363d;
}

.unit-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.unit-meta {
  padding: 12px 16px;
  font-size: 13px;
  color: #8b949e;
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-bottom: 1px solid #30363d;
}

.unit-doc, .unit-code {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
}

.doc-title, .code-header {
  font-weight: 600;
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.doc-content, .code-content {
  background: #0d1117;
  padding: 12px;
  border-radius: 8px;
  font-size: 13px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
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

.units-filter {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.units-filter .el-select {
  width: 150px;
}

.units-filter .el-input {
  flex: 1;
}
</style>
