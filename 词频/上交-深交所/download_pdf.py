import csv,requests,os,threading,time
shen_csv_headers = ['company', 'code', 'year', 'pdf']
shang_csv_headers=['company','code', 'type', 'year', 'date' ,"title",'pdf']
current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))  
 
shang_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
    'Referer': 'http://www.sse.com.cn/disclosure/listedinfo/regular/'}

shen_headers  = {'Accept':'application/json, text/javascript, */*; q=0.01',
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

def readTxt(file_name):# 读取已下载的公司代码
    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            f.write('')
    with open(file_name, "r") as f:
        data = f.read().splitlines()
        return data    
    
def read_csv_to_dict(filename,csv_headers):
    data = []
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, fieldnames=csv_headers)
        next(reader)  # 跳过头部行
        for row in reader:
            data.append(row)
    return data

shang_url_lst = read_csv_to_dict("上交所.csv",shang_csv_headers)
shen_url_lst = read_csv_to_dict("深交所.csv",shen_csv_headers)

def download_task(headers,url_lst,base_dir):
    list_number = readTxt("已下载.txt")
    for url in url_lst:
        if url["code"] in list_number:
            print(url["code"] + "-" +  url["year"],"已下载，跳过")
            continue
        print(url["code"] + "-" +  url["year"],"开始下载",threading.current_thread().ident)
       
        while True:
            try:
                response = requests.get(url["pdf"],headers=headers)
                response.raise_for_status()
                if not os.path.exists(base_dir +    url['code'] +'/'):
                    os.makedirs(base_dir + url['code'] +'/' )
                    
                with open(base_dir + url['code'] +'/'+url['code']+ "-" + 
                          url['year'] + "-" +url['company']+  ".pdf", "wb") as f:
                    f.write(response.content)
                    print(url["code"] +  "-" + url["year"],"下载完成")
                    
                    lock.acquire()
                    with open("已下载.txt", "a") as f:
                        f.write(url["code"] + "\n")
                        
                    lock.release()
                    
                break
            except Exception as e:
                print(e,threading.current_thread().ident)
                print("下载失败，重新下载")
                time.sleep(60)
       
if __name__ == "__mian__":         
    # 创建一个锁
    lock = threading.Lock()          
    she_ndir = "年报/深交/"
    shang_dir = "年报/上交所/"

    # 创建多个线程
    thread1 = threading.Thread(target=download_task, args=(shen_headers, shen_url_lst, she_ndir))
    thread2 = threading.Thread(target=download_task, args=(shang_headers, shang_url_lst, shang_dir))

    thread1.start()
    thread2.start()

    # 主线程等待所有子线程执行完毕
    thread1.join()
    thread2.join()

    print("All threads finished")

