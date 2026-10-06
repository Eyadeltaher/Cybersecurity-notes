
**LDAP** (Lightweight Directory Access Protocol) provides access to directory services: clients can search, read, add, modify, and delete directory entries when access controls permit it. Common deployments store identities, groups, devices, and service configuration.

## AD / LDAP Enumeration

**Purpose:** Query Active Directory through **LDAP** to discover information about the domain, such as users, groups, OUs, computers, and domain details.

### Tool → `NetExec (nxc)`

#### 1. Enumerate Groups
```bash
nxc ldap <DC-IP> -d <DOMAIN> \
-u <USERNAME> \
-H '<NTLM_HASH>' \
--groups
```

**Example:**
```bash
nxc ldap 10.113.130.110 -d spookysec.local \
-u Administrator \
-H '0e0363213e37b94221497260b0bcb4fc' \
--groups
```

**What it does:**  
Queries LDAP and lists the groups in the Active Directory domain and their members.

**Why does it work?**
Active Directory stores users, groups, computers, and other objects in an **LDAP directory**. An authenticated account can query objects that it has permission to read.

###  No credentials

You can attempt **anonymous LDAP/SMB enumeration**:
```bash
nxc ldap <DC-IP> -u '' -p '' --users
```

or:
```bash
nxc smb <DC-IP> -u '' -p '' --users
```

You may be able to retrieve things like domain information, users, or other directory data.

**Why?**  
Some AD environments allow **anonymous/unauthenticated queries** or have permissive legacy settings. But modern AD configurations generally restrict anonymous LDAP enumeration.

### Username + Password

This is the normal authenticated approach:
```bash
nxc ldap <DC-IP> \
-d spookysec.local \
-u james \
-p 'Password123!'
```

If you have valid credentials to login into the LDAP server, you can dump all the information about the Domain Admin using:
```bash
ldapdomaindump -u '<domain>\<username>' -p '<password>' 192.168.56.10 -o ldapoutput   
```

> **LDAP enumeration can be anonymous if the AD configuration permits it; otherwise, valid credentials are normally required. A username alone does not authenticate you, but it can be used for Kerberos user enumeration.**


---

### 2. Enumerate Organizational Units (OUs)

```bash
nxc ldap <DC-IP> -d <DOMAIN> \
-u <USERNAME> \
-H '<NTLM_HASH>' \
--query '(objectClass=organizationalUnit)' \
'distinguishedName'
```

**Example:**
```bash
nxc ldap 10.113.130.110 -d spookysec.local \
-u Administrator \
-H '0e0363213e37b94221497260b0bcb4fc' \
--query '(objectClass=organizationalUnit)' 'distinguishedName'
```

Example output:
```text
OU=Domain Controllers,DC=spookysec,DC=local
OU=Staff,DC=spookysec,DC=local
OU=Administrator,DC=spookysec,DC=local
```

**What it does:**  
Finds all **Organizational Units** in the domain.

**Why does it work?**

OUs are LDAP objects with:
```text
objectClass=organizationalUnit
```

The LDAP filter searches for objects matching that class.

---

### 3. Enumerate Domain Information

```bash
nxc ldap <DC-IP> -d <DOMAIN> \
-u <USERNAME> \
-H '<NTLM_HASH>' \
--query '(objectClass=domain)' \
'distinguishedName;name;objectSid'
```

**Example:**
```bash
nxc ldap 10.113.130.110 -d spookysec.local \
-u Administrator \
-H '0e0363213e37b94221497260b0bcb4fc' \
--query '(objectClass=domain)' \
'distinguishedName;name;objectSid'
```

This can retrieve:
```text
distinguishedName
name
objectSid
```

### Important LDAP Concepts

```text
LDAP
 │
 └── Active Directory Directory
       │
       ├── Users
       ├── Groups
       ├── Computers
       ├── OUs
       ├── GPO-related objects
       └── Domain information
```

### LDAP Query Structure

The important part is:
```text
(objectClass=organizationalUnit)
```

This is an **LDAP filter**.

For example:

```text
(objectClass=user)
```
→ Find user objects

```text
(objectClass=group)
```
→ Find group objects

```text
(objectClass=computer)
```
→ Find computer objects

```text
(objectClass=organizationalUnit)
```
→ Find OUs

### Key Point

> **LDAP enumeration is about querying the AD database for objects and their attributes.**

Unlike **SMB enumeration**, which focuses heavily on shares, SMB/RPC information, and Windows services, **LDAP enumeration gives you a structured view of the Active Directory directory itself.**


---

Here’s a useful **LDAP filter cheat sheet** for your AD notes. The general format is:

```text
(attribute=value)
```

With `nxc`:
```bash
nxc ldap <DC-IP> -d <DOMAIN> -u <USER> -H '<HASH>' \
--query '<FILTER>' '<ATTRIBUTES>'
```

## Common LDAP Filters

### Users

**All users**
```text
(objectClass=user)
```

**Users with a username**
```text
(sAMAccountName=*)
```

**Specific user**
```text
(sAMAccountName=james)
```

**Users whose name starts with `admin`**
```text
(sAMAccountName=admin*)
```

**Users with a description**
```text
(description=*)
```

**Users with a specific description**
```text
(description=*password*)
```

---

### Computers

**All computers**
```text
(objectClass=computer)
```

**Computers with a hostname**
```text
(dNSHostName=*)
```

**Domain Controllers**
```text
(userAccountControl:1.2.840.113556.1.4.803:=8192)
```

`8192` = `SERVER_TRUST_ACCOUNT` / Domain Controller flag.

---

### Groups

**All groups**
```text
(objectClass=group)
```

**Specific group**
```text
(cn=Domain Admins)
```

**Groups with members**
```text
(member=*)
```

**Groups containing a specific user**
```text
(member=CN=Administrator,CN=Users,DC=spookysec,DC=local)
```

---

### Organizational Units

**All OUs**
```text
(objectClass=organizationalUnit)
```

**OUs with a specific name**
```text
(ou=Staff)
```

---

## Useful Account Filters

### Disabled accounts
```text
(userAccountControl:1.2.840.113556.1.4.803:=2)
```
`2` = `ACCOUNTDISABLE`

### Accounts with Kerberos pre-authentication disabled
```text
(userAccountControl:1.2.840.113556.1.4.803:=4194304)
```

`4194304` = `DONT_REQ_PREAUTH`

This is particularly relevant for **AS-REP Roasting**.

### Password never expires

```text
(userAccountControl:1.2.840.113556.1.4.803:=65536)
```
`65536` = `DONT_EXPIRE_PASSWORD`

## Combining Filters

### AND `&`

Both conditions must be true:
```text
(&(objectClass=user)(sAMAccountName=*))
```

Example:
```text
(&(objectClass=user)(description=*password*))
```

→ Users whose description contains `password`.

### OR `|`

At least one condition must be true:
```text
(|(sAMAccountName=admin)(sAMAccountName=administrator))
```
→ Finds either `admin` or `administrator`.

### NOT `!`

Exclude a condition:d
```text
(&(objectClass=user)(!(sAMAccountName=Guest)))
```
→ Users except `Guest`.


example:
```bash
nxc ldap <DC-IP> -d spookysec.local \
-u Administrator -H '<HASH>' \
--query '(&(objectClass=user)(description=*))' \
'sAMAccountName;description'
```

These are especially useful for connecting **LDAP enumeration → Kerberoasting → AS-REP Roasting → AD privilege enumeration**.