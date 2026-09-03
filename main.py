import os
import json
import logging
from click import prompt
import requests
import google.generativeai as genai


from fastapi import FastAPI, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
from prompts import build_prompt


load_dotenv()
PROCESSED_SYS_IDS = set()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("task0")

app = FastAPI(title="Task0 Sherouk")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERVICENOW_INSTANCE_URL = os.getenv("SERVICENOW_INSTANCE_URL")
SERVICENOW_USERNAME = os.getenv("SERVICENOW_USERNAME")
SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD")

genai.configure(api_key=GEMINI_API_KEY)

with open(os.path.join(os.path.dirname(__file__), "kb_articles.json"), "r", encoding="utf-8") as f:
    KB_ARTICLES = json.load(f)["articles"]


def write_back_to_servicenow(incident_sys_id: str, decision: str, message: str):
    url = f"{SERVICENOW_INSTANCE_URL}/api/now/table/incident/{incident_sys_id}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    auth = (SERVICENOW_USERNAME, SERVICENOW_PASSWORD)

    if decision == "respond":
        body = {
            "work_notes": f"[AI Agent] Resolved: {message}",
            "close_notes": message,
            "close_code": "Solved (Permanently)",
            "state": "6",
        }
    elif decision == "ask":
        body = {
            "comments": message,
        }
    else:  # escalate
        body = {
            "work_notes": f"[AI Agent] Escalated: {message}",
        }

    resp = requests.patch(url, headers=headers, auth=auth, json=body, timeout=15)
    resp.raise_for_status()
    logger.info(f"Wrote back to ServiceNow incident {incident_sys_id}: {decision}")



def get_gemini_decision(short_description: str, description: str, priority: int) -> tuple[str, str]:
    prompt = build_prompt(short_description, description, priority)

    model = genai.GenerativeModel("gemini-3.6-flash")
    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    # Strip markdown code fences if Gemini adds them anyway
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:].strip()

    try:
        result = json.loads(raw_text)
        decision = result["decision"]
        message = result["message"]
    except (json.JSONDecodeError, KeyError):
        logger.error(f"Could not parse Gemini response, escalating by default. Raw: {raw_text}")
        decision = "escalate"
        message = "Could not determine an automated response; escalated for manual review."

    if decision not in ("respond", "ask", "escalate"):
        decision = "escalate"
        message = "Model returned an invalid decision; escalated for manual review."

    return decision, message



@app.get("/health")
def health():
    return {"status": "ok"}

class IncidentPayload(BaseModel):
    incident_sys_id: str
    number: str
    short_description: str
    description: Optional[str] = ""
    priority: int 


@app.post("/webhook", status_code=202)
async def webhook(payload: IncidentPayload, background_tasks: BackgroundTasks):
    if payload.incident_sys_id in PROCESSED_SYS_IDS:
        logger.info(f"Incident {payload.number} already processed. Skipping.")
        return {"status": "already processed", "number": payload.number}

    PROCESSED_SYS_IDS.add(payload.incident_sys_id)
    logger.info(f"Received incident {payload.number}: {payload.short_description}")

    background_tasks.add_task(process_incident, payload)

    return {"status": "accepted", "number": payload.number}


def process_incident(payload: IncidentPayload):
    try:
        decision, message = get_gemini_decision(
            payload.short_description, payload.description, payload.priority
        )
        logger.info(f"Incident {payload.number} -> decision={decision}, message={message}")
        write_back_to_servicenow(payload.incident_sys_id, decision, message)
    except Exception as e:
        logger.error(f"Failed to process incident {payload.number}: {e}")