from typing import Dict, List, Optional, Tuple
import hashlib
import json
from pathlib import Path
import numpy as np

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

class CodeVectorizer:
    """代码向量化服务 - 建立代码专属向量索引，支持混合检索"""

    COLLECTION_CODE_UNITS = "code_units"
    COLLECTION_SNIPPETS = "code_snippets"

    def __init__(self, persist_dir: str = None):
        if not CHROMADB_AVAILABLE:
            raise ImportError("请安装 chromadb: pip install chromadb")

        if persist_dir is None:
            persist_dir = Path.home() / ".ai_workbench" / "vectors"
        else:
            persist_dir = Path(persist_dir)

        persist_dir.mkdir(parents=True, exist_ok=True)

        self.chroma_client = chromadb.Client(Settings(
            persist_directory=str(persist_dir),
            anonymized_telemetry=False
        ))

        self.embedding_model = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception:
                try:
                    self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                except Exception:
                    self.embedding_model = None

        self._ensure_collections()

    def _ensure_collections(self):
        """确保向量集合存在"""
        try:
            self.code_units_collection = self.chroma_client.get_collection(self.COLLECTION_CODE_UNITS)
        except Exception:
            self.code_units_collection = self.chroma_client.create_collection(
                name=self.COLLECTION_CODE_UNITS,
                metadata={"description": "Code units index - function/class/interface/method"}
            )

        try:
            self.snippets_collection = self.chroma_client.get_collection(self.COLLECTION_SNIPPETS)
        except Exception:
            self.snippets_collection = self.chroma_client.create_collection(
                name=self.COLLECTION_SNIPPETS,
                metadata={"description": "Code snippets index"}
            )

    def _generate_embedding(self, texts: List[str]) -> List[List[float]]:
        """生成文本嵌入向量"""
        if self.embedding_model is None:
            return self._generate_fake_embedding(len(texts), 384)

        try:
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception:
            return self._generate_fake_embedding(len(texts), 384)

    def _generate_fake_embedding(self, n: int, dim: int) -> List[List[float]]:
        """生成伪嵌入向量（当无可用模型时）"""
        np.random.seed(42)
        embeddings = np.random.randn(n, dim).tolist()
        norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = (embeddings / norm).tolist()
        return embeddings

    def _make_doc_id(self, prefix: str, *parts: str) -> str:
        """生成唯一文档ID"""
        raw = ":".join(str(p) for p in parts)
        return f"{prefix}_{hashlib.md5(raw.encode()).hexdigest()[:12]}"

    def index_code_units(self, project_id: int, code_units: List[Dict],
                        file_tree: Dict = None) -> Dict:
        """索引代码单元"""
        if not code_units:
            return {"indexed": 0, "failed": 0}

        documents = []
        metadatas = []
        ids = []

        for unit in code_units:
            doc_content = self._build检索_document(unit)
            unit_id = self._make_doc_id(
                "unit",
                project_id,
                unit.get('file_path', ''),
                unit.get('name', ''),
                unit.get('start_line', 0)
            )

            documents.append(doc_content)
            metadatas.append({
                "project_id": project_id,
                "type": unit.get('type', 'unknown'),
                "name": unit.get('name', ''),
                "file_path": unit.get('file_path', ''),
                "start_line": unit.get('start_line', 0),
                "end_line": unit.get('end_line', 0),
                "signature": unit.get('signature', ''),
                "doc_comment": unit.get('doc_comment', ''),
                "language": self._detect_language_from_path(unit.get('file_path', '')),
            })
            ids.append(unit_id)

        embeddings = self._generate_embedding(documents)

        try:
            self.code_units_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            return {"indexed": len(ids), "failed": 0}
        except Exception as e:
            return {"indexed": 0, "failed": len(ids), "error": str(e)}

    def index_code_snippet(self, snippet_id: int, content: str,
                          language: str = None, tags: List[str] = None,
                          user_id: int = None) -> str:
        """索引代码片段"""
        doc_content = self._build_snippet_document(content, language, tags)
        snippet_id_str = self._make_doc_id("snippet", snippet_id)

        metadata = {
            "snippet_id": snippet_id,
            "language": language or "unknown",
            "tags": json.dumps(tags) if tags else "[]",
        }
        if user_id:
            metadata["user_id"] = user_id

        embedding = self._generate_embedding([doc_content])[0]

        self.snippets_collection.add(
            documents=[doc_content],
            metadatas=[metadata],
            ids=[snippet_id_str],
            embeddings=[embedding]
        )

        return snippet_id_str

    def _build检索_document(self, unit: Dict) -> str:
        """构建适合检索的文档内容"""
        parts = [
            f"类型: {unit.get('type', 'unknown')}",
            f"名称: {unit.get('name', '')}",
            f"文件: {unit.get('file_path', '')}",
            f"行号: {unit.get('start_line', 0)}-{unit.get('end_line', 0)}",
        ]

        if unit.get('signature'):
            parts.append(f"签名: {unit['signature']}")

        if unit.get('doc_comment'):
            parts.append(f"文档: {unit['doc_comment']}")

        if unit.get('parameters'):
            params = unit['parameters']
            if isinstance(params, list):
                if isinstance(params[0], dict):
                    param_str = ", ".join([f"{p.get('name', '')}: {p.get('type', '')}" for p in params])
                else:
                    param_str = ", ".join(str(p) for p in params)
                parts.append(f"参数: {param_str}")

        if unit.get('return_type'):
            parts.append(f"返回类型: {unit['return_type']}")

        if unit.get('dependencies'):
            deps = unit['dependencies']
            if isinstance(deps, list):
                deps = ", ".join(str(d) for d in deps[:10])
            parts.append(f"依赖: {deps}")

        content = unit.get('content', '')
        if content:
            parts.append(f"代码:\n{content[:3000]}")

        return "\n".join(parts)

    def _build_snippet_document(self, content: str, language: str = None,
                                tags: List[str] = None) -> str:
        """构建片段检索文档"""
        parts = [f"语言: {language or 'unknown'}"]

        if tags:
            parts.append(f"标签: {', '.join(tags)}")

        parts.append(f"代码:\n{content}")

        return "\n".join(parts)

    def search_code(self, query: str, project_id: int = None,
                   code_type: str = None, language: str = None,
                   top_k: int = 10, user_id: int = None) -> List[Dict]:
        """代码检索 - 支持按类型、语言、项目筛选"""

        where_filter = {}
        if project_id is not None:
            where_filter["project_id"] = project_id
        if code_type:
            where_filter["type"] = code_type
        if language:
            where_filter["language"] = language

        query_embedding = self._generate_embedding([query])[0]

        try:
            results = self.code_units_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter if where_filter else None,
                include=["documents", "metadatas", "distances"]
            )
        except Exception:
            return []

        formatted = []
        if results and results['ids'] and results['ids'][0]:
            for i, (doc, meta, dist) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                formatted.append({
                    "rank": i + 1,
                    "type": meta.get('type', 'unknown'),
                    "name": meta.get('name', ''),
                    "file_path": meta.get('file_path', ''),
                    "line": meta.get('start_line', 0),
                    "end_line": meta.get('end_line', 0),
                    "signature": meta.get('signature', ''),
                    "doc_comment": meta.get('doc_comment', ''),
                    "content": doc,
                    "relevance_score": round(1 - dist, 4) if dist is not None else 0,
                    "language": meta.get('language', '')
                })

        return formatted

    def search_by_function_name(self, func_name: str, project_id: int = None,
                                exact: bool = False) -> List[Dict]:
        """按函数名搜索"""
        if exact:
            query = f"function name: {func_name}"
        else:
            query = f"find function {func_name}"

        return self.search_code(query, project_id=project_id, code_type="function", top_k=10)

    def search_by_interface(self, api_path: str, project_id: int = None) -> List[Dict]:
        """按接口路径搜索"""
        return self.search_code(f"API endpoint route {api_path}", project_id=project_id, code_type="route")

    def search_snippets(self, query: str, language: str = None,
                       tags: List[str] = None, user_id: int = None,
                       top_k: int = 10) -> List[Dict]:
        """检索代码片段"""
        where_filter = {}
        if language:
            where_filter["language"] = language
        if user_id is not None:
            where_filter["user_id"] = user_id

        query_embedding = self._generate_embedding([query])[0]

        try:
            results = self.snippets_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter if where_filter else None,
                include=["documents", "metadatas", "distances"]
            )
        except Exception:
            return []

        formatted = []
        if results and results['ids'] and results['ids'][0]:
            for i, (doc, meta, dist) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                snippet_tags = meta.get('tags', '[]')
                if isinstance(snippet_tags, str):
                    snippet_tags = json.loads(snippet_tags)

                formatted.append({
                    "rank": i + 1,
                    "snippet_id": meta.get('snippet_id', 0),
                    "language": meta.get('language', 'unknown'),
                    "tags": snippet_tags,
                    "content": doc,
                    "relevance_score": round(1 - dist, 4) if dist is not None else 0,
                })

        return formatted

    def delete_project_vectors(self, project_id: int) -> int:
        """删除项目的所有向量"""
        try:
            all_data = self.code_units_collection.get(
                where={"project_id": project_id}
            )
            if all_data and all_data['ids']:
                self.code_units_collection.delete(ids=all_data['ids'])
                return len(all_data['ids'])
        except Exception:
            pass
        return 0

    def delete_snippet_vector(self, snippet_id: int) -> bool:
        """删除片段向量"""
        try:
            snippet_id_str = self._make_doc_id("snippet", snippet_id)
            self.snippets_collection.delete(ids=[snippet_id_str])
            return True
        except Exception:
            return False

    def get_collection_stats(self) -> Dict:
        """获取集合统计信息"""
        try:
            code_count = len(self.code_units_collection.get()['ids'])
        except Exception:
            code_count = 0

        try:
            snippet_count = len(self.snippets_collection.get()['ids'])
        except Exception:
            snippet_count = 0

        return {
            "code_units_count": code_count,
            "snippets_count": snippet_count,
            "embedding_model": "all-MiniLM-L6-v2" if self.embedding_model else "fallback",
        }

    def hybrid_search(self, query: str, project_id: int = None,
                     code_types: List[str] = None, top_k: int = 10) -> Dict:
        """混合检索 - 结合代码结构化信息和向量相似度"""

        results = {
            "by_name": [],
            "by_signature": [],
            "by_content": [],
            "final": []
        }

        results["by_name"] = self.search_code(
            query=f"name: {query}",
            project_id=project_id,
            code_type=code_types[0] if code_types and len(code_types) == 1 else None,
            top_k=top_k // 2
        )

        results["by_signature"] = self.search_code(
            query=f"signature {query}",
            project_id=project_id,
            code_type=code_types[0] if code_types and len(code_types) == 1 else None,
            top_k=top_k // 2
        )

        results["by_content"] = self.search_code(
            query=query,
            project_id=project_id,
            top_k=top_k
        )

        seen_ids = set()
        final_results = []

        for result_list in [results["by_name"], results["by_signature"], results["by_content"]]:
            for item in result_list:
                item_id = f"{item['file_path']}:{item['name']}:{item['line']}"
                if item_id not in seen_ids:
                    seen_ids.add(item_id)

                    score = item.get('relevance_score', 0)
                    if item in results["by_name"]:
                        score = score * 1.2
                    if item in results["by_signature"]:
                        score = score * 1.1

                    item['final_score'] = round(score, 4)
                    final_results.append(item)

        final_results.sort(key=lambda x: -x['final_score'])

        return {
            "by_name": results["by_name"],
            "by_signature": results["by_signature"],
            "by_content": results["by_content"],
            "final": final_results[:top_k]
        }

    @staticmethod
    def _detect_language_from_path(file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        from .code_parser import SUPPORTED_EXTENSIONS
        return SUPPORTED_EXTENSIONS.get(ext, 'unknown')

code_vectorizer_global: Optional[CodeVectorizer] = None

def get_code_vectorizer() -> CodeVectorizer:
    global code_vectorizer_global
    if code_vectorizer_global is None:
        code_vectorizer_global = CodeVectorizer()
    return code_vectorizer_global
