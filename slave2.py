import zmq
from multiprocessing import Process
import pymongo


def server_to_master(port="5556"):  # master port
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["DatabaseOfSlave2"]

    mycol = mydb["users"]
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:%s" % port)
    print("Running server on port: ", port)
    socket.setsockopt_string(zmq.SUBSCRIBE, '')  # listens to all topics

    while (True):
        # recieve and update the database ,TODO look at update record
        record = socket.recv_pyobj()
        print("record retrieved from master ", record)
        x = mycol.insert_one(record)
        print("id inserted", x.inserted_id)
        # print ("Received request #%s: %s" % (reqnum, message))
        # socket.send_string("World from %s" % port)


def server_to_client(ports=["5558"]):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["DatabaseOfSlave2"]

    mycol = mydb["users"]
    context = zmq.Context()
    print("Connecting to server with ports %s" % ports)
    socket = context.socket(zmq.REP)
    for port in ports:
        socket.bind("tcp://*:%s" % port)
    while True:
        message = socket.recv_pyobj()
        print(message)
        x = mycol.find_one(message)
        print(x)

        if x != None:
            socket.send_string("Found")
        else:
            socket.send_string("Not Found,Pls sign up.")


if __name__ == "__main__":
    # Now we can run a few servers
    # server_ports = range(5550,5558,2)
    # for server_port in server_ports:
    #   Process(target=server_to_master, args=(server_port,)).start()
    Process(target=server_to_master, args=(5556,)).start()

    # Now we can connect a client to all these servers
    Process(target=server_to_client, args=([5558],)).start()
