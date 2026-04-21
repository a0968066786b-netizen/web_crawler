# import urllib3

# # 關閉不安全連線的警告
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from flask import Flask, render_template, request
app = Flask(__name__)

import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

import requests
from bs4 import BeautifulSoup

@app.route("/")
def index():
    homepage = "<h1>楊子青Python網頁</h1>"
    homepage += "<a href=/mis>MIS</a><br>"
    homepage += "<a href=/today>顯示日期時間</a><br>"
    homepage += "<a href=/welcome?nick=tcyang>傳送使用者暱稱</a><br>"
    homepage += "<a href=/account>網頁表單傳值</a><br>"
    homepage += "<a href=/about>子青簡介網頁</a><br>"
    homepage += "<a href=/rwd>子青簡介網頁(響應式)</a><br>"
    homepage += "<br><a href=/read>讀取Firestore資料</a><br>"
    homepage += "<br><a href=/movie>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    return homepage

@app.route("/movie")
def movie():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"

    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".filmListAllX li")
    lastUpdate = sp.find("div", class_="smaller09").text[5:]#type:ignore
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

    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 

@app.route("/search")
def search():
    info = ""
    db = firestore.client()  
    docs = db.collection("電影").get() 
    for doc in docs:
        if "女" in doc.to_dict()["title"]:#type:ignore
            info += "片名：" + doc.to_dict()["title"] + "<br>"#type:ignore 
            info += "海報：" + doc.to_dict()["picture"] + "<br>"#type:ignore
            info += "影片介紹：" + doc.to_dict()["hyperlink"] + "<br>"#type:ignore
            info += "片長：" + doc.to_dict()["showLength"] + " 分鐘<br>" #type:ignore
            info += "上映日期：" + doc.to_dict()["showDate"] + "<br><br>" #type:ignore
    return info

@app.route("/searchQ", methods=["POST","GET"])
def searchQ():
    if request.method == "POST":
        MovieTitle = request.form["MovieTitle"]
        info = ""
        db = firestore.client()     
        collection_ref = db.collection("電影")
        docs = collection_ref.order_by("showDate").get()
        for doc in docs:
            if MovieTitle in doc.to_dict()["title"]: #type:ignore
                info += "片名：" + doc.to_dict()["title"] + "<br>" #type:ignore
                info += "影片介紹：" + doc.to_dict()["hyperlink"] + "<br>"#type:ignore
                info += "片長：" + doc.to_dict()["showLength"] + " 分鐘<br>" #type:ignore
                info += "上映日期：" + doc.to_dict()["showDate"] + "<br><br>"#type:ignore      
        return info
    else:  
        return render_template("input.html")

@app.route("/read")
def read():
    info = ""
    db = firestore.client()  
    docs = db.collection("電影").get() 
    for doc in docs:
        info += "片名：" + doc.to_dict()["title"] + "<br>"#type:ignore 
        info += "海報：" + doc.to_dict()["picture"] + "<br>"#type:ignore
        info += "影片介紹：" + doc.to_dict()["hyperlink"] + "<br>"#type:ignore
        info += "片長：" + doc.to_dict()["showLength"] + " 分鐘<br>" #type:ignore
        info += "上映日期：" + doc.to_dict()["showDate"] + "<br><br>" #type:ignore
    return info

if __name__ == "__main__":
    app.run(debug=True)