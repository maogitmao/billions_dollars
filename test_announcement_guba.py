#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'http://guba.eastmoney.com/'
})

stock_code = '002731'

print("测试东方财富股吧公告接口...")
print()

# 接口4：股吧公告列表
print("=" * 60)
print("测试接口4: 股吧公告列表")
print("=" * 60)
url4 = f'http://guba.eastmoney.com/interface/GetData.aspx'
params4 = {
    'type': '1',  # 1=公告
    'code': stock_code,
    'ps': '20',
    'p': '1',
    'sort': '1'
}

try:
    response4 = session.get(url4, params=params4, timeout=10)
    print(f"状态码: {response4.status_code}")
    print(f"返回内容前500字符: {response4.text[:500]}")
except Exception as e:
    print(f"错误: {e}")

print()

# 接口5：公司公告页面
print("=" * 60)
print("测试接口5: 公司公告页面API")
print("=" * 60)
url5 = 'http://emweb.securities.eastmoney.com/PC_HSF10/Notice/PageAjax'
params5 = {
    'code': f'SZ{stock_code}',
    'type': '1',  # 1=全部公告
    'page': '1',
    'pageSize': '20'
}

try:
    response5 = session.get(url5, params=params5, timeout=10)
    print(f"状态码: {response5.status_code}")
    data5 = response5.json()
    print(f"返回数据: {json.dumps(data5, ensure_ascii=False, indent=2)[:1000]}")
except Exception as e:
    print(f"错误: {e}")

print()

# 接口6：使用同花顺接口
print("=" * 60)
print("测试接口6: 同花顺公告接口")
print("=" * 60)
url6 = f'http://basic.10jqka.com.cn/{stock_code}/notice.html'

try:
    response6 = session.get(url6, timeout=10)
    print(f"状态码: {response6.status_code}")
    print(f"返回内容前500字符: {response6.text[:500]}")
except Exception as e:
    print(f"错误: {e}")
