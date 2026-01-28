#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
同花顺行情数据获取模块
"""

import akshare as ak
from datetime import datetime
import time
import requests


class THSDataFetcher:
    """同花顺数据获取器"""
    
    def __init__(self):
        self.cache = {}
        self.last_fetch_time = 0
        self.min_fetch_interval = 1  # 最小请求间隔（秒）
        self.session = None
        self._init_session()
    
    def _init_session(self):
        """初始化 requests session"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # 设置超时和重试
        adapter = requests.adapters.HTTPAdapter(
            max_retries=3,
            pool_connections=10,
            pool_maxsize=10
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def get_realtime_quote(self, stock_code, retry=2):
        """
        获取实时行情数据
        
        Args:
            stock_code: 股票代码（如：600000）
            retry: 重试次数
            
        Returns:
            dict: 行情数据字典
        """
        # 限制请求频率
        current_time = time.time()
        if current_time - self.last_fetch_time < self.min_fetch_interval:
            time.sleep(self.min_fetch_interval - (current_time - self.last_fetch_time))
        
        for attempt in range(retry):
            try:
                # 使用 akshare 获取实时行情
                df = ak.stock_zh_a_spot_em()
                self.last_fetch_time = time.time()
                
                # 查找对应股票
                stock_data = df[df['代码'] == stock_code]
                
                if stock_data.empty:
                    error_msg = f'股票代码不存在'
                    return self._create_error_quote(stock_code, error_msg)
                
                row = stock_data.iloc[0]
                
                return {
                    'code': stock_code,
                    'name': row['名称'],
                    'price': float(row['最新价']),
                    'change': float(row['涨跌额']),
                    'change_pct': float(row['涨跌幅']),
                    'volume': int(row['成交量']),
                    'amount': float(row['成交额']),
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                    'open': float(row['今开']),
                    'pre_close': float(row['昨收']),
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'error': None
                }
                
            except (requests.exceptions.ConnectionError, 
                    requests.exceptions.Timeout,
                    ConnectionResetError) as e:
                # 网络错误，重试
                if attempt < retry - 1:
                    wait_time = (attempt + 1) * 3  # 3秒、6秒
                    time.sleep(wait_time)
                    # 重新初始化 session
                    self._init_session()
                    continue
                else:
                    error_msg = f'网络连接超时，请检查网络'
                    return self._create_error_quote(stock_code, error_msg)
            
            except KeyError as e:
                error_msg = f'数据字段错误'
                return self._create_error_quote(stock_code, error_msg)
            except ValueError as e:
                error_msg = f'数据格式错误'
                return self._create_error_quote(stock_code, error_msg)
            except Exception as e:
                # 其他错误，重试
                if attempt < retry - 1:
                    wait_time = (attempt + 1) * 3
                    time.sleep(wait_time)
                    continue
                else:
                    error_msg = f'获取失败: {type(e).__name__}'
                    return self._create_error_quote(stock_code, error_msg)
        
        return self._create_error_quote(stock_code, '未知错误')
    
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
            'error': error_msg
        }
    
    def format_quote(self, quote_data):
        """
        格式化行情数据为显示文本
        
        Args:
            quote_data: 行情数据字典
            
        Returns:
            str: 格式化后的文本
        """
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
        
        text = (
            f"{trend} {quote_data['code']} {quote_data['name']}\n"
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
    fetcher = THSDataFetcher()
    quote = fetcher.get_realtime_quote("600000")
    print(fetcher.format_quote(quote))
