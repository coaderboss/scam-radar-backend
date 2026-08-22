from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import all independent agents
from agent_gatekeeper import validate_input
from agent_brand import check_brand_impersonation
from agent_dl import run_dl_scan
from agent_judge import get_master_verdict
from agent_news import fetch_live_threat_intel

app = FastAPI(title="Scam Intel Multi-Agent Pipeline")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

class ThreatReport(BaseModel):
    url: str | None = None
    message: str | None = None

@app.post("/scan-advanced")
def scan_advanced(data: ThreatReport):
    try:
        # Step 1: Gatekeeper (Validation)
        validate_input(data.url, data.message)
        
        # Step 2: Brand Impersonation Check
        brand_report = check_brand_impersonation(data.url)
        
        # Step 3: Deep Learning & RAG Memory execution
        dl_report = run_dl_scan(data.url, data.message)
        
        # Step 4: Master Judge (LLM Orchestration)
        final_verdict = get_master_verdict(dl_report, brand_report)

        return {
            "status": "success",
            "agents_report": {
                "brand_detective": brand_report,
                "deep_learning": dl_report
            },
            "master_verdict": final_verdict
        }

    except ValueError as ve:
        return {"error": str(ve)}
    except Exception as e:
        return {"error": f"System Failure: {str(e)}"}

@app.get("/live-intel")
def get_live_intel():
    try:
        intel_data = fetch_live_threat_intel()
        if "error" in intel_data:
            return {"status": "error", "message": intel_data["error"]}
        return {"status": "success", "feed": intel_data["data"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}        