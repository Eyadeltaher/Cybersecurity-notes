## SMB Enumeration

**Purpose:** Discover information about the Windows/AD environment through **SMB (Server Message Block)**.

**Common information:** Hostname, domain/workgroup, users, shares, permissions, and sometimes domain SID.

---

###  `enum4linux`

**Enumerate SMB information:**

```bash
enum4linux -a <TARGET_IP>
```

**Example:**

```bash
enum4linux -a 10.10.10.10
```

**What it does:**  
Performs multiple SMB/RPC enumeration techniques automatically.

**Can enumerate:**
- Domain/workgroup
- Users
- Groups
- Shares
- Domain SID
- OS information
    
**Why does it work?**

Windows exposes information through **SMB and RPC services**. If the target allows the relevant queries, `enum4linux` collects and displays this information.

---

###  `smbclient`

**List available shares:**

```bash
smbclient -L //<TARGET_IP> -N
```

**Example:**
```bash
smbclient -L //10.10.10.10 -N
```

`-L` → List shares  
`-N` → Don't ask for a password

**Connect to a share:**
```bash
smbclient //<TARGET_IP>/<SHARE> -U '<USERNAME>'
```

**Example:**
```bash
smbclient //10.10.10.10/Shared -U 'spookysec.local/mary'
```

**Why does it work?**

SMB servers expose **network shares** that clients can enumerate and access according to their permissions.

---

###  `rpcclient`

```bash
rpcclient -U "" -N <TARGET_IP>
```

Then:
```text
enumdomusers
```

**What it does:**  
Enumerates domain users through Windows RPC.

Other useful commands:
```text
enumdomgroups    # Enumerate domain groups
querydominfo     # Domain information
lsaquery         # Domain SID
srvinfo          # Server information
```

**Why does it work?**

`rpcclient` communicates with Windows **RPC interfaces** exposed through SMB, allowing queries about domain and server objects.

---

### `Nmap`

You can also enumerate shares with:
```bash
nmap -p445 --script smb-enum-shares TARGET_IP
```


---
## SMB Share Permissions
###  `NetExec (nxc)`

**Enumerate shares:**
```bash
nxc smb <TARGET_IP> -u '<USERNAME>' -p '<PASSWORD>' --shares
```

**Example:**
```bash
nxc smb 10.10.10.10 -u 'mary' -p 'Password123!' --shares
```

You may see:
```text
Share       Permissions
-----       -----------
ADMIN$      READ
C$          READ
IPC$        READ
backup      READ,WRITE
```

**Enumerate users:**
```bash
nxc smb <TARGET_IP> -u '<USERNAME>' -p '<PASSWORD>' --users
```

**Enumerate domain information:**
```bash
nxc smb <TARGET_IP> -u '<USERNAME>' -p '<PASSWORD>' --users --groups
```

**Why does it work?**

NXC uses protocols such as **SMB/RPC** to query information from the Windows host/domain.

### `smbmap`

Quickly identify share permissions:
```bash
smbmap -H TARGET_IP
```

Shows whether you have:
```text
READ
WRITE
NO ACCESS
```

This is useful for quickly finding **misconfigured or accessible shares**.


---

**Key ideas:**

> SMB enumeration helps us understand **what the Windows machine exposes** before moving to attacks or deeper AD enumeration.

> **SMB enumeration → Identify shares → Check share permissions → Check NTFS permissions → Determine effective access.**