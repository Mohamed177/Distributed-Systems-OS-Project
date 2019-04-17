import zmq
import time
import sys
import pymongo 

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["DATABASE"]

mycol = mydb["users"]

port = "5556"

if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % port)

#while True:
#  Wait for next request from client
mydict = socket.recv_pyobj()
print(mydict)
#print ("Received request: ", message)
x = mycol.insert_one(mydict)
print(x.inserted_id)
#socket.send_string("World from %s" % port)
