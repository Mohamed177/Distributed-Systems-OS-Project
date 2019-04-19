import zmq
import sys

portMaster = "5555" #5556 master second port for sub/pub
portSlave1 = "5557"
portSlave2 = "5558"

context = zmq.Context()
print("Connecting to server...")
socketMaster = context.socket(zmq.REQ)
socketSlave = context.socket(zmq.REQ)

socketSlave2 = context.socket(zmq.REQ)

socketMaster.connect("tcp://localhost:%s" % portMaster)

socketSlave.connect("tcp://localhost:%s" % portSlave1)
socketSlave2.connect("tcp://localhost:%s" % portSlave2) #TODO make another client

poller = zmq.Poller()
poller.register(socketSlave, zmq.POLLIN)
poller.register(socketSlave2, zmq.POLLIN)
test = -1

def checkTest():
    global test
    if test == 0:
        #slave 1 is down TODO poll
        #check if alive again
        if poller.poll(1000):
            message = socketSlave.recv_string()
            test = -1

    elif test == 1:
        #slave 2 is down
        if poller.poll(1000):
            message = socketSlave2.recv_string()
            test = -1

    elif test == 2:
        #check slave 1 then slave 2 if slave 1 is alive
        if poller.poll(1000):
            message = socketSlave.recv_string()
            test = 1
            if poller.poll(1000):
                message = socketSlave2.recv_string()
                test = -1
        #
        elif    poller.poll(1000):
                message = socketSlave2.recv_string()
                test = 0
        else:
            test = 2




def check(sock1,sock2,switch):  # master port
    global test
    if switch == 0:
        #fn flush if this server was down

        checkTest()
        if test == 2:
            print("everything still down :(")
            return

        if test != 0:
            socketSlave.send_pyobj(mydict)

        #check recieve from slave 1
        if poller.poll(1000):
            message = socketSlave.recv_string()
            print(message)
        else:
            if test == 1:
                test = 2
            else:
                test = 0
            print("slave 1 is down,trying with the next slave.")

            if test != 1 and test != 2:
                socketSlave2.send_pyobj(mydict)

            if poller.poll(1000):
                message = socketSlave2.recv_string()
                print(message)
            else:
                test = 2
                print("all slaves are down :(")

    elif switch == 1:

        checkTest()
        if test == 2:
            print("everything still down :(")
            return

        if test != 1:
            socketSlave2.send_pyobj(mydict)

        if poller.poll(1000):
            message = socketSlave2.recv_string()
            print(message)
        else:
            if test == 0:
                test = 2
            else:
                test = 1
            print("slave 2 is down,trying with the next slave.")
            if test != 0 and test != 2:
                socketSlave.send_pyobj(mydict)

            if poller.poll(1000):
                message = socketSlave.recv_string()
                print(message)
            else:
                test = 2
                print("all slaves are down :(")



#  Do 10 requests, waiting each time for a response

switchNo = 1

while True:
    welcMsg = "Please Choose Service:\n1 -> Sign Up\n2 -> Login\n"
    choice = int(input(welcMsg))
    if choice == 1:
        username = "Enter your Username:\n"
        username = input(username)
        email = "Enter your email:\n"
        email = input(email)
        password = "Enter your password:\n"
        password = input(password)
        mydict = {"username": username, "email": email, "pass": password}
        socketMaster.send_pyobj(mydict)
        #  Get the reply.
        message = socketMaster.recv_string()
        print(message)
        
    elif choice == 2:
        username = "Enter your Username:\n"
        username = input(username)

        password = "Enter your password:\n"
        password = input(password)
        mydict = {"username": username, "pass": password}

        switchNo +=1
        switchNo %=2
        print(switchNo+1)
        check(socketSlave, socketSlave2, switchNo)
##TODO -200 msec delay for every DB transaction
##TODO check if slave needs to be updated after revive from bahgdt

