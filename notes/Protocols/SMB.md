### SMB in simple terms

**SMB = Server Message Block**
	The main file and printer sharing protocol for Windows
	
Imagine you have:
Your PC  ───── Network ─────>  Another PC
                              └── Shared Folder

SMB allows your PC to access that shared folder as if you're accessing files on your own computer.

### What can SMB do?

With SMB, you can:

-  List files → `ls` / `dir`
-  Download files → `get`
-  Upload files → `put`
-  Change directories → `cd`
-  Delete files → `rm`
-  Read files → `more`
-  Authenticate with a username/password
-  Sometimes access shares anonymously

### Example

Suppose a server has:

10.10.10.10
    │
    └── shared
          ├── notes.txt
          ├── passwords.txt
          └── id_rsa

You connect:
`smbclient //10.10.10.10/shared -U Anonymous`
Then:
`smb: \> ls`
You might see:
notes.txt
passwords.txt
id_rsa

You can download a file:
`smb: \> get id_rsa`

### Why is SMB important in pentesting?
Because **misconfigured SMB shares can expose sensitive information**.


**NOTES**
- Older SMB ran on top of NetBIOS (Port 139).
- Modern SMB runs directly on TCP (Port 445) without NetBIOS
* NetBIOS and SMB are legacy and modern networking technologies often used together in Windows networks to share files, printers, and find other computers.
* Netbios --> Network Basic Input/Output System
* NetBIOS sets up names and sessions; SMB handles the actual file tasks

# Enumeration
## Enum4linux

**Enum4linux** is an **open-source** tool for enumerating information from Windows and Samba systems. It is a wrapper around the Samba tools smbclient, rpclient, net, and nmblookup, consolidating their functionality into a single easy-to-use interface. Enum4linux is particularly valuable during the reconnaissance phase of penetration testing, providing comprehensive information about Windows networks, shares, users, groups, and system configurations.

**Here are the primary uses of Enum4linux:**

- **User Enumeration:** Enum4linux enumerates local and domain users from Windows systems, providing usernames, RIDs (Relative Identifiers), and account information. This data is crucial for understanding the user landscape and identifying potential targets for further attacks.
    
- **Share Enumeration:** The tool discovers and lists SMB shares on target systems, identifying accessible network resources and potential data repositories. It also determines share permissions and access controls, revealing misconfigured or overly permissive shares.
    
- **Group Enumeration:** Enum4linux identifies local and domain groups along with their memberships, helping security professionals understand organizational structure and privilege distribution across the network.
    
- **Password Policy Discovery:** The tool retrieves password policy information including minimum length, complexity requirements, lockout thresholds, and password history. This information is valuable for planning password spraying attacks and understanding account security controls.
    
- **OS and Domain Information:** Enum4linux gathers operating system details, domain information, and workgroup configurations, providing context about the target environment and helping identify potential vulnerabilities.
    
- **RID Cycling:** The tool performs RID (Relative Identifier) cycling to enumerate users and groups even when standard enumeration methods are restricted, providing a reliable fallback enumeration technique.
    

## Core Features

- User Enumeration
- Group Enumeration
- Share Enumeration
- Password Policy Retrieval
- OS Information Discovery
- Domain/Workgroup Information
- RID Cycling
- SID Enumeration
- Printer Information
- Null Session Exploitation
- Credential-Based Enumeration
- Verbose Output Options
- Multiple Protocol Support

## Data sources

- SMB Protocol
- NetBIOS Protocol
- MSRPC Protocol
- SAMR (Security Account Manager Remote)
- LSA (Local Security Authority)
- Share Information
- Domain Controllers
- Windows Registry (Remote)
- Active Directory (via RPC)

## Common Enum4linux Commands

### 1. Basic Enumeration

- This command performs a basic enumeration of the target system, gathering general information about users, shares, and system configuration.

```
enum4linux <target>
```

### 2. Full Enumeration

- This command performs comprehensive enumeration using all available techniques, providing maximum information about the target system.

```
enum4linux -a <target> | tee output.log
```

### 3. User Enumeration

- This command specifically enumerates users on the target system, listing all local and domain user accounts.

```
enum4linux -U <target>
```

### 4. Share Enumeration

- This command lists all SMB shares available on the target system along with their permissions and access controls.

```
enum4linux -S <target>
```

### 5. Group Enumeration

- This command enumerates local and domain groups on the target system, including group memberships.

```
enum4linux -G <target>
```

### 6. Password Policy

- This command retrieves the password policy from the target system, including requirements and lockout settings.

```
enum4linux -P <target>
```

### 7. OS Information

- This command gathers operating system information including version, build number, and system architecture.

```
enum4linux -o <target>
```

### 8. RID Cycling

- This command performs RID cycling to enumerate users and groups through brute-forcing SIDs (Security Identifiers).

```
enum4linux -r <target>
```

### 9. Detailed RID Cycling

- This command performs detailed RID cycling with an extended range, discovering more users and groups through comprehensive SID enumeration.

```
enum4linux -R 500-550,1000-1050 <target>
```

### 10. Authenticated Enumeration

- This command performs enumeration using provided credentials, accessing information that requires authentication.

```
enum4linux -u <username> -p <password> <target>
```

### 11. Domain Information

- This command retrieves domain and workgroup information from the target system.

```
enum4linux -d <target>
```

### 12. List Users via RID

- This command enumerates users by iterating through RIDs, useful when other enumeration methods fail.

```
enum4linux -r -u <username> -p <password> <target>
```

### 13. Printer Information

- This command gathers information about network printers configured on the target system.

```
enum4linux -i <target>
```

### 14. Group Member Information

- This command retrieves detailed information about members of specific groups.

```
enum4linux -M <target>
```

### 15. Share Access Check

- This command checks which shares are accessible and attempts to list their contents.

```
enum4linux -s /usr/share/enum4linux/share-list.txt <target>
```

### 16. Verbose Output

- This command enables verbose output mode, displaying detailed information about enumeration operations and results.

```
enum4linux -v <target>
```

### 17. Workgroup Detection

- This command detects and displays the workgroup or domain name of the target system.

```
enum4linux -w <target>
```

### 18. Known Usernames Check

- This command checks for the existence of common or known usernames on the target system.

```
enum4linux -k <username> <target>
```

### 19. Dependency Check

- This command checks if all required dependencies (smbclient, rpcclient, etc.) are installed and accessible.

```
enum4linux -d
```


# Exploiting 


## SMB share access- a common misconfiguration

We can remotely access the SMB share using the syntax:
`Syntax: smbclient //[IP]/[SHARE] -U [USERNAME] -p [PORT]`
`Example: smbclient //10.10.10.10/secrets -U Anonymous -p 445`

