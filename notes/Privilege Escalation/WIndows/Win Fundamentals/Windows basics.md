# Windows File System Structure

Understanding the **C: drive hierarchy** is important during Windows penetration testing because different directories contain different types of system, user, and application data.

## 1. `C:\Windows`

Contains the **core Windows operating system files**.

Important locations include:
- `C:\Windows\System32` → Core system utilities, DLLs, and executables.
- `C:\Windows\SysWOW64` → 32-bit Windows components on 64-bit systems.
- `C:\Windows\Temp` → Temporary files created by Windows and applications.
- `C:\Windows\Fonts` → Installed system fonts.

### Pentesting Note

One important file is:

```text
C:\Windows\System32\config\SAM
```

The **SAM (Security Account Manager)** database stores local Windows account information, including password hashes.

> Access to the SAM database can be valuable during credential-related attacks, although it is normally protected by Windows.

---

## 2. `C:\Users\<username>`

Contains the **profiles of individual Windows users**.

Example:
```text
C:\Users\Eyad\
```

Common directories include:
```text
Desktop
Documents
Downloads
AppData
```

### `AppData`

Contains application-specific data and configuration.

Important subdirectories:
```text
C:\Users\<username>\AppData\Local
C:\Users\<username>\AppData\LocalLow
C:\Users\<username>\AppData\Roaming
```

### Pentesting Note

`AppData\Roaming` can contain:
- Configuration files
- Application data
- Credentials or tokens
- Browser-related data
- Sensitive application information    

Always inspect user directories when performing enumeration.

---

## 3. `C:\Program Files`

Contains **64-bit installed applications** on a typical 64-bit Windows system.

Example:
```text
C:\Program Files\Google\
C:\Program Files\Microsoft\
```

### Pentesting Note

Check the permissions/ACLs of installed applications.
Access Control List --> ACL

If a low-privileged user can modify:
- Executables
- DLLs
- Configuration files
    
it may create opportunities for **DLL hijacking, binary replacement, or privilege escalation**, depending on how the application is executed.

---

## 4. `C:\Program Files (x86)`

Contains **32-bit applications** on a typical 64-bit Windows installation.

Example:
```text
C:\Program Files (x86)\
```

It should be examined similarly to `C:\Program Files`, especially for:
- Weak permissions
- Writable application directories
- Vulnerable services
- DLL hijacking opportunities

---

## 5. `C:\ProgramData`

Contains **application data shared between users**.

Unlike user-specific `AppData`, this directory is generally used for data that applications need to access across multiple users.

Example:
```text
C:\ProgramData\<Application>\
```

### Pentesting Note

Some directories/files inside `ProgramData` may be writable by regular users.

Potential security issues include:
- Configuration file modification
- Configuration poisoning
- Persistence
- Application abuse

Always check the **permissions/ACLs** rather than assuming a directory is exploitable.

---

## 6. `C:\Temp` and `%TEMP%`

Windows and applications commonly use temporary directories to store temporary files.

Common locations include:
```text
C:\Temp
```

and:
```text
%TEMP%
```

`%TEMP%` is an **environment variable** that points to the current user's temporary directory.

You can check it with:
```cmd
echo %TEMP%
```

### Pentesting Note

Temporary directories may contain:
- Temporary files
- Logs
- Extracted files
- Installer files
- Application artifacts
    
They can also be used as **staging locations** during security testing.

---
### Quick Mental Map

|Location|Main Purpose|Pentesting Interest|
|---|---|---|
|`C:\Windows`|OS files|System files, SAM, services|
|`C:\Users\<user>`|User profiles|Documents, credentials, AppData|
|`C:\Program Files`|64-bit applications|Weak ACLs, DLL hijacking|
|`C:\Program Files (x86)`|32-bit applications|Weak ACLs, DLL hijacking|
|`C:\ProgramData`|Shared application data|Writable configs, persistence|
|`C:\Temp` / `%TEMP%`|Temporary files|Staging, sensitive artifacts|

---

# Windows CMD — Navigation & File Management

These are essential **CMD commands** for exploring and managing the Windows file system.

## 1. `dir`
Lists files and directories in the current location.
```cmd
dir
```

### Useful options
```cmd
dir /a
```

Shows hidden files and directories.
```cmd
dir /s
```

Searches recursively through subdirectories.
```cmd
dir /a /s
```

Shows all files, including hidden ones, recursively.

---

## 2. `cd` — Change Directory

Used to move between directories.
```cmd
cd <folder>
```

Example:
```cmd
cd Users
```

### Move one level up
```cmd
cd ..
```

### Go to the root of the current drive
```cmd
cd \
```

Example:
```text
C:\Users\Eyad> cd \
C:\>
```

---

## 3. `mkdir` — Make Directory

Creates a new directory.
```cmd
mkdir <foldername>
```

Example:
```cmd
mkdir test
```

Creates:
```text
test\
```

---

## 4. `rmdir` — Remove Directory

Removes a directory.
```cmd
rmdir <folder>
```

### Remove a directory and its contents
```cmd
rmdir /s <folder>
```

`/s` → removes the specified directory **and everything inside it**.

### Remove without confirmation
```cmd
rmdir /s /q <folder>
```

`/q` → quiet mode; does not ask for confirmation.

 Be careful with `/s /q` because it can delete a directory and all of its contents.

---

## 5. `copy`

Copies a file from one location to another.
```cmd
copy <source> <destination>
```

Example:
```cmd
copy file.txt C:\Backup\
```

This copies `file.txt` into the `C:\Backup\` directory.

---

## 6. `move`

Moves a file or directory to another location.
```cmd
move <source> <destination>
```

Example:
```cmd
move file.txt C:\Backup\
```

It can also be used to **rename** files:
```cmd
move old.txt new.txt
```

---

## 7. `del`

Deletes files.
```cmd
del <file>
```

Example:
```cmd
del test.txt
```

### Force deletion
```cmd
del /f test.txt
```

`/f` → forces deletion of read-only files.

### No confirmation prompt
```cmd
del /q test.txt
```

`/q` → quiet mode.

---

## 8. `type`

Displays the contents of a text file directly in CMD.
```cmd
type <filename>
```

Example:
```cmd
type notes.txt
```

This is similar to using:
```bash
cat notes.txt
```

on Linux.

### Pentesting Use

Useful for quickly inspecting:
- `.txt`
- `.log`
- `.ini`
- `.conf`
- Other text-based configuration files
    

For example:
```cmd
type C:\Users\Eyad\Desktop\notes.txt
```

---

## 9. `echo`

Prints text to the terminal or writes text to a file.
```cmd
echo Hello
```

Output:
```text
Hello
```

### Write to a file
```cmd
echo Hello > file.txt
```

Creates `file.txt` containing:
```text
Hello
```

### Append to a file
```cmd
echo Another line >> file.txt
```

`>` → **overwrite/create** the file.

`>>` → **append** to the existing file.

---

# Quick Reference

|Command|Purpose|Example|
|---|---|---|
|`dir`|List files/directories|`dir /a`|
|`cd`|Change directory|`cd Users`|
|`cd ..`|Go up one level|`cd ..`|
|`cd \`|Go to drive root|`cd \`|
|`mkdir`|Create directory|`mkdir test`|
|`rmdir`|Remove directory|`rmdir test`|
|`copy`|Copy files|`copy a.txt C:\Backup\`|
|`move`|Move/rename|`move a.txt b.txt`|
|`del`|Delete files|`del a.txt`|
|`type`|Read text file|`type notes.txt`|
|`echo`|Print/write text|`echo hello > a.txt`|

---

## Windows CMD — Process, Network & File Management Notes

### 1. `tasklist`

Displays the currently running processes.
```cmd
tasklist
```

Useful for process enumeration during a pentest.

### `/svc`
Shows the **services hosted by each process**.
```cmd
tasklist /svc
```

Example:
```text
Image Name        PID    Services
svchost.exe       1234   Dhcp, Dnscache
svchost.exe       1500   Spooler
```

This is useful because multiple Windows services can run inside the same `svchost.exe` process.

---

## 2. `taskkill`

Terminates a running process.

### Kill using PID
```cmd
taskkill /PID <PID>
```

Example:
```cmd
taskkill /PID 1234
```

### Force kill
```cmd
taskkill /PID 1234 /F
```

`/F` → forcibly terminates the process.

You can also terminate a process by its image name:
```cmd
taskkill /IM notepad.exe
```

Force it:
```cmd
taskkill /IM notepad.exe /F
```

### Pentesting Use

`tasklist` + `taskkill` can be useful when investigating or managing suspicious processes during a security assessment.

---

# 3. `ipconfig`

Displays Windows network configuration.
```cmd
ipconfig
```

Typical information:
```text
IPv4 Address
Subnet Mask
Default Gateway
```

### `ipconfig /all`

Provides much more detailed information:
```cmd
ipconfig /all
```

Can show:
- Hostname
- Network adapter information
- MAC address
- IPv4/IPv6 addresses
- Subnet mask
- Default gateway
- DNS servers
- DHCP information
- DHCP server
- Lease information
    
### Pentesting Perspective

`ipconfig /all` is useful for quickly understanding the machine's **network configuration and position on the network**.

---

# 4. `netstat -ano`

> The command is **`netstat`**

Displays network connections and listening ports.
```cmd
netstat -ano
```

The important options are:

|Option|Meaning|
|---|---|
|`-a`|Display all connections and listening ports|
|`-n`|Show addresses/ports numerically|
|`-o`|Show the owning process PID|

Example:

```text
Proto  Local Address     Foreign Address    State        PID
TCP    0.0.0.0:80        0.0.0.0:0          LISTENING    1234
TCP    192.168.1.10:443  10.0.0.5:52344    ESTABLISHED  5678
```

### Why is the PID useful?

You can connect the network connection to the process:
```cmd
netstat -ano
tasklist /FI "PID eq 1234"
```

This lets you answer:

> **Which process is listening on this port?**

---

# 5. `tracert`

Shows the path that packets take toward a destination.
```cmd
tracert google.com
```

Example concept:
```text
Your PC
   ↓
Router
   ↓
ISP
   ↓
Intermediate routers
   ↓
Destination
```

It displays the different **hops** between your machine and the destination.

### Useful for

- Understanding network paths
- Troubleshooting connectivity
- Identifying routing problems
- Network reconnaissance
    

Linux equivalent:
```bash
traceroute google.com
```

---

# 6. `ren`

`ren` is short for **rename**.

Used to rename files or directories.
```cmd
ren <old_name> <new_name>
```

Example:
```cmd
ren old.txt new.txt
```

The file:
```text
old.txt
```

becomes:
```text
new.txt
```

Another example:
```cmd
ren test test_old
```

### Important

`ren` changes the name **within the same directory**. It is not normally used to move a file to another directory.

---

# 7. `mklink`

`mklink` creates links in the Windows filesystem.

Basic syntax:
```cmd
mklink [options] <Link> <Target>
```

There are three important types:
```text
Symbolic Link (Soft Link)
Hard Link
Junction Point
```

---

## Symbolic Link — Soft Link

A symbolic link points to another file or directory.

### File symbolic link
```cmd
mklink link.txt target.txt
```

### Directory symbolic link
```cmd
mklink /D link_folder target_folder
```

Think of it like:
```text
link → target
```

The link stores a reference to the target path.

If the target is removed, the symbolic link can become **broken**.

### Example
```text
C:\Users\Eyad\Desktop\config.txt
                ↑
                |
          symbolic link
                |
                ↓
C:\ProgramData\config.txt
```

---

# Hard Link

A hard link creates another directory entry pointing to the **same underlying file data**.

Syntax:
```cmd
mklink /H link.txt target.txt
```

Example:
```cmd
mklink /H copy.txt original.txt
```

Conceptually:
```text
original.txt ──┐
               ├──> Same file data
copy.txt    ───┘
```

### Important characteristics
- Normally used for **files**, not directories.
- Both names refer to the same underlying file.
- Modifying one affects the same underlying content seen through the other.
- Deleting one name does **not** necessarily delete the underlying data as long as another hard link exists.
- It cannot normally point across different volumes.
    

---

# Junction Point

A junction is a Windows filesystem mechanism primarily used to link **directories**.

Syntax:
```cmd
mklink /J link_folder target_folder
```

Example:
```cmd
mklink /J C:\Link C:\RealFolder
```

Conceptually:
```text
C:\Link
   │
   └──────> C:\RealFolder
```

Junctions are commonly associated with directory redirection and compatibility within Windows.

---

# Soft vs Hard vs Junction

| Feature           | Symbolic Link  | Hard Link            | Junction                                |
| ----------------- | -------------- | -------------------- | --------------------------------------- |
| Common name       | Soft link      | Hard link            | Junction point                          |
| Files             | yes            | yes                  | no                                      |
| Directories       | yes            | no                   | yes                                     |
| Points to         | Path/reference | Same underlying file | Directory                               |
| Can become broken | yes            | no                   | Target directory can become unavailable |
| Cross-volume      | yes            | no                   | Generally no                            |
| Created with      | `mklink`       | `mklink /H`          | `mklink /J`                             |

* A hard link itself doesn't become a "broken link" in the same way a symbolic link does because it refers to the same underlying file rather than storing a path to another file.

### Easy way to remember

```text
Symbolic link → "Go over there"
Hard link     → "Another name for the same file"
Junction      → "This directory leads to that directory"
```

---

# 8. `attrib`

`attrib` displays or changes file attributes.
```cmd
attrib
```

You may see:
```text
A    file.txt
H    hidden.txt
R    readonly.txt
S    system.txt
```

The important attributes are:

|Attribute|Meaning|
|---|---|
|`H`|Hidden|
|`R`|Read-only|
|`S`|System|
|`A`|Archive|

---

## `H` — Hidden

Marks a file as hidden.
```cmd
attrib +H file.txt
```

Remove the hidden attribute:
```cmd
attrib -H file.txt
```

---

## `R` — Read-only

Makes the file read-only.
```cmd
attrib +R file.txt
```

Remove:
```cmd
attrib -R file.txt
```

---

## `S` — System

Marks the file as a system file.
```cmd
attrib +S file.txt
```

Remove:
```cmd
attrib -S file.txt
```

---

## `A` — Archive

The archive attribute traditionally indicates that a file has been modified and may need to be included in a backup.
```cmd
attrib +A file.txt
```

Remove:
```cmd
attrib -A file.txt
```

### Multiple attributes

You can combine them:
```cmd
attrib +H +S file.txt
```

Remove both:
```cmd
attrib -H -S file.txt
```

---

#  Security / Pentesting Note — Symbolic Links

Filesystem links can become security-relevant when an application or privileged process **trusts a path without validating where that path ultimately points**.

For example:

```text
Privileged Process
       │
       ↓
C:\Application\config
       │
       ↓
   Symbolic Link
       │
       ↓
Attacker-controlled location
```

This can potentially cause an elevated process to:
- Read attacker-controlled data
- Write to an unintended location
- Access files outside an intended directory
- Bypass poorly designed path restrictions
    
### Sandbox Escape / Path Traversal Context
Symlinks can also be relevant to **sandbox escapes** when a sandbox restricts access based only on filesystem paths but fails to properly resolve links.

The key security concept is:
> **Never assume that a path refers to the location it appears to reference. Resolve and validate the final target, especially when privileged operations are involved.**

This is closely related to **TOCTOU (Time-of-Check to Time-of-Use)** and filesystem link attacks.

---

# Windows Users, Groups & Permissions

Understanding **users, groups, and permissions** is essential for Windows administration and penetration testing. The goal during enumeration is to understand **who you are, which groups you belong to, what you can access, and what privileges you have**.

## 1. `net user`

Displays information about local user accounts.
```cmd
net user
```

Example:
```text
User accounts for \\WIN-PC

-------------------------------------------------------------------------------
Administrator
Guest
Bob
Eyad
```

### Pentesting Use
Useful for quickly discovering:
- Existing users
- Administrator accounts
- Guest accounts
- Potential targets for further enumeration
    

---

## 2. `net user <username>`

Displays detailed information about a specific user.
```cmd
net user admin
```

It can show information such as:
- Username
- Full name
- Account status
- Password-related settings
- Last logon
- Group memberships
- Local account information
    

Example:
```cmd
net user Administrator
```

### Pentesting Perspective

This helps determine whether an account:
- Is enabled
- Has administrative group membership
- Has password restrictions
- Has useful account information
    

---

# 3. Creating a User

```cmd
net user bob pass /add
```

Creates a local user named `bob` with the specified password.

Conceptually:
```text
New User
   │
   ├── Username: bob
   └── Password: pass
```

A safer real-world approach is to avoid putting passwords directly into command history or scripts.

### Pentesting Note
Creating users is an **administrative action** and normally requires sufficient privileges. In a legitimate assessment, this should only be done when explicitly authorized.

---

# 4. Delete a User

```cmd
net user bob /delete
```
Deletes the local user account `bob`.

---

# 5. `net localgroup`

Displays the local groups on the machine.
```cmd
net localgroup
```

Common groups include:
```text
Administrators
Users
Guests
Power Users
Remote Desktop Users
```

Groups make Windows permissions easier to manage because permissions can be assigned to a **group instead of individual users**.

---

# 6. `net localgroup Administrators`

Displays the members of the local **Administrators** group.
```cmd
net localgroup Administrators
```

Example:
```text
Members

-------------------------------------------------------------------------------
Administrator
Bob
```

### Pentesting Use

This is one of the first things to check after identifying your current user.

Question to ask:
> **Is my current account a member of the local Administrators group?**

---

# 7. Add a User to a Group

```cmd
net localgroup Administrators bob /add
```

Adds `bob` to the local **Administrators** group.

Conceptually:
```text
Bob
 │
 └──> Administrators
          │
          └──> Administrative privileges
```

This is a **privileged operation** and should only be performed with authorization.

To remove the user:
```cmd
net localgroup Administrators bob /delete
```

---

# Windows Groups & Permission Levels

Windows uses groups and security principals to determine what users can access and what actions they can perform.

The important built-in groups include:

## 1. `SYSTEM`

`SYSTEM` is **not a normal user account or group**. It is a highly privileged Windows security identity used by the operating system.

It generally has extremely high local privileges and is commonly associated with Windows services and system processes.
```text
SYSTEM
  ↓
Operating System
  ↓
Very high local privileges
```

### Pentesting Perspective

Getting code execution as `SYSTEM` generally represents **full local control of the Windows machine**.

---

## 2. `Administrators`

Members of the local `Administrators` group have extensive administrative rights.
They can generally:
- Modify system configuration
- Install software
- Manage users and groups
- Manage services
- Access protected resources
- Change security settings

However, modern Windows uses **User Account Control (UAC)**, so being an administrator does not necessarily mean every process automatically runs with a fully elevated token.

---

## 3. `Power Users`

`Power Users` is a legacy group.

Historically, members had more permissions than ordinary users but fewer than administrators.

On modern Windows systems, its importance is much lower than it was on older Windows versions.

> Don't assume that being a Power User is equivalent to being an Administrator.

---

## 4. `Users`

The `Users` group represents normal local users.

Members generally have:
- Limited system privileges
- Access to their own user profile
- Ability to run normal applications
- Limited ability to modify system-wide resources
    
A standard user should generally **not** be able to modify protected system files or administrative configuration.

---

## 5. `Guests`

The `Guests` group is intended for users with very limited access.

Guest accounts typically have significantly fewer permissions than standard users.

Historically, this group has been useful when analyzing overly permissive configurations, but modern Windows installations generally disable or restrict the built-in Guest account.

---

# Windows ACL Permissions

Windows uses **ACLs — Access Control Lists** to control access to files and directories.

An ACL contains **Access Control Entries (ACEs)** that define what a particular user or group can do.

For example:

```text
C:\secret.txt

Administrator → Full Control
SYSTEM        → Full Control
Users         → Read
Bob           → Read
Guest         → No Access
```

---

# `icacls`

`icacls` is one of the most important commands for inspecting Windows file and directory permissions.
```cmd
icacls <file>
```

Example:
```cmd
icacls secret.txt
```

Example output:
```text
secret.txt BUILTIN\Administrators:(F)
           NT AUTHORITY\SYSTEM:(F)
           BUILTIN\Users:(R)
```

Common permissions:

|Permission|Meaning|
|---|---|
|`F`|Full Control|
|`M`|Modify|
|`RX`|Read & Execute|
|`R`|Read|
|`W`|Write|
|`D`|Delete|

### Example
```text
Users:(RX)
```
means members of `Users` have:
- Read
- Execute

---

# 6. `whoami /all`

Displays extensive information about the **currently logged-in security context**.
```cmd
whoami /all
```

It can show:
- Current username
- User SID
- Group memberships
- Group SIDs
- Group attributes
- User privileges

Example concept:
```text
USER
 └── DOMAIN\Bob

GROUPS
 ├── Users
 ├── Remote Desktop Users
 └── Administrators

PRIVILEGES
 ├── SeChangeNotifyPrivilege
 └── ...
```

# 7. `whoami /priv`

Displays the privileges associated with the current security token.
```cmd
whoami /priv
```

Example:
```text
Privilege Name                  State
------------------------------  --------
SeChangeNotifyPrivilege        Enabled
SeShutdownPrivilege             Disabled
SeImpersonatePrivilege          Enabled
```

Some Windows privileges can have significant security implications depending on:
- Whether they are assigned
- Whether they are enabled
- The Windows version/configuration
- What processes/services the token belongs to

For example:
```text
SeImpersonatePrivilege
SeBackupPrivilege
SeRestorePrivilege
SeDebugPrivilege
```

can be particularly interesting during privilege-escalation analysis.

---
#  Windows Privilege Enumeration Workflow

After obtaining a Windows shell, a useful basic workflow is:
```cmd
whoami
whoami /all
whoami /priv

net user
net localgroup
net localgroup Administrators

ipconfig /all

tasklist
tasklist /svc

icacls <interesting-file>
```

The key questions during enumeration are:
1. **Who am I?** → `whoami`
2. **Which groups am I in?** → `whoami /all`
3. **What privileges do I have?** → `whoami /priv`
4. **What users exist?** → `net user`
5. **Who is an administrator?** → `net localgroup Administrators`
6. **Who can access this file?** → `icacls <file>`
7. **Can I modify something used by a privileged process?** → inspect ACLs + processes/services.

---

# Windows Authentication & Credential Access

## 1. `runas`

`runas` allows a user to run a program under a **different Windows user account**.

Basic syntax:
```cmd
runas /user:<username> <program>
```

Example with a domain account:
```cmd
runas /user:DOMAIN\admin cmd.exe
```

Windows will prompt for the password of `DOMAIN\admin`.

If authentication succeeds, a new `cmd.exe` process runs under that account's security context.
### Example
```text
Current User
     │
     │ runas
     ↓
DOMAIN\admin
     │
     ↓
cmd.exe running as admin
```

### Pentesting Perspective

If valid credentials have been **legitimately obtained during an authorized assessment**, `runas` can be used to verify whether those credentials provide access to a restricted application or resource.

> `runas` does **not** bypass authentication. You still need valid credentials and sufficient permissions.

---

# 2. SAM — Security Account Manager

The **SAM (Security Account Manager)** is a Windows database that stores information about **local user accounts**.

It is located at:
```text
C:\Windows\System32\config\SAM
```

The SAM contains credential-related information, including **NT password hashes** for local accounts.

Conceptually:
```text
SAM
 │
 ├── Administrator → NT hash
 ├── Guest         → NT hash
 └── Bob           → NT hash
```

The SAM is normally protected while Windows is running, so a normal user cannot simply read it like an ordinary text file.

---

# 3. SAM and NT Hashes

### SAM stores
**NT hashes** of local account passwords.

### SAM does NOT store

"NTLMv2 hashes."

This terminology is often confusing.
```text
NT hash
   ↓
Stored as part of local account credential data
   ↓
SAM
```

Whereas:
```text
NTLM / NTLMv2
   ↓
Authentication protocols
   ↓
Used during network authentication
```

So:
> **NT hash ≠ NTLMv2**

---

# 4. NTLM vs NTLMv2

### NTLM

NTLM is a Windows authentication protocol based on a **challenge-response mechanism**.

The server sends a challenge, and the client generates a response using credential-derived information.

Conceptually:
```text
Client                    Server
  │                         │
  │──── Authentication ────>│
  │                         │
  │<──── Challenge ─────────│
  │                         │
  │──── Response ──────────>│
  │                         │
  │      Authentication     │
```

### NTLMv2

NTLMv2 is a newer and stronger version of the NTLM authentication protocol.

It uses additional information in the challenge-response calculation, making it more resistant to some attacks than the older NTLM protocol.

The important distinction for your notes is:
```text
SAM
 ↓
NT password hashes

Network authentication
 ↓
NTLM / NTLMv2 protocols
 ↓
Challenge-response
```

---

# 5. How SAM Can Be Obtained During a Pentest

During an **authorized penetration test**, credential-dumping tools and offline techniques can be used to obtain the SAM database and associated system information.

Common tools/techniques include:
### Mimikatz
Mimikatz can perform Windows credential-related operations, including extracting credential material from certain sources when the tester has sufficient privileges.

### Impacket
Impacket includes tools for Windows authentication and credential-related operations, including techniques involving SAM data in appropriate privileged contexts.

### Volume Shadow Copy
A **Volume Shadow Copy** can provide an offline snapshot of the filesystem.

Conceptually:
```text
Running Windows
      │
      ↓
Volume Shadow Copy
      │
      ├── SAM
      └── SYSTEM
```

The `SYSTEM` hive is important because it contains information needed to interpret protected credential data from the SAM.

### Important
Accessing the SAM or dumping credentials generally requires **administrative/System-level access** and should only be performed on systems where you have explicit authorization.

---

# Windows Services Management

Windows services are background processes that can start automatically and run without direct user interaction.

### 1. Query Services
```cmd
sc query
```

Shows the status of active services.
```cmd
sc query type=all
```

Shows all services, including running and stopped services.
```cmd
sc query <name>
```

Shows the status of a specific service.

Example:
```cmd
sc query Spooler
```

### 2. Start & Stop Services

Start a service:
```cmd
sc start <name>
```

Stop a service:
```cmd
sc stop <name>
```

Example:
```cmd
sc start Spooler
sc stop Spooler
```

### 3. Create a Service

```cmd
sc create <name> binPath= "<path-to-exe>"
```

Example:
```cmd
sc create MyService binPath= "C:\Tools\program.exe"
```

This creates a Windows service that points to the specified executable.

> **Note:** The space after `=` is important with `sc` commands.

### 4. Delete a Service

```cmd
sc delete <name>
```

Example:
```cmd
sc delete MyService
```

This removes the service configuration.

### 5. Service Configuration — Privilege Escalation

```cmd
sc qc <name>
```

Displays the service's configuration, including:
- `BINARY_PATH_NAME` → path of the executable
- `SERVICE_START_NAME` → account used to run the service
- Startup type
- Dependencies
    

Example:
```cmd
sc qc MyService
```

#### Why is `sc qc` useful for PrivEsc?

During Windows privilege escalation, check whether a **high-privileged service** runs an executable that a low-privileged user can modify.

For example:
```text
SERVICE_START_NAME : LocalSystem
BINARY_PATH_NAME   : C:\Program Files\App\app.exe
```

If `app.exe` is writable by the current user, modifying or replacing it could potentially lead to **code execution with the service's privileges**.

**Key idea:**
> **Check who runs the service → check what executable it runs → check whether that executable/path is writable.**

---
# Windows Registry 

The **Windows Registry** is a hierarchical database used by Windows to store configuration settings for the OS, users, applications, and services.

### 1. Registry Hives

The main Registry hives are:

|Hive|Name|Purpose|
|---|---|---|
|**HKLM**|HKEY_LOCAL_MACHINE|System-wide settings|
|**HKCU**|HKEY_CURRENT_USER|Settings for the current user|
|**HKCR**|HKEY_CLASSES_ROOT|File associations and COM information|
|**HKU**|HKEY_USERS|Settings for all loaded user profiles|
|**HKCC**|HKEY_CURRENT_CONFIG|Current hardware configuration|

#### Important HKLM subkeys
```text
HKLM\SOFTWARE
```

Stores software and application configuration.
```text
HKLM\SYSTEM
```

Stores Windows system and service configuration.
```text
HKLM\SAM
```

Contains information related to local user accounts and password hashes.
```text
HKLM\SECURITY
```

Contains Windows security-related information.

#### Important HKCU locations

```text
HKCU\Software\Microsoft
```
Contains Microsoft application and Windows user settings.

```text
HKCU\Environment
```
Contains environment variables for the current user.

```text
HKCU\Console
```
Contains settings for Windows console applications.

---

# 2. Persistence via Registry

Attackers can abuse certain Registry locations to make a program execute automatically.

### HKCU Run Key

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
```
Programs placed here can execute automatically when **that user logs in**.

### HKLM Run Key

```text
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
```
Programs placed here can execute when **users log in**.

Usually requires **administrator privileges** to modify.

### Services

```text
HKLM\SYSTEM\CurrentControlSet\Services
```

Windows services are also configured through the Registry.

A service can be configured to start automatically and execute a specified program.

---

# 3. Registry Commands

Windows provides the `reg` command for interacting with the Registry.

### Query

Read Registry values:
```cmd
reg query HKCU\Environment
```
Useful for checking existing configuration and values.

### Add

Add a Registry value:
```cmd
reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Persist /t REG_SZ /d "cmd.exe"
```
Where:
- `/v` → value name
- `/t` → value type
- `/d` → data to store
    
### Delete

Delete a Registry value:
```cmd
reg delete HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v OldEntry /f
```
`/f` forces deletion without asking for confirmation.

### Export

Back up a Registry key:
```cmd
reg export HKLM backup.reg
```
Creates a `.reg` file containing the exported Registry data.

---

###  Privilege Escalation / Persistence Takeaway

When investigating a Windows machine, check Registry locations for:

```text
Run Keys
Services
Startup-related entries
Writable Registry keys
```

The important question is:

> **Can a low-privileged user modify a Registry location that causes a program to execute with higher privileges?**