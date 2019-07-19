#!/usr/bin/python3
class ConvertingBetweenMongodbdataAndJsonfile:
    def __init__(self, ipmongodb, databaseName, collectionName):
        self.ipmongodb = ipmongodb
        self.databaseName = databaseName
        self.collectionName = collectionName

    # 新增一個連線到Mongodb的db物件
    def connectMongodb2GetObjectdb(self, ipmongodb, databaseName):  # ex. (ipmongodb, database_name) = ("mongodb://localhost:27017/", "youtubeETLdb")
        from pymongo import MongoClient
        from bson.objectid import ObjectId
        conn = MongoClient(ipmongodb)
        db = conn[databaseName]  # 等同「db = conn.<databaseName>」，但唯有「conn[databaseName]」可以指定任意databaseName名稱
        return db

    # 將Mongodb指定資料庫中集合桶子的每筆資料拉出存成Json檔
    def saveMongodbdataAsJsonfile(self, storageFilePath, db = None, collection = None):
        if db == None:
            db = self.connectMongodb2GetObjectdb(self.ipmongodb, self.databaseName)
        if collection == None:
            collection = db[self.collectionName]  # 等同「collection = db.<collectionName>」，但唯有「collection = db[collectionName]」可以指定任意collectionName名稱

        onion = collection.find({}, {"_id": False})
        result = []
        for o in onion:
            result.append(o)

        with open(storageFilePath, "w") as f:
            import json
            json.dump(result, f)

    # 將Json檔的每筆資料存入Mongodb指定資料庫中的集合桶子裡
    def loadJsonfile2Mongodb(self, dataFilePath, db = None, collection = None):
        if db == None:
            db = self.connectMongodb2GetObjectdb(self.ipmongodb, self.databaseName)
        if collection == None:
            collection = db[self.collectionName]  # 等同「collection = db.<collectionName>」，但唯有「collection = db[collectionName]」可以指定任意collectionName名稱

        with open(dataFilePath, "r") as f:
            import json
            result = json.load(f)

        collection.insert_many(result)





if __name__ == '__main__':
    # 將Mongodb指定資料庫中集合桶子的每筆資料拉出存成Json檔
    storageFilePath = "./data8JsonState/youtubeETLdb_CTI_Television.json"
    onion = ConvertingBetweenMongodbdataAndJsonfile("mongodb://127.0.0.1:27017/", "youtubeETLdb", "CTI_Television")
    onion.saveMongodbdataAsJsonfile(storageFilePath, db = None, collection = None)


    # 將Json檔的每筆資料存入Mongodb指定資料庫中的集合桶子裡
    #dataFilePath = "./data8JsonState/youtubeETLdb_CTI_Television.json"
    #onion = ConvertingBetweenMongodbdataAndJsonfile("mongodb://127.0.0.1:27017/", "youtubeETLdb", "CTI_Television")
    #onion.loadJsonfile2Mongodb(dataFilePath, db = None, collection = None)





#========================= (You MUST do the following BEFORE you execute this .py file)
# INSTALL python packages THROUGH typing in 「pip3 install pymongo」 on your Linux Command Line
# INSTALL mongodb BY 「apt-get install -y mongodb」 OR manually
# START mongodb service(or called daemon) BY typing in 「service mongodb start」 OR 「cd /usr/mongodb/bin; ./mongod --dbpath /data/db」


