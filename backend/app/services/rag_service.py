import json
import time
import logging
from typing import Generator
from backend.app.core.config import settings
from backend.knowledge_base import search_knowledge, KNOWLEDGE_BASE

logger = logging.getLogger(__name__)


class RagService:
    def __init__(self) -> None:
        self._llm = None
        self._embeddings = None
        self._vectorstore = None
        self._initialized = False

    def _ensure_llm(self):
        if self._llm is not None:
            return self._llm
        try:
            from langchain_huggingface import HuggingFacePipeline
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
            model_name = settings.qwen_model_name
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
            pipe = pipeline("text-generation", model=model, tokenizer=tokenizer,
                            max_new_tokens=512, temperature=0.3)
            self._llm = HuggingFacePipeline(pipeline=pipe)
            logger.info("Qwen 模型加载成功")
        except Exception as exc:
            logger.warning("Qwen 模型加载失败，使用预置知识库：%s", exc)
            self._llm = None
        return self._llm

    def _ensure_embeddings(self):
        if self._embeddings is not None:
            return self._embeddings
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            self._embeddings = HuggingFaceEmbeddings(
                model_name=settings.embedding_model_name,
                model_kwargs={"device": settings.model_device},
            )
            logger.info("向量模型加载成功")
        except Exception as exc:
            logger.warning("向量模型加载失败：%s", exc)
            self._embeddings = None
        return self._embeddings

    def _get_vectorstore(self, user_id: int):
        if self._vectorstore is not None:
            return self._vectorstore
        emb = self._ensure_embeddings()
        if emb is None:
            return None
        try:
            from langchain_community.vectorstores import Chroma
            self._vectorstore = Chroma(
                collection_name=f"user_{user_id}_knowledge",
                persist_directory=str(settings.vector_path),
                embedding_function=emb,
            )
        except Exception as exc:
            logger.warning("向量数据库加载失败：%s", exc)
            self._vectorstore = None
        return self._vectorstore

    def _build_prompt(self, context: str, question: str) -> str:
        if context:
            return (
                "你是一个专业的 AI 编程助手。请结合上下文进行回答。\n\n"
                f"上下文:\n{context}\n\n"
                f"问题: {question}\n\n"
                "回答:"
            )
        return (
            f"你是一个专业的 AI 编程助手。\n\n"
            f"问题: {question}\n\n"
            "回答:"
        )

    def answer(self, user_id: int, question: str) -> tuple[str, list[dict]]:
        store = self._get_vectorstore(user_id)
        context = ""
        sources: list[dict] = []

        if store:
            try:
                docs = store.similarity_search(question, k=3)
                if docs:
                    context = "\n\n".join(doc.page_content for doc in docs)
                    sources = [doc.metadata for doc in docs]
            except Exception as exc:
                logger.warning("向量检索失败：%s", exc)

        llm = self._ensure_llm()
        if llm is None:
            return self._offline_answer(question), sources

        try:
            from langchain.prompts import PromptTemplate
            prompt = PromptTemplate.from_template(
                "你是一个专业的 AI 编程助手。请结合上下文进行回答。\n\n"
                "上下文:\n{context}\n\n"
                "问题: {question}\n\n"
                "回答:"
            )
            answer = llm.invoke(prompt.format(context=context or "无相关上下文", question=question))
            return str(answer), sources
        except Exception as exc:
            logger.warning("LLM 回答失败：%s", exc)
            return self._offline_answer(question), sources

    def _offline_answer(self, question: str) -> str:
        results = search_knowledge(question, top_k=2)
        if not results:
            return (
                "【智能代码工作台 · 离线助手】\n\n"
                f"问题：{question}\n\n"
                "抱歉，知识库中暂未收录相关内容。\n"
                "提示：本系统预置了 Git/Docker/SQL/Python/系统设计/前端等方向的常见问答。\n"
                "建议您：\n"
                "1. 尝试用更具体的技术关键词提问\n"
                "2. 在知识库页面上传相关文档进行补充\n"
                "3. 联网后从云端获取更完整的答案"
            )

        top = results[0]
        lines = [
            "【智能代码工作台 · 知识库检索回答】\n",
            f"📖 参考文档：{top['title']}\n",
            f"📁 分类：{top['category']}\n",
            "─" * 40,
            top['content'][:600],
        ]
        if len(results) > 1:
            lines.append("")
            lines.append("─" * 40)
            lines.append(f"📖 补充：{results[1]['title']}")
            lines.append(results[1]['content'][:300])
        lines.extend(["", "─" * 40, "💡 以上由本地预置知识库检索生成。"])
        return "\n".join(lines)

    def stream_answer(self, user_id: int, question: str) -> Generator[dict, None, None]:
        answer, sources = self.answer(user_id, question)
        for i in range(0, len(answer), 15):
            yield {"event": "token", "data": {"content": answer[i:i + 15]}}
            time.sleep(0.025)
        yield {"event": "metadata", "data": {"sources": sources}}
        yield {"event": "done", "data": {"success": True}}


rag_service = RagService()
