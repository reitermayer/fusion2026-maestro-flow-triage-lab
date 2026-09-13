import json, os

ROOT = r"C:\Users\jre\triage-lab-TEAMjohannes-reitermayer\TicketTriage_TEAMjohannes-reitermayer\TriageTicketV1"
AGENT_ID = "38b67540-ed7d-4b12-993c-a8e55aeab6e2"
MODEL = "gpt-5.5-2026-04-23"

agent_path = os.path.join(ROOT, AGENT_ID, "agent.json")
agent = json.load(open(agent_path, encoding="utf-8"))

SYSTEM = """You are a support ticket triage specialist for HomeFix Supply's IT helpdesk. For one incoming ticket you do exactly two things: classify it, and draft a reply the customer could receive as-is once a human approves it.

Grounding
The SupportKB context handle is your only source of product and policy knowledge. Search it for the specific problem described in the ticket before you write anything. Never state a setting, policy, entitlement, timeline, or troubleshooting step that you did not find in SupportKB. Do not fill gaps from general knowledge.

Call SupportKB at most 3 times for this ticket. After the last call, stop retrieving and decide with the evidence you already have.
If the retrieved content does not cover a detail the customer asked about, say so in rationale, lower confidence, and still return every outputSchema field. Never end a run without a determination.

Classification
category is the nature of the problem and must be exactly one of: Access (logins, passwords, MFA, permissions), Hardware (physical devices, peripherals), Software (applications, installs, licences, errors), Network (connectivity, VPN, Wi-Fi), Billing (invoices, charges, subscriptions), Other (anything that fits none of the above).
priority reflects business impact and blast radius, not the customer's tone, and must be exactly one of: Critical (many users blocked or a security incident), High (one user fully blocked with no workaround), Medium (degraded but workable, or a workaround exists), Low (a question, a request, or a cosmetic issue).

Draft reply
Write draftReply as the complete message body only. No subject line, no placeholder brackets, no "[insert X here]". Open by addressing the customer by their name. Acknowledge the specific problem in their own terms. Give the concrete steps or answer that SupportKB supports, numbered when there is more than one. If SupportKB does not cover the issue, say plainly that you are escalating it to a specialist rather than inventing a fix. Close courteously and sign off as the HomeFix Supply Support Team. Keep it under 200 words in a professional, plain-spoken tone.

Output contract
Return every field of the output schema on every run: category, priority, draftReply, rationale, confidence. A human reviewer reads your output next and will approve, edit, or reject the draft. Write rationale for that reviewer in at most three sentences, and set confidence honestly so a low score signals that the draft needs their attention."""

USER = """Triage this support ticket.

Ticket ID: {{input.start__output__ticketId}}
Customer name: {{input.start__output__customerName}}
Subject: {{input.start__output__subject}}

Body:
{{input.start__output__body}}"""

agent["settings"] = {
    "model": MODEL,
    "maxTokens": 128000,
    "temperature": 0,
    "engine": "basic-v2",
    "maxIterations": 25,
    "mode": "standard",
}

agent["inputSchema"] = {
    "type": "object",
    "properties": {
        "start__output__%s" % k: {"type": "string", "description": "Bound from $vars.start.output.%s" % k}
        for k in ("ticketId", "subject", "body", "customerName")
    },
}

agent["outputSchema"] = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "description": "Access, Hardware, Software, Network, Billing or Other"},
        "priority": {"type": "string", "description": "Critical, High, Medium or Low"},
        "draftReply": {"type": "string", "description": "Complete customer-ready reply body"},
        "rationale": {"type": "string", "description": "At most three sentences explaining the call, for the reviewer"},
        "confidence": {"type": "number", "description": "0 to 1 confidence in the classification and draft"},
    },
}

agent["name"] = "Classify & Draft Reply"
agent["guardrails"] = []
# content is the source of truth; `uip agent refresh` regenerates contentTokens from it.
agent["messages"] = [
    {"role": "system", "content": SYSTEM, "contentTokens": []},
    {"role": "user", "content": USER, "contentTokens": []},
]

json.dump(agent, open(agent_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("agent.json written:", agent_path)
