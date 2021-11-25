import socket
import threading
import struct
import array


def on_new_client(clientSocket, clientAddr):
    string = "Client: " + str(clientAddr) + " has connected... Port: " + str(clientSocket)
    print(string)


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