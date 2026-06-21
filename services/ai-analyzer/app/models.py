from pydantic import BaseModel
from typing import Optional


class AnalyzeRequest(BaseModel):
    log: str
    service: Optional[str] = "unknown"
    build_number: Optional[str] = "unknown"
    context: Optional[str] = "Jenkins CI/CD pipeline"


class AnalyzeResponse(BaseModel):
    service: str
    build_number: str
    root_cause: str
    fix_suggestion: str
    severity: str
    full_analysis: str
