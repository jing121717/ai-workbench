from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Optional, List
from pydantic import BaseModel
import json

router = APIRouter(prefix="/code-ai", tags=["代码AI能力"])

class CodeAnalysisRequest(BaseModel):
    code: str
    language: str
    analysis_type: str

class CodeConvertRequest(BaseModel):
    code: str
    source_language: str
    target_language: str
    framework: Optional[str] = ""

class UnitTestRequest(BaseModel):
    code: str
    language: str
    framework: Optional[str] = "pytest"

class ApiDocRequest(BaseModel):
    code: str
    language: str

class LogAnalyzeRequest(BaseModel):
    log_content: str
    error_type: Optional[str] = "runtime"
    code: Optional[str] = ""

class RefactorRequest(BaseModel):
    code: str
    language: str
    refactor_type: Optional[str] = "readability"

class SQLGenerateRequest(BaseModel):
    description: str
    db_type: Optional[str] = "mysql"
    db_schema: Optional[str] = ""

class SQLAnalyzeRequest(BaseModel):
    sql: str
    db_type: Optional[str] = "mysql"

class CRUDGenerateRequest(BaseModel):
    table_schema: str
    language: Optional[str] = "python"
    orm: Optional[str] = "sqlalchemy"

class ArchDiagramRequest(BaseModel):
    project_info: dict

def get_code_ai_service():
    from app.services.code_ai_service import get_code_ai_service as _get
    return _get()

def get_offline_service():
    from app.services.offline_code_service import get_offline_code_service as _get
    return _get()

def get_sql_service():
    from app.services.sql_arch_service import get_sql_enhance_service as _get
    return _get()

@router.get("/analysis-types")
async def get_analysis_types():
    """获取支持的分析类型"""
    service = get_code_ai_service()
    return service.get_supported_analysis_types()

@router.post("/analyze")
async def analyze_code(request: CodeAnalysisRequest):
    """代码分析（缺陷扫描、审查等）"""
    service = get_code_ai_service()

    if request.analysis_type == "defect":
        result = await service.analyze_defect(request.code, request.language)
    elif request.analysis_type == "review":
        result = await service.code_review(request.code, request.language)
    elif request.analysis_type == "comment":
        result = await service.generate_comments(request.code, request.language)
    else:
        raise HTTPException(400, f"不支持的分析类型: {request.analysis_type}")

    return result

@router.post("/convert")
async def convert_code(request: CodeConvertRequest):
    """跨语言代码转换"""
    service = get_code_ai_service()
    result = await service.convert_code(
        request.code,
        request.source_language,
        request.target_language,
        request.framework
    )
    return result

@router.post("/unit-test")
async def generate_unit_test(request: UnitTestRequest):
    """生成单元测试"""
    service = get_code_ai_service()
    result = await service.generate_unit_test(
        request.code,
        request.language,
        request.framework
    )
    return result

@router.post("/api-doc")
async def generate_api_doc(request: ApiDocRequest):
    """生成接口文档"""
    service = get_code_ai_service()
    result = await service.generate_api_doc(request.code, request.language)
    return result

@router.post("/log-analyze")
async def analyze_error_log(request: LogAnalyzeRequest):
    """分析错误日志"""
    service = get_code_ai_service()
    result = await service.analyze_error_log(
        request.log_content,
        request.error_type,
        request.code or ""
    )
    return result

@router.post("/refactor")
async def refactor_code(request: RefactorRequest):
    """代码重构"""
    service = get_code_ai_service()
    result = await service.refactor_code(
        request.code,
        request.language,
        request.refactor_type
    )
    return result

@router.post("/detect-language")
async def detect_language(code: str, filename: Optional[str] = None):
    """自动检测代码语言"""
    service = get_code_ai_service()
    language = service.detect_language(code, filename or "")
    return {"language": language}

@router.post("/upload-and-analyze")
async def upload_and_analyze(
    file: UploadFile = File(...),
    analysis_type: str = "defect"
):
    """上传文件并分析"""
    content = await file.read()
    code = content.decode('utf-8', errors='ignore')

    service = get_code_ai_service()
    language = service.detect_language(code, file.filename)

    if analysis_type == "defect":
        result = await service.analyze_defect(code, language)
    elif analysis_type == "review":
        result = await service.code_review(code, language)
    else:
        raise HTTPException(400, f"不支持的分析类型: {analysis_type}")

    return {
        "filename": file.filename,
        "language": language,
        "size": len(code),
        "result": result
    }

@router.post("/sql/generate")
async def generate_sql(request: SQLGenerateRequest):
    """从业务描述生成SQL"""
    service = get_sql_service()
    result = await service.generate_sql_from_description(
        request.description,
        request.db_type,
        request.db_schema
    )
    return result

@router.post("/sql/analyze")
async def analyze_sql(request: SQLAnalyzeRequest):
    """SQL性能分析"""
    service = get_sql_service()
    result = await service.analyze_sql_performance(request.sql, request.db_type)
    return result

@router.post("/sql/crud")
async def generate_crud(request: CRUDGenerateRequest):
    """生成CRUD代码"""
    service = get_sql_service()
    result = await service.generate_crud(
        request.table_schema,
        request.language,
        request.orm
    )
    return result

@router.get("/sql/supported-db")
async def get_supported_db():
    """获取支持的数据库类型"""
    service = get_sql_service()
    return {"db_types": service.get_supported_db_types(), "orms": service.get_supported_orms()}

@router.get("/offline/status")
async def check_offline_status():
    """检查离线模型状态"""
    service = get_offline_service()
    status = await service.check_ollama_status()
    return status

@router.get("/offline/models")
async def list_offline_models():
    """列出可用离线模型"""
    service = get_offline_service()
    models = await service.list_available_models()
    return {"models": [{"name": m.name, "size": m.size, "supports_code": m.supports_code} for m in models]}

@router.post("/offline/pull-model")
async def pull_offline_model(model_name: str):
    """拉取离线模型"""
    service = get_offline_service()
    result = await service.pull_model(model_name)
    return result

@router.post("/offline/analyze")
async def analyze_code_offline(code: str, language: str):
    """离线代码分析"""
    service = get_offline_service()
    result = await service.analyze_code_offline(code, language)
    return result

@router.post("/offline/refactor")
async def refactor_code_offline(code: str, language: str, refactor_type: str = "readability"):
    """离线代码重构"""
    service = get_offline_service()
    result = await service.refactor_code_offline(code, language, refactor_type)
    return result

@router.post("/offline/test")
async def generate_test_offline(code: str, language: str, framework: str = "pytest"):
    """离线生成测试"""
    service = get_offline_service()
    result = await service.generate_test_offline(code, language, framework)
    return result

@router.post("/offline/explain")
async def explain_code_offline(code: str, language: str):
    """离线代码解释"""
    service = get_offline_service()
    result = await service.explain_code_offline(code, language)
    return result

@router.post("/stream-analyze")
async def stream_code_analysis(
    request: CodeAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """流式代码分析"""
    service = get_code_ai_service()

    if request.analysis_type == "defect":
        result = await service.analyze_defect(request.code, request.language)
    elif request.analysis_type == "review":
        result = await service.code_review(request.code, request.language)
    else:
        raise HTTPException(400, f"不支持的分析类型: {request.analysis_type}")

    async def generate():
        yield f"data: {json.dumps({'status': 'completed', 'result': result})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )
