d
## 1. Host Discovery

First, identify **live hosts** in the target subnet.

### fping
```bash
fping -agq 10.211.11.0/24
```
- `-a` → Show only alive hosts.
- `-g` → Generate targets from the subnet.
- `-q` → Quiet output.

### Nmap
```bash
nmap -sn 10.211.11.0/24
```
- `-sn` → Host discovery only; doesn't perform port scanning.
    

---

# 2. Identify the Domain Controller

Important AD ports:

|    Port | Service     | Purpose                       |
| ------: | ----------- | ----------------------------- |
|  **88** | Kerberos    | AD authentication             |
| **135** | MS-RPC      | RPC enumeration               |
| **139** | NetBIOS/SMB | Legacy SMB                    |
| **389** | LDAP        | AD queries                    |
| **445** | SMB         | File sharing & AD enumeration |
| **464** | Kerberos    | Password changes              |
|     636 | LDAPS       | Encrypted LDAP                |

### Targeted Nmap Scan
```bash
nmap -p 88,135,139,389,445,636 -sV -sC -iL hosts.txt
```
- `-p` → Scan specific AD-related ports.
- `-sV` → Detect service versions.
- `-sC` → Run default NSE scripts.
- `-iL hosts.txt` → Read targets from a file.
    

**DC indicator:**
```text
88 (Kerberos)
389 (LDAP)
445 (SMB)
```
A host exposing these services is likely to be a **Domain Controller**.

---
# 3. Full Port Scan

For a more complete assessment:
```bash
nmap -sS -p- -T3 -iL hosts.txt -oN full_port_scan.txt
```
- `-sS` → TCP SYN scan.
- `-p-` → Scan all 65,535 ports.
- `-T3` → Normal scan speed.
- `-iL` → Read targets from `hosts.txt`.
- `-oN` → Save results to a file.
    
---

## DNS Enumeration

it is worth performing basic DNS enumeration to identify key services in the AD environment. DNS is the backbone of AD. Domain controllers, mail servers, and other critical infrastructure are all registered as DNS records. A few useful lookups include:

```bash
# Identify domain controllers via SRV records
nslookup -type=SRV _ldap._tcp.dc._msdcs.thm.loc 192.168.12.100

# Identify the Kerberos KDC
nslookup -type=SRV _kerberos._tcp.thm.loc 192.168.12.100

# Identify mail servers
nslookup -type=MX thm.loc 192.168.12.100
    
```

---

# Windows Manual Enumeration

Manual enumeration using native **CMD** and **PowerShell** commands.  
This is commonly called **Living off the Land (LOTL)** because it relies on built-in Windows tools.


## 1. Current User

### `whoami`
```cmd
whoami
```
Shows the current username and domain.

```text
DOMAIN\username
COMPUTER\username
```
- `DOMAIN\user` → Domain account
- `COMPUTER\user` → Local account

### Detailed User Information

```cmd
whoami /all
```

Shows:
- Username
- SID
- Group memberships
- Token privileges
    
**Important:** Check for interesting privileges such as:
```text
SeImpersonatePrivilege
SeAssignPrimaryTokenPrivilege
SeBackupPrivilege
SeRestorePrivilege
SeDebugPrivilege
```

---

## 2. Important Token Privileges

### SeImpersonatePrivilege

```text
SeImpersonatePrivilege
```

Allows a process to impersonate another security token.

Often interesting when the account is running as a **service account**.

Associated with token impersonation techniques such as **Potato attacks**.

### SeAssignPrimaryTokenPrivilege

Allows assigning another user's primary token to a process.

Often relevant together with:
```text
SeImpersonatePrivilege
```

### SeBackupPrivilege

Allows reading files while bypassing normal file permissions.

Can potentially expose sensitive files such as registry hives.

### SeRestorePrivilege

Allows writing to files/registry while bypassing normal permissions.

Can be dangerous when combined with writable system resources.

### SeDebugPrivilege

Allows debugging other processes.

Can potentially allow access to privileged process memory, including **LSASS**.

> When enumerating privileges, don't just look at group membership. **Token privileges can provide another path to privilege escalation.**

---

# 3. System Information

## Hostname
```cmd
hostname
```

Displays the computer name.

Useful for identifying the machine's role.

Example:
```text
DC01
WEB01
WIN10-PC
```

---

## Detailed System Information

```cmd
systeminfo
```

Displays:
- OS version
- Hostname
- Domain/workgroup
- System architecture
- Installed hotfixes
- Other system information

### Find OS Information

```cmd
systeminfo | findstr /B "OS"
```

### Find Domain Information

```cmd
systeminfo | findstr /B "Domain"
```

> `systeminfo` may require administrator privileges for some information.

---

# 4. Environment Variables

## CMD
```cmd
set
```

Displays environment variables.

Interesting variables include:
```text
USERNAME
USERDOMAIN
USERPROFILE
PATH
TEMP
ProgramFiles
```

Environment variables can reveal:
- Current user
- Domain
- User directories
- Installed software
- Development tools
- Important paths

### PowerShell

```powershell
Get-ChildItem Env:
```

or:

```powershell
dir env:
```

---

# 5. Enumerating Users

## Local Users

```cmd
net user
```

Lists local user accounts.

### Information About a User

```cmd
net user <username>
```

Example:

```cmd
net user administrator
```

Useful information includes:
- Account status
- Password settings
- Last logon
- Group memberships

---

## Domain Users

```cmd
net user /domain
```

Lists users in the Active Directory domain.

### Domain User Information

```cmd
net user <username> /domain
```

Example:
```cmd
net user administrator /domain
```

Useful information:
- Account status
- Password information
- Last logon
- Group memberships

> `/domain` makes the command query the domain instead of the local machine.

---

# 6. Enumerating Groups

## Domain Groups

```cmd
net group /domain
```

Lists all domain groups.

Interesting groups include:

```text
Domain Admins
Enterprise Admins
Server Operators
Backup Operators
Administrators
```

Also investigate custom groups containing:

```text
Admin
Admins
Backup
SQL
IT
```

---

## Domain Group Members

```cmd
net group "<group>" /domain
```

Example:
```cmd
net group "Domain Admins" /domain
```

Shows members of the specified domain group.

### Domain Computers

```cmd
net group "Domain Computers" /domain
```

Lists domain computer accounts.
Machine accounts usually end with:
```text
$
```

Example:
```text
DESKTOP-01$
DC01$
```

---

# 7. Local Groups

### List Local Groups

```cmd
net localgroup
```

Displays all local groups.

### List Group Members

```cmd
net localgroup administrators
```

Shows members of the local **Administrators** group.

Other interesting groups:
```text
Administrators
Backup Operators
Remote Desktop Users
Remote Management Users
```

---

# 8. Logged-On Users

## `query user`
```cmd
query user
```

or:
```cmd
quser
```

Shows currently logged-on users.

Example:
```text
USERNAME        SESSIONNAME    ID   STATE
administrator   rdp-tcp#0      2    Active
user            console        1    Active
```

Useful for identifying:
- Active users
- RDP sessions
- Console sessions
- Potential privileged users

**Important:** A privileged user currently logged in can be significant during authorized privilege-escalation testing.

---

# 9. Running Processes

## `tasklist`

```cmd
tasklist
```

Lists running processes.

### Verbose Output

```cmd
tasklist /V
```

Useful for identifying:
- Running applications
- Security software
- Services
- Privileged processes
- Processes belonging to other users

---

# 10. SMB Sessions

```cmd
net session
```

Displays active SMB sessions with the local machine.

Useful for identifying other systems/users currently connected through SMB.

> Usually requires administrator privileges.

---

# 11. User Home Directories

```cmd
dir C:\Users
```

Lists user directories.

Example:
```text
C:\Users\Administrator
C:\Users\john
C:\Users\Public
```

Useful for discovering users who have logged onto the machine.

---

# 12. Service Accounts

Services often run under dedicated accounts.

These accounts may have elevated privileges and sometimes have long-lived credentials.

## WMIC
```cmd
wmic service get Name,StartName
```

Shows:
- Service name
- Account used to run the service

Example:
```text
Name             StartName
----             ---------
SomeService      LocalSystem
BackupService    DOMAIN\backup
```

Interesting:
```text
DOMAIN\username
```

because a service may be running with a domain account.

### PowerShell Equivalent

```powershell
Get-WmiObject Win32_Service | Select Name, StartName
```

---

# 13. Enumerating Services with SC

## List Services

```cmd
sc query state= all
```

Lists all services.

### Filter Results

```cmd
sc query state= all | find "keyword"
```

Example:
```cmd
sc query state= all | find "DHCP"
```

---

## Service Configuration

```cmd
sc qc <ServiceName>
```

Example:
```cmd
sc qc DHCP
```

Important fields:
```text
BINARY_PATH_NAME
START_TYPE
SERVICE_START_NAME
```

### Why?

`SERVICE_START_NAME` tells you which account runs the service.

`BINARY_PATH_NAME` shows the executable path.

Both are important when investigating **service misconfigurations**.

---

# 14. Environment Variables for Software Discovery

```cmd
set
```

Look for variables that reveal installed software or development environments.

Examples:
```text
JAVA_HOME
PYTHONPATH
PATH
ProgramFiles
```

These can reveal:
- Java
- Python
- Development tools
- Custom applications
- Interesting directories

---

# 15. Windows Registry

The Registry stores a large amount of Windows configuration information.

Main registry hives:
```text
HKLM
HKCU
```

- `HKLM` → Computer/system-wide configuration
- `HKCU` → Current user's configuration

---

# 16. Auto-Logon Credentials

Check:
```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
```

Look for:
```text
DefaultUsername
DefaultPassword
AutoAdminLogon
```

You can query a specific value:
```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultUsername
```

Check whether:
```text
AutoAdminLogon = 1
```

and whether a:
```text
DefaultPassword
```

exists.

Misconfigured auto-logon can expose credentials in plaintext.

---

# 17. Installed Applications

```cmd
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall
```

Lists installed applications registered in the Registry.

Useful for discovering:
- Installed software
- Legacy applications
- Potentially vulnerable applications
- Applications with known default credentials

---

# 18. Search the Registry

Search for a keyword:
```cmd
reg query HKLM /f "password" /t REG_SZ /s
```

Breakdown:
```text
HKLM        → Search HKEY_LOCAL_MACHINE
/f          → Search for text
"password"  → Search term
/t REG_SZ   → Search string values
/s          → Search recursively
```

Other useful keywords:
```text
password
pass
credential
secret
token
username
```

---

# 19. Scheduled Tasks

### List Scheduled Tasks

```cmd
schtasks /query
```

Displays scheduled tasks.

Useful for finding:
- Tasks running as privileged users
- Custom scripts
- Suspicious executables
- Tasks with weak permissions
- Tasks running automatically

### More Detailed Output

```cmd
schtasks /query /fo LIST /v
```

Useful when you need details such as:
```text
Task name
Run As User
Task action
Schedule
```

### Run a Task
```cmd
schtasks /run /tn "<TaskName>"
```

### Create a Task
```cmd
schtasks /create
```

> For enumeration, focus primarily on **who runs the task** and **what executable/script it launches**.

---

# Quick Enumeration Checklist

For a fresh Windows shell, a practical order is:
```cmd
whoami /all
hostname
systeminfo
set

net user
net user /domain

net localgroup
net localgroup administrators

net group /domain
net group "Domain Admins" /domain
net group "Domain Computers" /domain

quser
tasklist /V
net session

dir C:\Users

wmic service get Name,StartName
sc query state= all
sc qc <ServiceName>

reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall

reg query HKLM /f "password" /t REG_SZ /s

schtasks /query /fo LIST /v
```

### Key things to look for
```text
Current user
    ↓
Groups / privileges
    ↓
OS / hostname / domain
    ↓
Users / administrators
    ↓
Logged-on privileged users
    ↓
Processes
    ↓
Service accounts
    ↓
Service configurations
    ↓
Environment variables
    ↓
Registry secrets / configuration
    ↓
Scheduled tasks
```

---

# Active Directory Enumeration with PowerShell

The **ActiveDirectory PowerShell module** provides commands for querying users, groups, computers, and domain policies.

## 1. ActiveDirectory Module

### Check if installed
```powershell
Get-Module -ListAvailable ActiveDirectory
```

**What it does:** Checks whether the `ActiveDirectory` module is installed.

### Import the module
```powershell
Import-Module ActiveDirectory
```

**What it does:** Loads the AD cmdlets into the current PowerShell session.

> On Windows workstations/servers, the module is commonly provided through **RSAT**. Domain Controllers normally have the AD management tools available.

---

# 2. User Enumeration

### Enumerate all users
```powershell
Get-ADUser -Filter *
```

**What it does:** Lists all domain user accounts.

### Get a specific user
```powershell
Get-ADUser -Identity <username>
```

### Get all properties
```powershell
Get-ADUser -Identity <username> -Properties *
```

### Select interesting properties
```powershell
Get-ADUser -Identity <username> -Properties LastLogonDate,MemberOf,Title,Description,PwdLastSet
```

Useful properties:

|Property|Purpose|
|---|---|
|`LastLogonDate`|Last known logon|
|`MemberOf`|Groups the user belongs to|
|`Description`|May contain useful information|
|`Title`|User's role/job|
|`PwdLastSet`|Password last-set information|
|`Enabled`|Whether the account is enabled|
|`SamAccountName`|Username|

### Search for users by name

```powershell
Get-ADUser -Filter "Name -like '*admin*'"
```

**What it does:** Finds users whose name contains `admin`.

---

# 3. Group Enumeration

### Enumerate all groups

```powershell
Get-ADGroup -Filter *
```

### Show only group names

```powershell
Get-ADGroup -Filter * | Select Name
```

### Enumerate group members

```powershell
Get-ADGroupMember -Identity "<Group Name>"
```

Example:
```powershell
Get-ADGroupMember -Identity "Domain Admins"
```

**What it does:** Shows users/groups that belong to the specified group.

Important groups to check:
- `Domain Admins`
- `Enterprise Admins`
- `Administrators`
- `Backup Operators`
- `Account Operators`
- `Server Operators`
- `Remote Management Users`

---

# 4. Computer Enumeration

### Enumerate all computers

```powershell
Get-ADComputer -Filter *
```

### Show useful information

```powershell
Get-ADComputer -Filter * | Select Name,OperatingSystem
```

**What it does:** Lists domain computers and their operating systems.

Useful for identifying:
- Domain Controllers
- Servers
- Workstations
- OS versions

---

# 5. Domain Password Policy

```powershell
Get-ADDefaultDomainPasswordPolicy
```

**What it does:** Displays the default domain password policy.

Important fields:

|Property|Meaning|
|---|---|
|`MinPasswordLength`|Minimum password length|
|`MaxPasswordAge`|Maximum password age|
|`MinPasswordAge`|Minimum password age|
|`PasswordHistoryCount`|Number of remembered passwords|
|`ComplexityEnabled`|Password complexity requirement|
|`LockoutThreshold`|Failed attempts before lockout|
|`LockoutDuration`|Account lockout duration|

Example:
```text
MinPasswordLength : 7
MaxPasswordAge    : 42.00:00:00
ComplexityEnabled : True
LockoutThreshold  : 0
```

---

# 6. Useful Enumeration Workflow
```powershell
# Check/import module
Get-Module -ListAvailable ActiveDirectory
Import-Module ActiveDirectory

# Users
Get-ADUser -Filter *
Get-ADUser -Identity <username> -Properties *

# Groups
Get-ADGroup -Filter *
Get-ADGroupMember -Identity "Domain Admins"

# Computers
Get-ADComputer -Filter *
Get-ADComputer -Filter * | Select Name,OperatingSystem

# Password policy
Get-ADDefaultDomainPasswordPolicy
```

## Quick Reference

|Goal|Command|
|---|---|
|Check AD module|`Get-Module -ListAvailable ActiveDirectory`|
|Import module|`Import-Module ActiveDirectory`|
|List users|`Get-ADUser -Filter *`|
|User details|`Get-ADUser -Identity <user>`|
|All user properties|`Get-ADUser -Identity <user> -Properties *`|
|Find users|`Get-ADUser -Filter "Name -like '*admin*'"`|
|List groups|`Get-ADGroup -Filter *`|
|Group members|`Get-ADGroupMember -Identity "<group>"`|
|List computers|`Get-ADComputer -Filter *`|
|Computer OS|`Get-ADComputer -Filter * \| Select Name,OperatingSystem`|
|Password policy|`Get-ADDefaultDomainPasswordPolicy`|