**LinPEAS** (Linux Privilege Escalation Awesome Script) is a comprehensive tool that scans for privilege escalation vectors. It color-codes output (red for critical, yellow for interesting) to help identify attack vectors quickly.

Instead of manually checking:
```text
sudo
SUID
SGID
Capabilities
Cron
Writable files
Processes
Credentials
Services
Docker
LXD
NFS
```

LinPEAS checks many of these automatically.

Think of it as:
```text
LinPEAS
   ↓
Automated enumeration
   ↓
Potential findings
   ↓
You investigate manually
   ↓
Confirm actual vulnerability
```

**Important:** LinPEAS finds **potential** vulnerabilities. A highlighted result does not automatically mean you have privilege escalation.

---
### How to Use LinPEAS

#### 1. Transfer LinPEAS to Target
```bash
# Upload to target
scp linpeas.sh jan@10.114.149.44:/dev/shm/
```

#### 2. Make Executable
```bash
chmod +x /dev/shm/linpeas.sh
```

#### 3. Run the Scan
```bash
# Basic scan
/dev/shm/linpeas.sh

# Full scan with more checks
/dev/shm/linpeas.sh -a

# Quick scan (less output)
/dev/shm/linpeas.sh -q

# saving output
./linpeas.sh > linpeas.txt 2>&1

# saving output (other way)
./linpeas.sh | tee linpeas.txt

# search saved output
grep -i "sudo" linpeas.txt
```

---

# Understanding the Colors

Generally, pay particular attention to:
```text
Red / highlighted
    ↓
Potentially important finding

Yellow / unusual
    ↓
Something worth investigating

Normal text
    ↓
Informational enumeration
```

> **Color = priority hint, not proof.**
Always manually verify the finding.

---

# `sudo`

One of the first things to inspect.

LinPEAS may show something like:
```text
User may run the following commands:
    (root) /usr/bin/find
```

This means the current user can run:
```text
find
```
as root.

Manually verify:
```bash
sudo -l
```

Expected:
```text
(root) /usr/bin/find
```

Then investigate the binary with GTFOBins.

---

# SUID

LinPEAS searches for SUID binaries.

You may see:
```text
-rwsr-xr-x root root /usr/bin/find
```

The:
```text
s
```

indicates SUID.

Manually verify:
```bash
find / -perm -4000 -type f 2>/dev/null
```

Example:
```text
/usr/bin/passwd
/usr/bin/sudo
/usr/bin/find
```

An unusual SUID binary is worth investigating.

---

# SGID

LinPEAS also looks for SGID binaries.

Manually enumerate:
```bash
find / -perm -2000 -type f 2>/dev/null
```

Example:
```text
/usr/bin/example
```

Check:
```bash
ls -l /usr/bin/example
```

You might see:
```text
-rwxr-sr-x 1 root users ... /usr/bin/example
```

The:
```text
s
```

in the group permission position indicates SGID.

---

# Capabilities

LinPEAS can find file capabilities.

Example:
```text
/usr/bin/python3 cap_setuid=ep
```

Manually verify:
```bash
getcap /usr/bin/python3
```

Expected:
```text
/usr/bin/python3 cap_setuid=ep
```

This is particularly interesting because `CAP_SETUID` can allow a process to change its UID.

Remember:
```text
LinPEAS finds it
      ↓
getcap verifies it
      ↓
Understand capability
      ↓
Check GTFOBins / relevant technique
```

---

# Cron

LinPEAS checks scheduled jobs.

You may find:
```text
* * * * * root /opt/scripts/backup.sh
```

Manually check:
```bash
cat /etc/crontab
```

Also:
```bash
ls -la /etc/cron.d/
```

Then investigate:
```text
Who runs it?
What does it execute?
Is the script writable?
Is its parent directory writable?
Does it use relative commands?
Is there a PATH hijacking opportunity?
```

---

# Writable Files

LinPEAS looks for files your current user can modify.

You may see:
```text
Writable: /opt/scripts/backup.sh
```

Verify:
```bash
ls -l /opt/scripts/backup.sh
```

And:
```bash
test -w /opt/scripts/backup.sh && echo "Writable"
```

Expected:
```text
Writable
```

A writable file becomes especially interesting when it is used by:
```text
root cron
root service
SUID program
privileged script
```

---

# Writable Directories

LinPEAS can also identify writable directories.

Example:
```text
Writable directory: /opt/tools
```

Check:
```bash
ls -ld /opt/tools
```

And:
```bash
test -w /opt/tools && echo "Writable"
```

This becomes particularly interesting when the directory contains or is used by a privileged program.

For example:

```text
root cron
    ↓
/opt/tools/backup
    ↓
/opt/tools writable
```

This could indicate a PATH or file-replacement opportunity.

---

# PATH

LinPEAS examines PATH-related information.

You might see:
```text
PATH=/opt/tools:/usr/local/bin:/usr/bin:/bin
```

Check your PATH:
```bash
echo $PATH
```

Then investigate suspicious writable directories:
```bash
ls -ld /opt/tools
```

A potential PATH hijacking situation looks like:
```text
Privileged process
       +
backup
       +
PATH=/opt/tools:/usr/bin:/bin
       +
/opt/tools writable
       ↓
Potential PATH hijacking
```

Remember to verify **which PATH the privileged process actually uses**.

---

# Processes

LinPEAS enumerates running processes.

You may see:
```text
root       1234  ... /usr/bin/example
```

Useful manual commands:
```bash
ps aux
```

or:
```bash
ps -ef
```

Look for:
```text
root-owned processes
custom applications
scripts
unusual services
applications running from /opt
```

A process is interesting when you can influence something it executes or loads.

---

# Credentials

LinPEAS searches for potentially exposed credentials.

Examples include:

```text
password=
DB_PASSWORD=
API_KEY=
token=
```

It may also find interesting files such as:
```text
.config
.bash_history
.env
application configuration files
SSH-related files
```

Manually inspect suspicious locations rather than assuming every finding is useful.

For example:
```bash
cat ~/.bash_history
```

or:
```bash
find /home -name ".env" -type f 2>/dev/null
```

Credentials can sometimes lead to:
```text
another user
root
database
SSH
application
```

---

# Docker

LinPEAS checks whether Docker is installed and whether your user has access to it.

Check:
```bash
docker --version
```

Example:
```text
Docker version 28.x
```

Then:
```bash
id
```

You might see:
```text
groups=...,docker
```

Membership in the `docker` group can be highly privileged because Docker can interact with the host filesystem and create privileged containers.

The important point is:
```text
docker group
      ↓
Potential host-level privileges
```

Investigate this carefully in a lab rather than assuming Docker installation alone is vulnerable.

---

# LXD

LinPEAS may detect LXD/LXC.

Check:
```bash
which lxc
```

and:
```bash
id
```

Look for relevant group membership.

The important idea is:
```text
LXD access
    ↓
Ability to manage containers
    ↓
Potential interaction with host resources
    ↓
Possible PrivEsc depending on configuration
```

Again, **LXD being installed does not automatically mean PrivEsc**.

---

# NFS

LinPEAS checks NFS-related configuration.

Check:
```bash
cat /etc/exports
```

Example:
```text
/home *(rw,sync,no_root_squash)
```

`no_root_squash` is particularly interesting.

Conceptually:
```text
NFS export
    +
rw
    +
no_root_squash
    ↓
Potentially dangerous configuration
```

You should investigate the export and whether the target is actually reachable/mountable from your lab machine.

---

# Interesting Services

LinPEAS lists services and applications.

Check:
```bash
systemctl list-units --type=service --state=running
```

Example:
```text
backup.service
custom-app.service
```

Then investigate:
```bash
systemctl status backup.service
```

Look for:
```text
ExecStart=
User=
Group=
```

For example:
```text
ExecStart=/opt/scripts/backup.sh
User=root
```

Now investigate:
```text
/opt/scripts/backup.sh
```

and its permissions.

---

# How to Prioritize Findings

Don't try to investigate every line of LinPEAS.

A good priority order is:

```text
1.  sudo
2.  SUID
3.  Capabilities
4.  Writable files used by root
5.  Writable directories
6.  Cron
7.  PATH hijacking
8.  Credentials
9.  Docker / LXD
10. Interesting services
11. NFS
12. Processes
```

Don't keep reading randomly.
Follow:
```text
Capability
    ↓
What binary?
    ↓
Can I execute it?
    ↓
What does CAP_SETUID allow?
    ↓
GTFOBins / technique
    ↓
Manual verification
```

---

# LinPEAS Checklist

```text
[ ] Run LinPEAS
[ ] Save the output
[ ] Check sudo
[ ] Check SUID
[ ] Check SGID
[ ] Check capabilities
[ ] Check cron
[ ] Check writable files
[ ] Check writable directories
[ ] Check PATH
[ ] Check processes
[ ] Check credentials
[ ] Check Docker
[ ] Check LXD
[ ] Check NFS
[ ] Check interesting services
[ ] Prioritize unusual/high-impact findings
[ ] Manually verify each finding
[ ] Use GTFOBins where appropriate
[ ] Test the final technique in the lab
```

### The main idea
```text
                 LinPEAS
                    ↓
          Find possible weaknesses
                    ↓
          ┌─────────┴─────────┐
          ↓                   ↓
       Interesting          Normal
        finding            findings
          ↓
   Manual verification
          ↓
   Understand the issue
          ↓
   Find exploitation path
          ↓
       PrivEsc
```



