from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

app = FastAPI(
    title="AI Log Analyzer",
    description="Analyzes Jenkins/EKS failure logs using Gemini AI and suggests fixes",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ai-analyzer"}


@app.get("/")
def root():
    return {"message": "AI Log Analyzer — powered by Gemini 2.5 Flash"}
