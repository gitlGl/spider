import  requests,json,time,os
#os.chdir(sys.path[0])
current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))
headers =  {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}

st = set()   
with open("data.json","a+",encoding="utf8") as f:
    f.seek(0)
    data_json = f.readlines()
    #print(data_json) 
   
for data in data_json:
    data = json.loads(data.strip('\n'))
    st.add(data["aid"])
    
numpage = 1 
while True:
    url = f"https://api.bilibili.com/x/web-interface/popular?ps=20&pn={numpage}"
    req = requests.get(url=url,headers=headers)
    time.sleep(2)
    f = open("data.json","a+",encoding="utf8")
    data_list = json.loads(req.text)["data"]["list"]
    if not data_list:
        time.sleep(5*60)#五分钟拉取一次热门
        numpage = 1
        continue
        
    for i in data_list:
        if not i["aid"]  in st:
            st.add(i["aid"])
            print("新增热门：",i["title"])
            text = json.dumps(i,ensure_ascii=False)
            f.write(text)
            f.write('\n')
    numpage = numpage + 1
    f.close()
            
    print("累计热门数量：",len(st))
    if len(st) > 600:
        print("已凑够600热门数量")
        break       
    
  

    



    
    
