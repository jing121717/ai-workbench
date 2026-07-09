# 🤖 AI Workbench

> AI Workbench is a full-stack AI coding workspace with a FastAPI backend, a Vue 3 web client, and a PySide6 desktop client. It supports account authentication, streaming chat, local knowledge-base search, code-assistant features, Docker-based deployment, and desktop packaging with PyInstaller.

---

## 📋 Features

### 🌐 Web Frontend (Vue3 + Element Plus)
- ✅ JWT user login / registration
- ✅ SSE server-side streaming conversation with real-time typewriter effect
- ✅ Multi-session management (create / switch / delete / rename)
- ✅ PDF / TXT document upload, build private RAG knowledge base
- ✅ Shortcut commands and question prompts
- ✅ Dark tech-style UI with smooth animations

### ⚡ Backend (FastAPI + LangChain)
- ✅ JWT Bearer Token authentication
- ✅ RESTful API + SSE streaming output interface
- ✅ Redis token bucket rate limiting
- ✅ Chroma vector database + Qwen Embedding RAG retrieval
- ✅ 23 preset programming knowledge bases (offline available)
- ✅ PDF parsing and vectorized storage
- ✅ Global exception handling and unified response format
- ✅ CORS cross-origin configuration

### 🖥️ Desktop Client (PySide6)
- ✅ Three-column layout (session list / conversation / knowledge base + settings)
- ✅ QThread multithread isolation, network requests won’t block UI
- ✅ SQLite local session cache (offline available)
- ✅ Offline AI Q&A with preset knowledge base
- ✅ PDF/TXT document upload (multithreaded)
- ✅ One-click PyInstaller packaging into standalone EXE
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

## 📁Project Structure

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

## 🚀  Local Startup Steps 

### Method 1: Docker Deployment (Recommended)

```bash
# Clone the project
git clone https://github.com/jing121717/ai-workbench.git
cd ai-workbench

# Start all services (MySQL + Redis + Backend + Frontend) 
docker compose up -d

# Access
# Frontend page：http://localhost:5173
# Backend API:http://localhost:8000
#  Default account：admin / Admin@123456
```

### Method 2: Local Development

**1. Install Dependencies**
```bash
# Backend
cd backend
pip install -r ../requirements.txt

# Frontend
cd frontend
npm install
```

**2. Initialize the Database**
```bash
cd backend
python init_db.py
# Create an admin account: admin / Admin@123456
```

**3. Start the Backend**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**4. Start the Frontend**
```bash
cd frontend
npm run dev -- --host 0.0.0.0
```

**5. One-Click Script (Linux/macOS)**
```bash
bash scripts/start_all.sh
```

---

## 🐳 Docker Deployment

### Prerequisites
- Docker Desktop installed
- Ports 8000, 3306, 6379, 5173 not in use

### Start Command
```bash
docker compose up -d
```

### View Logs
```bash
docker compose logs -f backend
docker compose logs -f frontend
```

### Stop Services
```bash
docker compose down
```

---

## 🖥️ Desktop EXE Packaging (Windows)

### Method 1: Using Script (Recommended)

```bat
# 1. Create a virtual environment and install dependencies
scriptssetup_gui_env.bat

# 2. Package EXE (generates guidistAIWorkbenchAIWorkbench.exe)
scriptspackage_gui.bat
```
### Method 2: Manual Packaging

```bat
# Install dependencies
pip install pyinstaller pyside6 requests

# Run packaging
cd gui
pyinstaller ai_workbench.spec --clean

# EXE location: gui/dist/AIWorkbench/AIWorkbench.exe
```

### Using the EXE (No Python Environment Needed)

1. Go to the `guidistAIWorkbench` directory
2. Double-click `AIWorkbench.exe` to run
3. First-time use:
- Confirm the backend address in "Settings" (default is `http://127.0.0.1:8000`)
- Or enter `true` to enable offline mode to directly ask questions based on the preset knowledge base
4. Default offline account: admin / Admin@123456

---

## 🔑 Default Accounts

| Platform | Username | Password |
|---------|---------|---------|
| Web Admin / Web | `admin` | `Admin@123456` |
| Desktop Client | Same as above | Same as above |

---

## 🌐 API Endpoints Overview

| Method | Path | Description |
|--------|------|------------|
| POST | `/api/v1/auth/login` | User login, returns JWT |
| POST | `/api/v1/auth/register` | User registration |
| GET | `/api/v1/auth/me` | Get current user info |
| GET | `/api/v1/chat/sessions` | Get list of chat sessions |
| POST | `/api/v1/chat/sessions` | Create a new session |
| DELETE | `/api/v1/chat/sessions/{id}` | Delete a session |
| GET | `/api/v1/chat/sessions/{id}/messages` | Get messages of a session |
| POST | `/api/v1/chat/stream` | SSE streaming chat |
| GET | `/api/v1/knowledge/documents` | Get list of documents |
| POST | `/api/v1/knowledge/upload` | Upload a document |
| DELETE | `/api/v1/knowledge/documents/{id}` | Delete a document |
| GET | `/api/health` | Health check |

---
## ⚙️ Environment Variables

Copy `.env.example` to `.env` and modify:

```bash
DATABASE_URL=mysql+pymysql://root:Root@123456@localhost:3306/ai_workbench
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production
QWEN_MODEL_NAME=Qwen/Qwen2.5-1.5B-Instruct
EMBEDDING_MODEL_NAME=BAAI/bge-small-zh-v1.5
MODEL_DEVICE=cpu
```

---

## 📚 Built-in Knowledge Base

The system comes with 23 common programming Q&As, covering the following areas:

| Category | Content |
|---------|---------|
| 🏆 Git | Common commands, conflict resolution, SSH Key, workflow, undo operations |
| 🐳 Docker | Common commands, Dockerfile best practices, Compose orchestration, networking & volumes |
| 🗄️ SQL | Queries, index optimization, transaction locks, interview questions |
| 🐍 Python | Decorators, async/await, error handling, performance optimization, design patterns |
| 🏗️ System Design | High-concurrency architectures, RESTful API, microservices, message queues |
| 🎨 Frontend | ES6+ syntax, Vue3 Composition API, TypeScript, performance optimization |
| ⚡ Redis | Data structures, caching strategies, distributed locks |
| 🌐 Networking | HTTP status codes, WebSocket, TLS handshake, TCP three-way handshake |
| 🚀 DevOps | CI/CD pipeline design |
| ✅ Best Practices | Code review essentials, troubleshooting, technical proposal writing |

---

## ✨ Project Highlights

1. **Frontend-Backend Separation + Dual-End Sync**: The web and desktop versions share the same backend, with real-time data sync.
2. **RAG Knowledge Base**: Supports PDF/TXT uploads to build a private vector knowledge base.
3. **Offline-First**: The desktop app comes with a preloaded knowledge base, answering common programming questions without the internet.
4. **Streaming Output**: SSE creates a typewriter effect, giving a ChatGPT-like experience.
5. **Multi-Thread Isolation**: Uses QThread in PySide6 to avoid UI lag.
6. **Containerized Deployment**: Docker Compose allows one-click launch of all dependencies.
7. **Offline Capable**: Packaged into an EXE with PyInstaller, no Python setup needed.
