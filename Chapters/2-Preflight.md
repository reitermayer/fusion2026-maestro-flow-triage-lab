# Chapter 2: Preflight

> [!NOTE]
> **The Big Picture: Trust, but Verify**  
> Never let an AI agent build on an unverified foundation. Before generating workflows that depend on shared enterprise infrastructure, you instruct your agent to inspect the tenant, confirm the 24 support tickets in Data Fabric, and test the `SupportKB` knowledge index. If shared resources are missing, you catch it in minute 2, not minute 30.

Before beginning the hands-on lab exercises, this chapter guides you through launching **Claude Code**, configuring session settings, and performing preflight health checks to verify that your environment, cloud connection, and **UiPath Agent Skills** are fully operational.

| Step | Action | Command / Task |
| :--- | :--- | :--- |
| **1. Pre-Authorize Tools** | Allow all `uip` commands and UiPath skills | PowerShell one-liner (`.claude/settings.local.json`) |
| **2. Launch Agent** | Start the interactive Claude Code CLI | `claude` |
| **3. Session Setup** | Configure mode, model, and effort | `Shift + Tab`, `/model`, `/effort high` |
| **4. CLI Status** | Run quick shell diagnostics from Claude | `! uip login status` |
| **5. Agent Preflight** | First prompt to verify shared tenant resources | Query Data Fabric tickets & SupportKB index |

---

## 1. Pre-Authorize Tools & Launch Claude Code

### 1.1 Pre-Authorize UiPath Commands and Skills

By default, Claude Code pauses and prompts for permission whenever a tool, terminal command, or external file read executes. To allow Claude Code to run all `uip` CLI subcommands, invoke UiPath agent skills, and read local skill documentation without prompt interruptions, run this one-liner in your terminal inside your team folder:

```powershell
New-Item -ItemType Directory -Force .claude | Out-Null; @{ permissions = @{ allow = @("PowerShell(uip *)", "Bash(uip *)", "Skill(uipath:*)", "Read(~/.uipath/**)", "Read(//**/.uipath/**)") } } | ConvertTo-Json -Depth 5 | Set-Content .claude/settings.local.json
```

> [!TIP]
> **What this does:**
> This creates `.claude/settings.local.json` in your workspace directory with wildcard allow rules:
> - `PowerShell(uip *)` and `Bash(uip *)`: Authorizes all UiPath CLI commands on Windows and macOS/Linux.
> - `Skill(uipath:*)`: Authorizes all UiPath agent skills.
> - `Read(~/.uipath/**)` and `Read(//**/.uipath/**)`: Authorizes reading local skill documentation and reference guides in `~/.uipath/.skills/` without triggering non-workspace file access prompts.

#### Verify Pre-Authorization Settings

##### Method 1: Inspect the Settings File (Terminal)
Verify that `.claude/settings.local.json` was generated properly:

```powershell
Get-Content .claude/settings.local.json
```

*Expected output:*
```json
{
  "permissions": {
    "allow": [
      "PowerShell(uip *)",
      "Bash(uip *)",
      "Skill(uipath:*)",
      "Read(~/.uipath/**)",
      "Read(//**/.uipath/**)"
    ]
  }
}
```

##### Method 2: Check Active Permissions Inside Claude Code
Once Claude Code is launched (Section 1.2):
- Type `/permissions` to view all active allow rules and confirm `uip *` and `Skill(uipath:*)` are enabled.
- Type `/config` to confirm that `local: .claude/settings.local.json` is loaded as an active settings source.

### 1.2 Launch Claude Code

Ensure your terminal is operating inside your team workspace directory (`triage-lab-TEAM<firstname>-<lastname>`), then start your AI coding agent:

```powershell
claude
```

When Claude Code launches in your project directory:
- It sets the current folder as its working context.
- It loads your pre-authorized tool permissions from `.claude/settings.local.json`.
- It detects the UiPath Agent Skills registered earlier with `claude plugin marketplace add ...`.

### 1.3 Configure Session Settings (Mode, Model, Effort)

Before sending prompts, configure your Claude Code session settings to optimize speed, autonomy, and reasoning depth for the workshop:

#### 1. Mode: Accept Edits (ON)
- **Shortcut:** Press **`Shift + Tab`** in your prompt to cycle permission modes until **Accept Edits** is active.
- **Why:** In default mode, Claude asks for confirmation before every file modification. In "Accept Edits" mode, Claude autonomously applies file edits and creates files, preventing prompt fatigue.

#### 2. Model: Opus
- **Command:** Type `/model` and press **Enter**, then select **Opus** from the menu.
- **Why:** Opus provides the highest reasoning capability, making it well-suited for architectural decisions and complex automation workflows.

#### 3. Effort: High
- **Command:** Type `/effort high` and press **Enter** (or pick **High** in the `/effort` menu).
- **Why:** High effort allocates an extended thinking budget, allowing the agent to plan multi-step tasks thoroughly and verify changes before responding.

---

## 2. Verify CLI Session in Claude Code

Once inside the interactive Claude Code prompt (`>`), you can run shell commands directly without sending them as LLM prompts by prefixing them with an exclamation mark (`!`).

### 2.1 Check Cloud Authentication Status

Verify your UiPath Cloud authentication status directly from within Claude Code:

```text
! uip login status
```

*Expected output:*
```text
Status           | Logged in
Identity         | <your-email>
IdentityType     | User
AuthFlow         | Interactive
CredentialSource | SavedLogin
BaseUrl          | https://staging.uipath.com
Organization     | uipathlabsworkshop
Tenant           | MVPSummit26
```

> [!NOTE]
> **Shell Passthrough with `!`:**
> In Claude Code, the `!` prefix executes the command in your underlying shell and prints the output directly into the Claude session. This confirms that your active UiPath Cloud login session is available to tools and skills during your workshop tasks.

---

## 3. First Prompt: Verify Shared Workshop Resources

Your first words to the coding agent - make it prove the shared workshop resources are reachable before you build anything on them.

### 3.1 Send the Preflight Prompt

Paste the following verification prompt directly into your Claude Code session:

```text
Verify my UiPath setup on this tenant: confirm the login is uipathlabsworkshop/MVPSummit26, that the shared Data Fabric entities TicketsV1, TicketsV2, and TicketsV3 exist and each holds 8 tickets (query the records, don't just list entities), and that the SupportKB knowledge index in the Shared folder exists and answers a test search. Report what you find; don't create or change anything.
```

### 3.2 While the Agent Works (2-3 min)

While the agent executes the queries:
- **Open a second browser tab** at [staging.uipath.com/uipathlabsworkshop/MVPSummit26](https://staging.uipath.com/uipathlabsworkshop/MVPSummit26).
- **Navigate to Data Fabric or Studio Web:** The portal URL opens Orchestrator by default. Click the **Product Launcher** (the 9 dots icon in the upper-left header) > **More** > **Data Fabric** (or **Studio Web**).

---

### 3.3 Checkpoint

> [!IMPORTANT]
> **Checkpoint - Resource Verification Criteria:**
> - Active login confirmed on `uipathlabsworkshop/MVPSummit26`.
> - Three Data Fabric entities (`TicketsV1`, `TicketsV2`, `TicketsV3`) exist and each holds 8 tickets.
> - The shared `SupportKB` index in the `Shared` folder exists and returns a HomeFix help article for a test query.
>
> Anything missing is a room problem, not yours - raise a hand. If it cannot be fixed in 3 minutes, a TA will move you to the backstop tenant.

#### Integrated Preflight Prompt Result
When Claude Code finishes executing the prompt from Section 3.1, you should see a report similar to:

```text
I have verified your UiPath setup on this tenant:

1. Active Login:
   - Organization: uipathlabsworkshop
   - Tenant: MVPSummit26
   - Status: Logged in

2. Shared Data Fabric Entities (Record Queries):
   - TicketsV1: Confirmed, 8 records (e.g. HF-1001 "Locked out of my account", HF-1002)
   - TicketsV2: Confirmed, 8 records
   - TicketsV3: Confirmed, 8 records

3. Context Grounding Index (Shared folder):
   - Index: SupportKB exists and ingestion status is Successful (backed by SupportKBDocs bucket)
   - Test Search: Returned "HomeFix Supply IT Helpdesk - Password Reset" (kb-01-password-reset.txt)

All shared workshop resources are active, reachable, and ready. Nothing was created or changed.
```

> [!NOTE]
> **Known Slow Spot:**
> The agent's knowledge-index search tool may report a 401 and spend a minute working around a stale token file. That is normal; it recovers on its own.
>
> If it is still stuck after 3 minutes, tell it:
> `"skip the index search, just confirm the index exists"`

---

## 4. Workspace Permissions & Session Controls

### 4.1 How Permissions Work in Claude Code

Because you configured `.claude/settings.local.json` in Section 1.1, Claude Code automatically executes all `uip` commands, invokes UiPath skills, and reads skill documentation from `~/.uipath/.skills/` without interrupting your workflow.

If Claude Code ever requests permission for an unlisted tool or a path outside the allowed patterns:
- Select **Always allow** (or allow for the session) to grant access for this project.
- Claude Code appends the approved rule directly to `.claude/settings.local.json`.

### 4.2 Exiting Claude Code

To exit the interactive Claude session and return to your PowerShell prompt at any time:
- Type `/exit` or `/quit` and press **Enter**.
- Or press `Ctrl+C`.
