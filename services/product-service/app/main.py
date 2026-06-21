from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router

app = FastAPI(
    title="Product Service",
    description="Microservice for managing product catalog",
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
    return {"status": "healthy", "service": "product-service"}


@app.get("/")
def root(:
    return {"message": "Product Service is running"}
