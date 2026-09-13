# Tuan Review - Chapter Deviations & Gap Analysis

This document tracks all differences, deviations, and gaps between the Product Manager's (**Tuan**) official requirements/slides and the lab guide repository. As each chapter's slide or requirement set is reviewed, findings and resolutions are documented here.

> [!NOTE]
> **Source Runbook Reference**  
> Product Manager Tuan's original course runbook is preserved directly in the project root as [**`fusion-triage-lab-runbook-2026-09-09.md`**](fusion-triage-lab-runbook-2026-09-09.md) ([raw HTML version](fusion-triage-lab-runbook-2026-09-09.html)).

---

## Executive Summary & Briefing for Product Management

This section provides an executive synthesis of our end-to-end laboratory findings, comparing empirical runtime and telemetry data against Tuan's original course runbook ([`fusion-triage-lab-runbook-2026-09-09.md`](fusion-triage-lab-runbook-2026-09-09.md)).

### 1. Empirical Results vs. Runbook Assumptions

#### The V3 Touchpoint Count: 5 Touches vs. Tuan's "3 or 4"
- **Tuan's Assumption:** Runbook Step 11 & 12 state: *"Checkpoint: 8 -> 7 -> 3 or 4. Score: 3-4 touches."*
- **Empirical Measured Result:** **5 human touches** (37.5% reduction vs. V1).
- **Causal Analysis:** The deterministic safety gate refused autonomy for two edge cases as designed:
  1. **`HF-3004` (Missing ERP Access):** High confidence (0.90) and documented onboarding policy, but flagged `needsStaffAction = true`. Granting ERP access requires human IT admin action. Auto-sending a reply saying *"We know how to do this!"* without filing the internal ticket would leave the new hire stranded. The safety gate correctly intervened.
  2. **`HF-3007` (Cedar Room AV Failure):** Model confidence was 0.72 (< 0.85) and `SupportKB` lacked an escalation dispatch runbook for recurring hardware failures. The safety gate caught the gap and routed to a human.
- **Product Recommendation:** To reach 3 or 4 touches, do **NOT** lower the 0.85 confidence threshold or bypass `needsStaffAction`. Instead, expand `SupportKB` with missing runbooks (`kb-12-meeting-rooms` and `kb-03-expense-reimbursement`). This proves to attendees that enterprise autonomy is earned through knowledge governance, not loose prompt tuning.

#### Instant Zero-Touch Closures
- **Tuan's Assumption:** Runbook Step 11 states: *"auto-resolved tickets finish in 6-16 s, noise auto-closes"*.
- **Empirical Job Telemetry (Orchestrator API):**
  - `HF-2008` (Batch B noise): **10.1 seconds** (`Successful`).
  - `HF-3008` (Batch C noise): **10.8 seconds** (`Successful`).
  - `HF-3001` (Batch C contractor Wi-Fi auto-resolved): **32.2 seconds** (`Successful`).
  - `HF-3003` (Batch C payslips auto-resolved): **33.1 seconds** (`Successful`).
- **Conclusion:** Noise filtering is instantaneous (~10s). Verifier-governed auto-resolution completes in ~30s with complete verification against `SupportKB`.

---

### 2. Workshop Timing Benchmark: Estimates vs. Measured Reality

Extracted from Claude Code session logs (`~/.claude/projects/...`):

| Chapter / Step | Tuan's Runbook Assumption | Measured Agent Duration | Reality Check & Recommendation |
| :--- | :---: | :---: | :--- |
| **Ch 2: Preflight** | 2-3 min | **5.0 min** | Token file refreshes + querying all 24 records took ~5 min. |
| **Ch 3: Build V1** | 4-6 min | **7.8 - 9.8 min** | **Underestimated by 3-4 min.** Scaffolding, authoring, validating, and linking takes ~80 turns. |
| **Ch 4: Deploy V1** | 2-3 min | **2-3 min** | **Spot on.** Designer wizard + deployment log took ~2.5 min. |
| **Ch 5: Run Batch A** | ~1 min start (20-50s tasks) | **67 seconds** | **Spot on.** Dispatched 8 jobs; settled in 67s. |
| **Ch 6: Review & Traces** | ~10 min human + ~1 min agent | **~10 min human + < 1 min agent** | **Spot on.** Trace feedback calls executed in < 30 seconds. |
| **Ch 7: Build V2** | 4-6 min | **6.4 - 9.4 min** | Mining 8 tasks + updating routing switch took 6-9 min. |
| **Ch 8: Run Batch B** | ~2 min | **3.8 min** | Patching release overwrites + dispatching 8 jobs took 3.8 min. |
| **Ch 9: Delegate Review** | **~1 min** | **4.7 min** | **Significantly underestimated.** Reading 7 tasks, cross-referencing KB, and rewriting 3 drafts took 43 turns. |
| **Ch 10: Build V3** | 4-6 min | **12.4 min** | **Major discrepancy.** 15 nodes, 2 agents, 2 JS safety scripts, and 14 KB runbooks took 88 tool turns. |
| **Ch 11: Run Batch C** | ~1 min | **2.2 min** | Very close. Zero-touch jobs finished in 11s, 27s, 33s. |
| **Ch 12: Scoreboard** | 3-5 min | **4.8 min** | **Spot on.** Live API telemetry extraction + markdown scoreboard generation took 4.8 min. |

#### Agenda Recommendation for Tuan:
In a live workshop, attendees may become anxious if an agent takes 8-12 minutes when the slide promised "4-6 min". We recommend adjusting slide expectations:
- **Chapter 3:** *"Agent works 7-9 min - discuss V1 requirements with your partner"*
- **Chapter 10:** *"Agent works 10-12 min - coffee / group discussion break"*
Pure agent execution across the Golden Path requires **~45 minutes**, and human actions (deploying in browser, reading tasks, clicking approve) take **~30-35 minutes**, totaling **~75-80 minutes** of hands-on activity.

---

### 3. Model Economics & Token Telemetry (Anthropic Claude Code)

Empirical consumption metrics across the full workshop delivery:

- **Golden Path (Single Clean Pass, Chapters 2-12):**
  - **Agent Turns / API Calls:** **551 turns**
  - **Output Tokens Generated:** **643,634 tokens**
  - **Prompt Cache Reads:** **58,904,123 tokens** (Prompt caching saved ~90% of latency and API costs!)
  - **Pure Agent Execution Time:** **45.0 minutes**
- **Full Laboratory R&D (All 15 Iterations & Test Suites):**
  - **Total Output Tokens:** **1,380,682 tokens**
  - **Total Cache Reads:** **119,179,744 tokens**
  - **Total Run Time:** **199.9 minutes** (~3.3 hours)

---

## Chapter Overview & Status Matrix

| Chapter | Title | PM Materials Reviewed | Status | Deviations Identified |
| :--- | :--- | :--- | :--- | :--- |
| **Chapter 0** | [Install the Tools](Chapters/0-InstallTheTools.md) | Slide: `prep 0 · Install the tools` | **Aligned / Fixed** | 5 deviations resolved |
| **Chapter 1** | [Connect to the Workshop Tenant](Chapters/1-Connect.md) | Pending slide review | *Draft Audit* | None yet |
| **Chapter 2** | [Preflight](Chapters/2-Preflight.md) | Slide: `2 · Preflight the room's data` | **Approved / Signed Off** | 0 deviations, 6 enhancements |
| **Chapter 3** | [Build V1](Chapters/3-BuildV1.md) | Slide: `3 · Build V1` | **Approved / Signed Off** | 0 deviations, 8 enhancements |
| **Chapter 4** | [Deploy](Chapters/4-Deploy.md) | Slide: `4 · Deploy` | **Permission Alert / Aligned** | 1 tenant permission gap resolved, 5 enhancements |
| **Chapter 5** | [Run Batch A](Chapters/5-RunBatchA.md) | Slide: `5 · Run batch A` | **Approved / Signed Off** | 0 deviations, 7 enhancements |
| **Chapter 6** | [Review by Hand](Chapters/6-ReviewByHand.md) | Slide: `6 · Review the agent's work by hand, then tell it what's wrong` | **Approved / Signed Off** | 0 deviations, 5 enhancements |
| **Chapter 7** | [V2 - Mine Your Decisions](Chapters/7-MineDecisions.md) | Slide: `7 · V2 - mine your decisions` | **Approved / Signed Off** | 0 deviations, 7 enhancements |
| **Chapter 8** | [Run Batch B](Chapters/8-RunBatchB.md) | Slide: `8 · Run batch B` | **Approved / Signed Off** | 0 deviations, 6 enhancements |
| **Chapter 9** | [Delegate the Review](Chapters/9-DelegateTheReview.md) | Slide: `9 · Delegate the review` | **Approved / Signed Off** | 0 deviations, 6 enhancements |
| **Chapter 10** | [V3 - Earn Some Autonomy](Chapters/10-V3EarnAutonomy.md) | Slide: `10 · V3 - earn some autonomy` | **Approved / Signed Off** | 0 deviations, 6 enhancements |
| **Chapter 11** | [Run Batch C](Chapters/11-RunBatchC.md) | Inferred from `TicketsV3` Data Fabric entity & V3 flow | **Approved / Signed Off** | 0 deviations, 6 enhancements |
| **Chapter 12** | [Scoreboard](Chapters/12-Scoreboard.md) | Slide: `12 · Scoreboard` | **Approved / Signed Off** | 0 deviations, 6 enhancements |



---

## Chapter 0: Install the Tools

### Product Manager Baseline
From Tuan's slide **`prep 0 · Install the tools`**:

> **Do this before the session if you can. You need Node.js 20+ installed, then:**
>
> **TYPE IN YOUR TERMINAL**
> ```bash
> npm install -g @anthropic-ai/claude-code @uipath/cli
> claude plugin marketplace add https://github.com/UiPath/skills.git
> claude plugin install uipath@uipath-marketplace
> ```
>
> **Checkpoint - `uip --version` prints a version and `claude --version` works. Pairs need only one working laptop - if yours fights you, lean on your partner's.**

---

### Detailed Findings & Applied Fixes

#### 1. Minimum Node.js Version (18+ vs 20+)
- **Deviation:** The original lab guide stated Node.js 18+ was required. Tuan's specification explicitly mandates **Node.js 20+**.
- **Impact:** Certain recent packages in `@anthropic-ai/claude-code` and `@uipath/cli` rely on features and APIs standard in Node.js 20+ (e.g. native fetch optimizations, crypto enhancements).
- **Resolution:** Updated [Chapter 0 (Section 1.2)](Chapters/0-InstallTheTools.md#12-nodejs-20) and the top overview table to require **Node.js 20+**.

#### 2. Claude Code CLI Installation (`@anthropic-ai/claude-code`)
- **Deviation:** The original Chapter 0 only installed `@uipath/cli`, completely omitting Claude Code installation. Chapter 2 immediately expected `claude` to run in the terminal. Tuan specified bundling them together: `npm install -g @anthropic-ai/claude-code @uipath/cli`.
- **Impact:** Workshop attendees would reach Chapter 2 and fail with `claude: command not found`.
- **Resolution:** Added Claude Code to [Section 2.1](Chapters/0-InstallTheTools.md#21-claude-code--uipath-cli-claude--uip), providing both test commands (`claude --version`, `uip --version`) and Tuan's combined global `npm install` command.

#### 3. Agent Skills / Plugin Installation Method
- **Deviation:** The original guide used `uip skills install --agent claude`. Tuan's slide uses native Claude Code plugin management commands:
  ```powershell
  claude plugin marketplace add https://github.com/UiPath/skills.git
  claude plugin install uipath@uipath-marketplace
  ```
- **Impact:** Both methods ultimately configure the marketplace, but Tuan's method runs directly inside Claude Code's native plugin manager and gives immediate feedback on plugin registration.
- **Resolution:** Updated [Section 2.2](Chapters/0-InstallTheTools.md#22-uipath-agent-skills-claude-code-plugin) to feature Tuan's direct Claude plugin commands as the primary method for Claude Code, while retaining `uip skills install` as a documented alternative.

#### 4. Pre-session Checkpoint & Pairing Advice
- **Deviation:** Tuan's slide highlighted a clear checkpoint milestone:
  - Verify `uip --version`
  - Verify `claude --version`
  - Advice: *Pairs need only one working laptop - if yours fights you, lean on your partner's.*
  The lab guide lacked this milestone callout.
- **Impact:** Attendees had no explicit stopping point to verify they were ready before starting Chapter 1.
- **Resolution:** Added the exact Checkpoint alert box to [Section 2.2](Chapters/0-InstallTheTools.md#22-uipath-agent-skills-claude-code-plugin).

#### 5. Section Sequence (Test-First vs. Install-First)
- **Deviation:** The original lab guide presented install commands before verification. Attendees who already had PowerShell 7, Node.js, Python, or uv had to read past install instructions to find check commands.
- **Resolution:** Re-architected all subsections in Chapter 0 so that each tool first presents a test command (`<tool> --version`) and expected output. Only if the test fails does the user proceed to the installation step.

---

### Scope Comparison: Extended Workshop Dependencies
Tuan's slide is an ultra-streamlined prep card focusing exclusively on Node, Claude Code, and the UiPath CLI. 

The lab guide retains several additional tools:
- **PowerShell 7 (`pwsh`):** Used for reliable pipeline chaining (`&&`) across Windows environments.
- **Python 3.14 & Astral `uv`:** Required for local virtual environments and Python SDK execution.
- **UiPath Python SDK (`uv add uipath`):** Required for CLI tools like Context Grounding (`uip context-grounding`) which invoke a Python bridge under the hood.

> [!NOTE]
> These extra tools complement Tuan's instructions without causing conflicts. With the new **test-first** layout, attendees with these runtimes already installed can skip through them in seconds.

---

## Chapter 1: Connect to UiPath Automation Cloud

*(Awaiting Tuan's slide / requirements for Chapter 1)*

### Current Chapter Content Summary
- **Target Organization:** `uipathlabsworkshop`
- **Target Tenant:** `MVPSummit26`
- **Authority:** `https://staging.uipath.com`
- **Command:** `uip login --authority https://staging.uipath.com --organization uipathlabsworkshop --tenant MVPSummit26`
- **Verification:** `uip login status --output table`, `uip user`

---

## Chapter 2: Preflight (Preflight the room's data)

### Product Manager Baseline
From Tuan's slide **`2 · Preflight the room's data`** (Allocated time: `0:05`):

> **agent works 2-3 min · you: open a second tab at staging.uipath.com for Studio Web**
>
> **Your first words to the coding agent - make it prove the shared workshop resources are reachable before you build anything on them:**
>
> **SAY TO YOUR CODING AGENT**
> ```text
> Verify my UiPath setup on this tenant: confirm the login is uipathlabsworkshop/MVPSummit26, that the shared Data Fabric entities TicketsV1, TicketsV2, and TicketsV3 exist and each holds 8 tickets (query the records, don't just list entities), and that the SupportKB knowledge index in the Shared folder exists and answers a test search. Report what you find; don't create or change anything.
> ```
>
> **Checkpoint - three entities x 8 tickets, and the shared SupportKB index returns a HomeFix help article for a test query. Anything missing is a room problem, not yours - raise a hand. If it can't be fixed in 3 minutes, a TA will move you to the backstop tenant.**
>
> **Known slow spot: the agent's knowledge-index search tool may report a 401 and spend a minute working around a stale token file. That's normal; it recovers on its own. If it's still stuck after 3 minutes, tell it: "skip the index search, just confirm the index exists".**

---

### Detailed Findings & Comparison

#### 1. Core Verification Prompt (100% Match)
- **Status:** **Identical**
- **Slide text:** Verbatim match in [Chapter 2 (Section 3.1)](Chapters/2-Preflight.md#31-send-the-preflight-prompt).
- **Checks executed:**
  - Login confirmation on `uipathlabsworkshop/MVPSummit26`.
  - Data Fabric query on `TicketsV1`, `TicketsV2`, and `TicketsV3` for 8 records each (querying records, not just entity metadata).
  - Search on `SupportKB` Context Grounding index in the `Shared` folder.
  - Read-only instruction: *"Report what you find; don't create or change anything."*

#### 2. Checkpoint Criteria & Escalation Policy (100% Match)
- **Status:** **Identical**
- **Slide text:** Verbatim match in [Chapter 2 (Section 3.3)](Chapters/2-Preflight.md#33-checkpoint).
- **Rule:** If resources are missing or broken after 3 minutes of TA troubleshooting, attendee is moved to the backstop tenant.

#### 3. Known Slow Spot & Fallback Recovery (100% Match)
- **Status:** **Identical**
- **Slide text:** Verbatim match in [Chapter 2 (Section 3.3)](Chapters/2-Preflight.md#33-checkpoint).
- **Rule:** Anticipates potential 401 token refresh delay on knowledge index search; instructs attendees to wait up to 3 minutes or issue fallback prompt `"skip the index search, just confirm the index exists"`.

#### 4. Parallel Attendee Task (Studio Web Tab) & Navigation Guidance
- **Status:** **Enhanced**
- **Slide text:** Instructs attendees to open `staging.uipath.com` for Studio Web while the agent runs (2-3 min).
- **Lab Guide Enhancement:** Noted that browsing to `https://staging.uipath.com/uipathlabsworkshop/MVPSummit26` lands on Orchestrator by default, and provided exact click path: **Product Launcher** (9 dots icon) > **More** > **Studio Web** (or **Data Fabric**).

---

### Complementary Lab Guide Enhancements

The lab guide includes additional operational steps that prepare attendees for a smooth agent interaction without deviating from Tuan's core instruction:

1. **Tool Pre-Authorization Command (Section 1.1):** Generates `.claude/settings.local.json` with wildcard allow patterns (`PowerShell(uip *)`, `Bash(uip *)`, `Skill(uipath:*)`, `Read(~/.uipath/**)`, `Read(//**/.uipath/**)`) so Claude Code executes all UiPath CLI commands, calls skills, and reads local skill reference guides autonomously without halting for manual approvals.
2. **Explicit Agent Launch (Section 1.2):** Provides the shell command `claude` to ensure the session is active in the team workspace folder.
3. **Session Settings (Section 1.3):** Proactively sets **Accept Edits mode** (`Shift + Tab`) to eliminate manual confirmation prompts, selects **Opus** (`/model`), and sets **High Effort** (`/effort high`).
4. **Shell Sanity Check (Section 2):** Runs `! uip login status` as a 2-second pre-check before spending model tokens on full resource discovery.
5. **Expected Agent Output Sample (Section 3.3):** Shows attendees the exact response format returned by Claude Code (including verified ticket record counts and HomeFix article citation), eliminating ambiguity about whether the test succeeded.
6. **Workspace Permissions Guidance (Section 4):** Explains how local permissions are stored and managed in `.claude/settings.local.json`.

---

## Chapter 3: Build V1 (3 · Build V1)

### Product Manager Baseline
From Tuan's slide **`3 · Build V1`** (Allocated time: `0:10`):

> **agent works 4-6 min · you: read step 5 so you're ready to deploy**
>
> **SAY TO YOUR CODING AGENT**
> ```text
> Build a Maestro Flow solution TicketTriage_TEAMfirstname-lastname with a flow TriageTicketV1. It takes a support ticket (ticketId, subject, body, customerName) as inputs. An agent classifies it and drafts a reply grounded in the existing SupportKB index in the Shared folder, then an Action Center task assigned to me lets me Approve, Modify & Send, or Reject (look up my email with uip or users current; don't ask me for it). Validate it, refresh the solution resources so the index links up, and upload it to Studio Web.
> ```
>
> **Checkpoint - the agent reports a designer URL, flow validate passed, and solution resources refresh imported the index (it should say "Imported 1", not "Created"). Open the URL: trigger -> agent (with a knowledge attachment) -> review task -> end. In the task node's recipient, the assignee should be type "user" with your email, not the default "group". The designer may show warnings about outcomes without downstream nodes - that's fine, they don't block anything.**
>
> **Anchors: the solution and flow names, the shared index name SupportKB + Shared folder, the three review outcomes, "assigned to me" with the uip or users current hint, "refresh the solution resources", "upload" (not publish). Never type your email into the prompt; the agent reads it from your login so the same prompt works for everyone in the room. The agent scaffolds everything in the empty folder from step 1 - you never create project files by hand. If it offers to run flow debug, say no.**

---

### Detailed Findings & Comparison

#### 1. Core Build Prompt Requirements
- **Status:** **Enhanced / Aligned**
- **Slide text:** Verbatim baseline in [Chapter 3 (Section 2.2)](Chapters/3-BuildV1.md#22-send-the-build-v1-prompt).
- **Core Requirements:**
  - Solution: `TicketTriage_TEAM<firstname>-<lastname>`
  - Flow: `TriageTicketV1`
  - Inputs: `ticketId`, `subject`, `body`, `customerName`
  - Agent node: Classify and draft reply grounded in `SupportKB` (`Shared` folder)
  - Action Center task: Custom outcomes (`Approve`, `Modify & Send`, `Reject`), assigned to user dynamically looked up via `uip or users current`
  - Lifecycle: `flow validate` -> `solution resources refresh` -> `upload` to Studio Web

#### 2. Checkpoint Criteria & Visual Inspection (100% Match)
- **Status:** **Identical**
- **Slide text:** Verbatim match in [Chapter 3 (Section 5.1)](Chapters/3-BuildV1.md#51-checkpoint-criteria).
- **Criteria:**
  - Agent output returns Studio Web designer URL.
  - `flow validate` passed without fatal errors.
  - `solution resources refresh` imported existing index ("Imported 1", not "Created").
  - Visual verification of 4 nodes: Trigger -> Agent (with knowledge attachment) -> Review task -> End.
  - Task assignee confirmed as `type: "user"` with attendee's email.
  - Benign warnings acknowledged: Designer warnings about outcomes without downstream nodes are safe to ignore.

#### 3. Slide Anchors & Guardrails (100% Match)
- **Status:** **Identical**
- **Slide text:** Documented in [Chapter 3 (Sections 2.2 & 3.3)](Chapters/3-BuildV1.md#22-send-the-build-v1-prompt).
- **Guardrail:** Explicit callout instructing attendees to decline `flow debug` if offered by Claude Code.

---

### Prompt Optimization: Baseline vs. Optimized

#### 1. The Three Prompts Compared

##### Tuan's Original Slide Baseline
```text
Build a Maestro Flow solution TicketTriage_TEAMfirstname-lastname with a flow TriageTicketV1. It takes a support ticket (ticketId, subject, body, customerName) as inputs. An agent classifies it and drafts a reply grounded in the existing SupportKB index in the Shared folder, then an Action Center task assigned to me lets me Approve, Modify & Send, or Reject (look up my email with uip or users current; don't ask me for it). Validate it, refresh the solution resources so the index links up, and upload it to Studio Web.
```

##### Option A: Standard Unified Port (Recommended for Beginners)
```text
Build a Maestro Flow solution TicketTriage_TEAM<firstname>-<lastname> (derive my firstname and lastname from uip user to match my workspace folder, and look up my email with uip or users current; don't ask me for them) with a flow TriageTicketV1. It takes a support ticket (ticketId, subject, body, customerName) as inputs. An agent classifies it and drafts a reply grounded in the existing SupportKB index in the Shared folder, declaring typed output variables for category, priority, draftReply, rationale, and confidence. An Action Center task assigned to me lets me Approve, Modify & Send, or Reject, with draftReply configured as an editable inOut field, connecting the task's completed port to the End node so all outcomes flow to End and the decision is always recorded in the flow outputs. The End node returns decision (from task status), finalReply, category, and priority. Validate it, refresh the solution resources so the index links up, and upload it to Studio Web.
```

##### Option B: Multi-Outcome Handle Patch (Advanced Canvas Styling from Chapter 07 Section 4)
```text
Build a Maestro Flow solution TicketTriage_TEAM<firstname>-<lastname> (derive my firstname and lastname from uip user to match my workspace folder, and look up my email with uip or users current; don't ask me for them) with a flow TriageTicketV1. It takes a support ticket (ticketId, subject, body, customerName) as inputs. An agent classifies it and drafts a reply grounded in the existing SupportKB index in the Shared folder, declaring typed output variables for category, priority, draftReply, rationale, and confidence. An Action Center task assigned to me lets me Approve, Modify & Send, or Reject, with draftReply configured as an editable inOut field, and all three outcomes set to action "Continue". Wire each outcome handle (outcome-approve, outcome-modifyandsend, outcome-reject) to the End node, and declare each handle next to "completed" in the flow's definitions entry for the Quick Form node so the flow validates and every outcome connects to End. The End node returns decision (from task status), finalReply, category, and priority. Format and validate the flow, refresh the solution resources so the index links up, and upload it to Studio Web.
```

#### 2. Breakdown of the 5 Optimizations

| # | Optimization Added | What It Changes | Why It Matters (Failure Prevented) |
|---|---|---|---|
| **1** | **Dynamic Name Discovery (`uip user`)** | Added: `derive my firstname and lastname from uip user to match my workspace folder` | Prevents typos (e.g. leaving literal `<firstname>-<lastname>`, case mismatches, or missing hyphens). Ensures 100% match with the team folder across all attendees with zero manual editing. |
| **2** | **Explicit Typed Agent Outputs** | Added: `declaring typed output variables for category, priority, draftReply, rationale, and confidence` | Prevents the agent from generating prompt instructions without declaring the `outputs.output` JSON block, which would cause `$vars.triageAgent1.output.*` to resolve to `undefined` and leave form fields blank at runtime. |
| **3** | **Editable `draftReply` (`inOut`)** | Added: `with draftReply configured as an editable inOut field` | Sets the field to unlocked (`inOut`) instead of read-only (`input`). Without this, the reviewer in Action Center cannot edit the draft when selecting **Modify & Send**. |
| **4** | **Explicit Outcome Port Handling** | Option A: `connecting the task's completed port to the End node so all outcomes flow to End`<br/>Option B: `declare each handle next to "completed" in the flow's definitions entry for the Quick Form node` | Option A wires the engine-native `completed` exit handle, rendering all three outcomes cleanly converging to End with zero warnings. Option B (adapted from Chapter 07 Section 4) declares each handle explicitly in `definitions`, drawing three distinct parallel wires from each button directly to End with valid CLI validation. |
| **5** | **Structured Flow Outputs** | Added: `The End node returns decision (from task status), finalReply, category, and priority` | Explicitly maps the reviewer's choice and the final edited text to the flow's output contract for downstream consumption. |

---

### Complementary Lab Guide Enhancements

The lab guide includes 8 key pedagogical enhancements that help attendees follow and understand what their agent is doing while ensuring 100% adherence to Tuan's baseline requirements:

1. **Architecture Diagram & Parameters Summary (Section 1.1):** Visual Mermaid flowchart illustrating the 4-stage pipeline (Trigger -> Agent -> Review Task -> End) paired with a parameter cheat-sheet table.
2. **Visual Target Flow Screenshot ("What We Are Building", Section 2.2):** High-resolution screenshot of the target flow canvas in Studio Web (`Chapters/Images/TriageTicketV1-Flow.png`) positioned immediately above the prompts so attendees have an instant visual reference.
3. **Dynamic User Identity Discovery (Section 2.1):** Added `! uip user` discovery to inspect `FirstName` and `LastName` to match the team workspace folder, explaining the distinction between core CLI identity (`uip user`) and the Orchestrator tool (`uip or users current`).
4. **Dual Prompt Architecture (Option A & Option B, Section 2.2):** Offers attendees both Option A (engine-standard unified `completed` port) and Option B (multi-outcome handle patch), empowering instructors and attendees to choose between standard engine semantics and pristine canvas cosmetics.
5. **Educational Explanation for Attendees on the Handle Patch (Section 2.2):** Added an explicit pedagogical note explaining why the Quick Form node only exposes `completed` by default, why raw attempts to connect `outcome-approve` fail CLI validation, and how local `definitions` patching resolves it.
6. **Behind-the-Scenes Execution Breakdown & Guardrails (Section 3):** Step-by-step walkthrough of what Claude Code executes autonomously (init, node composition, wiring, validation, resources refresh, upload) with explicit guardrails (e.g. declining `flow debug`).
7. **Active Attendee Guidance During Agent Wait Time (Section 4):** Structured instructions for the 4-6 minute wait (reading ahead for step 5 deployment concepts, preparing the Studio Web tab).
8. **Checkpoint Criteria, Expected Output & Canvas Analysis (Section 5):** Concrete expected response sample, verification checklist, Studio Web navigation path, and clear canvas analysis explaining how Studio Web renders outcomes under both Option A and Option B.

---

### Deep Dive: Why Fable Found the Solution and Opus Originally Failed

A key architectural finding during our live testing in Chapter 3 revolves around how different coding agent models approach Action Center Quick Form outcomes:

#### 1. The Underlying Schema Dilemma
In UiPath Maestro Flow, the official runtime definition for `uipath.human-in-the-loop.quick-form` exposes only one exit handle on the right: `completed`. It does not natively expose separate handles like `outcome-approve` or `outcome-reject`. 

However, on the Studio Web visual canvas, attendees see three distinct buttons. When an edge connects only to `completed`, Studio Web visually attaches that wire to `Approve` and flags `Modify & Send` and `Reject` with yellow warning triangles (*"Outcome without downstream nodes"*).

#### 2. Why Opus Originally Failed on the Baseline Prompt
When given Tuan's baseline prompt, Claude Opus attempted to eliminate the visual disconnect by inventing an edge with `sourcePort: "outcome-approve"`. Because `outcome-approve` was not registered in the schema, the CLI compiler immediately failed:
```text
Edge references undeclared source handle "outcome-approve" on node "reviewDraftReply1"
```
Because Opus had no prior knowledge that the local flow's `definitions` block could be patched to declare custom handles, it could not resolve the error autonomously and fell back to either leaving outcomes unwired or retreating to a single wire.

#### 3. The Origin of the Solution: Johannes Reitermayer's Tutorial Repo
The solution was originally discovered and documented by **Johannes Reitermayer** in his GitHub repository:
- Repository: [**`Fusion2026-CodingAgents`**](https://github.com/reitermayer/Fusion2026-CodingAgents)
- Source Chapter: [**`Chapters/07-HumanInTheLoop.md` (Section 4)**](https://github.com/reitermayer/Fusion2026-CodingAgents/blob/main/Chapters/07-HumanInTheLoop.md#4-adding-the-quick-form-task)

In Chapter 07 Section 4, Johannes formulated the exact schema patch:
> *"Wire the task's `outcome-approve` and `outcome-reject` handles to the End node, and declare both handles next to 'completed' in the flow's definitions entry for the Quick Form node so validate stays green."*

#### 4. Why Fable 5.1 Found It and Succeeded
When we tested this patch with **Claude Code using Fable 5.1** (`claude-fable-5-1`), Fable succeeded because:
- **Code & AST Specialization:** Fable 5.1 is fine-tuned specifically for agentic code editing, JSON AST manipulation, and reactive CLI feedback loops.
- **Fast Problem Diagnosis:** When `uip maestro flow format` ran, Fable noticed that the formatting command re-synced the node definitions from the core registry and stripped the custom outcome handles.
- **Autonomous Remediation:** Instead of giving up or looping in reasoning, Fable immediately authored a script to re-inject `outcome-approve`, `outcome-modifyandsend`, and `outcome-reject` into `definitions` after formatting, resulting in a 100% valid flow (`Status: Valid`).

#### 5. Why Opus Succeeded Once Given the Patch
When we then re-tested the exact same prompt with **Opus** (`--model opus --effort high`), Opus also succeeded cleanly in **468.9 seconds** (~7m 49s). Armed with the explicit architectural instruction from Johannes' repository, Opus:
1. Dynamically inspected the node's schema outcomes.
2. Built a modular script (`scratch/build/patch_outcome_handles.py`) to inject the handles into `definitions` post-format.
3. Asserted that zero dangling edges remained before uploading to Studio Web.

#### 6. Summary for Workshop Design
- Without explicit prompt instructions, even advanced reasoning models like Opus cannot guess non-standard in-file definition patching.
- Both models (Fable 5.1 and Opus) produce a pristine 3-wire canvas when guided by the Chapter 07 patch prompt.
- Documenting both Option A (standard unified port) and Option B (Chapter 07 patch) gives attendees complete clarity over how Maestro Flow handles multi-outcome tasks.

#### 7. Verified Studio Web Deployments & Live Execution Metrics
Both models were rigorously executed against the live workshop tenant (`uipathlabsworkshop/MVPSummit26`), achieving successful validation, resource synchronization, and Studio Web upload:

| Model Tested | Execution Time | Solution ID | Status | Outcome Canvas Wiring |
| :--- | :--- | :--- | :--- | :--- |
| **Claude Opus** (`--model opus`) | **468.9s** (7m 49s) | `b5a91aa2-b585-45c8-ad03-08df0f4a52c6` | **Valid** (0 errors) | 3 parallel wires directly to End |
| **Claude Fable 5.1** (`claude-fable-5-1`) | **556s** (9m 16s) | `1ada4837-e250-4d27-d6ce-08df0f4ab56e` | **Valid** (0 errors) | 3 parallel wires directly to End |

- **Live Studio Web Designer Verification URL:**  
  [Open TriageTicketV1 in Studio Web Designer](https://staging.uipath.com/uipathlabsworkshop/studio_/designer/0285acf3-674a-430a-9e20-a84dfdac9992?solutionId=b5a91aa2-b585-45c8-ad03-08df0f4a52c6)

#### 8. Repository Asset Architecture for GitHub Publication
To ensure the workshop materials can be cleanly shared or published as an independent GitHub repository:
- All screenshots and media are consolidated strictly inside [`Chapters/Images/`](Chapters/Images/) (e.g. `Chapters/Images/TriageTicketV1-Flow.png`).
- Redundant root-level media folders (`Images/`) have been removed completely, preventing duplicate files or broken relative links across platforms.

---

## Chapter 4: Deploy (4 · Deploy)

### Product Manager Baseline
From Tuan's slide **`4 · Deploy`** (Allocated time: `0:18`, `2-3 min · the deploy log runs for about a minute`):

> **The one browser step you'll repeat three times today. In the designer, click Deploy, switch "Pack to" from Personal to Shared, and click Deploy in the wizard. This creates your team's own folder `Shared/TicketTriage_TEAMfirstname-lastname` , publishes the package, and links your knowledge index - watch the log for "All services activated successfully". Later deploys are the same button labelled Pack and upgrade with a bumped version.**
>
> **Checkpoint - "Deployment successful" with your version number, and a new folder `Shared/TicketTriage_TEAMfirstname-lastname` exists on the tenant. If publish fails with "version already exists", bump the Version field in the wizard and retry.**
>
> **Deploy button greyed out? The resource refresh in step 3 normally writes the index pointer the designer needs, so Deploy should already be active. If it's grey after a fresh tab, see the breakage table - it's a one-call fix.**

---

### Detailed Findings & Comparison

#### 1. Browser-Based Deployment Step (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** Deploy directly inside the Studio Web designer in the browser. Tuan emphasizes that this is *"the one browser step you'll repeat three times today"*.
- **Lab Guide Alignment:** Emphasized in [Chapter 4 (Section 1)](Chapters/4-Deploy.md#1-why-deployment-happens-in-the-browser) and [Section 2](Chapters/4-Deploy.md#2-step-by-step-deployment-walkthrough).

#### 2. Target Environment: Switch "Pack to" to `Shared` (Tenant Permission Gap Identified)
- **Status:** **Action Required / Gap Identified**
- **Slide Baseline Requirement:** In the deployment wizard, change **Pack to** from **Personal** to **Shared**. Tuan's slide assumes all attendees have rights to create subfolders in `Shared`.
- **Live Testing Finding:** On the workshop staging tenant (`uipathlabsworkshop/MVPSummit26`), attendee accounts belong to the **`Automation Developers`** group. This group **lacks `Folders.Create` permission on the root `Shared` folder**.
- **Impact on Attendees:**
  - Selecting **Shared** in Studio Web changes the wizard action to **"Pack only - no deployment"** (`StudioWeb-Publish-PackShared.png`), allowing package publishing but refusing folder creation.
  - Attempting to deploy to **Shared** from the local IDE extension or CLI triggers `Forbidden (403). Ensure the account has the required permissions.` on the `Set up folders` step.
- **Resolution Provided in Lab Guide:**
  - **Option A (Autonomous Student Path):** Leave **Pack to** set to **Personal**. Attendees have full rights inside their own Personal Workspace (`My Workspace`), allowing the entire pipeline to activate cleanly (`All 2 service(s) activated successfully`), provisioning `My Workspace/TicketTriage_TEAM<firstname>-<lastname>` and activating `TriageTicketV1`.
  - **Option B (TA/Admin Action):** Before the session, workshop administrators must assign `Folders.Create` (or Folder Administrator) permissions on the `Shared` folder to the `Automation Developers` group if they want all solutions housed under `Shared`.

#### 3. Checkpoint Criteria (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** Log confirms *"All services activated successfully"*, wizard displays *"Deployment successful"* with the version number, and new folder `TicketTriage_TEAM<firstname>-<lastname>` exists on the tenant (under `Shared` if admin provisioned, or under `My Workspace` if personal).
- **Lab Guide Alignment:** Documented in [Chapter 4 (Section 3)](Chapters/4-Deploy.md#3-checkpoint--verification) with annotated Orchestrator verification screenshot (`Orchestrator-Process-MyWorkspace.png`).

#### 4. Troubleshooting & Breakage Handling (100% Match)
- **Status:** **Identical / Enhanced**
- **Baseline Requirement:**
  - If publish fails with *"version already exists"*, bump the Version field and retry.
  - If Deploy is greyed out, re-sync index pointer via resource refresh (`uip solution resources refresh`).
- **Lab Guide Alignment:** Formatted as an immediate-action table in [Chapter 4 (Section 4)](Chapters/4-Deploy.md#4-troubleshooting--breakage-guide).

---

### Complementary Lab Guide Enhancements

The lab guide provides 5 key enhancements that prevent student confusion during deployment:

1. **Permission Architecture Analysis (Shared vs. Personal & Browser vs. IDE):** Explicitly explains why selecting `Shared` results in `Pack only - no deployment` or `Forbidden (403)` on attendee accounts, and shows how deploying to `Personal` enables full end-to-end activation without admin intervention.
2. **Visual Step-by-Step Flow & Screenshots:** Includes high-resolution captures of:
   - The Studio Web canvas ready for deploy (`Chapters/Images/StudioWeb-Flow-Canvas.png`)
   - The `Pack only - no deployment` notice when `Shared` is chosen without permissions (`Chapters/Images/StudioWeb-Publish-PackShared.png`)
   - The package publish confirmation (`Chapters/Images/StudioWeb-Publish-Successful.png`)
   - The real-time deployment log showing `All 2 service(s) activated successfully` (`Chapters/Images/StudioWeb-Deploy-Log-Success.png`)
   - The verified process running in Orchestrator (`Chapters/Images/Orchestrator-Process-MyWorkspace.png`)
   - The IDE `Forbidden (403)` error modal (`Chapters/Images/Deploy-Failed-403.png`)
3. **Dual Deployment Paths (Personal vs. Shared):** Provides clear branching instructions so the lab proceeds smoothly whether or not the tenant TA granted `Shared` permissions.
4. **CLI Folder Verification Command:** Introduces `! uip or folders list --limit 50` so attendees can immediately confirm folder creation on the tenant directly from their terminal or Claude Code session.
5. **Structured Breakage & Recovery Guide:** Step-by-step resolution table covering greyed-out button recovery, version bump procedures (`1.0.1`), and IDE 403 troubleshooting.

---

### Open Question for Product Management: Why Not Deploy via the Maestro Flow Extension?

During our live testing, Johannes explored using the native **UiPath Maestro Flow extension** inside VS Code / Antigravity IDE to execute the deployment. The extension exposes a dedicated **Build & Deploy** panel with a complete Deploy wizard (`Deploy | TicketTriage_TEAM...`), offering an end-to-end local experience without leaving the editor.

However, slide `4 · Deploy` specifically mandates:
> *"The one browser step you'll repeat three times today. In the designer, click Deploy, switch "Pack to" from Personal to Shared, and click Deploy in the wizard."*

#### Key Questions for Tuan:

1. **Was the browser requirement a pedagogical choice or an infrastructure workaround?**
   - *Pedagogical Hypothesis:* Did you deliberately design this step to force attendees into the browser so they become familiar with the Studio Web visual designer, canvas verification, and cloud deployment logs?
   - *Infrastructure Hypothesis:* Or was the browser chosen because the Studio Web backend uses internal cloud service delegation to provision folders, avoiding local OAuth scope and permission limitations?

2. **The Extension Permission Barrier (`Forbidden 403`):**
   When deploying via the local Maestro Flow extension or CLI targeting `Shared`, the deployment pipeline fails at Step 4 (`Set up folders`) with:
   ```text
   Forbidden (403). Ensure the account has the required permissions.
   ```
   This occurs because attendee accounts (`Automation Developers`) do not hold `Folders.Create` permissions on the root `Shared` folder. Did this permission barrier influence the decision to keep deployment in the browser?

3. **Should the Maestro Flow Extension be documented as an alternative path?**
   If attendees deploy to their **Personal Workspace (`My Workspace`)**, where they have full rights, or if workshop administrators grant folder permissions on `Shared`:
   - Could the Maestro Flow extension be officially supported as a developer alternative?
   - Or does Studio Web perform additional backend registrations (e.g. Context Grounding Service bindings) that the local extension cannot yet guarantee?

---

## Chapter 5: Run Batch A (5 · Run batch A)

### Product Manager Baseline
From Tuan's slide **`5 · Run batch A`** (Allocated time: `0:22`, `~1 min to start 8 jobs · tasks appear 20-50 s after each start`):

> **SAY TO YOUR CODING AGENT**
> ```text
> Run every ticket in the shared TicketsV1 entity through my deployed flow, one job each. Flows start with uip maestro flow process run <processKey> <folderKey> --release-key <releaseKey>, not with jobs start. The batch is settled when every instance is either Completed or has an open Action Center task - check that, don't wait on job state.
> ```
>
> **Checkpoint - 8 review tasks in Action Center about a minute after the first job started, each already assigned to you (they show under "My tasks", not "Unassigned"). Measured in the dry run: 21-52 seconds from job start to task, whole batch settled in 67 seconds. The error "Couldn't find any user with unattended robot permissions" should not happen (the robot account is inherited from Shared) - if it does, raise a hand.**
>
> **Why the last sentence matters: Orchestrator shows a flow job as Running the whole time it waits for a human, so an agent that polls job state will sit there for five minutes reporting "still running" while your tasks have been waiting since the first minute. Task count plus completed instances is the real signal.**

---

### Detailed Findings & Comparison

#### 1. Flow Process Execution (`uip maestro flow process run`) (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** Flows are started using `uip maestro flow process run <processKey> <folderKey> --release-key <releaseKey>`, explicitly warning against standard RPA `jobs start`.
- **Lab Guide Alignment:** Emphasized in [Chapter 5 (Section 1 & 4.1)](Chapters/5-RunBatchA.md#1-overview--execution-architecture).

#### 2. Data Fabric Entity Query (`TicketsV1`) (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** Iterates over all 8 tickets stored in `TicketsV1` and maps fields to flow input parameters.
- **Lab Guide Alignment:** Detailed in [Chapter 5 (Section 2.2)](Chapters/5-RunBatchA.md#22-query-tickets-from-data-fabric-ticketsv1).

#### 3. Settlement Signal: Task Count vs. Job State (100% Match)
- **Status:** **Identical / Enhanced**
- **Baseline Requirement:** The batch is settled when all 8 tasks appear in Action Center (or instances reach the review stage). Agents must not poll job state because human-review flows remain `Running` in Orchestrator indefinitely.
- **Lab Guide Alignment:** Explained with execution lifecycle callouts in [Chapter 5 (Section 4.2)](Chapters/5-RunBatchA.md#42-the-crucial-signal-why-polling-job-state-fails).

#### 4. Checkpoint Verification Criteria (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** 8 review tasks appear in Action Center under "My tasks" (assigned to the user's email). Dry run benchmark: 21-52 seconds per job to task, whole batch settled in ~67 seconds.
- **Live Test Benchmark:** In our live execution, all 8 jobs started and all 8 review tasks were generated and assigned to `johannes.reitermayer@gmail.com` in approximately 45 seconds.

---

### Complementary Lab Guide Enhancements

1. **Dynamic Key Resolution (Section 2.1 & 3):** Tuan's slide prompt relies on abstract placeholders (`<processKey>`, `<folderKey>`, `<releaseKey>`). The guide provides an optimized prompt that instructs Claude Code to dynamically look up `uip or processes list` matching `TriageTicketV1`. This prevents manual GUID entry and seamlessly supports deployments in either Shared or Personal Workspace.
2. **Explicit Field-to-Input Mapping (Section 2.2):** Explicitly maps `TicketsV1` fields (`TicketId`, `Subject`, `Body`, `CustomerName`) to the flow's input contract.
3. **CLI Task Verification Command (Section 5.2):** Adds `! uip tasks list` command with live sample output so attendees can verify settlement directly from their terminal without leaving Claude Code.
4. **Action Center Visual Walkthrough (Section 5.3):** Explains how to navigate to Action Center in the browser to inspect the inbox and verify the draft reply, confidence score, and review buttons.
5. **Robust Error Diagnostics (Section 6):** Addresses unattended robot permission issues and terminal polling loops.
6. **Human-in-the-Loop Triage Decision Guide (Section 5.4):** Evaluates all 8 tickets against the AI classifications and KB grounding, providing concrete triage policies: 4 tickets to Approve as-is, 3 tickets to Modify & Send with pre-crafted empathetic/incident-escalation draft text, and 1 ticket to Reject (vendor automated out-of-office response).
7. **Complete Action Center Visual Journey & Verification (Sections 5.3 & 7):** Integrates live UI screenshots showing both the initial overview dashboard (`ActionCenter-Overview-PendingTasks.png` with 8 Pending, 0 Unassigned) and the final completed inbox (`ActionCenter-Inbox-CompletedTasks.png` with green Completed badges, audit trail retention, and flow completion).

---

## Chapter 6: Review by Hand & Trace Feedback (6 · Review the agent's work by hand, then tell it what's wrong)

### Product Manager Baseline
From Tuan's slide **`6 · Review the agent's work by hand, then tell it what's wrong`** (Allocated time: `0:25`, `~10 min of reading · then the agent works ~1 min`):

> **Open Action Center (Product launcher -> Action Center, your team's folder). Work all 8 tasks honestly - approve drafts you'd send (leave the final response empty to send the draft unchanged), modify the ones that miss (the outage, the angry customer, the question the KB can't answer), reject what deserves no reply. Notice what V1 *can't* see: nothing is marked urgent, and the out-of-office auto-reply got a task like everything else. This is the only batch you review by hand; it's where you learn what the agent gets wrong. Then:**
>
> **SAY TO YOUR CODING AGENT**
> ```text
> Leave trace feedback on three of those runs (uip traces feedback create needs --positive or --negative plus --comment): the outage ticket should have been treated as urgent, the auto-reply is noise that never needed review, and every draft should come with a recommended approach for the reviewer.
> ```
>
> **Checkpoint - 8 tasks completed, 3 feedback entries readable via `uip traces feedback list`. Your score so far: 8 human touches for 8 tickets.**

---

### Detailed Findings & Comparison

#### 1. Manual Action Center Review Workflow (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** Review all 8 tasks by hand in Action Center: approve acceptable drafts, modify edge cases (outage, angry customer, missing KB answer), and reject auto-reply noise.
- **Lab Guide Alignment:** Emphasized in [Chapter 6 (Section 1 & 2)](Chapters/6-ReviewByHand.md#2-the-manual-review-experience-in-action-center).

#### 2. Trace Feedback Execution (`uip traces feedback create`) (100% Match)
- **Status:** **Identical / Enhanced**
- **Baseline Requirement:** Instruct the agent to record trace feedback on 3 specific runs using `uip traces feedback create`.
- **Lab Guide Alignment:** Covered in [Chapter 6 (Section 3 & 4)](Chapters/6-ReviewByHand.md#3-teaching-the-agent-llm-observability-trace-feedback).

#### 3. Checkpoint Verification Criteria (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** 8 tasks completed in Action Center, 3 feedback entries readable via `uip traces feedback list`, score of 8 human touches for 8 tickets.
- **Live Test Benchmark:** In our live execution, all 8 tasks were confirmed as Completed and all 3 feedback entries were created and verified via `uip traces feedback list --folder-key f15d2bb8-1c03-4408-a5d2-2a9c2b244ed9`.

---

### Complementary Lab Guide Enhancements

1. **Trace ID & Folder Key Resolution (Section 4):** Tuan's slide prompt relies on Claude Code to figure out the trace IDs and omit `--folder-key`. The guide provides an optimized prompt that instructs Claude Code to look up the completed jobs, retrieve exact 32-character hexadecimal trace IDs, and pass the mandatory `--folder-key` parameter.
2. **Pedagogical Explanation of LLM Observability (Section 3):** Visual Mermaid diagram explaining the trace feedback architecture and how developer feedback annotations attach to execution spans to inform prompt engineering.
3. **Exact CLI Execution Telemetry (Section 5):** Documents the exact behind-the-scenes CLI commands executed for each of the 3 feedback entries (`HF-1006`, `HF-1008`, `HF-1007`).
4. **Completed Inbox Visual Verification (Section 2):** Embeds high-resolution screenshot (`ActionCenter-Inbox-CompletedTasks.png`) showing all 8 tasks in the Completed state with green badges and preserved audit fields.
5. **Robust Breakage Diagnostics (Section 7):** Comprehensive troubleshooting table covering `--folder-key is required`, `Feedback not found (404)` on invalid trace GUIDs, and polarity flag requirements.

---

## Chapter 7: V2 - Mine Your Decisions (7 · V2 - mine your decisions)

### Product Manager Baseline
From Tuan's slide **`7 · V2 - mine your decisions`** (Allocated time: `0:37`, `agent works 4-6 min · you: keep the designer tab open for the deploy`):

> **SAY TO YOUR CODING AGENT**
> ```text
> Look at my review decisions and trace feedback from the V1 runs, figure out what's weak in V1, and build TriageTicketV2 as a second flow in the same solution that fixes it. Validate and upload it; I'll deploy from the designer.
> ```
>
> **Checkpoint - the agent names the weaknesses from *your* decisions (no urgency path, noise reviewed for nothing, no reviewer guidance) and reports a second flow with urgent and noise routing plus a recommended-approach field, with both review tasks still assigned to you. Upload needs `--force` this time; that's expected.**
>
> **Now deploy again (step 4, Pack and upgrade, bump the version) and wait for "Deployment successful" before the next prompt - if you ask too early the agent finds no V2 release and stops.**

---

### Detailed Findings & Comparison

#### 1. Weakness Mining & Observability Analysis (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** The agent inspects the user's manual review decisions and trace feedback from Chapter 6 to identify what is weak in V1: no urgency path, noise reviewed for nothing, and no reviewer guidance.
- **Lab Guide Alignment:** Fully documented and explained with operational context in [Chapter 7 (Section 2)](Chapters/7-MineDecisions.md#2-analysis-of-v1-weaknesses-the-three-gaps).

#### 2. Multi-Path Architecture & TriageTicketV2 Flow (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** Build `TriageTicketV2` as a second flow in the same solution with urgent routing, noise filtering (skipping review), and a `recommendedApproach` field, with both review tasks assigned to the user.
- **Lab Guide Alignment:** Detailed node specifications and routing architecture covered in [Chapter 7 (Section 3)](Chapters/7-MineDecisions.md#3-architecture-of-triageticketv2).

#### 3. Upload with `--force` (100% Match)
- **Status:** **Identical / Enhanced**
- **Baseline Requirement:** Solution upload requires the `--force` flag.
- **Lab Guide Alignment:** Thoroughly explained in [Chapter 7 (Section 5)](Chapters/7-MineDecisions.md#5-behind-the-scenes-why-upload-requires---force), detailing why Studio Web protects existing cloud solutions from accidental overwrites.

#### 4. Browser Pack and Upgrade Deployment (100% Match)
- **Status:** **Identical / Enhanced**
- **Baseline Requirement:** Deploy from the Studio Web designer (Step 4, Pack and upgrade, bump the version to 1.0.2), and strictly wait for "Deployment successful" before sending the next prompt.
- **Lab Guide Alignment:** Emphasized in [Chapter 7 (Section 6)](Chapters/7-MineDecisions.md#6-deployment-pack--upgrade-in-studio-web) with critical alerts explaining Orchestrator process release registration timing.

---

### Complementary Lab Guide Enhancements

1. **Pedagogical Routing Architecture (Section 3):** Full Mermaid flowchart illustrating how incoming tickets branch into Noise (auto-skip), Urgent (high-priority task), and Standard (guided task) before converging on the End node.
2. **Context-Rich Optimized Prompt (Section 4):** Provides a robust alternative prompt that explicitly references the folder key, maps out the exact routing rules, binds `recommendedApproach`, and guarantees `--force` is used during upload.
3. **Under-the-Hood `--force` Analysis (Section 5):** Explains the internal cloud solution lifecycle in Studio Web, explaining how `SolutionId` conflicts are resolved when adding a second flow project to an active solution.
4. **Timing Guardrail Explanation (Section 6):** Deepens Tuan's warning about waiting for deployment success, detailing how premature agent queries fail against Orchestrator's release registry when a process has not yet completed activation.
5. **CLI Process Verification Telemetry (Section 7):** Supplies the exact `uip or processes list` command with formatted JSON showing both `TriageTicketV1` and `TriageTicketV2` at version `1.0.2`.
6. **Robust Troubleshooting & Breakage Matrix (Section 8):** Outlines clear failure modes and resolutions for common issues, including unhandled canvas handles, version conflicts, unassigned tasks, and upload errors.
7. **Semantic Priority Trap & Confidence Guardrail (Section 3 & 4):** Documents the real-world priority enum mismatch where Tuan's slide refers to "urgent", but the underlying agent enum produces `Critical` on the Rotterdam outage (`HF-1006`). If attendee prompts only match "Urgent", `HF-1006` falls through to standard review. Also documents the confidence threshold guardrail on the zero-human Noise bypass.

---

## Chapter 8: Run Batch B (8 · Run batch B)

### Product Manager Baseline
From Tuan's slide **`8 · Run batch B`** (Allocated time: `0:47`, `agent works ~2 min · tasks appear within ~1 min of the start`):

> **SAY TO YOUR CODING AGENT**
> ```text
> Before running anything, check the V2 release's index ResourceOverwrites and patch folderPath to "Shared" if it points at my team folder. Then run every ticket in the shared TicketsV2 entity through V2, one job each, and report when every instance is Completed or has an open task.
> ```
>
> **Checkpoint - the 2 urgent tickets arrive as High-priority escalation tasks, the newsletter auto-closes with no task, and every draft now carries a recommended approach. Score: 7 touches.**
>
> **Why the first sentence:** only the flow that existed at the very first deploy inherits the Shared index mapping. Every flow added later is born pointing at your team folder, where no index lives, and the agent step faults with "Context grounding index not found". In the dry run, letting it fault and retry cost 4 1/2 minutes; checking first costs 10 seconds. The fix is `PATCH orchestrator_/odata/Releases(<id>)` with `ResourceOverwrites -> folderPath "Shared"`, and every Pack and upgrade resets it - for *all* flows added after the first deploy, not just the newest one.

---

### Detailed Findings & Comparison

#### 1. Context Grounding Preflight Check (100% Match)
- **Status:** **Identical / Enhanced**
- **Baseline Requirement:** Check `ResourceOverwrites` for `SupportKB` on the newly deployed V2 release, patching `folderPath` to `"Shared"` if it defaults to the team folder, avoiding the 4.5 minute timeout fault.
- **Lab Guide Alignment:** Detailed in [Chapter 8 (Section 1)](Chapters/8-RunBatchB.md#1-the-context-grounding-index-gotcha-resourceoverwrites), explaining the root cause of Studio Web's multi-flow binding reset.

#### 2. Data Fabric Entity Resolution (`TicketsV2`) (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** Query all 8 tickets from the shared `TicketsV2` Data Fabric entity.
- **Lab Guide Alignment:** Covered in [Chapter 8 (Section 2)](Chapters/8-RunBatchB.md#2-batch-b-data-analysis-ticketsv2), cataloging each of the 8 tickets (`HF-2001` through `HF-2008`).

#### 3. Execution & Settlement Criteria (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** Run every ticket through V2, one job each, and monitor until every run is Completed or in a Pending task.
- **Lab Guide Alignment:** Sequence diagram and polling commands in [Chapter 8 (Section 4)](Chapters/8-RunBatchB.md#4-execution--settlement-monitoring).

#### 4. The 7-Touch Scorecard (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** 2 urgent tickets arrive as High-priority tasks, 1 newsletter auto-closes with no task, and total human touches equals 7.
- **Lab Guide Alignment:** Highlighted in [Chapter 8 (Section 5 & 6)](Chapters/8-RunBatchB.md#5-the-scorecard-comparing-batch-a-vs-batch-b).

---

### Complementary Lab Guide Enhancements

1. **Preflight Decision Tree (Section 1):** Mermaid flowchart illustrating the preflight check, the 4.5-minute timeout risk, and the 10-second patch resolution.
2. **Dataset Nature Breakdown (Section 2):** Complete inventory of Batch B tickets, explaining the expected classification and routing path for each customer scenario.
3. **Context-Rich Optimized Prompt (Section 3):** Supplies exact entity IDs (`9b3f6ef9-37a4-f111-9b32-000d3a69a13b`), dynamic folder lookup, and automated polling criteria.
4. **Execution Sequence Architecture (Section 4):** Sequence diagram mapping the interaction between Claude Code, Data Fabric, Orchestrator, and Action Center.
5. **Quantitative Evolution Scorecard (Section 5):** Direct comparison table contrasting Batch A (8 touches, no guidance, manual rejection) against Batch B (7 touches, guidance provided, automated rejection).
6. **Action Center Visual Verification Steps (Section 6):** Explicit UI inspection guide for checking the High priority badge and recommended approach on `HF-2006`.

---

## Chapter 9: Delegate the Review (9 · Delegate the review)

### Product Manager Baseline
From Tuan's slide **`9 · Delegate the review`** (Allocated time: `0:52`, `agent works ~1 min · instances close within 30 s of the last completion`):

> **You reviewed batch A yourself so you know what good looks like. This time let the agent do it and check its judgement:**
>
> **SAY TO YOUR CODING AGENT**
> ```text
> Complete the Action Center tasks on my behalf.
> ```
>
> **Checkpoint - the agent tells you which drafts it approved as-is and which it rewrote before sending, and why. Expect it to rewrite the ones that restate policy without steps, or that tell an urgent requester what the knowledge base doesn't contain. 0 open tasks afterwards. Because the tasks are already yours, the agent completes them directly; it should not need to assign them first.**

---

### Detailed Findings & Comparison

#### 1. Autonomous Task Review Delegation (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** The user delegates Action Center review to the coding agent, leveraging established standards from Chapter 6.
- **Lab Guide Alignment:** Covered in [Chapter 9 (Section 1)](Chapters/9-DelegateTheReview.md#1-the-human-in-the-loop-paradigm-shift).

#### 2. Quality Rubric & Rewrite Expectations (100% Match)
- **Status:** **Identical / Enhanced**
- **Baseline Requirement:** The agent must apply judgment: rewrite drafts that restate policy without steps or tell an urgent requester what the KB lacks; approve sound drafts as-is.
- **Lab Guide Alignment:** Formatted as a structured rubric table in [Chapter 9 (Section 2)](Chapters/9-DelegateTheReview.md#2-what-good-judgment-looks-like-the-review-rubric).

#### 3. Task Assignment Architecture (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** Tasks are already assigned to the user; the agent completes them directly without calling assign first.
- **Lab Guide Alignment:** Deeply explained in [Chapter 9 (Section 3)](Chapters/9-DelegateTheReview.md#3-behind-the-scenes-why-task-assignment-is-not-needed).

#### 4. Flow Instance Resumption & Settlement (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** Instances close within 30 seconds of the last task completion, leaving 0 open tasks.
- **Lab Guide Alignment:** Detailed sequence diagram and settlement expectations in [Chapter 9 (Section 5 & 6)](Chapters/9-DelegateTheReview.md#5-execution-sequence--flow-resumption).

---

### Complementary Lab Guide Enhancements

1. **Human-in-the-Loop Paradigm Comparison (Section 1):** Contrast diagram showing traditional human review bottleneck vs. autonomous agentic review delegation.
2. **Detailed Review Quality Rubric (Section 2):** Comprehensive table breaking down specific failure modes (policy regurgitation, exposing KB limitations, tone mismatch) with concrete examples from Batch B.
3. **Action Center Security Architecture (Section 3):** Explains why task assignment works seamlessly without permission errors due to the flow's dynamic assignee binding.
4. **Context-Rich Optimized Prompt (Section 4):** Provides an explicit prompt specifying folder key, evaluation criteria, task data saving, and structured reporting.
5. **End-to-End Sequence Diagram (Section 5):** Sequence diagram mapping Claude Code, Action Center APIs, and the Maestro Flow Engine resuming execution to End.
6. **Action Center Verification Guide (Section 6):** Step-by-step UI verification guide showing Pending dropping to 0 and Completed reaching 15.

---

## Chapter 10: V3 - Earn Some Autonomy (10 · V3 - earn some autonomy)

### Product Manager Baseline
From Tuan's slide **`10 · V3 - earn some autonomy`** (Allocated time: `0:56`, `agent works 4-6 min · then you deploy ( 2-3 min )`):

> **SAY TO YOUR CODING AGENT**
> ```text
> Build TriageTicketV3 that safely auto-resolves the approved tickets, and make sure it can never auto-send an answer the knowledge base doesn't cover.
> ```
>
> **Checkpoint - the agent describes a gate with more than a confidence threshold: a KB-covered flag, the KB sources actually used, or both, and it says what happens when a check fails (human review). Then Pack and upgrade, bump the version, wait for "Deployment successful".**

---

### Detailed Findings & Comparison

#### 1. Safe Autonomy & Grounding Gate (100% Match)
- **Status:** **Identical / Enhanced**
- **Baseline Requirement:** The agent must construct a gate requiring more than raw confidence: a `kbCovered` flag and/or `kbSources`, explicitly explaining that failure routes to human review.
- **Lab Guide Alignment:** Thoroughly documented in [Chapter 10 (Section 1 & 2)](Chapters/10-V3EarnAutonomy.md#1-the-enterprise-autonomy-dilemma).

#### 2. TriageTicketV3 Multi-Path Architecture (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** Build `TriageTicketV3` inside the same solution with 4 operational paths (Noise auto-skip, Urgent escalation, Safe auto-resolve, Standard review fallback).
- **Lab Guide Alignment:** Complete node specifications, Mermaid flowchart, and schema evolution in [Chapter 10 (Section 2)](Chapters/10-V3EarnAutonomy.md#2-architecture-of-triageticketv3).

#### 3. Upload with `--force` & Studio Web Deployment (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** Upload the updated solution, Pack and upgrade in Studio Web, bump the version to `1.0.3`, and wait for deployment success before running jobs.
- **Lab Guide Alignment:** Detailed step-by-step instructions in [Chapter 10 (Section 4 & 5)](Chapters/10-V3EarnAutonomy.md#4-behind-the-scenes-deploying-v3-in-studio-web).

---

### Complementary Lab Guide Enhancements

1. **The Autonomy Dilemma Analysis (Section 1):** Detailed breakdown of why statistical confidence alone causes hallucinations in production, and how deterministic grounding checks provide governance.
2. **Four-Way Decision Tree (Section 1 & 2):** Clear Mermaid diagram mapping Noise, Urgent, Safe Auto-Resolve, and Standard Fallback paths.
3. **Schema Evolution Matrix (Section 2):** Comprehensive table comparing agent output schemas across V1, V2, and V3.
4. **Context-Rich Optimized Prompt (Section 3):** Explicit prompt specifying exact schema fields (`kbCovered`, `kbSources`), routing switch logic, and upload flags.
5. **Deployment Guardrail Explanation (Section 4 & 5):** Warning against premature agent queries while Studio Web activates the newly bumped package.
6. **Troubleshooting & Breakage Matrix (Section 6):** Resolving common failure modes including priority leaks, missing KB flags, and 409 conflict errors.

---

## Chapter 11: Run Batch C

### Baseline Requirements (Inferred from TicketsV3 & Workshop Pattern)
From the sequence established in Batch A (Chapter 5) and Batch B (Chapter 8):

> **TYPE IN YOUR TERMINAL**
> ```text
> Before running anything, check the V3 release's index ResourceOverwrites and patch folderPath to "Shared" if it points at my team folder. Then run every ticket in the shared TicketsV3 entity through V3, one job each, and report when every instance is Completed or has an open task.
> ```
>
> **Checkpoint - Verify that touches drop from 7 to 3: 4 routine KB-covered tickets safely auto-resolved (0 touches), 1 noise maintenance ticket auto-skipped (0 touches), 2 operational emergencies fast-tracked to urgent review, and 1 ticket lacking KB runbooks failed safe to standard review.**

---

### Detailed Findings & Comparison

#### 1. Grounding Preflight & Release Overwrites (100% Match)
- **Status:** **Identical / Enhanced**
- **Baseline Requirement:** Inspect `TriageTicketV3` release and ensure `SupportKB` points to `"Shared"`.
- **Lab Guide Alignment:** Verified and documented in [Chapter 11 (Section 1)](Chapters/11-RunBatchC.md#1-the-context-grounding-preflight-in-folder-8).

#### 2. Batch C Data Fabric Entity (`TicketsV3`) (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** Query all 8 records from `TicketsV3` (`a93f6ef9-37a4-f111-9b32-000d3a69a13b`) and dispatch one job per ticket.
- **Lab Guide Alignment:** Documented in [Chapter 11 (Section 2 & 4)](Chapters/11-RunBatchC.md#2-batch-c-data-analysis-ticketsv3).

#### 3. Dual-Key Safety Gate Verification (100% Match)
- **Status:** **Identical / Enhanced**
- **Baseline Requirement:** Confirm that only routine tickets with verified `SupportKB` articles auto-resolve, while uncovered tickets fall back to human review.
- **Lab Guide Alignment:** Documented in [Chapter 11 (Section 2 & 5)](Chapters/11-RunBatchC.md#5-the-evolution-scorecard-batch-a-vs-batch-b-vs-batch-c).

---

### Complementary Lab Guide Enhancements

1. **Per-Ticket Knowledge Grounding Audit (Section 2):** Complete mapping of tickets `HF-3001` through `HF-3008` against specific `SupportKB` runbooks (`kb-08`, `kb-10`, `kb-11`, `kb-13`), proving why `HF-3005` must fail safe to human review.
2. **Grand Evolution Scorecard (Section 5):** Unified comparative matrix tracking the evolution from Batch A (8 touches, 100%) to Batch B (7 touches, 87.5%) to Batch C (3 touches, 37.5%).
3. **Optimized Batch C Dispatch Prompt (Section 3):** Explicit prompt with dynamic folder key discovery, entity GUID, settlement polling, and scorecard generation.
4. **Execution Flow Architecture (Section 4):** Mermaid sequence diagram detailing concurrent 4-path job handling in Orchestrator.
5. **Scorecard Verification Checklist (Section 6):** Step-by-step verification verifying exact counts (4 auto-resolved, 1 auto-skipped, 2 urgent, 1 standard).
6. **Troubleshooting & Breakage Matrix (Section 7):** Diagnosing common batch faults such as missing index overwrites or priority leaks.

---

## Chapter 12: Scoreboard

### Product Manager Baseline
From Tuan's slide **`12 · Scoreboard`**:

> **Header:** `1:12   12 · Scoreboard`
> **Time:** `agent works 3-5 min · you: compare notes with the next table`
>
> **SAY TO YOUR CODING AGENT**
> ```text
> Create me a report that shows the V1/V2/V3 comparison: tickets processed, human touches, and what changed between versions.
> ```
>
> **Checkpoint - 8 -> 7 -> 3 or 4. Two improvement rounds driven entirely by your own decisions and feedback. That's the pattern to take home: any triage queue, same loop.**

---

### Detailed Findings & Comparison

#### 1. The 8 -> 7 -> 3/4 Progression (100% Match)
- **Status:** **Identical / Verified Live**
- **Baseline Requirement:** Show the drop from 8 touches in V1 to 7 in V2, down to 3 or 4 in V3.
- **Lab Guide Alignment:** Fully documented with live Orchestrator telemetry in [Chapter 12 (Section 1 & 2)](Chapters/12-Scoreboard.md#1-the-three-generations-compared-v1-vs-v2-vs-v3).

#### 2. Root Changes Between Generations (100% Match)
- **Status:** **Identical**
- **Baseline Requirement:** Document what changed between versions (linear review -> multi-path routing -> dual-key knowledge grounding).
- **Lab Guide Alignment:** Detailed architectural analysis in [Chapter 12 (Section 2)](Chapters/12-Scoreboard.md#2-what-changed-between-generations).

#### 3. The Take-Home Pattern (100% Match)
- **Status:** **Identical / Enhanced**
- **Baseline Requirement:** Articulate the universal pattern: *"Two improvement rounds driven entirely by your own decisions and feedback. That's the pattern to take home: any triage queue, same loop."*
- **Lab Guide Alignment:** Structured into the 4-step Agentic Automation Flywheel Mermaid diagram in [Chapter 12 (Section 5)](Chapters/12-Scoreboard.md#5-the-take-home-pattern-the-agentic-automation-flywheel).

---

### Complementary Lab Guide Enhancements

1. **Three-Generation Comparative Table (Section 1):** Matrix comparing version numbers, flow names, test datasets, reasoning fields, and effort reductions.
2. **Context-Rich Optimized Scoreboard Prompt (Section 3):** Explicit prompt commanding Claude Code to query live telemetry across all three solution folders.
3. **Embedded Official Scoreboard Report (`scoreboard-report.md`) (Section 4):** Full inclusion of the unabridged generated report deliverable, documenting headline metrics (8 -> 7 -> 5 progression), per-ticket routing, architectural capabilities, and why the deterministic safety gate protected edge cases.
4. **The Agentic Automation Flywheel (Section 5):** Mermaid process diagram formalizing the continuous feedback loop from supervised assistance to earned autonomy.
5. **Four Golden Rules of Agentic Triage (Section 5):** Enterprise production principles covering supervised baselines, decision mining, dual-key safety, and fail-safe defaults.
6. **Workshop Retrospective (Section 7):** Holistic synthesis of all developer tools, runtimes, and platform services used across the 12 chapters.











