def life(y):
  print(f"您的西元生日8位數相加結果為 {Result}")

x = input("請輸入西元生日(年月日):")

str(x)
Result = 0

for i in range(8):
	Result +=int(x[i])

life(Result)