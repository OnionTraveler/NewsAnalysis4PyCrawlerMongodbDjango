#!/bin/bash
#Python的Selenium套件 搭配Chromedriver驅動程式 操作Chrome瀏覽器 在Linux環境下 之安裝 (與測試範例程式.py)

#========================= (安装chrome)
apt-get clean all; apt-get update; apt-get install -y libxss1 libappindicator1 libindicator7
cd /tmp; wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome*.deb; apt-get install -f -y

#========================= (安装Chromedriver驅動程式)  
# google-chrome --version  # 確認chrome版本
# http://chromedriver.storage.googleapis.com/XXX/XXX.zip  # 找到對應版本的驅動程式下載網址
cd /tmp; wget http://chromedriver.storage.googleapis.com/75.0.3770.90/chromedriver_linux64.zip
apt-get install -y unzip; unzip chromedriver_linux64.zip
mv -f chromedriver /usr/local/share/chromedriver
ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver
ln -s /usr/local/share/chromedriver /usr/bin/chromedriver

#========================= (安装Selenium套件)
pip3 install selenium

#========================= (安装爬網常用套件)
pip3 install beautifulsoup4










#========================= (運行下述的.py測試程式，若可完全執行則表整體安裝成功)
# #!/usr/bin/python3
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options

# chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')
# driver = webdriver.Chrome('/usr/bin/chromedriver',chrome_options=chrome_options)

# driver.get("https://github.com/OnionTraveler?tab=repositories")
# print(driver.title)
# driver.save_screenshot(driver.title+".png")  # 將driver從給定的網址中所得到的畫面截圖存檔


