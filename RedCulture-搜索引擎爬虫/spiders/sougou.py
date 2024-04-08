from playwright.sync_api import sync_playwright
import re,csv,time
from bs4 import BeautifulSoup
from datetime import datetime
from scrapy import Spider
from scrapy.http import Request
from twisted.internet.error import (DNSLookupError, TCPTimedOutError, 
                                    ConnectionLost,TimeoutError,ConnectionRefusedError)

from urllib.parse import urlparse

class SouGou(Spider):
    
    def __init__(self, url_set=None, *args, **kwargs):
        super(SouGou, self).__init__(*args, **kwargs)
        self.url_set = url_set
        
        
   
    name = "sougou"   
    
    def handle_redirect(self,route, request):
        if request.resource_type in ["image", "media", "websocket"]:#,"stylesheet"
            route.abort("")
            return
        
        if request.url.count('/') == 2:
            print("URL错误：",request.url)
            route.abort()
            
        else:
            #print(request.url)
            route.continue_() 
              
    def start_requests(self):
        """
        爬虫入口,重写该函数
        
        """
        f = open("关键词.csv",encoding="utf8")
       
        dics = csv.DictReader(f)
        with sync_playwright() as playwright:
            browser = playwright.firefox.launch(headless=True)
            context = browser.new_context(ignore_https_errors=True)
            self.context = context
                    
            for dic in dics:
                for key,value in dic.items():
                
                    if value != '':
                        page_num = 1 
                        url = f'https://www.sogou.com/sogou?interation=1728053249&interV=&query={value}&page={page_num}'
                        time.sleep(0.5) 
                        while url   in self.url_set: 
                            print(f"搜狗：{key}:{value}：第{page_num}页已下载")
                            page_num = page_num + 1 
                            url = f'https://www.sogou.com/sogou?interation=1728053249&interV=&query={value}&page={page_num}'
                        
                        yield Request(url, callback=self.parse, dont_filter=True,errback=self.on_error,
                                    cb_kwargs={"key":key,'value':value,'page_num': page_num,"context":self.context})
                    
                    
        f.close()
        context.close()
        browser.close()  
        
    def on_error(self, failure):
            
        if failure.check(DNSLookupError, TCPTimedOutError, 
                                    ConnectionLost,TimeoutError,ConnectionRefusedError):
            self.crawler.engine.schedule(Request(url=failure.request.url, callback=self.parse,errback=self.on_error,
                                                 cb_kwargs={"context":self.context}),self)
            
            
        else:
            self.logger.error('Unhandled exception: %s' % failure.value) 
              
    def check_url_scheme(self,url):
        parsed_url = urlparse(url)
        return parsed_url.scheme in  ["http", "https"]
       
    def parse(self,response, key,value,page_num,context):
        
        res = response.text
        next_url = f'https://www.sogou.com/sogou?interation=1728053249&interV=&query={value}&page={page_num+1}'
        current_url = f'https://www.sogou.com/sogou?interation=1728053249&interV=&query={value}&page={page_num}'
       
       
        flag = "此验证码用于确认这些请求是您的正常行为而不是自动程序发出的，需要您协助验证" in res
        if flag:
            print("搜狗：出现反爬验证码，sleep(60):",f"{key}:{value}:第{page_num}页")
            time.sleep(60) 
           
            
            yield Request(current_url, callback=self.parse,dont_filter=True ,errback=self.on_error,
                           cb_kwargs={"key":key,'value':value,'page_num': page_num,"context":context})
            
            
            
        p_href = '<h3 class="vr-title">.*?<a id=".*?" target="_blank"  cacheStrategy=.*?href="(.*?)">.*?</a>' 
        hrefs = re.findall(p_href, res, re.S)  # 因为正则里<h3 class="vr-title">后有换行，所以得加re.S 
        
        hrefs =[x for x in hrefs if self.check_url_scheme(x)]
         
        if not hrefs:
            return  
        
        
        if not flag and hrefs:
            p_source = '<p class="news-from text-lightgray">.*?<span>(.*?)</span><span>.*?</span>.*?</p>'
            sources = re.findall(p_source, res, re.S)
        

            p_date = '<p class="news-from text-lightgray">.*?<span>.*?</span><span>(.*?)</span>.*?</p>'
            dates = re.findall(p_date, res, re.S)
            dates = self.convert_time(dates)
            

            p_title = '<h3 class="vr-title">.*?<a id=".*?" target="_blank"  cacheStrategy=.*?href=".*?">(.*?)</a>'
            titles = re.findall(p_title, res, re.S)  # 因为正则里<h3 class="vr-title">后有换行，所以得加re.S

            titles =[re.sub(r'<em><!--red_beg-->(.*?)<!--red_end--></em>', r'\1', s) for s in titles]
            
            page = context.new_page()
            page.route("**/*", self.handle_redirect) 
       
            for i in range(len(titles)):
                titles[i] = re.sub('<.*?>', '', titles[i])
                count  = 0
                while True:
                    try:
                        page.goto('https://www.sogou.com' + hrefs[i])
                        page.wait_for_load_state("networkidle")
                        time.sleep(1)
                        
                        print(page.url)
                        hrefs[i] = page.url
                        break
                        
                    except Exception as e:
                        count = count + 1
                        if count > 10:
                            break
                        
                        print(e)
                        time.sleep(0.1)
                        
            page.close()        
            iter_zip = zip(hrefs,titles,dates,sources)
                
            for data in iter_zip:
                data_ = [*data]
                data_.extend([key,value])
                data_.append(current_url)
                
            
                yield {"data":data_}
                
            with open("进度.txt","a+",encoding="utf8") as f:
                f.write(current_url + '\n')
            
            print(f"搜狗：{key}:{value}：第{page_num}页")       
            
            soup = BeautifulSoup(res, 'html.parser')
            next_page_link = soup.find('a', text='下一页')
           
            
            if next_page_link:
                
                next_url = f'https://www.sogou.com/sogou?interation=1728053249&interV=&query={value}&page={page_num+1}'
                time.sleep(0.5)
                yield Request(next_url, callback=self.parse, dont_filter=True,errback=self.on_error,
                               cb_kwargs={"key":key,'value':value,'page_num': page_num + 1,"context":context})
            page.close()

  
    def convert_time(self,time_list):
        # 当前日期时间
        current_time = datetime.now().strftime('%Y年%m月%d日')
    
        for x in range(len(time_list)):
            if "小时前" in time_list[x]:
                # 时间格式已经是YYYY-MM-DD，无需处理
                time_list[x] = current_time
                
        return  time_list
    
    
    
