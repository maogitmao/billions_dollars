#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分时数据获取器

功能：获取股票当日分时数据
数据源：东方财富接口（主）+ 模拟数据（备用）
刷新频率：3秒（交易时段）

使用方法：
    fetcher = TimeshareFetcher(verbose=False)
    df = fetcher.get_timeshare_data('600519')
    
返回数据：
    DataFrame包含：time, price, volume, avg_price, pre_close
"""

import requests
import pandas as pd


class TimeshareFetcher:
    """分时数据获取器"""
    
    def __init__(self, verbose=False):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://finance.sina.com.cn'
        })
        self.verbose = verbose  # 是否输出详细日志
    
    def get_timeshare_data(self, stock_code):
        """
        获取分时数据
        
        Args:
            stock_code: 股票代码（如：600000、000001）
            
        Returns:
            DataFrame: 包含时间、价格、成交量等信息
        """
        try:
            # 判断市场
            if stock_code.startswith('6') or stock_code == '999999':
                market = 'sh'
            else:
                market = 'sz'
            
            # 首先获取基本行情数据（获取昨收价）
            basic_url = f'https://hq.sinajs.cn/list={market}{stock_code}'
            
            try:
                response = self.session.get(basic_url, timeout=5)
                response.encoding = 'gbk'
                
                if response.status_code != 200:
                    if self.verbose:
                        print(f"获取基本行情失败: HTTP {response.status_code}")
                    return self._generate_mock_data(stock_code)
                
                # 解析数据
                content = response.text
                if 'hq_str_' not in content:
                    if self.verbose:
                        print(f"基本行情数据格式错误")
                    return self._generate_mock_data(stock_code)
                
                data_str = content.split('"')[1]
                fields = data_str.split(',')
                
                if len(fields) < 32:
                    if self.verbose:
                        print(f"基本行情字段不足")
                    return self._generate_mock_data(stock_code)
                
                # 获取昨收价和当前价
                pre_close = float(fields[2])
                current_price = float(fields[3])
                
                if self.verbose:
                    print(f"获取到基本行情: 昨收={pre_close}, 现价={current_price}")
                
            except Exception as e:
                if self.verbose:
                    print(f"获取基本行情异常: {e}")
                return self._generate_mock_data(stock_code)
            
            # 尝试使用东方财富接口获取分时数据
            try:
                # 东方财富分时接口
                secid = f"1.{stock_code}" if market == 'sh' else f"0.{stock_code}"
                eastmoney_url = f'http://push2.eastmoney.com/api/qt/stock/trends2/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58&secid={secid}&iscr=0'
                
                em_response = self.session.get(eastmoney_url, timeout=5)
                em_data = em_response.json()
                
                if em_data.get('data') and em_data['data'].get('trends'):
                    trends = em_data['data']['trends']
                    pre_close_em = float(em_data['data']['preClose'])
                    
                    times = []
                    prices = []
                    volumes = []
                    
                    for trend in trends:
                        # 格式: "2024-01-29 09:30,3000.00,100,300000,0.5"
                        parts = trend.split(',')
                        if len(parts) >= 2:
                            time_str = parts[0].split(' ')[1]  # 提取时间部分
                            price = float(parts[1])
                            # 成交量可能是浮点数，需要转换
                            volume = int(float(parts[2])) if len(parts) > 2 else 0
                            
                            times.append(time_str)
                            prices.append(price)
                            volumes.append(volume)
                    
                    if len(times) > 0:
                        # 计算均价
                        avg_prices = []
                        cumsum_volume = 0
                        cumsum_amount = 0
                        
                        for i in range(len(prices)):
                            cumsum_volume += volumes[i]
                            cumsum_amount += prices[i] * volumes[i]
                            if cumsum_volume > 0:
                                avg_prices.append(cumsum_amount / cumsum_volume)
                            else:
                                avg_prices.append(prices[i])
                        
                        df = pd.DataFrame({
                            'time': times,
                            'price': prices,
                            'volume': volumes,
                            'avg_price': avg_prices
                        })
                        
                        df['pre_close'] = pre_close_em
                        
                        if self.verbose:
                            print(f"✅ 东方财富接口获取成功: {len(df)} 个数据点")
                        return df
                        
            except Exception as e:
                if self.verbose:
                    print(f"东方财富接口失败: {e}")
            
            # 如果所有接口都失败，生成模拟数据
            if self.verbose:
                print("所有接口失败，生成模拟数据")
            return self._generate_mock_timeshare_data(pre_close, current_price)
            
        except Exception as e:
            if self.verbose:
                print(f"获取分时数据失败: {e}")
                import traceback
                traceback.print_exc()
            return self._generate_mock_data(stock_code)
    
    def _generate_mock_data(self, stock_code):
        """生成模拟数据（当接口失败时）"""
        # 使用一个合理的价格
        base_price = 3000.0 if stock_code == '999999' else 100.0
        return self._generate_mock_timeshare_data(base_price, base_price * 1.01)
    
    def _generate_mock_timeshare_data(self, pre_close, current_price):
        """生成模拟的分时数据"""
        import numpy as np
        
        # 生成交易时段的时间点（每分钟一个点，更细腻）
        times = []
        
        # 上午时段 9:30-11:30
        for hour in [9, 10, 11]:
            start_min = 30 if hour == 9 else 0
            end_min = 30 if hour == 11 else 60
            for minute in range(start_min, end_min, 1):  # 改为1分钟间隔
                times.append(f"{hour:02d}:{minute:02d}")
        
        # 下午时段 13:00-15:00
        for hour in [13, 14]:
            for minute in range(0, 60, 1):  # 改为1分钟间隔
                times.append(f"{hour:02d}:{minute:02d}")
        times.append("15:00")
        
        # 生成价格数据（从昨收价到当前价的随机波动）
        n_points = len(times)
        
        # 使用随机游走生成价格
        price_change = current_price - pre_close
        trend = price_change / n_points
        
        prices = []
        price = pre_close
        
        for i in range(n_points):
            # 添加随机波动
            noise = np.random.normal(0, abs(price_change) * 0.1)
            price = price + trend + noise
            prices.append(max(price, pre_close * 0.95))  # 限制最低价
        
        # 确保最后一个价格是当前价
        prices[-1] = current_price
        
        # 生成成交量（随机）
        volumes = [int(np.random.uniform(1000, 10000)) for _ in range(n_points)]
        
        # 计算均价
        avg_prices = []
        cumsum_volume = 0
        cumsum_amount = 0
        
        for i in range(len(prices)):
            cumsum_volume += volumes[i]
            cumsum_amount += prices[i] * volumes[i]
            if cumsum_volume > 0:
                avg_prices.append(cumsum_amount / cumsum_volume)
            else:
                avg_prices.append(prices[i])
        
        df = pd.DataFrame({
            'time': times,
            'price': prices,
            'volume': volumes,
            'avg_price': avg_prices
        })
        
        df['pre_close'] = pre_close
        
        if self.verbose:
            print(f"✅ 生成模拟数据: {len(df)} 个数据点")
        return df


if __name__ == '__main__':
    # 测试
    fetcher = TimeshareFetcher(verbose=True)  # 测试时启用详细日志
    
    # 测试上证指数
    print("测试上证指数(999999):")
    df = fetcher.get_timeshare_data('999999')
    if df is not None:
        print(df.head())
        print(f"数据点数: {len(df)}")
    
    # 测试个股
    print("\n测试贵州茅台(600519):")
    df = fetcher.get_timeshare_data('600519')
    if df is not None:
        print(df.head())
        print(f"数据点数: {len(df)}")
