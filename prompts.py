import json
import os

with open(os.path.join(os.path.dirname(__file__), "kb_articles.json"), "r", encoding="utf-8") as f:
    KB_ARTICLES = json.load(f)["articles"]


def build_prompt(short_description: str, description: str, priority: int) -> str:
    kb_text = "\n".join(f"- (Article {a['id']}) {a['text']}" for a in KB_ARTICLES)
    return f"""You are a support ticket triage agent. You must decide what to do with a new incident using ONLY the knowledge base articles provided below. Do not use any outside knowledge.

KNOWLEDGE BASE ARTICLES (the only source you may use):
{kb_text}

INCIDENT:
Short description: {short_description}
Description: {description}
Priority: {priority}

INSTRUCTIONS:
1. Compare the incident against the knowledge base articles above.
2. Decide ONE of the following:
   - "respond": ONLY if the incident includes enough specific detail to be CONFIDENT a knowledge base article directly resolves it (e.g. mentions the specific device, error, or symptom the article describes). Write the solution from that article as the message.
   - "ask": if a knowledge base article might apply to the general topic, but the incident lacks specific details (e.g. just says "it doesn't work" without describing symptoms, error messages, or what was tried). This is the DEFAULT for vague reports. Write a short clarifying question as the message.
   - "escalate": if NONE of the knowledge base articles cover this problem's topic at all. Write a short note that a human should handle it.
3. Being vague is common. A short report like "it just doesn't work" or "having an issue" is NOT enough detail for "respond" — that must be "ask" instead. Reserve "respond" only for incidents with clear, specific symptoms matching an article.
4. If no article is even plausibly related to the topic, use "escalate".

EXAMPLES:
- Incident: "Printer not printing after office move" / "It was working yesterday. I tried turning it off and on." → respond (specific device + symptom clearly matches Article 1)
- Incident: "Cannot send email" / "It just doesn't work." → ask (mentions email, but no specific error, no detail on what's failing — too vague to confidently apply Article 2)
- Incident: "Request: annual leave approval" / "I would like to take next week off." → escalate (no knowledge base article covers HR/leave requests)

Respond with ONLY valid JSON, no markdown, no other text, in exactly this format:
{{"decision": "respond" | "ask" | "escalate", "message": "short message text here"}}"""