Windows privilege escalation starts with **enumeration**: collecting information about the system, user, privileges, services, applications, files, and configuration to identify possible escalation paths.

Basic workflow:
```text
Current User
    ↓
Groups & Privileges
    ↓
OS / Architecture
    ↓
Installed Software
    ↓
Services
    ↓
Scheduled Tasks
    ↓
Files & Permissions
    ↓
Credentials / Secrets
    ↓
Potential Privilege Escalation
```

---

## 1. Identify Current User

### `whoami`

```cmd
whoami
```

Shows the current username.
```cmd
whoami /user
```

Shows the user's **SID (Security Identifier)**.
```cmd
whoami /groups
```

Shows groups associated with the current security token.
```cmd
whoami /priv
```

Shows assigned privileges such as:
```text
SeImpersonatePrivilege
SeBackupPrivilege
SeRestorePrivilege
SeTakeOwnershipPrivilege
```

These can provide direct privilege-escalation opportunities.

---

## 2. System Information

### `systeminfo`

```cmd
systeminfo
```

Displays information such as:
- Windows version
- Build number
- Architecture
- Hostname
- Installed updates/hotfixes
- System boot time
- Domain/workgroup
- Memory information

Useful for determining whether the system may be vulnerable to a known Windows exploit.

### Architecture
```cmd
echo %PROCESSOR_ARCHITECTURE%
```

Typical results:
```text
AMD64
```
or:
```text
x86
```

This matters when selecting an executable or exploit.

---

## 3. Hostname

```cmd
hostname
```
Displays the computer name.

---

## 4. Current Environment

```cmd
set
```

Displays environment variables.

Useful variables include:
```cmd
echo %USERNAME%
echo %USERDOMAIN%
echo %USERPROFILE%
echo %TEMP%
echo %PATH%
```

The `PATH` variable is particularly important when investigating **Path Hijacking**.

---

## 5. Network Information

### `ipconfig`

```cmd
ipconfig
```

Basic network configuration.
```cmd
ipconfig /all
```

More detailed information:
- IP address
- DNS servers
- Default gateway
- Network adapters
- DHCP
- MAC address

### Connections
```cmd
netstat -ano
```

Shows:
- Listening ports
- Established connections
- Local/remote addresses
- PID associated with each connection
    
Example:
```text
TCP    0.0.0.0:135     0.0.0.0:0      LISTENING    1000
```

The PID can then be investigated with:
```cmd
tasklist /FI "PID eq 1000"
```

---

## 6. User and Group Enumeration

### Local users

```cmd
net user
```
Shows local accounts.

```cmd
net user administrator
```
Displays information about a specific account.

### Local groups

```cmd
net localgroup
```
Lists local groups.

```cmd
net localgroup administrators
```
Shows members of the local Administrators group.

---

## 7. Domain Information

```cmd
net user /domain
```
Attempts to enumerate domain users.

```cmd
net group "Domain Admins" /domain
```
Attempts to show members of the Domain Admins group.

```cmd
whoami /groups
```

Can reveal domain groups associated with the current token.

These are particularly useful during **Active Directory** enumeration.

---

## 8. Installed Software

### WMIC

```cmd
wmic product get name,version,vendor
```

Lists installed MSI-based software.

Look for:
- Old software
- Vulnerable versions
- Third-party applications
- Security software
- Software running with elevated privileges
    
**Tool:** `wmic.exe` — Windows built-in on older Windows versions; **deprecated/removed in newer Windows versions**.

### Registry alternative

```cmd
reg query HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall /s
```

Also check 32-bit software on 64-bit Windows:
```cmd
reg query HKLM\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall /s
```

---

## 9. Service Enumeration

Services frequently provide privilege-escalation opportunities.

```cmd
sc query
```
Lists services.

For a specific service:
```cmd
sc qc <service>
```

Example:
```cmd
sc qc WindowsScheduler
```

Look for:
```text
BINARY_PATH_NAME
SERVICE_START_NAME
START_TYPE
```

`BINARY_PATH_NAME` tells you which executable the service runs.
`SERVICE_START_NAME` tells you which account runs it.

Detailed service exploitation belongs in:

```text
03_Service_Exploitation.md
```

---

## 10. Scheduled Task Enumeration

```cmd
schtasks /query /fo LIST /v
```

Provides detailed information about scheduled tasks.

Look for:
- Tasks running as SYSTEM
- Executables/scripts in writable directories
- Tasks executing attacker-writable files
- Interesting task actions

For a specific task:
```cmd
schtasks /query /tn <task_name> /fo LIST /v
```

Detailed exploitation belongs in:
```text
06_Scheduled_Tasks.md
```

---

## 11. File and Directory Permissions

Check interesting directories:
```cmd
icacls C:\SomeDirectory
```

Check a specific executable:
```cmd
icacls C:\SomeDirectory\program.exe
```

Look for permissions such as:
```text
Everyone:(F)
Users:(M)
Authenticated Users:(M)
```

Where:
- `(F)` = Full control
- `(M)` = Modify
- `(W)` = Write
- `(RX)` = Read & Execute
    
Writable files/directories can lead to:
- Service exploitation
- DLL hijacking
- Path hijacking
- Scheduled-task exploitation
- Persistence

Detailed file-permission exploitation belongs in:
```text
04_Weak_File_and_Directory_Permissions.md
```

---

## 12. Search for Interesting Files

Common locations:
```cmd
dir C:\Users\ /s /b
```

Search for files with potentially interesting extensions:
```cmd
dir C:\Users\ /s /b *.txt
dir C:\Users\ /s /b *.ini
dir C:\Users\ /s /b *.config
dir C:\Users\ /s /b *.xml
```

Potentially interesting locations include:
```text
C:\Users\<user>\Desktop
C:\Users\<user>\Documents
C:\Users\<user>\Downloads
C:\ProgramData
C:\Windows\Temp
C:\Temp
```

Look for:
```text
password
passwd
credential
config
backup
database
```

---

## 13. Check PATH

```cmd
echo %PATH%
```

The `PATH` determines where Windows searches for executable commands.

A writable directory appearing early in `PATH` can potentially enable **Path Hijacking**.

Example:
```text
C:\Users\User\bin;
C:\Windows\System32;
C:\Windows;
```

If a privileged program executes:
```cmd
someprogram.exe
```

and searches `PATH`, an attacker-controlled `someprogram.exe` in a writable directory could potentially be executed instead.

Detailed exploitation belongs in:
```text
09_Path_Hijacking.md
```

---

## 14. Check Registry Auto-Run Locations

Useful enumeration:
```cmd
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
```

```cmd
reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\Run"
```

These keys can contain programs automatically executed when a user logs in.

Check their permissions if you suspect a writable persistence opportunity.

Detailed exploitation belongs in:
```text
16_Persistence.md
```

---

# Quick Enumeration Checklist

When you first obtain a Windows shell:
```cmd
whoami
whoami /groups
whoami /priv

hostname
systeminfo

ipconfig /all
netstat -ano

net user
net localgroup administrators

echo %PATH%

sc query
schtasks /query /fo LIST /v

wmic product get name,version,vendor

reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\Run"
```

Then investigate:
```text
[ ] Current user
[ ] Groups
[ ] Privileges
[ ] Windows version/build
[ ] Architecture
[ ] Network configuration
[ ] Listening ports
[ ] Local/domain users
[ ] Administrator membership
[ ] Installed software
[ ] Services
[ ] Scheduled tasks
[ ] Writable files/directories
[ ] PATH
[ ] Registry auto-runs
[ ] Credentials/secrets
```

## Common enumeration → exploitation mapping

|Enumeration finding|Investigate|
|---|---|
|`SeImpersonatePrivilege`|`02_User_and_Group_Privileges.md`|
|Writable service executable|`03_Service_Exploitation.md`|
|Writable directory|`04_Weak_File_and_Directory_Permissions.md`|
|Interesting registry permissions|`05_Registry.md`|
|Vulnerable scheduled task|`06_Scheduled_Tasks.md`|
|Unquoted service path|`07_Unquoted_Service_Paths.md`|
|Missing DLL in writable location|`08_DLL_Hijacking.md`|
|Writable directory in `PATH`|`09_Path_Hijacking.md`|
|Password/config files|`10_Credentials_and_Secrets.md`|
|`AlwaysInstallElevated = 1`|`11_AlwaysInstallElevated.md`|
|UAC weakness|`12_UAC_Bypass.md`|
|Privileged group membership|`14_Privileged_Groups.md`|
|Unpatched OS/software|`15_Kernel_and_OS_Exploits.md`|
|Writable startup location|`16_Persistence.md`|
|Automated enumeration|`17_Automated_Tools.md`|
