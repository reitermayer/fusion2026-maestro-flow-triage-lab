# Chapter 0: Install the Tools

> [!NOTE]
> **The Big Picture: Arming the Agent**  
> Before an AI coding agent can build enterprise automations, it needs the right tools in its hands. In this chapter, you equip Claude Code with the UiPath CLI and specialized Agent Skills, transforming a general reasoning model into a capable UiPath automation engineer that knows how to scaffold flows, validate schemas, and link cloud resources.

Welcome to the UiPath workshop setup guide. This chapter covers the end-to-end installation, configuration, and verification of all required development runtimes, package managers, the **UiPath CLI**, and **AI Agent Skills**.

| Program / Tool | Description |
| :--- | :--- |
| **PowerShell 7** | Cross-platform shell tested and used throughout this workshop |
| **Node.js** | JavaScript/TypeScript runtime required by CLI tools and SDKs |
| **Python 3** | Runtime required for UiPath coded automations, AI agents, and scripts |
| **uv** | Fast Python package and environment manager from Astral |
| **UiPath CLI (`uip`)** | Official command-line tool for building, packing, and managing UiPath projects |
| **UiPath Agent Skills** | Instruction packages teaching AI coding agents how to build UiPath automations with `uip` |
| **UiPath Python SDK** | Python library (`uipath`) for building coded automations and AI agents |

---

## 1. System Environment & Core Development Tools

### 1.1 Prerequisites: PowerShell 7 (`pwsh`)

The instructions and commands in this workshop have been tested using PowerShell 7.

#### Test if PowerShell 7 is Installed
Run this command from any terminal:

```powershell
pwsh --version
```

*Expected output:*
```text
PowerShell 7.x.x
```

If PowerShell 7 is installed, it prints its version (e.g. `PowerShell 7.x.x`). If you see an error that `pwsh` is not recognized, proceed to the installation step below.

#### Install PowerShell 7 via WinGet
If PowerShell 7 is not yet installed:

```powershell
winget install --id Microsoft.PowerShell -e --accept-source-agreements --accept-package-agreements
```

> [!NOTE]
> After installation completes, launch **PowerShell 7** (`pwsh`) from Windows Terminal or the Start menu before running subsequent commands.

---

### 1.2 Node.js

The Node.js JavaScript runtime is required by the UiPath CLI and agent tooling. Node.js 18 or later is required.

#### Test if Node.js is Installed
Run this command in PowerShell 7:

```powershell
node --version
```

*Expected output:*
```text
v20.x.x  # or higher (Node.js 18+ required)
```

If Node.js is installed and prints a compatible version, you can proceed to the next tool. If you see an error that `node` is not recognized, install it using the step below.

#### Install Node.js via WinGet
If Node.js is not yet installed:

```powershell
winget install --id OpenJS.NodeJS -e --accept-source-agreements --accept-package-agreements
```

---

### 1.3 Python 3

Python 3 is required for UiPath coded automations, AI agents, and scripts.

#### Test if Python 3 is Installed
Run this command in PowerShell 7:

```powershell
python --version
```

*Expected output:*
```text
Python 3.14.x  # or Python 3.10+
```

> [!NOTE]
> On Windows, standard CPython uses `python.exe` or `py.exe`. If `python` is not recognized, try `py -3 --version`.

If Python 3 is installed and prints its version, you can proceed to the next tool. If you see an error that `python` is not recognized, install it using the step below.

#### Install Python 3 via WinGet
If Python 3 is not yet installed:

```powershell
winget install --id Python.Python.3.14 -e --accept-source-agreements --accept-package-agreements
```

---

### 1.4 Astral uv

`uv` is a fast Python package and environment manager from Astral used to manage virtual environments and project dependencies.

#### Test if uv is Installed
Run this command in PowerShell 7:

```powershell
uv --version
```

*Expected output:*
```text
uv 0.x.x
```

If `uv` is installed and prints its version, you can proceed to the next step. If you see an error that `uv` is not recognized, install it using the step below.

#### Install Astral uv via WinGet
If `uv` is not yet installed:

```powershell
winget install --id astral-sh.uv -e --accept-source-agreements --accept-package-agreements
```

---

### 1.5 Refreshing the Environment PATH

When WinGet installs software, it updates the system and user `PATH` environment variables in the Windows Registry.

If you installed any new tools above, refresh the `PATH` in your current PowerShell 7 session without restarting the terminal:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

*(Alternatively, close and reopen your PowerShell 7 window).*

---

## 2. UiPath Platform & AI Agent Setup

### 2.1 UiPath CLI (`uip`)

The UiPath CLI is distributed globally on npm as `@uipath/cli`. It requires Node.js 18 or later.

*Official Reference:* [Installing UiPath CLI](https://docs.uipath.com/uipath-cli/standalone/latest/user-guide/installing-uipath-cli)

#### Test if UiPath CLI is Installed
Run this command in PowerShell 7:

```powershell
uip --version
```

*Expected output:*
```text
1.201.0
```

If the CLI is installed and prints its version, proceed to skills configuration. If you see an error that `uip` is not recognized, install it using the step below.

#### Install the UiPath CLI via npm
If the UiPath CLI is not yet installed, install it globally using `npm` in PowerShell 7:

```powershell
npm install -g @uipath/cli
```

> [!NOTE]
> **CLI Tools Install on First Use:**
> The base `uip` CLI ships as a lightweight host with only core commands preinstalled. When you run a command for a specific tool family for the first time - such as an Orchestrator command (`uip or ...`) - the CLI automatically downloads and installs the required tool package (e.g. `@uipath/orchestrator-tool`) from npm:
> ```text
> Installing @uipath/orchestrator-tool...
> ✓ Installed @uipath/orchestrator-tool
> ```
> Subsequent calls use the installed tool directly. You can inspect all installed tools anytime by running `uip tools list`.

---

### 2.2 UiPath Agent Skills

Skills are instruction packages that teach AI coding agents how to build UiPath automations using `uip`. While **tools** (`uip tools`) extend the CLI with new commands, **skills** (`uip skills`) extend your AI coding agent with UiPath domain knowledge and decision rules.

*Official References:*
- [Choosing Your Agent](https://docs.uipath.com/coding-agents/standalone/latest/user-guide/choosing-your-agent)
- [Skills Concepts & Installation](https://docs.uipath.com/uipath-cli/standalone/latest/user-guide/concepts-skills)

#### Test if Skills are Installed
List the installed skills to confirm registration with your agent:

```powershell
uip skills list
```

If your agent skills are already installed and listed (e.g. `uipath-platform`, `uipath-rpa`, etc.), proceed to project setup. If no skills are listed or you need to configure your agent, install them below.

#### Install Skills for your AI Coding Agent

##### Supported Agents
The CLI supports the following coding agents:

| Agent | Flag Value | Install Scope |
| :--- | :--- | :--- |
| **Claude Code** | `claude` | Global (managed by Claude plugin system) |
| **Cursor** | `cursor` | Global or Local (`--local`) |
| **GitHub Copilot** | `copilot` | Global or Local (`--local`) |
| **Google Antigravity** | `antigravity` | Global or Local (`--local`) |
| **Codex** | `codex` | Global or Local (`--local`) |
| **Gemini CLI** | `gemini` | Global or Local (`--local`) |
| **OpenCode** | `opencode` | Global or Local (`--local`) |
| **UiPath Autopilot** | `autopilot` | Global or Local (`--local`) |

##### Installation Command
To install skills for your specific agent, pass the `--agent` flag:

```powershell
# Install skills for Claude Code:
uip skills install --agent claude
```

> [!TIP]
> - **Auto-detection:** If you omit `--agent`, `uip skills install` interactively prompts you to choose among all detected coding agents on your machine.
> - **Global vs. Local (`--local`):** Most agents support installing skills locally into the current project repository (`--local`). However, Claude Code is global-only as its plugin system is user-scoped.

---

### 2.3 Project Setup & UiPath Python SDK

#### Test if UiPath Python SDK is Installed
Test importing the SDK in your project's virtual environment:

```powershell
uv run python -c "import uipath; print('UiPath SDK: OK')"
```

*Expected output:*
```text
UiPath SDK: OK
```

If the test succeeds, your local project environment and SDK are already configured. If the command fails (e.g. `No such file or directory`, `No module named 'uipath'`, or `uv` cannot find a project), initialize the project and add the SDK using the steps below.

#### Initialize Project & Add UiPath Python SDK
Before adding dependencies, initialize a local Python project in your workspace directory using `uv`. Creating a local project isolates dependencies inside a project virtual environment (`.venv`) and prevents modules from being installed into your global Python installation:

```powershell
# 1. Initialize a new Python project (creates pyproject.toml and an isolated virtual environment):
uv init

# 2. Add the UiPath Python SDK:
uv add uipath
```

> [!NOTE]
> **Environment Isolation & CLI Integration:**
> - **Protects Global Python:** Initializing a local project with `uv` isolates all packages in `.venv`, preventing conflicts and avoiding unintended changes to your system-wide Python environment.
> - **Why do we need `uv add uipath`?** Certain UiPath CLI tools - most notably **Context Grounding** (`uip context-grounding`) - are lightweight Node.js wrappers built with a Python bridge (`uipath-python-bridge`). When you run `uip context-grounding ...`, the CLI delegates the command directly to the `uipath` executable inside your local virtual environment (`.venv/Scripts/uipath.exe`).

---

### 2.4 Authentication: UiPath Automation Cloud

#### Test Connection & Login Status
Confirm your active login session and selected tenant:

```powershell
uip login status --output table
```

*Expected output (if already logged in):*
```text
Status           | Logged in
Identity         | user@example.com
Organization     | your-org-name
Tenant           | your-tenant-name
```

If you are already logged in to the desired organization and tenant, you are ready to proceed. If you are not logged in, proceed to authenticate below.

#### Log in to UiPath Automation Cloud
Authenticate your CLI session against your UiPath Cloud organization:

```powershell
uip login
```

This opens a browser window where you can sign in and select your Organization and Tenant.

---

### 2.5 Upgrading & Maintenance

*Official Reference:* [Upgrading UiPath CLI](https://docs.uipath.com/uipath-cli/standalone/latest/user-guide/installing-uipath-cli#upgrading)

#### Update the CLI Host
To upgrade the CLI to the latest release:
```powershell
npm install -g @uipath/cli@latest
```

#### Update Installed CLI Tools
Upgrading the CLI host does not automatically update individual tools. Update all installed tools with:
```powershell
uip tools update
```

#### Update Agent Skills
Re-fetch and update the skills catalog for your coding agent:
```powershell
uip skills update --agent claude
```
*(Or omit `--agent` to update skills across all configured agents).*
