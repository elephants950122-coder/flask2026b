from google import genai

# 1. 帶入金鑰建立 Client 物件
api_key = 'AIzaSyAta1jds_xeFt9qJcAs2rsN97FRRTv3V4c'
client = genai.Client(api_key=api_key)

# 2. 建立對話（指定最新的模型，這裡以最新的 gemini-3.5-flash 為例）
chat = client.chats.create(model='gemini-3.1-flash-lite')

# 3. 發送第一輪問題
response1 = chat.send_message('靜宜資管有什麼特色')
print("--- 第一輪回應 ---")
print(response1.text)

# 4. 發送第二輪問題（模型會自動記得前面的對話脈絡）
response2 = chat.send_message('可否提供該科系相關的笑話')
print("\n--- 第二輪回應 ---")
print(response2.text)
