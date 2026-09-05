# Reflection — Task 0: Agentic Incident Flow

## What was the hardest part?

The code wasn't the hard part — the environment was. I got stuck on a 401 error writing back to ServiceNow even though my password worked fine in the browser. Turned out newer PDIs block Basic Auth by default unless you add a specific role to the admin user — not mentioned anywhere in the guide.

The Gemini prompt also needed a few tries. It kept confidently answering a ticket that was supposed to be too vague. Adding real examples to the prompt fixed it — just telling it "ask when unsure" didn't.

## What would I improve with more time?

- A startup check that tests ServiceNow credentials immediately instead of failing on the first real ticket.
- Fake/mocked tests for Gemini and ServiceNow, so I don't need a new incident to test every prompt tweak.
- One retry on the Gemini call before escalating.