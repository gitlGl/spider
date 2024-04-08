
import os,time
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.sougou import SouGou
from spiders.baidu import BaiDu
from spiders.article import Article
import multiprocessing

def readTxt(file_name):# 读取已下载的公司代码
    if not os.path.exists(file_name):
        with open(file_name, "w",encoding="utf8") as f:
            f.write('')
            
    with open(file_name, "r",encoding="utf8") as f:
        data = f.read().splitlines()
        return set(data)



def work_sougou(spider):
    
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(spider,url_set =readTxt("进度.txt"))
    process.start()
  
def work_artile(spider):
    time.sleep(50)
    
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(spider)
    process.start()

if __name__ == '__main__':
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'settings'
    sougou_p = multiprocessing.Process(target=work_sougou, args=(SouGou,))
    
    sougou_p.start()
    
    artilr_p = multiprocessing.Process(target=work_artile, args=(Article,))
    artilr_p.start()
    
    settings = get_project_settings()

    process = CrawlerProcess(settings)
    spiders = [BaiDu]
    
    for spider_class in spiders:
        process.crawl(spider_class,  url_set =readTxt("进度.txt"))
      
    
    process.start()
    process.join()
    sougou_p.join()
    artilr_p.join()


