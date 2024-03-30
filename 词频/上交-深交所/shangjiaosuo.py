
import requests,re,csv
import json ,time,datetime
from codename import code_name_pairs
import os
current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))  

def date_ranges():
    begin = datetime.datetime(1990, 11, 26)
    now = datetime.datetime.today()
    interv = datetime.timedelta(days=900)
    dates = []
    date = begin
    while True:
        if (date < now) & (date + interv < now):
            date = date + interv
            dates.append(date.strftime('%Y-%m-%d'))
        else:
            dates.append(now.strftime('%Y-%m-%d'))
            break
    return [(d1, d2) for d1, d2 in zip(dates, dates[1:])]

cookies = {"Cookie": 'ba17301551dcbaf9_gdp_session_id=fe0089fe-71b7-4375-80c5-2b80d625e1df; gdp_user_id=gioenc-7b87geg9%2C5463%2C53ec%2Ca8g7%2C41aadbc577b5; ba17301551dcbaf9_gdp_session_id_sent=fe0089fe-71b7-4375-80c5-2b80d625e1df; VISITED_MENU=%5B%229075%22%2C%2210766%22%5D; sseMenuSpecial=14887; ba17301551dcbaf9_gdp_sequence_ids={%22globalKey%22:94%2C%22VISIT%22:2%2C%22PAGE%22:22%2C%22VIEW_CLICK%22:68%2C%22CUSTOM%22:4%2C%22VIEW_CHANGE%22:2}'}


def disclosure(code):
        """
        获得该公司的股票代码、报告类型、年份、定期报告披露日期、定期报告pdf下载链接，返回DataFrame。
        :param code:  股票代码
        :return: 返回DataFrame
        """
     
        datas = []
       
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            'Referer': 'http://www.sse.com.cn/disclosure/listedinfo/regular/'}
        
        base = 'http://query.sse.com.cn/security/stock/queryCompanyBulletin.do?isPagination=true&productId={code}&securityType=0101%2C120100%2C020100%2C020200%2C120200&reportType2=DQBG&reportType=&beginDate={beginDate}&endDate={endDate}&pageHelp.pageSize=25&pageHelp.pageCount=50&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5'
       
        dateranges = date_ranges()
        for begin, end in dateranges:
          
            url = base.format(code=code, beginDate=begin, endDate=end)
           
            print('正在获取{}  {}  {}定期报告披露信息'.format(begin,end,code))
            resp = requests.get(url, headers=headers, cookies=cookies)
           
            raw_data = json.loads(resp.text)
           
            results = raw_data['result']
           
            for result in results:
                pdf = 'http://www.sse.com.cn' + result['URL']
                if re.search('\d{6}_\d{4}_[13nz].pdf', pdf):

                    company = code_name_pairs[str(code)]
                    _type = result['BULLETIN_TYPE']
                    year = result['BULLETIN_YEAR']
                    date = result['SSEDATE']
                    data = [company, code, _type, year, date, pdf]
                    datas.append(data)

        
        return datas
        

headers=['company','code', 'type', 'year', 'date', 'pdf']
for code in code_name_pairs.keys():
    
    datas = disclosure(code)
    time.sleep(0.5)
    
    with open('stocks.csv','a+',encoding="utf8",newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)
        f_csv.writerows(datas)
    
    
