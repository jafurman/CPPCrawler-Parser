from pymongo import MongoClient


cluster = MongoClient("mongodb+srv://jafbird52:<password>@cluster0.rkoqs6r.mongodb.net/?retryWrites=true&w=majority")
db = cluster["CppCrawler"]
collection = db["JoshuaFurman"]

post = {"_id": 0}

collection.insert_one(post)
