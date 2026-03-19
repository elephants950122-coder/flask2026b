def life(y):
    # 先建立一個變數來存放加總結果
    result = 0
    
    # 使用你要求的 for range 加上索引值 y[i]
    # 因為生日是 8 位數，range(8) 會讓 i 分別是 0, 1, 2, 3, 4, 5, 6, 7
    for i in range(8):
        # 這裡就是用索引值去相加，記得要把文字轉成整數 int()
        result = result + int(y[i])
    
    # 第一次加完通常是雙位數 (例如 38)，我們再用同樣邏輯加一次變成個位數
    if result > 9:
        s_res = str(result) # 轉成字串才能用索引
        final = 0
        for i in range(len(s_res)):
            final = final + int(s_res[i])
        result = final

    # 如果加完還是兩位數 (例如 11)，再加最後一次
    if result > 9:
        s_res = str(result)
        final = 0
        for i in range(len(s_res)):
            final = final + int(s_res[i])
        result = final

    print(f"您的西元生日8位數相加結果為 {result}")

x = input("請輸入西元生日(年月日):")
# 印出第一個數字確認
#print(f"輸入的第一個數字是: {x[0]}")

# 呼叫函式執行
life(x)