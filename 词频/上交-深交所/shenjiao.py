import json ,csv,copy
import requests,json,os,time
from openpyxl import load_workbook
current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))  


def readTxt(file_name):# 读取已下载的公司代码
    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            f.write('')
    with open(file_name, "r") as f:
        data = f.read().splitlines()
        return data  

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
def getYear(tile:str):#获取年报标题上的年份，便于对年报进行重命名
    year = ''
    for i in tile:
        if i.isdigit():
            year += i
    if len(year) == 4:
        return year
    return False

def is_record(results):
    tem_results = copy.deepcopy(results)
    years = []
    for index1,result in enumerate(tem_results):
        title = result['title']
        year_ = getYear(result.get('title'))
        if  year_  in years:
                continue
        if "摘要"  in title:
            results.remove(result)
            continue
            
        if "取消"  in title:
              results.remove(result)
              continue
        if "英文"  in title:
             results.remove(result)
             continue
        if '说明' in title:
             results.remove(result)
             continue
       
        if "修订" in  title or "更新" in  title or "更正" in  title:
             for index2, x in enumerate( tem_results):
                 if getYear(x['title']) == year_ and index1!=index2:
                     print("更新")
                     years.append(getYear(x['title']))
                     results.remove(x)
                
    return results

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
#http://www.szse.cn/api/disc/info/download?id=c7427842-879c-4dcb-a2f2-7db95d3b10bf
#payload，获取源代码
csv_headers = ['company','code', 'year',  'pdf']
list_years = ["2015","2016","2017","2018","2019","2020","2021","2022"] # 下载所需要的年份年报
list_code = readTxt("深交所进度.txt")


for code_number in code_numbers:
    if code_numbers in list_code:
       print(f"已下载{code_number}")
       continue
    else:
       print(f"开始下载{code_number}")
   
    list_data = []
    for year in list_years:
      
        payload = {'seDate': (f"{str(int(year)+1)}-01-01",f"{str(int(year)+1)}-12-31"),
                'stock': ["{firm_id}".format(firm_id=code_number)],
                'channelCode': ["fixed_disc"],
                'pageSize': 60,
                'pageNum': '{page}'.format(page=1),
                "bigCategoryId":["010301"]
                            }
        while True:
            try:
                response = requests.post(url, headers=headers, data = json.dumps(payload))
                time.sleep(2.3)
                doc = response.json()
                datas = doc.get('data')
                break
            except Exception as e:
                print('获取失败，重新获取',e)
                time.sleep(60)
          
        datas = [x for x in datas if getYear(x.get('title'))]
        
        datas = is_record(datas)
        
        for data in datas:
            company = data.get('secName')
            year_ = getYear(data.get('title'))
            pdf = 'http://www.szse.cn/api/disc/info/download?id=' + data.get('id')
            code = code_number
            data_csv = [company, code, year_, pdf]
            
            list_data.append(data_csv)
            
    if not os.path.exists('深交所.csv'):
        with open('深交所.csv','a+',encoding="utf8",newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(csv_headers)
        
    with open('深交所.csv','a+',encoding="utf8",newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerows(list_data)
        
    with open("深交所进度.txt", 'a+') as f:
        f.write(str(code_number)+ '\n')
            
    print(f"已下载{code_number}")       
        
       