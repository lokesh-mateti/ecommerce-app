import os
import httpx
from fastapi import APIRouter, HTTPException
from app.models import AnalyzeRequest, AnalyzeResponse

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def build_prompt(req: AnalyzeRequest) -> str:
    return f"""You are a DevSecOps expert. Analyze this CI/CD failure log and respond in EXACTLY this format with no extra text:

ROOT CAUSE: <one sentence explaining the exact cause>
SEVERITY: <must be exactly one of: LOW, MEDIUM, HIGH, CRITICAL>
FIX:
1. <first step>
2. <second step>
3. <third step if needed>

Context: {req.context}
Service: {req.service}
Build: {req.build_number}

LOG:
{req.log[-2000:]}"""


@router.post("/analyze", response_model=AnalyzeResponse, tags=["analyzer"])
async def analyze_log(req: AnalyzeRequest):
    """Analyze a failure log using Gemini 2.5 Flash."""

    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")

    prompt = build_prompt(req)

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 512,
        }
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{GEMINI_URL}?key={GEMINI_API_KEY}",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {e.response.text}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Cannot reach Gemini API: {str(e)}")

    try:
        full_analysis = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise HTTPException(status_code=502, detail="Unexpected Gemini response format")

    # Parse structured fields
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
    """Convenience endpoint for Jenkins pipeline failures."""
    req.context = "Jenkins CI/CD pipeline on EKS microservices project"
    return await analyze_log(req)
