import zmq
import sys
import random
import time
import threading
import os

class Client:
    id = ""
    masterIp = "tcp://192.168.43.27:"
    masterPortList = ["9997","9998","9996"]
    services = ["Download","Upload"]
    zmqContext = zmq.Context()
    poller = zmq.Poller()
    timeOut = 1000
    uploadTimeout = 120000
    downloadedFile = []
    # constructor
    def __init__(self, clientId):
        self.id = clientId
        while True:
            try:
                print()
                self.start()
            except zmq.NotDone:
                print("Request Time out, please try again")


            
            print("To do another Service, Please press 1")
            name = input()
            if name != "1":
                print("Good bye")
                break


    # the main function of the client      
    def start(self):
        self.downloadedFile = []
        masterSocket = self.zmqContext.socket(zmq.REQ)
        masterSocket.linger = 0
        self.poller.register(masterSocket, zmq.POLLIN)
        for port in self.masterPortList:
            masterSocket.connect(self.masterIp+port)

        print("trying Connect to Master ...")
        myChoice = 0
        while(int(myChoice) != 1 and int(myChoice) != 2):
            myChoice = input("Choose one of the two services below:\n1. download\n2. upload\n")


        myChoice = int(myChoice)

        fileName = input("Enter the file name:\n")
            
        try:
            masterSocket.send_pyobj((str(self.id),self.services[myChoice-1],fileName))
        except zmq.ZMQError:
            print("error connecting to server")
            self.poller.unregister(masterSocket)
            masterSocket.close()
            return

        nodeKeepersData = None
        if(self.poller.poll(self.timeOut)):
            nodeKeepersData= masterSocket.recv_pyobj()
        else:
            print("request time out, while sending ID to server")
            self.poller.unregister(masterSocket)
            masterSocket.close()
            return
            

        if len(nodeKeepersData) == 0:
            print("All servers are busy, Please try later")
            self.poller.unregister(masterSocket)
            masterSocket.close()
            return
        
        if len(nodeKeepersData)==1:
            print("Wrong file name :((")
            self.poller.unregister(masterSocket)
            masterSocket.close()
            return

        self.poller.unregister(masterSocket)
        masterSocket.close()
        if int(myChoice) == 2:
            self.upload(fileName,nodeKeepersData)
        else:
            self.download(fileName,nodeKeepersData)


    # uploading Mp4 File
    def upload(self,fileName,nodeKeepersData):
        wrong = True # for enter the file name truly
        name = fileName
        data = None # The mp4 file
        while wrong:
            try:
                f = open(name,"rb")
            except IOError:
                print("Enter correct file name:")
                name = input()
                continue
            wrong = False
            data = f.read()
            f.close()

        print("Uploading to ip: ",nodeKeepersData[0]) 
        for i in range(1,len(nodeKeepersData)):
            print("at port: ",nodeKeepersData[i])

        s = self.zmqContext.socket(zmq.REQ)
        s.linger = 0
        self.poller.register(s,zmq.POLLIN)
        
        for i in range(1,len(nodeKeepersData)):
            s.connect(nodeKeepersData[0]+nodeKeepersData[i])
        
        s.send_pyobj((str(self.id),name,"Upload",-1,data))

        if(self.poller.poll(self.uploadTimeout)):
            s.recv_string()
            print("File "+name+" has been uploaded successfully")
        else:
            print("Can't upload the file, Please try again")
        
        self.poller.unregister(s)
        s.close()
    
    
    # downloading Mp4 File
    def download(self,fileName,nodeKeepersData):
        size = int(len(nodeKeepersData)/2)
        for i in range(0,size):
            self.downloadedFile.append("")
        i = 0
        counter = 1
        threads = []
        while (i < 2*size):
            t = threading.Thread(target = self.downloadPiece, args = (fileName,nodeKeepersData[i]+nodeKeepersData[i+1],counter,size))
            threads.append(t)
            i+= 2
            t.start()
            counter += 1
        
        for t in threads:
            t.join(self.uploadTimeout)
        
        f = open("down_"+fileName,"wb")
        for data in self.downloadedFile:
            f.write(data)
        f.close()

    def downloadPiece(self,name,target,count,size):
        print("Hello from thread ",count)
        socket = self.zmqContext.socket(zmq.REQ)
        socket.connect(target)
        socket.send_pyobj((str(self.id),name,"Download",count,size))
        self.downloadedFile[count-1] = socket.recv_pyobj()
        print(type(self.downloadedFile[count-1]),len(self.downloadedFile[count-1]))

    #stop connection when signout
    def __del__(self):
        x = 0

#c = Client(123)