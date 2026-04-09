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
    return link

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
