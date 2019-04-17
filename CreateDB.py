import pymongo 

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["DATABASE"]

mycol = mydb["users"] 
mydict = {"username": "mt", "email": "mt@g.c", "pass": "pass123"}
x = mycol.insert_one(mydict)  #insert one document
print(x.inserted_id)          #print unique id for inserted document

print(myclient.list_database_names()) #print DBs names in this DB
print(mydb.list_collection_names())   #print collection names in this DB

for x in mycol.find():
    print(x)