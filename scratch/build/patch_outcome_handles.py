"""Declare the three Quick Form outcome handles next to "completed".

Must run AFTER `uip maestro flow format` and after every Write/Edit on the .flow:
format (and the workspace's design-sync) re-syncs the quick-form definition from
the registry, which only ships the "completed" handle and drops these.
"""
import json, os, sys

ROOT = r"C:\Users\jre\triage-lab-TEAMjohannes-reitermayer\TicketTriage_TEAMjohannes-reitermayer\TriageTicketV1"
QF = "uipath.human-in-the-loop.quick-form"

flow_path = os.path.join(ROOT, "TriageTicketV1.flow")
flow = json.load(open(flow_path, encoding="utf-8"))

# Outcome ids/labels come from the node instance so the handles can never drift
# out of sync with the buttons the reviewer actually sees.
node = next(n for n in flow["nodes"] if n["type"] == QF)
outcomes = node["inputs"]["schema"]["outcomes"]

qf_def = next(d for d in flow["definitions"] if d.get("nodeType") == QF)
group = next(g for g in qf_def["handleConfiguration"] if g["position"] == "right")
completed = next(h for h in group["handles"] if h["id"] == "completed")

existing = {h["id"] for h in group["handles"]}
added = []
for oc in outcomes:
    hid = "outcome-%s" % oc["id"]
    if hid in existing:
        continue
    handle = dict(completed)
    handle["id"] = hid
    handle["label"] = oc["name"]
    handle["constraints"] = dict(completed.get("constraints", {}))
    group["handles"].append(handle)
    added.append(hid)

json.dump(flow, open(flow_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("handles now declared:", [h["id"] for h in group["handles"]])
print("added:", added)

# Fail loudly if an edge still points at a handle the definition does not declare.
declared = {h["id"] for g in qf_def["handleConfiguration"] for h in g["handles"]}
missing = [e["sourcePort"] for e in flow["edges"]
           if e["sourceNodeId"] == node["id"] and e["sourcePort"] not in declared]
if missing:
    sys.exit("ERROR: edges reference undeclared handles: %s" % missing)
