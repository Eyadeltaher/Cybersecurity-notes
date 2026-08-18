**NOTE** --> the system can be live and does not reply to ICMP Discovery packet --> cause of firewall.
so we use other ways like arp scan and others

---

CVE --> Common Vulnerabilities and Exposure
CVSS --> Common Vulnerability Scoring System
CVSS calculator used to know the score of Vulnerability [https://www.first.org/cvss/calculator/3.0]

---

you can try unknown directory to get error and know the technology used from it
https://depi.gov.eg/content/home  --> https://depi.gov.eg/content/hamadadddddd

---

```bash
dnsenum domain.com  --> enum for DNS records and try DNS Zone Transfer
```
DNS Zone Transfer Misconfiguration

### 1. What is a DNS Zone Transfer?

A **zone transfer** is a mechanism for copying DNS records from a primary DNS server to a secondary DNS server.

For example, suppose `example.com` has:

```text
example.com
├── www       → 10.0.0.10
├── mail      → 10.0.0.20
├── vpn       → 10.0.0.30
├── dev       → 10.0.0.40
└── internal  → 10.0.0.50
```

The secondary DNS server needs these records, so the primary can provide them through:
- **AXFR** → full zone transfer
- **IXFR** → incremental zone transfer
    
Normally, zone transfers should only be allowed between **trusted DNS servers**.

---

### 2. What is the misconfiguration?

The problem occurs when the DNS server allows **anyone** to request a zone transfer.

Conceptually:

```text
Attacker
   │
   │  "Give me the zone for example.com"
   ▼
DNS Server
   │
   │  AXFR
   ▼
Entire DNS Zone
```

Instead of getting only a normal DNS response:

```text
www.example.com → 10.0.0.10
```

the attacker may receive many records at once:

```text
www.example.com       10.0.0.10
mail.example.com      10.0.0.20
vpn.example.com       10.0.0.30
dev.example.com       10.0.0.40
git.example.com       10.0.0.50
internal.example.com  10.0.0.60
...
```

---

### 3. Why is this dangerous?
The main issue is **information disclosure**.
A successful zone transfer can reveal:
- Internal hostnames
- Subdomains
- IP addresses
- Mail servers
- Development/staging environments
- VPN infrastructure
- Administrative systems
- Naming conventions
- Sometimes internal/private network information
    
---
---
---

Linux has **three special permission bits** that extend the normal `rwx` permissions:

1. **SUID — Set User ID**
2. **SGID — Set Group ID**
3. **Sticky Bit**
    

---

## 1. SUID — Set User ID

**SUID makes a file execute with the permissions of the file's owner**, rather than the user who runs it.

Normally:
```text
User runs program → Program runs with user's permissions
```

With SUID:
```text
User runs program → Program runs with owner's permissions
```

### Example

Check `/usr/bin/passwd`:

```bash
ls -l /usr/bin/passwd
```

You might see:
```text
-rwsr-xr-x 1 root root ... /usr/bin/passwd
```

Notice:
```text
-rwsr-xr-x
   ^
   s
```

The `s` in the **owner's execute position** means SUID.

Because `passwd` is owned by `root`, it can perform certain operations with root privileges even when a normal user executes it.

### Set SUID

Using symbolic notation:
```bash
chmod u+s file
```

Using numeric notation:
```bash
chmod 4755 file
```
The **4** represents SUID.

### Remove SUID
```bash
chmod u-s file
```

---

# 2. SGID — Set Group ID

SGID has two different behaviors depending on whether it's applied to a **file** or **directory**.

### On an executable file

The program runs with the **group permissions of the file's group owner**.

Example:
```text
-rwxr-sr-x
     ^
     s
```

The `s` is in the **group execute position**.

Set it with:

```bash
chmod g+s file
```

Numeric:
```bash
chmod 2755 file
```

The **2** represents SGID.

---

### On a directory

This is where SGID becomes particularly useful.

When SGID is set on a directory, **new files and directories inherit the directory's group ownership**.

Example:

```bash
sudo mkdir /shared
sudo chgrp developers /shared
sudo chmod 2775 /shared
```

Now:
```text
/shared
```
has SGID.

Files created inside it will inherit the `developers` group rather than necessarily using the creator's primary group.

This is commonly useful for **shared project directories**.

Check it:
```bash
ls -ld /shared
```

You may see:
```text
drwxrwsr-x
     ^
     s
```

---

# 3. Sticky Bit

The Sticky Bit is mainly used on **directories**.

It means:

> Users can create files in the directory, but they can only delete or rename files they own (or if they have appropriate administrative privileges).

The classic example is:

```bash
/tmp
```

Check it:

```bash
ls -ld /tmp
```

You'll typically see:

```text
drwxrwxrwt
        ^
        t
```

The `t` at the end represents the Sticky Bit.

Without the Sticky Bit, imagine a shared directory where everyone has write permission:

```text
Alice → creates alice.txt
Bob   → deletes alice.txt
```

With the Sticky Bit:

```text
Alice → creates alice.txt
Bob   → cannot delete alice.txt
```

Set it with:

```bash
chmod +t directory
```

Numeric:

```bash
chmod 1777 directory
```

The **1** represents the Sticky Bit.

---

# Easy way to remember

|Permission|Number|Symbol|Main purpose|
|---|--:|---|---|
|**SUID**|`4`|`s`|Execute as **file owner**|
|**SGID**|`2`|`s`|Execute as **group** / inherit directory group|
|**Sticky Bit**|`1`|`t`|Users can only delete **their own files**|

So the special permission numbers are:

```text
4 = SUID
2 = SGID
1 = Sticky
```

They go **before the normal three permission digits**:

```text
chmod 4755 file
      ^
     SUID

chmod 2755 file
      ^
     SGID

chmod 1777 directory
      ^
    Sticky
```

### One important detail

Lowercase `s`/`t` means the execute permission is also present:

```text
rws  → SUID + execute
r-s  → SUID without execute
```

Similarly:

```text
rws  → SGID + execute
r-s  → SGID without execute

rwt  → Sticky + execute
rwT  → Sticky without execute
```

For pentesting/Linux enumeration, **SUID files are especially important to look for**, because incorrectly configured SUID programs can sometimes allow **privilege escalation**.