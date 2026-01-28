#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
时间工具
"""

from datetime import datetime, time
from typing import List, Tuple

from config import TRADING_HOURS, CALL_AUCTION_HOURS


def parse_time_range(time_str: str) -> time:
    """
    解析时间字符串
    
    Args:
        time_str: 时间字符串 'HH:MM'
        
    Returns:
        time对象
    """
    hour, minute = map(int, time_str.split(':'))
    return time(hour, minute)


def is_in_time_ranges(current_time: time, time_ranges: List[Tuple[str, str]]) -> bool:
    """
    判断当前时间是否在指定时间段内
    
    Args:
        current_time: 当前时间
        time_ranges: 时间段列表 [('09:30', '11:30'), ...]
        
    Returns:
        是否在时间段内
    """
    for start_str, end_str in time_ranges:
        start_time = parse_time_range(start_str)
        end_time = parse_time_range(end_str)
        
        if start_time <= current_time <= end_time:
            return True
    
    return False


def is_trading_time(dt: datetime = None) -> bool:
    """
    判断是否在交易时间
    
    Args:
        dt: 时间对象，None表示当前时间
        
    Returns:
        是否在交易时间
    """
    if dt is None:
        dt = datetime.now()
    
    # 周末不交易
    if dt.weekday() >= 5:
        return False
    
    current_time = dt.time()
    return is_in_time_ranges(current_time, TRADING_HOURS)


def is_call_auction_time(dt: datetime = None) -> bool:
    """
    判断是否在集合竞价时间
    
    Args:
        dt: 时间对象，None表示当前时间
        
    Returns:
        是否在集合竞价时间
    """
    if dt is None:
        dt = datetime.now()
    
    # 周末不交易
    if dt.weekday() >= 5:
        return False
    
    current_time = dt.time()
    return is_in_time_ranges(current_time, CALL_AUCTION_HOURS)


def get_trading_status() -> str:
    """
    获取当前交易状态
    
    Returns:
        'trading' / 'call_auction' / 'closed'
    """
    if is_trading_time():
        return 'trading'
    elif is_call_auction_time():
        return 'call_auction'
    else:
        return 'closed'
