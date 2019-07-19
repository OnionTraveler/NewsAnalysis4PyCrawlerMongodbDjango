#!/usr/bin/python3
def getDatetimeByConvertingUTC2(local, isDatetime4OutputFormat=True):  # ex. local = "Asia/Taipei"
    from dateutil.tz import gettz  # gettz(...) 取得某地區之時區資訊
    from datetime import datetime
    localDatetime = datetime.utcnow().astimezone(gettz(local))  # 從標準時區(UTC)轉至目標時區(.astimezone(...))
    result = datetime.strftime(localDatetime, "%Y-%m-%d %H:%M:%S")  # Convert the datetime 「TO STRING」 format

    if isDatetime4OutputFormat == True:
        return datetime.strptime(result, '%Y-%m-%d %H:%M:%S')  # Convert the string 「TO DATETIME」 format
    else:
        return result

def convertYoutubeDeltatime2Datetime(youtubeDeltatime):
    from datetime import timedelta
    tbd = youtubeDeltatime.split(" ")  # To Be Determined
    if "秒" in tbd[1]:
        return timedelta(seconds = int(tbd[0]))
    elif "分" in tbd[1]:
        return timedelta(minutes = int(tbd[0]))
    elif "時" in tbd[1]:
        return timedelta(hours = int(tbd[0]))
    elif "天" in tbd[1]:
        return timedelta(days = int(tbd[0]))
    elif "週" in tbd[1]:
        return timedelta(days = int(tbd[0])*7)





def getResponseBySeleniumScroll(webpageAddress, pages):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('/usr/bin/chromedriver',chrome_options=chrome_options)  # 宣告一個可作為操控瀏覽器的物件driver


    driver.implicitly_wait(3) # seconds # 一般給3秒
    driver.get(webpageAddress)  # 給定欲操控的網址給這個操縱物件driver

    import time
    from random import randint
    for i in range(pages):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(randint(5,10)/10)
    return driver.page_source  # 獲取「當前」總頁面(有被預覽到)的所有源始碼！

def dataETL4YoutubeChannel(response):
    dataETL4YoutubeChannelResult = []
    # 步驟零：給定資料擷取目標
    officialWebsite4Youtube = "https://www.youtube.com"
    from bs4 import BeautifulSoup # BeautifulSoup 為 bs4.py 的一個類別
    data = BeautifulSoup(response)

    videoPublisher = data.find("span", id="channel-title").text
    target = data.find_all("div", id="dismissable")
    for t in target:
        recordInformation = {}
        # 步驟一：資料擷取Extract
        try:
            videoTitle = t.find("a", id="video-title").text
            videoAddress = officialWebsite4Youtube + t.find("a", id="video-title")["href"]
            videoRunTime = t.find("a", id="thumbnail").find("span", class_="style-scope").text

            metadata_line = t.find_all("span", class_="style-scope ytd-grid-video-renderer")
            extractionDatetime = getDatetimeByConvertingUTC2("Asia/Taipei")
            releaseDatetime = extractionDatetime - convertYoutubeDeltatime2Datetime(metadata_line[1].text)
            #viewCounts = metadata_line[0].text

            everyVideoAddressPage = BeautifulSoup(getResponseBySeleniumScroll(videoAddress, 2))  # 注意：由於本動作平均費時約8秒鐘，若擷取資料過多(target)，會影響速度
            viewCounts = everyVideoAddressPage.find("span", class_="view-count style-scope yt-view-count-renderer").text
            likeCounts = everyVideoAddressPage.find_all("yt-formatted-string", class_="style-scope ytd-toggle-button-renderer style-text")[0].text  # ["aria-label"]
            dislikeCounts = everyVideoAddressPage.find_all("yt-formatted-string", class_="style-scope ytd-toggle-button-renderer style-text")[1].text  # ["aria-label"]
            videoAbstract = everyVideoAddressPage.find("yt-formatted-string", class_="content style-scope ytd-video-secondary-info-renderer").text
        except (AttributeError, IndexError) as error:
            continue


        # 步驟二：資料轉置清洗Transform
        import re
        from datetime import datetime
        recordInformation["videoPublisher"] = videoPublisher
        recordInformation["videoTitle"] = videoTitle.replace(u'\u3000',u' ')
        recordInformation["videoAddress"] = videoAddress
        recordInformation["videoRunTime"] = re.sub(' +', '', videoRunTime.replace("\n", " "))
        recordInformation["releaseDatetime"] = datetime.strftime(releaseDatetime, '%Y-%m-%d %H:%M:%S')
        recordInformation["extractionDatetime"] = datetime.strftime(extractionDatetime, '%Y-%m-%d %H:%M:%S')
        recordInformation["viewCounts"] = float(viewCounts.replace(",", "").replace("觀看次數：", "").replace("萬次", ""))*10000 if "萬" in viewCounts else float(viewCounts.replace(",", "").replace("觀看次數：", "").replace("次", ""))
        recordInformation["likeCounts"] = int(likeCounts.replace(" ", "").replace("人表示喜歡", ""))
        recordInformation["dislikeCounts"] = int(dislikeCounts.replace(" ", "").replace("人不喜歡", ""))
        recordInformation["videoAbstract"] = videoAbstract.split("\n")[0]


        # 步驟三：資料載入到一個空串列Load
        #print(recordInformation)
        dataETL4YoutubeChannelResult.append(recordInformation)

    return dataETL4YoutubeChannelResult





def connectMongodb2GetObjectdb(ipmongodb, databaseName):  # ex. (ipmongodb, database_name) = ("mongodb://localhost:27017/", "youtubeETLdb")
    from pymongo import MongoClient
    from bson.objectid import ObjectId
    conn = MongoClient(ipmongodb)
    db = conn[databaseName]  # 等同「db = conn.<databaseName>」，但唯有「conn[databaseName]」可以指定任意databaseName名稱
    return db

def loadDatalist2Mongodb(dataList, ipmongodb, databaseName, collectionName, db = None, collection = None):
    if db == None:
        db = connectMongodb2GetObjectdb(ipmongodb, databaseName)
    if collection == None:
        collection = db[collectionName]  # 等同「collection = db.<collectionName>」，但唯有「collection = db[collectionName]」可以指定任意collectionName名稱


    insertCountsTotally = 0
    updateCountsTotally4ViewCounts = 0
    updateCountsTotally4likeCounts = 0
    updateCountsTotally4dislikeCounts = 0
    updateCountsTotally = 0

    from datetime import datetime; twodaysago = datetime.strftime(getDatetimeByConvertingUTC2("Asia/Taipei", isDatetime4OutputFormat=True) - convertYoutubeDeltatime2Datetime("2 天"), "%Y-%m-%d")
    newestCollectionRecordReference = list(collection.find({"releaseDatetime":{"$gte":twodaysago}}).sort("releaseDatetime", -1))  # 撈出資料庫裡的最新(近2天)的筆資料來與爬網資料作比對  # 附註：生成器(Generator)只能執行一次迴圈，故「可將生成器轉成list型別」才可永久使用該變數!!
    recordReferenceTotalCount = len(newestCollectionRecordReference) # 所撈出資料庫裡的最新(近2天)的筆資料筆數

    for d in dataList:  # 「準備」要insert的資料串列
        updateCounts4ViewCounts = 0
        updateCounts4likeCounts = 0
        updateCounts4dislikeCounts = 0
        recordMismatchCount = 0
        for n in newestCollectionRecordReference:
            if d["videoTitle"] == n["videoTitle"]:
                if d["viewCounts"] > n["viewCounts"]:  # 判斷是否需更新觀看次數
                    collection.update_one({"videoTitle": n["videoTitle"]}, {"$set": {"viewCounts": d["viewCounts"]}})  # 更新觀看次數
                    updateCounts4ViewCounts = 1; updateCountsTotally4ViewCounts += 1
                if d["likeCounts"] != n["likeCounts"]:  # 判斷是否需更新推文次數
                    collection.update_one({"videoTitle": n["videoTitle"]}, {"$set": {"likeCounts": d["likeCounts"]}})  # 更新推文次數
                    updateCounts4likeCounts = 1; updateCountsTotally4likeCounts += 1
                if d["dislikeCounts"] != n["dislikeCounts"]:  # 判斷是否需更新噓文次數
                    collection.update_one({"videoTitle": n["videoTitle"]}, {"$set": {"dislikeCounts": d["dislikeCounts"]}})  # 更新噓文次數
                    updateCounts4dislikeCounts = 1; updateCountsTotally4dislikeCounts += 1
                collection.update_one({"videoTitle": n["videoTitle"]}, {"$set": {"extractionDatetime": d["extractionDatetime"]}})  # 只要有資料庫裡的資料作異動，便刷新擷取時間
            else:
                recordMismatchCount += 1
        if (updateCounts4ViewCounts + updateCounts4likeCounts + updateCounts4dislikeCounts) > 0: updateCountsTotally += 1

        if recordMismatchCount == recordReferenceTotalCount:  # 若比對接果皆呈現不匹配(即所爬到的資料本身並沒有存在於資料庫中)，則recordMismatchCount會恰等於recordReferenceTotalCount，此時即可insert該筆資料到資料庫裡裡
            collection.insert_one(d); insertCountsTotally += 1
            # 備註：刪除資料： collection.delete_many({})  # 移除集合桶子： collection.drop()  # 移除資料庫： db.dropDatabase()


    # 顯示在終端，方便測試知道資料庫中的更新情況
    print("資料庫名稱：%s" % (databaseName),
          "集合桶子名稱：%s" % (collectionName),
          "比對資料庫中之總筆數：%d 筆" % recordReferenceTotalCount,
          "爬網抓取資料之總筆數：%d 筆" % len(dataList),
          "新增總筆數：{0} 筆".format(insertCountsTotally),
          "異動總筆數：{0} 筆".format(updateCountsTotally),
          "觀看次數異動次數：{} 次".format(updateCountsTotally4ViewCounts),
          "推文次數異動次數：{} 次".format(updateCountsTotally4likeCounts),
          "噓文次數異動次數：{} 次".format(updateCountsTotally4dislikeCounts),
          sep = '\n')





if __name__ == '__main__':
    # 步驟0. 顯示本程式腳本開始執行的日期時間
    startDatetime = getDatetimeByConvertingUTC2("Asia/Taipei", False); print("startDatetime:", startDatetime)

    ask = {"CTI_Television": "https://www.youtube.com/channel/UCpu3bemTQwAU8PqM4kJdoEQ/videos",  # 中天新聞(紅?)
           "TTV_NEWS": "https://www.youtube.com/user/ttvnewsview/videos",  # 台視新聞 (藍?)
           "SET_NEWS": "https://www.youtube.com/user/setnews159/videos",  # 三立新聞(綠?)
           "EBC": "https://www.youtube.com/user/newsebc/videos"}  # 東森新聞(中?)

    for a in ask:
        # 步驟1. 得到問題網址的response
        pages = 1 if 12 <= getDatetimeByConvertingUTC2("Asia/Taipei", True).hour <= 22 else 4  # 在尖峰時段講求效率(每次少量資料((pages=2)(約55筆,約7.33分鐘))，但頻率(Linux裡crontab來設定)高)
        response = getResponseBySeleniumScroll(ask[a], pages)  # pages = 4 對於新聞視頻約為一天的影片量

        # 步驟2. 將response的內容去做ETL
        dataList = dataETL4YoutubeChannel(response)

        # 步驟3. 將ETL的結果存入資料庫
        loadDatalist2Mongodb(dataList, "mongodb://127.0.0.1:27017/", "youtubeETLdb", a, db = None, collection = None)

        # 步驟4. 顯示本程式腳本結束運作的日期時間
        endDatetime = getDatetimeByConvertingUTC2("Asia/Taipei", False); print("endDatetime:", endDatetime)





    # 在ipython3裡，可直接使用下二句連線到所欲爬的網址作.find(...)等操作
    # from bs4 import BeautifulSoup
    # BeautifulSoup(getResponseBySeleniumScroll("所要觀察的網址", 2)).find(...)

    # 在ipython3裡，可直接使用下三句連線到mongodb來做操作
    # db = connectMongodb2GetObjectdb("mongodb://127.0.0.1:27017/", "youtubeETLdb")
    # collection = db["CTI_Television"]
    # collection.find_one()

    # 在mongodb裡，可用以下操作來查詢所存入的資料
    # show dbs;
    # use youtubeETLdb;  # 選擇所要使用的資料庫
    # db.CTI_Television.findOne()
    # db.CTI_Television.find().count()
    # db.CTI_Television.find().pretty()
    # db.CTI_Television.find({"releaseDatetime":{$gte:"2019-07-15"}}).count()  # 以日期來查詢
    # db.CTI_Television.find({"viewCounts":{$gte:10000}}).count()  # 以觀看次數(熱度)來查詢
    # db.CTI_Television.find({"releaseDatetime":{$gte:"2019-07-15"}, "viewCounts":{$gte:10000}}).count()  # 以日期與觀看次數(熱度)來查詢





#========================= (You MUST do the following BEFORE you execute this .py file)
# INSTALL 「Chrome & Chromedriver」 on your Linux because they have to be used with 「Selenium」 in python
# INSTALL python packages THROUGH typing in 「pip3 install Selenium beautifulsoup4 pymongo」 on your Linux Command Line
# INSTALL mongodb BY 「apt-get install -y mongodb」 OR manually
# START mongodb service(or called daemon) BY typing in 「service mongodb start」 OR 「cd /usr/mongodb/bin; ./mongod --dbpath /data/db」

#========================= (You MUST do the following BEFORE|WHEN you set up crontab -e)
# INSTALL mongodb BY 「apt-get install -y cron」
# START cron service(or called daemon) BY typing in 「service cron start」
# WHEN you set up this .py file in 「crontab -e」, you MUST add ENVironmental Variables 「LANG=zh_CN.UTF-8」 before CMD in your editor
# The following are EXAMPLES when you edit schedule in 「crontab -e」:
# */30 0-18 * * * LANG=zh_CN.UTF-8 python3 /root/NewsAnalysis4PyCrawlerMongodbDjango/PyCrawler/ETL4YoutubeChannel.py >> /root/NewsAnalysis4PyCrawlerMongodbDjango/PyCrawler/Log4ETL/log4STDout.txt 2>> /root/NewsAnalysis4PyCrawlerMongodbDjango/PyCrawler/Log4ETL/log4STDerr.txt
# 15 1 * * * LANG=zh_CN.UTF-8 python3 /root/NewsAnalysis4PyCrawlerMongodbDjango/PyCrawler/ETL4YoutubeChannel.py >> /root/NewsAnalysis4PyCrawlerMongodbDjango/PyCrawler/Log4ETL/log4STDout.txt 2>> /root/NewsAnalysis4PyCrawlerMongodbDjango/PyCrawler/Log4ETL/log4STDerr.txt


