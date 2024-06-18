#!/usr/bin/python3
import socket
import select
import sys

"""
perfom the operation y with x and z
y is one the following operations: +,-,x,/
x, y,z are strings where x,z represents integers, and y as described above
"""
def cal(x, y, z):
    x = int(x)
    z = int(z)
    if (y == '+'):
        return x + z
    if (y == '-'):
        return x - z
    if (y == 'x'):
        return x * z
    if (y == '/'):
        return round( (x / z) ,2)

"""
checks if a given string(which represents an integer) is a palindrome
"""
def check_pal(word):
    return word == word[::-1]

"""
checks if a given string(which represents an integer) is primary
"""
def check_pri(word):
    num = int(word)
    if num <= 1:
        return False
    elif num <= 3:
        return True
    elif num % 2 == 0 or num % 3 == 0:
        return False
    i = 5
    while i * i <= num:
        if num % i == 0 or num % (i + 2) == 0:
            return False
        i += 6
    return True

"""
checks if the given msg is a valid msg to get from the client while logging in
"""
def Check_LogIn_Msg(Msg):
    if(Msg==""):
        return True
    if(Msg=="Welcome!Please log in."):
        return True
    if(Msg.startswith("User: ")==True):
        temp = Msg.split(' ')
        if(len(temp)==2):
            return True
        elif(len(temp)==4 and temp[2]=="Password:"):
            return True
    
    return False

"""
checks if the given msg is a valid msg to get from the client after logging in
"""
def Check_Func_Msg(Msg):
    if(Msg==""):
        return True
    if(Msg=="quit"):
        return True
    if(Msg.startswith("is_primary: ")==True or Msg.startswith("is_palindrome: ")==True):
        temp=Msg.split(' ')
        if(len(temp)==2):
            x=temp[1]
            if(x.isnumeric()):
                return True
    if(Msg.startswith("calculate: ")==True):
        temp=Msg.split(' ')
        if(len(temp)==4):
            x=temp[1]
            z=temp[3]
            if(x.isnumeric()==False or z.isnumeric()==False):
                return False
            y=temp[2]
            if(y!="+" and y!="-" and y!="x" and y!="/"):
                return False
            if(y=="/" and int(z)==0):
                return False
            return True        
    return False

"""
the function sends the next message for each client which is waiting for 
a response.
"""
def SendMsgsToClients(sockets, logging_in_sockets, already_connected_sockets, socket_msgs):
    for soc in sockets:
        if soc in logging_in_sockets:
            if (socket_msgs[soc] == "Welcome!Please log in."):
                soc.send(socket_msgs[soc].encode())
                socket_msgs[soc] = ""
            if (socket_msgs[soc] == "Failed to login."):
                soc.send(socket_msgs[soc].encode())
                socket_msgs[soc] = ""
            if ("good to see you" in socket_msgs[soc]):
                soc.send(socket_msgs[soc].encode())
                socket_msgs[soc] = ""
                logging_in_sockets.remove(soc)
                already_connected_sockets.append(soc)
            if(socket_msgs[soc]=="connection closed" or socket_msgs[soc]=="quit"):
                soc.send(socket_msgs[soc].encode())
                logging_in_sockets.remove(soc)
                socket_msgs.pop(soc)
                soc.close()

        if soc in already_connected_sockets:
            if(socket_msgs[soc]=="connection closed"):
                soc.send(socket_msgs[soc].encode())
                already_connected_sockets.remove(soc)
                socket_msgs.pop(soc)
                soc.close()
            else:
                soc.send(socket_msgs[soc].encode())
                socket_msgs[soc] = ""

"""
the function gets the message from each client who has sent a request.
"""
def GetMsgsFromClients(sockets, logging_in_sockets, already_connected_sockets, socket_msgs, users):
    for soc in sockets:
        msg=soc.recv(1024).decode()
        if(socket_msgs[soc]!=""):
            msg=" " + msg
        if soc in logging_in_sockets:
            if(Check_LogIn_Msg(socket_msgs[soc]+ msg)==False):
                socket_msgs[soc]="connection closed"
            else:
                socket_msgs[soc]+=msg
                if ("User: " in socket_msgs[soc] and "Password:" in socket_msgs[soc]):
                    temp = socket_msgs[soc].split(' ')
                    name = temp[1]
                    password = temp[3]
                    if name in users and users[name] == password:
                        socket_msgs[soc] = "Hi " + name + ", good to see you."
                    else:
                        # Send a failed login message regardless of whether the user doesn't exist or the password is wrong
                        socket_msgs[soc] = "Failed to login."
            

        if soc in already_connected_sockets:
            if(Check_Func_Msg(msg)==False):
                socket_msgs[soc]="connection closed"
            else:
                socket_msgs[soc] = msg
                if ("is_primary:" in socket_msgs[soc]):
                    temp = socket_msgs[soc].split(' ')
                    Answer = check_pri(temp[1])
                    if (Answer == True):
                        socket_msgs[soc] = "response: Yes."
                    else:
                        socket_msgs[soc] = "response: No."
                if ("is_palindrome:" in socket_msgs[soc]):
                    temp = socket_msgs[soc].split(' ')
                    Answer = check_pal(temp[1])
                    if (Answer == True):
                        socket_msgs[soc] = "response: Yes."
                    else:
                        socket_msgs[soc] = "response: No."
                if ("calculate:" in socket_msgs[soc]):
                    temp = socket_msgs[soc].split(' ')
                    res = cal(temp[1], temp[2], temp[3])  # i think here we should think how to split
                    socket_msgs[soc] = "response: " + str(res) + "."
                if ("quit" in socket_msgs[soc]):
                    socket_msgs[soc]="quit"

"""
the main function which starts the server and communicates with the clients
"""
def StartServer():
    hostname = '0.0.0.0'  
    port=1337
    num_of_clients = 0
    Users = {}

    """if(len(sys.argv))==3:
        port=(int)(sys.argv[2])
    elif len(sys.argv)!=2:
        print("Invalid Input")
        return
    try:
        users_file=sys.argv[1]
        file=open(users_file,'r')
    except:
        print("Error opening the file.")
        return"""
    file=open('C:/Users/OdayA/Desktop/users_file.txt','r')
    for line in file:
        num_of_clients += 1
        username, password = line.strip().split(' ')
        Users[username] = password
    server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    server_socket.bind((hostname, port))

    server_socket.listen()
    socket_msgs = {}
    logging_in_sockets = []
    already_connected_sockets = []

    try:
        while True:
            readable, writeable, _ = select.select([server_socket] + logging_in_sockets + already_connected_sockets,
                                                logging_in_sockets + already_connected_sockets, [])
            if server_socket in readable:  # this means we've got a new connection handle
                client_socket, client_address = server_socket.accept()
                socket_msgs[client_socket] = "Welcome!Please log in."
                writeable.append(client_socket)
                readable.remove(server_socket)
                logging_in_sockets.append(client_socket)
            if writeable:
                SendMsgsToClients(writeable, logging_in_sockets, already_connected_sockets, socket_msgs)
            if readable:
                GetMsgsFromClients(readable, logging_in_sockets, already_connected_sockets, socket_msgs, Users)
    except:
        print("An error has occured.")
        return


if __name__ == "__main__":
    StartServer()



