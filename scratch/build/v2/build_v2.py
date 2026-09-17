"""Build TriageTicketV2 (agent.json + context resource.json + TriageTicketV2.flow).

Run via Bash only. Never Write/Edit the .flow with the harness tools: this
workspace re-syncs .flow files after harness edits (see memory), while
Bash-driven writes are left alone.

Idempotent: re-running regenerates everything from the definitions in this
directory plus the scaffolded start node / trigger definition.
"""
import glob
import json
import os
import re
import uuid

SOLUTION = r"C:\Users\jre\triage-lab-TEAMjohannes-reitermayer\TicketTriage_TEAMjohannes-reitermayer"
ROOT = os.path.join(SOLUTION, "TriageTicketV2")
BUILD = os.path.dirname(os.path.abspath(__file__))
FLOW_PATH = os.path.join(ROOT, "TriageTicketV2.flow")

CTX_TYPE = "uipath.agent.resource.context.index.supportkb.e47fcbe5-bd8b-47fa-29dc-08df04e92605"
MODEL = "gpt-5.5-2026-04-23"          # same GA model as V1 so Batch B is comparable
ASSIGNEE = "user@example.com"

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
agent_dirs = [d for d in os.listdir(ROOT) if UUID_RE.match(d) and os.path.isdir(os.path.join(ROOT, d))]
assert len(agent_dirs) == 1, "expected exactly one inline-agent dir, found %r" % agent_dirs
AGENT_ID = agent_dirs[0]


def defnode(name):
    return json.load(open(os.path.join(BUILD, "def_%s.json" % name), encoding="utf-8"))["Data"]["Node"]


agent_def = defnode("uipath.agent.autonomous")
ctx_def = defnode(CTX_TYPE)
switch_def = defnode("core.logic.switch")
qf_def = defnode("uipath.human-in-the-loop.quick-form")
end_def = defnode("core.control.end")

# ---------------------------------------------------------------------------
# Node ids (single source of truth for every binding below)
# ---------------------------------------------------------------------------
N_START = "start"
N_AGENT = "classifyAndDraft"
N_CTX = "supportKbContext1"
N_ROUTE = "routeTicket"
N_URGENT = "urgentReview"
N_STANDARD = "standardReview"
N_END = "decisionRecorded"

INPUTS = [("ticketId", "Support ticket identifier"),
          ("subject", "Ticket subject line"),
          ("body", "Ticket body text"),
          ("customerName", "Name of the customer who raised the ticket")]

AGENT_OUTPUTS = [
    ("category", "string", "Access, Hardware, Software, Network, Billing, Noise or Other"),
    ("priority", "string", "Critical, High, Medium or Low"),
    ("draftReply", "string", "Complete customer-ready reply body; empty string when category is Noise"),
    ("rationale", "string", "At most three sentences explaining the classification, for the reviewer"),
    ("confidence", "number", "0 to 1 confidence in the classification and draft"),
    ("recommendedApproach", "string",
     "Two to four sentences of guidance for the human reviewer: the concrete next action, what to verify, "
     "and whether to approve, edit, or reject the draft"),
]

# ---------------------------------------------------------------------------
# Routing conditions. Defined ONCE; used verbatim by the Switch cases and by the
# End node's output expressions so the two can never drift apart. Switch case
# expressions are auto-evaluated JS (no =js: prefix); End outputs need =js:.
# ---------------------------------------------------------------------------
CATEGORY = "String($vars.%s.output.category || '').trim().toLowerCase()" % N_AGENT
PRIORITY = "String($vars.%s.output.priority || '').trim().toLowerCase()" % N_AGENT
CONFIDENCE = "Number($vars.%s.output.confidence)" % N_AGENT
# Auto-skip is the only path with no human in it, so a Noise call must also be
# confident. A low-confidence Noise ticket falls through to Standard Review
# instead of being silently dropped. Batch A's auto-reply scored 0.87.
NOISE_MIN_CONFIDENCE = 0.8
COND_NOISE = "%s === 'noise' && %s >= %s" % (CATEGORY, CONFIDENCE, NOISE_MIN_CONFIDENCE)
# The agent's priority enum is Critical/High/Medium/Low. Batch A's outage was
# already tagged Critical by V1; the flow just ignored it. 'urgent' is tolerated
# in case the model drifts from the enum.
COND_URGENT = "['critical', 'high', 'urgent'].indexOf(%s) !== -1" % PRIORITY

NOISE_DECISION = "AutoSkipped"
NOISE_FINAL_REPLY = "None - Auto-reply noise filtered"

# ---------------------------------------------------------------------------
# agent.json
# ---------------------------------------------------------------------------
SYSTEM = """You are a support ticket triage specialist for HomeFix Supply's IT helpdesk. For one incoming ticket you do three things: classify it, draft a reply the customer could receive as-is once a human approves it, and tell the human reviewer what you recommend they do next.

Grounding
The SupportKB context handle is your only source of product and policy knowledge. Search it for the specific problem described in the ticket before you write anything. Never state a setting, policy, entitlement, timeline, or troubleshooting step that you did not find in SupportKB. Do not fill gaps from general knowledge.

Call SupportKB at most 3 times for this ticket. After the last call, stop retrieving and decide with the evidence you already have.
If the retrieved content does not cover a detail the customer asked about, say so in rationale, lower confidence, and still return every outputSchema field. Never end a run without a determination.
Do not search SupportKB for a ticket you classify as Noise; there is nothing to look up.

Step 1: Noise check (do this first)
Some incoming messages are not tickets at all. Classify category as Noise when the message is an automated or machine-generated notice with no actionable request from a person, for example: out-of-office or vacation auto-replies, "this is an automated response" notices, delivery failure or bounce reports, read receipts, newsletters, marketing mail, or system notifications. Strong signals: the sender name looks like an automated mailbox (auto-reply, no-reply, mailer-daemon), the subject starts with "Out of Office" or "Automatic reply", or the body says it is an automated response. A real person asking for help is never Noise, even if the message is short or off-topic.
For Noise: set priority to Low, set draftReply to an empty string (a reply to an automated sender only creates mail loops), set confidence honestly, and write recommendedApproach as: no reply needed, close the ticket as automated noise, and the one signal that identifies it as automated.

Step 2: Classification
category is the nature of the problem and must be exactly one of: Access (logins, passwords, MFA, permissions), Hardware (physical devices, peripherals), Software (applications, installs, licences, errors), Network (connectivity, VPN, Wi-Fi), Billing (invoices, charges, subscriptions), Noise (automated notices, see Step 1), Other (anything that fits none of the above).
priority reflects business impact and blast radius, not the customer's tone, and must be exactly one of: Critical, High, Medium, Low.
- Critical: an operational outage or a security incident. Many users blocked, a site, warehouse, distribution center, store, or production system down, revenue or shipments stopped, a stated hard cutoff at risk. Words like "all", "everyone", "down", "stopped", "trucks waiting", "cannot ship", or "within the hour" from a site or team lead point here. Treat any message describing halted operations as Critical even when SupportKB has no article for the system involved.
- High: one user fully blocked with no workaround (cannot work at all), or a repeated failure of a previously escalated issue that now prevents core duties.
- Medium: degraded but workable, or a workaround exists.
- Low: a question, a request, an evaluation, a cosmetic issue, or Noise.
Tickets with Critical or High priority are fast-tracked to an urgent reviewer. Do not inflate priority to get attention, and do not deflate a genuine outage because the knowledge base is silent about it.

Step 3: Draft reply
Write draftReply as the complete message body only. No subject line, no placeholder brackets, no "[insert X here]", no prefixes or labels before the greeting. Open by addressing the customer by their name. Acknowledge the specific problem in their own terms. Give the concrete steps or answer that SupportKB supports, numbered when there is more than one. Close courteously and sign off as the HomeFix Supply Support Team. Keep it under 200 words in a professional, plain-spoken tone.
- Critical or High: lead with the fact that this is being treated as an urgent incident and is being escalated immediately to the on-call specialist team, and ask for the single most useful detail for the responders (site, number of users affected, a direct phone number). Include the Service Desk contact details only if SupportKB provides them. Do not describe an urgent outage as something you "cannot find a procedure for"; the customer needs ownership, not a search report.
- Frustrated, repeatedly delayed, or escalating customers (for example someone threatening to raise the issue with an executive): write with empathy first. Acknowledge the history and the impact on their work in one sentence, take explicit ownership ("I am taking ownership of this ticket and escalating it today"), and avoid defensive or procedural language. Never promise a date, a replacement, a refund, or a loaner unless SupportKB grants that entitlement; if it does, state it plainly.
- If SupportKB does not cover the issue, say plainly that you are escalating it to a specialist rather than inventing a fix.

Step 4: Recommended approach (for the reviewer, not the customer)
Write recommendedApproach as two to four sentences addressed to the human reviewer who decides whether to approve, edit, or reject your draft. It must name a concrete next action, not restate the draft. Cover: (1) what you recommend they do with the draft (approve as-is, edit a specific part, or reject and why); (2) the operational action you recommend beyond the email, for example escalate to the network on-call engineer, authorize an expedited loaner under the entitlement in SupportKB, dispatch on-site support, or close as noise; (3) anything they should verify first, such as an entitlement, a prior ticket reference, or a warranty status. Where SupportKB defines an entitlement or SLA, cite it; where it is silent, say so and frame the action as a judgment call for the reviewer. For Critical tickets the first sentence must be the escalation step. For customers threatening escalation, recommend the concrete relief the reviewer can authorize.

Output contract
Return every field of the output schema on every run: category, priority, draftReply, rationale, confidence, recommendedApproach. Write rationale for the reviewer in at most three sentences, and set confidence honestly so a low score signals that the draft needs their attention."""

USER = """Triage this support ticket.

Ticket ID: {{input.start__output__ticketId}}
Customer name: {{input.start__output__customerName}}
Subject: {{input.start__output__subject}}

Body:
{{input.start__output__body}}"""

agent_path = os.path.join(ROOT, AGENT_ID, "agent.json")
agent = json.load(open(agent_path, encoding="utf-8"))
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
        for k, _ in INPUTS
    },
}
agent["outputSchema"] = {
    "type": "object",
    "properties": {k: {"type": t, "description": d} for k, t, d in AGENT_OUTPUTS},
}
agent["name"] = "Classify, Draft & Recommend"
agent["guardrails"] = []
# content is the source of truth; `uip agent refresh` regenerates contentTokens from it.
agent["messages"] = [
    {"role": "system", "content": SYSTEM, "contentTokens": []},
    {"role": "user", "content": USER, "contentTokens": []},
]
json.dump(agent, open(agent_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("agent.json written:", agent_path)

# ---------------------------------------------------------------------------
# Context resource (SupportKB, Shared folder) - reuse the existing id if present
# ---------------------------------------------------------------------------
res_root = os.path.join(ROOT, AGENT_ID, "resources")
existing = [os.path.basename(p) for p in glob.glob(os.path.join(res_root, "*")) if os.path.isdir(p)]
CTX_RES = existing[0] if existing else str(uuid.uuid4())
res_dir = os.path.join(res_root, CTX_RES)
os.makedirs(res_dir, exist_ok=True)
QUERY_HINT = "The support problem described in the ticket, phrased as a knowledge base search query"
resource = {
    "$resourceType": "context",
    "name": "SupportKB",
    "description": ctx_def["description"],
    "folderPath": "Shared",
    "indexName": "SupportKB",
    "id": CTX_RES,
    "referenceKey": "",
    "settings": {
        "query": {"description": QUERY_HINT, "variant": "dynamic"},
        "folderPathPrefix": {"variant": "static", "value": ""},
        "threshold": 0,
        "resultCount": 5,
        "retrievalMode": "semantic",
        "fileExtension": {"value": "All"},
    },
    "contextType": "index",
}
json.dump(resource, open(os.path.join(res_dir, "resource.json"), "w", encoding="utf-8"), indent=2)
print("resource.json written:", res_dir)

# ---------------------------------------------------------------------------
# .flow
# ---------------------------------------------------------------------------
flow = json.load(open(FLOW_PATH, encoding="utf-8"))
flow["runtime"] = "maestro"

start = next(n for n in flow["nodes"] if n["type"] == "core.trigger.manual")
start["id"] = N_START
start["display"] = {"label": "Support ticket received", "icon": "play"}
start["outputs"] = {"output": {"type": "object",
                               "description": "Data passed when manually triggering the process.",
                               "source": "null", "var": "output"}}

agent_node = {
    "id": N_AGENT,
    "type": "uipath.agent.autonomous",
    "typeVersion": agent_def["version"],
    "display": {"label": "Classify, Draft & Recommend", "icon": "autonomous-agent"},
    "inputs": {
        "source": AGENT_ID,
        "agentInputVariables": [
            {"id": "start__output__%s" % k, "type": "string",
             "binding": "=$vars.start.output.%s" % k,
             "description": "Bound from $vars.start.output.%s" % k} for k, _ in INPUTS],
        "agentOutputVariables": [{"id": k, "type": t} for k, t, _ in AGENT_OUTPUTS],
    },
    "outputs": {
        "output": {"type": "object", "description": "Agent response", "var": "output",
                   "properties": {k: {"type": t} for k, t, _ in AGENT_OUTPUTS}},
        "error": {"type": "object", "description": "Error information if the node fails",
                  "source": "=Error", "var": "error"},
    },
}

ctx_node = {
    "id": N_CTX,
    "type": CTX_TYPE,
    "typeVersion": ctx_def["version"],
    "display": {"label": "SupportKB", "icon": "context"},
    "inputs": {
        "source": CTX_RES,
        "id": N_CTX,
        "name": "SupportKB",
        "description": ctx_def["description"],
        "referenceKey": "",
        "indexName": "SupportKB",
        "folderPath": "Shared",
        "resultCount": 5,
        "threshold": 0,
        "retrievalMode": "semantic",
        "query": {"mode": "prompt", "textValue": "", "promptValue": QUERY_HINT, "argumentPath": ""},
        "fileExtension": "All",
        "folderPathPrefix": {"mode": "text-builder", "textValue": "", "promptValue": "", "argumentPath": ""},
    },
}

route_node = {
    "id": N_ROUTE,
    "type": "core.logic.switch",
    "typeVersion": switch_def["version"],
    "display": {"label": "Route by category & priority", "icon": "between-horizontal-start"},
    "inputs": {
        "cases": [
            {"id": "noise", "label": "Noise: auto-skip", "expression": COND_NOISE},
            {"id": "urgent", "label": "Critical / High: urgent review", "expression": COND_URGENT},
        ]
    },
    "outputs": {
        "matchedCase": {"type": "string", "description": "The label of the matched case", "var": "matchedCase"},
        "matchedCaseId": {"type": "string",
                          "description": "The ID of the matched case (\"default\" for the default branch)",
                          "var": "matchedCaseId"},
    },
}

OUTCOMES = [("approve", "Approve", True),
            ("modifyandsend", "Modify & Send", False),
            ("reject", "Reject", False)]
OUTCOME_NAMES = [n for _, n, _ in OUTCOMES]


def field(fid, label, ftype, binding=None, direction="input", variable=None):
    f = {"id": fid, "label": label, "type": ftype, "direction": direction}
    if binding:
        f["binding"] = binding
    if variable:
        f["variable"] = variable
    return f


def review_node(node_id, label, title, task_priority, draft_var, note_var, lead_fields):
    """Quick Form task. `lead_fields` are shown first so the reviewer sees the
    routing signal (priority / guidance) before the ticket text."""
    common_ticket = [
        field("ticketid", "Ticket ID", "string", "vars.ticketId"),
        field("customername", "Customer Name", "string", "vars.customerName"),
        field("subject", "Subject", "string", "vars.subject"),
        field("body", "Ticket Body", "string", "vars.body"),
    ]
    agent_fields = [
        field("category", "Category", "string", "vars.%s.output.category" % N_AGENT),
        field("priority", "Priority", "string", "vars.%s.output.priority" % N_AGENT),
        field("confidence", "Confidence", "number", "vars.%s.output.confidence" % N_AGENT),
        field("rationale", "Agent Rationale", "string", "vars.%s.output.rationale" % N_AGENT),
        field("recommendedapproach", "Recommended Approach (for reviewer)", "string",
              "vars.%s.output.recommendedApproach" % N_AGENT),
    ]
    lead = [f for f in agent_fields if f["id"] in lead_fields]
    rest = [f for f in agent_fields if f["id"] not in lead_fields]
    # Batch A reviewers typed notes into the draft itself ("soften the tone!",
    # "High business impact:") and those notes became part of finalReply. The
    # separate note field gives them somewhere else to write.
    fields = lead + common_ticket + rest + [
        field("draftreply", "Draft Reply (sent to the customer; edit before Modify & Send)", "string",
              "vars.%s.output.draftReply" % N_AGENT, direction="inOut", variable=draft_var),
        field("reviewernote", "Reviewer Note (internal, never sent to the customer)", "string",
              direction="output", variable=note_var),
    ]
    return {
        "id": node_id,
        "type": "uipath.human-in-the-loop.quick-form",
        "typeVersion": qf_def["version"],
        "display": {"label": label, "icon": "users"},
        "inputs": {
            "title": title,
            "recipient": {"channels": ["ActionCenter"], "connections": {},
                          "assignee": {"type": "user", "value": ASSIGNEE}},
            "priority": task_priority,
            "schema": {
                "schemaId": str(uuid.uuid4()),
                "fields": fields,
                "outcomes": [{"id": i, "name": n, "type": "string", "isPrimary": p, "action": "Continue"}
                             for i, n, p in OUTCOMES],
            },
        },
        "outputs": {
            "output": {"type": "object", "description": "Task result data", "source": "=result", "var": "output",
                       "properties": {"draftreply": {"type": "string"},
                                      "reviewernote": {"type": "string"},
                                      "Action": {"type": "string", "enum": OUTCOME_NAMES, "default": "Approve"}}},
            "status": {"type": "string", "description": "Task completion status", "source": "=result.Action",
                       "var": "status", "enum": OUTCOME_NAMES, "default": "Approve"},
        },
    }


urgent_node = review_node(
    N_URGENT, "Urgent Review", "URGENT: Review Draft Reply (Critical/High impact)", "High",
    "vars.urgentDraftReply", "vars.urgentReviewerNote", lead_fields=("priority", "recommendedapproach"))
standard_node = review_node(
    N_STANDARD, "Standard Review", "Review Draft Reply", "Medium",
    "vars.standardDraftReply", "vars.standardReviewerNote", lead_fields=("recommendedapproach",))


def js(expr):
    return "=js:" + expr


# Each End output picks the value from whichever branch actually ran. The
# ternaries short-circuit, so the un-run task node is never dereferenced.
end_node = {
    "id": N_END,
    "type": "core.control.end",
    "typeVersion": end_def["version"],
    "display": {"label": "Decision Recorded", "icon": "circle-check"},
    "inputs": {},
    "outputs": {
        "decision": {"type": "string", "source": js(
            "(%s) ? %s : ((%s) ? $vars.%s.status : $vars.%s.status)"
            % (COND_NOISE, json.dumps(NOISE_DECISION), COND_URGENT, N_URGENT, N_STANDARD))},
        "finalReply": {"type": "string", "source": js(
            "(%s) ? %s : ((%s) ? $vars.%s.output.draftreply : $vars.%s.output.draftreply)"
            % (COND_NOISE, json.dumps(NOISE_FINAL_REPLY), COND_URGENT, N_URGENT, N_STANDARD))},
        "category": {"type": "string", "source": js("$vars.%s.output.category" % N_AGENT)},
        "priority": {"type": "string", "source": js("$vars.%s.output.priority" % N_AGENT)},
        "recommendedApproach": {"type": "string", "source": js("$vars.%s.output.recommendedApproach" % N_AGENT)},
        "reviewerNote": {"type": "string", "source": js(
            "(%s) ? \"\" : ((%s) ? ($vars.%s.output.reviewernote || \"\") : ($vars.%s.output.reviewernote || \"\"))"
            % (COND_NOISE, COND_URGENT, N_URGENT, N_STANDARD))},
    },
}

flow["nodes"] = [start, agent_node, ctx_node, route_node, urgent_node, standard_node, end_node]


def edge(sn, sp, tn, tp="input"):
    slug = "".join(p.capitalize() if i else p for i, p in enumerate(sp.split("-")))
    return {"id": "edge_%s_%s_%s_%s" % (sn, slug, tn, tp),
            "sourceNodeId": sn, "sourcePort": sp, "targetNodeId": tn, "targetPort": tp}


flow["edges"] = [
    edge(N_START, "output", N_AGENT),
    edge(N_AGENT, "context", N_CTX),
    edge(N_AGENT, "success", N_ROUTE),
    edge(N_ROUTE, "case-noise", N_END),
    edge(N_ROUTE, "case-urgent", N_URGENT),
    edge(N_ROUTE, "default", N_STANDARD),
] + [
    # One edge per reviewer outcome, the shape Studio Web writes and deployed V1
    # ran with. A single `completed` edge gets re-mapped to the primary outcome
    # only, leaving Modify & Send / Reject unwired. The handles are declared by
    # patch_v2_outcome_handles.py, which must run after `flow format`.
    edge(nid, "outcome-%s" % oid, N_END) for nid in (N_URGENT, N_STANDARD) for oid, _, _ in OUTCOMES
]

trigger_defs = [d for d in flow["definitions"] if d.get("nodeType") == "core.trigger.manual"]
flow["definitions"] = trigger_defs + [agent_def, ctx_def, switch_def, qf_def, end_def]

OUT_VARS = [
    ("decision", "Reviewer decision (Approve, Modify & Send, Reject) or AutoSkipped for noise"),
    ("finalReply", "The reply text as approved or edited by the reviewer; a fixed marker for auto-skipped noise"),
    ("category", "Ticket category assigned by the agent (includes Noise)"),
    ("priority", "Ticket priority assigned by the agent"),
    ("recommendedApproach", "Agent guidance to the reviewer on the next action"),
    ("reviewerNote", "Internal note from the reviewer; empty for auto-skipped noise"),
]
flow["variables"] = {
    "globals": [
        {"id": k, "direction": "in", "type": "string", "description": d, "triggerNodeId": N_START}
        for k, d in INPUTS
    ] + [
        {"id": k, "direction": "out", "type": "string", "description": d} for k, d in OUT_VARS
    ],
    "nodes": [
        {"id": "%s.output" % N_START, "type": "object",
         "description": "Data passed when manually triggering the process.",
         "binding": {"nodeId": N_START, "outputId": "output"}},
        {"id": "%s.output" % N_AGENT, "type": "object", "description": "Agent response",
         "binding": {"nodeId": N_AGENT, "outputId": "output"}},
        {"id": "%s.error" % N_AGENT, "type": "object", "description": "Error information if the node fails",
         "binding": {"nodeId": N_AGENT, "outputId": "error"}},
        {"id": "%s.matchedCase" % N_ROUTE, "type": "string", "description": "The label of the matched case",
         "binding": {"nodeId": N_ROUTE, "outputId": "matchedCase"}},
        {"id": "%s.matchedCaseId" % N_ROUTE, "type": "string", "description": "The ID of the matched case",
         "binding": {"nodeId": N_ROUTE, "outputId": "matchedCaseId"}},
    ] + [
        e for nid in (N_URGENT, N_STANDARD) for e in (
            {"id": "%s.output" % nid, "type": "object", "description": "Task result data",
             "binding": {"nodeId": nid, "outputId": "output"}},
            {"id": "%s.status" % nid, "type": "string", "description": "Task completion status",
             "binding": {"nodeId": nid, "outputId": "status"}},
        )
    ] + [
        {"id": "%s.%s" % (N_END, k), "type": "string", "binding": {"nodeId": N_END, "outputId": k}}
        for k, _ in OUT_VARS
    ],
}

# Placeholder layout; `uip maestro flow format` owns the final positions.
flow["layout"] = {"nodes": {n["id"]: {"position": {"x": 0, "y": 0},
                                      "size": {"width": 96, "height": 96},
                                      "collapsed": False} for n in flow["nodes"]}}

json.dump(flow, open(FLOW_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("flow written:", FLOW_PATH)
print("agent id:", AGENT_ID)
print("context resource uuid:", CTX_RES)
print("switch conditions:")
print("  noise :", COND_NOISE)
print("  urgent:", COND_URGENT)
