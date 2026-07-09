<template>
  <div class="layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <div class="logo-icon">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <rect width="28" height="28" rx="8" fill="url(#grad)"/>
              <path d="M8 14l4 4 8-8" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
              <defs>
                <linearGradient id="grad" x1="0" y1="0" x2="28" y2="28">
                  <stop stop-color="#58a6ff"/><stop offset="1" stop-color="#39d0d8"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div class="logo-text">
            <span class="logo-name">AI Workbench</span>
            <span class="logo-sub">智能代码助手</span>
          </div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/chat" class="nav-item" active-class="nav-item--active">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI 对话</span>
        </router-link>
        <router-link to="/knowledge" class="nav-item" active-class="nav-item--active">
          <el-icon><Document /></el-icon>
          <span>知识库</span>
        </router-link>
        <router-link to="/code-repository" class="nav-item" active-class="nav-item--active">
          <el-icon><FolderOpened /></el-icon>
          <span>代码仓库</span>
        </router-link>
        <router-link to="/code-ai" class="nav-item" active-class="nav-item--active">
          <el-icon><Cpu /></el-icon>
          <span>代码工具</span>
        </router-link>
        <router-link to="/snippets" class="nav-item" active-class="nav-item--active">
          <el-icon><Collection /></el-icon>
          <span>代码素材库</span>
        </router-link>
        <router-link to="/settings" class="nav-item" active-class="nav-item--active">
          <el-icon><Setting /></el-icon>
          <span>设置</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <el-avatar :size="32" style="background: linear-gradient(135deg,#58a6ff,#39d0d8)">
            {{ auth.userInfo?.username?.[0]?.toUpperCase() || 'A' }}
          </el-avatar>
          <div class="user-detail">
            <span class="user-name">{{ auth.userInfo?.nickname || auth.userInfo?.username }}</span>
            <span class="user-role">开发者</span>
          </div>
        </div>
        <el-button text @click="handleLogout" title="退出登录">
          <el-icon><SwitchButton /></el-icon>
        </el-button>
      </div>
    </aside>

    <!-- Main -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.layout { display: flex; height: 100vh; overflow: hidden; }

.sidebar {
  width: 220px; flex-shrink: 0;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex; flex-direction: column;
}

.sidebar-header { padding: 20px 16px; border-bottom: 1px solid var(--border-color); }

.logo { display: flex; align-items: center; gap: 10px; }
.logo-icon { width: 36px; height: 36px; flex-shrink: 0; }
.logo-text { display: flex; flex-direction: column; }
.logo-name { font-size: .9rem; font-weight: 700; color: var(--text-primary); }
.logo-sub { font-size: .65rem; color: var(--text-muted); letter-spacing: 1px; }

.sidebar-nav { flex: 1; padding: 12px 8px; display: flex; flex-direction: column; gap: 4px; }
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: var(--radius-sm);
  color: var(--text-secondary); text-decoration: none;
  font-size: .85rem; transition: all .2s;
}
.nav-item:hover { background: var(--bg-tertiary); color: var(--text-primary); }
.nav-item--active { background: rgba(88,166,255,.12); color: var(--accent-blue); border: 1px solid rgba(88,166,255,.2); }

.sidebar-footer {
  padding: 16px; border-top: 1px solid var(--border-color);
  display: flex; align-items: center; justify-content: space-between;
}
.user-info { display: flex; align-items: center; gap: 8px; }
.user-detail { display: flex; flex-direction: column; }
.user-name { font-size: .8rem; font-weight: 600; color: var(--text-primary); }
.user-role { font-size: .65rem; color: var(--text-muted); }

.main-content { flex: 1; overflow: hidden; display: flex; flex-direction: column; }
</style>
