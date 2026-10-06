## 1. Enumeration
1. System Information Enumeration
2. User and Group Enumeration
3. Sudo Permissions Enumeration
4. SUID/SGID Enumeration
5. Linux Capabilities Enumeration
6. Running Processes Enumeration
7. Open Ports and Network Enumeration
8. Installed Packages Enumeration
9. Environment Variables Enumeration
10. Cron Jobs Enumeration
11. File and Directory Permissions Enumeration
12. Mounted Filesystems Enumeration
13. Kernel Version Enumeration


## 2. Linux Capabilities
1. Dangerous File Capabilities
2. `CAP_DAC_READ_SEARCH` Exploitation
3. `CAP_SYS_ADMIN` Exploitation
4. `CAP_SYS_PTRACE` Exploitation


## 3. File and Directory Permissions
1. Writable `/etc/sudoers`
2. Writable `/etc/crontab`
3. Writable `/etc/ld.so.preload`
4. Writable System Binaries
5. Writable Configuration Files
6. Writable SSH Keys
7. Writable `/etc` Files
8. Insecure Temporary File Permissions


## 4. Cron Jobs and Scheduled Tasks
1. Systemd Timer Exploitation


## 5. PATH and Library Hijacking
1.  Dynamic Linker Hijacking
2. Python Module Hijacking
3. Library Search Order Exploitation

## 6. Credentials and Secrets
1. Password Hunting
2. Password Reuse
3. Credential Hunting in History Files
4. SSH Private Key Discovery
5. Credentials in Configuration Files
6. Credentials in Scripts
7. Credentials in Environment Variables
8. Database Credential Discovery
9. SSH Agent Hijacking
10. Browser Credential Discovery


## 7. Services and Processes
1. Exploiting Misconfigured Services
2. Writable Service Executables
3. Writable Service Configuration Files
4. Service PATH Hijacking
5. Process Injection
6. `ptrace` Exploitation
7. Insecure Systemd Service Files
8. Docker Service Misconfiguration


## 8. Containers and Virtualization
1. Docker Group Exploitation
2. Docker Socket Abuse
3. Privileged Docker Containers
4. LXC/LXD Group Exploitation
5. Container Escape
6. Kubernetes Misconfiguration Exploitation


## 9. Other Techniques

1. NFS `no_root_squash` Exploitation
2. D-Bus Misconfiguration Exploitation
3. Abusing Writable `/proc` Interfaces
4. Exploiting Weak SSH Configuration
5. Wildcard Injection
6. Bash Function Exploitation
7. Exploiting Misconfigured `sudoedit`
8. Logrotate Exploitation
9. Screen and Tmux Session Hijacking
10. TTY Group Exploitation