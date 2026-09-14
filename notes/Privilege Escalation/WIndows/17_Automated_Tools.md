
Automated enumeration tools quickly search for common **Privilege Escalation** vectors.

```text
Automated Enumeration
        ↓
Find suspicious permissions / services / patches / credentials
        ↓
Manually verify
        ↓
Exploit the discovered vector
```

 **Important:** Automated tools can miss vulnerabilities. Always understand and perform manual enumeration too.

---

### 1. WinPEAS

**WinPEAS** = Windows Privilege Escalation Awesome Scripts.

Enumerates:
- Users/groups
- Privileges
- Services
- Scheduled tasks
- Registry
- Credentials
- File permissions
- Installed software
- Missing patches
- Other common PrivEsc vectors
    
Run:
```cmd
winpeas.exe
```

Save output to a file:
```cmd
winpeas.exe > outputfile.txt
```
→ Recommended because WinPEAS output can be very long.

**Key idea:**  
`WinPEAS → automated local enumeration → identify possible PrivEsc paths → manually verify → exploit`

---

### 2. PrivescCheck

**PrivescCheck** is a PowerShell-based alternative to WinPEAS.

Unlike WinPEAS, it doesn't require executing a compiled binary.

If PowerShell execution policy blocks the script:
```powershell
Set-ExecutionPolicy Bypass -Scope process -Force
```
- `Bypass` → temporarily bypass execution-policy restrictions.
- `-Scope process` → affects only the current PowerShell process.
- `-Force` → don't ask for confirmation.
    

Load the script:
```powershell
. .\PrivescCheck.ps1
```

Then run:
```powershell
Invoke-PrivescCheck
```

Attack/usage chain:
```text
Get PrivescCheck
      ↓
Bypass execution policy if required
      ↓
Load script
      ↓
Invoke-PrivescCheck
      ↓
Review PrivEsc findings
```

---

### 3. WES-NG — Windows Exploit Suggester

**WES-NG** runs on your **attacking machine** rather than the Windows target.

Useful when uploading/running enumeration tools on the target could trigger antivirus.

Attack chain:
```text
Windows target
    ↓
systeminfo
    ↓
Save output
    ↓
Transfer systeminfo.txt to Kali
    ↓
WES-NG compares OS/patches against exploit database
    ↓
Potential missing patches / exploits
```

On the Windows target:
```cmd
systeminfo > systeminfo.txt
```

→ Collects Windows version, build, installed updates and system information.

On Kali:
```bash
wes.py --update
```

→ Updates WES-NG's vulnerability database.

Then:
```bash
wes.py systeminfo.txt
```

→ Checks the target's system information against known vulnerabilities/missing patches.

**Important:** WES-NG suggests potential exploits; manually verify that the vulnerability applies to the target.

---

### 4. Metasploit — Local Exploit Suggester

If you already have a **Meterpreter** session:
```text
msfconsole
```

Then:
```text
use multi/recon/local_exploit_suggester
```

Select your Meterpreter session:
```text
set SESSION <session_id>
run
```

→ Enumerates the target and suggests local exploits that may allow privilege escalation.

Attack chain:
```text
Meterpreter session
        ↓
local_exploit_suggester
        ↓
Potential local exploits
        ↓
Select applicable exploit
        ↓
SYSTEM / elevated privileges
```

---
### Quick Comparison

|Tool|Runs on|Main purpose|
|---|---|---|
|**WinPEAS**|Windows|Broad PrivEsc enumeration|
|**PrivescCheck**|Windows|PowerShell PrivEsc enumeration|
|**WES-NG**|Kali/AttackBox|Find missing patches + possible exploits|
|**Metasploit LPE Suggester**|Via Meterpreter|Suggest local exploits|


**Golden rule:** `Automated tools identify possibilities; manual enumeration confirms them.`