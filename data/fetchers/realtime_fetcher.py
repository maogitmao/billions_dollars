#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
实时行情数据获取模块 - 多数据源支持
"""

import requests
import json
from datetime import datetime
import time


class RealtimeFetcher:
    """实时行情数据获取器 - 支持多个免费数据源"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://quote.eastmoney.com/'
        })
    
    def get_realtime_quote(self, stock_code):
        """
        获取实时行情 - 尝试多个数据源
        """
        # 数据源优先级
        sources = [
            self.fetch_from_sina,      # 新浪财经（最稳定）
            self.fetch_from_163,       # 网易财经
            self.fetch_from_qq,        # 腾讯财经
        ]
        
        for fetch_func in sources:
            try:
                quote = fetch_func(stock_code)
                if quote and not quote.get('error'):
                    return quote
            except Exception as e:
                continue
        
        # 所有数据源都失败
        return self._create_error_quote(stock_code, '所有数据源均不可用')
    
    def fetch_from_sina(self, stock_code):
        """从新浪财经获取实时行情"""
        try:
            # 转换股票代码格式
            if stock_code.startswith('6'):
                symbol = f'sh{stock_code}'
            elif stock_code.startswith('0') or stock_code.startswith('3'):
                symbol = f'sz{stock_code}'
            else:
                symbol = f'sh{stock_code}'
            
            url = f'http://hq.sinajs.cn/list={symbol}'
            response = self.session.get(url, timeout=5)
            response.encoding = 'gbk'
            
            if response.status_code != 200:
                return None
            
            # 解析数据
            content = response.text
            if 'var hq_str_' not in content:
                return None
            
            data_str = content.split('="')[1].split('";')[0]
            data_list = data_str.split(',')
            
            if len(data_list) < 32:
                return None
            
            name = data_list[0]
            open_price = float(data_list[1])
            pre_close = float(data_list[2])
            current_price = float(data_list[3])
            high = float(data_list[4])
            low = float(data_list[5])
            volume = int(data_list[8])
            amount = float(data_list[9])
            
            change = current_price - pre_close
            change_pct = (change / pre_close * 100) if pre_close > 0 else 0
            
            # 计算振幅
            amplitude = ((high - low) / pre_close * 100) if pre_close > 0 else 0
            
            # 获取市值数据（需要额外请求）
            market_cap, circulation = self.get_market_cap(stock_code, current_price)
            
            return {
                'code': stock_code,
                'name': name,
                'price': current_price,
                'change': change,
                'change_pct': change_pct,
                'volume': volume,
                'amount': amount,
                'high': high,
                'low': low,
                'open': open_price,
                'pre_close': pre_close,
                'amplitude': amplitude,
                'market_cap': market_cap,
                'circulation': circulation,
                'time': datetime.now().strftime('%H:%M:%S'),
                'source': '新浪财经',
                'error': None
            }
            
        except Exception as e:
            return None
    
    def get_market_cap(self, stock_code, current_price):
        """获取市值数据"""
        try:
            # 从东方财富获取市值数据
            if stock_code.startswith('6'):
                market_code = f'1.{stock_code}'
            else:
                market_code = f'0.{stock_code}'
            
            url = f'http://push2.eastmoney.com/api/qt/stock/get?secid={market_code}&fields=f116,f117'
            response = self.session.get(url, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    # f116: 总市值（元）
                    # f117: 流通市值（元）
                    total_market_cap = data['data'].get('f116', 0)
                    circulation_market_cap = data['data'].get('f117', 0)
                    
                    if total_market_cap > 0:
                        # 转换为亿元
                        market_cap = total_market_cap / 100000000
                        circulation = circulation_market_cap / 100000000 if circulation_market_cap > 0 else 0
                        return market_cap, circulation
        except:
            pass
        
        return 0, 0
    
    def fetch_from_163(self, stock_code):
        """从网易财经获取实时行情"""
        try:
            # 转换股票代码格式
            if stock_code.startswith('6'):
                symbol = f'0{stock_code}'
            elif stock_code.startswith('0') or stock_code.startswith('3'):
                symbol = f'1{stock_code}'
            else:
                symbol = f'0{stock_code}'
            
            url = f'http://api.money.126.net/data/feed/{symbol}'
            response = self.session.get(url, timeout=5)
            
            if response.status_code != 200:
                return None
            
            # 解析JSON数据
            text = response.text
            if not text or text == 'null':
                return None
            
            # 移除回调函数包装
            json_str = text.split('(')[1].split(')')[0] if '(' in text else text
            data = json.loads(json_str)
            
            stock_data = data.get(symbol, {})
            if not stock_data:
                return None
            
            current_price = float(stock_data.get('price', 0))
            pre_close = float(stock_data.get('yestclose', 0))
            high = float(stock_data.get('high', 0))
            low = float(stock_data.get('low', 0))
            
            # 计算振幅
            amplitude = ((high - low) / pre_close * 100) if pre_close > 0 else 0
            
            # 获取市值数据
            market_cap, circulation = self.get_market_cap(stock_code, current_price)
            
            return {
                'code': stock_code,
                'name': stock_data.get('name', '未知'),
                'price': current_price,
                'change': float(stock_data.get('updown', 0)),
                'change_pct': float(stock_data.get('percent', 0)),
                'volume': int(stock_data.get('volume', 0)),
                'amount': float(stock_data.get('turnover', 0)),
                'high': high,
                'low': low,
                'open': float(stock_data.get('open', 0)),
                'pre_close': pre_close,
                'amplitude': amplitude,
                'market_cap': market_cap,
                'circulation': circulation,
                'time': datetime.now().strftime('%H:%M:%S'),
                'source': '网易财经',
                'error': None
            }
            
        except Exception as e:
            return None
    
    def fetch_from_qq(self, stock_code):
        """从腾讯财经获取实时行情"""
        try:
            # 转换股票代码格式
            if stock_code.startswith('6'):
                symbol = f'sh{stock_code}'
            elif stock_code.startswith('0') or stock_code.startswith('3'):
                symbol = f'sz{stock_code}'
            else:
                symbol = f'sh{stock_code}'
            
            url = f'http://qt.gtimg.cn/q={symbol}'
            response = self.session.get(url, timeout=5)
            response.encoding = 'gbk'
            
            if response.status_code != 200:
                return None
            
            # 解析数据
            content = response.text
            if 'v_' not in content:
                return None
            
            data_str = content.split('="')[1].split('";')[0]
            data_list = data_str.split('~')
            
            if len(data_list) < 48:
                return None
            
            name = data_list[1]
            current_price = float(data_list[3])
            pre_close = float(data_list[4])
            open_price = float(data_list[5])
            volume = int(data_list[6])
            high = float(data_list[33])
            low = float(data_list[34])
            amount = float(data_list[37])
            
            change = current_price - pre_close
            change_pct = (change / pre_close * 100) if pre_close > 0 else 0
            
            # 计算振幅
            amplitude = ((high - low) / pre_close * 100) if pre_close > 0 else 0
            
            # 获取市值数据
            market_cap, circulation = self.get_market_cap(stock_code, current_price)
            
            return {
                'code': stock_code,
                'name': name,
                'price': current_price,
                'change': change,
                'change_pct': change_pct,
                'volume': volume,
                'amount': amount,
                'high': high,
                'low': low,
                'open': open_price,
                'pre_close': pre_close,
                'amplitude': amplitude,
                'market_cap': market_cap,
                'circulation': circulation,
                'time': datetime.now().strftime('%H:%M:%S'),
                'source': '腾讯财经',
                'error': None
            }
            
        except Exception as e:
            return None
    
    def _create_error_quote(self, stock_code, error_msg):
        """创建错误行情数据"""
        return {
            'code': stock_code,
            'name': '获取失败',
            'price': 0.0,
            'change': 0.0,
            'change_pct': 0.0,
            'volume': 0,
            'amount': 0.0,
            'high': 0.0,
            'low': 0.0,
            'open': 0.0,
            'pre_close': 0.0,
            'time': datetime.now().strftime('%H:%M:%S'),
            'source': '无',
            'error': error_msg
        }
    
    def format_quote(self, quote_data):
        """格式化行情数据为显示文本"""
        if quote_data.get('error'):
            return f"❌ {quote_data['code']} - {quote_data['error']}"
        
        # 判断涨跌
        change_pct = quote_data['change_pct']
        if change_pct > 0:
            trend = "📈"
            color_text = "上涨"
        elif change_pct < 0:
            trend = "📉"
            color_text = "下跌"
        else:
            trend = "➡️"
            color_text = "平盘"
        
        source_tag = f" [{quote_data.get('source', '未知')}]"
        
        text = (
            f"{trend} {quote_data['code']} {quote_data['name']}{source_tag}\n"
            f"   价格: ¥{quote_data['price']:.2f}  "
            f"{color_text}: {quote_data['change']:+.2f} ({quote_data['change_pct']:+.2f}%)\n"
            f"   今开: ¥{quote_data['open']:.2f}  "
            f"最高: ¥{quote_data['high']:.2f}  "
            f"最低: ¥{quote_data['low']:.2f}\n"
            f"   成交量: {quote_data['volume']:,}  "
            f"成交额: ¥{quote_data['amount']/100000000:.2f}亿\n"
            f"   更新时间: {quote_data['time']}"
        )
        
        return text


if __name__ == "__main__":
    # 测试代码
    fetcher = RealtimeFetcher()
    
    test_stocks = ['600000', '000001', '600519']
    for code in test_stocks:
        print(f"\n测试股票: {code}")
        quote = fetcher.get_realtime_quote(code)
        print(fetcher.format_quote(quote))
        time.sleep(1)
