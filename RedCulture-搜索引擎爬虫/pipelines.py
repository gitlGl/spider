from pony.orm import *

db = Database()  # 创建一个Pony ORM数据库实例
class ArticleData(db.Entity):
    id = PrimaryKey(int, auto=True)
    url = Required(str,max_len=3000)
    source_url = Required(str,max_len=3000)
    
    title = Optional(str,max_len=3000)
    date = Optional(str)
    source = Optional(str)
    
    type_ = Optional(str)  # 添加type字段
    keyword = Optional(str)  # 添加keyword字段
    
    num = Required(int)#跳动次数
    crawled = Required(bool, default=False)
    isRed = Optional(bool)
    
    article = Optional(LongStr)
    
    
    
db.bind(provider='mysql', host='localhost', user='root', passwd='123456', db='RedCulture')
db.generate_mapping(create_tables=True)

# 设置自动提交事务
db.provider.auto_commit = True
    
class PonyPipeline:

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        item = item["data"]
        if spider.name == "sougou" or spider.name == "baidu":

            with db_session:
                existing_url =ArticleData.get(url = item[0])
                if not existing_url:
                    ArticleData(url=item[0], title=item[1], date=item[2], source=item[3],
                    type_ = item[4],keyword = item[5],source_url = item[6],num = 0 )
   

        return item


