import requests
from bs4 import BeautifulSoup

from flask import Flask, render_template, request
from datetime import datetime

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)

app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>歡迎進入林建宇的網站20260409</h1>"
    link += "<a href = /mis>課程</a><hr>"
    link += "<a href = /today>現在時間日期</a><hr>"
    link += "<a href = /me>關於我</a><hr>"
    link += "<a href = /welcome?u=建宇&d=靜宜資管&c=資訊管理導論>Get傳值</a><hr>"
    link += "<a href = /account>POST傳值(帳號密碼)</a><hr>"
    link += "<a href = /math>次方與根號運算</a><hr>"
    link += "<a href=/read>讀取Firestore資料</a><hr>"
    link += "<a href=/read2>讀取Firestore資料(關鍵字查詢)</a><hr>"
    link += "<a href=/search>讀取Firestore資料(關鍵字查詢:input)</a><hr>"
    link += "<a href=/spider>爬取子青老師本學期課程</a><hr>"
    link += "<a href=/movie1>爬取即將上映電影</a><hr>"
    return link

from flask import Flask, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/movie1")
def movie1():
    # 1. 建立網頁上的「搜尋表單 (Search Form)」
    # 這裡的 action="/movie1" 會將資料傳回這個同一個路由
    # name="q" 代表我們等一下要用 "q" 這個變數名稱來接收輸入值
    search_form = """
    <h2>近期上映電影搜尋</h2>
    <form action="/movie1" method="GET">
        <input type="text" name="q" placeholder="請輸入片名關鍵字" style="padding: 5px; font-size: 16px;">
        <button type="submit" style="padding: 5px 10px; font-size: 16px;">搜尋</button>
    </form>
    <hr>
    """
    
    Result = search_form
    
    # 2. 透過 Flask 的 request 取得網頁表單傳來的關鍵字
    q = request.args.get("q", "")
    
    # 如果使用者還沒輸入任何東西，提示他輸入
    if not q:
        Result += "請在上方輸入關鍵字，然後點擊搜尋。"
        return Result

    # 3. 開始爬蟲與資料處理
    url = "https://www.atmovies.com.tw/movie/next/"
    try:
        Data = requests.get(url)
        Data.encoding = "utf-8"
        sp = BeautifulSoup(Data.text, "html.parser")
        result = sp.select(".filmListAllX li")
        
        found_movie = False # 用來記錄有沒有找到電影
        
        for item in result:
            img_tag = item.find("img")
            a_tag = item.find("a")
            
            # 確保有抓到標籤再繼續，避免程式崩潰
            if img_tag and a_tag:
                movie_title = img_tag.get("alt", "")
                
                # 4. 比對關鍵字
                if q in movie_title:
                    found_movie = True
                    introduce = "https://www.atmovies.com.tw" + a_tag.get("href", "")
                    post = img_tag.get("src", "")
                    
                    # 避免圖片網址本身沒帶 https 的問題
                    if not post.startswith("http"):
                        post = "https://www.atmovies.com.tw" + post
                    
                    # 5. 組合 HTML 結果 (修正了引號與標籤格式)
                    Result += f'<a href="{introduce}" target="_blank">{movie_title}</a><br>'
                    Result += f'<img src="{post}" style="max-width: 200px; margin-top: 10px;"><br><br>'
                    
        # 如果跑完迴圈都沒有找到匹配的電影
        if not found_movie:
            Result += f"找不到與「<strong>{q}</strong>」相關的電影。"

    except Exception as e:
        Result += f"爬蟲發生錯誤：{str(e)}"
        
    return Result

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

@app.route("/spider")
def spider():
    Result = ""
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".team-box a")

    for i in result:
        Result += i.text + i.get("href") + "<br>"
    return Result

@app.route("/search", methods=["GET", "POST"])
def search():
    results = []  # 準備一個空清單來裝所有符合條件的老師
    keyword = ""
    if request.method == "POST":
        keyword = request.form.get("keyword", "")
        if keyword:
            db = firestore.client()
            collection_ref = db.collection("靜宜資管")
            docs = collection_ref.get()  # 抓取所有文件
            
            for doc in docs:
                teacher = doc.to_dict()
                # 模糊比對：只要老師姓名裡包含關鍵字，就加入清單
                if keyword in teacher.get("name", ""):
                    results.append(teacher)  # 這裡會不斷累積符合條件的人
    
    # 將包含「多位老師」的清單傳給網頁
    return render_template("search.html", results=results, keyword=keyword)

@app.route("/read2")
def read2():
    Result = ""
    keyword = "李"
    db = firestore.client()
    collection_ref = db.collection("靜宜資管")    
    docs = collection_ref.get()    
    for doc in docs:   
        teacher = doc.to_dict()
        if keyword in teacher["name"]:      
            Result += str(teacher) + "<br>"

    if Result == "":
        Result = "抱歉，查無此關鍵字姓名之老師資料"    
    return Result

@app.route("/read")
def read():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("靜宜資管")    
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).get()    
    for doc in docs:         
        Result += str(doc.to_dict()) + "<br>"    
    return Result

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>返回首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html", datetime = str(now))

@app.route("/me")
def me():
    return render_template("mis2B.html")

@app.route("/welcome", methods = ["GET"])
def welcome():
    user = request.values.get("u")
    d = request.values.get("d")
    c = request.values.get("c")
    return render_template("welcome.html", name = user, dep = d, course = c)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")


@app.route("/math", methods=["GET", "POST"])
def math():
    if request.method == "POST":
        try:
            # 對應你的 int(input())，從網頁表單取得資料並轉為整數
            x = int(request.form["x"])
            y = int(request.form["y"])
            opt = request.form["opt"]

            # 你的運算邏輯 (已修正 y=0 的 bug)
            if opt == "∧":
                result = x ** y
            elif opt == "√":
                if y == 0:
                    result = "數學不能開0次方根"
                else:
                    result = x ** (1/y)
            else:
                result = "請輸入 ∧ 或 √"
            
            # 將結果顯示在網頁上
            return f"計算結果：{result} <br><br><a href='/math'>繼續計算</a> | <a href='/'>回首頁</a>"
            
        except ValueError:
            return "輸入格式錯誤，請確保 x 和 y 都是輸入整數！<br><a href='/math'>返回重新計算</a>"
    else:
        return render_template("math.html")

if __name__ == "__main__":
    app.run(debug=True)