import socket


sock = socket.socket()


def connect_to_server(command_split):
    global sock
    
    try:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP)
    except socket.error as err:
        print("There was an error creating a socket: " + err.strerror)
        return False
    host = command_split[1]
    port = 7777
    print("Attempting to connect to host IP: %s User: %s Pass: %s" % (host, command_split[2], command_split[3]))
    try:
        sock.connect((host,port))
    except socket.error as err:
        print("Caught connection error: %s" % err.strerror)
        return False

    login_msg = command_split[2] + " " + command_split[3]
    sock.send(login_msg.encode())

    response = sock.recv(1024).decode()
    if response.__contains__("ERROR"):
        print(response)
        sock.close()
        return False
    else:
        print(response)
    return True


def print_usage():
    print("tigerc.py commands:\n")
    print("\tconnect <TigerS IP Addr> <User> <Password>: attempts to connect to the server with the username and password\n")
    print("\tget <File name>: downloads a file from the server\n")
    print("\tput <File name>: sends a file to the server\n")
    print("\texit: closes the server connection OR ends application if no connection is established\n\n")


def handle_commands():
    isConnected = False
    while True:
        command = input("Enter a command: ")
        command_split = command.split(" ")
        if command_split[0] == "connect" and len(command_split) == 4:
            if not isConnected:
                # Attempt to connect to the server with the given login info
                isConnected = connect_to_server(command_split)
            else:
                print("You are already connected to a server. Disconnect by entering \"exit\"\n")
        elif command_split[0] == "get":
            print("get received")
        elif command_split[0] == "put":
            '''print("put received")
            file_to_send = open("test.txt", "rb")
            sock.sendfile(file_to_send)
            print("File sent!")'''
        elif command_split[0] == "exit":
            if not isConnected:
                print("Exit received, no current connection. Exiting application...\n")
                return()
            else:
                print("Disconnecting from the server...\n")
                exit_msg = "exit"
                sock.send(exit_msg.encode())
                sock.close()
                isConnected = False
        else:
            print("Invalid command entered!\n")
            print_usage()


def main():
    print_usage()
    handle_commands()

if __name__ == "__main__":
    main()