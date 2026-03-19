def Split(x):
	x = x.split(",")
	school = x[0].replace("我是", "")
	print(f"學校:{school}")
	print(f"系級:{x[1]}")
	print(f"姓名:{x[2]}")

# 只有當直接執行 example1.py 時，這段才會跑
if __name__ == "__main__":
	Name = "我是靜宜大學,資管二B,林建宇"
	Split(Name)