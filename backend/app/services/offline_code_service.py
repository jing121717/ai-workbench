import os
import json
import asyncio
import tempfile
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

@dataclass
class OfflineModelInfo:
    name: str
    size: str
    supports_code: bool
    supports_embedding: bool

class OfflineCodeService:
    """离线本地代码推理服务 - 支持CodeLlama、Qwen-Code等本地模型"""

    DEFAULT_MODELS = {
        "codellama:7b": {"supports_code": True, "supports_embedding": False, "size": "3.8GB"},
        "codellama:13b": {"supports_code": True, "supports_embedding": False, "size": "7GB"},
        "qwen:1.8b-code": {"supports_code": True, "supports_embedding": True, "size": "1GB"},
        "qwen:4b-code": {"supports_code": True, "supports_embedding": True, "size": "2.4GB"},
        "qwen:14b-code": {"supports_code": True, "supports_embedding": True, "size": "8GB"},
        "starcoder:1b": {"supports_code": True, "supports_embedding": True, "size": "600MB"},
        "starcoder:3b": {"supports_code": True, "supports_embedding": True, "size": "1.5GB"},
        "deepseek-coder:1.3b": {"supports_code": True, "supports_embedding": True, "size": "700MB"},
        "deepseek-coder:6.7b": {"supports_code": True, "supports_embedding": True, "size": "3.5GB"},
        "llama2:7b": {"supports_code": False, "supports_embedding": False, "size": "3.8GB"},
    }

    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        self.ollama_base_url = ollama_base_url
        self.code_model = os.environ.get("OFFLINE_CODE_MODEL", "codellama:7b")
        self.embedding_model = os.environ.get("OFFLINE_EMBEDDING_MODEL", "nomic-embed-text")
        self._fernet = None
        self._chroma_client = None

        if CRYPTO_AVAILABLE:
            self._init_encryption()
        if CHROMADB_AVAILABLE:
            self._init_vector_db()

    def _init_encryption(self):
        """初始化源码加密"""
        key_dir = Path.home() / ".ai_workbench"
        key_dir.mkdir(parents=True, exist_ok=True)
        key_path = key_dir / ".code_key"

        if key_path.exists():
            with open(key_path, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, 'wb') as f:
                f.write(key)
            key_path.chmod(0o600)

        self._fernet = Fernet(key)

    def _init_vector_db(self):
        """初始化本地向量数据库"""
        persist_dir = Path.home() / ".ai_workbench" / "offline_vectors"
        persist_dir.mkdir(parents=True, exist_ok=True)

        try:
            from chromadb.config import Settings
            self._chroma_client = chromadb.Client(Settings(
                persist_directory=str(persist_dir),
                anonymized_telemetry=False
            ))

            try:
                self._code_collection = self._chroma_client.get_collection("offline_code")
            except Exception:
                self._code_collection = self._chroma_client.create_collection(
                    name="offline_code",
                    metadata={"description": "Offline code index"}
                )
        except Exception as e:
            print(f"Warning: Could not initialize vector DB: {e}")

    def encrypt_source_code(self, code: str) -> str:
        """加密源码"""
        if self._fernet is None:
            raise RuntimeError("Encryption not available. Please install cryptography: pip install cryptography")
        return self._fernet.encrypt(code.encode()).decode()

    def decrypt_source_code(self, encrypted: str) -> str:
        """解密源码"""
        if self._fernet is None:
            raise RuntimeError("Encryption not available")
        return self._fernet.decrypt(encrypted.encode()).decode()

    async def check_ollama_status(self) -> Dict:
        """检查Ollama服务状态"""
        if not AIOHTTP_AVAILABLE:
            return {"available": False, "error": "aiohttp not installed"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_base_url}/api/tags", timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = [m['name'] for m in data.get('models', [])]
                        return {
                            "available": True,
                            "models": models,
                            "current_code_model": self.code_model,
                            "current_embedding_model": self.embedding_model
                        }
                    else:
                        return {"available": False, "error": f"HTTP {resp.status}"}
        except asyncio.TimeoutError:
            return {"available": False, "error": "Connection timeout. Is Ollama running?"}
        except Exception as e:
            return {"available": False, "error": str(e)}

    async def list_available_models(self) -> List[OfflineModelInfo]:
        """列出可用模型"""
        status = await self.check_ollama_status()

        if not status.get("available"):
            return []

        available = status.get("models", [])
        result = []

        for model_name, info in self.DEFAULT_MODELS.items():
            result.append(OfflineModelInfo(
                name=model_name,
                size=info["size"],
                supports_code=info["supports_code"],
                supports_embedding=info["supports_embedding"]
            ))

        return result

    async def pull_model(self, model_name: str) -> Dict:
        """拉取模型"""
        if not AIOHTTP_AVAILABLE:
            return {"success": False, "error": "aiohttp not installed"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_base_url}/api/pull",
                    json={"name": model_name},
                    timeout=aiohttp.ClientTimeout(total=3600)
                ) as resp:
                    if resp.status == 200:
                        return {"success": True, "message": f"Model {model_name} pulled successfully"}
                    else:
                        text = await resp.text()
                        return {"success": False, "error": f"HTTP {resp.status}: {text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def is_code_model_available(self) -> bool:
        """检查代码模型是否可用"""
        status = await self.check_ollama_status()
        if not status.get("available"):
            return False

        models = status.get("models", [])
        return any(
            self.code_model in m or
            'codellama' in m.lower() or
            'qwen' in m.lower() and 'code' in m.lower() or
            'deepseek' in m.lower() and 'coder' in m.lower() or
            'starcoder' in m.lower()
            for m in models
        )

    async def analyze_code_offline(self, code: str, language: str) -> Dict:
        """离线代码分析"""
        if not await self.is_code_model_available():
            return {
                "success": False,
                "error": "本地代码模型不可用，请检查 Ollama 服务是否启动，或配置正确的模型",
                "hint": "运行: ollama pull codellama:7b"
            }

        prompt = f"""分析以下{language}代码，返回JSON格式的问题列表：
代码：
```
{code}
```

JSON格式（必须严格JSON，不要有其他内容）：
{{"issues": [{{"severity": "high|medium|low", "description": "问题描述", "line": 行号, "type": "问题类型"}}], "summary": "总体评价", "score": 分数}}"""

        return await self._call_ollama(prompt)

    async def refactor_code_offline(self, code: str, language: str,
                                   refactor_type: str = "readability") -> Dict:
        """离线代码重构"""
        if not await self.is_code_model_available():
            return {"success": False, "error": "本地代码模型不可用"}

        type_prompts = {
            "readability": "优化代码可读性，重命名变量，增强注释，拆分过长函数",
            "performance": "优化性能和内存使用，减少不必要的计算，优化算法复杂度",
            "security": "增强安全性，添加输入验证，防止注入攻击，使用安全API",
            "modularity": "拆分大函数为小函数，提高模块化程度，降低耦合度"
        }

        prompt = f"""作为代码重构专家，重构以下{language}代码，{type_prompts.get(refactor_type, type_prompts['readability'])}。

原始代码：
```{language}
{code}
```

返回JSON格式（必须严格JSON）：
{{"refactored_code": "重构后的完整代码", "changes": ["改动1", "改动2"], "benefits": ["收益1"]}}"""

        return await self._call_ollama(prompt)

    async def generate_test_offline(self, code: str, language: str,
                                   framework: str = "pytest") -> Dict:
        """离线生成单元测试"""
        if not await self.is_code_model_available():
            return {"success": False, "error": "本地代码模型不可用"}

        prompt = f"""为以下{language}代码生成{frequency}单元测试。

代码：
```{language}
{code}
```

返回JSON格式（必须严格JSON）：
{{"test_code": "完整的测试代码", "coverage_notes": "覆盖率说明"}}"""

        return await self._call_ollama(prompt)

    async def explain_code_offline(self, code: str, language: str) -> Dict:
        """离线代码解释"""
        if not await self.is_code_model_available():
            return {"success": False, "error": "本地代码模型不可用"}

        prompt = f"""详细解释以下{language}代码的功能和工作原理。

代码：
```{language}
{code}
```

返回JSON格式（必须严格JSON）：
{{"explanation": "详细解释", "key_points": ["要点1", "要点2"], "input_output": "输入输出说明"}}"""

        return await self._call_ollama(prompt)

    async def complete_code_offline(self, code: str, language: str,
                                   context: str = "") -> Dict:
        """代码补全"""
        if not await self.is_code_model_available():
            return {"success": False, "error": "本地代码模型不可用"}

        prompt = f"""根据上下文补全以下{language}代码，只返回需要添加的部分，不要重复已有代码。

已有代码：
```{language}
{code}
```

上下文说明：{context or '无特殊要求'}

返回JSON格式（必须严格JSON）：
{{"completed_code": "补全后的完整代码或新增部分"}}"""

        return await self._call_ollama(prompt)

    async def _call_ollama(self, prompt: str, model: str = None,
                          temperature: float = 0.3,
                          max_tokens: int = 2048) -> Dict:
        """调用 Ollama 本地模型"""
        if not AIOHTTP_AVAILABLE:
            return {"error": "aiohttp not available"}

        model = model or self.code_model

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_ctx": 4096,
                            "max_tokens": max_tokens
                        }
                    },
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response_text = data.get('response', '')

                        try:
                            json_match = None
                            for pattern in [r'\{[\s\S]*\}', r'\[[\s\S]*\]']:
                                match = self._extract_json(response_text, pattern)
                                if match:
                                    json_match = match
                                    break

                            if json_match:
                                return json.loads(json_match)
                            else:
                                return {"raw_response": response_text}
                        except json.JSONDecodeError:
                            return {"raw_response": response_text}
                    else:
                        text = await resp.text()
                        return {"error": f"HTTP {resp.status}: {text}"}
        except asyncio.TimeoutError:
            return {"error": "Request timeout. Try a smaller model or reduce max_tokens."}
        except Exception as e:
            return {"error": str(e)}

    def _extract_json(self, text: str, pattern: str) -> Optional[str]:
        """提取JSON字符串"""
        import re
        match = re.search(pattern, text)
        if match:
            return match.group()
        return None

    def index_code_for_offline(self, project_id: int, code_units: List[Dict]) -> int:
        """为离线模式索引代码"""
        if self._code_collection is None:
            return 0

        count = 0
        for unit in code_units:
            doc_id = hashlib.md5(
                f"{project_id}:{unit.get('file_path', '')}:{unit.get('name', '')}".encode()
            ).hexdigest()

            content = self._build_offline_doc(unit)

            try:
                self._code_collection.add(
                    documents=[content],
                    metadatas=[{
                        "project_id": project_id,
                        "type": unit.get('type', ''),
                        "name": unit.get('name', ''),
                        "file_path": unit.get('file_path', '')
                    }],
                    ids=[doc_id]
                )
                count += 1
            except Exception:
                continue

        return count

    def _build_offline_doc(self, unit: Dict) -> str:
        """构建离线检索文档"""
        parts = [
            f"类型: {unit.get('type', '')}",
            f"名称: {unit.get('name', '')}",
            f"文件: {unit.get('file_path', '')}",
        ]

        if unit.get('signature'):
            parts.append(f"签名: {unit['signature']}")

        if unit.get('content'):
            parts.append(f"代码:\n{unit['content'][:2000]}")

        return "\n".join(parts)

    def search_offline_index(self, query: str, project_id: int = None, top_k: int = 5) -> List[Dict]:
        """搜索离线索引"""
        if self._code_collection is None:
            return []

        where_filter = {"project_id": project_id} if project_id else None

        try:
            results = self._code_collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_filter
            )

            formatted = []
            if results and results['ids'] and results['ids'][0]:
                for doc, meta, dist in zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                ):
                    formatted.append({
                        "name": meta.get('name', ''),
                        "type": meta.get('type', ''),
                        "file_path": meta.get('file_path', ''),
                        "content": doc,
                        "score": round(1 - dist, 4) if dist else 0
                    })

            return formatted
        except Exception:
            return []

offline_code_service_global: Optional[OfflineCodeService] = None

def get_offline_code_service() -> OfflineCodeService:
    global offline_code_service_global
    if offline_code_service_global is None:
        offline_code_service_global = OfflineCodeService()
    return offline_code_service_global
