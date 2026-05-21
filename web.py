import os
import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, make_response, jsonify
from datetime import datetime
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
    link += "<a href='/mis'>課程</a><hr>"
    link += "<a href='/today'>現在時間日期</a><hr>"
    link += "<a href='/me'>關於我</a><hr>"
    link += "<a href='/welcome?u=建宇&d=靜宜資管&c=資訊管理導論'>Get傳值</a><hr>"
    link += "<a href='/account'>POST傳值(帳號密碼)</a><hr>"
    link += "<a href='/math'>次方與根號運算</a><hr>"
    link += "<a href='/read'>讀取Firestore資料</a><hr>"
    link += "<a href='/read2'>讀取Firestore資料(關鍵字查詢)</a><hr>"
    link += "<a href='/search'>讀取Firestore資料(關鍵字查詢:input)</a><hr>"
    link += "<a href='/spider'>爬取子青老師本學期課程</a><hr>"
    link += "<a href='/movie1'>爬取即將上映電影</a><hr>"
    link += "<a href='/spiderMovie'>爬取即將上映電影並存入資料庫</a><hr>"
    link += "<a href='/searchMovie'>從資料庫搜尋電影</a><hr>"
    link += "<a href='/road'>台中市十大肇事路口</a><hr>"
    link += "<a href='/weather'>最新天氣預報查詢</a><hr>"
    link += "<a href='/rate'>本週新片進DB</a><hr>"
    link += "<a href='/webdemo'>聊天機器人</a><hr>"
    return link

@app.route("/webdemo")
def webdemo():
    return render_template("webdemo.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    # 取得 Dialogflow 傳來的請求資料
    req = request.get_json(force=True)
    
    # 為了避免 KeyError 當機，改用 .get() 來安全取值
    action = req.get("queryResult", {}).get("action", "")
    
    # 設定一個預設回覆
    info = "抱歉，我目前無法處理這個動作喔！"
    
    if action == "rateChoice":
        # 取得使用者輸入的分級 (因為你說 Dialogflow 已經設定好同義詞轉換了)
        rate = req.get("queryResult", {}).get("parameters", {}).get("rate", "")
        
        info = "我是林建宇設計的機器人，您選擇的電影分級是：" + rate + "，本週相關電影有：\n\n"

        # 連線到 Firestore 資料庫
        db = firestore.client()
        # 注意：這裡要確定對應到你有爬蟲寫入資料的那個集合名稱
        collection_ref = db.collection("本週新片含分級") 
        docs = collection_ref.get()
        
        result = ""
        count = 0
        
        # 開始迴圈比對資料庫
        for doc in docs:
            movie_data = doc.to_dict()
            # 比對 Dialogflow 傳來的分級是否包含在資料庫的 rate 欄位中
            if rate in movie_data.get("rate", ""):
                result += "🎬 片名：" + movie_data.get("title", "") + "\n"
                #result += "🔗 介紹：" + movie_data.get("hyperlink", "") + "\n\n"
                count += 1
        
        # 判斷有沒有找到符合條件的電影
        if count > 0:
            info += result
        else:
            info += "目前資料庫中找不到符合此分級的電影喔！"

    # 將整理好的字串包裝成 Dialogflow 看得懂的 JSON 格式回傳
    return make_response(jsonify({"fulfillmentText": info}))

@app.route("/rate")
def rate():
    #本週新片
    url = "https://www.atmovies.com.tw/movie/new/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    lastUpdate = sp.find(class_="smaller09").text[5:]
    print(lastUpdate)
    print()

    result=sp.select(".filmList")

    for x in result:
        title = x.find("a").text
        introduce = x.find("p").text

        movie_id = x.find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw/movie/" + movie_id
        picture = "https://www.atmovies.com.tw/photo101/" + movie_id + "/pm_" + movie_id + ".jpg"

        r = x.find(class_="runtime").find("img")
        rate = ""
        if r != None:
            rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
            if rr == "G":
                rate = "普遍級"
            elif rr == "P":
                rate = "保護級"
            elif rr == "F2":
                rate = "輔12級"
            elif rr == "F5":
                rate = "輔15級"
            else:
                rate = "限制級"

        t = x.find(class_="runtime").text

        t1 = t.find("片長")
        t2 = t.find("分")
        showLength = t[t1+3:t2]

        t1 = t.find("上映日期")
        t2 = t.find("上映廳數")
        showDate = t[t1+5:t2-8]

        doc = {
            "title": title,
            "introduce": introduce,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": int(showLength),
            "rate": rate,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("本週新片含分級").document(movie_id)
        doc_ref.set(doc)
    return "本週新片已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate

@app.route("/weather", methods=["GET", "POST"])
def weather():
    # 建立搜尋表單與置中樣式
    search_form = """
    <style>
        body {
            text-align: center;
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 30px auto;
        }
        input, button {
            padding: 8px;
            font-size: 16px;
        }
    </style>
    <h2>最新天氣預報查詢</h2>
    <form action="/weather" method="POST"> 
        <input type="text" name="city" placeholder="請輸入完整縣市 (如：臺中市)" style="width: 60%;">
        <button type="submit" style="cursor: pointer;">查詢</button>
    </form>
    <br><a href="/" style="text-decoration: none; color: gray;">← 回首頁</a>
    <hr>
    """

    # 使用你原本的變數 R 來組合字串
    R = search_form
    city = ""
    
    # 透過 POST 抓取輸入的縣市
    if request.method == "POST":
        city = request.form.get("city", "")
    
    # 如果沒輸入 (例如剛進網頁)，就直接回傳表單
    if not city:
        return R

    # 以下使用你原本的變數與邏輯
    city = city.replace("台", "臺")
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=rdec-key-123-45678-011121314&format=JSON&locationName=" + city
    
    try:
        Data = requests.get(url)
        JsonData = json.loads(Data.text)
        
        # 簡單檢查一下有沒有抓到該縣市的資料 (防呆)
        if not JsonData.get("records", {}).get("location", []):
            R += f"<p style='color: red;'>找不到「<strong>{city}</strong>」的天氣資料，請確認是否輸入完整的縣市。</p>"
        else:
            # 使用你原本的變數結構
            R += "<h3 style='color: #007bff;'>" + JsonData["records"]["location"][0]["locationName"] + " 最新天氣預報</h3>"
            
            Weather = json.loads(Data.text)["records"]["location"][0]["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
            Rain = json.loads(Data.text)["records"]["location"][0]["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
            
            # 將結果排版後加進 R
            R += f"<p style='font-size: 18px;'>目前天氣：<b>{Weather}</b></p>"
            R += f"<p style='font-size: 18px;'>降雨機率：<b style='color: #d9534f;'>{Rain}%</b></p>"

    except Exception as e:
        R += f"<p style='color: red;'>發生錯誤：{str(e)}</p>"

    return R

@app.route("/road")
def road():
    R = "<h1>台中市十大肇事路口(113年10月)作者:林建宇</h1><br>"
    url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"
    Data = requests.get(url)
    #print(Data.text)

    JsonData = json.loads(Data.text)
    for item in JsonData:
        R += item["路口名稱"] + ", 原因:" + item["主要肇因"] + ", 件數:" + item["總件數"] + "<br>"
    
    return R

@app.route("/searchMovie")
def searchMovie():
    db = firestore.client()
    collection_ref = db.collection("電影2B")
    docs = collection_ref.get()
    total_movies = len(docs)

    search_form = f"""
    <style>
        body {{
            text-align: center;
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 30px auto;
        }}
        img {{
            border-radius: 10px;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
        }}
    </style>
    <h2>資料庫電影搜尋</h2>
    <h4 style="color: #d9534f;">目前資料庫中共有 {total_movies} 筆電影資料</h4>
    <form action="/searchMovie" method="GET">
        <input type="text" name="q" placeholder="請輸入片名關鍵字" style="padding: 8px; font-size: 16px; width: 60%;">
        <button type="submit" style="padding: 8px 15px; font-size: 16px; cursor: pointer;">搜尋</button>
    </form>
    <br><a href="/" style="text-decoration: none; color: gray;">← 回首頁</a>
    <hr>
    """
    
    result_html = search_form
    keyword = request.args.get("q", "")
    
    # ⚠️ 這裡我們把原本的「if not keyword: return...」整段拿掉了！

    count = 0  
    last_update_str = ""  
    movie_results_html = "" 
    
    for doc in docs:
        movie_data = doc.to_dict()
        title = movie_data.get("title", "")
        
        # ✨ 關鍵修改：如果 keyword 為空字串，或者 keyword 包含在 title 中，就放行！
        if not keyword or keyword in title:
            count += 1 
            if not last_update_str:
                last_update_str = movie_data.get("lastUpdate", "未知")
            
            movie_id = doc.id
            picture = movie_data.get("picture", "")
            hyperlink = movie_data.get("hyperlink", "")
            showDate = movie_data.get("showDate", "")
            
            movie_results_html += f"<p><b>編號：</b>{movie_id}</p>"
            movie_results_html += f"<h3><a href='{hyperlink}' target='_blank' style='color: #2c3e50;'>{title}</a></h3>"
            movie_results_html += f"<p style='color: #7f8c8d;'><b>上映日期：</b>{showDate}</p>"
            movie_results_html += f"<img src='{picture}' style='max-width: 250px; margin-top: 10px;'><br><br><hr>"
            
    if count > 0:
        # 根據是不是有輸入關鍵字，顯示不同的提示文字
        if keyword:
            result_html += f"<h3 style='color: #007bff;'>本次搜尋找到 {count} 部電影</h3>"
        else:
            result_html += f"<h3 style='color: #28a745;'>以下為資料庫中所有電影</h3>"
            
        result_html += f"<p style='color: gray; font-size: 14px;'>資料庫最後更新時間：{last_update_str}</p><hr>"
        result_html += movie_results_html 
    else:
        result_html += f"<p style='color: red;'>資料庫中找不到與「<strong>{keyword}</strong>」相關的電影。</p>"
        
    return result_html


@app.route("/spiderMovie")
def spiderMovie():
    R = ""
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

    R += "網站最近更新日期" + lastUpdate + "<br>"
    R += "總共爬取" + str(total) + "部電影到資料庫"

    return R + "<a href='/'>回首頁</a>"


@app.route("/movie1")
def movie1():
    # 1. 建立網頁上的「搜尋表單 (Search Form)」
    search_form = """
    <h2>近期上映電影搜尋</h2>
    <form action="/movie1" method="GET">
        <input type="text" name="q" placeholder="請輸入片名關鍵字" style="padding: 5px; font-size: 16px;">
        <button type="submit" style="padding: 5px 10px; font-size: 16px;">搜尋</button>
    </form>
    <hr>
    """
    
    result_html = search_form
    
    # 2. 透過 Flask 的 request 取得網頁表單傳來的關鍵字
    q = request.args.get("q", "")
    
    # 如果使用者還沒輸入任何東西，提示他輸入
    if not q:
        result_html += "請在上方輸入關鍵字，然後點擊搜尋。"
        return result_html

    # 3. 開始爬蟲與資料處理
    url = "https://www.atmovies.com.tw/movie/next/"
    try:
        response = requests.get(url)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        movies = soup.select(".filmListAllX li")
        
        found_movie = False # 用來記錄有沒有找到電影
        
        for item in movies:
            img_tag = item.find("img")
            a_tag = item.find("a")
            
            # 確保有抓到標籤再繼續，避免程式崩潰
            if img_tag and a_tag:
                movie_title = img_tag.get("alt", "")
                
                # 4. 比對關鍵字
                if q in movie_title:
                    found_movie = True
                    movie_link = "https://www.atmovies.com.tw" + a_tag.get("href", "")
                    poster_url = img_tag.get("src", "")
                    
                    # 避免圖片網址本身沒帶 https 的問題
                    if not poster_url.startswith("http"):
                        poster_url = "https://www.atmovies.com.tw" + poster_url
                    
                    # 5. 組合 HTML 結果
                    result_html += f'<a href="{movie_link}" target="_blank">{movie_title}</a><br>'
                    result_html += f'<img src="{poster_url}" style="max-width: 200px; margin-top: 10px;"><br><br>'
                    
        # 如果跑完迴圈都沒有找到匹配的電影
        if not found_movie:
            result_html += f"找不到與「<strong>{q}</strong>」相關的電影。"

    except Exception as e:
        result_html += f"爬蟲發生錯誤：{str(e)}"
        
    return result_html + "<a href='/'>回首頁</a>"


@app.route("/spider")
def spider():
    result_html = ""
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    course_links = soup.select(".team-box a")

    for link in course_links:
        result_html += link.text + link.get("href", "") + "<br>"
    return result_html + "<a href='/'>回首頁</a>"


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
                    results.append(teacher)
    
    return render_template("search.html", results=results, keyword=keyword) + "<a href='/'>回首頁</a>"


@app.route("/read2")
def read2():
    result_html = ""
    keyword = "李"
    db = firestore.client()
    collection_ref = db.collection("靜宜資管")    
    docs = collection_ref.get()    
    
    for doc in docs:   
        teacher = doc.to_dict()
        if keyword in teacher.get("name", ""):      
            result_html += str(teacher) + "<br>"

    if result_html == "":
        result_html = "抱歉，查無此關鍵字姓名之老師資料"    
    return result_html + "<a href='/'>回首頁</a>"


@app.route("/read")
def read():
    result_html = ""
    db = firestore.client()
    collection_ref = db.collection("靜宜資管")    
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).get()    
    for doc in docs:         
        result_html += str(doc.to_dict()) + "<br>"    
    return result_html + "<a href='/'>回首頁</a>"


@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href='/'>返回首頁</a>"


@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html", datetime=str(now))


@app.route("/me")
def me():
    return render_template("mis2B.html")


@app.route("/welcome", methods=["GET"])
def welcome():
    user = request.values.get("u")
    d = request.values.get("d")
    c = request.values.get("c")
    return render_template("welcome.html", name=user, dep=d, course=c)


@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form.get("user", "")
        pwd = request.form.get("pwd", "")
        result_html = f"您輸入的帳號是：{user}; 密碼為：{pwd}" 
        return result_html
    else:
        return render_template("account.html")


@app.route("/math", methods=["GET", "POST"])
def math():
    if request.method == "POST":
        try:
            x = int(request.form["x"])
            y = int(request.form["y"])
            opt = request.form["opt"]

            if opt == "∧":
                result = x ** y
            elif opt == "√":
                if y == 0:
                    result = "數學不能開0次方根"
                else:
                    result = x ** (1/y)
            else:
                result = "請輸入 ∧ 或 √"
            
            return f"計算結果：{result} <br><br><a href='/math'>繼續計算</a> | <a href='/'>回首頁</a>"
            
        except ValueError:
            return "輸入格式錯誤，請確保 x 和 y 都是輸入整數！<br><a href='/math'>返回重新計算</a>"
    else:
        return render_template("math.html")


# 確保伺服器執行的程式碼只出現在整份檔案的最尾端
if __name__ == "__main__":
    app.run(debug=True)