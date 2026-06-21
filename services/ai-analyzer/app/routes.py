import os
import httpx
from fastapi import APIRouter, HTTPException
from app.models import AnalyzeRequest, AnalyzeResponse

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def build_prompt(req: AnalyzeRequest) -> str:
    return f"""You are a DevSecOps expert analyzing a CI/CD pipeline failure.

Context: {req.context}
Service: {req.service}
Build Number: {req.build_number}

Analyze the following failure log and provide:
1. ROOT CAUSE: What exactly caused the failure (1-2 sentences)
2. SEVERITY: One of [LOW, MEDIUM, HIGH, CRITICAL]
3. FIX: Exact steps to fix the issue (numbered list)

Keep your response concise and actionable. Format exactly as:
ROOT CAUSE: <explanation>
SEVERITY: <level>
FIX:
1. <step>
2. <step>
...

FAILURE LOG:
{req.log[-3000:]}
"""


@router.post("/analyze", response_model=AnalyzeResponse, tags=["analyzer"])
async def analyze_log(req: AnalyzeRequest):
    """Analyze a failure log using Gemini 2.5 Flash and return root cause + fix."""

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
            "temperature": 0.2,
            "maxOutputTokens": 1024,
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

    # Extract text from Gemini response
    try:
        full_analysis = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise HTTPException(status_code=502, detail="Unexpected Gemini response format")

    # Parse structured fields
    root_cause = "See full analysis"
    severity = "MEDIUM"
    fix_suggestion = "See full analysis"

    lines = full_analysis.split("\n")
    fix_lines = []
    in_fix = False

    for line in lines:
        if line.startswith("ROOT CAUSE:"):
            root_cause = line.replace("ROOT CAUSE:", "").strip()
        elif line.startswith("SEVERITY:"):
            severity = line.replace("SEVERITY:", "").strip()
        elif line.startswith("FIX:"):
            in_fix = True
        elif in_fix and line.strip():
            fix_lines.append(line.strip())

    if fix_lines:
        fix_suggestion = "\n".join(fix_lines)

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
    """Convenience endpoint specifically for Jenkins pipeline failures."""
    req.context = "Jenkins CI/CD pipeline on EKS microservices project"
    return await analyze_log(req)
