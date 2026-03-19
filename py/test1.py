def square(y):
  print(f"{y} 的平方為 {y**2}") 

x = int(input("請輸入整數:"))
#x += 10
#print("python程式測試", x)
if (x<=0):
	print(f"您輸入的整數是{x}，小於等於0")
else:
	print(f"您輸入的整數是{x}，大於等於0")
	for i in range(1, x+1):
		#print(i, end = ",")
		square(i)