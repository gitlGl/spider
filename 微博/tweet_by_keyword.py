import datetime,time
import json
import re
import requests

def base62_decode(string):
    """
    base
    """
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    string = str(string)
    num = 0
    idx = 0
    for char in string:
        power = (len(string) - (idx + 1))
        num += alphabet.index(char) * (len(alphabet) ** power)
        idx += 1

    return num


def reverse_cut_to_length(content, code_func, cut_num=4, fill_num=7):
    """
    url to mid
    """
    content = str(content)
    cut_list = [content[i - cut_num if i >= cut_num else 0:i] for i in range(len(content), 0, (-1 * cut_num))]
    cut_list.reverse()
    result = []
    for i, item in enumerate(cut_list):
        s = str(code_func(item))
        if i > 0 and len(s) < fill_num:
            s = (fill_num - len(s)) * '0' + s
        result.append(s)
    return ''.join(result)


def url_to_mid(url: str):
    """>>> url_to_mid('z0JH2lOMb')
    3501756485200075
    """
    result = reverse_cut_to_length(url, base62_decode)
    return int(result)


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
        "_id": str(data['mid']),
        "mblogid": data['mblogid'],
        "created_at": parse_time(data['created_at']),
        "geo": data.get('geo', None),
        "ip_location": data.get('region_name', None),
        "reposts_count": data['reposts_count'],
        "comments_count": data['comments_count'],
        "attitudes_count": data['attitudes_count'],
        "source": data['source'],
        "content": data['text_raw'].replace('\u200b', ''),
        "pic_urls": ["https://wx1.sinaimg.cn/orj960/" + pic_id for pic_id in data.get('pic_ids', [])],
        "pic_num": data['pic_num'],
        'isLongText': False,
        'is_retweet': False,
        "user": parse_user_info(data['user']),
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
    return tweet


def parse_long_tweet(response):
    """
    解析长推文
    """
    data = json.loads(response.text)['data']
    item = response.meta['item']
    item['content'] = data['longTextContent']
    yield item


def request_callback(url, callback):
    res = requests.get(headers=REQUEST_HEADERS,url=url)
    time.sleep(1)
    return callback(res)
    
def parse_tweet(response):
    """
    解析推文
    """
    data = json.loads(response.text)
    item = parse_tweet_info(data)
    item['keyword'] = response.meta['keyword']
    if item['isLongText']:
        url = "https://weibo.com/ajax/statuses/longtext?id=" + item['mblogid']
        yield request_callback(url, callback=parse_long_tweet)
    else:
        yield item
        
def parse(response):
    """
    网页解析
    """
    html = response.text
    if '<p>抱歉，未找到相关结果。</p>' in html:
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
    item['keyword'] = KEYWORD
    print(item)
    if item['isLongText']:
        url = "https://weibo.com/ajax/statuses/longtext?id=" + item['mblogid']
        yield request_callback(url, callback=parse_long_tweet)
    else:
        yield item


name = "tweet_spider_by_keyword"
base_url = "https://s.weibo.com/"

def start_requests():
    """
    爬虫入口
    """
    for keyword in keywords:
        global  KEYWORD
        KEYWORD = keyword
        if not is_split_by_hour:
            _start_time = start_time.strftime("%Y-%m-%d-%H")
            _end_time = end_time.strftime("%Y-%m-%d-%H")
            url = f"https://s.weibo.com/weibo?q={keyword}&timescope=custom%3A{_start_time}%3A{_end_time}&page=1"
            yield request_callback(url, callback=parse)
        else:
            time_cur = start_time
            while time_cur < end_time:
                _start_time = time_cur.strftime("%Y-%m-%d-%H")
                _end_time = (time_cur + datetime.timedelta(hours=1)).strftime("%Y-%m-%d-%H")
                url = f"https://s.weibo.com/weibo?q={keyword}&timescope=custom%3A{_start_time}%3A{_end_time}&page=1"
                yield request_callback(url, callback=parse)
                time_cur = time_cur + datetime.timedelta(hours=1)
                

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Cookie': "WEIBOCN_FROM=1110006030; loginScene=102003; geetest_token=81cc99ad82885c35b9dd3524ff23f91e; SUB=_2A25Iu0wCDeRhGeFN6lEU9SfMzjWIHXVrucHKrDV6PUJbkdAGLWPakW1NQH8835WX39PyYDkfxW20UdZNSR_z7VeB; _T_WM=91902402832; XSRF-TOKEN=0b4a6a; MLOGIN=1; M_WEIBOCN_PARAMS=lfid%3D102803%26luicode%3D20000174%26uicode%3D10000011%26fid%3D231093_-_selffollowed"
}
KEYWORD = ''


# 这里keywords可替换成实际待采集的数据
keywords = ['丽江',"测试"]
# 这里的时间可替换成实际需要的时间段
start_time = datetime.datetime(year=2022, month=10, day=1, hour=0)
end_time = datetime.datetime(year=2022, month=10, day=1, hour=1)
# 是否按照小时进行切分，数据量更大; 对于非热门关键词**不需要**按照小时切分
is_split_by_hour = True

if  __name__ == "__main__" :             
    for i in start_requests():
        for i2 in i:
            for i3 in i2 :
                ...