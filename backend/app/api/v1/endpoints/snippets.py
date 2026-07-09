from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/snippets", tags=["代码素材库"])

class SnippetCreate(BaseModel):
    title: str
    content: str
    language: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    description: Optional[str] = None
    is_public: Optional[bool] = False
    project_id: Optional[int] = None

class SnippetUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    language: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    is_favorite: Optional[bool] = None

class TemplateCreate(BaseModel):
    name: str
    category: Optional[str] = None
    content: str
    variables: Optional[List[dict]] = []
    description: Optional[str] = None
    is_global: Optional[bool] = False

def get_db():
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_id() -> int:
    from app.core.security import get_current_user
    user = get_current_user()
    return user.id

@router.get("/")
async def list_snippets(
    category: Optional[str] = None,
    language: Optional[str] = None,
    tags: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取代码片段列表"""
    from app.models.code_models import CodeSnippet
    from sqlalchemy import or_, and_

    query = db.query(CodeSnippet).filter(
        or_(CodeSnippet.user_id == user_id, CodeSnippet.is_public == True)
    )

    if category:
        query = query.filter(CodeSnippet.category == category)
    if language:
        query = query.filter(CodeSnippet.language == language)
    if is_favorite is not None:
        query = query.filter(CodeSnippet.is_favorite == is_favorite)
    if keyword:
        query = query.filter(
            or_(
                CodeSnippet.title.contains(keyword),
                CodeSnippet.content.contains(keyword),
                CodeSnippet.description.contains(keyword)
            )
        )

    total = query.count()
    snippets = query.order_by(CodeSnippet.updated_at.desc()).offset((page-1)*page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "list": [
            {
                "id": s.id,
                "title": s.title,
                "language": s.language,
                "category": s.category,
                "tags": s.tags or [],
                "is_favorite": s.is_favorite,
                "use_count": s.use_count,
                "description": s.description,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None
            }
            for s in snippets
        ]
    }

@router.post("/")
async def create_snippet(
    data: SnippetCreate,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """创建代码片段"""
    from app.models.code_models import CodeSnippet
    from app.services.code_vectorizer import get_code_vectorizer

    snippet = CodeSnippet(
        title=data.title,
        content=data.content,
        language=data.language,
        category=data.category,
        tags=data.tags or [],
        description=data.description,
        is_public=data.is_public,
        user_id=user_id,
        project_id=data.project_id
    )
    db.add(snippet)
    db.commit()
    db.refresh(snippet)

    try:
        vectorizer = get_code_vectorizer()
        vectorizer.index_code_snippet(
            snippet_id=snippet.id,
            content=data.content,
            language=data.language,
            tags=data.tags,
            user_id=user_id
        )
    except Exception:
        pass

    return {"id": snippet.id, "message": "创建成功"}

@router.get("/{snippet_id}")
async def get_snippet(
    snippet_id: int,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取单个片段"""
    from app.models.code_models import CodeSnippet
    from sqlalchemy import or_

    snippet = db.query(CodeSnippet).filter(
        and_(
            CodeSnippet.id == snippet_id,
            or_(CodeSnippet.user_id == user_id, CodeSnippet.is_public == True)
        )
    ).first()

    if not snippet:
        raise HTTPException(404, "片段不存在")

    snippet.use_count += 1
    db.commit()

    return {
        "id": snippet.id,
        "title": snippet.title,
        "content": snippet.content,
        "language": snippet.language,
        "category": snippet.category,
        "tags": snippet.tags or [],
        "is_favorite": snippet.is_favorite,
        "use_count": snippet.use_count,
        "description": snippet.description,
        "created_at": snippet.created_at.isoformat() if snippet.created_at else None,
        "updated_at": snippet.updated_at.isoformat() if snippet.updated_at else None
    }

@router.put("/{snippet_id}")
async def update_snippet(
    snippet_id: int,
    data: SnippetUpdate,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """更新片段"""
    from app.models.code_models import CodeSnippet

    snippet = db.query(CodeSnippet).filter(
        CodeSnippet.id == snippet_id,
        CodeSnippet.user_id == user_id
    ).first()

    if not snippet:
        raise HTTPException(404, "片段不存在")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(snippet, key, value)

    snippet.updated_at = datetime.now()
    db.commit()

    return {"message": "更新成功"}

@router.delete("/{snippet_id}")
async def delete_snippet(
    snippet_id: int,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """删除片段"""
    from app.models.code_models import CodeSnippet
    from app.services.code_vectorizer import get_code_vectorizer

    snippet = db.query(CodeSnippet).filter(
        CodeSnippet.id == snippet_id,
        CodeSnippet.user_id == user_id
    ).first()

    if not snippet:
        raise HTTPException(404, "片段不存在")

    db.delete(snippet)
    db.commit()

    try:
        vectorizer = get_code_vectorizer()
        vectorizer.delete_snippet_vector(snippet_id)
    except Exception:
        pass

    return {"message": "删除成功"}

@router.post("/{snippet_id}/favorite")
async def toggle_favorite(
    snippet_id: int,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """切换收藏状态"""
    from app.models.code_models import CodeSnippet

    snippet = db.query(CodeSnippet).filter(
        CodeSnippet.id == snippet_id,
        CodeSnippet.user_id == user_id
    ).first()

    if not snippet:
        raise HTTPException(404, "片段不存在")

    snippet.is_favorite = not snippet.is_favorite
    db.commit()

    return {"is_favorite": snippet.is_favorite}

@router.post("/batch-export")
async def batch_export(
    snippet_ids: List[int],
    format: str = "json",
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """批量导出片段"""
    from app.models.code_models import CodeSnippet

    snippets = db.query(CodeSnippet).filter(
        CodeSnippet.id.in_(snippet_ids),
        CodeSnippet.user_id == user_id
    ).all()

    if format == "markdown":
        content = "\n\n".join([
            f"## {s.title}\n\n```{s.language or ''}\n{s.content}\n```\n\n{s.description or ''}"
            for s in snippets
        ])
    else:
        content = json.dumps([
            {
                "title": s.title,
                "content": s.content,
                "language": s.language,
                "category": s.category,
                "tags": s.tags,
                "description": s.description
            }
            for s in snippets
        ], ensure_ascii=False, indent=2)

    return {
        "content": content,
        "filename": f"snippets_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.{format}",
        "count": len(snippets)
    }

@router.post("/batch-import")
async def batch_import(
    content: str,
    format: str = "json",
    category: Optional[str] = None,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """批量导入片段"""
    import json

    try:
        if format == "json":
            items = json.loads(content)
        else:
            items = [{"title": "Imported", "content": content, "category": category}]
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON format")

    created = 0
    from app.models.code_models import CodeSnippet

    for item in items:
        if not isinstance(item, dict):
            continue

        snippet = CodeSnippet(
            title=item.get("title", "Untitled"),
            content=item.get("content", ""),
            language=item.get("language"),
            category=item.get("category") or category,
            tags=item.get("tags", []),
            description=item.get("description"),
            user_id=user_id
        )
        db.add(snippet)
        created += 1

    db.commit()

    return {"message": f"成功导入 {created} 个片段", "created": created}

@router.get("/categories/list")
async def list_categories(
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取所有分类"""
    from app.models.code_models import CodeSnippet
    from sqlalchemy import func

    categories = db.query(
        CodeSnippet.category,
        func.count(CodeSnippet.id).label("count")
    ).filter(
        CodeSnippet.user_id == user_id,
        CodeSnippet.category.isnot(None)
    ).group_by(CodeSnippet.category).all()

    return [{"name": c[0] or "未分类", "count": c[1]} for c in categories]

@router.get("/tags/cloud")
async def get_tags_cloud(
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取标签云"""
    from app.models.code_models import CodeSnippet
    import json

    snippets = db.query(CodeSnippet.tags).filter(
        CodeSnippet.user_id == user_id,
        CodeSnippet.tags.isnot(None)
    ).all()

    tag_count = {}
    for s in snippets:
        tags = s[0] if s[0] else []
        for tag in tags:
            tag_count[tag] = tag_count.get(tag, 0) + 1

    return [
        {"name": k, "count": v}
        for k, v in sorted(tag_count.items(), key=lambda x: -x[1])[:50]
    ]

@router.get("/templates/")
async def list_templates(
    category: Optional[str] = None,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取模板列表"""
    from app.models.code_models import SnippetTemplate

    query = db.query(SnippetTemplate).filter(
        (SnippetTemplate.user_id == user_id) | (SnippetTemplate.is_global == True)
    )

    if category:
        query = query.filter(SnippetTemplate.category == category)

    templates = query.order_by(SnippetTemplate.use_count.desc()).all()

    return [
        {
            "id": t.id,
            "name": t.name,
            "category": t.category,
            "content": t.content,
            "variables": t.variables or [],
            "description": t.description,
            "use_count": t.use_count
        }
        for t in templates
    ]

@router.post("/templates/")
async def create_template(
    data: TemplateCreate,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """创建模板"""
    from app.models.code_models import SnippetTemplate

    template = SnippetTemplate(
        name=data.name,
        category=data.category,
        content=data.content,
        variables=data.variables or [],
        description=data.description,
        is_global=data.is_global,
        user_id=user_id if not data.is_global else None
    )
    db.add(template)
    db.commit()
    db.refresh(template)

    return {"id": template.id, "message": "创建成功"}

@router.get("/search/")
async def search_snippets(
    query: str,
    language: Optional[str] = None,
    top_k: int = 10,
    user_id: int = Depends(get_current_user_id)
):
    """语义搜索片段"""
    from app.services.code_vectorizer import get_code_vectorizer

    try:
        vectorizer = get_code_vectorizer()
        results = vectorizer.search_snippets(
            query=query,
            language=language,
            user_id=user_id,
            top_k=top_k
        )
        return {"results": results}
    except Exception as e:
        return {"results": [], "error": str(e)}

import json
