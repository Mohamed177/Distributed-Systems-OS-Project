import pymongo #PyMongo is a Python distribution containing tools for working with MongoDB.

#To create a database in MongoDB, start by creating a MongoClient object, then specify a connection URL with the correct ip address
#and the name of the database you want to create. MongoDB will create the database if it does not exist, and make a connection to it.


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
#In MongoDB, a database is not created until it gets content, so if this is your first time creating a database,
#you should complete the next two chapters (create collection and create document) before you check if the database exists!
#same for collection, it won't appear till a document is created

print(myclient.list_database_names()) #print DBs names in this DB
print(mydb.list_collection_names())   #print collection names in this DB

#collection ==>  table
#document   ==>  record
mycol = mydb["users"] #create a collection
mydict = {"username": "mt", "email": "mt@g.c", "pass": "pass123"}
x = mycol.insert_one(mydict)  #insert one document
print(x.inserted_id)          #print unique id for inserted document
mylist = [
  {"username": "mt1", "email": "mt@g.c1", "pass": "pass1231"},
  {"username": "mt2", "email": "mt@g.c2", "pass": "pass1232"}
]

#insert with specific ids
"""mylist = [
  {"_id" = 1,"username": "mt1", "email": "mt@g.c1", "pass": "pass1231"},
  {"_id" = 2,"username": "mt2", "email": "mt@g.c2", "pass": "pass1232"}
]"""

y = mycol.insert_many(mylist)
print(y.inserted_ids)

x = mycol.find_one() #returns the first document in the collection
print(x)

#The first parameter of the find() method is a query object. In this example we use an empty query object,
#which selects all documents in the collection.
for x in mycol.find(): #equvialent for "SELECT *"
  print(x)
#x = mycol.insert_one(mydict)

#The second parameter of the find() method is an object describing which fields to include in the result.
#This parameter is optional, and if omitted, all fields will be included in the result.
for x in mycol.find({},{ "_id": 0, "username": 1, "email": 1 }):
  print(x)
#You are not allowed to specify both 0 and 1 values in the same object (except if one of the fields is the _id field). 
#If you specify a field with the value 0, all other fields get the value 1, and vice versa
#for x in mycol.find({},{ "_id": 0, "username": 1, "email": 1, "pass" :0 }):  #error (mynf3sh aktb 3la 7agat 0 w 7agat 1 ala wl _id,
#  print(x)                                                                   #3'er kda lazm y7ot 0 ya 1 bs)

#When finding documents in a collection, you can filter the result by using a query object.
myquery = { "username": "1" }
mydoc = mycol.find(myquery)
for x in mydoc:
  print(x)
#To make advanced queries you can use modifiers as values in the query object.
"""myquery = { "address": { "$gt": "H" } }"""
#To find only the documents where the "address" field starts with the letter "S", use the regular expression {"$regex": "^S"}:
"""myquery = { "address": { "$regex": "^S" } }"""

#To delete one document, we use the delete_one() method.
#The first parameter of the delete_one() method is a query object defining which document to delete.
#Note: If the query finds more than one document, only the first occurrence is deleted.
myquery = { "address": "Mountain 21" }
mycol.delete_one(myquery)

#To delete more than one document, use the delete_many() method.
#The first parameter of the delete_many() method is a query object defining which documents to delete.
myquery = { "address": {"$regex": "^S"} }
x = mycol.delete_many(myquery)
print(x.deleted_count, " documents deleted.")

#To delete all documents in a collection, pass an empty query object to the delete_many() method:
x = mycol.delete_many({})
print(x.deleted_count, " documents deleted.")

#You can delete a table, or collection as it is called in MongoDB, by using the drop() method.
mycol.drop()