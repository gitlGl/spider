import re,csv,time
from datetime import datetime
from bs4 import BeautifulSoup
from scrapy import Spider
from scrapy.http import Request
from twisted.internet.error import (DNSLookupError, TCPTimedOutError, 
                                    ConnectionLost,TimeoutError,ConnectionRefusedError)

from urllib.parse import urlparse
class BaiDu(Spider):
    
    name = "baidu"  
    
    def __init__(self, url_set=None, *args, **kwargs):
        super(BaiDu, self).__init__(*args, **kwargs)
        self.url_set = url_set
        
    def start_requests(self):
        """
        爬虫入口,重写该函数
        
        """
        f = open("关键词.csv",encoding="utf8")
       
        dics = csv.DictReader(f)             
        for dic in dics:
            
            for key,value in dic.items():
                
                if value != '': 
                        page_num = 0
                        time.sleep(0.5)
                        url = 'http://www.baidu.com/s?tn=news&rtt=4&bsst=1&cl=2&wd=' + value  + f"&pn={page_num}"
                        while url   in self.url_set: 
                            print(f"百度：{key}:{value}：第{page_num}页已下载")
                            page_num = page_num + 10  
                            url = 'http://www.baidu.com/s?tn=news&rtt=4&bsst=1&cl=2&wd=' + value  + f"&pn={page_num}"
                        
                        yield Request(url, callback=self.parse, dont_filter=True,errback=self.on_error,
                                        cb_kwargs={"key":key,'value':value,'page_num': page_num})
        f.close()  
        
                
    def check_url_scheme(self,url):
            parsed_url = urlparse(url)
            return parsed_url.scheme in  ["http", "https"]
        
    def parse(self,response, key,value,page_num):
        url = 'http://www.baidu.com/s?tn=news&rtt=4&bsst=1&cl=2&wd=' + value
        next_url = url + f"&pn={page_num + 10}"
        current_url = url + f"&pn={page_num}"
        
        res = response.text 
                
        res = response.text 
        flag = "百度安全验证" in res
        
            
        if flag:
            print(f"百度：出现反爬验证码，sleep(60):{key}:{value}:第{page_num}页")
            
            time.sleep(60)
            
            yield Request(current_url, callback=self.parse, dont_filter=True,errback=self.on_error,
                                      cb_kwargs={"key":key,'value':value,'page_num': page_num})
        
        if not flag:
            num_str = ""
            for x in reversed(response.url):
                if x.isdigit():
                    num_str  = num_str + x
                    
                else:
                    break
                
            
            
            if num_str[::-1] != str(page_num):
                return
          
        if not flag:    
            p_href = '<h3 class="news-title_1YtI1 "><a href="(.*?)"'
            hrefs = re.findall(p_href, res, re.S)
            hrefs = [url.replace("&amp;wfr=spider&amp;for=pc", "") for url in hrefs ]
            hrefs = [x for x in hrefs if self.check_url_scheme(x)]
         
            
            p_title = '<h3 class="news-title_1YtI1 ">.*?>(.*?)</a>'
            titles = re.findall(p_title, res, re.S)
            titles = [self.remove_tags(item) for item in  titles]

            p_date = '<span class="c-color-gray2 c-font-normal c-gap-right-xsmall" .*?>(.*?)</span>'
            dates = re.findall(p_date, res)
            dates = self.convert_time(dates)
            
            p_source = '<span class="c-color-gray" .*?>(.*?)</span>'
            
            sources = re.findall(p_source, res)
            
            for i in range(len(titles)):
                titles[i] = titles[i].strip()  
                titles[i] = re.sub('<.*?>', '', titles[i])  
                
            
            iter_zip = zip(hrefs,titles,dates,sources)
            
            for data in iter_zip:
                data_ = [*data]
                data_.extend([key,value])
                data_.append(current_url)
                yield {"data":data_}
                    
            with open("进度.txt","a+",encoding="utf8") as f:
                f.write(current_url + '\n')
            
            soup = BeautifulSoup(res, 'html.parser')

            next_page_link = soup.find('a', class_='n')  # 查找class为n的a标签
            
            print(f"百度：{key}:{value}：第{page_num}页")
        
            if next_page_link:
                time.sleep(0.5) 
            
                yield Request(next_url, callback=self.parse, dont_filter=True,errback=self.on_error,
                            cb_kwargs={"key":key,'value':value,'page_num': page_num + 10})
        
    def on_error(self, failure):
                
        if failure.check(DNSLookupError, TCPTimedOutError, 
                                    ConnectionLost,TimeoutError,ConnectionRefusedError):
            time.sleep(60)
            self.crawler.engine.schedule(Request(url=failure.request.url, callback=self.parse,errback=self.on_error),self)
            
            
        else:
            self.logger.error('Unhandled exception: %s' % failure.value)   
            
    def convert_time(self,time_list):
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

    def remove_tags(self,text):
        clean_text = re.sub(r'<!--.*?-->', '', text)  # 去除<!-- -->标记
        clean_text = re.sub(r'<em>|</em>', '', clean_text)  # 去除<em> </em>标记
        clean_text = re.sub(r'<!--/s-text-->', '', clean_text)  # 去除<!--/s-text-->标记
        return clean_text



    
    


            