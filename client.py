import zmq
import sys
import time
import ClientFS

#sockets inialization
portMaster = "1234" #5556 master second port for sub/pub
portSlave1 = "5557"
portSlave2 = "5558"

context = zmq.Context()
print("Connecting to server...")
socketMaster = context.socket(zmq.REQ)
socketSlave = context.socket(zmq.REQ)

socketSlave2 = context.socket(zmq.REQ)

socketMaster.connect("tcp://192.168.43.27:%s" % portMaster)

socketSlave.connect("tcp://192.168.43.145:%s" % portSlave1)
socketSlave2.connect("tcp://localhost:%s" % portSlave2) #TODO make another client

poller = zmq.Poller()
poller.register(socketSlave, zmq.POLLIN)
poller.register(socketSlave2, zmq.POLLIN)
TIMEOUT = 3000  #timeout for all recv

test = -1

def checkTest():
    
    global test
    if test == 0:
        #slave 1 is down TODO poll
        #check if alive again
        if poller.poll(TIMEOUT):
            message = socketSlave.recv_string()
            test = -1

    elif test == 1:
        #slave 2 is down
        if poller.poll(TIMEOUT):
            message = socketSlave2.recv_string()
            test = -1

    elif test == 2:
        #check slave 1 then slave 2 if slave 1 is alive
        if poller.poll(TIMEOUT):
            message = socketSlave.recv_string()
            test = 1
            if poller.poll(TIMEOUT):
                message = socketSlave2.recv_string()
                test = -1
        #
        elif    poller.poll(TIMEOUT):
                message = socketSlave2.recv_string()
                test = 0
        else:
            test = 2




def check(switch, choice):  # master port
    global test
    if switch == 0:
        #fn flush if this server was down

        checkTest()
        if test == 2:
            print("everything still down :(, sending to master")
            mydict['choice'] = choice
            socketMaster.send_pyobj(mydict)
            message = socketMaster.recv_string()
            print(message)
            return

        if test != 0:
            socketSlave.send_pyobj(mydict)

        #check recieve from slave 1
        if poller.poll(TIMEOUT):
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

            if poller.poll(TIMEOUT):
                message = socketSlave2.recv_string()
                print(message)
            else:
                test = 2
                print("all slaves are down :(, sending to master")
                mydict['choice'] = choice
                socketMaster.send_pyobj(mydict)
                message = socketMaster.recv_string()
                print(message)
    

    elif switch == 1:

        checkTest()
        if test == 2:
            print("everything still down :(, sending to master")
            mydict['choice'] = choice
            socketMaster.send_pyobj(mydict)
            message = socketMaster.recv_string()
            print(message)
            return

        if test != 1:
            socketSlave2.send_pyobj(mydict)

        if poller.poll(TIMEOUT):
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

            if poller.poll(TIMEOUT):
                message = socketSlave.recv_string()
                print(message)
            else:
                test = 2
                print("all slaves are down :(, sending to master")
                mydict['choice'] = choice
                socketMaster.send_pyobj(mydict)
                message = socketMaster.recv_string()
                print(message)
                return
    elif switch == 2:
        mydict['choice'] = choice
        socketMaster.send_pyobj(mydict)
        message = socketMaster.recv_string()
        print(message)

    if(message == "Found"):
        return 1
    else: return 0



#  Do 10 requests, waiting each time for a response

switchNo = 1

found = 0

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

        #calculate time before send
        millisBefore = int(round(time.time() * 1000))

        socketMaster.send_pyobj(mydict)
        #  Get the reply.
        message = socketMaster.recv_string()

        #calculate time after recv
        millisAfter = int(round(time.time() * 1000))

        print("time elapsed: ", millisAfter - millisBefore, '\nRecieved message: ', message)
        
    elif choice == 2:
        username = "Enter your Username:\n"
        username = input(username)

        email = "Enter your email:\n"
        email = input(email)

        password = "Enter your password:\n"
        password = input(password)
        mydict = {"username": username, "pass": password}

        switchNo +=1
        switchNo %=3
        print("switching to server: ", switchNo+1)

        #calculate time before send
        millisBefore = int(round(time.time() * 1000))

        found = check(switchNo, choice)

        #calculate time after recv
        millisAfter = int(round(time.time() * 1000))

        print("time elapsed: ", millisAfter - millisBefore)

        if(found == 1):
            c = ClientFS.Client(username+password+email)

##TODO -200 msec delay for every DB transaction
##TODO check if slave needs to be updated after revive from bahgt
##TODO client can login from master also 

