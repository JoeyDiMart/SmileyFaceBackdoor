'''
Testing testing
'''


from ftplib import FTP  # import so python can handle FTP protocol stuff


##### Here lets put all the variables
IP_addr = '192.168.4.186'
PORT = 21
USER = ''
PASSWORD = ''
USE_PASSIVE = False  # if connection fails set this to true idk



ftp = FTP()  # create an FTP object
ftp.connect(IP_addr, PORT)
ftp.set_pasv(USE_PASSIVE)
ftp.login(USER, PASSWORD)  # send username and password to the FTP server

print(f"Connected to {IP_addr}. Type 'exit' to quit.")

while True:
    try:
        current_dir = ftp.pwd()
        command = input(f"ftp:{current_dir}>").strip()

        if command == "exit":
            ftp.quit()
            break
        elif command.startswith("cd "):
            ftp.cwd(command[3:])
        elif command == "cd..":
            ftp.cwd("..")
        elif command == "ls":
            ftp.dir()
        elif command == "pwd":
            print(current_dir)


        elif command.startswith("cat "):
            filename = command[4:]
            lines = []
            ftp.retrlines(f'RETR {filename}', lines.append)
            print(lines)

        else:
            print("Commands: cd <dir>, cd.., ls, pwd, exit")

    except Exception as e:
        print(f"error: {e}")