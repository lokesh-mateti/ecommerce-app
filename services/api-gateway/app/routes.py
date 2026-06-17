import os
import httpx
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse

from app.models import TokenRequest, TokenResponse
from app.auth import authenticate_user, create_access_token, verify_token

router = APIRouter()

# In EKS these resolve via Kubernetes Service DNS.
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://localhost:8002")


@router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(payload: TokenRequest):
    if not authenticate_user(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=payload.username)
    return TokenResponse(access_token=token)


async def _proxy_request(base_url: str, path: str, request: Request) -> JSONResponse:
    """Forwards the incoming request to the target microservice and relays its response."""
    url = f"{base_url}{path}"
    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.request(
                method=request.method,
                url=url,
                content=body,
                params=request.query_params,
                headers={"content-type": "application/json"},
            )
        return JSONResponse(
            status_code=response.status_code,
            content=response.json() if response.content else None,
        )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=f"Upstream service unavailable: {base_url}")


@router.api_route(
    "/api/v1/products/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"],
    tags=["gateway"],
)
async def products_proxy(path: str, request: Request, user: str = Depends(verify_token)):
    return await _proxy_request(PRODUCT_SERVICE_URL, f"/api/v1/products/{path}", request)


@router.api_route(
    "/api/v1/orders/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    tags=["gateway"],
)
async def orders_proxy(path: str, request: Request, user: str = Depends(verify_token)):
    return await _proxy_request(ORDER_SERVICE_URL, f"/api/v1/orders/{path}", request)
