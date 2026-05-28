from google import genai

client = genai.Client(api_key='AIzaSyAta1jds_xeFt9qJcAs2rsN97FRRTv3V4c')

# 直接體驗最新一代的 3.5 Flash 
response = client.models.generate_content(
    model='gemini-3.5-flash',
    contents='靜宜資管有什麼特色?',
)

print(response.text)
