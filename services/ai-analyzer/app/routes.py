import os
import httpx
from fastapi import APIRouter, HTTPException
from app.models import AnalyzeRequest, AnalyzeResponse

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]

def get_gemini_url(model: str) -> str:
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

def build_prompt(req: AnalyzeRequest) -> str:
    return f"""You are a DevSecOps expert. Analyze this Jenkins failure log and respond in exactly this format (keep it brief, 3-4 lines total):

ROOT CAUSE: <one sentence>
SEVERITY: <HIGH/MEDIUM/LOW>
FIX: <one sentence with the exact fix>

Service: {req.service}
Build: {req.build_number}
LOG: {req.log[-5000:]}"""

async def call_gemini(payload: dict) -> dict:
    """Try each model in order, falling back on 503."""
    last_error = None
    async with httpx.AsyncClient(timeout=30.0) as client:
        for model in GEMINI_MODELS:
            try:
                response = await client.post(
                    f"{get_gemini_url(model)}?key={GEMINI_API_KEY}",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                if response.status_code == 503:
                    last_error = f"Model {model} unavailable (503)"
                    continue  # try next model
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                last_error = f"Gemini API error ({model}): {e.response.text}"
                if e.response.status_code != 503:
                    raise HTTPException(status_code=502, detail=last_error)
                continue  # 503 — try next model
            except httpx.RequestError as e:
                raise HTTPException(status_code=503, detail=f"Cannot reach Gemini API: {str(e)}")

    raise HTTPException(status_code=503, detail=f"All Gemini models unavailable. Last error: {last_error}")

@router.post("/analyze", response_model=AnalyzeResponse, tags=["analyzer"])
async def analyze_log(req: AnalyzeRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")

    payload = {
        "contents": [
            {
                "parts": [{"text": build_prompt(req)}]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1024,
        }
    }

    data = await call_gemini(payload)

    try:
        full_analysis = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise HTTPException(status_code=502, detail=f"Unexpected response: {data}")

    root_cause = "See full analysis"
    severity = "MEDIUM"
    fix_lines = []
    in_fix = False

    for line in full_analysis.split("\n"):
        line = line.strip()
        if line.startswith("ROOT CAUSE:"):
            root_cause = line.replace("ROOT CAUSE:", "").strip()
        elif line.startswith("SEVERITY:"):
            severity = line.replace("SEVERITY:", "").strip()
        elif line.startswith("FIX:"):
            in_fix = True
        elif in_fix and line:
            fix_lines.append(line)

    fix_suggestion = "\n".join(fix_lines) if fix_lines else "See full analysis"

    return AnalyzeResponse(
        service=req.service,
        build_number=req.build_number,
        root_cause=root_cause,
        fix_suggestion=fix_suggestion,
        severity=severity,
        full_analysis=full_analysis,
    )

@router.post("/analyze/jenkins", tags=["analyzer"])
async def analyze_jenkins_failure(req: AnalyzeRequest):
    req.context = "Jenkins CI/CD pipeline on EKS microservices project"
    return await analyze_log(req)
