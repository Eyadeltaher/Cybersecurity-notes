
The File Transfer Protocol (FTP) uses specific commands to manage connections and transfer files. These are typically divided into **Standard User Commands** (the ones you type into a terminal like Windows CMD or Linux shell) and **Raw Commands** (the background signals sent between computers)

- **port 21**
## Common User Commands

| Command         | Description                                                                                         |
| :-------------- | :-------------------------------------------------------------------------------------------------- |
| ftp             | Accesses the ftp command interpreter.                                                               |
| open            | Logs in to the remote system from the command interpreter.                                          |
| close           | Logs out of the remote system and returns to the command interpreter.                               |
| bye             | Quits the ftp command interpreter.                                                                  |
| help            | Lists all ftp commands or, if a command name is supplied, briefly describes what the command does.  |
| reset           | Re-synchronizes the command-reply sequencing with the remote ftp server.                            |
| ls              | Lists the contents of the remote working directory.                                                 |
| pwd             | Displays the name of the remote working directory.                                                  |
| cd              | Changes the remote working directory.                                                               |
| lcd             | Changes the local working directory.                                                                |
| mkdir           | Creates a directory on the remote system.                                                           |
| rmdir           | Deletes a directory on the remote system.                                                           |
| get, mget       | Copies a file (or multiple files) from the remote working directory to the local working directory. |
| put, mput       | Copies a file (or multiple files) from the local working directory to the remote working directory. |
| delete, mdelete | Deletes a file (or multiple files) from the remote working directory.                               |
``` bash
ftp ftp.example.com
```


## Essential Configuration Commands
- **`passive`**: Toggleshelp between "Active" and "Passive" mode. This is helpful if you are behind a firewall or router and can't download files.
- **`prompt`**: Turns off the "Are you sure?" confirmation when downloading or uploading multiple files (useful with `mget` or `mput`).
- **`hash`**: Prints a `#` on your screen for every 1024 bytes transferred, so you can see the progress of large files.
- **`status`**: Shows your current connection settings and transfer modes.

### Quick Tips
- **Help**: Typing `help` or `?` inside an FTP session will list all available commands for that specific client.
- **Local Commands**: In many FTP clients, putting an exclamation mark (`!`) before a command (like `!ls`) will run that command on your local machine instead of the server.


## FTP anonymous login
FTP anonymous login allows users to access FTP servers without a dedicated username or password, typically using "anonymous"

enter `anonymous` as the username and password when connecting


## FTP  login bruteforce

``` bash
hydra -t 4 -l user -P rockyou.txt ftp://machine_IP 
```

-t 4                                   Number of parallel connections per target  
-l user                             Points to the user who's account you're trying to compromise  
-P path to dictionary Points to the file containing the list of possible passwords  
-vV                                   Sets verbose mode to very verbose, shows the login+pass combination
machine IP                    The IP address of the lab machine  
  