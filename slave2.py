import zmq
import time
import sys
from  multiprocessing import Process
from  multiprocessing import Value
import pymongo 



def server_to_master(port, waitForMasterComplete): #master port
    # database connection inialization 
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["DatabaseOfSlave"]
    mycol = mydb["users2"]

    #socket inialization
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://192.168.43.27:%s" % port)
    print ("Subscriber socket running at port: ", port)
    socket.setsockopt_string(zmq.SUBSCRIBE, '') #listens to all topics
    
    while(True):
        # recieve and update the database ,TODO look at update record
        record = socket.recv_pyobj()
        # block the other process from retrieving data until this process finishes
        waitForMasterComplete.value = 1
        print("record retrieved from master ",record)
        # to test consistensy
        # time.sleep(5)
        x = mycol.insert_one(record)
        # release the other process
        waitForMasterComplete.value = 0
        print("id inserted ",x.inserted_id)
         
def server_to_client(port, waitForMasterComplete):
    # database connection inialization 
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["DatabaseOfSlave"]
    mycol = mydb["users2"]

    #socket inialization
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:%s" % port)
    print ("Slave to Client socket binded at port %s" % port)

    while True:
        # Recieve from Client login request
        message = socket.recv_pyobj()
        print ("record to be queried upon", message)

        # check for master insertion
        while (waitForMasterComplete.value == 1):
            time.sleep(0.1)
        x = mycol.find_one(message)
        print("record found : ", x)

        # Respond to Client
        if x != None:
            socket.send_string("Found")
        else:
            socket.send_string("Not Found,Pls sign up.")



if __name__ == "__main__":
    
    waitForMasterComplete = Value('i')

    Process(target=server_to_master, args=(5556,waitForMasterComplete)).start()
        
    # Now we can connect a client to all these servers
    Process(target=server_to_client, args=(5558,waitForMasterComplete)).start()