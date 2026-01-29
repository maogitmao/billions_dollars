#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from data.fetchers.stock_info_crawler import StockInfoCrawler
import json

crawler = StockInfoCrawler()
print('测试获取002731的公告...')
announcements = crawler.get_announcements_detailed('002731', days=7)
print(f'获取到 {len(announcements)} 条公告')
for ann in announcements[:5]:
    print(json.dumps(ann, ensure_ascii=False, indent=2))
