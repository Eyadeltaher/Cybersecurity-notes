
| Tool          | Main Use                  | SSH Required? |         SOCKS Proxy | Port Forwarding | Best Use                                             |
| ------------- | ------------------------- | ------------: | ------------------: | --------------: | ---------------------------------------------------- |
| **Chisel**    | Tunneling & pivoting      |            NO |                 Yes |             Yes | Pivoting when SSH isn't available                    |
| **Socat**     | Relays & port forwarding  |            NO |                  NO |             Yes | Simple TCP relays/forwards                           |
| **SSH**       | Tunneling & remote access |           Yes |                 Yes |             Yes | Flexible tunneling when SSH is available             |
| **sshuttle**  | VPN-like subnet tunneling |           Yes |                  NO |              NO | Accessing an entire internal subnet transparently    |
| **FoxyProxy** | Proxy configuration       |            NO | Uses existing proxy |              NO | Easily switching browser traffic between proxies     |
| **plink.exe** | SSH tunneling on Windows  |           Yes |                 Yes |             Yes | SSH tunneling from Windows, especially older systems |

### Quick distinction
```text
SSH           → Create tunnels
Socat         → Relay connections
sshuttle      → Tunnel an entire subnet
FoxyProxy     → Configure applications to use a proxy
Plink         → Windows command-line SSH/tunneling
Chisel        → create tunneling without SSH
```

