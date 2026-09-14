## 1. Access Control in Active Directory

Active Directory controls **who can access or modify objects** using an access-control system.

Objects include:
- Users
- Groups
- Computers
- OUs
- Domains
- GPOs
- Files/folders
- Other AD objects
    
The main concepts are:
```text
User / Group
     ↓
Security Token
     ↓
ACL
     ↓
ACE
     ↓
Allow / Deny Permission
```

---

# 2. ACL — Access Control List

**ACL = Access Control List**

An ACL is a list that defines **who can access an object and what they can do**.

There are two important types:
```text
ACL
├── DACL → Permissions
└── SACL → Auditing
```

### Example

Imagine a user object:
```text
User: John
```

Its ACL might contain:
```text
Domain Admins → Full Control
Helpdesk      → Reset Password
John          → Read
Everyone      → Read
```

The ACL determines what each security principal can do.

---

# 3. ACE — Access Control Entry

**ACE = Access Control Entry**

An ACE is **one individual rule inside an ACL**.

Example:
```text
DACL

ACE 1:
Domain Admins → Allow → Full Control

ACE 2:
Helpdesk → Allow → Reset Password

ACE 3:
Bob → Deny → Write
```

Think:
```text
ACL = collection of rules
ACE = one rule
```

### ACE contains things such as:
- Security principal
- Allow/Deny
- Permission
- Object/attribute
- Inheritance information

---

# 4. DACL — Discretionary Access Control List

**DACL = Discretionary Access Control List**

The DACL controls **who is allowed or denied access** to an object.

Example:
```text
User Object
     │
     └── DACL
          ├── Domain Admins → Allow Full Control
          ├── Helpdesk → Allow Reset Password
          └── User → Allow Read
```

If an object's DACL doesn't grant you a required permission, you normally cannot perform that action.

### Important

DACL = **authorization**

It answers:

> "Can this user perform this action?"

---

# 5. SACL — System Access Control List

**SACL = System Access Control List**

SACL controls **auditing**.

Instead of determining whether someone can access something, it specifies **which access attempts should be logged**.

Example:
```text
SACL

Domain Admins → Audit → Successful Modification
Everyone      → Audit → Failed Access
```

When the specified event occurs, Windows can generate security audit events.

### Remember
```text
DACL → Allow / Deny
SACL → Audit / Log
```

---

# 6. ACL vs ACE vs DACL vs SACL

Easy way to remember:

|Term|Meaning|
|---|---|
|ACL|Access Control List|
|ACE|One entry/rule in an ACL|
|DACL|ACL containing permission rules|
|SACL|ACL containing auditing rules|

Think of it like:
```text
ACL
│
├── DACL
│    ├── ACE
│    ├── ACE
│    └── ACE
│
└── SACL
     ├── ACE
     └── ACE
```

---

# 7. Common AD Permissions

Some important permissions you'll encounter during AD enumeration:

### Generic permissions
```text
GenericAll
GenericWrite
GenericRead
GenericExecute
```

### Object permissions
```text
CreateChild
DeleteChild
DeleteTree
ReadControl
WriteDacl
WriteOwner
WriteProperty
```

### Extended rights

Examples:
```text
ForceChangePassword
AddMember
DCSync
Reset Password
Write SPN
```

These permissions become particularly interesting during **AD privilege escalation**.

---

# 8. GenericAll

### `GenericAll`

Means essentially:

> **Full control over the object**

Depending on the object, this can allow actions such as:

- Modify attributes
- Change permissions
- Change ownership
- Delete object
- Add/remove group membership
- Reset passwords
    

Example:
```text
User A
   │
   └── GenericAll → User B
```

User A has extensive control over User B.

This is a **high-value BloodHound edge**.

---

# 9. GenericWrite

### `GenericWrite`

Allows writing/modifying properties of an object.

Example:
```text
Attacker
   │
   └── GenericWrite
          ↓
       User B
```

Depending on the object and writable attributes, this can potentially lead to privilege escalation.

---

# 10. WriteDACL

### `WriteDACL`

Allows modifying the object's **DACL**.

This is extremely important.

For example:
```text
Attacker
   │
   └── WriteDACL
          ↓
       User B
```

The attacker may be able to modify User B's permissions and grant themselves additional rights.

Conceptually:
```text
WriteDACL
    ↓
Modify DACL
    ↓
Grant yourself permission
    ↓
Control object
```

---

# 11. WriteOwner

### `WriteOwner`

Allows changing the **owner** of an object.

Ownership is important because the owner can generally modify the object's permissions.

Conceptually:
```text
WriteOwner
    ↓
Become owner
    ↓
Modify permissions
    ↓
Gain control
```

---

# 12. ForceChangePassword

This permission allows a principal to **reset another user's password without knowing the old password**, assuming the necessary rights and conditions are present.

Example:
```text
Helpdesk
   │
   └── ForceChangePassword
             ↓
          User B
```

This can become dangerous if User B is privileged.

---

# 13. DCSync Rights

DCSync is particularly important in AD security.

Certain replication permissions allow an account to request directory replication data.

Important rights include:
```text
DS-Replication-Get-Changes
DS-Replication-Get-Changes-All
```

If an attacker obtains appropriate replication privileges over the domain, they may be able to abuse them to retrieve credential material from the domain.

This is why **DCSync-capable permissions should be tightly controlled**.

---

# 14. Inheritance

AD permissions can be inherited.

For example:
```text
OU: IT
 │
 ├── User A
 ├── User B
 └── Computer A
```

A permission applied to the OU may be inherited by objects underneath it.

Example:
```text
OU
 │
 └── Allow Group X → Read
          ↓
     inherited by
          ↓
     Users inside OU
```

When analyzing AD permissions, always consider:
```text
Explicit permission
        +
Inherited permission
        ↓
Effective access
```

---

# 15. Security Principals

Permissions are assigned to **security principals**.

Common security principals:
- Users
- Groups
- Computers
- Service accounts
- Managed service accounts
    
Example:
```text
Domain Admins
      ↓
Permission
      ↓
AD Object
```

---

# 16. Important AD Groups

Some built-in groups are especially important during AD security assessments.

## Domain Admins
```text
Domain Admins
      ↓
Administrative control over the domain
```

Members of Domain Admins have extensive privileges throughout the domain.

From an attacker perspective:
```text
Low Privileged User
       ↓
Privilege Escalation
       ↓
Domain Admin
```

is a major objective in many AD attack scenarios.

---

# 17. Enterprise Admins

**Enterprise Admins** is a forest-level privileged group.

Think:

```text
Domain Admin
     ↓
Domain-level privilege

Enterprise Admin
     ↓
Forest-level privilege
```

Enterprise Admins has privileges across the forest, particularly for managing domains and forest-wide configuration.

---

# 18. Forest Root Domain

A **forest** can contain multiple domains.

Example:
```text
Forest
│
├── example.local       ← Forest Root Domain
│
├── sales.example.local
│
└── dev.example.local
```

The first domain created in the forest is the **forest root domain**.

The forest root is important because forest-wide administrative relationships and groups are associated with it.

---

# 19. Domain vs Forest

### Domain

A logical security/administrative boundary containing:
- Users
- Computers
- Groups
- OUs
- Domain Controllers
- Policies

Example:
```text
corp.local
```

### Forest

A collection of one or more AD domains that share a common AD structure/trust framework.

Example:
```text
Forest
│
├── corp.local
├── eu.corp.local
└── dev.corp.local
```

---

# 20. Domain Admin vs Enterprise Admin

| |Domain Admin|Enterprise Admin|
|---|---|---|
|Scope|Domain|Forest|
|Main purpose|Domain administration|Forest-wide administration|
|Example|`CORP\Domain Admins`|`CORP\Enterprise Admins`|
|Privilege level|Very high|Extremely high|

Easy memory:
```text
Domain Admin
    ↓
One domain

Enterprise Admin
    ↓
Entire forest
```

---

# 21. Other Important Groups

### Administrators
Local/domain administrative group depending on context.
### Account Operators
Can perform certain account-management operations.
### Backup Operators
Have privileges related to backup/restore operations and can be security-sensitive.
### Server Operators
Can perform administrative operations on domain controllers in certain configurations.
### Print Operators
Historically provides printer-management privileges and can be security-sensitive.
### Remote Desktop Users
Members can log on through RDP where configured.
### Domain Users
Default group containing normal domain user accounts.
### Domain Computers
Contains domain-joined computer accounts by default.

---

# 22. Built-in vs Delegated Permissions

Not every powerful account needs to be a Domain Admin.

Organizations commonly use **delegation**.

Example:
```text
Helpdesk
   │
   ├── Reset user passwords
   ├── Unlock accounts
   └── Read user information
```

This is safer than:
```text
Helpdesk
   ↓
Domain Admin
```

From a pentesting perspective, delegated permissions are extremely important because **privilege escalation often happens through unexpected permissions rather than obvious administrator membership**.

---

# 23. The Important Attack Path Concept

One of the most important ideas to understand with AD ACLs:
```text
Low-privileged user
       ↓
ACL permission
       ↓
Control another object
       ↓
Control privileged object
       ↓
Privilege escalation
```

Example:
```text
User A
  │
  │ GenericAll
  ↓
User B
  │
  │ MemberOf
  ↓
Domain Admins
```

User A may not be a Domain Admin directly.

But the **relationship between objects** can create an attack path.

This is exactly why tools such as **BloodHound** are useful.

---

# 24. BloodHound ACL Edges to Remember

When studying BloodHound, pay special attention to:
```text
GenericAll
GenericWrite
WriteDacl
WriteOwner
ForceChangePassword
AddMember
AddSelf
WriteSPN
Owns
AdminTo
DCSync
```

Think of BloodHound as showing:
```text
WHO
 ↓
HAS WHAT RIGHT
 ↓
OVER WHICH OBJECT
 ↓
WHICH LEADS TO WHAT
```

---

# Quick Cheat Sheet

```text
ACL
└── Access Control List
      │
      ├── DACL
      │     └── Who can access/do what
      │
      └── SACL
            └── What access should be audited

ACE
└── Individual rule inside ACL
```

### Permissions

```text
GenericAll       → Full control
GenericWrite     → Write properties
WriteDACL        → Modify permissions
WriteOwner       → Change owner
ForceChangePassword → Reset password
AddMember        → Add users to groups
WriteSPN         → Modify SPN
DCSync rights    → Directory replication privileges
```

### Privilege hierarchy

```text
Normal User
    ↓
Privileged User
    ↓
Domain Admin
    ↓
Enterprise Admin
    ↓
Forest-wide control
```

### Most important distinction

```text
DACL → Authorization
SACL → Auditing
ACE  → Individual rule
ACL  → Collection/list
```

**Pentesting mindset:** Don't just ask _"Is this user an administrator?"_ Ask **"What objects can this user control, what permissions do they have, and what privileged objects can those permissions eventually reach?"**