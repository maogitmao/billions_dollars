#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据获取器模块
"""

from .realtime_fetcher import RealtimeFetcher
from .kline_fetcher import KLineFetcher

__all__ = ['RealtimeFetcher', 'KLineFetcher']
