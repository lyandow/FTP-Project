import socket
from os.path import exists, getsize


sock = socket.socket()


def connect_to_server(command_split):
    global sock
    
    # Try to establish a create a socket
    try:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP)
    except socket.error as err:
        print("There was an error creating a socket: " + err.strerror)
        return False
    
    # Try to connect to the server, IP specified by user
    host = command_split[1]
    port = 7777
    print("Attempting to connect to host IP: %s User: %s Pass: %s" % (host, command_split[2], command_split[3]))
    try:
        sock.connect((host,port))
    except socket.error as err:
        print("Caught connection error: %s" % err.strerror)
        return False

    # Send login username and password to server after connecting.
    login_msg = command_split[2] + " " + command_split[3]
    sock.send(login_msg.encode())

    # Get response from server, server tells us if login was successful or not
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

    # Check if file exists - we can't send a file that doesn't exist
    if exists(command_split[1]):
        put_msg = "PUT: " + command_split[1] + " " + str(getsize(command_split[1]))

        # Send put command and info to the server
        sock.send(put_msg.encode())

        not_ready = True

        # Wait until we receive the READY message from the server
        while not_ready:
            response = sock.recv(1024).decode()
            response_split = response.split(" ")

            # Server checks if it already has the file. If so,
            # Server asks if we want to overwrite it with our local version
            if response_split[0] == "CONFIRM:":
                # Get Y/N input from the user, send it to the server
                print(response)
                client_confirm = input()
                sock.send(client_confirm.encode())

                # If client said No, return to avoid infinite loop
                if client_confirm[0] == "N":
                    return
            elif response_split[0] == "READY":
                not_ready = False

        print("Sending %s to the server..." % command_split[1])

        # Open the file so we can send it to the server
        file_to_send = open(command_split[1], "rb")

        # Read first 1024 bytes
        data = file_to_send.read(1024)
        while data:
            # Send data to the server
            sock.send(data)

            # Try to read more data from the file. Loop exits when data is empty
            data = file_to_send.read(1024)
        print("Finished sending file!")

        # Wait for server to acknowledge that it has fully received the file,
        # which it does by a calculation based on the file size we sent
        server_ack = sock.recv(1024).decode().split(" ")
        if server_ack[0] == "FULLY":
            print("Server acknowledged that the file was received in full!")
    else:
        print("ERROR: %s - this file does not exist in this directory" % command_split[1])


def get_from_server(command_split):
    global sock


    ready = True
    if exists(command_split[1]):
        confirm = input("CONFIRM: File already exists in this directory. Do you want to overwrite it with the server's copy? Y/N:")
        if confirm[0] == "N":
            ready = False
        elif confirm[0] == "Y":
            ready = True

    if ready:

        # Send get command to the server
        get_str = "GET: " + command_split[1]
        sock.send(get_str.encode())

        # Get size of file from the server
        response = sock.recv(1024).decode()
        response_split = response.split(" ")

        # If response is not ERROR, then it is the size
        if response_split[0] == "ERROR:":
            print(response)
            return

        # Receive the file in chunks of 1024 bytes (default is 1)
        number_of_chunks = int(int(response_split[0]) / 1024) + 1

        ready_str = "READY"
        sock.send(ready_str.encode())

        # Open file in write mode
        write_file = open(command_split[1], "wb")
        for n in range(0, number_of_chunks):
            # Receive a chunk of 1024 bytes and write it to the file
            data = sock.recv(1024)
            write_file.write(data)
        write_file.close()

        print("Successfully received file from the server")


def print_usage():
    print("tigerc.py commands:\n")
    print("\tconnect <TigerS IP Addr> <User> <Password>: attempts to connect to the server with the username and password\n")
    print("\tget <File name>: downloads a file from the server\n")
    print("\tput <File name>: sends a file to the server. File names cannot include spaces.\n")
    print("\texit: closes the server connection OR ends application if no connection is established\n\n")


def handle_commands():
    isConnected = False
    while True:
        # Wait for input
        command = input("Enter a command: ")
        command_split = command.split(" ")

        # Parse input for the 4 commands specified
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
                # Attempt to download a file from the server
                get_from_server(command_split)
        elif command_split[0] == "put" and len(command_split) == 2:
            if not isConnected:
                print("You need to connect to a server before you can send a file!")
                print_usage()
            else:
                # Attempt to send a file to the server
                put_to_server(command_split)
        elif command_split[0] == "exit":
            if not isConnected:
                # Exit application if not connected to server
                print("Exit received, no current connection. Exiting application...\n")
                return()
            else:
                # Disconnect from the server
                print("Disconnecting from the server...\n")
                exit_msg = "exit"

                # Send exit message to server so the server knows to close the socket too
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