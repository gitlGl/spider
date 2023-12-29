import  requests,json,time,csv,datetime,os
#os.chdir(sys.path[0])
current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))

headers =  {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
def countdown(seconds):
    for i in range(seconds, 0, -1):
        print(i, end='\r')
        time.sleep(1)
        
        
with open('data.csv',"w+",newline = '',encoding="utf8") as f_csv:
        csv.writer(f_csv).writerow(['up主','播放量','时间','视频分类','收藏','点赞',"分享"]) 
        
st = set()  
count = 1     
numpage = 1 
while True:
    url = f"https://api.bilibili.com/x/web-interface/popular?ps=20&pn={numpage}"
    req = requests.get(url=url,headers=headers)
    time.sleep(1)
    
    data_list = json.loads(req.text)["data"]["list"]
    if not data_list:
        count = count + 1
        print(f"五秒后开始第{count}轮拉取热门更新")
        countdown(5)
        numpage = 1
        continue
    
    f_csv = open("data.csv","a+",encoding="utf8",newline="")
    
    for item in data_list:
        if not item["aid"]  in st:
            st.add(str(item["aid"]))
            
            dt = datetime.datetime.fromtimestamp(item["ctime"])
            time_string = dt.strftime('%Y-%m-%d')
            
            csv.writer(f_csv).writerow([ item["owner"]["name"],item["stat"]["view"],
                                         time_string,item["tname"],
                                         item["stat"]["favorite"],item["stat"]["like"],
                                         item["stat"]["share"]
                                        ])
            
    numpage = numpage + 1
    f_csv.close()
            
    print(f"第{count}轮:热门累计热门数量：",len(st))
    
    if len(st) > 600:
        print("已凑够600热门数量")
        break       
    
  

    
