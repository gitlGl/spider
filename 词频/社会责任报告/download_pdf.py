import csv,requests,os,threading,time
from fake_useragent import UserAgent

ua = UserAgent()

shen_csv_headers =['code','company' ,'year','pdf','title','id']
shang_csv_headers=['code', 'year', 'company', 'report_title', 'documentId', 'pdf']
current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))  
 


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

def download_task(url_lst,base_dir):
    list_number = readTxt("已下载.txt")
    headers = {"User-Agent": ua.random}
    for url in url_lst:
        if url["code"] in list_number:
            print(url["code"] + "-" +  url["year"],"已下载，跳过")
            continue
        print(url["code"] + "-" +  url["year"],"开始下载",threading.current_thread().ident)
       
        while True:
            try:
                print(url["pdf"])
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
       
if __name__ == '__main__':        
    # 创建一个锁
    lock = threading.Lock()          
    she_ndir = "年报/深交/"
    shang_dir = "年报/上交所/"

    # 创建多个线程
    thread1 = threading.Thread(target=download_task, args=( shen_url_lst, she_ndir))
    thread2 = threading.Thread(target=download_task, args=( shang_url_lst, shang_dir))

    thread1.start()
    thread2.start()

    # 主线程等待所有子线程执行完毕
    thread1.join()
    thread2.join()

    print("All threads finished")

