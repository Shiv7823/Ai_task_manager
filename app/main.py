from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import tasks, ai
from app.core.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Task Manager API",
    description="FastAPI backend with JWT auth and Gemini AI integration for intelligent task management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(ai.router, prefix="/ai", tags=["AI Features"])

@app.get("/", tags=["Health"])
def root():
    return {"status": "running", "message": "AI Task Manager API is live"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "version": "1.0.0"}
