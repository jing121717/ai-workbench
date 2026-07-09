from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum, JSON, BigInteger, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class CodeProject(Base):
    __tablename__ = "code_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, comment="项目名称")
    local_path = Column(String(1000), comment="本地路径")
    is_git_repo = Column(Boolean, default=False, comment="是否Git仓库")
    git_remote_url = Column(String(500), comment="Git远程地址")
    git_current_branch = Column(String(100), comment="当前分支")
    tech_stack = Column(JSON, comment="技术栈列表")
    summary = Column(Text, comment="项目简介")
    project_tree = Column(JSON, comment="项目结构树")
    languages_stats = Column(JSON, comment="语言统计")
    total_files = Column(Integer, default=0)
    total_units = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    kb_id = Column(Integer, ForeignKey("knowledge_bases.id"), comment="关联知识库ID")
    is_active = Column(Boolean, default=True)
    last_synced_at = Column(DateTime, comment="最后同步时间")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="code_projects")
    code_units = relationship("CodeUnit", back_populates="project", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_owner_id", "owner_id"),
        Index("idx_kb_id", "kb_id"),
    )

class CodeUnit(Base):
    __tablename__ = "code_units"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("code_projects.id", ondelete="CASCADE"), nullable=False)
    unit_type = Column(String(50), nullable=False, comment="function/class/interface/method/constant")
    name = Column(String(255), nullable=False, comment="单元名称")
    file_path = Column(String(1000), nullable=False)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    content = Column(Text, nullable=False, comment="代码内容")
    signature = Column(String(500), comment="函数签名")
    doc_comment = Column(Text, comment="文档注释")
    return_type = Column(String(100), comment="返回类型")
    parameters = Column(JSON, comment="参数列表")
    dependencies = Column(JSON, comment="依赖列表")
    vector_id = Column(String(255), comment="向量库ID")
    is_indexed = Column(Boolean, default=False, comment="是否已索引")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("CodeProject", back_populates="code_units")

    __table_args__ = (
        Index("idx_project_type", "project_id", "unit_type"),
        Index("idx_name", "name"),
        Index("idx_file_path", "file_path"),
        Index("idx_vector_id", "vector_id"),
    )

class CodeSnippet(Base):
    __tablename__ = "code_snippets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False, comment="代码内容")
    language = Column(String(50), comment="语言 python/java/ts等")
    category = Column(String(50), comment="分类: utility/business/sql/frontend/config")
    tags = Column(JSON, comment="标签列表")
    description = Column(Text, comment="描述说明")
    is_favorite = Column(Boolean, default=False)
    use_count = Column(Integer, default=0, comment="使用次数")
    vector_id = Column(String(255), comment="向量库ID")
    is_public = Column(Boolean, default=False, comment="是否公开")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("code_projects.id"), comment="关联项目")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="code_snippets")

    __table_args__ = (
        Index("idx_category", "category"),
        Index("idx_user_favorite", "user_id", "is_favorite"),
        Index("idx_user_language", "user_id", "language"),
        UniqueConstraint("user_id", "title", name="uix_user_snippet_title"),
    )

class SnippetTemplate(Base):
    __tablename__ = "snippet_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), comment="模板分类")
    content = Column(Text, nullable=False)
    variables = Column(JSON, comment="变量定义")
    description = Column(Text)
    use_count = Column(Integer, default=0)
    is_global = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_category", "category"),
        Index("idx_user", "user_id"),
    )

class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("code_projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), ondelete="CASCADE", nullable=False)
    role = Column(String(20), default="viewer", comment="owner/editor/viewer")
    can_read = Column(Boolean, default=True)
    can_write = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_share = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("CodeProject")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uix_project_user"),
        Index("idx_project_member", "project_id", "user_id"),
    )

class CodeAnalysisTask(Base):
    __tablename__ = "code_analysis_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_type = Column(String(50), nullable=False, comment="defect/test/refactor/doc/convert")
    status = Column(String(20), default="pending", comment="pending/running/completed/failed")
    input_data = Column(JSON, comment="输入数据")
    output_data = Column(JSON, comment="输出结果")
    code_content = Column(Text)
    language = Column(String(50))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("code_projects.id"), comment="关联项目")
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_user_status", "user_id", "status"),
        Index("idx_task_type", "task_type"),
    )

class IDEIntegration(Base):
    __tablename__ = "ide_integrations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ide_type = Column(String(50), comment="vscode/vim/emacs/jetbrains")
    api_token = Column(String(255), comment="API令牌")
    settings = Column(JSON, comment="IDE设置")
    is_active = Column(Boolean, default=True)
    last_connected_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_user_ide", "user_id", "ide_type"),
    )

class CodeReviewComment(Base):
    __tablename__ = "code_review_comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("code_projects.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(1000))
    line_number = Column(Integer)
    content = Column(Text, nullable=False)
    severity = Column(String(20), comment="info/warning/error")
    resolved = Column(Boolean, default=False)
    parent_id = Column(Integer, ForeignKey("code_review_comments.id"), comment="回复父ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ai_summary = Column(Text, comment="AI评审意见摘要")
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("CodeProject")
    user = relationship("User")
    replies = relationship("CodeReviewComment", backref="parent", remote_side=[id])

    __table_args__ = (
        Index("idx_project_file", "project_id", "file_path"),
    )
