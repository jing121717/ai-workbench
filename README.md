# 🤖 AI Workbench · 全栈 AI 智能代码工作台

> 一套完整的前后端分离架构项目，包含 **FastAPI 后端**、**Vue3 网页端**、**PySide6 桌面客户端**，实现 **Web / 桌面双端数据互通**，支持 **Docker 容器化部署**与**桌面端 EXE 离线打包**，可直接用于毕设 / 简历项目。

---

## 📋 功能清单

### 🌐 Web 前端（Vue3 + Element Plus）
- ✅ JWT 用户登录 / 注册
- ✅ SSE 服务端流式对话，实时打字机效果
- ✅ 多会话管理（创建 / 切换 / 删除 / 重命名）
- ✅ PDF / TXT 文档上传，构建私有 RAG 知识库
- ✅ 快捷指令与问题提示
- ✅ 深色科技风格 UI，流畅动画

### ⚡ 后端（FastAPI + LangChain）
- ✅ JWT Bearer Token 认证
- ✅ RESTful API + SSE 流式输出接口
- ✅ Redis 令牌桶限流
- ✅ Chroma 向量数据库 + Qwen Embedding RAG 检索
- ✅ 预置 23 条编程知识库（离线可用）
- ✅ PDF 文件解析与向量化入库
- ✅ 全局异常捕获与统一响应格式
- ✅ CORS 跨域配置

### 🖥️ 桌面客户端（PySide6）
- ✅ 三栏布局（会话列表 / 对话 / 知识库+设置）
- ✅ QThread 多线程隔离，网络请求不卡 UI
- ✅ SQLite 本地会话缓存（离线可用）
- ✅ 预置知识库离线 AI 问答
- ✅ PDF/TXT 文档上传（多线程）
- ✅ 一键 PyInstaller 打包为独立 EXE

---

## 🏗️ 技术架构

```
┌──────────────────────────────────────────────────────────────┐
│                       客户端层                                 │
│  ┌─────────────────────┐         ┌──────────────────────────┐  │
│  │   Vue3 网页端       │         │   PySide6 桌面客户端    │  │
│  │   (http://localhost:5173)   │   (独立 EXE，双击即运行)  │  │
│  └────────┬───────────┘         └──────────┬─────────────┘  │
│           │  SSE / REST                          │           │
│           │  JWT Bearer                          │           │
└───────────┼───────────────────────────────────────┼───────────┘
            │                                       │
            ▼                                       ▼
┌──────────────────────────────────────────────────────────────┐
│                      FastAPI 后端                            │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐   │
│  │  认证接口     │  │  对话接口     │  │  知识库接口     │   │
│  │  /auth/*     │  │  /chat/*     │  │  /knowledge/*  │   │
│  └──────────────┘  └──────────────┘  └────────────────┘   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐   │
│  │  Redis 限流  │  │ LangChain   │  │  Chroma 向量库  │   │
│  │  令牌桶       │  │  Qwen LLM  │  │  RAG 检索      │   │
│  └──────────────┘  └──────────────┘  └────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
ai-workbench/
├─ backend/                    # FastAPI 后端
│   ├─ app/
│   │   ├─ api/v1/endpoints/  # API 路由（auth/chat/knowledge）
│   │   ├─ core/               # 配置/安全/异常/限流
│   │   ├─ db/                 # SQLAlchemy 会话
│   │   ├─ models/             # ORM 模型
│   │   ├─ repositories/       # 数据仓储层
│   │   ├─ schemas/            # Pydantic 请求/响应模型
│   │   ├─ services/           # 业务逻辑层（RAG/对话/认证）
│   │   └─ main.py             # FastAPI 应用入口
│   ├─ knowledge_base.py       # 预置 23 条编程知识库
│   └─ init_db.py              # 数据库初始化脚本
│
├─ frontend/                   # Vue3 前端
│   ├─ src/
│   │   ├─ api/                # Axios HTTP 客户端
│   │   ├─ stores/             # Pinia 状态管理（auth/chat）
│   │   ├─ types/              # TypeScript 类型定义
│   │   ├─ views/              # 页面组件（登录/对话/知识库/设置）
│   │   ├─ router.ts          # Vue Router 路由配置
│   │   ├─ App.vue              # 根组件（布局）
│   │   └─ main.ts             # 应用入口
│   └─ vite.config.ts          # Vite 构建配置
│
├─ gui/                        # PySide6 桌面客户端
│   ├─ app/
│   │   ├─ api_client.py       # HTTP 客户端（复用后端接口）
│   │   ├─ cache.py             # SQLite 本地会话缓存
│   │   ├─ main_window.py       # 主窗口（三栏布局）
│   │   ├─ offline_service.py   # 离线 AI 问答服务
│   │   └─ workers.py           # QThread 多线程工作者
│   ├─ main.py                 # 桌面端入口
│   └─ ai_workbench.spec       # PyInstaller 打包配置
│
├─ docs/
│   └─ screenshots/            # 项目截图
│
├─ scripts/
│   ├─ start_all.sh            # Linux/macOS 一键启动脚本
│   ├─ start_all.bat           # Windows 一键启动脚本
│   ├─ package_gui.bat        # Windows EXE 打包脚本
│   ├─ setup_gui_env.bat      # Windows 桌面端环境创建
│   └─ package_gui.sh         # Linux/macOS EXE 打包脚本
│
├─ docker-compose.yml           # Docker 编排（后端+MySQL+Redis）
├─ Dockerfile                   # 后端容器镜像
├─ requirements.txt             # Python 依赖
├─ .env.example                 # 环境变量模板
├─ .gitignore                   # Git 忽略配置
└─ README.md                    # 项目文档（本文件）
```

---

## 🚀 本地启动步骤

### 方式一：Docker 部署（推荐）

```bash
# 克隆项目
git clone https://github.com/jing121717/ai-workbench.git
cd ai-workbench

# 启动所有服务（MySQL + Redis + 后端 + 前端）
docker compose up -d

# 访问
# 前端页面：http://localhost:5173
# 后端 API：http://localhost:8000
# 默认账号：admin / Admin@123456
```

### 方式二：本地开发

**1. 安装依赖**
```bash
# 后端
cd backend
pip install -r ../requirements.txt

# 前端
cd frontend
npm install
```

**2. 初始化数据库**
```bash
cd backend
python init_db.py
# 创建管理员账号：admin / Admin@123456
```

**3. 启动后端**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**4. 启动前端**
```bash
cd frontend
npm run dev -- --host 0.0.0.0
```

**5. 一键脚本（Linux/macOS）**
```bash
bash scripts/start_all.sh
```

---

## 🐳 Docker 部署

### 前提条件
- Docker Desktop 已安装
- 端口 8000、3306、6379、5173 未被占用

### 启动命令
```bash
docker compose up -d
```

### 查看日志
```bash
docker compose logs -f backend
docker compose logs -f frontend
```

### 停止服务
```bash
docker compose down
```

---

## 🖥️ 桌面端 EXE 打包（Windows）

### 方式一：使用脚本（推荐）

```bat
# 1. 创建虚拟环境并安装依赖
scripts\setup_gui_env.bat

# 2. 打包 EXE（生成 gui\dist\AIWorkbench\AIWorkbench.exe）
scripts\package_gui.bat
```

### 方式二：手动打包

```bat
# 安装依赖
pip install pyinstaller pyside6 requests

# 执行打包
cd gui
pyinstaller ai_workbench.spec --clean

# EXE 位置：gui/dist/AIWorkbench/AIWorkbench.exe
```

### 使用 EXE（无需 Python 环境）

1. 进入 `gui\dist\AIWorkbench\` 目录
2. 双击 `AIWorkbench.exe` 即可运行
3. 首次使用：
   - 在"设置"中确认后端地址（默认 `http://127.0.0.1:8000`）
   - 或输入 `true` 启用离线模式，直接基于预置知识库问答
4. 默认离线账号：admin / Admin@123456

---

## 🔑 默认账号

| 平台 | 用户名 | 密码 |
|------|--------|------|
| Web 后台 / 网页 | `admin` | `Admin@123456` |
| 桌面客户端 | 同上 | 同上 |

---

## 🌐 API 接口一览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 用户登录，返回 JWT |
| POST | `/api/v1/auth/register` | 用户注册 |
| GET | `/api/v1/auth/me` | 获取当前用户信息 |
| GET | `/api/v1/chat/sessions` | 获取会话列表 |
| POST | `/api/v1/chat/sessions` | 创建新会话 |
| DELETE | `/api/v1/chat/sessions/{id}` | 删除会话 |
| GET | `/api/v1/chat/sessions/{id}/messages` | 获取会话消息 |
| POST | `/api/v1/chat/stream` | SSE 流式对话 |
| GET | `/api/v1/knowledge/documents` | 获取文档列表 |
| POST | `/api/v1/knowledge/upload` | 上传文档 |
| DELETE | `/api/v1/knowledge/documents/{id}` | 删除文档 |
| GET | `/api/health` | 健康检查 |

---

## ⚙️ 环境变量

复制 `.env.example` 为 `.env` 并修改：

```bash
DATABASE_URL=mysql+pymysql://root:Root@123456@localhost:3306/ai_workbench
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production
QWEN_MODEL_NAME=Qwen/Qwen2.5-1.5B-Instruct
EMBEDDING_MODEL_NAME=BAAI/bge-small-zh-v1.5
MODEL_DEVICE=cpu
```

---

## 📚 预置知识库

系统内置 23 条常见编程问答，覆盖以下方向：

| 分类 | 内容 |
|------|------|
| 🏆 Git | 常用命令、冲突解决、SSH Key、工作流、撤销操作 |
| 🐳 Docker | 常用命令、Dockerfile 最佳实践、Compose 编排、网络与卷 |
| 🗄️ SQL | 查询语句、索引优化、事务锁、面试题 |
| 🐍 Python | 装饰器、async/await、报错处理、性能优化、设计模式 |
| 🏗️ 系统设计 | 高并发架构、RESTful API、微服务、消息队列 |
| 🎨 前端 | ES6+ 语法、Vue3 组合式 API、TypeScript、性能优化 |
| ⚡ Redis | 数据结构、缓存策略、分布式锁 |
| 🌐 网络 | HTTP 状态码、WebSocket、TLS 握手、TCP 三次握手 |
| 🚀 DevOps | CI/CD 流水线设计 |
| ✅ 最佳实践 | 代码审查要点、故障排查、技术方案写作 |

---

## ✨ 项目亮点

1. **前后端分离 + 双端互通**：Web 端和桌面端共用同一后端，数据实时同步
2. **RAG 知识库**：支持 PDF/TXT 上传，构建私有向量知识库
3. **离线优先**：桌面端预置知识库，无网络也能回答常见编程问题
4. **流式输出**：SSE 实现打字机效果，用户体验接近 ChatGPT
5. **多线程隔离**：PySide6 使用 QThread，避免 UI 卡顿
6. **容器化部署**：Docker Compose 一键启动全套依赖
7. **可离线运行**：PyInstaller 打包为 EXE，无需配置 Python 环境

---

## 📝 License

MIT License · 可自由使用于毕设、简历项目、开源学习
