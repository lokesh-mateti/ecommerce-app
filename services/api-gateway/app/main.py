from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router

app = FastAPI(
    title="API Gateway",
    description="Single entry point that authenticates requests and routes them to backend microservices",
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
    """Liveness/readiness probe endpoint for Kubernetes."""
    return {"status": "healthy", "service": "api-gateway"}


@app.get("/")
def root():
    return {"message": "API Gateway v4 - Demo"}
