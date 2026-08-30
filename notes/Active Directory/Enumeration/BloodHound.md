### What is BloodHound?

**BloodHound** is an Active Directory graph-analysis tool. It maps relationships between AD objects to find **privilege escalation paths** and possible routes to **Domain Admin**.

**Attack/technique to associate with BloodHound:** **AD Relationship / Attack Path Enumeration**. BloodHound itself isn't an attack; it is primarily an **enumeration and attack-path analysis tool**.

It helps answer:
```text
Who can control what?
        ↓
What permissions exist?
        ↓
What attack path leads to Domain Admin?
```

### Tools

|Tool|Purpose|
|---|---|
|`bloodhound-python`|Collects AD information|
|`BloodHound`|Visualizes and analyzes the collected data|
|`Neo4j` / PostgreSQL|Backend databases used by BloodHound CE|
|`SharpHound`|Windows-based BloodHound collector|

---

# 1. Start BloodHound

```bash
cd ~/BloodHound
docker compose up -d
```

Open the web interface:
```bash
xdg-open http://localhost:8080/ui/login
```

Check that the containers are running:
```bash
docker compose ps
```

---

# 2. Collect AD Data

### Tool: `bloodhound-python`

Collects information from Active Directory and produces files that can be imported into BloodHound.

### With password
```bash
bloodhound-python \
  -u Administrator \
  -p 'Password123!' \
  -d spookysec.local \
  -dc ATTACKTIVEDIRECTORY.spookysec.local \
  -ns <DC_IP> \
  -c All
```

### With NTLM hash
```bash
bloodhound-python \
  -u Administrator \
  -d spookysec.local \
  -dc ATTACKTIVEDIRECTORY.spookysec.local \
  -ns <DC_IP> \
  -c All \
  --hashes 'LM_HASH:NTLM_HASH'
```

Example:
```bash
bloodhound-python \
  -u Administrator \
  -d spookysec.local \
  -dc ATTACKTIVEDIRECTORY.spookysec.local \
  -ns 10.113.130.110 \
  -c All \
  --hashes 'aad3b435b51404eeaad3b435b51404ee:0e0363213e37b94221497260b0bcb4fc'
```

### What does `-c All` collect?

It requests multiple categories of AD information, including:
```text
Users
Groups
Computers
Sessions
ACLs
GPOs
Domains
Trusts
Containers
```

The output is usually several `.json` files.

---

# 3. Import the Data

In BloodHound:
```text
Upload / Import
      ↓
Select bloodhound-python .json files
      ↓
BloodHound builds the graph
      ↓
Analyze relationships
```

---

# 4. Analyze the Graph

The important idea is that BloodHound doesn't simply show objects — it shows **relationships**.

Example:
```text
User
 │
 ├── MemberOf → Group
 │                 │
 │                 └── AdminTo → Computer
 │
 └── GenericAll → User
                       │
                       └── MemberOf → Domain Admins
```

This can reveal an **attack path** that isn't obvious from normal enumeration.

---

# 5. Most Important Queries

BloodHound has built-in **Cypher queries / search functionality**. Some of the most useful things to investigate are:

### Find paths to Domain Admins

Look for paths from a compromised user/computer to:
```text
Domain Admins
```

This is one of the first things to check after importing data.

---

### Find shortest path between two objects

Conceptually:
```text
Compromised User
       ↓
    [Path]
       ↓
Domain Admins
```

Use BloodHound's **Shortest Paths / Pathfinding** functionality to identify the relationship chain.

---

### Find Domain Admin members

Search for:
```text
Domain Admins
```

Then inspect:
```text
Members
     ↓
Users / Groups
     ↓
How those accounts can be reached
```

---

### Find Users with Admin Rights

Investigate relationships such as:
```text
AdminTo
MemberOf
HasSession
```

Especially:
```text
User → AdminTo → Computer
```

---

### Find Dangerous ACLs

Pay special attention to:
```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
ForceChangePassword
AddMember
AllExtendedRights
```

These indicate potentially powerful control over AD objects.

---

# 6. Useful BloodHound Relationships

|Relationship|Meaning|
|---|---|
|`MemberOf`|User/group belongs to another group|
|`AdminTo`|Principal has administrative rights over a computer|
|`HasSession`|User has a session on a computer|
|`GenericAll`|Full control over an object|
|`GenericWrite`|Can modify important object properties|
|`WriteDACL`|Can modify the object's ACL|
|`WriteOwner`|Can change the object's owner|
|`ForceChangePassword`|Can force another user's password change|
|`AddMember`|Can add members to a group|
|`CanRDP`|Can RDP to a computer|
|`ExecuteDCOM`|Can execute through DCOM|
|`AllowedToDelegate`|Delegation relationship|

---

# 7. The Main Workflow

```text
1. Start BloodHound
        ↓
2. Collect AD data
   bloodhound-python
        ↓
3. Import JSON files
        ↓
4. Find interesting relationships
        ↓
5. Identify attack paths
        ↓
6. Investigate permissions
        ↓
7. Follow the shortest path to higher privileges
```

### Key idea

> **BloodHound is mainly about relationships and attack paths, not simply enumeration.**

---

# 8. Stop / Close BloodHound

```bash
cd ~/BloodHound
docker compose down
```

This stops the containers **without deleting the persistent Docker volumes/data**.

Start it again later with:

```bash
cd ~/BloodHound
docker compose up -d
```

Check status:

```bash
docker compose ps
```

