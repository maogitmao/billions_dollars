#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
行情数据获取工作线程
"""

from PyQt5.QtCore import QThread, pyqtSignal
from data.fetchers.realtime_fetcher import RealtimeFetcher


class QuoteWorker(QThread):
    """行情数据获取工作线程"""
    
    # 信号：返回行情数据
    quote_ready = pyqtSignal(dict)
    # 信号：返回错误信息
    error_occurred = pyqtSignal(str, str)  # stock_code, error_msg
    
    def __init__(self, stock_code):
        super().__init__()
        self.stock_code = stock_code
        self.fetcher = RealtimeFetcher()
    
    def run(self):
        """在后台线程中获取数据"""
        try:
            quote = self.fetcher.get_realtime_quote(self.stock_code)
            self.quote_ready.emit(quote)
        except Exception as e:
            self.error_occurred.emit(self.stock_code, str(e))
