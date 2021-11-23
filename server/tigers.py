import socket
import threading
import struct
import array

class TCPPacket:
    def __init__(self,
                 src_host:  str,
                 src_port:  int,
                 dst_host:  str,
                 dst_port:  int,
                 seq_num:   int,
                 ack_num:   int,
                 flags:     int = 0):
        self.src_host = src_host
        self.src_port = src_port
        self.dst_host = dst_host
        self.dst_port = dst_port
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.flags = flags

    def build(self) -> bytes:
        packet = struct.pack(
            '!HHIIBBHHH',
            self.src_port,  # Source Port
            self.dst_port,  # Destination Port
            self.seq_num,              # Sequence Number
            self.ack_num,              # Acknoledgement Number
            5 << 4,         # Data Offset
            self.flags,     # Flags
            8192,           # Window
            0,              # Checksum (initial value)
            0               # Urgent pointer
        )

        pseudo_hdr = struct.pack(
            '!4s4sHH',
            socket.inet_aton(self.src_host),    # Source Address
            socket.inet_aton(self.dst_host),    # Destination Address
            socket.IPPROTO_TCP,                 # PTCL
            len(packet)                         # TCP Length
        )

        checksum = chksum(pseudo_hdr + packet)

        packet = packet[:16] + struct.pack('H', checksum) + packet[18:]

        return packet


def chksum(packet: bytes) -> int:
    if len(packet) % 2 != 0:
        packet += b'\0'

    res = sum(array.array("H", packet))
    res = (res >> 16) + (res & 0xffff)
    res += res >> 16

    return (~res) & 0xffff


def on_new_client(clientSocket, clientAddr):
    string = "Client: " + clientAddr + " has connected\n"
    print(string)


def main():
    # Create server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
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
        result = s.recv(4096)
        packet = TCPPacket(result)
        print("Before Thread")
        newClient = threading.Thread(target=on_new_client, name="FTP Client {}".format(threading.active_count() - 1), args=(client, clientAddr))
        newClient.daemon = True
        newClient.start()

if __name__ == "__main__":
    main()