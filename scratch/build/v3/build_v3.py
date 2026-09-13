"""Build TriageTicketV3 (two inline agents + context resources + TriageTicketV3.flow).

V3 = V2's evidence-driven routing plus a safe auto-resolve path. A ticket is only
auto-resolved (no human, finalReply = draftReply) when ALL of these hold:
  1. checkSafetyGate (deterministic script, gate_check_safety.js): not Noise, not
     Critical/High, Low/Medium priority, confidence >= 0.85, kbCovered === true,
     kbGaps reported and empty, needsStaffAction === false, every kbSources entry
     is a real SupportKB article id, and the draft does not escalate, promise
     follow-up, leak KB gaps, or carry placeholders.
  2. verifyGrounding (independent inline agent with its own SupportKB handle)
     re-checks every claim in the draft and every question in the ticket.
  3. checkVerification (deterministic script, gate_check_verification.js): the
     verifier's booleans are strictly true and both finding lists are empty.
Any failure, missing field, or malformed value routes to a human task instead.

Run via Bash only (see memory: harness Write/Edit on a .flow gets re-synced).
Build chain (from the solution dir):
  python ../scratch/build/v3/build_v3.py
  uip agent refresh --inline-in-flow --path TriageTicketV3/<drafter>   (and <verifier>)
  uip maestro flow format TriageTicketV3/TriageTicketV3.flow
  python ../scratch/build/v3/patch_v3_outcome_handles.py
  uip maestro flow validate TriageTicketV3/TriageTicketV3.flow
"""
import glob
import json
import os
import uuid

SOLUTION = r"C:\Users\jre\triage-lab-TEAMjohannes-reitermayer\TicketTriage_TEAMjohannes-reitermayer"
ROOT = os.path.join(SOLUTION, "TriageTicketV3")
BUILD = os.path.dirname(os.path.abspath(__file__))
FLOW_PATH = os.path.join(ROOT, "TriageTicketV3.flow")

CTX_TYPE = "uipath.agent.resource.context.index.supportkb.e47fcbe5-bd8b-47fa-29dc-08df04e92605"
MODEL = "gpt-5.5-2026-04-23"          # same GA model as V1/V2 so batches stay comparable
ASSIGNEE = "johannes.reitermayer@gmail.com"

# Inline agent project ids from `uip agent init --inline-in-flow` (2026-09-13).
DRAFTER_ID = "bf42e911-6500-4286-918b-2644bbfd096c"
VERIFIER_ID = "8f46a36b-9558-41a7-a053-a889f8c4de25"
for d in (DRAFTER_ID, VERIFIER_ID):
    assert os.path.isfile(os.path.join(ROOT, d, "agent.json")), "missing inline agent " + d


def defnode(name):
    return json.load(open(os.path.join(BUILD, "def_%s.json" % name), encoding="utf-8"))["Data"]["Node"]


def read_script(name):
    return open(os.path.join(BUILD, name), encoding="utf-8").read().strip() + "\n"


agent_def = defnode("uipath.agent.autonomous")
ctx_def = defnode(CTX_TYPE)
script_def = defnode("core.action.script")
switch_def = defnode("core.logic.switch")
qf_def = defnode("uipath.human-in-the-loop.quick-form")
end_def = defnode("core.control.end")

# ---------------------------------------------------------------------------
# Node ids (single source of truth for every binding below)
# ---------------------------------------------------------------------------
N_START = "start"
N_AGENT = "classifyAndDraft"
N_AGENT_CTX = "draftSupportKb"
N_GATE = "checkSafetyGate"
N_ROUTE = "routeTicket"
N_VERIFY = "verifyGrounding"
N_VERIFY_CTX = "verifySupportKb"
N_VCHECK = "checkVerification"
N_DECIDE = "autoResolveDecision"
N_URGENT = "urgentReview"
N_STANDARD = "standardReview"
N_GROUNDING = "groundingReview"
N_END_SKIPPED = "autoSkipped"
N_END_RESOLVED = "autoResolved"
N_END_URGENT = "urgentReviewed"
N_END_STANDARD = "standardReviewed"
N_END_GROUNDING = "groundingReviewed"

INPUTS = [("ticketId", "Support ticket identifier"),
          ("subject", "Ticket subject line"),
          ("body", "Ticket body text"),
          ("customerName", "Name of the customer who raised the ticket")]

STRING_LIST = {"type": "array", "items": {"type": "string"}}

AGENT_OUTPUTS = [
    ("category", {"type": "string"}, "Access, Hardware, Software, Network, Billing, Noise or Other"),
    ("priority", {"type": "string"}, "Critical, High, Medium or Low"),
    ("draftReply", {"type": "string"}, "Complete customer-ready reply body; empty string when category is Noise"),
    ("rationale", {"type": "string"}, "At most three sentences explaining the classification, for the reviewer"),
    ("confidence", {"type": "number"}, "0 to 1 confidence in the classification and draft"),
    ("recommendedApproach", {"type": "string"},
     "Two to four sentences of guidance for the human reviewer: the concrete next action, what to verify, "
     "and whether to approve, edit, or reject the draft"),
    ("kbCovered", {"type": "boolean"},
     "true only if retrieved SupportKB content fully answers every question and request in the ticket and "
     "supports every fact in draftReply; false if SupportKB is silent, partial, or you are unsure"),
    ("kbSources", STRING_LIST,
     "SupportKB article ids (for example kb-01-password-reset) whose retrieved content supports draftReply; "
     "empty when nothing was retrieved"),
    ("kbGaps", STRING_LIST,
     "Each question, request, or detail in the ticket that retrieved SupportKB content does not answer; "
     "empty only when there is no gap"),
    ("needsStaffAction", {"type": "boolean"},
     "true if resolving the ticket needs a HomeFix staff member to do anything beyond sending this reply "
     "(approve an exception, look up a record, escalate, dispatch, chase an approver); false if the reply "
     "alone resolves it"),
]

VERIFIER_OUTPUTS = [
    ("draftGrounded", {"type": "boolean"},
     "true only if every factual claim in the draft is stated in retrieved SupportKB content"),
    ("answersEveryQuestion", {"type": "boolean"},
     "true only if the draft fully answers every question and request in the ticket"),
    ("unsupportedClaims", STRING_LIST,
     "Each claim in the draft that retrieved SupportKB content does not state, quoted from the draft; empty if none"),
    ("unansweredQuestions", STRING_LIST,
     "Each question or request in the ticket the draft does not fully answer; empty if none"),
    ("verdictNotes", {"type": "string"},
     "At most three sentences for a human reviewer: which articles you checked and what failed, if anything"),
]

NOISE_DECISION = "AutoSkipped"
NOISE_FINAL_REPLY = "None - Auto-reply noise filtered"
RESOLVED_DECISION = "AutoResolved"

KB_CATALOG = """kb-01-password-reset: Password reset
kb-02-vpn-setup: VPN setup
kb-03-expense-reports: Expense reports and duplicate charges
kb-04-mfa-enrollment: Multi-factor authentication (MFA)
kb-05-software-requests: Requesting software
kb-06-email-signature: Email, signature and shared mailboxes
kb-07-printers: Printing
kb-08-guest-wifi: Wi-Fi and guest access
kb-09-laptop-hardware: Laptops and hardware
kb-10-phishing: Reporting phishing and suspicious email
kb-11-onboarding: New hire IT onboarding
kb-12-meeting-rooms: Meeting rooms and AV
kb-13-hr-portal-access: HR portal and payslip access
kb-14-service-desk: Contacting the Service Desk"""

# ---------------------------------------------------------------------------
# Drafter agent (V2 prompt + knowledge coverage self-assessment)
# ---------------------------------------------------------------------------
DRAFTER_SYSTEM = """You are a support ticket triage specialist for HomeFix Supply's IT helpdesk. For one incoming ticket you do four things: classify it, draft a reply the customer could receive, tell the human reviewer what you recommend they do next, and state honestly how much of the ticket SupportKB actually covers.

Your coverage assessment decides whether the reply may be sent with no human review. Overstating coverage can send a customer an answer nobody vetted; understating it only costs a quick human review. When in doubt, report a gap.

Grounding
The SupportKB context handle is your only source of product and policy knowledge. Search it for the specific problem described in the ticket before you write anything. Never state a setting, policy, entitlement, timeline, URL, contact detail, or troubleshooting step that you did not find in retrieved SupportKB content. Do not fill gaps from general knowledge.

SupportKB contains these articles. Cite them by id, exactly as written:
""" + KB_CATALOG + """

Call SupportKB at most 3 times for this ticket. After the last call, stop retrieving and decide with the evidence you already have.
If the retrieved content does not cover a detail the customer asked about, list it in kbGaps, say so in rationale, lower confidence, and still return every outputSchema field. Never end a run without a determination.
Do not search SupportKB for a ticket you classify as Noise; there is nothing to look up.

Step 1: Noise check (do this first)
Some incoming messages are not tickets at all. Classify category as Noise when the message is an automated or machine-generated notice with no actionable request from a person, for example: out-of-office or vacation auto-replies, "this is an automated response" notices, delivery failure or bounce reports, read receipts, newsletters, marketing mail, or system notifications. Strong signals: the sender name looks like an automated mailbox (auto-reply, no-reply, mailer-daemon), the subject starts with "Out of Office" or "Automatic reply", or the body says it is an automated response. A real person asking for help is never Noise, even if the message is short or off-topic.
For Noise: set priority to Low, set draftReply to an empty string (a reply to an automated sender only creates mail loops), set kbCovered to false, kbSources and kbGaps to empty lists, needsStaffAction to false, set confidence honestly, and write recommendedApproach as: no reply needed, close the ticket as automated noise, and the one signal that identifies it as automated.

Step 2: Classification
category is the nature of the problem and must be exactly one of: Access (logins, passwords, MFA, permissions), Hardware (physical devices, peripherals), Software (applications, installs, licences, errors), Network (connectivity, VPN, Wi-Fi), Billing (invoices, charges, subscriptions, expenses), Noise (automated notices, see Step 1), Other (anything that fits none of the above).
priority reflects business impact and blast radius, not the customer's tone, and must be exactly one of: Critical, High, Medium, Low.
- Critical: an operational outage or a security incident. Many users blocked, a site, warehouse, distribution center, store, or production system down, revenue or shipments stopped, a stated hard cutoff at risk. Words like "all", "everyone", "down", "stopped", "trucks waiting", "cannot ship", or "within the hour" from a site or team lead point here. Treat any message describing halted operations as Critical even when SupportKB has no article for the system involved.
- High: one user fully blocked with no workaround (cannot work at all), or a repeated failure of a previously escalated issue that now prevents core duties.
- Medium: degraded but workable, or a workaround exists.
- Low: a question, a request, an evaluation, a cosmetic issue, or Noise.
Tickets with Critical or High priority are fast-tracked to an urgent reviewer. Do not inflate priority to get attention, and do not deflate a genuine outage because the knowledge base is silent about it.

Step 3: Draft reply
Write draftReply as the complete message body only. No subject line, no placeholder brackets, no "[insert X here]", no prefixes or labels before the greeting. Open by addressing the customer by their name. Acknowledge the specific problem in their own terms. Give the concrete steps or answer that SupportKB supports, numbered when there is more than one. Close courteously and sign off as the HomeFix Supply Support Team. Keep it under 200 words in a professional, plain-spoken tone. Never mention SupportKB, the knowledge base, articles, or runbooks to the customer.
- Fully covered tickets: the reply must stand on its own. Answer every question with the SupportKB steps, and do not promise follow-up, escalation, or a human looking into it, because none will happen.
- Critical or High: lead with the fact that this is being treated as an urgent incident and is being escalated immediately to the on-call specialist team, and ask for the single most useful detail for the responders (site, number of users affected, a direct phone number). Include the Service Desk contact details only if SupportKB provides them. Do not describe an urgent outage as something you "cannot find a procedure for"; the customer needs ownership, not a search report.
- Frustrated, repeatedly delayed, or escalating customers (for example someone threatening to raise the issue with an executive or to work around the process): write with empathy first. Acknowledge the history and the impact on their work in one sentence, take explicit ownership ("I am taking ownership of this ticket and escalating it today"), and avoid defensive or procedural language. Never promise a date, a replacement, a refund, a reimbursement, or a loaner unless SupportKB grants that entitlement; if it does, state it plainly.
- If SupportKB does not cover the issue, say plainly that you are escalating it to a specialist rather than inventing a fix, and give the customer concrete next steps SupportKB does support.

Step 4: Recommended approach (for the reviewer, not the customer)
Write recommendedApproach as two to four sentences addressed to the human reviewer who decides whether to approve, edit, or reject your draft. It must name a concrete next action, not restate the draft. Cover: (1) what you recommend they do with the draft (approve as-is, edit a specific part, or reject and why); (2) the operational action you recommend beyond the email, for example escalate to the network on-call engineer, route to the finance or expenses queue, authorize an expedited loaner under the entitlement in SupportKB, dispatch on-site support, or close as noise; (3) anything they should verify first, such as an entitlement, a prior ticket reference, or a warranty status. Where SupportKB defines an entitlement or SLA, cite it; where it is silent, say so and frame the action as a judgment call for the reviewer. For Critical tickets the first sentence must be the escalation step. For customers threatening escalation, recommend the concrete relief the reviewer can authorize.

Step 5: Knowledge coverage (decides whether a human reviews the reply)
- kbSources: the ids of the SupportKB articles whose retrieved content supports your draft, for example ["kb-04-mfa-enrollment", "kb-06-email-signature"]. Only cite an article whose content you actually retrieved in this run. Never cite an id that is not in the list above.
- kbGaps: first list every separate question and request in the ticket, including implied ones ("is there any way to still get reimbursed?", "and will that sync everywhere?"). For each one, check whether retrieved SupportKB content answers it directly. Add every one that is unanswered or only partly answered to kbGaps, in a few words each. Also add any fact in your draft you could not find in retrieved content. kbGaps is empty only when nothing is missing.
- needsStaffAction: true when resolving the ticket needs a HomeFix staff member to do something beyond this reply, for example approving a policy exception, looking up or chasing an existing request, escalating, dispatching someone, or changing an account on the customer's behalf. Steps the customer can take themselves, including submitting a documented catalog request, do not count.
- kbCovered: true only when kbGaps is empty, kbSources is not empty, and the draft contains nothing that retrieved SupportKB content does not state. Otherwise false. A partial answer is false. A policy the article implies but does not state is false.

Output contract
Return every field of the output schema on every run: category, priority, draftReply, rationale, confidence, recommendedApproach, kbCovered, kbSources, kbGaps, needsStaffAction. Write rationale for the reviewer in at most three sentences, and set confidence honestly so a low score signals that the draft needs their attention."""

DRAFTER_USER = """Triage this support ticket.

Ticket ID: {{input.start__output__ticketId}}
Customer name: {{input.start__output__customerName}}
Subject: {{input.start__output__subject}}

Body:
{{input.start__output__body}}"""

# ---------------------------------------------------------------------------
# Verifier agent (independent grounding audit, never rewrites)
# ---------------------------------------------------------------------------
VERIFIER_SYSTEM = """You are an independent grounding auditor for HomeFix Supply's IT helpdesk. Another agent drafted a reply to a support ticket and says SupportKB fully covers it. If you confirm that, the reply is sent to the customer with no human review. Your job is to catch any claim or unanswered question that would make that unsafe. You did not write the draft and you must not trust its author's citations or confidence.

Grounding
The SupportKB context handle is your only source of truth. Search it yourself for the topics in the ticket and in the draft. The cited article ids you receive are search hints only.
Call SupportKB at most 3 times. After the last call, stop retrieving and decide with the evidence you already have. If retrieval fails or returns nothing relevant, you cannot confirm anything: report the draft as not grounded. Never end a run without a determination.

SupportKB articles:
""" + KB_CATALOG + """

Step 1: Claims in the draft
Split the draft into individual claims: every instruction or step, URL, app or product name, menu or button name, number, limit, duration, timeline, entitlement, policy statement, contact channel, phone extension, and opening hours. Greetings, sign-offs, empathy, and restating the customer's own words are not claims.
A claim is supported only if retrieved SupportKB content states it. Paraphrase is fine. Generalizing, combining two facts into a new one, extending a policy to a case it does not mention, or filling in a plausible detail is not supported.
Any promise that someone will escalate, follow up, investigate, approve, or contact the customer is unsupported, because a reply that is sent without review has nobody behind it.
Quote each unsupported claim from the draft into unsupportedClaims.

Step 2: Questions in the ticket
List every separate question and request in the ticket, including implied ones. Each must be fully answered by the draft using supported claims. Add each one that is unanswered, partly answered, or answered only with an unsupported claim to unansweredQuestions.

Step 3: Verdict
draftGrounded is true only if unsupportedClaims is empty. answersEveryQuestion is true only if unansweredQuestions is empty. If you are unsure about any claim or question, treat it as unsupported or unanswered. Write verdictNotes in at most three sentences for a human reviewer: which articles you checked and what failed, if anything.
Do not rewrite or improve the draft. Return every output field on every run: draftGrounded, answersEveryQuestion, unsupportedClaims, unansweredQuestions, verdictNotes."""

VERIFIER_INPUTS = [
    ("start__output__subject", "=$vars.start.output.subject", "Bound from $vars.start.output.subject"),
    ("start__output__body", "=$vars.start.output.body", "Bound from $vars.start.output.body"),
    ("%s__output__draftReply" % N_AGENT, "=$vars.%s.output.draftReply" % N_AGENT,
     "Bound from $vars.%s.output.draftReply" % N_AGENT),
    ("%s__output__citedKbDocs" % N_GATE, "=$vars.%s.output.citedKbDocs" % N_GATE,
     "Bound from $vars.%s.output.citedKbDocs" % N_GATE),
]

VERIFIER_USER = """Audit this draft reply before it is sent without human review.

Ticket subject: {{input.start__output__subject}}

Ticket body:
{{input.start__output__body}}

Draft reply:
{{input.%s__output__draftReply}}

Articles the drafting agent cited (search hints only): {{input.%s__output__citedKbDocs}}""" % (N_AGENT, N_GATE)


def write_agent(agent_id, name, system, user, inputs, outputs):
    path = os.path.join(ROOT, agent_id, "agent.json")
    agent = json.load(open(path, encoding="utf-8"))
    agent["settings"] = {"model": MODEL, "maxTokens": 128000, "temperature": 0,
                         "engine": "basic-v2", "maxIterations": 25, "mode": "standard"}
    agent["inputSchema"] = {"type": "object",
                            "properties": {k: {"type": "string", "description": d} for k, _, d in inputs}}
    agent["outputSchema"] = {"type": "object",
                             "properties": {k: dict(s, description=d) for k, s, d in outputs},
                             "required": [k for k, _, _ in outputs]}
    agent["name"] = name
    agent["guardrails"] = []
    # content is the source of truth; `uip agent refresh` regenerates contentTokens from it.
    agent["messages"] = [{"role": "system", "content": system, "contentTokens": []},
                         {"role": "user", "content": user, "contentTokens": []}]
    json.dump(agent, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("agent.json written:", path)


DRAFTER_INPUTS = [("start__output__%s" % k, "=$vars.start.output.%s" % k, "Bound from $vars.start.output.%s" % k)
                  for k, _ in INPUTS]
write_agent(DRAFTER_ID, "Classify, Draft & Assess KB Coverage", DRAFTER_SYSTEM, DRAFTER_USER,
            DRAFTER_INPUTS, AGENT_OUTPUTS)
write_agent(VERIFIER_ID, "Verify Draft Against SupportKB", VERIFIER_SYSTEM, VERIFIER_USER,
            VERIFIER_INPUTS, VERIFIER_OUTPUTS)


# ---------------------------------------------------------------------------
# Context resources (SupportKB, Shared folder) - one per agent, ids reused if present
# ---------------------------------------------------------------------------
def write_context(agent_id, query_hint):
    res_root = os.path.join(ROOT, agent_id, "resources")
    existing = [os.path.basename(p) for p in glob.glob(os.path.join(res_root, "*")) if os.path.isdir(p)]
    res_id = existing[0] if existing else str(uuid.uuid4())
    os.makedirs(os.path.join(res_root, res_id), exist_ok=True)
    resource = {
        "$resourceType": "context", "name": "SupportKB", "description": ctx_def["description"],
        "folderPath": "Shared", "indexName": "SupportKB", "id": res_id, "referenceKey": "",
        "settings": {"query": {"description": query_hint, "variant": "dynamic"},
                     "folderPathPrefix": {"variant": "static", "value": ""},
                     "threshold": 0, "resultCount": 5, "retrievalMode": "semantic",
                     "fileExtension": {"value": "All"}},
        "contextType": "index",
    }
    json.dump(resource, open(os.path.join(res_root, res_id, "resource.json"), "w", encoding="utf-8"), indent=2)
    print("resource.json written:", res_id)
    return res_id


DRAFT_QUERY = "The support problem described in the ticket, phrased as a knowledge base search query"
VERIFY_QUERY = "One topic or claim from the ticket or draft reply to check, phrased as a knowledge base search query"
DRAFT_CTX_RES = write_context(DRAFTER_ID, DRAFT_QUERY)
VERIFY_CTX_RES = write_context(VERIFIER_ID, VERIFY_QUERY)

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

ERROR_OUTPUT = {"type": "object", "description": "Error information if the node fails", "source": "=Error", "var": "error"}


def agent_node(node_id, label, agent_id, inputs, outputs):
    return {
        "id": node_id,
        "type": "uipath.agent.autonomous",
        "typeVersion": agent_def["version"],
        "display": {"label": label, "icon": "autonomous-agent"},
        "inputs": {
            "source": agent_id,
            "agentInputVariables": [{"id": k, "type": "string", "binding": b, "description": d}
                                    for k, b, d in inputs],
            "agentOutputVariables": [{"id": k, "type": s["type"]} for k, s, _ in outputs],
        },
        "outputs": {
            "output": {"type": "object", "description": "Agent response", "var": "output",
                       "properties": {k: dict(s) for k, s, _ in outputs}},
            "error": dict(ERROR_OUTPUT),
        },
    }


def ctx_node(node_id, res_id, query_hint):
    return {
        "id": node_id,
        "type": CTX_TYPE,
        "typeVersion": ctx_def["version"],
        "display": {"label": "SupportKB", "icon": "context"},
        "inputs": {
            "source": res_id, "id": node_id, "name": "SupportKB", "description": ctx_def["description"],
            "referenceKey": "", "indexName": "SupportKB", "folderPath": "Shared",
            "resultCount": 5, "threshold": 0, "retrievalMode": "semantic",
            "query": {"mode": "prompt", "textValue": "", "promptValue": query_hint, "argumentPath": ""},
            "fileExtension": "All",
            "folderPathPrefix": {"mode": "text-builder", "textValue": "", "promptValue": "", "argumentPath": ""},
        },
    }


def script_node(node_id, label, script_file, description):
    return {
        "id": node_id,
        "type": "core.action.script",
        "typeVersion": script_def["version"],
        "display": {"label": label, "icon": "code"},
        "inputs": {"script": read_script(script_file)},
        "outputs": {
            "output": {"type": "object", "description": description, "source": "=result.response", "var": "output"},
            "error": dict(ERROR_OUTPUT),
        },
    }


def switch_node(node_id, label, cases):
    return {
        "id": node_id,
        "type": "core.logic.switch",
        "typeVersion": switch_def["version"],
        "display": {"label": label, "icon": "between-horizontal-start"},
        "inputs": {"cases": [{"id": i, "label": l, "expression": e} for i, l, e in cases]},
        "outputs": {
            "matchedCase": {"type": "string", "description": "The label of the matched case", "var": "matchedCase"},
            "matchedCaseId": {"type": "string",
                              "description": "The ID of the matched case (\"default\" for the default branch)",
                              "var": "matchedCaseId"},
        },
    }


GATE = "$vars.%s.output" % N_GATE
VCHECK = "$vars.%s.output" % N_VCHECK

drafter_node = agent_node(N_AGENT, "Classify, Draft & Assess KB Coverage", DRAFTER_ID, DRAFTER_INPUTS, AGENT_OUTPUTS)
drafter_ctx = ctx_node(N_AGENT_CTX, DRAFT_CTX_RES, DRAFT_QUERY)
gate_node = script_node(N_GATE, "Safety Gate (deterministic)", "gate_check_safety.js",
                        "Route (noise, urgent, verify, review), gate failures, and KB citation summary")
# Every case compares against an exact route string; anything else (including a
# script that returned nothing) falls to the default human review branch.
route_node = switch_node(N_ROUTE, "Route by gate result", [
    ("noise", "Noise: auto-skip", "%s.route === 'noise'" % GATE),
    ("urgent", "Critical / High: urgent review", "%s.route === 'urgent'" % GATE),
    ("verify", "KB-covered candidate: verify grounding",
     "%s.route === 'verify' && %s.autoResolveCandidate === true" % (GATE, GATE)),
])
verifier_node = agent_node(N_VERIFY, "Verify Draft Against SupportKB", VERIFIER_ID, VERIFIER_INPUTS, VERIFIER_OUTPUTS)
verifier_ctx = ctx_node(N_VERIFY_CTX, VERIFY_CTX_RES, VERIFY_QUERY)
vcheck_node = script_node(N_VCHECK, "Grounding Check (deterministic)", "gate_check_verification.js",
                          "Whether the independent verifier confirmed the draft, with failure reasons")
decide_node = switch_node(N_DECIDE, "Auto-resolve only if verified", [
    ("verified", "Verified: auto-resolve", "%s.verified === true" % VCHECK),
])

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


def review_node(node_id, label, title, task_priority, draft_var, note_var, gate_binding, gate_label, lead_fields):
    """Quick Form task. `lead_fields` are shown first so the reviewer sees the
    routing signal (why it was not auto-resolved / guidance) before the ticket text."""
    common_ticket = [
        field("ticketid", "Ticket ID", "string", "vars.ticketId"),
        field("customername", "Customer Name", "string", "vars.customerName"),
        field("subject", "Subject", "string", "vars.subject"),
        field("body", "Ticket Body", "string", "vars.body"),
    ]
    agent_fields = [
        field("autonomygate", gate_label, "string", gate_binding),
        field("category", "Category", "string", "vars.%s.output.category" % N_AGENT),
        field("priority", "Priority", "string", "vars.%s.output.priority" % N_AGENT),
        field("confidence", "Confidence", "number", "vars.%s.output.confidence" % N_AGENT),
        field("rationale", "Agent Rationale", "string", "vars.%s.output.rationale" % N_AGENT),
        field("recommendedapproach", "Recommended Approach (for reviewer)", "string",
              "vars.%s.output.recommendedApproach" % N_AGENT),
        field("kbsources", "SupportKB Sources Cited", "string", "vars.%s.output.kbSourcesText" % N_GATE),
        field("kbgaps", "KB Gaps Flagged by the Agent", "string", "vars.%s.output.kbGapsText" % N_GATE),
    ]
    lead = [f for f in agent_fields if f["id"] in lead_fields]
    rest = [f for f in agent_fields if f["id"] not in lead_fields]
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


GATE_SUMMARY = "vars.%s.output.gateSummary" % N_GATE
VERIFY_SUMMARY = "vars.%s.output.verificationSummary" % N_VCHECK
urgent_node = review_node(
    N_URGENT, "Urgent Review", "URGENT: Review Draft Reply (Critical/High impact)", "High",
    "vars.urgentDraftReply", "vars.urgentReviewerNote", GATE_SUMMARY, "Why this was not auto-resolved",
    lead_fields=("priority", "recommendedapproach"))
standard_node = review_node(
    N_STANDARD, "Standard Review", "Review Draft Reply", "Medium",
    "vars.standardDraftReply", "vars.standardReviewerNote", GATE_SUMMARY, "Why this was not auto-resolved",
    lead_fields=("autonomygate", "recommendedapproach"))
grounding_node = review_node(
    N_GROUNDING, "Grounding Review", "Review Draft Reply (KB grounding check failed)", "Medium",
    "vars.groundingDraftReply", "vars.groundingReviewerNote", VERIFY_SUMMARY,
    "Why the grounding check blocked auto-resolve", lead_fields=("autonomygate", "recommendedapproach"))


def js(expr):
    return "=js:" + expr


OUT_VARS = [
    ("decision", "string",
     "AutoSkipped (noise), AutoResolved (KB-verified, no human), or the reviewer outcome: Approve, Modify & Send, Reject"),
    ("finalReply", "string",
     "Reply to send: the verified draft for AutoResolved, the approved or edited draft after review, "
     "empty after Reject, a fixed marker for auto-skipped noise"),
    ("category", "string", "Ticket category assigned by the agent (includes Noise)"),
    ("priority", "string", "Ticket priority assigned by the agent"),
    ("recommendedApproach", "string", "Agent guidance to the reviewer on the next action"),
    ("reviewerNote", "string", "Internal note from the reviewer; empty when no human reviewed the ticket"),
    ("kbCovered", "boolean", "true only if the agent reported full SupportKB coverage with no gaps"),
    ("kbSources", "string", "SupportKB article ids the agent cited"),
    ("autonomyGate", "string", "Why the ticket was or was not auto-resolved (gate and verifier findings)"),
]


def end_node(node_id, label, decision, final_reply, reviewer_note, gate):
    shared = {
        "category": js("$vars.%s.output.category" % N_AGENT),
        "priority": js("$vars.%s.output.priority" % N_AGENT),
        "recommendedApproach": js("$vars.%s.output.recommendedApproach" % N_AGENT),
        "kbCovered": js("%s.kbCovered === true" % GATE),
        "kbSources": js("%s.kbSourcesText" % GATE),
    }
    own = {"decision": js(decision), "finalReply": js(final_reply), "reviewerNote": js(reviewer_note),
           "autonomyGate": js(gate)}
    merged = dict(shared, **own)
    return {
        "id": node_id,
        "type": "core.control.end",
        "typeVersion": end_def["version"],
        "display": {"label": label, "icon": "circle-check"},
        "inputs": {},
        "outputs": {k: {"type": t, "source": merged[k]} for k, t, _ in OUT_VARS},
    }


def reviewed_end(node_id, label, review_id, gate):
    # A rejected draft must never surface as a reply to send.
    return end_node(
        node_id, label,
        "$vars.%s.status" % review_id,
        "$vars.%s.status === 'Reject' ? '' : ($vars.%s.output.draftreply || '')" % (review_id, review_id),
        "$vars.%s.output.reviewernote || ''" % review_id,
        gate)


end_nodes = [
    end_node(N_END_SKIPPED, "Auto-Skipped (noise)", json.dumps(NOISE_DECISION), json.dumps(NOISE_FINAL_REPLY),
             '""', "%s.gateSummary" % GATE),
    end_node(N_END_RESOLVED, "Auto-Resolved (KB-verified)", json.dumps(RESOLVED_DECISION),
             "$vars.%s.output.draftReply" % N_AGENT, '""', "%s.verificationSummary" % VCHECK),
    reviewed_end(N_END_URGENT, "Urgent Review Recorded", N_URGENT, "%s.gateSummary" % GATE),
    reviewed_end(N_END_STANDARD, "Standard Review Recorded", N_STANDARD, "%s.gateSummary" % GATE),
    reviewed_end(N_END_GROUNDING, "Grounding Review Recorded", N_GROUNDING, "%s.verificationSummary" % VCHECK),
]

flow["nodes"] = [start, drafter_node, drafter_ctx, gate_node, route_node, verifier_node, verifier_ctx,
                 vcheck_node, decide_node, urgent_node, standard_node, grounding_node] + end_nodes


def edge(sn, sp, tn, tp="input"):
    slug = "".join(p.capitalize() if i else p for i, p in enumerate(sp.split("-")))
    return {"id": "edge_%s_%s_%s_%s" % (sn, slug, tn, tp),
            "sourceNodeId": sn, "sourcePort": sp, "targetNodeId": tn, "targetPort": tp}


flow["edges"] = [
    edge(N_START, "output", N_AGENT),
    edge(N_AGENT, "context", N_AGENT_CTX),
    edge(N_AGENT, "success", N_GATE),
    edge(N_GATE, "success", N_ROUTE),
    edge(N_ROUTE, "case-noise", N_END_SKIPPED),
    edge(N_ROUTE, "case-urgent", N_URGENT),
    edge(N_ROUTE, "case-verify", N_VERIFY),
    edge(N_ROUTE, "default", N_STANDARD),
    edge(N_VERIFY, "context", N_VERIFY_CTX),
    edge(N_VERIFY, "success", N_VCHECK),
    edge(N_VCHECK, "success", N_DECIDE),
    edge(N_DECIDE, "case-verified", N_END_RESOLVED),
    edge(N_DECIDE, "default", N_GROUNDING),
] + [
    # One edge per reviewer outcome (Studio Web's native shape). The handles are
    # declared by patch_v3_outcome_handles.py, which must run after `flow format`.
    edge(nid, "outcome-%s" % oid, end_id)
    for nid, end_id in ((N_URGENT, N_END_URGENT), (N_STANDARD, N_END_STANDARD), (N_GROUNDING, N_END_GROUNDING))
    for oid, _, _ in OUTCOMES
]

trigger_defs = [d for d in flow["definitions"] if d.get("nodeType") == "core.trigger.manual"]
flow["definitions"] = trigger_defs + [agent_def, ctx_def, script_def, switch_def, qf_def, end_def]


def node_var(nid, out_id, vtype, description):
    return {"id": "%s.%s" % (nid, out_id), "type": vtype, "description": description,
            "binding": {"nodeId": nid, "outputId": out_id}}


flow["variables"] = {
    "globals": [
        {"id": k, "direction": "in", "type": "string", "description": d, "triggerNodeId": N_START}
        for k, d in INPUTS
    ] + [
        {"id": k, "direction": "out", "type": t, "description": d} for k, t, d in OUT_VARS
    ],
    "nodes": [
        node_var(N_START, "output", "object", "Data passed when manually triggering the process."),
    ] + [
        v for nid in (N_AGENT, N_VERIFY) for v in (
            node_var(nid, "output", "object", "Agent response"),
            node_var(nid, "error", "object", "Error information if the node fails"))
    ] + [
        v for nid in (N_GATE, N_VCHECK) for v in (
            node_var(nid, "output", "object", "The return value of the script"),
            node_var(nid, "error", "object", "Error information if the node fails"))
    ] + [
        v for nid in (N_ROUTE, N_DECIDE) for v in (
            node_var(nid, "matchedCase", "string", "The label of the matched case"),
            node_var(nid, "matchedCaseId", "string", "The ID of the matched case"))
    ] + [
        v for nid in (N_URGENT, N_STANDARD, N_GROUNDING) for v in (
            node_var(nid, "output", "object", "Task result data"),
            node_var(nid, "status", "string", "Task completion status"))
    ],
}

# Placeholder layout; `uip maestro flow format` owns the final positions.
flow["layout"] = {"nodes": {n["id"]: {"position": {"x": 0, "y": 0},
                                      "size": {"width": 96, "height": 96},
                                      "collapsed": False} for n in flow["nodes"]}}

json.dump(flow, open(FLOW_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("flow written:", FLOW_PATH)
print("drafter:", DRAFTER_ID, "ctx", DRAFT_CTX_RES)
print("verifier:", VERIFIER_ID, "ctx", VERIFY_CTX_RES)
