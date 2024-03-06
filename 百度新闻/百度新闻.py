import requests
import re,os,chardet,time,csv
from datetime import datetime

current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))  
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}

def convert_time(time_list):
    # 当前日期时间
    current_time = datetime.now().strftime('%Y-%m-%d')

    # 正则表达式匹配时间格式
    pattern = r'\d{4}-\d{2}-\d{2}'
    # 遍历时间列表并处理
    for i in range(len(time_list)):
        if re.match(pattern, time_list[i]):
            # 时间格式已经是YYYY-MM-DD，无需处理
            continue
        else:
            time_list[i] = current_time
            
    return  time_list

def remove_tags(text):
    clean_text = re.sub(r'<!--.*?-->', '', text)  # 去除<!-- -->标记
    clean_text = re.sub(r'<em>|</em>', '', clean_text)  # 去除<em> </em>标记
    clean_text = re.sub(r'<!--/s-text-->', '', clean_text)  # 去除<!--/s-text-->标记
    return clean_text

def get_num(keyword):
    url = 'http://www.baidu.com/s?tn=news&rtt=4&bsst=1&cl=2&wd=' + keyword
    text = requests.get(url, headers=headers, timeout=100).text
    # 定义正则表达式模式
    pattern = r'<span class="nums c-color-gray2">.*?(\d+).*?</span>'

    result = re.search(pattern, text)
    matched_text = result.group(1)
    print(matched_text)
  
    return int(matched_text )

def get_article(hrefs):
    articles = []
    for href in hrefs:
        try:
            article = requests.get(href, headers=headers, timeout=10).content
            encoding = chardet.detect(article)['encoding']
            article = article.decode(encoding)
        
        except:
            article = ''
            
        if article == '':
            print("爬取失败")
            continue
                  
        p_article = '<p>(.*?)</p>'
        article_main = re.findall(p_article, article)  # 获取<p>标签里的正文信息
        
        article = ''.join(article_main)  # 将列表转换成为字符串
        clean_text = re.sub(r'<.*?>', '', article)
        clean_text = re.sub(r'&nbsp;| +', ' ', clean_text)
        clean_text = re.sub(r'&\w+;', '', clean_text)
        clean_text = clean_text.strip()
        #print(clean_text)
        articles.append(clean_text)
        time.sleep(1) 
        
    return articles
    
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

def baidu(key,word):
    num = get_num(word)
    url = 'http://www.baidu.com/s?tn=news&rtt=4&bsst=1&cl=2&wd=' + word # 其中设置rtt=4则为按时间排序，如果rtt=1则为按焦点排序
    
  
    for x in range(0,num,10):
        url = url + f"&pn={x}"
        res = requests.get(url, headers=headers, timeout=10).text
        # 定义正则表达式模式
    
        p_href = '<h3 class="news-title_1YtI1 "><a href="(.*?)"'
        hrefs = re.findall(p_href, res, re.S)
        
        p_title = '<h3 class="news-title_1YtI1 ">.*?>(.*?)</a>'
        titles = re.findall(p_title, res, re.S)
        titles = [remove_tags(item) for item in  titles]
    
        p_date = '<span class="c-color-gray2 c-font-normal c-gap-right-xsmall" .*?>(.*?)</span>'
        dates = re.findall(p_date, res)
        dates = convert_time(dates)
        
        
        p_source = '<span class="c-color-gray" .*?>(.*?)</span>'
        
        sources = re.findall(p_source, res)
        
       

    
        for i in range(len(titles)):
            titles[i] = titles[i].strip()  
            titles[i] = re.sub('<.*?>', '', titles[i])  
        
        articles = get_article(hrefs)
        
       
        iter_zip = zip(hrefs,titles,dates,sources,articles)
        for data in iter_zip:
            data_ = [*data]
            data_.extend([key,value])
          
            save_data(key + '.csv',data_)
            
            
head = ["href","title","date","source","article",'分类',"关键词"]       
        
            
# 这里keywords可替换成实际待采集的数据

f = open("关键词.csv",encoding="utf8") 

dics = csv.DictReader(f)             
for dic in dics:
    for key,value in dic.items():
        if value != '':
            baidu(key,value)
    

