
**sshuttle** creates a VPN-like tunnel through SSH. Unlike a normal SOCKS proxy, applications can connect directly to internal IPs without configuring Proxychains.
### Requirements
- Linux compromised host
- SSH access
- Python installed on the target

## Basic Usage
```bash
sshuttle -r USERNAME@ADDRESS SUBNET
```
### Example
```bash
sshuttle -r user@172.16.0.5 172.16.0.0/24
```

After connecting, traffic to `172.16.0.0/24` is routed through the compromised host.

You can then interact with internal hosts normally:
```bash
nmap 172.16.0.10
```

or:
```bash
ssh user@172.16.0.10
```

## Automatic Subnet Detection
```bash
sshuttle -r USERNAME@ADDRESS -N
```
`-N` attempts to determine the target subnet from the compromised host's routing table.

## SSH Key Authentication
```bash
sshuttle -r USERNAME@ADDRESS --ssh-cmd "ssh -i KEYFILE" SUBNET
```
### Example
```bash
sshuttle -r user@172.16.0.5 --ssh-cmd "ssh -i private_key" 172.16.0.0/24
```

## Exclude the Compromised Host

If the compromised host is inside the subnet being forwarded, sshuttle may break its own SSH connection.

```bash
sshuttle -r USERNAME@ADDRESS SUBNET -x COMPROMISED_IP
```
### Example
```bash
sshuttle -r user@172.16.0.5 172.16.0.0/24 -x 172.16.0.5
```

