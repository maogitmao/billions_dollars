#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from datetime import datetime, timedelta

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'http://www.eastmoney.com/'
})

stock_code = '002731'
start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

print(f"测试公告接口...")
print(f"股票代码: {stock_code}")
print(f"起始日期: {start_date}")
print()

# 测试接口1：新版数据中心
print("=" * 60)
print("测试接口1: 新版数据中心")
print("=" * 60)
url1 = 'http://datacenter-web.eastmoney.com/api/data/v1/get'
params1 = {
    'sortColumns': 'NOTICE_DATE,SECURITY_CODE',
    'sortTypes': '-1,-1',
    'pageSize': 20,
    'pageNumber': 1,
    'reportName': 'RPT_PUBLIC_OP_NEWNOTICE',
    'columns': 'ALL',
    'filter': f'(SECURITY_CODE="{stock_code}")(NOTICE_DATE>=\'{start_date}\')'
}

try:
    response1 = session.get(url1, params=params1, timeout=10)
    print(f"状态码: {response1.status_code}")
    data1 = response1.json()
    print(f"返回数据: {data1}")
    if data1.get('result') and data1['result'].get('data'):
        print(f"获取到 {len(data1['result']['data'])} 条公告")
        for item in data1['result']['data'][:3]:
            print(f"  - {item.get('NOTICE_DATE')}: {item.get('NOTICE_TITLE')}")
    else:
        print("未获取到公告数据")
except Exception as e:
    print(f"错误: {e}")

print()

# 测试接口2：旧版接口
print("=" * 60)
print("测试接口2: 旧版接口")
print("=" * 60)
url2 = 'http://np-anotice-stock.eastmoney.com/api/security/ann'
params2 = {
    'sr': -1,
    'page_size': 20,
    'page_index': 1,
    'ann_type': 'A',
    'client_source': 'web',
    'stock_list': f'sz{stock_code}',
    'begin_time': start_date,
    'end_time': datetime.now().strftime('%Y-%m-%d')
}

try:
    response2 = session.get(url2, params=params2, timeout=10)
    print(f"状态码: {response2.status_code}")
    data2 = response2.json()
    if data2.get('data') and data2['data'].get('list'):
        print(f"获取到 {len(data2['data']['list'])} 条公告")
        for item in data2['data']['list'][:3]:
            print(f"  - {item.get('notice_date')}: {item.get('title')}")
    else:
        print("未获取到公告数据")
        print(f"返回数据: {data2}")
except Exception as e:
    print(f"错误: {e}")

print()

# 测试接口3：F10公告接口
print("=" * 60)
print("测试接口3: F10公告接口")
print("=" * 60)
url3 = 'http://datacenter-web.eastmoney.com/api/data/v1/get'
params3 = {
    'sortColumns': 'NOTICE_DATE',
    'sortTypes': '-1',
    'pageSize': 20,
    'pageNumber': 1,
    'reportName': 'RPT_F10_NOTICE_LATEST',
    'columns': 'ALL',
    'filter': f'(SECUCODE="002731.SZ")'
}

try:
    response3 = session.get(url3, params=params3, timeout=10)
    print(f"状态码: {response3.status_code}")
    data3 = response3.json()
    print(f"返回数据keys: {data3.keys() if isinstance(data3, dict) else 'not dict'}")
    if data3.get('result') and data3['result'].get('data'):
        print(f"获取到 {len(data3['result']['data'])} 条公告")
        for item in data3['result']['data'][:5]:
            print(f"  - {item.get('NOTICE_DATE')}: {item.get('NOTICETITLE')}")
    else:
        print("未获取到公告数据")
        print(f"返回: {data3}")
except Exception as e:
    print(f"错误: {e}")
