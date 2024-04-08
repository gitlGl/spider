import requests
import random
import json
import time
import csv,os

current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))
keyword = "社会责任报告"

#定义csv字段，存储PDF链接信息至data/csr_links.csv
csvf = open('深交.csv', 'a+', encoding='utf-8', newline='')
fieldnames = ['id', 'name', 'code', 'date', 'title', 'pdf_link', 'size']
writer = csv.DictWriter(csvf, fieldnames=fieldnames)
writer.writeheader()

#伪装头
headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
           'Content-Type': 'application/json',
           'Host': 'www.szse.cn',
           'Origin': 'http://www.szse.cn',
           'Proxy-Connection': 'close',
           'Referer': 'http://www.szse.cn/disclosure/listed/fixed/index.html',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
           'X-Request-Type': 'ajax',
           'X-Requested-With': 'XMLHttpRequest'}




def readTxt(process_file):
    if not os.path.exists(process_file):
        with open(process_file, "w") as f:
            f.write('0')
            return 0
            
    with open(process_file, "r") as f:
        data = f.read().splitlines()
        return int(data[0])
    
page = readTxt("深交进度.txt")


#post方法参数
payload ={"seDate": ["",""],
           "searchKey": [keyword],
           "channelCode": ["listedNotice_disc"],
           "pageSize": 50,
           "pageNum": page + 1}

#发起请求
url = 'http://www.szse.cn/api/disc/announcement/annList?random={}'.format(random.random())
resp = requests.post(url,
                     headers=headers,
                     data=json.dumps(payload))

#当data关键词有对应的非空列表，循环一直进行。
while resp.json()['data']:
    time.sleep(1)
    count = 0 
    while True:
        count = count + 1
        if count > 5:
            break
        try:
            resp = requests.post(url,
                     headers=headers,
                     data=json.dumps(payload))
            break
        except Exception as e:
            print(e)

    
    
    csrs = resp.json()['data']
    for csr in csrs:
        #以字典样式写入csv
        data = {'pdf_link': 'http://disc.static.szse.cn/download'+ csr['attachPath'],
                'code': str(csr['secCode'][0]),
                'name': csr['secName'][0],
                'title': csr['title'],
                'date': csr['publishTime'],
                'size': csr['attachSize'],
                'id': csr['id']}
        writer.writerow(data)
             
    print( f"第{payload['pageNum']}页完成")
        
    payload['pageNum'] = payload['pageNum'] + 1
              
    with open("深交进度.txt","w") as f:
        f.write(str(payload['pageNum']))
        f.flush()

    
#关闭csv
csvf.close()
