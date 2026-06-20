from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

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


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Add HTTPBearer security scheme so Swagger shows the Authorize button
    schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
        }
    }
    # Apply security globally to all routes
    for path in schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"HTTPBearer": []}])
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/health")
def health_check():
    """Liveness/readiness probe endpoint for Kubernetes."""
    return {"status": "healthy", "service": "api-gateway"}


@app.get("/")
def root():
    return {"message": "API Gateway v4 - Demo"}
