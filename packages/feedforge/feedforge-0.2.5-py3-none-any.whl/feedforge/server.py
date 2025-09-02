from __future__ import annotations

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from .analysis import Analyzer


class AnalyzeRequest(BaseModel):
    description: str = Field(..., description="User interest description")
    max_results_per_keyword: int = Field(2, ge=1, le=10)
    num_keywords: int = Field(5, ge=1, le=10)


class AnalyzeResponse(BaseModel):
    keywords: List[str]
    videos: List[str]


app = FastAPI(title="FeedForge Analysis Service", version="0.1.0")


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    try:
        analyzer = Analyzer()
        result = await analyzer.analyze(
            description=req.description,
            max_results_per_keyword=req.max_results_per_keyword,
            num_keywords=req.num_keywords,
        )
        return AnalyzeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    uvicorn.run("feedforge.server:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    run()