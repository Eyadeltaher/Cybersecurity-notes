# What is GTFOBins?

**GTFOBins** is a website containing techniques for abusing legitimate Linux binaries in unexpected ways.

For example, a binary like:
```bash
find
```

is normally used to search for files.

But under certain privileged conditions, `find` can also be used to execute commands.

So GTFOBins answers:

> **"I found this binary with special privileges. What can I do with it?"**

---

### When should I use GTFOBins?

GTFOBins is most useful **after enumeration**.

For example, you find:
```bash
sudo -l
```

Output:
```text
User eyad may run the following commands:
    (root) /usr/bin/find
```

Now you have:
```text
sudo
 ↓
find
 ↓
runs as root
```

Search for:
```text
find + sudo
```

on GTFOBins and look at the **Sudo** section.

The workflow is:
```text
Enumeration
    ↓
Find interesting binary
    ↓
Search GTFOBins
    ↓
Select the relevant technique
    ↓
Test it in the lab
```

---

# Sudo Abuse

Check what you can run with sudo:
```bash
sudo -l
```

Example:
```text
User eyad may run the following commands:
    (root) /usr/bin/find
```

This means:
```text
eyad
 ↓
can execute find
 ↓
as root
```

Now check GTFOBins for:
```text
find → Sudo
```

The important thing is that **sudo itself isn't necessarily the vulnerability**.

The problem is:
```text
User can run a powerful/abusable binary as root
```

---

# SUID Abuse

Find SUID binaries:
```bash
find / -perm -4000 -type f 2>/dev/null
```

Example:

```text
/usr/bin/find
/usr/bin/vim
/usr/bin/passwd
```

If you find an unusual binary:
```text
/usr/bin/find
```

check GTFOBins for:
```text
find → SUID
```

The idea is:
```text
SUID binary
    ↓
Runs with owner's privileges
    ↓
Usually root
    ↓
GTFOBins technique
    ↓
Potential privilege escalation
```

---

# Shell Escapes

Some programs allow you to execute another command or open a shell from inside them.

For example, `vim` normally opens an editor:

```bash
vim file.txt
```

But `vim` can also execute external commands.

This is called a **shell escape**.

Conceptually:
```text
vim
 ↓
Execute external command
 ↓
Shell
```

This becomes dangerous when:
```text
vim
 +
SUID / sudo
 +
root
```

because the shell may inherit elevated privileges.

---

# File Read

Some binaries can be abused to read files that your normal user cannot access.

For example:
```text
sudo binary
      ↓
runs as root
      ↓
can read protected files
```

This is useful when the goal isn't immediately getting a shell but instead accessing sensitive information.

Examples of things you might investigate:
```text
/etc/shadow
/root/*
/etc/passwd
configuration files
SSH keys
application secrets
```

The exact technique depends on the binary.

---

# File Write

Some binaries can also write or modify files.

This can be more dangerous than simple file reading.

For example:
```text
Privileged binary
      ↓
Can write arbitrary files
      ↓
Modify a privileged configuration/script
      ↓
Potential privilege escalation
```

Always check GTFOBins for the **File Write** section when you find a privileged binary.

---

# Command Execution

This is one of the most important GTFOBins categories.

A binary may allow you to execute another command:
```text
binary
  ↓
command execution
  ↓
/bin/sh
  ↓
privileged shell
```

For example, if:
```text
sudo -l
```

shows:
```text
(root) /usr/bin/find
```

then the important question becomes:
> Can `find`, when executed as root, execute another command?

GTFOBins can provide the relevant technique.

---

# Important Binaries

You don't need to memorize every GTFOBins entry. These are worth recognizing:

### `find`

Normally:
```bash
find /tmp -type f
```

Used for finding files.

It can also perform command execution, making it interesting with:
```text
sudo
SUID
```

---

### `vim`

Normally:
```bash
vim file.txt
```

Useful to remember because it can provide:
```text
shell escape
command execution
```

Especially interesting when running as root.

---

### `less`

Normally:
```bash
less file.txt
```

Used to view files.

It can have shell/command-execution functionality, so check GTFOBins when you find it running with elevated privileges.

---

### `awk`

Normally:
```bash
awk '{print $1}' file.txt
```

Used for text processing.

It can also execute commands, making it interesting in privileged contexts.

---

### `bash`

Normally:
```bash
bash
```

If you can execute Bash as root through `sudo` or another privileged mechanism:

```text
sudo
 ↓
bash
 ↓
root shell
```

This is one of the simplest cases.

---

### `cp`

Normally:
```bash
cp file1 file2
```

Used to copy files.

When privileged, its ability to **write files** can become important.

Think:
```text
cp running as root
       ↓
write protected file
       ↓
potential escalation
```

---

### `env`

Normally:
```bash
env
```

displays environment variables.

It can also be used to execute programs with a modified environment, which makes it interesting when allowed through `sudo`.

---

### `python`

Normally:
```bash
python3 script.py
```

Python is particularly interesting because it can:
```text
execute commands
read files
write files
spawn shells
```

If you find:
```text
sudo python3
```

or a capability such as:
```text
/usr/bin/python3 cap_setuid=ep
```

GTFOBins is one of the first places to check.

---

### `perl`

Similar to Python.
```text
perl
 ↓
execute code
 ↓
command execution
```

Therefore:
```text
sudo perl
```

is worth investigating.

---

### `nmap`

`nmap` is normally a network scanner:
```bash
nmap 127.0.0.1
```

Older versions and certain configurations have features that can provide command execution.

If you find:
```text
sudo nmap
```

check its GTFOBins entry rather than assuming it is safe.

---

### `tar`

Normally:
```bash
tar -cf backup.tar files/
```

Used for archiving files.

Some `tar` functionality can execute commands, so:
```text
sudo tar
```

is worth checking on GTFOBins.

---

# Enumeration → GTFOBins → Exploitation

This is the most important workflow to remember.

Suppose:
```bash
sudo -l
```

returns:
```text
User eyad may run the following commands:
    (root) /usr/bin/vim
```

Don't immediately try random commands.

Instead:
```text
1. Enumeration
      ↓
2. Identify binary
      ↓
3. Check GTFOBins
      ↓
4. Select "Sudo"
      ↓
5. Find the relevant technique
      ↓
6. Test in your lab
```

---

# Quick GTFOBins Checklist

When you find an interesting binary:

```text
[ ] What is the binary?
[ ] How can I execute it?
[ ] Is it SUID?
[ ] Can I run it with sudo?
[ ] Does it have capabilities?
[ ] Can it execute commands?
[ ] Can it read files?
[ ] Can it write files?
[ ] Does it have a shell escape?
[ ] Check the corresponding GTFOBins section
```

Then:

```text
Enumeration
     ↓
Interesting binary
     ↓
Privilege context
     ↓
GTFOBins
     ↓
Relevant technique
     ↓
Lab verification
```

### The key idea
**GTFOBins is basically a lookup table for turning legitimate Linux programs into useful primitives when those programs are available with excessive privileges.**

