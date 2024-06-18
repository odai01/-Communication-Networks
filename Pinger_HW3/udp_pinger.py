import socket
import time
import sys
import struct

def StartPinger():
    # Default values for parameters
    server_ip = '127.0.0.1' 
    server_port = 1337
    count = 10  
    timeout = 1  
    data_size=100 

    #  Checking than the number of arguments is valid
    n=len(sys.argv)
    if(n!=2 and n!=4 and n!=6 and n!=8 and n!=10):
        print(f"Invalid number of argumnets")
        return
    # Parsing command line arguments for customization
    # If the number of argument is valid we assume the command line arguments follow the format: <IP> -p <port> -s <size> -c <count> -t <timeout>
    for i in range(n):
        if i==1:
           server_ip = sys.argv[1]
        elif sys.argv[i] == '-p':
            server_port = int(sys.argv[i + 1])
        elif sys.argv[i] == '-s':
            data_size = int(sys.argv[i + 1])
        elif sys.argv[i] == '-c':
            count = int(sys.argv[i + 1])
        elif sys.argv[i] == '-t':
            timeout = float(sys.argv[i + 1])/1000 

    addr = (server_ip, server_port)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)
    num_of_recieved_packets=0
    for i in range(count):
        OPCODE = 0
        ID = i
        DATA = b'x' * data_size  
        message = struct.pack('!II', OPCODE, ID) + DATA
        try:
            client_socket.sendto(message, addr)
            start_time = time.time()
            received_message, server = client_socket.recvfrom(1024)
            num_of_recieved_packets+=1
            rtt = (time.time() - start_time)*1000
            X= len(received_message)
            print(f"{X} bytes from {server_ip}: seq={ID} rtt={rtt:.3f} ms")
        except socket.timeout:
            print(f"request timeout for icmp_seq {ID}")

    lost_packets=(count-num_of_recieved_packets)/count
    print(f"--- {server_ip} statistics ---")
    print(f"{count} packets transmitted, {num_of_recieved_packets} packets recieved, {lost_packets}% packet loss")
    client_socket.close()



if __name__ == '__main__':
    StartPinger()