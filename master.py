import zmq
import time
import sys
import pymongo 

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["DATABASE"]

mycol = mydb["users"]

portRep = "5555"
portPub = "5556"

if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % portRep)

socketPub = context.socket(zmq.PUB)
socketPub.bind("tcp://*:%s" % portPub)

while True:
    # Wait for next request from client
    mydict = socket.recv_pyobj()
    print(mydict)
    socket.send_string("recieved")
    #x = mycol.insert_one(mydict)
    #print(x.inserted_id)
    # Send Inset Request to all SLAVES
    socketPub.send_pyobj(mydict)


