import pandas as pd
import os,time
url = "https://s.askci.com/stock/a/0-0?&pageNum="
def conver(number):#检查xls文件格式，调整文件内容
    tem = str(number)
    if len(tem) < 6:
        lenth = 6 - len(tem)
        for i in range(lenth):
            tem = "0" + tem
    return tem
def readTxt(file_name):# 读取已下载的公司代码
    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            f.write('0')
    with open(file_name, "r") as f:
        data = f.read().splitlines()
        return data 
lenth = readTxt("t.txt") 

for i in range(int(lenth[0])+1,260):
    print(i)
    while True:
        try:
            data = pd.read_html(url + str(i))[3]
            break
        except Exception as e:
            print(e)
            time.sleep(100)


    data = data.iloc[:,1]
    data = [conver(i) for i in data] 
    data = pd.DataFrame(data,dtype=str)
    data.to_csv("股票代码.csv",mode="a+",encoding="gbk",header=False,index=False)
    with open("t.txt","r+") as f:
        f.write(str(i))


