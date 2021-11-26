import socket
from os.path import exists, getsize


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


def put_to_server(command_split):
    global sock

    if exists(command_split[1]):
        put_msg = "put " + command_split[1] + " " + str(getsize(command_split[1]))

        sock.send(put_msg.encode())

        not_ready = True

        while not_ready:
            response = sock.recv(1024).decode()
            response_split = response.split(" ")
            if response_split[0] == "CONFIRM:":
                print(response)
                client_confirm = input()
                sock.send(client_confirm.encode())
                if client_confirm[0] == "N":
                    return
            elif response_split[0] == "READY":
                not_ready = False

        print("Sending %s to the server..." % command_split[1])
        file_to_send = open(command_split[1], "rb")
        data = file_to_send.read(1024)
        while data:
            sock.send(data)
            data = file_to_send.read(1024)
        print("Finished sending file!")
        server_ack = sock.recv(1024).decode().split(" ")
        if server_ack[0] == "FULLY":
            print("Server acknowledged that the file was received in full!")
    else:
        print("ERROR: %s - this file does not exist in this directory" % command_split[1])


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
        elif command_split[0] == "get" and len(command_split) == 2:
            if not isConnected:
                print("You need to connect to a server before you can get a file!")
                print_usage()
            else:
                print("get received")
        elif command_split[0] == "put" and len(command_split) == 2:
            if not isConnected:
                print("You need to connect to a server before you can send a file!")
                print_usage()
            else:
                put_to_server(command_split)
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