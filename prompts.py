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
   - "respond": if a knowledge base article clearly and specifically covers this exact problem. Write the solution from that article as the message.
   - "ask": if a knowledge base article MIGHT apply, but the incident is too vague to be sure. Write a short clarifying question as the message.
   - "escalate": if NONE of the knowledge base articles cover this problem. Write a short note that a human should handle it.
3. If unsure whether an article applies, prefer "ask" over "respond". If no article is even plausibly related, use "escalate".

Respond with ONLY valid JSON, no markdown, no other text, in exactly this format:
{{"decision": "respond" | "ask" | "escalate", "message": "short message text here"}}"""