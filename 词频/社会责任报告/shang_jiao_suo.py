import requests,re,csv,os,time

current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))

csv_file_path = '上交所.csv'
url = "http://query.sse.com.cn/search/getESSearchDoc.do?"
cookies = {"Cookie": 'ba17301551dcbaf9_gdp_session_id=fe0089fe-71b7-4375-80c5-2b80d625e1df; gdp_user_id=gioenc-7b87geg9%2C5463%2C53ec%2Ca8g7%2C41aadbc577b5; ba17301551dcbaf9_gdp_session_id_sent=fe0089fe-71b7-4375-80c5-2b80d625e1df; VISITED_MENU=%5B%229075%22%2C%2210766%22%5D; sseMenuSpecial=14887; ba17301551dcbaf9_gdp_sequence_ids={%22globalKey%22:94%2C%22VISIT%22:2%2C%22PAGE%22:22%2C%22VIEW_CLICK%22:68%2C%22CUSTOM%22:4%2C%22VIEW_CHANGE%22:2}'}

   
headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            'Referer': 'http://www.sse.com.cn/disclosure/listedinfo/regular/' }
def readTxt(process_file):
    if not os.path.exists(process_file):
        with open(process_file, "w") as f:
            f.write('0')
            return 0
            
    with open(process_file, "r") as f:
        data = f.read().splitlines()
        return int(data[0])
    
params = {
    #"jsonCallBack" : "jsonpCallback90069020",
    "page": 1,
    "limit": 10,
    "publishTimeEnd": "",
    "publishTimeStart": "",
    "orderByDirection": "DESC",
    "orderByKey": "create_time",
    "searchMode": "preciseMulti",
    "spaceId": 3,
    "keyword": "社会责任报告",
    "siteName": "sse",
    "keywordPosition": "title",
    "channelId": "10001",
    "channelCode": "8349,8997,9797,12971,13033,13118,12002,8361,13219,8362,12905,9857,9858,9859,9860,9862,9863,9871,9868,9865,9867",
    "_": "1712569780963"

   }

page = readTxt("上交进度.txt")
params["page"] = page + 1

    
def extract_data(raw_data):                                                                                                                                                                                                                                                                                                                 
    pdf = 'http://www.sse.com.cn/' +  raw_data['extend'][4]["value"]
    createTime = raw_data['createTime'][:10]
    year = str(int(createTime[:4]) - 1)
    
    # 提取股票代码和报告标题
    documentId = raw_data['documentId']
    code = documentId[7:][:6]
    company = raw_data['extend'][5]["value"]
    if company is None:
        company =  raw_data["title"].replace(f"[{code}]", "").replace("</em>",'').replace("<em>",'')
        
    report_title = company + createTime + "社会责任报告"
    return code,year, company,report_title,documentId,pdf

    

def shang_jiao_suo():
    res = requests.get(url,params=params,cookies=cookies,headers=headers)
    raw_data = res.json()['data']["knowledgeList"]

    while raw_data:
        data = []
        for x in raw_data:
            data.append(extract_data (x))
            # CSV 文件路径
        
        # 写入数据到 CSV 文件
        if not os.path.exists(csv_file_path):
            with open(csv_file_path, "w",newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['code', 'year', 'company', 'report_title', 'documentId', 'pdf'])
                
            
        with open(csv_file_path, 'a+', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)
            csvfile.flush()
            
        with open("上交进度.txt","w") as f:
            f.write(str(params["page"]))
            
        print( f"上交所：第{params['page']}页完成")  
        params["page"] = params["page"] + 1
        
        while True:
            try:
                time.sleep(1)
                res = requests.get(url,params=params,cookies=cookies,headers=headers)
                raw_data = res.json()['data']["knowledgeList"]
                break
                
            except Exception as e:
                print(e)
                time.sleep(60)
        

if __name__ == '__main__':
    shang_jiao_suo()
    

    
    

   
    
    








