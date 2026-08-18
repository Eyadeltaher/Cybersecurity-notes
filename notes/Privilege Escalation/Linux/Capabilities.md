### What are Linux Capabilities?

Normally, Linux permissions are roughly:
```text
normal user → limited privileges
root        → almost everything
```

Capabilities split some of root's powers into smaller privileges.

For example:
```text
CAP_NET_RAW
```

allows certain raw network operations without giving the process full root privileges.

This is useful for **least privilege**, but if a powerful capability is assigned to the wrong binary, it can become a privilege-escalation path.

---

### Capabilities vs SUID

SUID:
```text
-rwsr-xr-x
    ↑
 SUID
```
means:
> Execute this program with the owner's privileges.


Capabilities are more specific:
```text
/usr/bin/somebinary cap_setuid=ep
```
means:
> This binary has the ability to change its UID.

So:
```text
SUID → potentially gives the program the owner's privileges

Capability → gives the program specific privileged powers
```

---

### Important Capabilities

You don't need to memorize every capability. These are especially useful during PrivEsc enumeration:

| Capability            | Simple meaning                          |
| --------------------- | --------------------------------------- |
| `CAP_SETUID`          | Change process UID                      |
| `CAP_SETGID`          | Change process GID                      |
| `CAP_DAC_OVERRIDE`    | Bypass many file permission checks      |
| `CAP_DAC_READ_SEARCH` | Bypass file read/search restrictions    |
| `CAP_CHOWN`           | Change file ownership                   |
| `CAP_NET_RAW`         | Raw network operations                  |
| `CAP_NET_ADMIN`       | Network configuration                   |
| `CAP_SYS_ADMIN`       | Very broad system administration powers |

**`CAP_SETUID`, `CAP_DAC_OVERRIDE`, `CAP_DAC_READ_SEARCH`, and `CAP_SYS_ADMIN` deserve particular attention during PrivEsc.**

---

### Finding Capabilities

The most important command:
```bash
getcap -r / 2>/dev/null
```

This recursively searches the filesystem for files with capabilities.

Example:
```text
/usr/bin/ping cap_net_raw=ep
/usr/bin/python3 cap_setuid=ep
```

The interesting finding is:
```text
/usr/bin/python3 cap_setuid=ep
```

because Python has `CAP_SETUID`.

---

### Understanding `=ep`

Example:
```text
/usr/bin/python3 cap_setuid=ep
```

The important part is:
```text
cap_setuid=ep
```

`e` = **Effective**
The capability is active when the program runs.

`p` = **Permitted**
The capability is available to the process.

For PrivEsc enumeration, seeing:
```text
cap_setuid=ep
```
is particularly interesting.

---

### Check a Specific Binary

You can check a binary directly:
```bash
getcap /usr/bin/python3
```

Expected:
```text
/usr/bin/python3 cap_setuid=ep
```

If there is no output:
then that binary has no file capability.

---

### `capsh --print`

Another useful command:
```bash
capsh --print
```

Example:
```text
Current: cap_net_raw,cap_net_admin=eip
Bounding set =cap_chown,cap_dac_override,cap_setuid,...
```
This shows capabilities associated with the **current process/environment**, not simply files on disk.

For file-based PrivEsc hunting, `getcap -r /` is usually more important.

**Why is `capsh` useful?**
Suppose you're already inside a shell:
```bash
id
```

Output: `uid=1000(eyad) gid=1000(eyad) groups=1000(eyad)`
You appear to be a normal user.

But:
```bash
capsh --print
```

might show: `Current: cap_net_raw=eip`
That tells you: 
>Although I'm not root, my current process has an additional privileged capability.

**What is `Bounding set`?**
Think of the **bounding set as a limit**:
> "These are the capabilities this process could potentially retain/use; capabilities outside this set are restricted."

---
### Check Process Capabilities

You can inspect a running process:

```bash
cat /proc/$$/status | grep Cap
```

Example:
```text
CapInh:  0000000000000000
CapPrm:  0000000000000000
CapEff:  0000000000000000
CapBnd:  000001ffffffffff
CapAmb:  0000000000000000
```

These values are hexadecimal capability masks.

If you want an easier human-readable view, use:
```bash
capsh --print
```

---

### `CAP_SETUID`
This is one of the most interesting capabilities.

Normally:
```bash
id
```

might show:
```text
uid=1000(eyad) gid=1000(eyad) groups=1000(eyad)
```

A binary with:
```text
cap_setuid=ep
```

may be able to change its process UID.

That's why something like:
```text
/usr/bin/python3 cap_setuid=ep
```

is highly suspicious.

The important chain is:
```text
Low-privileged user
        ↓
Can execute capability-enabled binary
        ↓
Binary has CAP_SETUID
        ↓
Can potentially change UID
        ↓
Potential root-level execution
```

u can demonstrate the capability by starting Python and changing the **Python process's UID** to 0:
```bash
/usr/bin/python3 -c 'import os; os.setuid(0); os.system("/bin/sh")'
```
Then: `id` --> `uid=0(root) gid=1000(eyad) groups=1000(eyad)`

---

### `CAP_DAC_OVERRIDE`

`DAC` means **Discretionary Access Control** — the normal Linux file permissions.

`CAP_DAC_OVERRIDE` allows a process to bypass many normal file permission checks.

For example, a process with this capability may be able to access files that a normal user cannot.

Finding:
```text
/usr/bin/example cap_dac_override=ep
```
should therefore be investigated.

---

### `CAP_DAC_READ_SEARCH`

This is related to reading/searching files and directories despite normal permission restrictions.

For example:
```text
/usr/bin/example cap_dac_read_search=ep
```

could allow the binary to access files that the current user normally couldn't read.

During enumeration, this can be interesting because it may allow access to sensitive files.

---

### `CAP_SYS_ADMIN`

This capability is extremely broad.

Finding:
```text
/usr/bin/example cap_sys_admin=ep
```

should immediately make you investigate the binary.

`CAP_SYS_ADMIN` covers many system-level operations and is often considered one of the most powerful capabilities.

Don't assume:
```text
CAP_SYS_ADMIN = instant root
```

Instead:
```text
CAP_SYS_ADMIN
      ↓
Very powerful privilege
      ↓
Investigate what the specific binary can do
```

---

### Use GTFOBins

Once you find a capability-enabled binary, search for that binary on **GTFOBins** and specifically look at its **Capabilities** section.

For example:
```text
/usr/bin/python3 cap_setuid=ep
```

Your workflow becomes:

```text
getcap -r /
      ↓
Find suspicious binary
      ↓
Identify capability
      ↓
Check GTFOBins
      ↓
Check the Capabilities technique
      ↓
Test safely in your lab
```

The capability alone isn't enough—you need to understand **how that particular binary can use it**.

---
### Find Capabilities Quickly

For a PrivEsc enumeration checklist:

```bash
# Find all file capabilities
getcap -r / 2>/dev/null

# Check a specific binary
getcap /usr/bin/python3

# Show current process capabilities
capsh --print

# Check capability fields of current process
grep Cap /proc/$$/status
```

---

### What Should You Look For?

When you get:
```text
getcap -r / 2>/dev/null
```

don't treat every result as a vulnerability.

For example:
```text
/usr/bin/ping cap_net_raw=ep
```

is generally expected.

But:
```text
/usr/bin/python3 cap_setuid=ep
```
is much more interesting.

Think:
```text
Capability
    ↓
What does it allow?
    ↓
Which binary has it?
    ↓
Can I execute that binary?
    ↓
Can the capability affect my privileges?
    ↓
Check GTFOBins
```

---

### Capability PrivEsc Checklist

```text
[ ] Run getcap -r / 2>/dev/null
[ ] Identify unusual binaries
[ ] Identify the capability
[ ] Understand what the capability allows
[ ] Confirm I can execute the binary
[ ] Check GTFOBins
[ ] Check the Capabilities technique
```

### The main thing to remember
```text
SUID:
"Run this program with the owner's privileges."

Capabilities:
"Give this program specific powerful abilities."
```

For Linux PrivEsc, the key command to remember is:

```bash
getcap -r / 2>/dev/null
```

Then ask:

> **"Is there a capability-enabled binary that gives me a powerful ability I shouldn't have?"**