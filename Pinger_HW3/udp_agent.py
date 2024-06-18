import socket
import sys
import struct


def StartAgent():
    # Default values
    host = '127.0.0.1'
    port = 1337
    
    n=len(sys.argv)
    if(n!=3):
        print(f"Invalid number of argumnets")
        return
    
    # Parsing command line arguments for customization
    for i in range(n):
        if sys.argv[i] == '-p':
            port = int(sys.argv[i + 1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))

    try:
        while True:
            # Receive PING request
            message, address = server_socket.recvfrom(1024)
            # Unpack the message according to the protocol structure
            opcode, id = struct.unpack('!II', message[:8])
            data = message[8:]
            
            # Check if the OPCODE is for a PING request
            if opcode == 0:
                # Create PING reply with OPCODE 1 and the same ID and data
                reply = struct.pack('!II', 1, id) + data
    
                # Send the PING reply to the pinger
                server_socket.sendto(reply, address)

    except Exception as e:
        server_socket.close()
        return

    # The server will run indefinitely until an error occurs or manually stopped

if __name__ == '__main__':
    StartAgent()