from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Query
from typing import Optional, List
from pydantic import BaseModel
import tempfile
import shutil
from pathlib import Path

router = APIRouter(prefix="/code-projects", tags=["代码仓库管理"])

class ProjectCreate(BaseModel):
    name: str
    local_path: Optional[str] = None
    is_git_repo: bool = False

class GitCloneRequest(BaseModel):
    url: str
    local_path: Optional[str] = None
    branch: Optional[str] = "main"

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

def get_code_parser():
    from app.services.code_parser import CodeRepositoryParser
    return CodeRepositoryParser()

def get_code_vectorizer():
    from app.services.code_vectorizer import get_code_vectorizer as _get
    return _get()

@router.get("/")
async def list_projects(
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取项目列表"""
    from app.models.code_models import CodeProject, ProjectMember

    owned = db.query(CodeProject).filter(CodeProject.owner_id == user_id).all()

    memberships = db.query(ProjectMember).filter(ProjectMember.user_id == user_id).all()
    member_project_ids = [m.project_id for m in memberships]

    if member_project_ids:
        shared = db.query(CodeProject).filter(
            CodeProject.id.in_(member_project_ids),
            CodeProject.owner_id != user_id
        ).all()
    else:
        shared = []

    return {
        "owned": [
            {
                "id": p.id,
                "name": p.name,
                "tech_stack": p.tech_stack or [],
                "total_files": p.total_files,
                "total_units": p.total_units,
                "is_git_repo": p.is_git_repo,
                "last_synced_at": p.last_synced_at.isoformat() if p.last_synced_at else None,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in owned
        ],
        "shared": [
            {
                "id": p.id,
                "name": p.name,
                "tech_stack": p.tech_stack or [],
                "total_files": p.total_files,
                "total_units": p.total_units,
                "owner_id": p.owner_id
            }
            for p in shared
        ]
    }

@router.post("/")
async def create_project(
    data: ProjectCreate,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """创建项目"""
    from app.models.code_models import CodeProject
    from datetime import datetime

    project = CodeProject(
        name=data.name,
        local_path=data.local_path,
        is_git_repo=data.is_git_repo,
        owner_id=user_id,
        created_at=datetime.now()
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return {"id": project.id, "name": project.name, "message": "创建成功"}

@router.get("/{project_id}")
async def get_project(
    project_id: int,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取项目详情"""
    from app.models.code_models import CodeProject, ProjectMember

    project = db.query(CodeProject).filter(CodeProject.id == project_id).first()

    if not project:
        raise HTTPException(404, "项目不存在")

    if project.owner_id != user_id:
        membership = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        ).first()
        if not membership:
            raise HTTPException(403, "无权限访问")

    return {
        "id": project.id,
        "name": project.name,
        "local_path": project.local_path,
        "is_git_repo": project.is_git_repo,
        "git_remote_url": project.git_remote_url,
        "git_current_branch": project.git_current_branch,
        "tech_stack": project.tech_stack or [],
        "summary": project.summary,
        "project_tree": project.project_tree,
        "languages_stats": project.languages_stats,
        "total_files": project.total_files,
        "total_units": project.total_units,
        "last_synced_at": project.last_synced_at.isoformat() if project.last_synced_at else None,
        "created_at": project.created_at.isoformat() if project.created_at else None
    }

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """删除项目"""
    from app.models.code_models import CodeProject
    from app.services.code_vectorizer import get_code_vectorizer

    project = db.query(CodeProject).filter(
        CodeProject.id == project_id,
        CodeProject.owner_id == user_id
    ).first()

    if not project:
        raise HTTPException(404, "项目不存在或无权限删除")

    try:
        vectorizer = get_code_vectorizer()
        vectorizer.delete_project_vectors(project_id)
    except Exception:
        pass

    db.delete(project)
    db.commit()

    return {"message": "删除成功"}

@router.post("/upload")
async def upload_code_repository(
    name: str,
    background_tasks: BackgroundTasks,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """上传代码仓库（文件夹）"""
    return {"message": "请使用 /code-projects/upload-file 接口上传文件"}

@router.post("/upload-file")
async def upload_project_file(
    name: str,
    files: List[UploadFile] = File(...),
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """通过文件上传创建项目"""
    from app.models.code_models import CodeProject
    from app.services.code_parser import CodeRepositoryParser
    from app.services.code_vectorizer import get_code_vectorizer
    from datetime import datetime
    import os

    temp_dir = Path(tempfile.mkdtemp(prefix="ai_workbench_repo_"))

    try:
        for file in files:
            file_path = temp_dir / file.filename
            content = await file.read()
            with open(file_path, 'wb') as f:
                f.write(content)

        parser = CodeRepositoryParser()
        project_info = parser.parse_repository(str(temp_dir))

        project = CodeProject(
            name=name,
            local_path=str(temp_dir),
            is_git_repo=False,
            tech_stack=project_info.tech_stack,
            summary=project_info.summary,
            project_tree=project_info.project_tree,
            languages_stats=project_info.languages_stats,
            total_files=project_info.total_files,
            total_units=project_info.total_units,
            owner_id=user_id,
            created_at=datetime.now(),
            last_synced_at=datetime.now()
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        vectorizer = get_code_vectorizer()
        vectorizer.index_code_units(project.id, project_info.code_units)

        return {
            "id": project.id,
            "name": project.name,
            "tech_stack": project.tech_stack,
            "total_files": project.total_files,
            "total_units": project.total_units,
            "summary": project.summary
        }

    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(500, str(e))

@router.post("/git-clone")
async def git_clone_repository(
    data: GitCloneRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """克隆Git仓库"""
    from app.models.code_models import CodeProject
    from app.services.code_parser import CodeRepositoryParser
    from app.services.code_vectorizer import get_code_vectorizer
    from datetime import datetime
    import subprocess

    if not data.local_path:
        data.local_path = str(Path.home() / ".ai_workbench" / "repos")

    target_dir = Path(data.local_path) / data.url.split('/')[-1].replace('.git', '')
    target_dir.parent.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', '-b', data.branch or 'main', data.url, str(target_dir)],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            raise HTTPException(400, f"Git clone failed: {result.stderr}")

        parser = CodeRepositoryParser()
        project_info = parser.parse_repository(str(target_dir), is_git=True)

        project = CodeProject(
            name=project_info.name,
            local_path=str(target_dir),
            is_git_repo=True,
            git_remote_url=data.url,
            git_current_branch=data.branch or 'main',
            tech_stack=project_info.tech_stack,
            summary=project_info.summary,
            project_tree=project_info.project_tree,
            languages_stats=project_info.languages_stats,
            total_files=project_info.total_files,
            total_units=project_info.total_units,
            owner_id=user_id,
            created_at=datetime.now(),
            last_synced_at=datetime.now()
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        vectorizer = get_code_vectorizer()
        vectorizer.index_code_units(project.id, project_info.code_units)

        return {
            "id": project.id,
            "name": project.name,
            "git_url": data.url,
            "branch": data.branch or 'main',
            "tech_stack": project.tech_stack,
            "total_files": project.total_files,
            "total_units": project.total_units
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(400, "Git clone timeout")
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/{project_id}/structure")
async def get_project_structure(
    project_id: int,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取项目结构树"""
    from app.models.code_models import CodeProject

    project = db.query(CodeProject).filter(CodeProject.id == project_id).first()
    if not project:
        raise HTTPException(404, "项目不存在")

    if project.owner_id != user_id:
        raise HTTPException(403, "无权限访问")

    return {
        "tree": project.project_tree,
        "languages_stats": project.languages_stats
    }

@router.get("/{project_id}/units")
async def get_code_units(
    project_id: int,
    unit_type: Optional[str] = None,
    file_path: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取代码单元列表"""
    from app.models.code_models import CodeProject, CodeUnit
    from sqlalchemy import and_

    project = db.query(CodeProject).filter(CodeProject.id == project_id).first()
    if not project:
        raise HTTPException(404, "项目不存在")

    query = db.query(CodeUnit).filter(CodeUnit.project_id == project_id)

    if unit_type:
        query = query.filter(CodeUnit.unit_type == unit_type)
    if file_path:
        query = query.filter(CodeUnit.file_path.contains(file_path))

    total = query.count()
    units = query.offset((page-1)*page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "units": [
            {
                "id": u.id,
                "type": u.unit_type,
                "name": u.name,
                "file_path": u.file_path,
                "start_line": u.start_line,
                "end_line": u.end_line,
                "signature": u.signature,
                "doc_comment": u.doc_comment,
                "is_indexed": u.is_indexed
            }
            for u in units
        ]
    }

@router.post("/{project_id}/sync")
async def sync_project(
    project_id: int,
    background_tasks: BackgroundTasks,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """同步项目"""
    from app.models.code_models import CodeProject
    from app.services.code_parser import CodeRepositoryParser
    from app.services.code_vectorizer import get_code_vectorizer
    from datetime import datetime

    project = db.query(CodeProject).filter(
        CodeProject.id == project_id,
        CodeProject.owner_id == user_id
    ).first()

    if not project:
        raise HTTPException(404, "项目不存在")

    try:
        parser = CodeRepositoryParser()
        project_info = parser.parse_repository(project.local_path)

        project.tech_stack = project_info.tech_stack
        project.summary = project_info.summary
        project.project_tree = project_info.project_tree
        project.languages_stats = project_info.languages_stats
        project.total_files = project_info.total_files
        project.total_units = project_info.total_units
        project.last_synced_at = datetime.now()

        db.commit()

        vectorizer = get_code_vectorizer()
        vectorizer.delete_project_vectors(project_id)
        vectorizer.index_code_units(project_id, project_info.code_units)

        return {
            "message": "同步成功",
            "total_files": project.total_files,
            "total_units": project.total_units
        }

    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/search/")
async def search_code(
    query: str,
    project_id: Optional[int] = None,
    unit_type: Optional[str] = None,
    language: Optional[str] = None,
    top_k: int = 10
):
    """代码检索"""
    from app.services.code_vectorizer import get_code_vectorizer

    try:
        vectorizer = get_code_vectorizer()
        results = vectorizer.search_code(
            query=query,
            project_id=project_id,
            code_type=unit_type,
            language=language,
            top_k=top_k
        )

        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/{project_id}/members/")
async def add_project_member(
    project_id: int,
    user_id_to_add: int,
    role: str = "viewer",
    can_read: bool = True,
    can_write: bool = False,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """添加项目成员"""
    from app.models.code_models import CodeProject, ProjectMember

    project = db.query(CodeProject).filter(
        CodeProject.id == project_id,
        CodeProject.owner_id == user_id
    ).first()

    if not project:
        raise HTTPException(404, "项目不存在或无权限")

    member = ProjectMember(
        project_id=project_id,
        user_id=user_id_to_add,
        role=role,
        can_read=can_read,
        can_write=can_write
    )
    db.add(member)
    db.commit()

    return {"message": "成员添加成功"}
