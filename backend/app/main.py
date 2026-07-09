from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.api.v1.endpoints import auth, chat, knowledge
from backend.app.api.v1.endpoints import code_ai, code_projects, snippets, ide_integration
from backend.app.core.exceptions import AIWorkbenchException

app = FastAPI(
    title="AI Workbench API",
    version="1.0.0",
    description="全栈 AI 智能代码工作台 · FastAPI 后端服务",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AIWorkbenchException)
async def ai_exception_handler(request: Request, exc: AIWorkbenchException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"服务器内部错误：{str(exc)}"},
    )


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "AI Workbench Backend"}


@app.get("/api/health")
async def api_health():
    return {"status": "ok", "version": "1.0.0", "service": "AI Workbench API"}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(knowledge.router, prefix="/api/v1")
app.include_router(code_projects.router, prefix="/api/v1")
app.include_router(code_ai.router, prefix="/api/v1")
app.include_router(snippets.router, prefix="/api/v1")
app.include_router(ide_integration.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
