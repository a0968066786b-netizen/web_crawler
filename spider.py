# import urllib3

# # 關閉不安全連線的警告
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

import requests
from bs4 import BeautifulSoup

url = "http://www.atmovies.com.tw/movie/next/"
Data = requests.get(url)
Data.encoding = "utf-8"
# print(Data.text)

sp = BeautifulSoup(Data.text, "html.parser")
result=sp.select(".filmListAllX li")
lastUpdate = sp.find("div", class_="smaller09").text[5:]#type:ignore
#print(result)
# info = ""
for item in result:
    # 這裡開始每一行都要對齊
    picture = item.find("img").get("src").replace(" ", "") # type: ignore
    title = item.find("div", class_="filmtitle").text # type: ignore
    movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")#type:ignore

    # 檢查這一行，確保它跟上一行的開頭完全垂直對齊
    hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href") # type: ignore
    
    show = item.find("div", class_="runtime").text.replace("上映日期：", "") # type: ignore
    show = show.replace("片長：", "")
    show = show.replace("分", "")
    showDate = show[0:10]
    showLength = show[13:]

    doc = {
      "title": title,
      "picture": picture,
      "hyperlink": hyperlink,
      "showDate": showDate,
      "showLength": showLength,
      "lastUpdate": lastUpdate
  }

    db = firestore.client()
    doc_ref = db.collection("電影").document(movie_id)
    doc_ref.set(doc)


    # info 這一行也要對齊
    # info += picture + "\n" + title + "\n" + hyperlink + "\n" + show + "\n\n" # type: ignore
# print("-"*30)
# print(info)#type: ignore

