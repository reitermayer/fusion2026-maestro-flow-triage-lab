"""Declare Quick Form outcome handles (outcome-<id>) for TriageTicketV2.

Must run AFTER `uip agent refresh --inline-in-flow` and `uip maestro flow format`:
both re-sync the quick-form definition from the registry, which only ships the
"completed" handle. Both review nodes share one definition, so their outcome
ids must match; this script fails if they do not, or if any edge still points
at an undeclared handle.
"""
import json
import os
import sys

FLOW_PATH = r"C:\Users\jre\triage-lab-TEAMjohannes-reitermayer\TicketTriage_TEAMjohannes-reitermayer\TriageTicketV2\TriageTicketV2.flow"
QF = "uipath.human-in-the-loop.quick-form"

flow = json.load(open(FLOW_PATH, encoding="utf-8"))

nodes = [n for n in flow["nodes"] if n["type"] == QF]
outcome_sets = {n["id"]: [(o["id"], o["name"]) for o in n["inputs"]["schema"]["outcomes"]] for n in nodes}
if len({json.dumps(v) for v in outcome_sets.values()}) != 1:
    sys.exit("ERROR: quick-form nodes declare different outcomes: %s" % outcome_sets)
outcomes = next(iter(outcome_sets.values()))

qf_def = next(d for d in flow["definitions"] if d.get("nodeType") == QF)
group = next(g for g in qf_def["handleConfiguration"] if g["position"] == "right")
completed = next(h for h in group["handles"] if h["id"] == "completed")

existing = {h["id"] for h in group["handles"]}
for oid, name in outcomes:
    hid = "outcome-%s" % oid
    if hid in existing:
        continue
    handle = dict(completed)
    handle["id"] = hid
    handle["label"] = name
    handle["constraints"] = dict(completed.get("constraints", {}))
    group["handles"].append(handle)

json.dump(flow, open(FLOW_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("handles declared:", [h["id"] for h in group["handles"]])

declared = {h["id"] for g in qf_def["handleConfiguration"] for h in g["handles"]}
node_ids = {n["id"] for n in nodes}
missing = [(e["sourceNodeId"], e["sourcePort"]) for e in flow["edges"]
           if e["sourceNodeId"] in node_ids and e["sourcePort"] not in declared]
unwired = [(nid, "outcome-%s" % oid) for nid in node_ids for oid, _ in outcomes
           if not any(e["sourceNodeId"] == nid and e["sourcePort"] == "outcome-%s" % oid for e in flow["edges"])]
if missing or unwired:
    sys.exit("ERROR: undeclared handles %s / unwired outcomes %s" % (missing, unwired))
print("all outcomes wired on:", sorted(node_ids))
