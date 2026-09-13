# UiPath Agentic Automation Workshop - Triage Lab

Welcome to the **UiPath Agentic Automation Workshop**. This repository contains the step-by-step guides and workspace setup for building, orchestrating, and testing AI agent-driven automations with the **UiPath CLI (`uip`)**, **Claude Code**, and **UiPath Agent Skills**.

---

## Table of Contents

- [Overview](#overview)
- [Chapters](#chapters)
  - [Chapter 0: Install the Tools](Chapters/0-InstallTheTools.md)
  - [Chapter 1: Connect to the Workshop Tenant](Chapters/1-Connect.md)
  - [Chapter 2: Preflight](Chapters/2-Preflight.md)
  - [Chapter 3: Build V1](Chapters/3-BuildV1.md)
  - [Chapter 4: Deploy](Chapters/4-Deploy.md)
  - [Chapter 5: Run Batch A](Chapters/5-RunBatchA.md)
  - [Chapter 6: Review by Hand & Trace Feedback](Chapters/6-ReviewByHand.md)
  - [Chapter 7: V2 - Mine Your Decisions](Chapters/7-MineDecisions.md)
  - [Chapter 8: Run Batch B](Chapters/8-RunBatchB.md)
  - [Chapter 9: Delegate the Review](Chapters/9-DelegateTheReview.md)
  - [Chapter 10: V3 - Earn Some Autonomy](Chapters/10-V3EarnAutonomy.md)
  - [Chapter 11: Run Batch C](Chapters/11-RunBatchC.md)
  - [Chapter 12: Scoreboard](Chapters/12-Scoreboard.md)
- [Review & Deviations Log](#review--deviations-log)
- [Quick Verification Checklist](#quick-verification-checklist)

---

## Overview

In this workshop, you pair with an AI coding agent (**Claude Code**) augmented with specialized **UiPath Agent Skills**. You will connect to the workshop staging tenant, explore and query shared Data Fabric entities and knowledge bases, and build automations using modern developer tooling.

---

## Chapters

### [Chapter 0: Install the Tools](Chapters/0-InstallTheTools.md)
End-to-end installation and verification of developer runtimes, package managers, CLIs, and agent skills. Each subsection follows a **test-first** approach so you can quickly verify existing software before installing.

- **1. System Environment & Core Development Tools**
  - [1.1 Prerequisites: PowerShell 7 (`pwsh`)](Chapters/0-InstallTheTools.md#11-prerequisites-powershell-7-pwsh)
  - [1.2 Node.js (20+)](Chapters/0-InstallTheTools.md#12-nodejs-20)
  - [1.3 Python 3](Chapters/0-InstallTheTools.md#13-python-3)
  - [1.4 Astral uv](Chapters/0-InstallTheTools.md#14-astral-uv)
  - [1.5 Refreshing the Environment PATH](Chapters/0-InstallTheTools.md#15-refreshing-the-environment-path)
- **2. UiPath Platform & AI Agent Setup**
  - [2.1 Claude Code & UiPath CLI (`claude` & `uip`)](Chapters/0-InstallTheTools.md#21-claude-code--uipath-cli-claude--uip)
  - [2.2 UiPath Agent Skills (Claude Code Plugin)](Chapters/0-InstallTheTools.md#22-uipath-agent-skills-claude-code-plugin)
  - [2.3 Project Setup & UiPath Python SDK](Chapters/0-InstallTheTools.md#23-project-setup--uipath-python-sdk)
  - [2.4 Authentication: UiPath Automation Cloud](Chapters/0-InstallTheTools.md#24-authentication-uipath-automation-cloud)
  - [2.5 Upgrading & Maintenance](Chapters/0-InstallTheTools.md#25-upgrading--maintenance)

---

### [Chapter 1: Connect to the Workshop Tenant](Chapters/1-Connect.md)
Create and enter your team workspace folder, then authenticate the UiPath CLI with the workshop staging tenant (`MVPSummit26`).

- **1. Create and Enter Workspace Directory**
  - [1.1 Team Folder Naming Convention](Chapters/1-Connect.md#11-team-folder-naming-convention) (`triage-lab-TEAM<firstname>-<lastname>`)
  - [1.2 Create and Navigate in PowerShell 7](Chapters/1-Connect.md#12-create-and-navigate-in-powershell-7) (`mkdir ... && cd ...`)
  - [1.3 Verify Current Directory](Chapters/1-Connect.md#13-verify-current-directory) (`pwd`)
- **2. Interactive Authentication**
  - [2.1 Workshop Environment Details](Chapters/1-Connect.md#21-workshop-environment-details) (Staging authority, organization, tenant)
  - [2.2 Log in via Browser](Chapters/1-Connect.md#22-log-in-via-browser) (`uip login --authority ...`)
  - [2.3 Verify Connection Status](Chapters/1-Connect.md#23-verify-connection-status) (`uip login status --output table`)
  - [2.4 View User Information](Chapters/1-Connect.md#24-view-user-information) (`uip user`)

---

### [Chapter 2: Preflight](Chapters/2-Preflight.md)
Pre-authorize UiPath tools, launch Claude Code in your workspace, configure optimal session settings, and run preflight health checks to verify shared workshop resources.

- **1. Pre-Authorize Tools & Launch Claude Code**
  - [1.1 Pre-Authorize UiPath Commands and Skills](Chapters/2-Preflight.md#11-pre-authorize-uipath-commands-and-skills) (`.claude/settings.local.json`)
  - [1.2 Launch Claude Code](Chapters/2-Preflight.md#12-launch-claude-code) (`claude`)
  - [1.3 Configure Session Settings](Chapters/2-Preflight.md#13-configure-session-settings-mode-model-effort) (Accept Edits mode, Opus model, High effort)
- **2. Verify CLI Session in Claude Code**
  - [2.1 Check Cloud Authentication Status](Chapters/2-Preflight.md#21-check-cloud-authentication-status) (Shell passthrough via `!`)
- **3. First Prompt: Verify Shared Workshop Resources**
  - [3.1 Send the Preflight Prompt](Chapters/2-Preflight.md#31-send-the-preflight-prompt) (Data Fabric tickets & SupportKB search)
  - [3.2 While the Agent Works](Chapters/2-Preflight.md#32-while-the-agent-works-2-3-min) (Open Studio Web)
  - [3.3 Checkpoint](Chapters/2-Preflight.md#33-checkpoint) (Verification criteria & slow-spot fallback)
- **4. Workspace Permissions & Session Controls**
  - [4.1 How Permissions Work in Claude Code](Chapters/2-Preflight.md#41-how-permissions-work-in-claude-code)
  - [4.2 Exiting Claude Code](Chapters/2-Preflight.md#42-exiting-claude-code)

---

### [Chapter 3: Build V1](Chapters/3-BuildV1.md)
Prompt Claude Code to scaffold, compose, validate, link, and upload the `TicketTriage` Maestro Flow with an autonomous agent grounded in `SupportKB` and Action Center human review.

- **1. Overview & Architecture**
  - [1.1 Flow Architecture](Chapters/3-BuildV1.md#11-flow-architecture) (Trigger -> Agent -> Action Center Task -> End)
  - [1.2 Key Anchors and Parameters](Chapters/3-BuildV1.md#12-key-anchors-and-parameters)
- **2. The Build Prompt**
  - [2.1 Discover Your User Identity](Chapters/3-BuildV1.md#21-discover-your-user-identity-uip-user-vs-uip-or-users-current) (`uip user` vs. `uip or users current`)
  - [2.2 Send the Build V1 Prompt](Chapters/3-BuildV1.md#22-send-the-build-v1-prompt) (Optimized Build V1 Prompt)
- **3. What the Agent Executes Behind the Scenes**
  - [3.1 Solution & Flow Initialization](Chapters/3-BuildV1.md#31-solution--flow-initialization)
  - [3.2 Node Composition & Wiring](Chapters/3-BuildV1.md#32-node-composition--wiring)
  - [3.3 Validation, Resource Linking & Upload](Chapters/3-BuildV1.md#33-validation-resource-linking--upload)
- **4. While the Agent Works**
  - [4.1 Deployment Preparation](Chapters/3-BuildV1.md#4-while-the-agent-works-4-6-min)
- **5. Checkpoint & Verification**
  - [5.1 Checkpoint Criteria](Chapters/3-BuildV1.md#51-checkpoint-criteria) (Designer URL, validate, Imported 1, assignee)
  - [5.2 Expected Agent Response Sample](Chapters/3-BuildV1.md#52-expected-agent-response-sample)
  - [5.3 Visual Inspection in Studio Web](Chapters/3-BuildV1.md#53-visual-inspection-in-studio-web)

---

### [Chapter 4: Deploy](Chapters/4-Deploy.md)
Deploy your V1 Maestro Flow solution from Studio Web to Orchestrator, provisioning your team folder under `Shared` and linking shared resources.

- **1. Why Deployment Happens in the Browser**
  - [1.1 Permission Architecture: Browser vs. Local IDE](Chapters/4-Deploy.md#1-why-deployment-happens-in-the-browser)
- **2. Step-by-Step Deployment Walkthrough**
  - [2.1 Open Flow Designer in Studio Web](Chapters/4-Deploy.md#21-step-1-open-the-flow-designer-in-studio-web)
  - [2.2 Open Deploy Wizard](Chapters/4-Deploy.md#22-step-2-open-the-deploy-wizard)
  - [2.3 Switch "Pack to" from Personal to Shared](Chapters/4-Deploy.md#23-step-3-switch-pack-to-from-personal-to-shared)
  - [2.4 Click Deploy and Monitor Log](Chapters/4-Deploy.md#24-step-4-click-deploy-and-monitor-the-log)
- **3. Checkpoint & Verification**
  - [3.1 Browser Checkpoint](Chapters/4-Deploy.md#31-browser-checkpoint)
  - [3.2 Verify Folder Provisioning via UiPath CLI](Chapters/4-Deploy.md#32-verify-folder-provisioning-via-uipath-cli) (`! uip or folders list`)
- **4. Troubleshooting & Breakage Guide**
  - [4.1 Deploy Button Greyed Out Fix](Chapters/4-Deploy.md#4-troubleshooting--breakage-guide)
  - [4.2 Version Already Exists Fix](Chapters/4-Deploy.md#4-troubleshooting--breakage-guide)
  - [4.3 Forbidden (403) in Local IDEs](Chapters/4-Deploy.md#deep-dive-understanding-the-forbidden-403-error-in-local-ides)

---

### [Chapter 5: Run Batch A](Chapters/5-RunBatchA.md)
Execute the first batch of 8 customer support tickets from Data Fabric (`TicketsV1`) through your deployed `TriageTicketV1` flow, monitoring task creation in Action Center.

- **1. Overview & Execution Architecture**
  - [1.1 Flow Execution Architecture](Chapters/5-RunBatchA.md#1-overview--execution-architecture) (`uip maestro flow process run`)
- **2. Parameter Discovery**
  - [2.1 Discover Deployed Process Keys](Chapters/5-RunBatchA.md#21-discover-deployed-process-keys) (`uip or processes list`)
  - [2.2 Query Tickets from Data Fabric](Chapters/5-RunBatchA.md#22-query-tickets-from-data-fabric-ticketsv1) (`TicketsV1`)
- **3. The Run Batch A Prompt**
  - [3.1 Send the Batch Prompt](Chapters/5-RunBatchA.md#3-the-run-batch-a-prompt) (Optimized Prompt with Settlement Polling Guardrail)
- **4. Behind-the-Scenes Execution & Settlement Polling**
  - [4.1 Job Dispatch Loop](Chapters/5-RunBatchA.md#41-job-dispatch-loop)
  - [4.2 Why Polling Job State Fails](Chapters/5-RunBatchA.md#42-the-crucial-signal-why-polling-job-state-fails) (Task count vs. job status)
- **5. Checkpoint & Verification**
  - [5.1 Verification Checklist](Chapters/5-RunBatchA.md#51-verification-checklist) (8 tasks under "My tasks")
  - [5.2 Verify via UiPath CLI](Chapters/5-RunBatchA.md#52-verify-via-uipath-cli) (`! uip tasks list`)
  - [5.3 Verify in Action Center Browser](Chapters/5-RunBatchA.md#53-verify-in-action-center-browser)
  - [5.4 Triage Decision Guide (Reviewing Batch A)](Chapters/5-RunBatchA.md#54-triage-decision-guide-reviewing-batch-a)
- **6. Troubleshooting Guide**
  - [6.1 Unattended Robot Permissions & Stale Tokens](Chapters/5-RunBatchA.md#6-troubleshooting--breakage-guide)
- **7. Completed Batch A in Action Center**
  - [7.1 Completed Tasks & Audit Trail Verification](Chapters/5-RunBatchA.md#7-completed-batch-a-in-action-center)

---

### [Chapter 6: Review by Hand & Trace Feedback](Chapters/6-ReviewByHand.md)
Review the agent's triage decisions from Batch A by hand in Action Center, observe what V1 gets wrong, and instruct Claude Code to leave LLM Observability Trace Feedback on three runs using `uip traces feedback create`.

- **1. Overview & Learning Objectives**
  - [1.1 V1 Capabilities & Limitations](Chapters/6-ReviewByHand.md#1-overview--learning-objectives) (Urgency gap, vendor noise, missing reviewer guidance)
- **2. The Manual Review Experience in Action Center**
  - [2.1 Action Center Outcomes](Chapters/6-ReviewByHand.md#2-the-manual-review-experience-in-action-center) (Approve, Modify & Send, Reject)
- **3. Teaching the Agent: LLM Observability Trace Feedback**
  - [3.1 What is Trace Feedback](Chapters/6-ReviewByHand.md#3-teaching-the-agent-llm-observability-trace-feedback) (`uip traces feedback create`)
- **4. The Chapter 6 Prompts**
  - [4.1 Send the Trace Feedback Prompt](Chapters/6-ReviewByHand.md#4-the-chapter-6-prompts) (Baseline vs. Optimized Prompt)
- **5. Behind-the-Scenes CLI Execution**
  - [5.1 Feedback Dispatch for HF-1006, HF-1008, HF-1007](Chapters/6-ReviewByHand.md#5-what-the-agent-executes-behind-the-scenes)
- **6. Checkpoint & Verification**
  - [6.1 Verify Feedback via UiPath CLI](Chapters/6-ReviewByHand.md#6-checkpoint--verification) (`! uip traces feedback list`)
- **7. Troubleshooting & Breakage Guide**
  - [7.1 Resolving Missing Folder Keys & Invalid Trace GUIDs](Chapters/6-ReviewByHand.md#7-troubleshooting--breakage-guide)

---

### [Chapter 7: V2 - Mine Your Decisions](Chapters/7-MineDecisions.md)
Instruct Claude Code to mine your manual review decisions and trace feedback from Batch A, identify V1 weaknesses, build `TriageTicketV2` with multi-path routing and reviewer guidance, and deploy from Studio Web.

- **1. Overview & The "Mining Decisions" Paradigm**
  - [1.1 Autonomous Architecture Evolution](Chapters/7-MineDecisions.md#1-overview--the-mining-decisions-paradigm) (Trace annotations informing workflow design)
- **2. Analysis of V1 Weaknesses**
  - [2.1 The Three Gaps](Chapters/7-MineDecisions.md#2-analysis-of-v1-weaknesses-the-three-gaps) (Urgency gap, auto-reply noise waste, missing reviewer guidance)
- **3. Architecture of TriageTicketV2**
  - [3.1 Multi-Path Routing Design](Chapters/7-MineDecisions.md#3-architecture-of-triageticketv2) (Noise bypass, urgent queue, standard review with recommended approach)
- **4. The Chapter 7 Prompts**
  - [4.1 Send the Build V2 Prompt](Chapters/7-MineDecisions.md#4-the-chapter-7-prompts) (Baseline vs. Optimized Prompt)
- **5. Behind the Scenes: Solution Upload**
  - [5.1 Why Upload Requires `--force`](Chapters/7-MineDecisions.md#5-behind-the-scenes-why-upload-requires---force) (Preventing remote solution overwrites)
- **6. Deployment: Pack & Upgrade in Studio Web**
  - [6.1 Step-by-Step Designer Deployment](Chapters/7-MineDecisions.md#6-deployment-pack--upgrade-in-studio-web) (Bumping version to 1.0.2 and release timing guardrail)
- **7. Checkpoint & Verification**
  - [7.1 Verify Deployed Process via UiPath CLI](Chapters/7-MineDecisions.md#7-checkpoint--verification) (`! uip or processes list`)
- **8. Troubleshooting & Breakage Guide**
  - [8.1 Common Pitfalls & Solutions](Chapters/7-MineDecisions.md#8-troubleshooting--breakage-guide) (Premature agent prompts, version collisions, unassigned tasks)

---

### [Chapter 8: Run Batch B](Chapters/8-RunBatchB.md)
Inspect the newly deployed V2 release's index bindings, patch ResourceOverwrites to Shared, dispatch all 8 tickets from TicketsV2, and verify the 7-touch scorecard.

- **1. The Context Grounding Index Gotcha**
  - [1.1 Preflight ResourceOverwrites](Chapters/8-RunBatchB.md#1-the-context-grounding-index-gotcha-resourceoverwrites) (Avoiding the 4.5-minute timeout fault)
- **2. Batch B Data Analysis**
  - [2.1 The TicketsV2 Entity](Chapters/8-RunBatchB.md#2-batch-b-data-analysis-ticketsv2) (2 urgent tickets, 5 standard tickets, 1 auto-skipped newsletter)
- **3. The Chapter 8 Prompts**
  - [3.1 Send the Batch B Prompt](Chapters/8-RunBatchB.md#3-the-chapter-8-prompts) (Baseline vs. Optimized Prompt)
- **4. Execution & Settlement Monitoring**
  - [4.1 Settle All Runs](Chapters/8-RunBatchB.md#4-execution--settlement-monitoring) (Monitoring jobs and Action Center tasks)
- **5. The Scorecard: Batch A vs. Batch B**
  - [5.1 Comparing Touchpoints](Chapters/8-RunBatchB.md#5-the-scorecard-comparing-batch-a-vs-batch-b) (Quantitative reduction to 7 touches)
- **6. Checkpoint & Verification**
  - [6.1 Action Center UI Inspection](Chapters/8-RunBatchB.md#6-checkpoint--verification) (Verifying High-priority escalation tasks)
- **7. Troubleshooting & Breakage Guide**
  - [7.1 Common Issues & Fixes](Chapters/8-RunBatchB.md#7-troubleshooting--breakage-guide) (Missing index faults, priority mismatch)

---

### [Chapter 9: Delegate the Review](Chapters/9-DelegateTheReview.md)
Delegate Action Center human-in-the-loop reviews directly to your AI coding agent, checking its judgment against quality rubrics and settling all flow instances to zero open tasks.

- **1. The Human-in-the-Loop Paradigm Shift**
  - [1.1 From Manual Bottleneck to Autonomous Reviewer](Chapters/9-DelegateTheReview.md#1-the-human-in-the-loop-paradigm-shift)
- **2. What Good Judgment Looks Like: The Review Rubric**
  - [2.1 Evaluating Drafts & Identifying Flaws](Chapters/9-DelegateTheReview.md#2-what-good-judgment-looks-like-the-review-rubric) (Policy regurgitation, KB gap disclosures)
- **3. Why Task Assignment Is Not Needed**
  - [3.1 Action Center Assignment Architecture](Chapters/9-DelegateTheReview.md#3-behind-the-scenes-why-task-assignment-is-not-needed)
- **4. The Chapter 9 Prompts**
  - [4.1 Baseline vs. Optimized Prompt](Chapters/9-DelegateTheReview.md#4-the-chapter-9-prompts)
- **5. Execution Sequence & Flow Resumption**
  - [5.1 Settle All Runs & Resume Maestro Flow](Chapters/9-DelegateTheReview.md#5-execution-sequence--flow-resumption)
- **6. Checkpoint & Verification**
  - [6.1 Action Center UI Inspection](Chapters/9-DelegateTheReview.md#6-checkpoint--verification) (0 pending tasks, 15 completed)
- **7. Troubleshooting & Breakage Guide**
  - [7.1 Common Issues & Fixes](Chapters/9-DelegateTheReview.md#7-troubleshooting--breakage-guide)
- **8. Summary: The Complete Agentic Lifecycle**
  - [8.1 End-to-End Architectural Synthesis](Chapters/9-DelegateTheReview.md#8-summary-the-complete-agentic-lifecycle)

---

### [Chapter 10: V3 - Earn Some Autonomy](Chapters/10-V3EarnAutonomy.md)
Architect TriageTicketV3 with a knowledge grounding safety gate (kbCovered flag and kbSources citations), introduce a safe auto-resolution path, and deploy the upgraded package in Studio Web.

- **1. The Enterprise Autonomy Dilemma**
  - [1.1 Why Confidence Scores Are Not Enough](Chapters/10-V3EarnAutonomy.md#1-the-enterprise-autonomy-dilemma)
- **2. Architecture of TriageTicketV3**
  - [2.1 The Four Operational Paths & Schema Evolution](Chapters/10-V3EarnAutonomy.md#2-architecture-of-triageticketv3)
- **3. The Chapter 10 Prompts**
  - [3.1 Baseline vs. Optimized Prompt](Chapters/10-V3EarnAutonomy.md#3-the-chapter-10-prompts)
- **4. Behind the Scenes: Deploying V3 in Studio Web**
  - [4.1 Pack & Upgrade to Version 1.0.3](Chapters/10-V3EarnAutonomy.md#4-behind-the-scenes-deploying-v3-in-studio-web)
- **5. Checkpoint & Verification**
  - [5.1 CLI Process Release Inspection](Chapters/10-V3EarnAutonomy.md#5-checkpoint--verification)
- **6. Troubleshooting & Breakage Guide**
  - [6.1 Common Issues & Fixes](Chapters/10-V3EarnAutonomy.md#6-troubleshooting--breakage-guide)

### [Chapter 11: Run Batch C](Chapters/11-RunBatchC.md)
Verify SupportKB index bindings in Folder 8, dispatch all 8 tickets from TicketsV3 through TriageTicketV3, and benchmark the grand scorecard proving a 62.5% reduction in human touches.

- **1. The Context Grounding Preflight in Folder 8**
  - [1.1 Preflight ResourceOverwrites](Chapters/11-RunBatchC.md#1-the-context-grounding-preflight-in-folder-8) (Verifying Shared folder grounding)
- **2. Batch C Data Analysis**
  - [2.1 The TicketsV3 Entity](Chapters/11-RunBatchC.md#2-batch-c-data-analysis-ticketsv3) (4 auto-resolvable tickets, 1 fail-safe, 2 urgent, 1 auto-skip)
- **3. The Chapter 11 Prompts**
  - [3.1 Send the Batch C Prompt](Chapters/11-RunBatchC.md#3-the-chapter-11-prompts) (Baseline vs. Optimized Prompt)
- **4. Execution & Settlement Architecture**
  - [4.1 Multi-Path Settlement](Chapters/11-RunBatchC.md#4-execution--settlement-architecture) (Tracking concurrent 4-path execution)
- **5. The Evolution Scorecard: Batch A vs. Batch B vs. Batch C**
  - [5.1 Quantitative Touchpoint Comparison](Chapters/11-RunBatchC.md#5-the-evolution-scorecard-batch-a-vs-batch-b-vs-batch-c) (Tracking the drop from 8 to 7 to 3 touches)
- **6. Checkpoint & Verification**
  - [6.1 Scorecard Verification](Chapters/11-RunBatchC.md#6-checkpoint--verification) (Confirming 3 pending tasks in Action Center)
- **7. Troubleshooting & Breakage Guide**
  - [7.1 Common Issues & Fixes](Chapters/11-RunBatchC.md#7-troubleshooting--breakage-guide)

### [Chapter 12: Scoreboard](Chapters/12-Scoreboard.md)
Synthesize the end-to-end telemetry into an executive comparative scoreboard across V1, V2, and V3, benchmark the drop in human touches (8 -> 7 -> 3/4), and formalize the universal 4-step Agentic Automation Flywheel.

- **1. The Three Generations Compared**
  - [1.1 Comprehensive Evolution Matrix](Chapters/12-Scoreboard.md#1-the-three-generations-compared-v1-vs-v2-vs-v3) (Comparing versions, datasets, and reasoning fields)
- **2. What Changed Between Generations**
  - [2.1 Architectural Shifts](Chapters/12-Scoreboard.md#2-what-changed-between-generations) (Linear baseline -> Multi-path triage -> Dual-key earned autonomy)
- **3. The Chapter 12 Prompts**
  - [3.1 Baseline vs. Optimized Prompt](Chapters/12-Scoreboard.md#3-the-chapter-12-prompts)
- **4. The Official Scoreboard Report (`scoreboard-report.md`)**
  - [4.1 Executive Telemetry & Analysis](Chapters/12-Scoreboard.md#4-the-official-scoreboard-report-scoreboard-reportmd) (Full embedded report deliverable: 8 -> 7 -> 5 progression, per-ticket routing, capabilities matrix, and SupportKB knowledge backlog)
- **5. The Take-Home Pattern**
  - [5.1 The Agentic Automation Flywheel](Chapters/12-Scoreboard.md#5-the-take-home-pattern-the-agentic-automation-flywheel) (The repeatable 4-step production loop)
- **6. Checkpoint & Verification**
  - [6.1 Checkpoint Criteria](Chapters/12-Scoreboard.md#6-checkpoint--verification) (8 -> 7 -> 5 progression verification)
- **7. Workshop Retrospective**
  - [7.1 Full Platform & Tooling Synthesis](Chapters/12-Scoreboard.md#7-workshop-retrospective--summary)

---



## Review & Master Runbook

For a line-by-line audit comparing the workshop materials against Product Manager requirements and guidelines, see:

- [**Tuan-Review.md**](Tuan-Review.md) - Chapter-by-chapter deviations, gap analysis, and applied fixes.
- [**fusion-triage-lab-runbook-2026-09-09.md**](fusion-triage-lab-runbook-2026-09-09.md) - Product Manager Tuan's original course runbook rendered in native GitHub Markdown ([raw HTML version](fusion-triage-lab-runbook-2026-09-09.html)).

---

## Quick Verification Checklist

Before starting the exercises, verify that your machine satisfies the core prerequisites:

```powershell
# 1. Shell & Runtimes
pwsh --version              # PowerShell 7.x
node --version              # v20.x or higher
python --version            # Python 3.10+
uv --version                # uv 0.x

# 2. CLIs & Agent
claude --version            # Claude Code 2.x
uip --version               # UiPath CLI 1.201.0+

# 3. Claude Skills Plugin
claude plugin list          # uipath@uipath-marketplace enabled

# 4. UiPath Cloud Connection
uip login status --output table
```
