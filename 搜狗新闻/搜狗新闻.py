
from playwright.sync_api import Playwright, sync_playwright
import requests,re,time,csv,os
from bs4 import BeautifulSoup
from datetime import datetime

current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))  

def convert_time(time_list):
    # 当前日期时间
    current_time = datetime.now().strftime('%Y年%m月%d日')
   
    for x in range(len(time_list)):
        if "小时前" in time_list[x]:
            # 时间格式已经是YYYY-MM-DD，无需处理
            time_list[x] = current_time
            
    return  time_list

def get_hrefs(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
    
    
    while True:
        try:
            res = requests.get(url, headers=headers, timeout=10).text
            if "此验证码用于确认这些请求是您的正常行为而不是自动程序发出的，需要您协助验证。" in res:
                print("出现反爬验证码，sleep(600)")
                time.sleep(600)
                
            else:
                
                soup = BeautifulSoup(res, 'html.parser')
                next_page_link = soup.find('a', text='下一页')
                if next_page_link:
                    next_page_link = True
                else:
                    next_page_link = False
                    
                break
            
        except Exception as e:
            time.sleep(1)
            print(e,e.__traceback__.tb_lineno,e.__traceback__.tb_frame)
            return None
    
    p_source = '<p class="news-from text-lightgray">.*?<span>(.*?)</span><span>.*?</span>.*?</p>'
    sources = re.findall(p_source, res, re.S)
  

    p_date = '<p class="news-from text-lightgray">.*?<span>.*?</span><span>(.*?)</span>.*?</p>'
    dates = re.findall(p_date, res, re.S)
    dates = convert_time(dates)
    

    p_title = '<h3 class="vr-title">.*?<a id=".*?" target="_blank"  cacheStrategy=.*?href=".*?">(.*?)</a>'
    titles = re.findall(p_title, res, re.S)  # 因为正则里<h3 class="vr-title">后有换行，所以得加re.S

    titles =[re.sub(r'<em><!--red_beg-->(.*?)<!--red_end--></em>', r'\1', s) for s in titles]
    

    p_href = '<h3 class="vr-title">.*?<a id=".*?" target="_blank"  cacheStrategy=.*?href="(.*?)">.*?</a>'
    hrefs = re.findall(p_href, res, re.S)  # 因为正则里<h3 class="vr-title">后有换行，所以得加re.S


    for i in range(len(titles)):
        titles[i] = re.sub('<.*?>', '', titles[i])
        hrefs[i] = 'https://www.sogou.com' + hrefs[i]

    return sources,dates,titles,hrefs,next_page_link

def save_data(filename,data):
     
    if not os.path.exists(filename):
        f = open(filename, 'wt',encoding="utf8",newline = '')
        f_csv = csv.writer(f)
        f_csv.writerow(head)
        f_csv.writerow(data)
      
        f.close()
        return
   
    f = open(filename, 'a+',encoding="utf8",newline = '')
    f_csv = csv.writer(f)
    f_csv.writerow(data) 
    f.close() 
      
def handle_redirect(route, request):
    if request.resource_type in ["image", "media", "websocket"]:#,"stylesheet"
        route.abort("")
        return
    
    if request.url.count('/') == 2:
        print("URL错误：",request.url)
        route.abort()
        
    else:
        #print(request.url)
        route.continue_()   
        
def get_artiles(page,hrefs):
    artiles = []
    for index,x in enumerate(hrefs):
        try:
            page.goto(x,timeout=100000)
            page.wait_for_load_state("networkidle")
            time.sleep(1)
            hrefs[index] = page.url
            print(page.url)
            
        except Exception as e:
            print(e,e.__traceback__.tb_lineno,e.__traceback__.tb_frame)
            # 获取所有 <p> 标签中的文字
            
        all_p_tags = page.query_selector_all('p')
        p_texts = [tag.text_content() for tag in all_p_tags]

        # 合并所有文字内容为一个字符串
        merged_text = ''.join(p_texts)# 去除所有空格
        artile = merged_text.replace(' ', '')
        pattern = r"\|[^\|]+\||\d{3}-\d{8}|\d{3}\d{8}|\[\d+\]|\w+@[a-zA-Z0-9]+\.[a-zA-Z]+|www\.[a-zA-Z0-9]+\.[a-zA-Z]+"
        artile = re.sub(pattern, "", artile)
        artiles.append(artile)
        
    return artiles
    
def run(playwright: Playwright) -> None:
    browser = playwright.firefox.launch(headless=False)
    context = browser.new_context()
    
    # 打开页面继续操作
    page = context.new_page()
    page.route("**/*", handle_redirect)
    
    f = open("关键词.csv",encoding="utf8") 
    dics = csv.DictReader(f)   
              
    for dic in dics:
        for key,value in dic.items():
            if value == '':
                continue
            url = 'https://www.sogou.com/sogou?interation=1728053249&interV=&query=' + value + "&page=1"
            result = get_hrefs(url)
            if result:
                sources,dates,titles,hrefs,next_page_link =  result
                    
            else:
                next_page_link = False
             
            count = 2 
            while next_page_link:
                print(f"{key}:{value}第{count -1}页")
                
                #避免其他异常出现
                if len(hrefs) != 0:
                    count = count  + 1
                    print("获取到的链接:",hrefs)
                    
                else:
                    time.sleep(5)
                    print(f"重新获取获取{key}:{value}第{count -1}页的链接:")
                    continue
                
                    
                artiles = get_artiles(page,hrefs)
                
                iter_zip = zip(hrefs,titles,dates,sources,artiles)
                for data in iter_zip:
                    data_ = [*data]
                    data_.extend([key,value])
                    save_data(key + '.csv',data_)
                        
                next_url = f'https://www.sogou.com/sogou?interation=1728053249&interV=&query=' + value + "&page={count}"
                result = get_hrefs(next_url)
                if result:
                    sources,dates,titles,hrefs,next_page_link =  result
                    
                else:
                    next_page_link = False
                
            count = 2 
                   
    f.close()
    page.close()
    context.close()
    browser.close()
    
head = ["href","title","date","source","article",'分类',"关键词"]   
with sync_playwright() as playwright:
    run(playwright)
    
    