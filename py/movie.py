import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

import requests
from bs4 import BeautifulSoup

db = firestore.client()
url = "http://www.atmovies.com.tw/movie/next/"
Data = requests.get(url)
Data.encoding = "utf-8"

sp = BeautifulSoup(Data.text, "html.parser")
lastUpdate = sp.find(class_="smaller09").text.replace("更新時間：", "")

result=sp.select(".filmListAllX li")
info = ""
total = 0
for item in result:
  total += 1
  movie_id = item.find("a").get("href").replace("/movie/", "").replace("/", "")
  title = item.find(class_="filmtitle").text
  picture = "https://www.atmovies.com.tw" + item.find("img").get("src")
  hyperlink = "https://www.atmovies.com.tw" + item.find("a").get("href")
  showDate = item.find(class_="runtime").text[5:15]

  info += movie_id + "\n" + title + "\n"
  info += picture + "\n" + hyperlink + "\n" + showDate + "\n\n"

  doc = {
      "title": title,
      "picture": picture,
      "hyperlink": hyperlink,
      "showDate": showDate,
      "lastUpdate": lastUpdate
  }

  doc_ref = db.collection("電影2B").document(movie_id)
  doc_ref.set(doc)

#print(info)
print(lastUpdate)
print("總共爬取" + str(total) + "部電影到資料庫")
