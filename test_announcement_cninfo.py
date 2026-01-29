#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime, timedelta

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'http://www.cninfo.com.cn/'
})

stock_code = '002731'
start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
end_date = datetime.now().strftime('%Y-%m-%d')

print("测试巨潮资讯网公告接口...")
print(f"股票代码: {stock_code}")
print(f"日期范围: {start_date} 到 {end_date}")
print()

# 巨潮资讯网公告接口
print("=" * 60)
print("巨潮资讯网公告列表")
print("=" * 60)
url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
data = {
    'stock': stock_code,
    'searchkey': '',
    'plate': 'sz',  # 深圳
    'category': '',
    'trade': '',
    'column': 'szse',  # 深交所
    'columnTitle': '历史公告查询',
    'pageNum': 1,
    'pageSize': 30,
    'tabName': 'fulltext',
    'sortName': '',
    'sortType': '',
    'limit': '',
    'showTitle': '',
    'seDate': f'{start_date}~{end_date}'
}

try:
    response = session.post(url, data=data, timeout=10)
    print(f"状态码: {response.status_code}")
    result = response.json()
    
    if result.get('announcements'):
        announcements = result['announcements']
        print(f"获取到 {len(announcements)} 条公告")
        print()
        for i, ann in enumerate(announcements[:10], 1):
            print(f"{i}. {ann.get('announcementTitle')}")
            print(f"   日期: {ann.get('announcementTime')}")
            print(f"   类型: {ann.get('announcementTypeName')}")
            print()
    else:
        print("未获取到公告")
        print(f"返回数据: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
