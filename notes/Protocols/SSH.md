
# SSH Quick Notes for CTF & Pentesting

## 1. Basic Login

```bash
ssh user@target_ip
```

Example:

```bash
ssh kali@192.168.1.10
```

Specify port:

```bash
ssh user@target_ip -p 2222
```

---

## 2. Login with Private Key

Very common in CTFs.

```bash
ssh -i id_rsa user@target_ip
```

If permission error:

```bash
chmod 600 id_rsa
```

Then retry.

---

## 3. Common SSH Enumeration

### Check SSH version

```bash
nmap -sV -p 22 target
```

or

```bash
nc target 22
```

Example output:

```bash
SSH-2.0-OpenSSH_8.2p1
```

Useful for finding exploits.

---

## 4. Brute Force (Only in labs / CTF)

Using Hydra:

```bash
hydra -l root -P rockyou.txt ssh://target
```

Username list:

```bash
hydra -L users.txt -P passwords.txt ssh://target
```

Custom port:

```bash
hydra -l admin -P pass.txt ssh://target -s 2222
```

---

## 5. File Transfer

### Download from target

```bash
scp user@target:/path/file .
```

Example:

```bash
scp user@10.10.10.5:/home/user/flag.txt .
```

---

### Upload to target

```bash
scp file.txt user@target:/tmp/
```

---

## 6. SSH Tunneling (Very Important)

This shows up a lot.

---

### Local Port Forwarding

Access internal services.

```bash
ssh -L local_port:internal_ip:remote_port user@target
```

Example:

```bash
ssh -L 8080:127.0.0.1:80 user@target
```

Then visit:

```bash
http://localhost:8080
```

Use when target can access something you can't.

---

### Dynamic Port Forwarding (SOCKS Proxy)

Pivoting.

```bash
ssh -D 9050 user@target
```

Then configure proxychains:

```bash
proxychains nmap target
```

---

### Remote Port Forwarding

Expose your machine to target.

```bash
ssh -R 4444:localhost:4444 user@target
```

Useful for reverse shells.

---

## 7. Run Commands Without Shell

```bash
ssh user@target "whoami"
```

Example:

```bash
ssh user@target "cat /etc/passwd"
```

Good for automation.

---

## 8. Useful Options

### Verbose mode

Debug connection issues.

```bash
ssh -v user@target
```

More details:

```bash
ssh -vvv user@target
```

---

### Disable host key checking (CTFs)

Avoid prompts.

```bash
ssh -o StrictHostKeyChecking=no user@target
```

---

## 9. If You Find id_rsa

Always try:

```bash
chmod 600 id_rsa
ssh -i id_rsa user@target
```

Check if encrypted:

```bash
ssh-keygen -yf id_rsa
```

Crack passphrase:  
Using John the Ripper

```bash
ssh2john kay_id_rsa > kay_hash.txt
john --wordlist=rockyou.txt kay_hash.txt
john --show kay_hash.txt
```

---

## 10. SSH Config File

Sometimes useful creds:

```bash
cat ~/.ssh/config
```

Look for:

- usernames
    
- private key paths
    
- alternate ports
    
- jump hosts
    

---

## 11. Authorized Keys Abuse

If writable:

```bash
echo "your_public_key" >> ~/.ssh/authorized_keys
```

Persistent access.

Generate key:

```bash
ssh-keygen
```

---

## 12. SSH Escape Sequence

When stuck:

Disconnect:

```bash
~.
```

(Type after Enter)

---

## 13. Useful Enumeration on Box

After access:

```bash
whoami
id
sudo -l
uname -a
ss -tulpn
netstat -tulpn
find / -perm -4000 2>/dev/null
```

---

# Typical CTF Workflow

### Found credentials

```bash
ssh user@target
```

### Found private key

```bash
chmod 600 id_rsa
ssh -i id_rsa user@target
```

### Internal web service

```bash
ssh -L 8080:127.0.0.1:80 user@target
```

### Need pivot

```bash
ssh -D 9050 user@target
```

---

## Fix Backspace Not Deleting in SSH

```bash
export TERM=xterm
```

---
# Commands to Memorize

These are the must-know ones:

```bash
ssh user@ip
ssh -i key user@ip
ssh -p port user@ip
scp file user@ip:/tmp
ssh -L 8080:127.0.0.1:80 user@ip
ssh -D 9050 user@ip
ssh -v user@ip
chmod 600 id_rsa
```

# Problem i faced
### `192.168.1.10` IS probably your VM

This is interesting:
```bash
ssh muhammad@192.168.1.10
```

actually reached an SSH server, but the SSH negotiation failed:

```text
Unable to negotiate with 192.168.1.10 port 22:
no matching host key type found.
Their offer: ssh-rsa,ssh-dss
```

That means **192.168.1.10 is reachable and SSH is running**. 

The problem is that your modern OpenSSH client doesn't accept the VM's old `ssh-rsa`/`ssh-dss` host keys by default.

### Try this
```bash
ssh -o HostKeyAlgorithms=+ssh-rsa muhammad@192.168.1.10
```

