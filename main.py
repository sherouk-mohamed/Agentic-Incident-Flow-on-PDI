import os
import json
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("task0")

app = FastAPI(title="Task0 Sherouk")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERVICENOW_INSTANCE_URL = os.getenv("SERVICENOW_INSTANCE_URL")
SERVICENOW_USERNAME = os.getenv("SERVICENOW_USERNAME")
SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD")


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
async def webhook(payload: IncidentPayload):
    logger.info(f"Received incident {payload.number}: {payload.short_description}")
    return {"status": "accepted", "number": payload.number}