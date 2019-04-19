import zmq
import sys

portMaster = "5555"
portSlave  = "5557"

context = zmq.Context()
print ("Connecting to server...")
socketMaster = context.socket(zmq.REQ)
socketSlave  = context.socket(zmq.REQ)
socketMaster.connect("tcp://localhost:%s" % portMaster)
socketSlave.connect ("tcp://localhost:%s" % portSlave)

#  Do 10 requests, waiting each time for a response
while True:
    welcMsg = "Please Choose Service:\n1 -> Sign Up\n2 -> Login\n"
    choice = int(input(welcMsg))
    if (choice == 1):
        username = "Enter your Username:\n"
        username = input(username)
        email    = "Enter your email:\n"
        email    = input(email)
        password = "Enter your password:\n"
        password = input(password)
        mydict   = {"username": username, "email": email, "pass": password}
        socketMaster.send_pyobj(mydict)
        #  Get the reply.
        message = socketMaster.recv_string()
        print("Received reply ")
        
    elif (choice == 2):
        username = "Enter your Username:\n"
        username = input(username)
        email    = "Enter your email:\n"
        email    = input(email)
        password = "Enter your password:\n"
        password = input(password)
        mydict   = {"username": username, "email": email, "pass": password}
        socketSlave.send_pyobj(mydict)
        message = socketSlave.recv_string()
        print(message)