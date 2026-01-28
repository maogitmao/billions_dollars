#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据中心 - 统一数据管理
"""

from typing import Dict, List, Optional, Any
import threading
from datetime import datetime
import pandas as pd

from .event_bus import event_bus, EventType
from config import DATA_REFRESH_INTERVAL


class DataCenter:
    """
    数据中心（单例模式）
    统一管理所有股票数据
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 数据存储
        self._quotes: Dict[str, Dict] = {}           # 实时行情
        self._klines: Dict[str, pd.DataFrame] = {}   # K线数据
        self._indicators: Dict[str, Dict] = {}       # 技术指标
        self._fundamentals: Dict[str, Dict] = {}     # 基本面数据
        
        # 数据获取器（延迟初始化）
        self._fetchers = {}
        
        # 锁
        self._data_lock = threading.Lock()
        
        self._initialized = True
    
    def set_fetcher(self, fetcher_type: str, fetcher):
        """
        设置数据获取器
        
        Args:
            fetcher_type: 获取器类型 (realtime/kline/tick/market/fundflow/fundamental)
            fetcher: 获取器实例
        """
        self._fetchers[fetcher_type] = fetcher
    
    def get_quote(self, stock_code: str) -> Optional[Dict]:
        """
        获取实时行情
        
        Args:
            stock_code: 股票代码
            
        Returns:
            行情数据字典
        """
        with self._data_lock:
            return self._quotes.get(stock_code)
    
    def update_quote(self, stock_code: str, quote_data: Dict):
        """
        更新实时行情
        
        Args:
            stock_code: 股票代码
            quote_data: 行情数据
        """
        with self._data_lock:
            self._quotes[stock_code] = quote_data
        
        # 发布事件
        event_bus.publish(EventType.QUOTE_UPDATED, {
            'stock_code': stock_code,
            'data': quote_data
        })
    
    def get_kline(self, stock_code: str, period: str = 'daily') -> Optional[pd.DataFrame]:
        """
        获取K线数据
        
        Args:
            stock_code: 股票代码
            period: 周期 (1min/5min/15min/30min/60min/daily/weekly/monthly)
            
        Returns:
            K线DataFrame
        """
        key = f"{stock_code}_{period}"
        with self._data_lock:
            return self._klines.get(key)
    
    def update_kline(self, stock_code: str, kline_data: pd.DataFrame, period: str = 'daily'):
        """
        更新K线数据
        
        Args:
            stock_code: 股票代码
            kline_data: K线数据
            period: 周期
        """
        key = f"{stock_code}_{period}"
        with self._data_lock:
            self._klines[key] = kline_data
        
        # 发布事件
        event_bus.publish(EventType.KLINE_UPDATED, {
            'stock_code': stock_code,
            'period': period,
            'data': kline_data
        })
    
    def get_indicator(self, stock_code: str, indicator_name: str) -> Optional[Any]:
        """
        获取技术指标
        
        Args:
            stock_code: 股票代码
            indicator_name: 指标名称
            
        Returns:
            指标数据
        """
        with self._data_lock:
            stock_indicators = self._indicators.get(stock_code, {})
            return stock_indicators.get(indicator_name)
    
    def update_indicator(self, stock_code: str, indicator_name: str, indicator_data: Any):
        """
        更新技术指标
        
        Args:
            stock_code: 股票代码
            indicator_name: 指标名称
            indicator_data: 指标数据
        """
        with self._data_lock:
            if stock_code not in self._indicators:
                self._indicators[stock_code] = {}
            self._indicators[stock_code][indicator_name] = indicator_data
        
        # 发布事件
        event_bus.publish(EventType.INDICATOR_UPDATED, {
            'stock_code': stock_code,
            'indicator': indicator_name,
            'data': indicator_data
        })
    
    def get_fundamental(self, stock_code: str) -> Optional[Dict]:
        """
        获取基本面数据
        
        Args:
            stock_code: 股票代码
            
        Returns:
            基本面数据字典
        """
        with self._data_lock:
            return self._fundamentals.get(stock_code)
    
    def update_fundamental(self, stock_code: str, fundamental_data: Dict):
        """
        更新基本面数据
        
        Args:
            stock_code: 股票代码
            fundamental_data: 基本面数据
        """
        with self._data_lock:
            self._fundamentals[stock_code] = fundamental_data
    
    def get_all_quotes(self) -> Dict[str, Dict]:
        """获取所有实时行情"""
        with self._data_lock:
            return self._quotes.copy()
    
    def get_monitored_stocks(self) -> List[str]:
        """获取所有监控的股票代码"""
        with self._data_lock:
            return list(self._quotes.keys())
    
    def clear_stock_data(self, stock_code: str):
        """
        清除指定股票的所有数据
        
        Args:
            stock_code: 股票代码
        """
        with self._data_lock:
            self._quotes.pop(stock_code, None)
            self._indicators.pop(stock_code, None)
            self._fundamentals.pop(stock_code, None)
            
            # 清除所有周期的K线
            keys_to_remove = [k for k in self._klines.keys() if k.startswith(stock_code)]
            for key in keys_to_remove:
                self._klines.pop(key, None)
    
    def clear_all(self):
        """清除所有数据"""
        with self._data_lock:
            self._quotes.clear()
            self._klines.clear()
            self._indicators.clear()
            self._fundamentals.clear()


# 全局数据中心实例
data_center = DataCenter()
