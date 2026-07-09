from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from typing import Dict, List, Optional
from pydantic import BaseModel
import json
import asyncio

router = APIRouter(prefix="/ide", tags=["IDE联动"])

class IDEIntegrationManager:
    """IDE集成管理器"""

    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.user_sessions: Dict[int, dict] = {}

    async def connect_ide(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_sessions[user_id] = {
            "connected_at": asyncio.get_event_loop().time(),
            "files_modified": []
        }

    def disconnect_ide(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]

    async def send_to_ide(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
                return True
            except Exception:
                return False
        return False

    async def broadcast_to_user(self, user_id: int, message: dict):
        await self.send_to_ide(user_id, message)

ide_manager = IDEIntegrationManager()

@router.websocket("/ws/{user_id}")
async def ide_websocket(websocket: WebSocket, user_id: int):
    """IDE WebSocket连接"""
    await ide_manager.connect_ide(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()

            msg_type = data.get("type")

            if msg_type == "code_save":
                await handle_code_save(user_id, data)
            elif msg_type == "query_kb":
                await handle_kb_query(user_id, data)
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            elif msg_type == "sync_status":
                await handle_sync_status(user_id, data)

    except WebSocketDisconnect:
        ide_manager.disconnect_ide(user_id)
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
        ide_manager.disconnect_ide(user_id)

async def handle_code_save(user_id: int, data: dict):
    """处理IDE文件保存事件"""
    from app.services.code_parser import CodeRepositoryParser
    from app.services.code_vectorizer import get_code_vectorizer

    file_path = data.get("file_path")
    content = data.get("content", "")
    language = data.get("language", "")

    parser = CodeRepositoryParser()
    units = parser.parse_code_string(content, language, file_path)

    try:
        vectorizer = get_code_vectorizer()
        result = vectorizer.index_code_units(user_id, [u.__dict__ for u in units])

        await ide_manager.send_to_ide(user_id, {
            "type": "code_sync_result",
            "file_path": file_path,
            "indexed": result.get("indexed", 0),
            "success": True
        })
    except Exception as e:
        await ide_manager.send_to_ide(user_id, {
            "type": "code_sync_result",
            "file_path": file_path,
            "success": False,
            "error": str(e)
        })

async def handle_kb_query(user_id: int, data: dict):
    """处理IDE知识库查询"""
    from app.services.code_vectorizer import get_code_vectorizer

    query = data.get("query", "")
    file_path = data.get("file_path")
    project_id = data.get("project_id")

    try:
        vectorizer = get_code_vectorizer()
        language = parser.detect_language_from_path(file_path) if file_path else None

        results = vectorizer.search_code(
            query=query,
            project_id=project_id,
            language=language,
            top_k=10
        )

        await ide_manager.send_to_ide(user_id, {
            "type": "kb_results",
            "query": query,
            "results": results
        })
    except Exception as e:
        await ide_manager.send_to_ide(user_id, {
            "type": "kb_results",
            "query": query,
            "results": [],
            "error": str(e)
        })

async def handle_sync_status(user_id: int, data: dict):
    """处理同步状态查询"""
    await ide_manager.send_to_ide(user_id, {
        "type": "sync_status",
        "connected": True,
        "session": ide_manager.user_sessions.get(user_id, {})
    })

@router.post("/query")
async def ide_query_knowledge(
    query: str,
    project_id: Optional[int] = None,
    file_path: Optional[str] = None,
    language: Optional[str] = None,
    top_k: int = 10
):
    """IDE查询知识库接口"""
    from app.services.code_vectorizer import get_code_vectorizer

    try:
        vectorizer = get_code_vectorizer()

        if not language and file_path:
            from app.services.code_vectorizer import CodeVectorizer
            language = CodeVectorizer._detect_language_from_path(file_path)

        results = vectorizer.search_code(
            query=query,
            project_id=project_id,
            language=language,
            top_k=top_k
        )

        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/sync-file")
async def ide_sync_file(
    file_path: str,
    content: str,
    language: Optional[str] = None,
    project_id: Optional[int] = None
):
    """同步文件到知识库"""
    from app.services.code_parser import CodeRepositoryParser
    from app.services.code_vectorizer import get_code_vectorizer

    if not language:
        from app.services.code_vectorizer import CodeVectorizer
        language = CodeVectorizer._detect_language_from_path(file_path)

    parser = CodeRepositoryParser()
    units = parser.parse_code_string(content, language, file_path)

    try:
        vectorizer = get_code_vectorizer()
        unit_dicts = [u.__dict__ for u in units]

        if project_id:
            for u in unit_dicts:
                u['project_id'] = project_id

        result = vectorizer.index_code_units(project_id or 0, unit_dicts)

        return {
            "success": True,
            "indexed": result.get("indexed", 0),
            "file_path": file_path
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/batch-sync")
async def ide_batch_sync(
    files: List[dict],
    project_id: int
):
    """批量同步文件"""
    from app.services.code_parser import CodeRepositoryParser
    from app.services.code_vectorizer import get_code_vectorizer

    parser = CodeRepositoryParser()
    vectorizer = get_code_vectorizer()

    total_indexed = 0
    errors = []

    for file_info in files:
        try:
            content = file_info.get("content", "")
            file_path = file_info.get("file_path", "")
            language = file_info.get("language") or CodeVectorizer._detect_language_from_path(file_path)

            units = parser.parse_code_string(content, language, file_path)
            unit_dicts = [u.__dict__ for u in units]

            for u in unit_dicts:
                u['project_id'] = project_id

            result = vectorizer.index_code_units(project_id, unit_dicts)
            total_indexed += result.get("indexed", 0)
        except Exception as e:
            errors.append({"file": file_info.get("file_path"), "error": str(e)})

    return {
        "total_indexed": total_indexed,
        "total_files": len(files),
        "errors": errors
    }

@router.get("/status/{user_id}")
async def get_ide_status(user_id: int):
    """获取IDE连接状态"""
    return {
        "connected": user_id in ide_manager.active_connections,
        "session": ide_manager.user_sessions.get(user_id, {})
    }

@router.post("/notify")
async def send_ide_notification(
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "info"
):
    """向IDE发送通知"""
    success = await ide_manager.send_to_ide(user_id, {
        "type": "notification",
        "title": title,
        "message": message,
        "notification_type": notification_type
    })

    if not success:
        raise HTTPException(404, "IDE未连接")

    return {"success": True}

IDE_PLUGIN_OPENAPI = """
# AI Workbench VSCode 插件接口文档

## 安装
```bash
ext install ai-workbench.vscode-extension
```

## 配置
在VSCode设置中配置服务器地址：
```json
{
  "aiWorkbench.serverUrl": "http://localhost:8000",
  "aiWorkbench.apiKey": "your-api-key"
}
```

## 功能

### 1. 代码知识库查询
在编辑器中选中代码，右键选择"查询AI知识库"

### 2. 实时文件同步
保存文件时自动同步到知识库

### 3. AI代码补全
输入注释自动生成代码建议

### 4. 错误诊断
代码错误时显示AI分析结果

## API列表

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/v1/ide/query | POST | 查询知识库 |
| /api/v1/ide/sync-file | POST | 同步文件 |
| /api/v1/ide/ws/{user_id} | WebSocket | 实时通信 |
| /api/v1/ide/status/{user_id} | GET | 连接状态 |

## WebSocket消息格式

### 发送
```json
{"type": "code_save", "file_path": "main.py", "content": "...", "language": "python"}
{"type": "query_kb", "query": "查找用户认证函数", "file_path": "auth.py"}
```

### 接收
```json
{"type": "code_sync_result", "file_path": "main.py", "indexed": 5, "success": true}
{"type": "kb_results", "query": "...", "results": [...]}
```
"""
