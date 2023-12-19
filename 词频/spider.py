import requests,time,json
import csv,re
import os
import psutil,math
from concurrent.futures import ThreadPoolExecutor
import threading
import copy
from openpyxl import load_workbook
#os.chdir(sys.path[0])
current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))

def chekData(number):# 检查已下载公司年报数量是否足够
    for root, dirs, files in os.walk(base_dir):
        if len(files) != number:
            if root != base_dir:
                print("年报数量不足请检查："+root)

def download(url_item):# 下载年报
    fname = open(file_name, "a")
    for url in url_item:
        if url['number']+url['year'] in download_Progress:
            print(f"{ url['number']+url['year']}已下载过，跳过") # 打印进度
            continue
        while True:
            try:
                    r = session.get(url['url'])
                    break
            except:
                print("请求失败，正在重试")
        if not os.path.exists(base_dir+ url['number'] +'/'):
            os.makedirs(base_dir+ url['number'] +'/' )
        with open(base_dir+ url['number'] +'/'+url['number']+ "-" + url['year'] + "-" +url['name']+  ".pdf", "wb") as f:
            f.write(r.content)                    
            print(f"{url['number']}-{url['year']}年报下载完成！") # 打印进度
        with open(file_name, "a") as fname:
            fname.write(url['number']+url['year'] +'\n') # 将内容追加到到文件尾部
    fname.close()

def downloadError(url,number,name):# 存在公司年报不带年份下载到“存在问题年报文件夹”文件夹
    while True:
        try: 
                r = session.get(url)
                break
        except:
            print("请求失败，正在重试")
            time.sleep(60)
    if not os.path.exists(dir_error+ number +'/'):
        os.makedirs(dir_error+ number +'/' )
    with open(dir_error+ number +'/'+number+ "-" + name  + ".pdf", "wb") as f:    
        f.write(r.content) 
    print(f"{number}年报下载完成！") # 打印进度


def getYear(tile:str):#获取年报标题上的年份，便于对年报进行重命名
    year = ''
    for i in tile:
        if i.isdigit():
            year += i
    if len(year) == 4:
        return year
    return False


def pageDownload(year,pageNum,req):
    url_item = []
    list_item = json.loads(req.text)["announcements"]
    
    with lock:
        if not list_item:# 确保json.loads(req.text)["announcements"]非空，是可迭代对象
            return
        
        if not os.path.exists('年报元数据.csv'):
            with open('年报元数据.csv',"a+",newline = '') as csv_f:
                csv.writer(csv_f).writerow(list_item[0].keys())
            
        with open('年报元数据.csv',"a+",newline = '') as csv_f:
            writer = csv.writer(csv_f)
            for item in list_item:
                writer.writerow(item.values())

    for item in list_item:# 遍历announcements列表中的数据，目的是排除英文报告和报告摘要，唯一确定年度报告或者更新版
        number = item["secCode"]
        invalid_chars = r'[\\/:"*?<>|]'
        name = re.sub(invalid_chars, '',item['secName'] )
        year_  = getYear(item["announcementTitle"])
        if not year_ in list_years:
            continue
        if "摘要"  in item["announcementTitle"]:
            continue
        if "取消"  in item["announcementTitle"]:
            continue
        if "英文"  in item["announcementTitle"]:
            continue
        if '说明' in item["announcementTitle"]:
            continue
        if "修订" in item["announcementTitle"] or "更新" in item["announcementTitle"] or "更正" in item["announcementTitle"]:
            adjunctUrl = item["adjunctUrl"] # "finalpage/2019-04-30/1206161856.PDF" 中间部分便为年报发布日期，只需对字符切片即可
            pdfurl = "http://static.cninfo.com.cn/" + adjunctUrl
            
            if year_:
                item1 = {}
                item1["url"] = pdfurl
                item1["year"] = year_
                item1["number"] = number
                item1['name'] = name
                url_item.append(item1)
            else:#年报标题上无年份，或含年份外的其他数字
                downloadError(pdfurl,number)
            # df = pd.DataFrame([pdfurl])
            # df.to_csv('年报url.csv', mode='a', index=False, header=False)
            with lock:  
                with open('年报url.csv',"a+",newline = '') as csv_f:
                    csv.writer(csv_f).writerow([pdfurl])
                    
        else:
            adjunctUrl = item["adjunctUrl"] # "finalpage/2019-04-30/1206161856.PDF" 中间部分便为年报发布日期，只需对字符切片即可
            pdfurl = "http://static.cninfo.com.cn/" + adjunctUrl
            year_  = getYear(item["announcementTitle"])
            if year_ :
                item2 = {}
                item2["url"] = pdfurl
                item2["year"] = year_
                item2["number"] = number
                item2['name'] = name
                url_item.append(item2)
            else:
                downloadError(pdfurl,number,name)  #存在公司年报不带年份下载到“存在问题年报文件夹”文件夹
            # df = pd.DataFrame([pdfurl])
            # df.to_csv('年报url.csv', mode='a', index=False, header=False)
            with lock:
                with open('年报url.csv',"a+",newline = '') as csv_f:
                    csv.writer(csv_f).writerow([pdfurl])
    download(url_item)
    if file_name_xls =='':
        print(f"{year}年{pageNum}页下载完成！") # 打印进度
        with open(file_name, "a") as fname:
            fname.write(f"{year + pageNum}\n") # 将内容追加到到文件尾部


def get_pages(url,headers,data_):
    while True:
        try:
                req = session.post(url,data=data_,headers=headers)
                json_data = json.loads(req.text)
                break
        except Exception as e :
            print("请求失败，稍后重试",e)
            time.sleep(60)
    
    
    totalAnnouncement = json_data['totalAnnouncement']#不能用网上的totalpages，有的会出错
    a = totalAnnouncement / 30
    totalpages = math.ceil(a)
    return totalpages

def req(year,org_dict,number = ''): # 传入年份，机构字典，股票代码

    # post请求地址（巨潮资讯网的那个查询框实质为该地址）
    url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    # 表单数据，需要在浏览器开发者模式中查看具体格式
    data_ = copy.deepcopy(data)
   
    data_["seDate"] = f"{str(int(year)+1)}-01-01~{str(int(year)+1)}-12-31"
    if number == '':
        data_["stock"] = ''
    else:
        data_["stock"] = number + "," + org_dict[number]
        
    # 请求头
    headers =  {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
    # 发起请求
    pages = get_pages(url,headers,data_)+1
    if pages > 2:
        print(f"共{pages-1}页")
    if file_name_xls != "":
        for pageNum in range(1,pages):
            data_["pageNum"] = str(pageNum)
            while True:
                try:   
                        req = session.post(url,data=data_,headers=headers)
                        break
                except:
                    print("请求失败，稍后重试")
                    time.sleep(60)
            pageDownload(year,pageNum,req)
    else:
        with ThreadPoolExecutor(max_workers=5) as executor: 
            for pageNum in range(1,pages+1):
                data_["pageNum"] = str(pageNum)
                while True:
                    try:
                            req = session.post(url,data=data_,headers=headers)
                            break
                    except:
                        print("请求失败，稍后重试")
                        time.sleep(60)
                if year + str(pageNum) in download_Progress:
                    print(f"{year + str(pageNum)}已下载过，跳过")
                    continue
                executor.submit(pageDownload,year,str(pageNum),req)
            executor.shutdown(wait=True)

def thread_(number,org_dict,list_years):# 多进程调用req函数
    #输出线程id
    for year in list_years:# 下载所需要的年份年报
        if number + year in download_Progress:
            print(f"{ number + year}已下载过，跳过")
            continue
        print(f"正在下载{year},{number}年报")
        req(year,org_dict,number)# 调用req函数
        time.sleep(0.5)# 适当休眠，避免爬虫过快

def get_orgid():#获取A股公司代码对应的OrgId,用于构造表单数据
    org_dict = {}
    while True:
        try:
            org_json = requests.get("http://www.cninfo.com.cn/new/data/szse_stock.json").json()["stockList"]
            break
        except Exception as e:
            print("获取公司代码失败60秒后重试",e)
            time.sleep(61)

    for i in range(len(org_json)):
        org_dict[org_json[i]["code"]] = org_json[i]["orgId"]
      

    return org_dict
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
    else:
        print("格式错误：",number)
def getNumber():#获取xls文件内的公司代码
    # 加载 Excel 文件
    workbook = load_workbook(file_name_xls)
    # 选择第一个工作表
    sheet = workbook.active
    return [cell.value for cell in sheet['A']]

def main():

    if file_name_xls != '':
        with ThreadPoolExecutor(max_workers=psutil.cpu_count()+3) as executor: # 创建线程池，最大线程数为10
            for number in list_number: # 循环公司代码
                executor.submit(thread_,number,org_dict,list_years)
            executor.shutdown(wait=True)
    else:
        thread_('',org_dict,list_years)
    chekData(len(list_years))# 检查已下载公司年报数量是否足够

def readTxt():# 读取已下载的公司代码
    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            f.write('')
    with open(file_name, "r") as f:
        data = f.read().splitlines()
        return data    

"""
 建议有能力的同学重构代码，把代码改为数据清洗与网络请求分离，这种方式能更精准获取需要的信息
 使用方法：
    1.假设需要下载分类为农业行业的上市公司年报，需要把'trade': '',设置为对应的值，且设置file_name_xls = "",
    2.假设需要下载特定公司年报，设置file_name_xls = "公司年代码.xls",设置'trade': '','plate': '',#该参数为股市板块为空
"""
session = requests.session()
lock = threading.Lock()
base_dir = "出口上市公司年报/"# 下载的年报存放的文件夹
dir_error = "存在问题年报/"#需要手动核实问题的年报存放的文件夹
file_name = "已下载公司代码.txt"#记录年报的下载进度
file_name_xls = ""#需要下载的公司代码所在的xls文件,出口上市公司.xls
download_Progress = readTxt()# 读取已下载进度
list_years = ["2015","2016","2017","2018","2019","2020","2021"] # 下载所需要的年份年报
data  = {
        "pageNum":"1",
        "pageSize":"30",
        "tabName":"fulltext",
        "stock":'' ,# 公司代码
        "seDate":'',#构造时间参数
        "column":"szse",
        "category":"category_ndbg_szsh",#类型为年报
        "isHLtitle": "true",
        "sortName":"time",
        "sortType": "desc",
        'trade': '',#该参数为行业
        'plate': '',#该参数为股市板块
        }
if file_name_xls != "":
    list_number = getNumber()#获取出口上市公司.xls文件内的公司代码，下载出口上市公司年报
org_dict = get_orgid()
if __name__ == '__main__':    
   main()
   session.close()


