## User Enumeration

User enumeration means discovering **valid domain users** in an Active Directory environment. Knowing valid usernames is useful for password spraying, Kerberos attacks, privilege analysis, and further enumeration.

---
### `kerbrute`
a powerful tool to brute-force and enumerate valid usernames via Kerberos protocol

**Username enumeration:**
```bash
kerbrute userenum \
-d <domain> \
--dc <DC-IP> \
users.txt
```
the tool path --> /home/eyad/.local/share/pipx/venvs/impacket/bin

**Example:**

```bash
kerbrute userenum \
-d spookysec.local \
--dc 10.10.10.10 \
users.txt
```

**What it does:**  
Tests a list of usernames against the Kerberos service and identifies accounts that appear to exist.

**Why this works:**  
Kerberos responds differently depending on whether the requested principal exists. `kerbrute` uses these responses to identify potentially valid usernames.

Tools like **enum4linux** or **rpcclient** may return _some_ usernames, but they could be:
- Disabled accounts
- Non-domain accounts
- Fake honeypot users
- Or even false positives

Running those through **kerbrute** lets us confirm which ones are real, active AD users, which allows us to target them more accurately with password sprays.
    
Valid accounts appear as:
```text
[+] VALID USERNAME: guy.smith@tryhackme.loc
```

---

### `netexec` (NXC)

**Enumerate users via SMB:**
```bash
nxc smb <DC-IP> -u '<username>' -p '<password>' --users
```

**Example:**
```bash
nxc smb 10.10.10.10 -u 'guest' -p '' --users
```

**What it does:**  
Attempts to retrieve the domain's user list through SMB/RPC.

**Why this works:**  
Windows exposes information through **SMB/RPC** services. If the supplied account has enough permissions, NXC can query domain user information.

---

### `rpcclient`
A Remote Procedure Call (RPC) is a software communication protocol that allows a program on one computer to execute a function or procedure on another computer over a network as if it were running locally

```bash
rpcclient -U '<domain>/<username>%<password>' <DC-IP>
```

Then:
```text
enumdomusers
```

**Example:**
```bash
rpcclient -U 'spookysec/guest%' 10.10.10.10
```

```text
rpcclient $> enumdomusers
```
**What it does:**  
Enumerates users belonging to the domain.

**Why this works:**  
`rpcclient` communicates with Windows **RPC services**. The `enumdomusers` RPC call asks the domain controller for accounts that the connected user is allowed to enumerate.

###  RPC Null Session

Test anonymous RPC access:
```bash
rpcclient -U "" 10.211.11.10 -N
```
- `-U ""` → empty username
- `-N` → don't ask for a password


---

### `ldapsearch`

```bash
ldapsearch -x -H ldap://<DC-IP> \
-D '<username>@<domain>' -w '<password>' \
-b 'DC=<domain>,DC=<tld>' \
'(objectClass=user)' sAMAccountName
```

**Example:**

```bash
ldapsearch -x -H ldap://10.10.10.10 \
-D 'user@spookysec.local' -w 'Password123!' \
-b 'DC=spookysec,DC=local' \
'(objectClass=user)' sAMAccountName
```

**What it does:**  
Queries LDAP for objects whose class is `user` and displays their `sAMAccountName`.

**Why this works:**  
Active Directory stores users as **LDAP objects**. LDAP allows authenticated clients to query directory objects according to their permissions.

---

### Quick Comparison

|Tool|Method|Authentication|
|---|---|---|
|`nxc`|SMB/RPC|Usually required|
|`rpcclient`|RPC|Usually required|
|`ldapsearch`|LDAP|Usually required|
|`kerbrute`|Kerberos|Not necessarily|

### Key idea

```text
Find valid users
      ↓
Understand the domain
      ↓
Identify interesting accounts
      ↓
Check authentication attacks
      ↓
Enumerate privileges / relationships
```

**Important:** User enumeration itself doesn't mean compromising an account. It gives you the **valid usernames** needed for later AD attacks.