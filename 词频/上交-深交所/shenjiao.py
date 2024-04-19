import json ,time,datetime
import requests,json,os,time
from openpyxl import load_workbook
current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))  

def check(number):#检查xls文件格式，调整文件内容
    if type(number) == str:
        if len(number) == 6 and number.isdigit():
            return number
    if type(number) == float:
        tem = str(int(number))
        if len(tem) < 6:
            lenth = 6 - len(tem)
            for i in range(lenth):
                tem = "0" + tem
        return tem
    
    if type(number) == int:
        tem = str(number)
        if len(tem) < 6:
            lenth = 6 - len(tem)
            for i in range(lenth):
                tem = "0" + tem
        return tem
    else:
        print("格式错误：",number)
        
def getNumber(file_name_xls):#获取xls文件内的公司代码
    # 加载 Excel 文件
    workbook = load_workbook(file_name_xls)
    # 选择第一个工作表
    sheet = workbook.active
    return [cell.value for cell in sheet['A'] if check(cell.value) ]


#pdf_url = 'http://disc.static.szse.cn/download'+data.get('attachPath')


code_numbers = getNumber("深交所代码.xlsx")
# 需要的时间段
date = ["2013-12-31", "2020-5-29"]


url = 'http://www.szse.cn/api/disc/announcement/annList?random=0.8015180112682705'
headers = {'Accept':'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Connection':'keep-alive',
            'Content-Length':'92',
            'Content-Type':'application/json',
            'DNT':'1',
            'Host':'www.szse.cn',
            'Origin':'http://www.szse.cn',
            'Referer':'http://www.szse.cn/disclosure/listed/fixed/index.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
            'X-Request-Type':'ajax',
            'X-Requested-With':'XMLHttpRequest'}

#payload，获取源代码
list_years = ["2015","2016","2017","2018","2019","2020","2021","2022"] # 下载所需要的年份年报
for code_number in code_numbers:
    print(code_number)
    for year in list_years:
      
        payload = {'seDate': (f"{str(int(year)+1)}-01-01",f"{str(int(year)+1)}-12-31"),
                'stock': ["{firm_id}".format(firm_id=code_number)],
                'channelCode': ["fixed_disc"],
                'pageSize': 60,
                'pageNum': '{page}'.format(page=1)}
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        doc = response.json()
        
        datas = doc.get('data')
        print(datas)
        datas = json.dumps(datas)
        time.sleep(3)
        
        if datas != "[]":
            with open('parsed_data.txt', 'a+', encoding='utf-8') as f:
                f.write(f"{datas}\n")
      
    
   