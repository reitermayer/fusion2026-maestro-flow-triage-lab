# Fusion Triage Lab Runbook

> **Fusion 2026 - Hands-on Lab - 120 min**  
> *Author: Product Manager Tuan*

You and your coding agent will build a support-ticket triage flow for HomeFix Supply, review its work in Action Center, and let the agent mine your decisions to ship two better versions. Everyone builds against the same shared knowledge base, `SupportKB` in the Shared folder; there is no per-team index to create. Type the prompts in your own words - only the **bold anchors** inside them must survive your paraphrase. Every step shows how long the agent works and what you do meanwhile, so nobody sits watching a spinner.

| Workshop Dimension | Details |
| :--- | :--- |
| **Tenant** | `staging.uipath.com/uipathlabsworkshop/MVPSummit26` |
| **Your Team Code** | `TEAMfirstname-lastname` (e.g. `TEAMjane-doe`) |
| **Prebuilt for You** | `TicketsV1` / `TicketsV2` / `TicketsV3` Data Fabric entities & `SupportKB` index in `Shared` |
| **Hands-On Time** | ~65 min of the 120 min (the rest is discussion) |

---

## Steps

### Prep: 0 - Install the Tools

Do this before the session if you can. You need Node.js 20+ installed, then:

**TYPE IN YOUR TERMINAL:**
```bash
npm install -g @anthropic-ai/claude-code @uipath/cli
claude plugin marketplace add https://github.com/UiPath/skills.git
claude plugin install uipath@uipath-marketplace
```

> [!NOTE]
> **Checkpoint:** `uip --version` prints a version and `claude --version` works. Pairs need only one working laptop - if yours fights you, lean on your partner's.

---

### 0:00: 1 - Connect to the Workshop Tenant
*⏱ ~3 min - browser sign-in*

Pick your team code first: **TEAM** followed by your first and last name, lowercase with a hyphen, for example `TEAMjane-doe`. Everyone shares one tenant, so this code is what keeps your solution, deployment folder, and tasks from colliding with the person next to you. Use it everywhere the guide says `TEAMfirstname-lastname`. Then make an empty folder for your build and start Claude Code inside it - everything you create today lives here:

**TYPE IN YOUR TERMINAL:**
```bash
mkdir triage-lab-TEAMfirstname-lastname && cd triage-lab-TEAMfirstname-lastname
claude
```

Inside Claude Code, the `!` prefix runs a command directly. Log the UiPath CLI into the workshop environment (a browser window opens - sign in with the workshop account on your table card):

**TYPE IN CLAUDE CODE:**
```bash
! uip login --authority "https://staging.uipath.com/identity_" --organization uipathlabsworkshop --tenant MVPSummit26
```

Then verify you landed in the right place:

**TYPE IN CLAUDE CODE:**
```bash
! uip login status
```

> [!NOTE]
> **Checkpoint:** Status shows BaseUrl `staging.uipath.com`, org `uipathlabsworkshop`, tenant `MVPSummit26`. Anything else (`cloud.uipath.com`, your own org): rerun the login line above before going further.

---

### 0:05: 2 - Preflight the Room's Data
*⏱ Agent works 2-3 min - You: open a second tab at staging.uipath.com for Studio Web*

Your first words to the coding agent - make it prove the shared workshop resources are reachable before you build anything on them:

**SAY TO YOUR CODING AGENT:**
```text
Verify my UiPath setup on this tenant: confirm the login is uipathlabsworkshop/MVPSummit26, that the shared Data Fabric entities TicketsV1, TicketsV2, and TicketsV3 exist and each holds 8 tickets (query the records, don't just list entities), and that the SupportKB knowledge index in the Shared folder exists and answers a test search. Report what you find; don't create or change anything.
```

> [!NOTE]
> **Checkpoint:** Three entities x 8 tickets, and the shared SupportKB index returns a HomeFix help article for a test query. Anything missing is a room problem, not yours - raise a hand. If it can't be fixed in 3 minutes, a TA will move you to the backstop tenant.

> [!TIP]
> **Known Slow Spot:** The agent's knowledge-index search tool may report a 401 and spend a minute working around a stale token file. That's normal; it recovers on its own. If it's still stuck after 3 minutes, tell it: *"skip the index search, just confirm the index exists"*.

---

### 0:10: 3 - Build V1
*⏱ Agent works 4-6 min - You: read step 5 so you're ready to deploy*

**SAY TO YOUR CODING AGENT:**
```text
Build a Maestro Flow solution TicketTriage_TEAMfirstname-lastname with a flow TriageTicketV1. It takes a support ticket (ticketId, subject, body, customerName) as inputs. An agent classifies it and drafts a reply grounded in the existing SupportKB index in the Shared folder, then an Action Center task assigned to me lets me Approve, Modify & Send, or Reject (look up my email with uip or users current; don't ask me for it). Validate it, refresh the solution resources so the index links up, and upload it to Studio Web.
```

> [!NOTE]
> **Checkpoint:** The agent reports a designer URL, `flow validate` passed, and `solution resources refresh` imported the index (it should say "Imported 1", not "Created"). Open the URL: trigger -> agent (with a knowledge attachment) -> review task -> end. In the task node's recipient, the assignee should be type "user" with *your* email, not the default "group". The designer may show warnings about outcomes without downstream nodes - that's fine, they don't block anything.

> [!IMPORTANT]
> **Anchors:** The solution and flow names, the shared index name `SupportKB` + Shared folder, the three review outcomes, "assigned to me" with the `uip or users current` hint, "refresh the solution resources", "upload" (not publish). Never type your email into the prompt; the agent reads it from your login so the same prompt works for everyone in the room. The agent scaffolds everything in the empty folder from step 1 - you never create project files by hand. If it offers to run `flow debug`, say no.

---

### 0:18: 4 - Deploy
*⏱ 2-3 min - the deploy log runs for about a minute*

The one browser step you'll repeat three times today. In the designer, click **Deploy**, switch "Pack to" from Personal to **Shared**, and click Deploy in the wizard. This creates your team's own folder `Shared/TicketTriage_TEAMfirstname-lastname`, publishes the package, and links your knowledge index - watch the log for "All services activated successfully". Later deploys are the same button labelled **Pack and upgrade** with a bumped version.

> [!NOTE]
> **Checkpoint:** "Deployment successful" with your version number, and a new folder `Shared/TicketTriage_TEAMfirstname-lastname` exists on the tenant. If publish fails with "version already exists", bump the Version field in the wizard and retry.

> [!TIP]
> **Deploy button greyed out?** The resource refresh in step 3 normally writes the index pointer the designer needs, so Deploy should already be active. If it's grey after a fresh tab, see the breakage table - it's a one-call fix.

---

### 0:22: 5 - Run Batch A
*⏱ ~1 min to start 8 jobs - tasks appear 20-50 s after each start*

**SAY TO YOUR CODING AGENT:**
```text
Run every ticket in the shared TicketsV1 entity through my deployed flow, one job each. Flows start with uip maestro flow process run <processKey> <folderKey> --release-key <releaseKey>, not with jobs start. The batch is settled when every instance is either Completed or has an open Action Center task - check that, don't wait on job state.
```

> [!NOTE]
> **Checkpoint:** 8 review tasks in Action Center about a minute after the first job started, each already assigned to you (they show under "My tasks", not "Unassigned"). Measured in the dry run: 21-52 seconds from job start to task, whole batch settled in 67 seconds. The error *"Couldn't find any user with unattended robot permissions"* should not happen (the robot account is inherited from Shared) - if it does, raise a hand.

> [!IMPORTANT]
> **Why the last sentence matters:** Orchestrator shows a flow job as *Running* the whole time it waits for a human, so an agent that polls job state will sit there for five minutes reporting "still running" while your tasks have been waiting since the first minute. Task count plus completed instances is the real signal.

---

### 0:25: 6 - Review the Agent's Work by Hand, Then Tell It What's Wrong
*⏱ ~10 min of reading - then the agent works ~1 min*

Open Action Center (Product launcher -> Action Center, your team's folder). Work all 8 tasks honestly - approve drafts you'd send (leave the final response empty to send the draft unchanged), modify the ones that miss (the outage, the angry customer, the question the KB can't answer), reject what deserves no reply. Notice what V1 *can't* see: nothing is marked urgent, and the out-of-office auto-reply got a task like everything else. This is the only batch you review by hand; it's where you learn what the agent gets wrong. Then:

**SAY TO YOUR CODING AGENT:**
```text
Leave trace feedback on three of those runs (uip traces feedback create needs --positive or --negative plus --comment): the outage ticket should have been treated as urgent, the auto-reply is noise that never needed review, and every draft should come with a recommended approach for the reviewer.
```

> [!NOTE]
> **Checkpoint:** 8 tasks completed, 3 feedback entries readable via `uip traces feedback list`. Your score so far: **8 human touches for 8 tickets.**

---

### 0:37: 7 - V2 - Mine Your Decisions
*⏱ Agent works 4-6 min - You: keep the designer tab open for the deploy*

**SAY TO YOUR CODING AGENT:**
```text
Look at my review decisions and trace feedback from the V1 runs, figure out what's weak in V1, and build TriageTicketV2 as a second flow in the same solution that fixes it. Validate and upload it; I'll deploy from the designer.
```

> [!NOTE]
> **Checkpoint:** The agent names the weaknesses from *your* decisions (no urgency path, noise reviewed for nothing, no reviewer guidance) and reports a second flow with urgent and noise routing plus a recommended-approach field, with both review tasks still assigned to you. Upload needs `--force` this time; that's expected.

Now deploy again (step 4, **Pack and upgrade**, bump the version) and wait for "Deployment successful" before the next prompt - if you ask too early the agent finds no V2 release and stops.

---

### 0:47: 8 - Run Batch B
*⏱ Agent works ~2 min - tasks appear within ~1 min of the start*

**SAY TO YOUR CODING AGENT:**
```text
Before running anything, check the V2 release's index ResourceOverwrites and patch folderPath to "Shared" if it points at my team folder. Then run every ticket in the shared TicketsV2 entity through V2, one job each, and report when every instance is Completed or has an open task.
```

> [!NOTE]
> **Checkpoint:** The 2 urgent tickets arrive as **High-priority escalation tasks**, the newsletter auto-closes with no task, and every draft now carries a recommended approach. Score: **7 touches.**

> [!IMPORTANT]
> **Why the first sentence:** Only the flow that existed at the very first deploy inherits the Shared index mapping. Every flow added later is born pointing at your team folder, where no index lives, and the agent step faults with "Context grounding index not found". In the dry run, letting it fault and retry cost 4.5 minutes; checking first costs 10 seconds. The fix is `PATCH orchestrator_/odata/Releases(<id>)` with ResourceOverwrites -> folderPath "Shared", and every Pack and upgrade resets it - for *all* flows added after the first deploy, not just the newest one.

---

### 0:52: 9 - Delegate the Review
*⏱ Agent works ~1 min - instances close within 30 s of the last completion*

You reviewed batch A yourself so you know what good looks like. This time let the agent do it and check its judgement:

**SAY TO YOUR CODING AGENT:**
```text
Complete the Action Center tasks on my behalf.
```

> [!NOTE]
> **Checkpoint:** The agent tells you which drafts it approved as-is and which it rewrote before sending, and why. Expect it to rewrite the ones that restate policy without steps, or that tell an urgent requester what the knowledge base doesn't contain. 0 open tasks afterwards. Because the tasks are already yours, the agent completes them directly; it should not need to assign them first.

---

### 0:56: 10 - V3 - Earn Some Autonomy
*⏱ Agent works 4-6 min - then you deploy (2-3 min)*

**SAY TO YOUR CODING AGENT:**
```text
Build TriageTicketV3 that safely auto-resolves the approved tickets, and make sure it can never auto-send an answer the knowledge base doesn't cover.
```

> [!NOTE]
> **Checkpoint:** The agent describes a gate with more than a confidence threshold: a KB-covered flag, the KB sources actually used, or both, and it says what happens when a check fails (human review). Then Pack and upgrade, bump the version, wait for "Deployment successful".

---

### 1:07: 11 - Run Batch C
*⏱ ~1 min - auto-resolved tickets finish in 6-16 s, review tasks appear in ~15 s*

**SAY TO YOUR CODING AGENT:**
```text
Check the V3 release's index folderPath and patch it to "Shared" if needed, then run every ticket in TicketsV3 through V3 and report when every instance is Completed or has an open task.
```

> [!NOTE]
> **Checkpoint:** 3-4 tickets auto-resolve with a cited KB article, noise auto-closes, 2 urgent escalate, and 1-2 land in review - always including the question the KB doesn't cover. Score: **3-4 touches.** If the KB-uncovered ticket was auto-sent instead, your gate trusts confidence alone - ask your agent how it knows the KB actually covered the answer. Then finish the remaining tasks with the step-9 prompt.

---

### 1:12: 12 - Scoreboard
*⏱ Agent works 3-5 min - You: compare notes with the next table*

**SAY TO YOUR CODING AGENT:**
```text
Create me a report that shows the V1/V2/V3 comparison: tickets processed, human touches, and what changed between versions.
```

> [!NOTE]
> **Checkpoint:** 8 -> 7 -> 3 or 4. Two improvement rounds driven entirely by your own decisions and feedback. That's the pattern to take home: any triage queue, same loop.

---

## Benchmark: How Long Things Actually Take

Measured on the 2026-09-09 dry run (gpt-5.4, staging). Use these to know when to nudge your agent instead of waiting:

| Stage / Action | Measured Duration | What to Do Meanwhile |
| :--- | :--- | :--- |
| **Agent step per ticket** (classify + KB search + draft) | V1: 21-52 s to task (median 41 s)<br/>V3: 13-14 s to task, 6-16 s auto-resolve | Nothing. Eight jobs run in parallel, so a batch settles in about a minute, not eight. |
| **Whole batch** (first start to last task/completion) | V1: 67 s<br/>V3: 36 s<br/>V2: 412 s (unpatched release fault & retry) | If the agent is still "polling" after 2 minutes, tell it to count open tasks and completed instances and report. |
| **Completing tasks -> flow instances finish** | Under 30 s | Ask for the report right away. |
| **Build a flow version** (scaffold, author, validate, upload) | 4-6 min of agent time | Open the designer, read the next step, look at the previous version's tasks. |
| **Designer deploy / Pack and upgrade** | 1-2 min of log, 2-3 min with clicks | Wait for "Deployment successful" before the run prompt. |
| **Trace feedback, task completion, release patch** | Under 1 min each | These are single API calls; a long wait here means the agent is stuck on auth, not working. |

---

## Troubleshooting: If Something Breaks

| Symptom | Resolution / Fix |
| :--- | :--- |
| **Agent has been "waiting for jobs" for > 2 min** | The jobs are almost certainly done. Flow jobs show *Running* while they wait on a human. Say: *"stop polling job state - list open Action Center tasks and completed instances and report"*. |
| **Deploy button is greyed out** | The index debug overwrite is missing - `solution resources refresh` normally writes it, but it resets on every upload. Have your agent GET `studio_/backend/api/resourcebuilder/solutions/<solutionId>/overwrites` and PATCH the index resource's overwrite to type "Reference", kind "Index", your index name, and the Shared folder key (expect 204). Then refresh the designer in a fresh tab. |
| **Review tasks arrive Unassigned** | The task node kept the default `assignee: {type: "group"}`. Have the agent set the recipient assignee to type "user" with your email (from `uip or users current`), re-upload with `--force`, and Pack and upgrade. Meanwhile, tasks can still be opened from the Unassigned list. |
| **Agent wants to run `flow debug`** | Say no. Debug runs execute in your personal workspace where the index doesn't resolve. Deployed runs only. |
| **Agent packs or publishes from CLI** | Stop it - CLI packaging silently drops the agent's knowledge attachment. Deploys go through the designer button only. |
| **"Run TicketsV2" -> agent says no V2 release** | The deploy hasn't finished (or you skipped it). Wait for "Deployment successful" in the designer, then say "try again". |
| **Publish fails: "version already exists"** | Bump the Version field in the deploy wizard (1.0.0 -> 1.0.1) and retry. Never delete and recreate your solution - the old package name keeps its versions. |
| **Jobs won't start (`jobs start` returns 409)** | Flows use `uip maestro flow process run <processKey> <folderKey> --release-key <rk>`. Your agent knows this if you nudge it. |
| **V2/V3 agent faults: "Index not found"** | A flow added after the first deploy gets its release index mapping pointed at your team folder instead of Shared, and every redeploy resets it. Have your agent PATCH the release's ResourceOverwrites (folderPath "Shared"), then `uip maestro flow instance retry` the faulted instances. |
| **Task completion returns HTTP 403 (error 1010)** | Not a permissions problem - it's the web application firewall rejecting a non-browser client. Tell the agent to send a browser User-Agent header (or use curl). |
| **Agent faults: "Missing static query value"** | The knowledge attachment's query variant is "static" with no value. It must be `dynamic` (the agent supplies the query at runtime) - fix the resource's `settings.query` and re-upload. |
| **Agent runs but answers nonsense / no message** | Prompts reference variables that don't exist. Regenerate prompts from actual inputs. If editing `agent.json` messages directly, update `contentTokens` to match `content`. |
| **Job faults: "no user with unattended robot permissions"** | The robot account should be inherited from Shared. Raise a hand - a TA runs one `uip or users assign` for your folder. |
| **Agent answers questions KB shouldn't cover** | The index isn't attached. Check the flow shows a knowledge attachment on the agent node, and that step 2's test search worked. |
| **Designer goes blank or shows stale deploy screen** | Known Studio Web quirk - open a fresh tab and confirm the tenant picker shows MVPSummit26. |
| **You're behind the room** | Raise a hand - TAs carry reference builds of V1/V2/V3 and can drop you into the room's current step in one command. |

---

*Fusion Triage Lab - HomeFix Supply scenario - Everything you build lives in your team's own folder, so you can't break anyone else's run. - Prompts and timings updated 2026-09-09 from a full end-to-end dry run.*
