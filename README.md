# Task 0 — Agentic Incident Flow on ServiceNow PDI

## Demo Video
[Watch the demo](https://drive.google.com/file/d/1S183-ISuy_o_JIIIP3orKt6Pje91rT9q/view?usp=sharing)

## What this does

A new incident is created in ServiceNow → a FastAPI service asks Gemini to decide **respond**, **ask**, or **escalate** based only on 5 fixed knowledge base articles → the result is written back to the same ticket automatically.

## Setup

1. Clone and enter the repo, then set up the environment:
   ```
   git clone https://github.com/sherouk-mohamed/Agentic-Incident-Flow-on-PDI.git
   cd Agentic-Incident-Flow-on-PDI
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your Gemini API key and ServiceNow instance URL/credentials.

3. **Important:** grant your ServiceNow admin user the `snc_basic_auth_api_access` role (Users → admin → Roles → Edit), or the write-back API calls will fail with 401. Newer PDIs block Basic Auth by default.

4. Run the service:
   ```
   uvicorn main:app --reload --port 8000
   ```

5. In another terminal, expose it with ngrok:
   ```
   ngrok http 8000
   ```

6. In ServiceNow, create a Business Rule using `business_rule.js` (Table: Incident, When: after insert), replacing `YOUR_ENDPOINT` with your ngrok URL.

7. Create a test incident and watch the decision appear back on the ticket.

## Files

- `main.py` — the service (webhook, Gemini call, ServiceNow write-back)
- `prompts.py` — the exact Gemini prompt
- `kb_articles.json` — the 5 knowledge base articles
- `test_incidents.json` — 3 test tickets with expected decisions
- `business_rule.js` — ServiceNow trigger script
- `reflection.md` — what was hard, what I'd improve

## Screenshots

### Business Rule Setup
_(add screenshot)_

### Respond / Ask / Escalate — before & after
_(add screenshots)_

## Notes

- Duplicate incidents are only processed once (in-memory guard).
- Bad payloads return a clear `400` error — the service never crashes.
- If Gemini's response can't be parsed, it falls back to `escalate` instead of guessing.
