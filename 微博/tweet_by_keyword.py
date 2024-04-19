import datetime,time
import json
import re
import requests
import csv,types,os
current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))  

def parse_time(s):
    """
    Wed Oct 19 23:44:36 +0800 2022 => 2022-10-19 23:44:36
    """
    targets = datetime.datetime.strptime(s,"%a %b %d %H:%M:%S +0800 %Y")
    return targets
    
def parse_user_info(data):
    """
    解析用户信息
    """
    # 基础信息
    user = {
        "_id": str(data['id']),
        "avatar_hd": data['avatar_hd'],
        "nick_name": data['screen_name'],
        "verified": data['verified'],
    }
    # 额外的信息
    keys = ['description', 'followers_count', 'friends_count', 'statuses_count',
            'gender', 'location', 'mbrank', 'mbtype', 'credit_score']
    for key in keys:
        if key in data:
            user[key] = data[key]
    if 'created_at' in data:
        user['created_at'] = parse_time(data.get('created_at'))
    if user['verified']:
        user['verified_type'] = data['verified_type']
        if 'verified_reason' in data:
            user['verified_reason'] = data['verified_reason']
    return user

def parse_tweet_info(data):
    """
    解析推文数据
    """
    tweet = {
        "_id": str(data.get('mid', None)),
        "mblogid": data.get('mblogid', None),
        "created_at": parse_time(data.get('created_at', None)),
        "geo": data.get('geo', None),
        "ip_location": data.get('region_name', None),
        "reposts_count": data.get('reposts_count', None),
        "comments_count": data.get('comments_count', None),
        "attitudes_count": data.get('attitudes_count', None),
        "source": data.get('source', None),
        "content": data.get('text_raw', None),
        "pic_urls": ["https://wx1.sinaimg.cn/orj960/" + pic_id for pic_id in data.get('pic_ids', [])],
        "pic_num": data.get('pic_num', None),
        'isLongText': False,
        'is_retweet': False,
        "user": parse_user_info(data.get('user', None)),
    }
    if '</a>' in tweet['source']:
        tweet['source'] = re.search(r'>(.*?)</a>', tweet['source']).group(1)
    if 'page_info' in data and data['page_info'].get('object_type', '') == 'video':
        media_info = None
        if 'media_info' in data['page_info']:
            media_info = data['page_info']['media_info']
        elif 'cards' in data['page_info'] and 'media_info' in data['page_info']['cards'][0]:
            media_info = data['page_info']['cards'][0]['media_info']
        if media_info:
            tweet['video'] = media_info['stream_url']
    tweet['url'] = f"https://weibo.com/{tweet['user']['_id']}/{tweet['mblogid']}"
    if 'continue_tag' in data and data['isLongText']:
        tweet['isLongText'] = True
    if 'retweeted_status' in data:
        tweet['is_retweet'] = True
        tweet['retweet_id'] = data['retweeted_status']['mid']
        
    if  not tweet['_id']:
        return None
    
    return tweet


    
def parse(response):
    """
    网页解析
    """
    html = response.text
    if '<p>抱歉，未找到相关结果。</p>' in html:
        print("'<p>抱歉，未找到相关结果。</p>'")
        time.sleep(10)
        return
    
    tweet_ids = re.findall(r'weibo\.com/\d+/(.+?)\?refer_flag=1001030103_" ', html)
    for tweet_id in tweet_ids:
        url = f"https://weibo.com/ajax/statuses/show?id={tweet_id}"
        yield request_callback(url,callback=parse_tweet)
    next_page = re.search('<a href="(.*?)" class="next">下一页</a>', html)
    if next_page:
        url = "https://s.weibo.com" + next_page.group(1)
        yield request_callback(url, callback=parse)  

def parse_tweet(response):
    """
    解析推文
    """
    data = json.loads(response.text)
    item = parse_tweet_info(data)
    
    item['关键词'] = KEYWORD[1]
    item['分类'] = KEYWORD[0]
    
    if item['isLongText']:
        print("isLongText")
        url = "https://weibo.com/ajax/statuses/longtext?id=" + item['mblogid']
        res = request_callback(url)
        data = json.loads(res.text)['data']
        item['content'] = data['longTextContent']
        yield item
        
    else:
        yield item

def start_requests():
    """
    爬虫入口
    """
    for dic in dics:
        for key,value in dic.items():
            if not value:
                continue
            global  KEYWORD
            KEYWORD = (key,value)
            
            if not is_split_by_hour:
                _start_time = start_time.strftime("%Y-%m-%d-%H")
                _end_time = end_time.strftime("%Y-%m-%d-%H")
                url = f"https://s.weibo.com/weibo?q={value}&timescope=custom%3A{_start_time}%3A{_end_time}&page=1"
                yield request_callback(url, callback=parse)
            else:
                time_cur = start_time
                while time_cur < end_time:
                    _start_time = time_cur.strftime("%Y-%m-%d-%H")
                    _end_time = (time_cur + datetime.timedelta(hours=1)).strftime("%Y-%m-%d-%H")
                    url = f"https://s.weibo.com/weibo?q={value}&timescope=custom%3A{_start_time}%3A{_end_time}&page=1"
                    yield request_callback(url, callback=parse)
                    time_cur = time_cur + datetime.timedelta(hours=1)
                
def request_callback(url, callback=None):
    time.sleep(3)
    res = requests.get(headers=REQUEST_HEADERS,url=url)
    if  callback is None:
        return res
    
    return callback(res)                

def get_data(gen):
    for i in gen:
        if isinstance(i,types.GeneratorType):
            get_data(i)
        else :
            if i is None:
                continue
           
            save_data(KEYWORD[0] + '.csv',i)

      
def save_data(filename,data):
#     headers = list(data.keys())
#     union_set = set(headers).union(set(head))

# # 将并集转换回列表
#     union_list = list(union_set)
    
    print(data)
    
    if not os.path.exists(filename):
        f = open(filename, 'wt',encoding="utf8",newline = '')
        f_csv = csv.DictWriter(f, head,)
        f_csv.writeheader()
        f_csv.writerows([data])
        f.close()
        return
   
    f = open(filename, 'a+',encoding="utf8",newline = '')
    f_csv = csv.DictWriter(f,head)
    f_csv.writerows([data]) 
    f.close()
      
   
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Cookie': "SINAGLOBAL=2217637827461.287.1709544909396; ULV=1709544909597:1:1:1:2217637827461.287.1709544909396:; PC_TOKEN=a7ee3c7f71; ALF=1715774596; SUB=_2A25LGWfUDeRhGeFN6lEU9SfMzjWIHXVoV-UcrDV8PUJbkNAbLXTEkW1NQH88334bVSIfUomqmBdjnIhZjYZRt_Ni; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhpIvPLn_vp7Xy-Y1zFbc8h5JpX5KMhUgL.FoM0eKefSK.7SK.2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMNe020SK-4eh-4; XSRF-TOKEN=WKTOVwyw0Vu5xrKJB9iCaO5x; WBPSESS=y9jd-BcqKKMv9rbK7sP8E4WeiPJ9683G8IQH6GmwLJL7Gk6bfHtfN-LZ_t9fG3MUyk-GfHiiH_WSiBeNfqt32OT-nnLMZ8YxlNYONsv-KiQq_6xRX3XBCcRLR7VeAbKa_UmclzSTqdyzo-CTkIGMSw=="
}
KEYWORD = ''

# 这里keywords可替换成实际待采集的数据

f = open("关键词.csv",encoding="utf8") 

dics = csv.DictReader(f)


# 这里的时间可替换成实际需要的时间段
start_time = datetime.datetime(year=2022, month=10, day=1, hour=0)
end_time = datetime.datetime(year=2023, month=10, day=1, hour=1)
# 是否按照小时进行切分，数据量更大; 对于非热门关键词**不需要**按照小时切分
is_split_by_hour = True



       
head = ['_id', 'mblogid', 'created_at', 'geo', 'ip_location', 'reposts_count', 'comments_count', 'attitudes_count', 'source', 'content', 'pic_urls', 'pic_num', 'isLongText', 'is_retweet', 'user', 'url', '关键词', '分类',"video",'retweet_id']

if  __name__ == "__main__" :             
   gen = start_requests()
   get_data(gen)
   f.close()
   