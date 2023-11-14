import  xlrd
import requests,time,json
import pandas as pd
import xlrd,os,sys
import math
import asyncio,aiohttp
import copy
current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))

class Session():
    session =   None
    async def getSession():
        if Session.session == None:
            Session.session = aiohttp.ClientSession()
            Session.session.keep_alive = False
        return Session.session
    
def chekData(number):# 检查已下载公司年报数量是否足够
    list_folder_name = next(os.walk(base_dir))[1]
    for folder_name in list_folder_name:
        list_filename = os.listdir(base_dir+folder_name)
        if len(list_filename) != number :
            print("年报数量不足请检查："+folder_name)


async def downlaodTask(item):  
    if item['number'] +item['year'] in download_Progress:
        print(f"{item['number'] +item['year']}已下载过，跳过")
        return
    session = await  Session.getSession()
    while True:
        try:
            async with semaphore:
                async with session.get(url=item['url']) as req:
                    content = await req.read()
                    break
        except Exception as e:
            print("请求失败，正在重试",e)
            time.sleep(60)
    if not os.path.exists(base_dir+ item['number'] +'/'):
        os.makedirs(base_dir+ item['number'] +'/' )
    with  open(base_dir+ item['number'] +'/'+item['number']+ "-" + item['year'] + "年度报告" + ".pdf", "wb")as f:
        f.write(content)                       
    print(f"{item['number']}-{item['year']}年报下载完成！") # 打印进度 
    with open(file_name, 'a+') as writers: # 打开文件
        writers.write(item["number"] + item['year'] +'\n') # 将内容追加到到文件尾部

async def download(url_item):# 下载年报
    task_list = []
    for url in url_item:
        if file_name_xls == '':
            task = asyncio.create_task(downlaodTask(url))
            task_list.append(task)
            if len(task_list) > 0:
                await asyncio.wait(task_list)
        else:
            await downlaodTask(url)

async def downloadError(url,stock):# 存在公司年报不带年份下载到“存在问题年报文件夹”文件夹
    session = await  Session.getSession()
    while True:
        try:
            async with semaphore:
                async with session.get(url=url) as req:
                    content = await req.read()
                    break
        except Exception as e:
            print("请求失败，正在重试",e)
            time.sleep(60)
    if not os.path.exists(dir_error+ stock +'/'):
        os.makedirs(dir_error+ stock +'/' )
    with  open(dir_error+ stock +'/'+stock+ "-" + "年度报告" + ".pdf", "wb") as f:
            f.write(content)                       
    print(f"{stock}年报下载完成！") # 打印进度


async def pageDownload(list_item):
    url_item = []
    if not list_item:# 确保json.loads(req.text)["announcements"]非空，是可迭代对象
        return
    number =''
    for item in list_item:# 遍历announcements列表中的数据，目的是排除英文报告和报告摘要，唯一确定年度报告或者更新版
        number = item["secCode"]
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
            year_  = getYear(item["announcementTitle"])
            if year_:
                item1 = {}
                item1["url"] = pdfurl
                item1["year"] = year_
                item1["number"] = number
                url_item.append(item1)
            else:#年报标题上无年份，或含年份外的其他数字
                await  downloadError(pdfurl,number)
            df = pd.DataFrame([pdfurl])
            df.to_csv('年报url.csv', mode='a', index=False, header=False)  
        else:
            adjunctUrl = item["adjunctUrl"] # "finalpage/2019-04-30/1206161856.PDF" 中间部分便为年报发布日期，只需对字符切片即可
            pdfurl = "http://static.cninfo.com.cn/" + adjunctUrl
            year_  = getYear(item["announcementTitle"])
            if year_ :
                item2 = {}
                item2["url"] = pdfurl
                item2["year"] = year_
                item2["number"] = number
                url_item.append(item2)
            else:
               await downloadError(pdfurl,number)  #存在公司年报不带年份下载到“存在问题年报文件夹”文件夹
            df = pd.DataFrame([pdfurl])
            df.to_csv('年报url.csv', mode='a', index=False, header=False)
    await download(url_item)
    
  
def getYear(tile:str):#获取年报标题上的年份，便于对年报进行重命名
    year = ''
    for i in tile:
        if i.isdigit():
            year += i
    if len(year) == 4:
        return year
    return False

def readTxt():# 读取已下载的公司代码
    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            f.write('')
    with open(file_name, "r") as f:
        data = f.read().splitlines()
        return data
    
async def get_pages(url,headers,data_):
    session = await  Session.getSession()
    while True:
        try:
            async with semaphore:
                async with session.post(url=url,data=data_,headers=headers) as req:
                    json_data = json.loads(await req.text())
                    totalAnnouncement = json_data['totalAnnouncement']#不能用网上的totalpages，有的会出错
                    a = totalAnnouncement / 30
                    totalpages = math.ceil(a)
                    break
           
        except Exception as e :
            print("请求失败，稍后重试",e)
            time.sleep(60)
    return totalpages

async def req(year,org_dict,number = ''):
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
    pages = await get_pages(url,headers,data_)
    if pages > 1:
        print(f"共{pages}页")
    for pageNum in range(1,pages+1):
        data_["pageNum"] = str(pageNum)
        session = await  Session.getSession()
        while True:
            try:
                async with semaphore:
                    async with session.post(url=url,data=data_,headers=headers) as req:
                        list_item = json.loads(await req.text())["announcements"]
                        break
            except Exception as e:
                    print("请求失败，稍后重试",e)
                    time.sleep(60)
        if file_name_xls == '':
            if year + str(pageNum) in download_Progress:
                print(f"{year + str(pageNum)}已下载过，跳过")
                continue
        await pageDownload(list_item)

       
        if file_name_xls == '': 
            print(f"{year}年第{pageNum}页下载完成！") # 打印进度
            with open(file_name, 'a+') as writers: # 打开文件
                writers.write(year + str(pageNum) +'\n') # 将内容追加到到文件尾部


async def thread_(org_dict,list_years):# 多进程调用req函数
    task_list = []
    if file_name_xls == '':
        for year in list_years:# 下载所需要的年份年报
            task = asyncio.create_task(req(year,org_dict,''))
            task_list.append(task)
    else:
        for number in list_number: # 循环公司代码
            for year in list_years:

                if number + year in download_Progress:
                    print(f"{ number + year}已下载过，跳过")
                    continue
             
                task = asyncio.create_task(req(year,org_dict,number))
                task_list.append(task)
    if len(task_list) > 0:
            await asyncio.wait(task_list)

    
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
    list_number = []
    with xlrd.open_workbook(file_name_xls) as book:
        sheets = book.sheets()
        for sheet in sheets:
            rows = sheet.nrows
            for i in range(1, rows):
                list1 = sheet.row_values(rowx=i)
                number = check(list1[0])
                if number == None:
                    continue
                else:
                    list_number.append(number)
    return list_number


async def main():

    await thread_(org_dict,list_years)
    chekData(len(list_years))# 检查已下载公司年报数量是否足够
    await Session.session.close()# 关闭session


"""
 使用方法：
    1.假设需要下载分类为农业行业的上市公司年报，需要把'trade': '',设置为对应的值，且设置file_name_xls = "",
    2.假设需要下载特定公司年报，设置file_name_xls = "公司年代码.xls",设置'trade': '','plate': '',#该参数为股市板块为空
"""
semaphore = asyncio.Semaphore(10) # 限制并发量为10
base_dir = "出口上市公司年报/"# 下载的年报存放的文件夹
dir_error = "存在问题年报/"#需要手动核实问题的年报存放的文件夹
file_name = "已下载公司代码.txt"#记录年报的下载进度
file_name_xls = ""#需要下载的公司代码所在的xls文件出口上市公司.xls
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

if file_name_xls != '':
    list_number = getNumber()#获取出口上市公司.xls文件内的公司代码，下载出口上市公司年报
org_dict = get_orgid()

if __name__ == '__main__':

    asyncio.run(main())