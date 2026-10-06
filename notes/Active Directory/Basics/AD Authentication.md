# 1- NTLM Authentication

## What is NTLM?

**NTLM (NetNTLM)** is a **challenge-response authentication protocol** used in Windows.
- **NTLMv1** → Old and insecure.
- **NTLMv2** → Improved, but still has security weaknesses.
- Kerberos is the default in modern AD, but NTLM remains as a fallback.
    

---

## How NTLM Works

```text
Client             Server              Domain Controller
  │                   │                       │
  │── Username ──────>│                       │
  │<── Challenge ─────│                       │
  │                   │                       │
  │── Response ──────>│                       │
  │                   │── Challenge + ───────>│
  │                   │   Response             │
  │                   │<──── Verification ────│
  │<── Access ────────│                       │
```

1. Client sends its **username** to the server.
2. Server sends a random **challenge**.
3. Client uses the **NT hash** of its password to calculate a response.
4. Server forwards the username, challenge, and response to the **Domain Controller**.
5. DC calculates the expected response using the user's NT hash.
6. If the responses match → **authentication succeeds**.
    
> The actual password is **never sent over the network**.

## NTLM Advantages
- Simple authentication mechanism.
- Doesn't require time synchronization like Kerberos.
- Works as a fallback when Kerberos is unavailable.
- Can work in **workgroup/non-domain environments**.
    
## NTLM Security Weaknesses
- **No mutual authentication** → vulnerable to impersonation/MITM.
- **NTLM relay attacks** are possible.
- **Pass-the-Hash** → an attacker with the NT hash can authenticate without knowing the password.
- **NTLMv1** has weak cryptography.

## When NTLM Is Used
- Kerberos is unavailable.
- The resource is accessed using an **IP address** instead of a hostname.
- The service has no valid **SPN**.
- The target isn't domain-joined.
- A legacy application requires NTLM.
    

### Key Difference
```text
Kerberos:
User → DC → TGT → TGS → Service

NTLM:
User → Service → DC → Verification
```

**Kerberos = ticket-based**
**NTLM = challenge-response**

---

# NTLM Authentication with Impacket
**Impacket** is a collection of Python tools for interacting with network protocols commonly used in Windows/AD environments.

## `smbclient.py`
Used to connect to an **SMB share** using credentials.
```bash
smbclient.py thm.loc/claire:'Password123!'@192.168.11.51
```
### Format
```text
smbclient.py DOMAIN/USERNAME:PASSWORD@TARGET_IP
```

Example:
```text
smbclient.py thm.loc/claire:'Password123!'@192.168.11.51
       │        │       │                 │
       │        │       │                 └── Target
       │        │       └── Password
       │        └── Username
       └── Domain
```

After successful authentication, you get an SMB shell:
```text
#
```
### List Available Shares
```text
shares
```
Lists the SMB shares available on the target.
### Connect to a Share
```text
use SHARE1
```
Connects to the `SHARE1` SMB share.

---

# 2- Kerberos Authentication

## What is Kerberos?

**Kerberos** is the default authentication protocol in modern Windows domains.

The main difference from NTLM:
```text
NTLM:
Client → Service → Domain Controller

Kerberos:
Client → Domain Controller → Ticket → Service
```

Kerberos authenticates the user **with the Domain Controller first**, then uses tickets to access services.

---

## Key Components

|Component|Purpose|
|---|---|
|**KDC**|Handles Kerberos ticket requests; runs on the DC|
|**AS**|Verifies users and issues TGTs|
|**TGS**|Issues service tickets|
|**TGT**|Used to request service tickets|
|**ST**|Ticket for a specific service|
|**SPN**|Identifies a specific service|
|**KRBTGT**|Special AD account whose hash encrypts TGTs|

---

# Kerberos Authentication Flow

### 1. AS-REQ
The client sends the username and a timestamp encrypted with a key derived from the user's password.
```text
Client ───── AS-REQ ─────> KDC
```

### 2. AS-REP

The KDC verifies the user and returns:
- Session Key
- TGT
```text
Client <──── AS-REP ───── KDC
              │
              ├── Session Key
              └── TGT
```

The **TGT is encrypted with the KRBTGT hash**, so the client cannot modify or read it.


### 3. TGS-REQ
When accessing a service, the client sends:
- TGT
- Service's SPN
- Authenticator

```text
Client ───── TGS-REQ ─────> KDC
```

### 4. TGS-REP
The KDC returns a **Service Ticket (ST)** and a service session key.
```text
Client <──── TGS-REP ───── KDC
              │
              ├── Service Ticket
              └── Service Session Key
```

The Service Ticket is encrypted using the **service account's password hash**.

### 5. AP-REQ
The client presents the Service Ticket to the target service.
```text
Client ───── AP-REQ / ST ─────> Service
                                  │
                                  ▼
                              Access Granted
```

The service decrypts and validates the ticket using its own account's key.

# Complete Kerberos Flow
```text
                 Domain Controller
                 ┌───────────────┐
                 │      KDC      │
                 └───────────────┘
                    ▲         │
              AS-REQ│         │AS-REP
                    │         │
                    │         ▼
                 ┌───────────────┐
                 │    Client     │
                 └───────────────┘
                    │
                    │ TGS-REQ
                    ▼
                 ┌───────────────┐
                 │      KDC      │
                 └───────────────┘
                    │
                    │ TGS-REP
                    ▼
                 Client
                    │
                    │ Service Ticket
                    ▼
                 Service
                    │
                    ▼
                Access Granted
```


# Kerberos Advantages
- **Mutual authentication** — client and server can verify each other.
- **No password transmission** — passwords aren't sent over the network.
- **Single Sign-On (SSO)** — one TGT can be used to access multiple services.
- **Delegation support**.
- **Better performance** — services can validate tickets without contacting the DC for every request.
- **Time-limited tickets** reduce the lifetime of stolen tickets.

# Kerberos Weaknesses
- Requires **time synchronization** (typically within 5 minutes).
- KDC availability is critical.
- **Pass-the-Ticket** can abuse stolen tickets.
- Compromising the **KRBTGT hash** allows Golden Ticket attacks.
- **Kerberoasting** can target service tickets.
- Requires correct **SPN/DNS configuration**.
    
---

# Credential Cache (ccache)

Kerberos tickets can be stored in **ccache files** on Linux systems.

Common location:
```text
/tmp/krb5cc_<UID>
```

The `KRB5CCNAME` variable specifies which cache to use.

### View Tickets
```bash
klist
```

Displays the Kerberos tickets stored in the current cache.

> If an attacker obtains a valid ccache containing a user's tickets, they may be able to authenticate as that user without knowing the password (**Pass-the-Ticket / Pass-the-ccache**).

---

# Kerberos with Impacket

## 1. Add Hostname to `/etc/hosts`

Kerberos service authentication uses Service Principal Names (SPNs), which identify services such as `cifs/SERVER1.thm.loc`. Therefore, using the correct hostname is important when requesting a service ticket.

Kerberos relies on **hostnames/SPNs**, so use the hostname rather than the IP when authenticating.
```bash
echo "192.168.11.51 SERVER1.thm.loc" >> /etc/hosts
```
Adds a hostname-to-IP mapping.

## 2. Request a TGT

Use Impacket's `getTGT.py`:
```bash
getTGT.py thm.loc/mary:'SuperLongForKerberos123!' -dc-ip 192.168.11.100
```
### Explanation
```text
thm.loc/mary:password
        │
        └── Domain + Username + Password

-dc-ip 192.168.11.100
        │
        └── Domain Controller IP
```

The tool requests a **TGT** and saves it as:
```text
mary.ccache
```

## 3. Set the ccache
```bash
export KRB5CCNAME=mary.ccache
```
Tells Kerberos tools to use `mary.ccache` for authentication.

## 4. Authenticate Using the Ticket

```bash
smbclient.py thm.loc/mary@SERVER1.thm.loc -k -no-pass -dc-ip 192.168.11.100
```

### Important options

|Option|Meaning|
|---|---|
|`-k`|Use Kerberos authentication|
|`-no-pass`|Don't ask for a password; use the ticket|
|`-dc-ip`|Specify the Domain Controller|
|`SERVER1.thm.loc`|Target hostname|
### Flow
```text
mary.ccache
     │
     │ TGT
     ▼
   KDC
     │
     │ Service Ticket
     ▼
 SERVER1
     │
     ▼
Access Granted
```

**Important:** With Kerberos, use the **hostname instead of the IP address** because Kerberos relies on **SPNs**, which are associated with service hostnames.

---

# Common AD Authentication Weaknesses

## NTLM Weaknesses
- **Weak hashing** → NTLM hashes are unsalted and fast to crack.
- **Pass-the-Hash (PtH)** → Use an NTLM hash directly without knowing the password.
- **NTLM Relay** → Relay captured NTLM authentication to another service.
- **Downgrade attacks** → Force authentication from Kerberos to NTLM.
- **No mutual authentication** → Client cannot verify the server.

## Kerberos Weaknesses
- **Kerberoasting** → Request service tickets for SPN accounts and crack them offline.
- **AS-REP Roasting** → Target users with Kerberos pre-authentication disabled.
- **Pass-the-Ticket (PtT)** → Reuse stolen Kerberos tickets.
- **Overpass-the-Hash** → Use an NTLM hash to obtain a Kerberos ticket.
- **Golden Ticket** → KRBTGT hash → forge TGTs for any user.
- **Silver Ticket** → Service account hash → forge tickets for a specific service.

## Configuration Weaknesses
- Weak passwords
- Password spraying
- Misconfigured Kerberos delegation
- Stale/unused accounts
