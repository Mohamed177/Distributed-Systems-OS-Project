import zmq
import time
import sys
import pymongo 

# database connection inialization 
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["DATABASE"]
mycol = mydb["users8"]

portRep = "1234" #take response from client
portPub = "5556" #published socket

#sockets inialization
context = zmq.Context()

socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % portRep)
print ("Master to Client socket running at port: ", portRep)

socketPub = context.socket(zmq.PUB)
socketPub.bind("tcp://*:%s" % portPub)
print ("Publisher socket running at port: ", portPub)


def check(record):  # master port
    #check if record already exists
    x = mycol.find_one(record)
    if x != None:
        socket.send_string("you are already signed up, pls log in.")
    else:
        y = mycol.insert_one(record)
        print("inserted record with id: ", y.inserted_id)
        socket.send_string("signed up succeeded")
        socketPub.send_pyobj(record)


while True:
    # Wait for next request from client
    mydict = socket.recv_pyobj()
    if(mydict.get("choice") == 2):
        mydict.pop("choice")
        x = mycol.find_one(mydict)
        print("record found : ", x)
        # Respond to Client
        if x != None:
            socket.send_string("Found")
        else:
            socket.send_string("Not Found,Pls sign up.")
        
    else:
        print("Record to be inserted: ", mydict)
        check(mydict)