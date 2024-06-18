#!/usr/bin/python3
import socket
import sys

"""
the main function which connects the client to the desired server and
starts to communicate with it.
"""
def start_client():
    host = '127.0.0.1'
    port = 1337
    if(len(sys.argv))==3:
        host=(sys.argv[1])
        port=int(sys.argv[2])

    elif len(sys.argv) != 1:
        print("Invalid Input")
        return
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
        except:
            print("Error connecting to the server.")
            return
        first_attempt = True

        try:
            while True:
                if first_attempt:
                    msg = s.recv(1024).decode()
                    print(msg)
                    first_attempt = False

                username = input()
                if("User: " in username):
                    if(len(username.split(' '))==2):
                        s.send(username.encode())
                else:
                    print("Connection closed due to incorrect log in syntax.")
                    s.close()
                    return
                    

                
                password = input()
                s.send(password.encode())

                msg = s.recv(1024).decode()
                if "good to see you" in msg:
                    print(msg)
                    break

                elif "Failed to login." in msg:
                    print(msg)
                    continue

                elif "connection closed"==msg:
                    print("Connection closed due to incorrect log in syntax.")
                    return

        except:
            print("An error has occured.")
            return

        try:
            while True:
                func = input()
                s.send(func.encode())
                response = s.recv(1024).decode()
                if(response=="quit"):
                    return
                if(response=="connection closed"):
                    print("Connection closed due to an incorrect syntax or an unprovided function.")
                    return
                print(response)

        except:
            print("An error has occured.")

if __name__ == '__main__':
    start_client()
