import zmq
import time
import sys
import pymongo 

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["DATABASE"]

mycol = mydb["users"]

portRep = "5555" #take response from client
portPub = "5556" #published socket


context = zmq.Context()

socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % portRep)

socketPub = context.socket(zmq.PUB)
socketPub.bind("tcp://*:%s" % portPub)


def check(record):  # master port

    x = mycol.find_one(record)
    if x != None:
        socket.send_string("you are already signed up ,pls log in.")
    else:
        y = mycol.insert_one(record)
        print(y.inserted_id)
        socket.send_string("signed up succeeded")
        socketPub.send_pyobj(mydict)


while True:
    # Wait for next request from client
    mydict = socket.recv_pyobj()
    print(mydict)

    check(mydict)



