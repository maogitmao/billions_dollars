#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
行情管理器 - 使用线程池优化大量股票监控
"""

from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot
from data.fetchers.realtime_fetcher import RealtimeFetcher
import traceback


class QuoteSignals(QObject):
    """行情信号类（QRunnable不能直接发送信号）"""
    quote_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str, str)
    batch_completed = pyqtSignal(int, int)  # (completed, total)


class QuoteTask(QRunnable):
    """行情获取任务"""
    
    def __init__(self, stock_code, fetcher):
        super().__init__()
        self.stock_code = stock_code
        self.fetcher = fetcher
        self.signals = QuoteSignals()
        self.setAutoDelete(True)
    
    @pyqtSlot()
    def run(self):
        """执行行情获取"""
        try:
            quote = self.fetcher.get_realtime_quote(self.stock_code)
            if quote:
                self.signals.quote_ready.emit(quote)
            else:
                self.signals.error_occurred.emit(self.stock_code, "获取失败")
        except Exception as e:
            self.signals.error_occurred.emit(self.stock_code, str(e))


class QuoteManager(QObject):
    """行情管理器 - 使用线程池管理大量股票"""
    
    # 信号
    quote_updated = pyqtSignal(dict)  # 单个行情更新
    batch_progress = pyqtSignal(int, int)  # 批次进度 (completed, total)
    all_completed = pyqtSignal()  # 全部完成
    
    def __init__(self, max_workers=20):
        """
        初始化行情管理器
        
        Args:
            max_workers: 最大并发线程数（默认20，可根据网络情况调整）
        """
        super().__init__()
        
        # 线程池配置
        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(max_workers)
        
        # 数据获取器（复用连接）
        self.fetcher = RealtimeFetcher()
        
        # 统计信息
        self.total_tasks = 0
        self.completed_tasks = 0
        
        print(f"📊 行情管理器初始化: 最大并发数={max_workers}")
    
    def fetch_quotes(self, stock_codes, priority_codes=None):
        """
        批量获取行情
        
        Args:
            stock_codes: 股票代码列表
            priority_codes: 优先获取的股票代码（可见股票）
        """
        if not stock_codes:
            return
        
        # 重置统计
        self.total_tasks = len(stock_codes)
        self.completed_tasks = 0
        
        # 优先级排序
        if priority_codes:
            # 优先处理可见股票
            priority_set = set(priority_codes)
            sorted_codes = [c for c in stock_codes if c in priority_set] + \
                          [c for c in stock_codes if c not in priority_set]
        else:
            sorted_codes = stock_codes
        
        # 创建任务并提交到线程池
        for stock_code in sorted_codes:
            task = QuoteTask(stock_code, self.fetcher)
            task.signals.quote_ready.connect(self._on_quote_ready)
            task.signals.error_occurred.connect(self._on_error)
            self.thread_pool.start(task)
    
    def _on_quote_ready(self, quote):
        """行情数据就绪"""
        self.completed_tasks += 1
        self.quote_updated.emit(quote)
        self.batch_progress.emit(self.completed_tasks, self.total_tasks)
        
        # 检查是否全部完成
        if self.completed_tasks >= self.total_tasks:
            self.all_completed.emit()
    
    def _on_error(self, stock_code, error_msg):
        """处理错误"""
        self.completed_tasks += 1
        self.batch_progress.emit(self.completed_tasks, self.total_tasks)
        
        # 创建错误行情数据
        error_quote = {
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
            'error': error_msg
        }
        self.quote_updated.emit(error_quote)
        
        # 检查是否全部完成
        if self.completed_tasks >= self.total_tasks:
            self.all_completed.emit()
    
    def get_active_count(self):
        """获取活跃线程数"""
        return self.thread_pool.activeThreadCount()
    
    def get_max_thread_count(self):
        """获取最大线程数"""
        return self.thread_pool.maxThreadCount()
    
    def set_max_thread_count(self, count):
        """设置最大线程数"""
        self.thread_pool.setMaxThreadCount(count)
        print(f"📊 线程池最大并发数已调整为: {count}")
    
    def wait_for_done(self, timeout_ms=30000):
        """等待所有任务完成"""
        return self.thread_pool.waitForDone(timeout_ms)
    
    def clear(self):
        """清空任务队列"""
        self.thread_pool.clear()
