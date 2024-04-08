import re,csv,time
from bs4 import BeautifulSoup
from scrapy import Spider
from scrapy.http import Request
from twisted.internet.error import (DNSLookupError, TCPTimedOutError, 
                            ConnectionLost,TimeoutError,ConnectionRefusedError)

from pony.orm import db_session, select
from scrapy.linkextractors import LinkExtractor

from pony.orm import  db_session,commit
from pipelines import ArticleData
from functools import partial
from urllib.parse import urlparse

class Article(Spider):
    
    name = "Article"  
    D_MAX = 100
    
    def __init__(self,  *args, **kwargs):
        super(Article, self).__init__(*args, **kwargs)
        self.key_set = set()

        with open('关键词.csv',encoding="utf8") as f:
            f_csv = csv.reader(f)
            headers = next(f_csv)
            for row in f_csv:
                self.key_set.update(row)
                
            self.key_set.remove('')
            
        
    def start_requests(self):
        with db_session:
            database_urls = select((a.url ,a.keyword,a.type_,a.num)for a in ArticleData if not a.crawled  ).limit(self.D_MAX)
            while len(database_urls) < 5:
                print("Article sleep 60")
                time.sleep(10)
                database_urls = select((a.url ,a.keyword,a.type_,a.num)for a in ArticleData if not a.crawled ).limit(self.D_MAX)
                
            
            for database_url,keyword,type_ ,num,in database_urls:
                if not self.is_valid_url(database_url):
                    self.set_crawled(database_url)
                    continue
                
                yield Request(database_url, callback=self.parse, dont_filter=True,errback = partial(self.on_error, url=database_url),
                           cb_kwargs={"keyword":keyword,"type_":type_,"num":num,"current_url":database_url })
                
    def is_valid_url(self,url):
        result = urlparse(url)
        return all([result.scheme, result.netloc])  
          
    def set_crawled(self,url):
        with db_session:
            article_data = ArticleData.get(url=url)
            if article_data:
                article_data.crawled = True
                
            commit()
            
       
    def get_data(self,html):
                
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html, 'html.parser')

        # 获取标题
        title = soup.title
        
        if not title:
            title = " "
            
        else:
            if  title.string is None:
                title = " "
            else:
                title = title.string
            
        date = self.get_date(html)
        if not date:
            date = ""
           
        text_list = []
        for p_tag in soup.find_all('p'):
            text = ''.join(p_tag.strings) 
            text_list.append(text)
       
        article = '\n'.join(text_list)  # 将列表转换成为字符
        
        if not article:
            article = ""
        
        return title ,date,article
          
    def parse(self,response,keyword,type_,num,current_url):
       
        lenth = len(self.crawler.engine.slot.scheduler)
        
        if lenth < 2:
            print("增加")
            with db_session:
                database_urls = select((a.url ,a.keyword,a.type_,a.num) for a in ArticleData if not a.crawled ).limit(self.D_MAX)
                
                while len(database_urls) < 2:
                    print("Article sleep 1")
                    time.sleep(1)
                    database_urls = select((a.url ,a.keyword,a.type_,a.num) for a in ArticleData if not a.crawled ).limit(self.D_MAX )
            
            for database_url,keyword,type_,num_ in database_urls:
                if not self.is_valid_url(database_url):
                    self.set_crawled(database_url)
                    continue

                self.crawler.engine.schedule(Request(url=database_url,  errback = partial(self.on_error, url=database_url), dont_filter=True,
                                    callback=self.parse,cb_kwargs={"keyword":keyword,"type_":type_,"num":num_,"current_url":database_url}),self)
                
        print(len(self.crawler.engine.slot.scheduler))
               
        try:    
            html  = response.text
           
        except Exception:
            self.set_crawled(current_url)
            
            return

        title ,date,article = self.get_data(html)
        
        count = 0
        for key in self.key_set:
            n = article.count(key)
            if n > 0:
                article = article.replace(key,f"[{key}]")
                
            count = count + n 
            
        if count > 1 :       
            extract_urls = self.get_urls(response) 
            for extract_url in extract_urls:
                
                if not self.is_valid_url(extract_url):
                    continue
                
                with db_session:
                    existing_url = ArticleData.get(url=extract_url)
                    
                    if not existing_url:
                        ArticleData(url=extract_url, source_url = current_url,num = num + 1,
                                    keyword = keyword,type_ = type_)
                    commit()
                    
            if num == 0:
                try:
                    with db_session:
                        
                        article_data = ArticleData.get(url=current_url)
                        if article_data:
                            article_data.isRed = True
                            article_data.article = article
                        commit()
                except Exception as e:
                    print(e)
            
            else:   
                try:
                    with db_session:
                        article_data = ArticleData.get(url=current_url)
                        if article_data:
                            article_data.isRed = True
                            article_data.article = article
                            article_data.title = title
                            article_data.date = date
                        commit() 
                        
                except Exception as e:
                    print(e)
        
        else:
            try:
                with db_session:
                        article_data = ArticleData.get(url=current_url)
                        if article_data:
                            article_data.isRed = False
                            article_data.article = article
                            article_data.title = title
                            article_data.date = date
                        commit() 
                        
            except Exception as e:
                print(e)
            
        self.set_crawled(current_url)  
            
    def get_urls(self,response):
        link_extractor = LinkExtractor()
        links = link_extractor.extract_links(response)
        urls =  [link.url for link in links]
        return [url for url in urls if urlparse(url).path and urlparse(url).path != "/" ]
          
        
    def on_error(self, failure, url):
        self.set_crawled(url) 
             
        print("error",url)
        if failure.check(DNSLookupError, TCPTimedOutError, 
                                    ConnectionLost,TimeoutError,ConnectionRefusedError):
            
            with db_session:
                article_data = ArticleData.get(url=failure.request.url)
                if article_data:
                    article_data.crawled = True
            
        else:
            self.logger.error('Unhandled exception: %s' % failure.value) 
            

    def get_date(self,html):
        # 定义日期的正则表达式模式
        date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',  # 匹配格式：2022-05-23
            r'\b\d{4}年\d{1,2}月\d{1,2}日\b'  # 匹配格式：2023年5月3日
        ]

        # 在HTML文本中查找所有匹配的日期
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, html)
            dates.extend(matches)

        # 获取第一个日期
        first_date = None
        if dates:
            first_date = dates[0]
            return first_date
        
        return False

       

        
        
         