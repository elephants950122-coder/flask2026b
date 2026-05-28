from google import genai

client = genai.Client(api_key='AIzaSyAta1jds_xeFt9qJcAs2rsN97FRRTv3V4c')

question = input("請輸入您想要詢問AI的什麼問題?")

# 直接體驗最新一代的 3.5 Flash 
response = client.models.generate_content(
    model = 'gemini-3.5-flash',
    contents = question,
)

print(response.text)
