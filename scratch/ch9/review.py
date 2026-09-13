import json, subprocess, shutil, sys
uip = shutil.which("uip"); FOLDER = "3565469"
def run(*a):
    p = subprocess.run([uip, *a, "--output", "json"], capture_output=True, text=True, encoding="utf-8")
    try: d = json.loads(p.stdout)
    except Exception: raise SystemExit(f"{a[:3]} -> {p.stdout} {p.stderr}")
    if d.get("Result") != "Success": raise SystemExit(f"{a[:3]} -> {json.dumps(d)[:800]}")
    return d

DECISIONS = {
 101474836: ("Approve", None, "Approved as-is: grounded self-service reset steps; answers both the phone/off-network and the sync questions. Only follow up if he has no registered mobile number."),
 101474837: ("Approve", None, "Approved as-is: answers both the MFA phone switch and the returns@ shared mailbox request with concrete KB steps."),
 101474838: ("Approve", None, "Approved as-is: accurate VP-approval path for reports over 90 days and the Thursday payout cycle. Internal: route to the expenses/finance queue, not IT app troubleshooting."),
 101474839: ("Approve", None, "Approved as-is: KB self-service fix via Company Portal plus fallback contacts. If she replies, confirm this is office FollowMe printing, not a warehouse label printer (Operations)."),
 101474841: ("Modify & Send", """Hi Viktor,

Thanks for checking before changing any HomeFix laptops. Dual-boot and disk repartitioning on company laptops need a decision from our endpoint and security team, so I have routed your question to them to confirm whether it is permitted and which tooling, if any, is approved.

To get this moving:
1. Submit a Software Request in the IT catalog for Ubuntu dual-boot, with the business justification: the GPU workloads your group needs to run, how many people and laptops are involved, and when you need it.
2. Name the disk-partitioning tool you were planning to use in the same request, so it is reviewed at the same time.
3. Until the review comes back, please don't repartition drives or install Ubuntu or partitioning tools from the internet. Installs outside Company Portal are blocked by policy and raise a security alert.

We'll get back to you with the team's decision and the approved setup for your GPU work.

Best regards,
HomeFix Supply Support Team""",
  "Rewritten: the draft told the requester we have no helpdesk article on this (internal KB gap) and restated install policy without a path forward. New draft gives concrete steps (Software Request with justification, name the tool, hold off meanwhile). Internal: route to endpoint management/security owner to decide on dual-boot + repartitioning; KB is silent on dual-boot."),
 101474842: ("Modify & Send", """Hi Carla,

We have opened this as a Critical incident and escalated it to the on-call specialist team now. We understand the whole finance team has been getting a 502 error in Concur since 8am and that approvals for today's 6pm month-end close are blocked, and we are working against that deadline.

What happens next:
1. The on-call team is investigating the Concur outage, including whether it is a wider vendor-side incident.
2. You will get a first status update from us within 30 minutes, and regular updates until Concur is working again.

To help the responders move faster, please reply with:
- Roughly how many people are affected
- A screenshot of the 502 error and the browser you are using
- A direct phone number for a finance contact who can test with IT

If you need us urgently in the meantime, call the Service Desk at extension 4357 (HELP), staffed 06:00-20:00 local time, Monday to Saturday, and quote ticket HF-2006.

We own this ticket until it is resolved.

Best regards,
HomeFix Supply Support Team""",
  "Rewritten: led with Critical ownership and a 30-minute first-update commitment (KB: High severity triaged within 30 min), removed the Concur portal link (useless while Concur returns 502), asked for user count, screenshot, and a test contact. Internal: page the Concur/vendor SaaS owner now, check vendor status, open an incident bridge; KB has no Concur outage runbook."),
 101474844: ("Modify & Send", """Hi Owen,

You're right, three weeks with no update is not acceptable, and I'm sorry. I have taken ownership of your request and I'm chasing it today.

Here is what I'm doing:
1. Finding out exactly where your request is waiting. Requests under $500/year go to your manager for approval, and a tool from a new vendor also needs a security review of about 5 business days.
2. Following up directly with whoever is holding it.
3. Updating you before Friday with who the request is waiting on and when you can expect the license.

If you have the request number, please reply with it so I can find it faster.

Please hold off on buying the license on your own card. We can't confirm that a personal purchase would be reimbursed, and software installed outside Company Portal is blocked on company laptops.

Regards,
HomeFix Supply Support Team""",
  "Rewritten: the draft re-explained the Software Request process he already followed and warned about internet installs, without addressing the three-week delay or his Friday personal-card threat. New draft owns the delay and commits to an update before Friday. Internal: look up the original Software Request, identify manager approval vs new-vendor security review, nudge the approver; do not authorize personal-card reimbursement without Finance/Procurement."),
}

ids = [int(x) for x in sys.argv[1:]] or list(DECISIONS)
for tid in ids:
    action, draft, note = DECISIONS[tid]
    cur = run("tasks", "data", "get", str(tid), "--folder-id", FOLDER)["Data"]
    if cur["Status"] == "Completed":
        print(tid, "already completed:", cur["Action"]); continue
    data = {k.lower(): v for k, v in cur["Data"].items()}
    if draft: data["draftreply"] = draft
    data["reviewernote"] = note
    payload = json.dumps(data, ensure_ascii=False)
    run("tasks", "data", "save", str(tid), "--folder-id", FOLDER, "--data", payload)
    run("tasks", "complete", str(tid), "--type", "QuickFormTask", "--folder-id", FOLDER, "--action", action, "--data", payload)
    after = run("tasks", "data", "get", str(tid), "--folder-id", FOLDER)["Data"]
    print(tid, data["ticketid"], "->", after["Status"], after["Action"], "| draft kept newlines:", "\n" in after["Data"].get("Draftreply", ""), "| note saved:", bool(after["Data"].get("Reviewernote")))
