# Understanding /dev/shm

### What is /dev/shm?

`/dev/shm` stands for **"shared memory"** and is a temporary file storage location that exists **only in RAM** (not on disk). It's mounted as a `tmpfs` filesystem.

```bash
# Check if /dev/shm is mounted
mount | grep shm
# Output: tmpfs on /dev/shm type tmpfs (rw,nosuid,nodev)
```

### Why Use /dev/shm for Tools Like LinPEAS?

| Feature | Benefit |
|---------|---------|
| **Writable by Everyone** | No permission issues, anyone can read/write/execute |
| **Fast (RAM-Based)** | Operations are extremely fast, no disk I/O bottleneck |
| **Volatile (No Persistence)** | Files auto-delete on reboot, no forensic traces |
| **Less Likely to Be Monitored** | Often overlooked by security tools |
| **No `noexec` Mount Option** | Can execute binaries from here (unlike `/tmp` sometimes) |
| **Bypass Disk Quotas** | Uses RAM instead of disk space |

### Common Uses
```bash
# Upload tools
scp linpeas.sh jan@10.114.149.44:/dev/shm/

# Compile exploits in RAM
gcc exploit.c -o /dev/shm/exploit
/dev/shm/exploit

# Temporary file storage
echo "sensitive_data" > /dev/shm/temp.txt

# SSH keys (temporary use)
cp ~/.ssh/id_rsa /dev/shm/
chmod 600 /dev/shm/id_rsa
```

### Clean Up After Yourself
```bash
# Always clean up for good OPSEC
rm -f /dev/shm/linpeas.sh
rm -f /dev/shm/exploit
```

---

## Compare /dev/shm vs /tmp

| Feature         | `/dev/shm`           | `/tmp`                      |
| --------------- | -------------------- | --------------------------- |
| **Location**    | RAM (tmpfs)          | Disk (usually)              |
| **Speed**       | Very Fast            | Slower (disk I/O)           |
| **Persistence** | Lost on reboot       | Survives reboot (sometimes) |
| **Execution**   | Executable (usually) | May have `noexec`           |
| **Monitoring**  | Less monitored       | Often monitored             |
| **Forensics**   |  No traces on disk   | Leaves traces on disk       |
| **Size Limit**  | Usually 50% of RAM   | Usually 10-20% of disk      |
| **Common Use**  | RAM disks, tmpfs     | Temporary files             |