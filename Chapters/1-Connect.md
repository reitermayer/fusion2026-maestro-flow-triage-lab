# Chapter 1: Connect to the Workshop Tenant

> [!NOTE]
> **The Big Picture: Building the Bridge**  
> AI agents cannot work in a vacuum; they need live cloud access to inspect enterprise assets, query databases, and deploy solutions. Here, you establish the authenticated bridge between your local terminal and UiPath Automation Cloud (`MVPSummit26`), isolating your work inside your team workspace folder.

---

## 1. Create and Enter Workspace Directory

### 1.1 Team Folder Naming Convention

Each participant or team in the workshop works inside their own dedicated directory. The naming standard is:

```text
triage-lab-TEAM<firstname>-<lastname>
```

For example, if your name is Johannes Reitermayer, your directory is:
`triage-lab-TEAMjohannes-reitermayer`.

### 1.2 Create and Navigate in PowerShell 7

Use modern PowerShell 7 chaining (`&&`) to create the folder and immediately switch into it in a single command:

```powershell
mkdir triage-lab-TEAM<firstname>-<lastname> && cd triage-lab-TEAM<firstname>-<lastname>
```

> [!TIP]
> **PowerShell 7 Pipeline Chaining (`&&`):**
> The `&&` operator ensures that `cd` only executes if `mkdir` successfully creates the directory. Be sure to replace `<firstname>` and `<lastname>` with your actual first and last name.

### 1.3 Verify Current Directory

Confirm that your terminal is operating inside your new workspace folder:

```powershell
pwd
```

*Expected output:*
```text
Path
----
C:\Users\<user>\triage-lab-TEAM<firstname>-<lastname>
```

---

## 2. Interactive Authentication

### 2.1 Workshop Environment Details

For this workshop, connect to the designated staging instance:

| Parameter | Value | Notes |
| :--- | :--- | :--- |
| **Portal URL** | `https://staging.uipath.com/uipathlabsworkshop/MVPSummit26` | Web browser interface |
| **Authority** | `https://staging.uipath.com` | Custom staging authority URL |
| **Organization** | `uipathlabsworkshop` | Workshop organization |
| **Tenant** | `MVPSummit26` | Workshop tenant |

### 2.2 Log in via Browser

To log in directly to the workshop environment, run `uip login` with the `--authority`, `--organization`, and `--tenant` flags:

```powershell
uip login --authority https://staging.uipath.com --organization uipathlabsworkshop --tenant MVPSummit26
```

This launches your default browser pointing to the staging authority and authenticates your CLI directly against the `uipathlabsworkshop` organization and `MVPSummit26` tenant.

---

### 2.3 Verify Connection Status

Confirm that your session is active and review your connection details:

```powershell
uip login status --output table
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

---

### 2.4 View User Information

Inspect the authenticated user details:

```powershell
uip user
```

*Expected output:*
```text
UserId     <your-user-id>
Name       <your-name>
Username   <your-email>
Email      <your-email>
```
