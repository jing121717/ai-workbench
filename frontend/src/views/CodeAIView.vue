<template>
  <div class="code-ai-container">
    <div class="ai-toolbar">
      <el-tabs v-model="activeTool" @tab-change="activeTool = $event">
        <el-tab-pane label="🔍 缺陷扫描" name="defect" />
        <el-tab-pane label="🔄 跨语言转换" name="convert" />
        <el-tab-pane label="✅ 单元测试" name="test" />
        <el-tab-pane label="📄 接口文档" name="doc" />
        <el-tab-pane label="📋 日志解析" name="log" />
        <el-tab-pane label="🔧 代码重构" name="refactor" />
      </el-tabs>
    </div>

    <div class="ai-main">
      <!-- 左侧：输入 -->
      <div class="input-panel">
        <div class="panel-header">
          <span>输入代码 / 内容</span>
          <el-select v-model="language" placeholder="选择语言" style="width: 140px;">
            <el-option label="Python" value="python" />
            <el-option label="JavaScript" value="javascript" />
            <el-option label="TypeScript" value="typescript" />
            <el-option label="Java" value="java" />
            <el-option label="Go" value="go" />
            <el-option label="Rust" value="rust" />
            <el-option label="SQL" value="sql" />
            <el-option label="C/C++" value="cpp" />
          </el-select>
        </div>

        <div class="input-actions-top">
          <el-select v-if="activeTool === 'convert'" v-model="targetLanguage" placeholder="目标语言" style="width: 140px;">
            <el-option label="Python" value="python" />
            <el-option label="JavaScript" value="javascript" />
            <el-option label="TypeScript" value="typescript" />
            <el-option label="Go" value="go" />
            <el-option label="Java" value="java" />
          </el-select>

          <el-select v-if="activeTool === 'test'" v-model="testFramework" placeholder="测试框架" style="width: 140px;">
            <el-option label="pytest" value="pytest" />
            <el-option label="unittest" value="unittest" />
            <el-option label="jest" value="jest" />
            <el-option label="JUnit" value="junit" />
          </el-select>

          <el-select v-if="activeTool === 'refactor'" v-model="refactorType" placeholder="重构类型" style="width: 140px;">
            <el-option label="可读性" value="readability" />
            <el-option label="性能" value="performance" />
            <el-option label="安全性" value="security" />
            <el-option label="模块化" value="modularity" />
          </el-select>
        </div>

        <el-input
          v-model="codeInput"
          type="textarea"
          :rows="12"
          placeholder="粘贴代码、错误日志或描述..."
          class="code-input"
          @keydown.ctrl.enter="runAnalysis"
        />

        <div class="input-actions">
          <el-upload :auto-upload="false" @change="handleFileUpload">
            <el-button>📎 上传文件</el-button>
          </el-upload>
          <el-button type="primary" @click="runAnalysis" :loading="analyzing">
            🚀 {{ analysisBtnText }}
          </el-button>
        </div>
      </div>

      <!-- 右侧：输出 -->
      <div class="output-panel">
        <div class="panel-header">
          <span>分析结果</span>
          <el-button v-if="result" size="small" @click="copyResult">📋 复制</el-button>
        </div>

        <div class="result-content" v-loading="analyzing">
          <!-- 缺陷扫描结果 -->
          <template v-if="activeTool === 'defect' && result">
            <div v-if="result.issues?.length" class="issues-list">
              <div
                v-for="(issue, idx) in result.issues"
                :key="idx"
                class="issue-card"
                :class="issue.severity"
              >
                <div class="issue-header">
                  <el-tag :type="severityType[issue.severity]" size="small">
                    {{ issue.severity?.toUpperCase() }}
                  </el-tag>
                  <el-tag size="small" type="info">{{ issue.type }}</el-tag>
                  <span v-if="issue.location" class="issue-location">{{ issue.location }}</span>
                </div>
                <div class="issue-desc">{{ issue.description }}</div>
                <div class="issue-suggestion">💡 {{ issue.suggestion }}</div>
                <pre v-if="issue.code_snippet" class="issue-code">{{ issue.code_snippet }}</pre>
              </div>
            </div>

            <div v-if="result.summary" class="summary-card">
              <div class="score" v-if="result.score">
                代码评分: <span class="score-num" :class="getScoreClass(result.score)">{{ result.score }}</span>/100
              </div>
              <div class="summary-text">{{ result.summary }}</div>
            </div>
          </template>

          <!-- 跨语言转换结果 -->
          <template v-if="activeTool === 'convert' && result">
            <div v-if="result.converted_code" class="code-output">
              <pre><code>{{ result.converted_code }}</code></pre>
            </div>

            <div v-if="result.compatibility_notes?.length" class="notes-section">
              <h4>⚠️ 兼容性说明</h4>
              <ul>
                <li v-for="(note, idx) in result.compatibility_notes" :key="idx">{{ note }}</li>
              </ul>
            </div>
          </template>

          <!-- 单元测试结果 -->
          <template v-if="activeTool === 'test' && result">
            <div v-if="result.test_code" class="code-output">
              <pre><code>{{ result.test_code }}</code></pre>
            </div>
            <div v-if="result.test_framework" class="meta-info">
              测试框架: {{ result.test_framework }}
            </div>
          </template>

          <!-- 接口文档结果 -->
          <template v-if="activeTool === 'doc' && result">
            <div v-if="result.api_name" class="api-doc">
              <h3>{{ result.api_name }}</h3>
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item label="Endpoint">{{ result.endpoint }}</el-descriptions-item>
                <el-descriptions-item label="Method">
                  <el-tag size="small">{{ result.method }}</el-tag>
                </el-descriptions-item>
              </el-descriptions>

              <h4 v-if="result.parameters?.length">参数</h4>
              <el-table v-if="result.parameters?.length" :data="result.parameters" border size="small">
                <el-table-column prop="name" label="参数名" />
                <el-table-column prop="type" label="类型" width="80" />
                <el-table-column prop="required" label="必填" width="60">
                  <template #default="{ row }">{{ row.required ? '是' : '否' }}</template>
                </el-table-column>
                <el-table-column prop="description" label="说明" />
              </el-table>

              <h4 v-if="result.request_example">请求示例</h4>
              <pre v-if="result.request_example" class="example-code">{{ result.request_example }}</pre>
            </div>
          </template>

          <!-- 日志解析结果 -->
          <template v-if="activeTool === 'log' && result">
            <div v-if="result.root_cause" class="log-analysis">
              <el-alert type="error" :closable="false" class="root-cause">
                <template #title>
                  <strong>根因：</strong> {{ result.root_cause }}
                </template>
              </el-alert>

              <div class="analysis-section" v-if="result.error_location">
                <h4>📍 错误位置</h4>
                <code>{{ result.error_location }}</code>
              </div>

              <div class="analysis-section" v-if="result.solution?.steps">
                <h4>✅ 解决步骤</h4>
                <ol>
                  <li v-for="(step, idx) in result.solution.steps" :key="idx">{{ step }}</li>
                </ol>
              </div>

              <div class="analysis-section" v-if="result.solution?.code_fix">
                <h4>🔧 修复代码</h4>
                <pre class="code-output">{{ result.solution.code_fix }}</pre>
              </div>
            </div>
          </template>

          <!-- 代码重构结果 -->
          <template v-if="activeTool === 'refactor' && result">
            <div v-if="result.refactored_code" class="code-output">
              <pre><code>{{ result.refactored_code }}</code></pre>
            </div>

            <div v-if="result.changes?.length" class="changes-list">
              <h4>📝 改动内容</h4>
              <div v-for="(change, idx) in result.changes" :key="idx" class="change-item">
                <span class="change-type">{{ change.type }}</span>
                <span>{{ change.description || change.before }}</span>
              </div>
            </div>
          </template>

          <!-- 空状态 -->
          <div v-if="!result && !analyzing" class="empty-result">
            <div class="empty-icon">{{ toolIcons[activeTool] }}</div>
            <p>输入代码后点击分析按钮</p>
            <p class="empty-hint">{{ toolHints[activeTool] }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const activeTool = ref('defect')
const language = ref('python')
const targetLanguage = ref('python')
const testFramework = ref('pytest')
const refactorType = ref('readability')
const codeInput = ref('')
const analyzing = ref(false)
const result = ref<any>(null)

const toolIcons: Record<string, string> = {
  defect: '🔍', convert: '🔄', test: '✅', doc: '📄', log: '📋', refactor: '🔧'
}

const toolHints: Record<string, string> = {
  defect: '识别安全漏洞、性能问题、潜在Bug',
  convert: 'Python/JavaScript/Go等语言互转',
  test: '自动生成单元测试用例',
  doc: '从代码生成API接口文档',
  log: '分析错误日志，定位问题原因',
  refactor: '优化代码结构和可读性'
}

const severityType: Record<string, string> = {
  high: 'danger', medium: 'warning', low: 'info'
}

const analysisBtnText = computed(() => {
  const texts: Record<string, string> = {
    defect: '运行分析', convert: '开始转换', test: '生成测试',
    doc: '生成文档', log: '解析日志', refactor: '开始重构'
  }
  return texts[activeTool.value] || '分析'
})

const api = (window as any).api || {
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

const runAnalysis = async () => {
  if (!codeInput.value.trim()) {
    ElMessage.warning('请输入代码')
    return
  }

  analyzing.value = true
  result.value = null

  try {
    let endpoint = ''
    let requestData: any = {
      code: codeInput.value,
      language: language.value
    }

    switch (activeTool.value) {
      case 'defect':
        endpoint = '/api/v1/code-ai/analyze'
        requestData.analysis_type = 'defect'
        break
      case 'convert':
        endpoint = '/api/v1/code-ai/convert'
        requestData.source_language = language.value
        requestData.target_language = targetLanguage.value
        break
      case 'test':
        endpoint = '/api/v1/code-ai/unit-test'
        requestData.framework = testFramework.value
        break
      case 'doc':
        endpoint = '/api/v1/code-ai/api-doc'
        break
      case 'log':
        endpoint = '/api/v1/code-ai/log-analyze'
        requestData.error_type = 'runtime'
        break
      case 'refactor':
        endpoint = '/api/v1/code-ai/refactor'
        requestData.refactor_type = refactorType.value
        break
    }

    const { data } = await api.post(endpoint, requestData)
    result.value = data
  } catch (e: any) {
    ElMessage.error('分析失败: ' + (e.message || '未知错误'))
  } finally {
    analyzing.value = false
  }
}

const handleFileUpload = async (file: any) => {
  const content = await file.raw.text()
  codeInput.value = content
}

const getScoreClass = (score: number) => {
  if (score >= 80) return 'score-good'
  if (score >= 60) return 'score-warning'
  return 'score-bad'
}

const copyResult = () => {
  const text = result.value ? JSON.stringify(result.value, null, 2) : ''
  navigator.clipboard.writeText(text)
  ElMessage.success('已复制')
}
</script>

<style scoped>
.code-ai-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #0d1117;
  color: #e6edf3;
}

.ai-toolbar {
  padding: 0 24px;
  border-bottom: 1px solid #30363d;
}

.ai-toolbar :deep(.el-tabs__header) {
  margin-bottom: 0;
}

.ai-main {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  padding: 16px 24px;
  overflow: hidden;
}

.input-panel, .output-panel {
  background: #161b22;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  color: #e6edf3;
  font-weight: 600;
}

.input-actions-top {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.code-input :deep(textarea) {
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  background: #0d1117 !important;
  color: #e6edf3 !important;
  border: 1px solid #30363d !important;
  border-radius: 8px !important;
  resize: none;
}

.input-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.result-content {
  flex: 1;
  overflow-y: auto;
  color: #e6edf3;
}

.issues-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.issue-card {
  background: #0d1117;
  border-radius: 8px;
  padding: 12px;
  border-left: 3px solid;
}

.issue-card.high { border-color: #f85149; }
.issue-card.medium { border-color: #d29922; }
.issue-card.low { border-color: #58a6ff; }

.issue-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.issue-location {
  font-size: 12px;
  color: #8b949e;
  margin-left: auto;
}

.issue-desc {
  margin: 8px 0;
  color: #8b949e;
  font-size: 13px;
}

.issue-suggestion {
  background: rgba(88, 166, 255, 0.1);
  padding: 8px 12px;
  border-radius: 6px;
  color: #58a6ff;
  font-size: 13px;
}

.issue-code {
  background: #21262d;
  padding: 8px;
  border-radius: 6px;
  font-size: 12px;
  overflow-x: auto;
  margin-top: 8px;
}

.summary-card {
  background: #0d1117;
  border-radius: 8px;
  padding: 16px;
  margin-top: 12px;
}

.score {
  font-size: 16px;
  margin-bottom: 8px;
}

.score-num {
  font-size: 24px;
  font-weight: bold;
}

.score-good { color: #3fb950; }
.score-warning { color: #d29922; }
.score-bad { color: #f85149; }

.code-output {
  background: #0d1117;
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
}

.code-output pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.notes-section, .changes-list {
  margin-top: 16px;
}

.notes-section h4, .changes-list h4 {
  margin-bottom: 8px;
  color: #d29922;
}

.api-doc h3 {
  margin-bottom: 16px;
}

.api-doc h4 {
  margin: 16px 0 8px;
  color: #58a6ff;
}

.example-code {
  background: #0d1117;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  overflow-x: auto;
}

.log-analysis {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.root-cause {
  background: rgba(248, 81, 73, 0.1);
}

.analysis-section {
  background: #0d1117;
  border-radius: 8px;
  padding: 12px;
}

.analysis-section h4 {
  margin-bottom: 8px;
  color: #58a6ff;
}

.analysis-section code {
  color: #e6edf3;
}

.empty-result {
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

.empty-hint {
  font-size: 12px;
  margin-top: 8px;
}

.meta-info {
  margin-top: 8px;
  font-size: 13px;
  color: #8b949e;
}

.change-item {
  background: #0d1117;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 4px;
  display: flex;
  gap: 8px;
}

.change-type {
  color: #58a6ff;
  font-size: 12px;
}
</style>
