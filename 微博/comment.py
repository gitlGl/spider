import json,requests
import datetime,time
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

def parse_time(s):
    """
    Wed Oct 19 23:44:36 +0800 2022 => 2022-10-19 23:44:36
    """
    targets = datetime.datetime.strptime(s,"%a %b %d %H:%M:%S +0800 %Y")
    return targets


def start_requests():
    """
    爬虫入口
    """
    # 这里tweet_ids可替换成实际待采集的数据
    tweet_ids = ['4999611272662866']
    for tweet_id in tweet_ids:
        mid =tweet_id
        url = f"https://weibo.com/ajax/statuses/buildComments?" \
            f"is_reload=1&id={mid}&is_show_bulletin=2&is_mix=0&count=20"
        yield request_callback(url, callback=parse, source_url = url)

def parse(response,source_url):
    """
    网页解析
    """
    data = json.loads(response.text)
    for comment_info in data['data']:
        item = parse_comment(comment_info)
        yield item
        # 解析二级评论
        if 'more_info' in comment_info:
            url = f"https://weibo.com/ajax/statuses/buildComments?is_reload=1&id={comment_info['id']}" \
                f"&is_show_bulletin=2&is_mix=1&fetch_level=1&max_id=0&count=100"
            yield request_callback(url, callback=parse,source_url = url)
    if data.get('max_id', 0) != 0 and 'fetch_level=1' not in source_url:
        url = source_url + '&max_id=' + str(data['max_id'])
        yield request_callback(url, callback=parse, source_url = url)


def parse_comment(data):
    """
    解析comment
    """
    item = dict()
    item['created_at'] = parse_time(data['created_at'])
    item['_id'] = data['id']
    item['like_counts'] = data['like_counts']
    item['ip_location'] = data.get('source', '')
    item['content'] = data['text_raw']
    item['comment_user'] = parse_user_info(data['user'])
    if 'reply_comment' in data:
        item['reply_comment'] = {
            '_id': data['reply_comment']['id'],
            'text': data['reply_comment']['text'],
            'user': parse_user_info(data['reply_comment']['user']),
        }
        
    return item

def request_callback(url, callback,source_url=None):
    res = requests.get(headers=REQUEST_HEADERS,url=url)
    time.sleep(1)
    return callback(res,source_url)

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Cookie': "WEIBOCN_FROM=1110006030; loginScene=102003; geetest_token=81cc99ad82885c35b9dd3524ff23f91e; SUB=_2A25Iu0wCDeRhGeFN6lEU9SfMzjWIHXVrucHKrDV6PUJbkdAGLWPakW1NQH8835WX39PyYDkfxW20UdZNSR_z7VeB; _T_WM=91902402832; XSRF-TOKEN=0b4a6a; MLOGIN=1; M_WEIBOCN_PARAMS=lfid%3D102803%26luicode%3D20000174%26uicode%3D10000011%26fid%3D231093_-_selffollowed"
}

import types
if  __name__ == "__main__" :             
    for i in start_requests():
        for i2 in i:
            time.sleep(1)
            if isinstance(i2,types.GeneratorType):
                print("test")
                continue
            print(i2)