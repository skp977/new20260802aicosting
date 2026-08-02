from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from fastapi import FastAPI
from pydantic import BaseModel

from orchestrators.manual_request_orchestrator import ManualRequestOrchestrator

app = FastAPI(
    title="PM Automation API",
    version="1.0.0"
)

engine = ManualRequestOrchestrator()

class InquiryRequest(BaseModel):
    text: str

@app.get("/health")
def health():
    return {
        "status": "ok"
    }

@app.post("/process-inquiry")
def process_inquiry(data: InquiryRequest):

    result = engine.process(
        data.text
    )

    return result
