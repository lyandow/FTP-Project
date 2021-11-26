import socket
import threading
import struct
import array


def on_new_client(clientSocket, clientAddr):
    string = "Client: " + str(clientAddr) + " has connected..."
    print(string)
    # Receive the username and password from this client
    data = clientSocket.recv(1024).decode()
    client_user_and_pass = data.split(" ")

    # Open file containing usernames and passwords
    login_file = open("users.txt", "r")
    lines = login_file.readlines()
    
    # Remove special characters from the username/password file
    # File format is as follows:
    # <username1> <password1>
    # <username2> <password2>
    # and so on
    for n in range(0, len(lines)):
        lines[n] = lines[n].strip()

    # Check if client's sent username and password are listed in the file
    valid_user = False
    line_number = 0
    while(not valid_user and line_number < len(lines)):
        stored_user_and_pass = lines[line_number].split(" ")
        # If client's username and password match a line in the users.txt file, username is valid
        if stored_user_and_pass[0] == client_user_and_pass[0] and stored_user_and_pass[1] == client_user_and_pass[1]:
            valid_user = True
        line_number += 1
    
    if not valid_user:
        error_message = "ERROR: The specified Username and Password are invalid. Closing connection..."
        clientSocket.send(error_message.encode())
        clientSocket.close()
        return
    else:
        success_message = "SUCCESS: Login with specified Username and Password was successful."
        clientSocket.send(success_message.encode())

    # at this point, the client has successfully logged in and
    # established a connection. Thus, we can wait to receive
    # messages from the client.

    receive_client_messages(clientSocket, clientAddr)

    # We only reach here if the receive_client_messages function
    # returns, which only happens when the client sends an
    # exit message. Here, we have to close the socket and return
    # to close the thread

    clientSocket.close()
    print("Client %s has disconnected..." % str(clientAddr))
    return


def receive_client_messages(clientSocket, clientAddr):
    # Wait infinitely for data from the client
    while True:
        # Receive message from client, split by spaces
        received_message = clientSocket.recv(1024).decode()
        received_message = received_message.split(" ")

        if received_message[0] == "exit":
            # Client sent us "exit", so we return to end the thread
            return




def main():
    # Create server socket
    s = socket.socket()
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    port = 7777
    string = "listening on " + hostname + "\nIP: " + ip + "\n"
    print(string)

    # Bind socket, listen
    s.bind((ip, port))
    s.listen(10)

    clientCount = 0

    # Create a thread for each new client that connects. Each thread runs the on_new_client function
    while True:
        clientCount += 1
        client, clientAddr = s.accept()
        newClient = threading.Thread(target=on_new_client, name="FTP Client {}".format(threading.active_count() - 1), args=(client, clientAddr))
        newClient.daemon = True
        newClient.start()

if __name__ == "__main__":
    main()