#!/bin/bash
# install automatically 
apt-get install -y mongodb


# install manually
# git clone https://github.com/OnionTraveler/dockerTECH4Mongodb.git





#========================= (RDB <---> NoSQL)
# 資料庫(database) <---> 資料庫(database)
# 表格(table) <---> 集合桶子(collection)
# 列(row) <---> 文件記錄(document)
# 行(column) <---> 屬性欄位(field)

# 顯示所有資料庫: show databases; <---> show dbs;
# 顯示所有資料庫: show tables; <---> show collections;





#========================= (DML指令對照MySQL)
# 選擇 資料庫 -> use 資料庫名稱;
# 新增 資料(列) -> INSERT INTO 表格名稱(行名稱1, 行名稱2, 行名稱3,) VALUES (對應值1, 對應值2, 對應值3);
# 修改 資料(列) -> UPDATE 表格名稱 SET 欲修改行名稱=新對應值 [WHERE 某行名稱=該對應值];
# 刪除 資料(列) -> DELETE FROM 表格名稱 [WHERE 某行名稱=該對應值];


#========================= (DML指令對照MongoDB)
# 選擇|創建 資料庫 -> use 資料庫名稱;
# 創建 集合桶子 -> db.createCollection("集合桶子名稱");
# 新增 資料(文件記錄) -> db.集合桶子名稱.insert({屬性欄位名稱1:對應值1, 屬性欄位名稱2:對應值2, 屬性欄位名稱3:對應值3});
# 修改 資料(文件記錄) -> db.集合桶子名稱.update({某屬性欄位名稱:{$eq:該對應值}}, {欲修屬性欄位名稱:新對應值}, {multi: true});
# 刪除 資料(文件記錄) -> db.集合桶子名稱.deleteMany({某屬性欄位名稱:該對應值});





#========================= (DQL指令對照MySQL)
# SELECT * FROM 表格名稱;
# SELECT * FROM 表格名稱 WHERE ...;
# WHERE 行名稱 = ...

# WHERE 行名稱 in ("A", "D")
# WHERE 行名稱1 = "A" AND 行名稱2 < 30
# WHERE 行名稱1 = "A" OR 行名稱2 < 30
# WHERE 行名稱1 = "A" AND ( 行名稱2 < 30 OR 行名稱3 LIKE "p%")

# SELECT * FROM 表格名稱 LIMIT 1;


#========================= (DQL指令對照MongoDB)  [.pretty()]
# db.集合桶子名稱.find({});
# db.集合桶子名稱.find({...: ...});
# 屬性欄位名稱:...

# 屬性欄位名稱: {$in: ["A", "D" ]}
# 屬性欄位名稱1: "A", 屬性欄位名稱2: {$lt: 30}
# $or: [{屬性欄位名稱1: "A" }, {屬性欄位名稱2: { $lt: 30 }}]
# 屬性欄位名稱1: "A", $or: [{屬性欄位名稱2: { $lt: 30 } }, {屬性欄位名稱3: /^p/ }]

# db.集合桶子名稱.findOne({});





#========================= (Query and Projection Operators)
# MySQL <---> MongoDB
# in <---> 屬性欄位名稱: {$in: [ ..., ...]}
# and <---> {..., ...}
# or <---> $or: [屬性欄位名稱1: ..., 屬性欄位名稱2: ...]
# not in <---> $nin

# = <---> $eq
# > <---> $gt
# >= <---> $gte
# < <---> { $lt: ...}
# <= <---> $lte
# != <---> $ne


