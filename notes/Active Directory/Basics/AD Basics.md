# Windows Domain

- A **Windows Domain** is a group of users and computers centrally managed by an organization.
- **Active Directory (AD)** is the central repository used to manage the domain.
- A **Domain Controller (DC)** is the server that runs Active Directory services.


### Main Advantages

- **Centralized Identity Management:** Manage users centrally through Active Directory.
- **Security Policy Management:** Configure and apply security policies to users and computers across the domain.

---
# Active Directory Basics — Core Objects

## Parent / Root Domain

- The lab's parent/root domain is `THM.LOC`.
- The Domain Controller is `ROOTDC.THM.LOC`.

- The **Domain Controller (DC)** runs **Active Directory Domain Services (AD DS)**.



## Active Directory Domain Services (AD DS)

**AD DS** is the core service of a Windows domain.

It acts as a **central directory/catalogue** that stores information about network objects, such as:
- Users
- Computers
- Groups
- Printers
- Shares
    
---

## Users

Users are **security principals**, meaning they can:
- Authenticate to the domain.
- Be assigned permissions to resources.
    

Users can represent:
- **People** — employees or other individuals.
- **Services** — accounts used to run services such as IIS or MSSQL.

Service users should generally have only the privileges required to run their service.

---

## Machine Accounts

When a computer joins the domain, a **machine object/account** is created in AD.

Machine accounts are also **security principals**.

They follow this naming format:
```text
COMPUTERNAME$
```

Example:
```text
ROOTDC$
```

Machine account passwords are automatically rotated and are typically **120 random characters** long.

---

## Security Groups

Security groups allow permissions to be assigned to multiple users or computers at once.

Groups can contain:
- Users
- Computers
- Other groups
    

### Important Default Groups

|Group|Purpose|
|---|---|
|**Domain Admins**|Administrative privileges across the domain|
|**Server Operators**|Can administer Domain Controllers|
|**Backup Operators**|Can access files for backup purposes regardless of normal permissions|
|**Account Operators**|Can create or modify domain accounts|
|**Domain Users**|Contains domain user accounts|
|**Domain Computers**|Contains domain computers|
|**Domain Controllers**|Contains Domain Controllers|

---

## Active Directory Users and Computers (ADUC)

**AD Users and Computers (ADUC)** is used to manage:
- Users
- Groups
- Computers

It allows administrators to create, delete, modify, and reset passwords for these objects.

---

## Organizational Units (OUs)

**Organizational Units (OUs)** are containers used to **organize** users and computers.

Example:
```text
THM
├── IT
├── Management
├── Marketing
├── R&D
└── Sales
```

OUs are mainly used to:
- Organize users/computers.
- Apply policies to groups of users/computers.

A user can belong to **only one OU at a time**.

---

## Default AD Containers

|Container|Purpose|
|---|---|
|**Builtin**|Default groups available to Windows hosts|
|**Computers**|Domain computers are placed here by default|
|**Domain Controllers**|Contains the Domain Controllers|
|**Users**|Default domain users and groups|
|**Managed Service Accounts**|Contains accounts used by services|

---

## Security Groups vs OUs

The key difference:

> **OUs → Organize objects and apply policies**  
> **Security Groups → Assign permissions**

A user can belong to **multiple security groups**, but can be in **only one OU at a time**.

---

# Windows Domain Authentication

In a Windows domain, user credentials are centrally managed by the **Domain Controllers (DCs)**.

When a user authenticates to a domain service, the authentication can use one of two protocols:

- **Kerberos** — default authentication protocol in **modern** Windows domains.
- **NetNTLM** — **legacy** challenge-response protocol kept for compatibility.
    

---

# 1. Kerberos Authentication

Kerberos uses **tickets** as proof that a user has authenticated.

The **Key Distribution Center (KDC)**, usually running on the Domain Controller, issues these tickets.

### Important Components

- **KDC** → Issues Kerberos tickets.
    
- **TGT (Ticket Granting Ticket)** → Used to request tickets for specific services.
    
- **TGS (Ticket Granting Service ticket)** → Allows access to a specific service.
    
- **SPN (Service Principal Name)** → Identifies the service being accessed.
    
- **Session Key** → Used for subsequent Kerberos requests.
    

---

## Phase 1 — Request TGT

The user sends their **username + timestamp**, encrypted using a key derived from their password, to the KDC.

```text
User                         KDC / Domain Controller
 │                                      │
 │── Username + Timestamp ─────────────>│
 │   encrypted with password-derived key│
 │                                      │
 │<──────────── TGT + Session Key ──────│
 │                                      │
```

The KDC verifies the user and returns:
- **TGT**
- **Session Key**

The TGT is encrypted using the **krbtgt account's password hash**, so the user cannot read its contents.

---

## Phase 2 — Request Service Ticket (TGS)

When the user wants to access a service, such as a:
- File share
- Website
- Database
    
the user sends the TGT to the KDC along with information identifying the requested service.

```text
User                         KDC / Domain Controller
 │                                      │
 │── TGT + Username + Timestamp ───────>│
 │   + SPN                              │
 │                                      │
 │<──────────── TGS + Service Key ──────│
 │                                      │
```

The **SPN** identifies the service and server the user wants to access.

The KDC returns a **TGS** and a **Service Session Key**.

The TGS is encrypted using a key derived from the **Service Owner's password hash**.

---

## Phase 3 — Authenticate to the Service

The user sends the TGS to the requested service.

```text
User                         Service
 │                              │
 │────── TGS ──────────────────>│
 │                              │
 │                              │ Decrypts TGS
 │                              │ using service
 │                              │ account's key
 │                              │
 │<────── Access Granted ───────│
 │                              │
```

The service uses its configured account's password hash to decrypt the TGS and validate the **Service Session Key**.

### Kerberos Flow — All Phases

```text
                  DOMAIN CONTROLLER
                 ┌──────────────────┐
                 │       KDC        │
                 └──────────────────┘
                    ▲           │
             1. TGT │           │ TGT
                    │           ▼
                 ┌─────────────────┐
                 │      USER       │
                 └─────────────────┘
                    │
             2. Request TGS
                    │
                    ├───────────────> KDC
                    │
                    │<────────────── TGS
                    │
             3. Send TGS
                    │
                    ▼
              ┌───────────┐
              │  SERVICE  │
              └───────────┘
```

### Easy way to remember

```text
Password
   │
   ▼
KDC
   │
   ▼
TGT
   │
   ▼
KDC + SPN
   │
   ▼
TGS
   │
   ▼
Service
```

**TGT = "I authenticated to the domain."**

**TGS = "I am allowed to authenticate to this specific service."**

---

# 2. NetNTLM Authentication

NetNTLM uses a **challenge-response** mechanism.

The user's password or password hash is **not sent directly over the network**.

### Phase 1 — Authentication Request

```text
Client                         Server
  │                              │
  │──── Authentication Request ─>│
  │                              │
```

### Phase 2 — Server Sends Challenge

The server generates a random challenge.

```text
Client                         Server
  │                              │
  │──── Authentication Request ─>│
  │                              │
  │<──────── Challenge ──────────│
  │                              │
```

### Phase 3 — Client Calculates Response

The client uses its password hash and the challenge to calculate a response.

```text
Client                         Server
  │                              │
  │──── Challenge Response ─────>│
  │                              │
```

### Phase 4 — Server Asks the DC

For a **domain account**, the server forwards the challenge and response to the Domain Controller.

```text
Client            Server              Domain Controller
  │                  │                       │
  │── Response ─────>│                       │
  │                  │                       │
  │                  │── Challenge + ───────>│
  │                  │   Response            │
  │                  │                       │
  │                  │<────── Result ────────│
  │                  │                       │
  │<────── Result ───│                       │
```

The Domain Controller independently calculates the expected response and compares it with the client's response.

```text
Match?
  │
  ├── YES → Authentication succeeds
  │
  └── NO  → Authentication fails
```

---

# 3. NetNTLM with a Local Account

The process is slightly different for a **local account**.

The server does not need to contact a Domain Controller because the account's password hash is stored locally in the **SAM** (Security Account Manager).

```text
Domain Account:

Client → Server → Domain Controller
                  │
                  └── Verify


Local Account:

Client → Server
           │
           └── Verify using local SAM
```

---

# Active Directory Trees, Forests & Trusts

## 1. Trees

A **Tree** is a collection of domains that share the same namespace.

Example:

```text
thm.loc
└── tbm.thm.loc
    ├── us.tbm.thm.loc
    └── uk.tbm.thm.loc
```

Each domain can have its own:
- Domain Controller
- Users
- Computers
- Resources
    
Trees allow an organization to **partition its network into independently managed domains**.

### Example

`thm.loc` → Parent domain  
`tbm.thm.loc` → Banking subdomain

The banking IT team can manage its own domain without having administrative control over the parent domain.

### Enterprise Admins

**Enterprise Admins** have administrative privileges across **all domains in the forest**.
- **Domain Admins** → Admin privileges over one domain.
- **Enterprise Admins** → Admin privileges across the entire enterprise/forest.
    

---

# 2. Forests

A **Forest** is a collection of AD trees that can use **different namespaces**.

Example:
```text
Forest
│
├── thm.loc
│   └── tbm.thm.loc
│
└── tvm.loc
```

Here:

- `thm.loc` is one tree.
- `tvm.loc` is another tree.
- Both trees are part of the same forest.

Forests allow organizations with different namespaces to integrate their Active Directory environments.

---

# 3. Trust Relationships

A **trust relationship** allows users from one domain to be authorized to access resources in another domain.

Example:
```text
tvm.loc  ───── trust ─────>  tbm.thm.loc
```

A user from `tvm.loc` can potentially access resources in `tbm.thm.loc` **if permissions are granted**

### One-Way Trust

If **Domain A trusts Domain B**:
```text
Domain A  ── trusts ──>  Domain B
```

Users from **Domain B** can potentially be authorized to access resources in **Domain A**.

> **Trust direction ≠ access direction.**

### Two-Way Trust

Both domains trust each other:
```text
Domain A  <──────>  Domain B
```

Users from either domain can potentially be authorized to access resources in the other domain.

Domains joined under a tree or forest normally have **two-way trust relationships by default**.

### Important

A trust **does not automatically give users access to all resources**.

It only allows users from one domain to potentially be authorized in another domain. **Permissions still determine what they can access.**

---

# Active Directory Delegation

## Advanced Features

**Advanced Features** in **Active Directory Users and Computers (ADUC)** displays additional AD containers and management options.

Enable it from:
```text
View → Advanced Features
```

---

## Delegation

**Delegation** allows administrators to give specific users or groups **limited administrative permissions over an Organizational Unit (OU)** without giving them Domain Administrator privileges.

### Example

IT support may need to reset passwords for users but should not have full domain administration privileges.

```text
Tech Support Group
        │
        │ delegated permission
        ▼
   Bankers OU
        │
        ▼
Reset user passwords
```

This follows the principle of **delegating only the permissions required for a specific task**.

### Key Points
- Delegation is applied to an **OU**.
- Permissions can be assigned to a **user or group**.
- Delegated users do **not** need to be Domain Admins.
- Delegation can provide very granular control over specific AD objects and tasks.

---
# Domain Computers

When a computer joins an Active Directory domain, a **computer object** is created in AD.

By default:
- Domain-joined computers are placed in the **Computers** container.
- Domain Controllers are placed in the **Domain Controllers** OU.
    
However, keeping all computers in one container is not ideal because different types of machines usually require different policies.

## Main Types of Domain Computers

### Workstations
- Used by regular users for daily work and browsing.
- Should **not** normally have privileged users logged in.
    
### Servers
- Provide services to users or other servers.
- Usually require different security policies from workstations.

### Domain Controllers
- Manage the Active Directory domain.
- Are among the **most sensitive systems** in the network.
- Store password hashes for domain accounts.
    
## Organizing Computers with OUs

A common structure is:
```text
THM.LOC
│
├── Workstations
│   ├── Laptop1
│   └── Laptop2
│
├── Servers
│   ├── Server1
│   └── Server2
│
└── Domain Controllers
    └── DC1
```

Separating computers into different OUs makes it easier to **apply different policies** to workstations, servers, and other systems.

---

# Group Policy Objects (GPOs)

**Group Policy Objects (GPOs)** are collections of settings used to apply **configurations and security policies** to users and computers in Active Directory.

GPOs allow administrators to apply different policies to different **OUs**.

```text
GPO
 │
 ├── User Configuration
 │
 └── Computer Configuration
```

## GPO Scope

To use a GPO:
1. Create the GPO under **Group Policy Objects**.
2. Link it to an OU or the domain.

A GPO applies to the linked OU **and its sub-OUs**.
```text
Domain
│
└── Bankers OU
    └── Users
```

If a GPO is linked to the **domain**, it can also affect the Bankers OU.

### Default GPOs

- **Default Domain Policy** → Linked to the entire domain.
- **Default Domain Controllers Policy** → Linked to the Domain Controllers OU.
    

---

## Security Filtering

**Security Filtering** controls which users or computers receive a GPO.

By default, GPOs apply to:

**Authenticated Users** → includes authenticated users and computers.

---

## GPO Configuration

GPOs contain two main configuration sections:
```text
Computer Configuration
User Configuration
```

- **Computer Configuration** → Settings for computers.
- **User Configuration** → Settings for users.
    
---

# GPO Example: Local Administrators

A GPO can be used to centrally configure the local Administrators group on machines in an OU.

Example:
```text
Servers OU
    │
    └── GPO
         │
         └── Product Admins
                  ↓
          Local Administrators
```

This allows the **Product Admins** group to become local administrators on servers in the targeted OU.

---

# SYSVOL

**SYSVOL** is a network share on Domain Controllers used to distribute GPO-related files across the domain.

It is stored by default under:
```text
C:\Windows\SYSVOL\sysvol\
```

GPO changes may take time to propagate to computers.

To force a computer to update its policies:
```powershell
gpupdate /force
```

### Key Concept

> **GPO = Centralized configuration and security policies for users and computers.**

> **OU = Determines where the GPO applies.**

> **Security Filtering = Determines who/what receives the GPO.**

> **SYSVOL = Distributes GPOs across the domain.

---

# Forest Trusts & Resource Sharing

## Forest Trust

A **Forest Trust** connects two separate AD forests and allows users from one forest to access resources in another.

Example:

```text
thm.loc Forest  <──────────────>  tvm.loc Forest
                  Two-way Trust
```

A **two-way trust** allows authentication/authorization to work in both directions, subject to permissions.

### Forest-Wide Authentication

When establishing a forest trust, **Forest-wide authentication** can be configured to allow authentication across the trusted forests.

---

# Cross-Forest Access

A user from one domain can be added to a security group in another trusted domain.

Example:
```text
THM\Claire
     │
     ▼
TVM\Server Admins
     │
     ▼
Server2
```

`THM\Claire` remains managed by the **THM.LOC** domain, but membership in the **TVM** security group gives her permissions to resources in the TVM domain.

---

# Trust Between Parent & Child Domains

If:
```text
thm.loc
└── tbm.thm.loc
```

are domains in the same forest, there is an **intrinsic two-way trust** between the parent and child domains.

If the `thm.loc` forest also has a two-way trust with `tvm.loc`:

```text
          Two-way trust
thm.loc  <──────────────>  tvm.loc
   │
   │ parent-child trust
   ▼
tbm.thm.loc
```

This allows trust to extend between `tvm.loc` and `tbm.thm.loc`.

---

# Cross-Domain Group Membership

A user from another trusted domain can be added to a security group by specifying the user's domain.

Example:
```text
tvm\alice.king
```

can be added to:
```text
tbm.thm.loc\Product Admins
```

The user is still managed by `tvm.loc`; only the **group membership and resulting permissions** come from `tbm.thm.loc`.

# Key Concept

AD trust relationships can create **complex cross-domain attack and access paths**.

Example:

```text
tvm.loc
  │
  │ alice.king
  ▼
Product Admins
  │
  │ GPO grants local admin
  ▼
Servers OU
  │
  ▼
Server1
```

So a user managed in one forest can potentially gain administrative access to a machine in another domain through:

**Trust → Group Membership → GPO → Local Administrator privileges**.


