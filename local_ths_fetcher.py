#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
本地同花顺数据获取模块
通过同花顺客户端或本地数据文件获取行情
"""

import os
import json
import csv
from datetime import datetime
import subprocess


class LocalTHSFetcher:
    """本地同花顺数据获取器"""
    
    def __init__(self):
        self.ths_path = self.find_ths_installation()
        self.data_cache = {}
    
    def find_ths_installation(self):
        """查找同花顺安装路径"""
        possible_paths = [
            "/opt/ths",
            "/opt/同花顺",
            os.path.expanduser("~/.wine/drive_c/同花顺"),
            os.path.expanduser("~/同花顺"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def get_realtime_quote(self, stock_code):
        """
        获取实时行情数据
        
        策略：
        1. 尝试从同花顺导出的CSV文件读取
        2. 尝试通过同花顺命令行接口
        3. 使用模拟数据（开发测试用）
        """
        
        # 方法1：从CSV文件读取
        quote = self.read_from_csv(stock_code)
        if quote:
            return quote
        
        # 方法2：从同花顺客户端读取（如果有API）
        quote = self.read_from_ths_api(stock_code)
        if quote:
            return quote
        
        # 方法3：返回模拟数据
        return self.get_mock_quote(stock_code)
    
    def read_from_csv(self, stock_code):
        """从CSV文件读取行情数据"""
        csv_files = [
            f"ths_data/quotes_{stock_code}.csv",
            f"ths_data/quotes.csv",
            "ths_data/realtime_quotes.csv"
        ]
        
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                try:
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row.get('代码') == stock_code or row.get('code') == stock_code:
                                return self.parse_csv_row(row, stock_code)
                except Exception as e:
                    print(f"读取CSV失败: {e}")
        
        return None
    
    def parse_csv_row(self, row, stock_code):
        """解析CSV行数据"""
        try:
            return {
                'code': stock_code,
                'name': row.get('名称', row.get('name', '未知')),
                'price': float(row.get('最新价', row.get('price', 0))),
                'change': float(row.get('涨跌额', row.get('change', 0))),
                'change_pct': float(row.get('涨跌幅', row.get('change_pct', 0))),
                'volume': int(float(row.get('成交量', row.get('volume', 0)))),
                'amount': float(row.get('成交额', row.get('amount', 0))),
                'high': float(row.get('最高', row.get('high', 0))),
                'low': float(row.get('最低', row.get('low', 0))),
                'open': float(row.get('今开', row.get('open', 0))),
                'pre_close': float(row.get('昨收', row.get('pre_close', 0))),
                'time': datetime.now().strftime('%H:%M:%S'),
                'error': None
            }
        except Exception as e:
            return None
    
    def read_from_ths_api(self, stock_code):
        """从同花顺API读取（如果可用）"""
        if not self.ths_path:
            return None
        
        # 尝试读取同花顺的实时数据文件
        # 同花顺通常会在用户目录下保存数据
        possible_data_paths = [
            os.path.expanduser("~/.wine/drive_c/users/*/Application Data/hexin/T0002/blocknew"),
            os.path.expanduser("~/.wine/drive_c/同花顺/T0002/blocknew"),
            os.path.expanduser("~/同花顺/data"),
        ]
        
        # TODO: 实现同花顺数据文件解析
        
        return None
    
    def import_from_clipboard(self):
        """从剪贴板导入数据（用户从同花顺复制）"""
        try:
            import pyperclip
            clipboard_data = pyperclip.paste()
            
            # 解析剪贴板数据
            lines = clipboard_data.strip().split('\n')
            if len(lines) > 0:
                # 假设格式：代码\t名称\t最新价\t涨跌幅...
                return self.parse_clipboard_data(lines)
        except:
            pass
        
        return None
    
    def parse_clipboard_data(self, lines):
        """解析剪贴板数据"""
        # TODO: 根据实际的同花顺复制格式来解析
        return None
    
    def create_sample_csv(self):
        """创建示例CSV文件，用户可以从同花顺导出后放到这里"""
        sample_file = "ths_data/quotes_template.csv"
        os.makedirs("ths_data", exist_ok=True)
        
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write("代码,名称,最新价,涨跌额,涨跌幅,成交量,成交额,最高,最低,今开,昨收\n")
            f.write("600000,浦发银行,8.50,0.10,1.19,12345678,105000000,8.55,8.45,8.48,8.40\n")
        
        return sample_file
    
    def get_mock_quote(self, stock_code):
        """获取模拟行情数据（用于测试）"""
        import random
        
        # 生成模拟数据
        base_price = random.uniform(10, 100)
        change_pct = random.uniform(-5, 5)
        change = base_price * change_pct / 100
        
        return {
            'code': stock_code,
            'name': f'股票{stock_code}',
            'price': round(base_price, 2),
            'change': round(change, 2),
            'change_pct': round(change_pct, 2),
            'volume': random.randint(1000000, 100000000),
            'amount': round(random.uniform(10000000, 1000000000), 2),
            'high': round(base_price * 1.05, 2),
            'low': round(base_price * 0.95, 2),
            'open': round(base_price * 0.98, 2),
            'pre_close': round(base_price - change, 2),
            'time': datetime.now().strftime('%H:%M:%S'),
            'error': None,
            'is_mock': True  # 标记为模拟数据
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
        
        # 是否为模拟数据
        mock_tag = " [模拟数据]" if quote_data.get('is_mock') else ""
        
        text = (
            f"{trend} {quote_data['code']} {quote_data['name']}{mock_tag}\n"
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
    fetcher = LocalTHSFetcher()
    quote = fetcher.get_realtime_quote("600000")
    print(fetcher.format_quote(quote))
