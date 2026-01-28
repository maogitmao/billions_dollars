#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
K线数据获取模块
"""

import requests
import pandas as pd
from datetime import datetime, timedelta


class KLineFetcher:
    """K线数据获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_kline_data(self, stock_code, period='daily', count=120):
        """
        获取K线数据
        
        Args:
            stock_code: 股票代码
            period: 周期 daily/weekly/monthly
            count: 获取数量
            
        Returns:
            DataFrame: K线数据
        """
        # 尝试多个数据源
        sources = [
            self.fetch_from_akshare,
            self.fetch_from_eastmoney,
            self.fetch_from_sina,
            self.fetch_from_163
        ]
        
        for fetch_func in sources:
            try:
                df = fetch_func(stock_code, count)
                if df is not None and not df.empty and len(df) > 10:
                    print(f"{fetch_func.__name__} 成功获取 {len(df)} 条数据")
                    return df
            except Exception as e:
                print(f"{fetch_func.__name__} 失败: {e}")
                continue
        
        return None
    
    def fetch_from_akshare(self, stock_code, count):
        """从akshare获取K线数据"""
        try:
            import akshare as ak
            
            # 获取历史数据
            df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="")
            
            if df is None or df.empty:
                return None
            
            # 重命名列
            df = df.rename(columns={
                '日期': 'day',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume'
            })
            
            # 选择需要的列
            df = df[['day', 'open', 'high', 'low', 'close', 'volume']]
            df['day'] = pd.to_datetime(df['day'])
            
            # 取最近count条数据
            df = df.tail(count).reset_index(drop=True)
            
            return df
            
        except Exception as e:
            print(f"akshare获取失败: {e}")
            return None
    
    def fetch_from_sina(self, stock_code, count):
        """从新浪财经获取K线数据"""
        try:
            if stock_code.startswith('6'):
                symbol = f'sh{stock_code}'
            else:
                symbol = f'sz{stock_code}'
            
            # 新浪K线接口
            url = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={symbol}&scale=240&ma=5,10,20,30&datalen={count}'
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            # 解析JSON数据
            import json
            data = json.loads(response.text)
            
            if not data:
                return None
            
            # 转换为DataFrame
            df = pd.DataFrame(data)
            df['day'] = pd.to_datetime(df['day'])
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            return df
            
        except Exception as e:
            print(f"新浪财经获取失败: {e}")
            return None
    
    def fetch_from_163(self, stock_code, count):
        """从网易财经获取K线数据"""
        try:
            if stock_code.startswith('6'):
                symbol = f'0{stock_code}'
            else:
                symbol = f'1{stock_code}'
            
            # 计算日期范围
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=count*2)).strftime('%Y%m%d')
            
            url = f'http://quotes.money.163.com/service/chddata.html?code={symbol}&start={start_date}&end={end_date}&fields=TCLOSE;HIGH;LOW;TOPEN;VOTURNOVER'
            
            response = self.session.get(url, timeout=10)
            response.encoding = 'gbk'
            
            if response.status_code != 200:
                return None
            
            # 解析CSV数据
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            
            if df.empty:
                return None
            
            # 重命名列
            df = df.rename(columns={
                '日期': 'day',
                '开盘价': 'open',
                '最高价': 'high',
                '最低价': 'low',
                '收盘价': 'close',
                '成交量': 'volume'
            })
            
            # 选择需要的列并排序
            df = df[['day', 'open', 'high', 'low', 'close', 'volume']]
            df['day'] = pd.to_datetime(df['day'])
            df = df.sort_values('day').tail(count).reset_index(drop=True)
            
            return df
            
        except Exception as e:
            print(f"网易财经获取失败: {e}")
            return None
    
    def fetch_from_eastmoney(self, stock_code, count):
        """从东方财富获取K线数据"""
        try:
            if stock_code.startswith('6'):
                secid = f'1.{stock_code}'
            else:
                secid = f'0.{stock_code}'
            
            url = f'http://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58&klt=101&fqt=0&end=20500101&lmt={count}'
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if not data.get('data') or not data['data'].get('klines'):
                return None
            
            klines = data['data']['klines']
            
            # 解析K线数据
            rows = []
            for kline in klines:
                parts = kline.split(',')
                rows.append({
                    'day': parts[0],
                    'open': float(parts[1]),
                    'close': float(parts[2]),
                    'high': float(parts[3]),
                    'low': float(parts[4]),
                    'volume': float(parts[5])
                })
            
            df = pd.DataFrame(rows)
            df['day'] = pd.to_datetime(df['day'])
            
            return df
            
        except Exception as e:
            print(f"东方财富获取失败: {e}")
            return None


if __name__ == "__main__":
    # 测试代码
    fetcher = KLineFetcher()
    df = fetcher.get_kline_data("600000")
    if df is not None:
        print(df.head())
        print(f"获取到 {len(df)} 条K线数据")
