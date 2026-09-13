import json, os, uuid

ROOT = r"C:\Users\jre\triage-lab-TEAMjohannes-reitermayer\TicketTriage_TEAMjohannes-reitermayer\TriageTicketV1"
BUILD = r"C:\Users\jre\triage-lab-TEAMjohannes-reitermayer\scratch\build"
AGENT_ID = "38b67540-ed7d-4b12-993c-a8e55aeab6e2"
CTX_TYPE = "uipath.agent.resource.context.index.supportkb.e47fcbe5-bd8b-47fa-29dc-08df04e92605"
CTX_RES = str(uuid.uuid4())
ASSIGNEE = "johannes.reitermayer@gmail.com"

flow_path = os.path.join(ROOT, "TriageTicketV1.flow")
flow = json.load(open(flow_path, encoding="utf-8"))


def defnode(name):
    return json.load(open(os.path.join(BUILD, "def_%s.json" % name), encoding="utf-8"))["Data"]["Node"]


end_def = defnode("core.control.end")
agent_def = defnode("uipath.agent.autonomous")
qf_def = defnode("uipath.human-in-the-loop.quick-form")
ctx_def = defnode("context")

INPUTS = [("ticketId", "Support ticket identifier"),
          ("subject", "Ticket subject line"),
          ("body", "Ticket body text"),
          ("customerName", "Name of the customer who raised the ticket")]

# ---- nodes -----------------------------------------------------------------
start = flow["nodes"][0]
start["display"] = {"label": "Support ticket received", "icon": "play"}
start["outputs"] = {"output": {"type": "object",
                               "description": "Data passed when manually triggering the process.",
                               "source": "null", "var": "output"}}

agent_node = {
    "id": "triageAgent1",
    "type": "uipath.agent.autonomous",
    "typeVersion": agent_def["version"],
    "display": {"label": "Classify & Draft Reply", "icon": "autonomous-agent"},
    "inputs": {
        "source": AGENT_ID,
        "agentInputVariables": [
            {"id": "start__output__%s" % k, "type": "string",
             "binding": "=$vars.start.output.%s" % k,
             "description": "Bound from $vars.start.output.%s" % k} for k, _ in INPUTS],
        "agentOutputVariables": [
            {"id": "category", "type": "string"},
            {"id": "priority", "type": "string"},
            {"id": "draftReply", "type": "string"},
            {"id": "rationale", "type": "string"},
            {"id": "confidence", "type": "number"}],
    },
    "outputs": {
        "output": {"type": "object", "description": "Agent response", "var": "output",
                   "properties": {"category": {"type": "string"},
                                  "priority": {"type": "string"},
                                  "draftReply": {"type": "string"},
                                  "rationale": {"type": "string"},
                                  "confidence": {"type": "number"}}},
        "error": {"type": "object", "description": "Error information if the node fails",
                  "source": "=Error", "var": "error"},
    },
}

ctx_node = {
    "id": "supportKbContext1",
    "type": CTX_TYPE,
    "typeVersion": ctx_def["version"],
    "display": {"label": "SupportKB", "icon": "context"},
    "inputs": {
        "source": CTX_RES,
        "id": "supportKbContext1",
        "name": "SupportKB",
        "description": ctx_def["description"],
        "referenceKey": "",
        "indexName": "SupportKB",
        "folderPath": "Shared",
        "resultCount": 5,
        "threshold": 0,
        "retrievalMode": "semantic",
        "query": {"mode": "prompt", "textValue": "",
                  "promptValue": "The support problem described in the ticket, phrased as a knowledge base search query",
                  "argumentPath": ""},
        "fileExtension": "All",
        "folderPathPrefix": {"mode": "text-builder", "textValue": "", "promptValue": "", "argumentPath": ""},
    },
}

OUTCOMES = [("approve", "Approve", True),
            ("modifyandsend", "Modify & Send", False),
            ("reject", "Reject", False)]
OUTCOME_NAMES = [n for _, n, _ in OUTCOMES]

review_node = {
    "id": "reviewDraftReply1",
    "type": "uipath.human-in-the-loop.quick-form",
    "typeVersion": qf_def["version"],
    "display": {"label": "Review Draft Reply", "icon": "users"},
    "inputs": {
        "title": "Review Draft Reply",
        "recipient": {"channels": ["ActionCenter"], "connections": {},
                      "assignee": {"type": "user", "value": ASSIGNEE}},
        "priority": "Medium",
        "schema": {
            "schemaId": str(uuid.uuid4()),
            "fields": [
                {"id": "ticketid", "label": "Ticket ID", "type": "string", "direction": "input",
                 "binding": "vars.ticketId"},
                {"id": "customername", "label": "Customer Name", "type": "string", "direction": "input",
                 "binding": "vars.customerName"},
                {"id": "subject", "label": "Subject", "type": "string", "direction": "input",
                 "binding": "vars.subject"},
                {"id": "body", "label": "Ticket Body", "type": "string", "direction": "input",
                 "binding": "vars.body"},
                {"id": "category", "label": "Category", "type": "string", "direction": "input",
                 "binding": "vars.triageAgent1.output.category"},
                {"id": "priority", "label": "Priority", "type": "string", "direction": "input",
                 "binding": "vars.triageAgent1.output.priority"},
                {"id": "rationale", "label": "Agent Rationale", "type": "string", "direction": "input",
                 "binding": "vars.triageAgent1.output.rationale"},
                {"id": "confidence", "label": "Confidence", "type": "number", "direction": "input",
                 "binding": "vars.triageAgent1.output.confidence"},
                {"id": "draftreply", "label": "Draft Reply", "type": "string", "direction": "inOut",
                 "binding": "vars.triageAgent1.output.draftReply", "variable": "vars.draftReply"},
            ],
            "outcomes": [{"id": i, "name": n, "type": "string", "isPrimary": p, "action": "Continue"}
                         for i, n, p in OUTCOMES],
        },
    },
    "outputs": {
        "output": {"type": "object", "description": "Task result data", "source": "=result", "var": "output",
                   "properties": {"draftreply": {"type": "string"},
                                  "Action": {"type": "string", "enum": OUTCOME_NAMES, "default": "Approve"}}},
        "status": {"type": "string", "description": "Task completion status", "source": "=result.Action",
                   "var": "status", "enum": OUTCOME_NAMES, "default": "Approve"},
    },
}

end_node = {
    "id": "end1",
    "type": "core.control.end",
    "typeVersion": end_def["version"],
    "display": {"label": "Decision Recorded", "icon": "circle-check"},
    "inputs": {},
    "outputs": {
        "decision": {"source": "=js:$vars.reviewDraftReply1.status", "type": "string"},
        "finalReply": {"source": "=js:$vars.reviewDraftReply1.output.draftreply", "type": "string"},
        "category": {"source": "=js:$vars.triageAgent1.output.category", "type": "string"},
        "priority": {"source": "=js:$vars.triageAgent1.output.priority", "type": "string"},
    },
}

flow["nodes"] = [start, agent_node, ctx_node, review_node, end_node]


# ---- edges -----------------------------------------------------------------
def edge(sn, sp, tn, tp="input"):
    slug = "".join(p.capitalize() if i else p for i, p in enumerate(sp.split("-")))
    return {"id": "edge_%s_%s_%s_%s" % (sn, slug, tn, tp),
            "sourceNodeId": sn, "sourcePort": sp, "targetNodeId": tn, "targetPort": tp}


flow["edges"] = [
    edge("start", "output", "triageAgent1"),
    edge("triageAgent1", "context", "supportKbContext1"),
    edge("triageAgent1", "success", "reviewDraftReply1"),
] + [edge("reviewDraftReply1", "outcome-%s" % i, "end1") for i, _, _ in OUTCOMES]

# ---- definitions -----------------------------------------------------------
flow["definitions"] = flow["definitions"] + [agent_def, ctx_def, qf_def, end_def]

# ---- variables -------------------------------------------------------------
flow["variables"] = {
    "globals": [
        {"id": k, "direction": "in", "type": "string", "description": d, "triggerNodeId": "start"}
        for k, d in INPUTS
    ] + [
        {"id": "decision", "direction": "out", "type": "string",
         "description": "Reviewer decision: Approve, Modify & Send, or Reject"},
        {"id": "finalReply", "direction": "out", "type": "string",
         "description": "The reply text as approved or edited by the reviewer"},
        {"id": "category", "direction": "out", "type": "string",
         "description": "Ticket category assigned by the agent"},
        {"id": "priority", "direction": "out", "type": "string",
         "description": "Ticket priority assigned by the agent"},
    ],
    "nodes": [
        {"id": "start.output", "type": "object",
         "description": "Data passed when manually triggering the process.",
         "binding": {"nodeId": "start", "outputId": "output"}},
        {"id": "triageAgent1.output", "type": "object", "description": "Agent response",
         "binding": {"nodeId": "triageAgent1", "outputId": "output"}},
        {"id": "triageAgent1.error", "type": "object", "description": "Error information if the node fails",
         "binding": {"nodeId": "triageAgent1", "outputId": "error"}},
        {"id": "reviewDraftReply1.output", "type": "object", "description": "Task result data",
         "binding": {"nodeId": "reviewDraftReply1", "outputId": "output"}},
        {"id": "reviewDraftReply1.status", "type": "string", "description": "Task completion status",
         "binding": {"nodeId": "reviewDraftReply1", "outputId": "status"}},
        {"id": "end1.decision", "type": "string", "binding": {"nodeId": "end1", "outputId": "decision"}},
        {"id": "end1.finalReply", "type": "string", "binding": {"nodeId": "end1", "outputId": "finalReply"}},
        {"id": "end1.category", "type": "string", "binding": {"nodeId": "end1", "outputId": "category"}},
        {"id": "end1.priority", "type": "string", "binding": {"nodeId": "end1", "outputId": "priority"}},
    ],
}

flow["runtime"] = "maestro"

# ---- layout (placeholders; flow format owns final positions) ---------------
flow["layout"] = {"nodes": {n["id"]: {"position": {"x": 0, "y": 0},
                                      "size": {"width": 96, "height": 96},
                                      "collapsed": False} for n in flow["nodes"]}}

json.dump(flow, open(flow_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("flow written:", flow_path)
print("context resource uuid:", CTX_RES)

# ---- context resource.json -------------------------------------------------
res_dir = os.path.join(ROOT, AGENT_ID, "resources", CTX_RES)
os.makedirs(res_dir, exist_ok=True)
resource = {
    "$resourceType": "context",
    "name": "SupportKB",
    "description": ctx_def["description"],
    "folderPath": "Shared",
    "indexName": "SupportKB",
    "id": CTX_RES,
    "referenceKey": "",
    "settings": {
        "query": {"description": "The support problem described in the ticket, phrased as a knowledge base search query",
                  "variant": "dynamic"},
        "folderPathPrefix": {"variant": "static", "value": ""},
        "threshold": 0,
        "resultCount": 5,
        "retrievalMode": "semantic",
        "fileExtension": {"value": "All"},
    },
    "contextType": "index",
}
json.dump(resource, open(os.path.join(res_dir, "resource.json"), "w", encoding="utf-8"), indent=2)
print("resource written:", res_dir)
