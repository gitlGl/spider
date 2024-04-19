


import requests
import time
import csv
#抓取的数据属于排行榜
#https://quote.eastmoney.com/center/gridlist.html#hs_a_board

def collect():
    url = 'https://datacenter-web.eastmoney.com/api/data/v1/get'
    headers = {'User-Agent': ua}
    params = {
        'sortColumns': 'SECURITY_CODE',
        'sortTypes': '1',
        'pageSize': '10000',
        'pageNumber': '1',
        'reportName': 'RPT_VALUEANALYSIS_DET',
        'columns': 'ALL',
        'quoteColumns': '',
        'source': 'WEB',
        'client': 'WEB',
        'filter': f'''(TRADE_DATE='{time.strftime("%Y-%m-%d", time.localtime(time.time() - 60 * 60 * 24))}')'''
    }
    res = requests.get(url=url, headers=headers, params=params).json()
    for li in res['result']['data']:
        secid = '0' + '.' + li['SECUCODE'][:6] if li['SECUCODE'][-2:] == 'SZ' else '1' + '.' + li['SECUCODE'][:6]
        urlLi = 'http://push2.eastmoney.com/api/qt/stock/get'
        paramsLi = {
            'fltt': '2',
            'invt': '2',
            'fields': 'f55,f62,f84,f85,f92,f173,f103,f104,f105,f108,f109,f116,f117,f126,f160,f183,f184,f185,f186,f187,f188,f190,f162,f167,f189',
            'secid': secid
        }
        resLi = requests.get(url=urlLi, headers=headers, params=paramsLi).json()
        dic = {
            '序号': res['result']['data'].index(li) + 1,
            '股票代码': li['SECURITY_CODE'],
            '股票简称': li['SECURITY_NAME_ABBR'],
            '最新价': li['CLOSE_PRICE'],
            '涨跌幅(%)': li['CHANGE_RATE'],
            'PE(TTM)': li['PE_TTM'],
            'PE(静)': li['PE_LAR'],
            '市净率': li['PB_MRQ'],
            'PEG值': li['PEG_CAR'],
            '市销率': li['PS_TTM'],
            '市现率': li['PCF_OCF_TTM'],
            '所属行业': li['BOARD_NAME'],
            '收益': resLi['data']['f55'],
            'ROE': resLi['data']['f173'],
            '同比': resLi['data']['f185'],
            '净资产': resLi['data']['f92'],
            '总股本': resLi['data']['f84'],
            '净利率': resLi['data']['f187'],
            '总营收': resLi['data']['f183'],
            '流通股': resLi['data']['f85'],
            '负债率': resLi['data']['f188'],
            '净利润': resLi['data']['f105'],
            'PE(动)': resLi['data']['f162'],
            '总值': resLi['data']['f116'],
            '毛利率': resLi['data']['f186'],
            '流值': resLi['data']['f117'],
            '每股未分配利润': resLi['data']['f190']
        }
        print(dic)
        csv.writer(open('东方财富数据.csv', 'a', encoding='utf-8-sig', newline='')).writerow(dic.values())


if __name__ == '__main__':
    ua = 'Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/91.0.4472.106Safari/537.36'
    csv.writer(open('东方财富数据.csv', 'w', encoding='utf-8-sig', newline='')).writerow(
        ['序号', '股票代码', '股票简称', '最新价', '涨跌幅(%)', 'PE(TTM)', 'PE(静)', '市净率', 'PEG值', '市销率', '市现率', '所属行业', '收益', 'ROE',
         '同比', '净资产', '总股本', '净利率', '总营收', '流通股', '负债率', '净利润', 'PE(动)', '总值', '毛利率', '流值', '每股未分配利润'])
    collect()
