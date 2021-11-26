import socket
import threading
from threading import Lock
import struct
import array
from os.path import exists


lock = Lock()


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

'''
    Since we don't want two separate clients writing the same
    file at the same time, we need this function synchronized
'''
def handle_put(clientSocket, received_message):
    global lock
    
    lock.acquire(1)
        
    ready_message = "READY FOR FILE"

    # format: put <filename> <filesize>

    need_confirmation = False

    # Check if file already exists
    if exists(received_message[1]):
        need_confirmation = True

        while need_confirmation:
            confirmation_msg = "CONFIRM: File already exists on the server. Do you want to overwrite the file? Y/N:"
            clientSocket.send(confirmation_msg.encode())

            # wait for response
            data = clientSocket.recv(1024).decode()
            
            if data[0] == "Y":
                need_confirmation = False
            elif data[0] == "N":
                # Client said no, so we don't need to wait for a file
                # Release lock for other clients and return
                lock.release()
                return

    if not need_confirmation:
        clientSocket.send(ready_message.encode())

        number_of_chunks = int(int(received_message[2]) / 1024) + 1
        write_file = open(received_message[1], "wb")
        for n in range(0, number_of_chunks):
            data = clientSocket.recv(1024)
            write_file.write(data)

    full_rcv_msg = "FULLY RECEIVED FILE"
    clientSocket.send(full_rcv_msg.encode())

    lock.release()

def receive_client_messages(clientSocket, clientAddr):
    # Wait infinitely for data from the client
    while True:
        # Receive message from client, split by spaces
        received_message = clientSocket.recv(1024).decode()
        received_message = received_message.split(" ")

        if received_message[0] == "exit":
            # Client sent us "exit", so we return to end the thread
            return
        elif received_message[0] == "put":
            # Client sent us "put"
            handle_put(clientSocket, received_message)
            





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