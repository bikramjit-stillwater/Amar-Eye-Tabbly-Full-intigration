from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import os
import csv
import io
import re
from openpyxl import load_workbook

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TABBLY_API_KEY = os.getenv("API_KEY")
TABBLY_ORG_ID = os.getenv("ORG_ID")

# Single Agent Configuration
AMAR_EYE_AGENT_ID = 5565
AMAR_EYE_CAMPAIGN_ID = 2301
AGENT_NAME = "Amar Eye Yoga"

class CallRequest(BaseModel):
    phone: str
    name: str
    instruction: str
    agent_id: int

def get_custom_first_line(name: str) -> str:
    clean_name = str(name).strip()
    return f"Hello {clean_name}, I’m calling from Amar Eye Yoga. Thank you for connecting with us. Could you please tell me more about your eye problem?"

def clean_text(value):
    return str(value or "").strip()

def clean_phone(value):
    s = str(value or "").strip()
    if s.lower() == "none": return ""
    if s.endswith(".0"): s = s[:-2]
    s = re.sub(r"[^\d]", "", s)
    return f"+{s}" if not s.startswith("+") else s

def build_contact(phone, name, instruction):
    return {
        "phone_number": phone,
        "campaign_id": AMAR_EYE_CAMPAIGN_ID,
        "participant_identity": name,
        "use_agent_id": AMAR_EYE_AGENT_ID,
        "creator_by": "api",
        "custom_first_line": get_custom_first_line(name),
        "custom_instruction": instruction,
        "sip_call_id": "NA"
    }

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/agents")
def get_agents():
    # Returning just the one required agent
    return {
        "status": "success",
        "data": [{"id": AMAR_EYE_AGENT_ID, "agent_name": AGENT_NAME}]
    }

@app.post("/call")
def make_call(data: CallRequest):
    if not TABBLY_API_KEY:
        raise HTTPException(status_code=500, detail="API_KEY is missing")

    url = "https://www.tabbly.io/dashboard/agents/endpoints/add-campaign-contacts"
    payload = {
        "api_key": TABBLY_API_KEY,
        "contacts": [build_contact(clean_phone(data.phone), clean_text(data.name), clean_text(data.instruction))]
    }

    response = requests.post(url, json=payload, timeout=60)
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# ... (Include your existing bulk-upload and call-logs logic here)
